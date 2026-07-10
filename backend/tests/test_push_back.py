import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO)

from services.session_service import SessionState, auto_validate_session_review
from services.chat_service import _prepare_chat_context, _build_resilient_fallback
from review_mode import REVIEW_CHECKLIST

def test_push_back_in_chat_context():
    """Verify that if LLM tries to advance phase in Guidance Mode, but previous phases are incomplete,
    the active phase is pushed back to the oldest incomplete phase."""
    
    # 1. Setup a session state where Phase 0 is incomplete
    session = SessionState(
        current_phase=0,
        phase_history=[0],
        review_progress={
            "0": {
                "problem_statement": {"completed": False, "evidence": ""},
                "stakeholder_analysis": {"completed": False, "evidence": ""},
            }
        }
    )
    
    # Mock LLM configuration & classification
    mock_llm_config = MagicMock()
    mock_llm_config.base_url = "http://fake"
    mock_llm_config.api_key = "fake"
    mock_llm_config.model = "fake"
    
    mock_classification = {
        "phase": 2, # LLM tries to advance them directly to Phase 2 (Design)
        "phase_name": "Design",
        "confidence": 0.9,
        "transition": "advance",
    }
    
    # Mock database load/persist
    with patch("services.chat_service.get_or_create_session", return_value=session), \
         patch("services.chat_service.get_llm_config", return_value=mock_llm_config), \
         patch("services.chat_service.classify_phase", return_value=mock_classification), \
         patch("services.chat_service.retrieve_context") as mock_retrieve, \
         patch("services.chat_service.build_system_prompt", return_value=("system", {"version": "1.0"})):
         
        mock_retrieve.return_value.context = "fake context"
        mock_retrieve.return_value.sources = []
        mock_retrieve.return_value.used = True
        mock_retrieve.return_value.top_k = 3
        mock_retrieve.return_value.candidate_count = 5
        mock_retrieve.return_value.preview = ""
        mock_retrieve.return_value.retrieval_mode = "local"
        
        # Invoke _prepare_chat_context in "guidance" mode
        res = _prepare_chat_context(
            user_message="I want to design my database now",
            session_id="test-session",
            project_id="test-project",
            conversation_history=[],
            request_id="req-1",
            mode="guidance"
        )
        
        updated_session = res[1]
        
        # Check that their phase was PUSHED BACK to Phase 0 because Phase 0 is incomplete!
        assert updated_session.current_phase == 0, f"Expected active phase to be 0, but got {updated_session.current_phase}"
        print("[OK] test_push_back_in_chat_context passed successfully!")

def test_allow_advance_when_previous_phases_complete():
    """Verify that if all previous phases are complete, the student is successfully allowed to advance."""
    
    # Create complete checklist progress for Phase 0
    phase_0_progress = {}
    for pt in REVIEW_CHECKLIST[0]:
        phase_0_progress[pt["id"]] = {"completed": True, "evidence": "strong evidence"}
        
    session = SessionState(
        current_phase=0,
        phase_history=[0],
        review_progress={
            "0": phase_0_progress
        }
    )
    
    mock_llm_config = MagicMock()
    mock_llm_config.base_url = "http://fake"
    mock_llm_config.api_key = "fake"
    mock_llm_config.model = "fake"
    
    mock_classification = {
        "phase": 1, # LLM tries to advance them to Phase 1 (Conceive)
        "phase_name": "Conceive",
        "confidence": 0.95,
        "transition": "advance",
    }
    
    with patch("services.chat_service.get_or_create_session", return_value=session), \
         patch("services.chat_service.get_llm_config", return_value=mock_llm_config), \
         patch("services.chat_service.classify_phase", return_value=mock_classification), \
         patch("services.chat_service.retrieve_context") as mock_retrieve, \
         patch("services.chat_service.build_system_prompt", return_value=("system", {"version": "1.0"})):
         
        mock_retrieve.return_value.context = "fake context"
        mock_retrieve.return_value.sources = []
        mock_retrieve.return_value.used = True
        mock_retrieve.return_value.top_k = 3
        mock_retrieve.return_value.candidate_count = 5
        mock_retrieve.return_value.preview = ""
        mock_retrieve.return_value.retrieval_mode = "local"
        
        res = _prepare_chat_context(
            user_message="I have completed my problem statement and stakeholder research",
            session_id="test-session",
            project_id="test-project",
            conversation_history=[],
            request_id="req-2",
            mode="guidance"
        )
        
        updated_session = res[1]
        
        # Check that they ARE allowed to advance to Phase 1 because Phase 0 checklist is fully complete!
        assert updated_session.current_phase == 1, f"Expected active phase to be 1, but got {updated_session.current_phase}"
        print("[OK] test_allow_advance_when_previous_phases_complete passed successfully!")

def test_push_back_during_auto_validation():
    """Verify that auto_validate_session_review automatically pushes back the active phase if previous phases are incomplete."""
    
    # 1. Setup a session in DB mock where the user is in Phase 2, but Phase 0 is incomplete
    session_data = {
        "id": "test-session",
        "project_id": "test-project",
        "current_phase": 2, # User is in Phase 2
        "phase_history": [0, 1, 2],
        "phase_exit_met": [],
        "review_progress": {
            "0": {
                "problem_statement": {"completed": False, "evidence": ""},
            }
        }
    }
    
    # AI validation mock outputs that Phase 0 is still incomplete
    mock_ai_validation = {
        "0": {
            "problem_statement": {"completed": False, "evidence": ""},
        }
    }
    
    with patch("services.session_service.get_session", return_value=session_data), \
         patch("services.session_service.get_messages", return_value=[]), \
         patch("services.session_service.list_project_artifacts", return_value=[]), \
         patch("services.session_service.validate_review_checklist_with_ai", return_value=mock_ai_validation), \
         patch("services.session_service.persist_session") as mock_persist:
         
        res = auto_validate_session_review("test-session", update_current_phase=True)
        
        # Grab the session that was persisted
        persisted_session = mock_persist.call_args.kwargs.get("session") or mock_persist.call_args[0][1]
        
        # Check that the session active phase was pushed back to Phase 0!
        assert persisted_session.current_phase == 0, f"Expected active phase to be pushed back to 0, but got {persisted_session.current_phase}"
        assert res["phaseProgress"]["phases"][0]["active"] == True
        print("[OK] test_push_back_during_auto_validation passed successfully!")

def test_push_back_in_stream_path():
    """Verify push-back fires in streaming path: meta SSE event reflects pushed-back phase."""
    import json
    from services.chat_service import process_chat_stream

    session = SessionState(
        current_phase=0,
        phase_history=[0],
        review_progress={
            "0": {
                "problem_statement": {"completed": False, "evidence": ""},
            }
        }
    )

    mock_llm_config = MagicMock()
    mock_llm_config.base_url = "http://fake"
    mock_llm_config.api_key = "fake"
    mock_llm_config.model = "fake"

    mock_classification = {
        "phase": 3,
        "phase_name": "Design",
        "confidence": 0.9,
        "transition": "advance",
    }

    with patch("services.chat_service.get_or_create_session", return_value=session), \
         patch("services.chat_service.get_llm_config", return_value=mock_llm_config), \
         patch("services.chat_service.classify_phase", return_value=mock_classification), \
         patch("services.chat_service.retrieve_context") as mock_retrieve, \
         patch("services.chat_service.build_system_prompt", return_value=("system", {"version": "1.0"})), \
         patch("services.chat_service.llm_stream_completion", return_value=iter(["Hello", " world"])), \
         patch("services.chat_service.get_messages", return_value=[]), \
         patch("services.chat_service.save_message"), \
         patch("services.chat_service.persist_session"), \
         patch("services.chat_service.update_session_name"), \
         patch("services.chat_service.auto_validate_session_review"), \
         patch("services.chat_service.validate_current_phase_criteria", return_value={}):

        mock_retrieve.return_value.context = "fake context"
        mock_retrieve.return_value.sources = []
        mock_retrieve.return_value.used = True
        mock_retrieve.return_value.top_k = 3
        mock_retrieve.return_value.candidate_count = 5
        mock_retrieve.return_value.preview = ""
        mock_retrieve.return_value.retrieval_mode = "local"
        mock_retrieve.return_value.embedding_degraded = False

        events = list(process_chat_stream(
            user_message="I want to design my system now",
            session_id="test-session-stream",
            project_id="test-project",
            conversation_history=[],
            request_id="req-stream-1",
            mode="guidance",
        ))

        meta_event = None
        for event in events:
            if event.startswith("data: "):
                data = json.loads(event[6:])
                if data.get("type") == "meta":
                    meta_event = data
                    break

        assert meta_event is not None, "No meta event in stream"
        active_phases = [p for p in meta_event["phaseProgress"]["phases"] if p.get("active")]
        assert len(active_phases) == 1
        assert active_phases[0]["id"] == 0, f"Expected active phase 0, got {active_phases[0]['id']}"
        print("[OK] test_push_back_in_stream_path passed successfully!")


def test_stream_timeout_fallback_is_phase_aware():
    response = _build_resilient_fallback(0, "guidance")

    assert "Phase 0: Empathize" in response
    assert "should not skip ahead" in response
    assert "specific user" in response
    assert "I could not generate a response right now" not in response

if __name__ == "__main__":
    print("Running EngiBuddy Push-back Mechanism Unit Tests...")
    test_push_back_in_chat_context()
    test_allow_advance_when_previous_phases_complete()
    test_push_back_during_auto_validation()
    test_push_back_in_stream_path()
    print("All push-back mechanism tests passed successfully!")
