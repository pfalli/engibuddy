# Start EngiBuddy Locally

1. Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o-mini
   RAG_EMBEDDING_PROVIDER=openai
   RAG_EMBEDDING_API_KEY=your_openai_api_key
   RAG_EMBEDDING_BASE_URL=https://api.openai.com/v1
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   RAG_TOP_K=3
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

2. Start the backend from the project root:

   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. In a second terminal, start the frontend from the project root:

   ```powershell
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000).
