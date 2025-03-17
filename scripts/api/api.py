from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import sys
from dotenv import load_dotenv

sys.path.insert(2,'D:/marouf_chatbot/scripts') # for local development
load_dotenv('D:/marouf_chatbot/.env') # load from local project root


# load_dotenv('/app/.env') # for docker container env
from cache.caching import redis_object, get_cache_key
from chatbot.chatbot import *



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

r = redis_object()


@app.post("/chat")
async def get_reply(query:query):
    try:
        user_query = query.query.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        #------------------------------------
        cache_key = get_cache_key(user_query)
        cached_response = r.get(cache_key)
        if cached_response:
            print("Serving from cache...")
            return {"response": cached_response}
        #------------------------------------

        response = get_response(user_query, encoder, index, chunks)

        # the response after without thinking
        final_response = re.sub(r'<think>.*?</think>\s*', '', response, flags=re.DOTALL).strip()

        return {"response": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")