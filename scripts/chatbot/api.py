from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import split_text, build_or_load_faiss_index, load_database_data, generate_embeddings, get_response
from caching import redis_object, get_cache_key
from sentence_transformers import SentenceTransformer


class query(BaseModel):
    query:str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

text_data = load_database_data()
chunks = split_text(text_data)
embeddings = generate_embeddings(chunks)
index = build_or_load_faiss_index(embeddings)
encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@app.post("/chat")
async def get_resply(query:query):
    try:
        user_query = query.query.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if user_query.lower() == "exit":
            print("Goodbye")
            sys.exit() 

        response = get_response(user_query, encoder, index, chunks)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
