import json as json_mod
import logging
import os
import threading
from typing import Generator
from uuid import uuid4

import requests

from config import LLMConfig, get_llm_config
from db import get_messages, list_project_artifacts, save_message
from observability import log_event, retrieval_metrics
from rag import retrieve_context
from review_mode import build_review_progress, normalize_review_progress, update_review_point
from services.review_validation_service import validate_current_phase_criteria
from services.session_service import (
    SessionState,
    auto_validate_session_review,
    get_or_create_session,
    persist_session,
    update_session_name,
)
from system_prompt import (
    build_system_prompt,
    classify_phase,
    get_phase_progress,
    resolve_active_phase,
)

logger = logging.getLogger(__name__)


def llm_chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    messages: list[dict],
    temperature: float = 0.6,
    max_tokens: int = 1024,
) -> str:
    fallback_response = "I could not generate a response right now. Please try again."
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=60,
        )
        if not resp.ok:
            logger.error("LLM API error (%s): %s", resp.status_code, resp.text[:400])
            return fallback_response
        data = resp.json()
        choices = data.get("choices")
        if not choices or not isinstance(choices, list):
            return fallback_response
        message = choices[0].get("message")
        if not isinstance(message, dict):
            return fallback_response
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            joined = "\n".join(text_parts).strip()
            if joined:
                return joined
        return fallback_response
    except Exception:
        logger.exception("Unexpected error in llm_chat_completion")
        return fallback_response


def llm_stream_completion(
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    messages: list[dict],
    temperature: float = 0.6,
    max_tokens: int = 1024,
) -> Generator[str, None, None]:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    try:
        with requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            stream=True,
            timeout=60,
        ) as resp:
            if not resp.ok:
                logger.error("LLM stream API error (%s): %s", resp.status_code, resp.text[:400])
                return
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    return
                try:
                    chunk = json_mod.loads(data_str)
                    delta = chunk["choices"][0]["delta"]
                    token = delta.get("content") or ""
                    if token:
                        yield token
                except (json_mod.JSONDecodeError, KeyError, IndexError):
                    continue
    except Exception:
        logger.exception("Unexpected error in llm_stream_completion")


def _sse(event: dict) -> str:
    return f"data: {json_mod.dumps(event)}\n\n"


def _build_resilient_fallback(phase_id: int, mode: str) -> str:
    """Return useful coaching when the upstream model stream is unavailable."""
    phase_names = {
        0: "Empathize",
        1: "Conceive",
        2: "Design",
        3: "Implement",
        4: "Test/Revise",
        5: "Operate",
    }
    phase_name = phase_names.get(phase_id, "current")
    if mode == "review":
        return (
            "The AI review service is temporarily unavailable, so I could not validate your "
            f"{phase_name} evidence just now. Your work has been kept; please retry validation shortly."
        )

    questions = {
        0: "Who is the specific user, and what evidence do you have about the problem they experience?",
        1: "What distinct solution options have you compared, and which criteria will you use to choose one?",
        2: "What design details, dependencies, and testable requirements still need to be documented?",
        3: "What is the smallest working increment you can build and verify next?",
        4: "Which acceptance criterion should you test next, and what measured evidence will count as passing?",
        5: "Who will receive or operate the solution, and how will you confirm successful delivery?",
    }
    question = questions.get(phase_id, "What evidence do you have for completing your current phase?")
    return (
        "The AI response service is temporarily unavailable, but your project progress is safe. "
        f"You are still in Phase {phase_id}: {phase_name}; we should not skip ahead until its evidence is complete. "
        f"{question}"
    )


def _format_review_snapshot(review_progress: dict) -> str:
    phases = review_progress.get("phases")
    if not isinstance(phases, list):
        return "No review checklist progress is available yet."

    lines: list[str] = []
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        phase_name = phase.get("name", "Unknown phase")
        phase_id = phase.get("id", "?")
        completed_count = phase.get("completedCount", 0)
        total_count = phase.get("totalCount", 0)
        lines.append(f"Phase {phase_id} - {phase_name}: {completed_count}/{total_count} points complete.")

        points = phase.get("points")
        if not isinstance(points, list):
            continue
        for point in points:
            if not isinstance(point, dict):
                continue
            label = str(point.get("label", "")).strip()
            evidence = str(point.get("evidence", "")).strip()
            status = "done" if bool(point.get("completed", False)) else "missing"
            if evidence:
                lines.append(f"- {status}: {label} Evidence: {evidence}")
            else:
                lines.append(f"- {status}: {label}")

    return "\n".join(lines) if lines else "No review checklist progress is available yet."


def _prepare_chat_context(
    user_message: str,
    session_id: str | None,
    project_id: str | None,
    conversation_history: list,
    request_id: str,
    mode: str,
    review_source_session_id: str | None = None,
) -> tuple[dict, SessionState, str, str, str, dict, object, dict]:
    """Shared setup for both streaming and non-streaming chat paths."""
    clean_message = user_message.strip()
    history = [
        {"role": m.role, "content": m.content}
        for m in (conversation_history or [])[-12:]
        if getattr(m, "content", "").strip()
    ]
    normalized_project_id = (project_id or "default").strip() or "default"
    normalized_session_id = (session_id or "").strip() or f"session-{uuid4().hex[:12]}"

    session: SessionState = get_or_create_session(
        session_id=normalized_session_id,
        project_id=normalized_project_id,
    )
    session.project_id = normalized_project_id
    review_source_session: SessionState | None = None
    clean_review_source_session_id = (review_source_session_id or "").strip()
    if mode == "review" and clean_review_source_session_id and clean_review_source_session_id != normalized_session_id:
        review_source_session = get_or_create_session(
            session_id=clean_review_source_session_id,
            project_id=normalized_project_id,
        )
        session.current_phase = review_source_session.current_phase
        session.phase_history = list(review_source_session.phase_history)
        session.phase_exit_met = set(review_source_session.phase_exit_met)
    llm_config: LLMConfig = get_llm_config()

    classification = classify_phase(
        user_message=clean_message,
        history=history,
        current_phase=session.current_phase,
        llm_call=lambda system, messages: llm_chat_completion(
            base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            model=llm_config.model,
            system=system,
            messages=messages,
            temperature=0.0,
            max_tokens=220,
        ),
    )

    phase_id = resolve_active_phase(
        classification=classification,
        previous_phase=session.current_phase,
        confidence_threshold=0.6,
    )
    # Classifier output is LLM-generated and not guaranteed to stay in range —
    # clamp defensively so an out-of-range value can never index past the
    # fixed 6-phase checklist below.
    phase_id = max(0, min(5, phase_id))
    if mode == "guidance":
        fresh_session = get_or_create_session(session_id=normalized_session_id, project_id=normalized_project_id)
        session.review_progress = fresh_session.review_progress

    if mode in ("guidance", "review"):
        # Review Mode has no checklist of its own — gate against the source
        # guidance session's real evidence so a confident phase jump can't
        # skip an unaddressed earlier phase.
        progress_source = review_source_session.review_progress if review_source_session else session.review_progress
        review_prog = build_review_progress(progress_source)
        oldest_incomplete = None
        for p_idx in range(6):
            phase_completed = review_prog["phases"][p_idx]["completed"]
            if not phase_completed:
                oldest_incomplete = p_idx
                break
        if oldest_incomplete is not None and phase_id > oldest_incomplete:
            logger.info(
                "Pushing back session %s (mode=%s) to oldest incomplete phase: %d (LLM resolved %d)",
                normalized_session_id, mode, oldest_incomplete, phase_id
            )
            phase_id = oldest_incomplete
            incomplete_phases = {
                p_idx for p_idx in range(oldest_incomplete, 6)
                if not review_prog["phases"][p_idx]["completed"]
            }
            session.phase_exit_met -= incomplete_phases

    previous_phase = session.current_phase
    session.current_phase = phase_id
    if phase_id > previous_phase:
        for completed_phase in range(previous_phase, phase_id):
            session.phase_exit_met.add(completed_phase)
    if phase_id not in session.phase_history:
        session.phase_history.append(phase_id)

    # --- Sync criteria re-evaluation for current phase (Problems 2, 3, 7, 10) ---
    # Run a focused LLM call for the current phase's criteria BEFORE generating the
    # bot response so the system prompt reflects the most up-to-date checklist state,
    # and the bot can announce phase completion in the same turn it is detected.

    # Fetch artifacts once here so both guidance validation AND the artifact
    # injection below (which serves both modes) can share the same list.
    project_artifacts = list_project_artifacts(project_id=normalized_project_id)

    all_criteria_just_met = False
    checklist_state: list[dict] | None = None
    sync_guidance_validation = os.getenv("ENGIBUDDY_SYNC_GUIDANCE_VALIDATION", "").strip().lower() == "true"
    if mode == "guidance" and sync_guidance_validation:
        session_messages_so_far = get_messages(session_id=normalized_session_id)

        # Capture state BEFORE this turn to detect transitions (Problem 3)
        prev_review_prog = build_review_progress(session.review_progress)
        prev_phase_points = prev_review_prog["phases"][phase_id]["points"]
        prev_all_met = all(p["completed"] for p in prev_phase_points)

        # Include current user message in validation context (not yet persisted)
        messages_with_current = [
            *session_messages_so_far,
            {"role": "user", "content": clean_message},
        ]
        phase_validation = validate_current_phase_criteria(
            phase_id=phase_id,
            messages=messages_with_current,
            artifacts=project_artifacts,
        )

        # Merge new results into session review_progress (Problem 10: always persist)
        if phase_validation:
            updated_progress = normalize_review_progress(session.review_progress)
            for point_id, point_state in phase_validation.items():
                updated_progress = update_review_point(
                    raw_progress=updated_progress,
                    phase_id=phase_id,
                    point_id=point_id,
                    completed=bool(point_state.get("completed", False)),
                    evidence=str(point_state.get("evidence", "")),
                )
            session.review_progress = updated_progress

        # Check for full phase completion transition (Problem 3)
        fresh_review_prog = build_review_progress(session.review_progress)
        fresh_phase_points = fresh_review_prog["phases"][phase_id]["points"]
        new_all_met = all(p["completed"] for p in fresh_phase_points)
        all_criteria_just_met = new_all_met and not prev_all_met

        checklist_state = fresh_phase_points  # {id, label, completed, evidence}

    rag_result = retrieve_context(
        user_message=clean_message,
        phase_id=phase_id,
        project_id=normalized_project_id,
        mode=mode,
    )
    if rag_result.embedding_degraded:
        logger.warning(
            "Session %s: RAG retrieval degraded to local embeddings — coaching quality may be reduced",
            normalized_session_id,
        )
    metric = retrieval_metrics.record(phase_id=phase_id, top_k=rag_result.top_k, empty=not rag_result.used)
    log_event(
        message="retrieval_metrics",
        request_id=request_id,
        phase=phase_id,
        top_k=rag_result.top_k,
        candidates=rag_result.candidate_count,
        empty=not rag_result.used,
        aggregate=metric,
    )

    # Build system prompt with live checklist state (Problems 1, 5, 8)
    system_prompt, prompt_meta = build_system_prompt(
        phase_id,
        session_id=normalized_session_id,
        mode=mode,
        checklist_state=checklist_state,
        all_criteria_just_met=all_criteria_just_met,
    )

    if mode == "review":
        review_snapshot_session = review_source_session or session
        review_snapshot = _format_review_snapshot(build_review_progress(review_snapshot_session.review_progress))
        system_prompt = (
            f"{system_prompt}\n\n---\nCurrent Review Mode snapshot:\n{review_snapshot}\n---\n"
            "Use this snapshot to explain which Guidance Mode points have already been discussed, "
            "which checklist points still need evidence, and what the student should do next."
        )

    if rag_result.context:
        if mode == "guidance":
            rag_instruction = (
                "The context above contains templates, fill-in-the-blank methods, and coaching tools for this phase. "
                "In Guidance Mode: if templates are available, first present the method choices to the student (A/B/C menu) "
                "and ask them to pick one. Only after they choose should you present the matching template using its "
                "fill-in-the-blank format as written. Do not paraphrase the template — use its structure and labels."
            )
        else:
            rag_instruction = "Use the above context to inform your coaching, but still follow the phase rules."
        system_prompt = (
            f"{system_prompt}\n\n---\nReference context from knowledge base:\n{rag_result.context}\n---\n"
            f"{rag_instruction}"
        )

    # --- Direct artifact injection ---
    # Bypass vector similarity entirely: inject the student's uploaded documents
    # straight into the system prompt so the bot can always reference project-specific
    # content regardless of embedding quality.  This is the primary fix for the issue
    # where uploaded files were indexed but never surfaced in chat responses.
    relevant_artifacts = [
        a for a in project_artifacts
        if a.get("relevance") != "not_relevant" and str(a.get("content", "")).strip()
    ]
    if relevant_artifacts:
        artifact_sections: list[str] = []
        for artifact in relevant_artifacts[:6]:
            title   = str(artifact.get("title", "")).strip() or "Untitled"
            phase   = artifact.get("phase_id")
            label   = f"Phase {phase}" if phase is not None else "general"
            content = str(artifact.get("content", "")).strip()
            snippet = content[:800] + ("..." if len(content) > 800 else "")
            artifact_sections.append(f"[{title} | {label}]\n{snippet}")
        artifacts_block = "\n\n".join(artifact_sections)
        system_prompt = (
            f"{system_prompt}\n\n---\n## Student's Uploaded Project Documents\n"
            "The student has uploaded the documents below. When answering questions "
            "about their specific project, reference this content directly and "
            "prioritise it over general examples.\n\n"
            f"{artifacts_block}\n---"
        )
        logger.info(
            "Injected %d project artifact(s) into system prompt for session %s",
            len(relevant_artifacts[:6]),
            normalized_session_id,
        )

    return (
        clean_message,
        session,
        normalized_session_id,
        normalized_project_id,
        system_prompt,
        prompt_meta,
        rag_result,
        classification,
        history,
        llm_config,
    )


def process_chat(
    user_message: str,
    session_id: str | None,
    project_id: str | None,
    conversation_history: list,
    request_id: str,
    mode: str = "guidance",
    review_source_session_id: str | None = None,
) -> dict:
    (
        clean_message,
        session,
        normalized_session_id,
        normalized_project_id,
        system_prompt,
        prompt_meta,
        rag_result,
        classification,
        history,
        llm_config,
    ) = _prepare_chat_context(
        user_message,
        session_id,
        project_id,
        conversation_history,
        request_id,
        mode,
        review_source_session_id=review_source_session_id,
    )

    existing_message_count = len(get_messages(session_id=normalized_session_id))

    assistant_message = llm_chat_completion(
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        model=llm_config.model,
        system=system_prompt,
        messages=[*history, {"role": "user", "content": clean_message}],
    ) or "No response returned."

    persist_session(normalized_session_id, session)

    if existing_message_count == 0 and history:
        for item in history:
            role = item.get("role")
            content = (item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                save_message(session_id=normalized_session_id, role=role, content=content)

    save_message(session_id=normalized_session_id, role="user", content=clean_message)
    save_message(session_id=normalized_session_id, role="assistant", content=assistant_message)
    if existing_message_count <= 1:
        auto_name = " ".join(clean_message.split()[:6])[:50].strip()
        if auto_name:
            update_session_name(normalized_session_id, auto_name)

    review_payload_session = session
    if mode == "review" and review_source_session_id:
        review_payload_session = get_or_create_session(
            session_id=review_source_session_id,
            project_id=normalized_project_id,
        )
    phase_progress_payload = get_phase_progress(review_payload_session)
    review_progress_payload = build_review_progress(review_payload_session.review_progress)
    # Run full all-phase validation after every guidance message (Problems 2, 7, 10).
    # The focused sync validation above already updated the current phase; this background
    # pass catches cross-phase evidence from earlier in the conversation.
    if mode == "guidance":
        _session_id_for_validation = normalized_session_id
        def _bg_validate():
            try:
                auto_validate_session_review(_session_id_for_validation, update_current_phase=True)
            except Exception:
                logger.exception("Background checklist validation failed for session %s", _session_id_for_validation)
        threading.Thread(target=_bg_validate, daemon=True).start()

    return {
        "sessionId": normalized_session_id,
        "assistantMessage": assistant_message,
        "classification": classification,
        "phaseProgress": phase_progress_payload,
        "reviewProgress": review_progress_payload,
        "ragUsed": rag_result.used,
        "ragDegraded": rag_result.embedding_degraded,
        "ragSources": rag_result.sources,
        "ragPreview": rag_result.preview,
        "ragRetrievalMode": rag_result.retrieval_mode,
        "ragTopK": rag_result.top_k,
        "ragCandidates": rag_result.candidate_count,
        "promptVersion": prompt_meta["version"],
    }


def process_chat_stream(
    user_message: str,
    session_id: str | None,
    project_id: str | None,
    conversation_history: list,
    request_id: str,
    mode: str = "guidance",
    review_source_session_id: str | None = None,
) -> Generator[str, None, None]:
    try:
        (
            clean_message,
            session,
            normalized_session_id,
            normalized_project_id,
            system_prompt,
            prompt_meta,
            rag_result,
            classification,
            history,
            llm_config,
        ) = _prepare_chat_context(
            user_message,
            session_id,
            project_id,
            conversation_history,
            request_id,
            mode,
            review_source_session_id=review_source_session_id,
        )
    except Exception:
        logger.exception("Error in chat stream setup")
        yield _sse({"type": "error", "message": "Failed to prepare response. Please try again."})
        return

    existing_message_count = len(get_messages(session_id=normalized_session_id))

    review_meta_session = session
    if mode == "review" and review_source_session_id:
        review_meta_session = get_or_create_session(
            session_id=review_source_session_id,
            project_id=normalized_project_id,
        )

    # Emit metadata before streaming so UI updates phase stepper immediately
    yield _sse({
        "type": "meta",
        "sessionId": normalized_session_id,
        "classification": classification,
        "phaseProgress": get_phase_progress(review_meta_session),
        "reviewProgress": build_review_progress(review_meta_session.review_progress),
        "ragUsed": rag_result.used,
        "ragDegraded": rag_result.embedding_degraded,
        "ragSources": rag_result.sources,
        "ragPreview": rag_result.preview,
        "ragRetrievalMode": rag_result.retrieval_mode,
        "ragTopK": rag_result.top_k,
        "ragCandidates": rag_result.candidate_count,
        "promptVersion": prompt_meta["version"],
    })

    full_response = ""
    try:
        for token in llm_stream_completion(
            base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            model=llm_config.model,
            system=system_prompt,
            messages=[*history, {"role": "user", "content": clean_message}],
        ):
            full_response += token
            yield _sse({"type": "token", "token": token})
    except Exception:
        logger.exception("Error during LLM stream")
        yield _sse({"type": "error", "message": "Stream interrupted. Please try again."})
        return

    if not full_response.strip():
        full_response = _build_resilient_fallback(session.current_phase, mode)
        yield _sse({"type": "token", "token": full_response})

    persist_session(normalized_session_id, session)

    if existing_message_count == 0 and history:
        for item in history:
            role = item.get("role")
            content = (item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                save_message(session_id=normalized_session_id, role=role, content=content)

    save_message(session_id=normalized_session_id, role="user", content=clean_message)
    save_message(session_id=normalized_session_id, role="assistant", content=full_response)
    if existing_message_count <= 1:
        auto_name = " ".join(clean_message.split()[:6])[:50].strip()
        if auto_name:
            update_session_name(normalized_session_id, auto_name)

    review_payload_session = session
    if mode == "review" and review_source_session_id:
        review_payload_session = get_or_create_session(
            session_id=review_source_session_id,
            project_id=normalized_project_id,
        )
    phase_progress_payload = get_phase_progress(review_payload_session)
    review_progress_payload = build_review_progress(review_payload_session.review_progress)
    # Run full all-phase validation after every guidance message (Problems 2, 7, 10).
    if mode == "guidance":
        _session_id_for_validation = normalized_session_id
        def _bg_validate_stream():
            try:
                auto_validate_session_review(_session_id_for_validation, update_current_phase=True)
            except Exception:
                logger.exception("Background checklist validation failed for session %s", _session_id_for_validation)
        threading.Thread(target=_bg_validate_stream, daemon=True).start()

    yield _sse({
        "type": "done",
        "sessionId": normalized_session_id,
        "phaseProgress": phase_progress_payload,
        "reviewProgress": review_progress_payload,
    })
