from groq import Groq
from dotenv import load_dotenv  
from sqlalchemy import create_engine, exc as sql_exc
from sqlalchemy import text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import os
import sys
import numpy as np
from textwrap import dedent
import redis
import re
from hashlib import md5

sys.path.insert(1, 'D:/marouf_chatbot/scripts/cache') # for local development

from cache.caching import redis_object, get_cache_key

# load_dotenv('/app/.env')  # docker relative path

load_dotenv('D:/marouf_chatbot/.env') # load from local project root


# DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}" # docker
# EMBEDDINGS_FILE = "/app/scripts/api/embeddings.npy"  # Absolute path in Docker
# FAISS_INDEX_FILE = "/app/scripts/api/faiss_index.index" # Absolute path in Docker

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}" # local
EMBEDDINGS_FILE = "D:/marouf_chatbot/scripts/api/embeddings.npy"  # local
FAISS_INDEX_FILE = "D:/marouf_chatbot/scripts/api/faiss_index.index"  # local

CHUNK_SIZE = 512
FAISS_K = 3
MODEL_NAME = "deepseek-r1-distill-llama-70b"


r = redis_object()



def load_database_data():
    """load QA from database"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            results = conn.execute(text("""select question, answers from qa_trivia""")).fetchall()

        return [f"Question: {q}\nAnswer: {a}" for q, a in results]

    except sql_exc.SQLAlchemyError as e:
        print(f"DataBase error: {e}")
        exit(1)


def split_text(text_data):
    """"split text into chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap=100,
        separators=["\nQuestion: ", "\nAnswer: ", "\n"]
        )
    return splitter.split_text('\n'.join(text_data))


def generate_embeddings(chunks):
    """generat or load embeddings"""
    if os.path.exists(EMBEDDINGS_FILE):
        return np.load(EMBEDDINGS_FILE)

    encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = encoder.encode(chunks)
    np.save(EMBEDDINGS_FILE, embeddings)
    return embeddings


def build_or_load_faiss_index(embeddings):
    """manage faiss index"""
    if os.path.exists(FAISS_INDEX_FILE):
        return faiss.read_index(FAISS_INDEX_FILE)
    
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_FILE)
    return index


def create_messages(query, context):
    """Create structured messages for the LLM."""
    system_msg = dedent("""\
    You are Marouf, a friendly and helpful assistant. Your purpose is to answer questions based on the provided context and engage in friendly conversation.

    Rules:
    1. If the user greets you (e.g., "hi", "hello"), respond warmly and ask how you can help them.
    2. If the user asks about your name or identity lik " who are you" ..., say: "My name is Marouf, I'm a chatbot programmed by Mohammad Al-Jermy, and I'm here to help you!"
    3. If the user asks a question related to the provided context, answer it based ONLY on the context. If the context doesn't contain relevant information, say: "I don't have enough information to answer this question."
    4. If the user asks about your creator, say: "My creator is Mohammad Al-Jermy, he is a data scientist."
    5. If the user asks a question unrelated to the context (e.g., translation, calculation), politely guide them to ask about something related to the data trivia. For example: "I'm here to help with trivia questions! Feel free to ask me anything about the data."
    6. Always maintain a friendly and approachable tone.
    """)
    
    user_msg = dedent(f"""\
    Context: {' '.join(context)}
    Question: {query}
    """)
    
    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]


def get_response(query, encoder, index, chunks):
    
    api_key = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=api_key)

    query_embedding = encoder.encode(query)
    faiss.normalize_L2(query_embedding.reshape(1, -1))

    _, indices = index.search(query_embedding.reshape(1, -1), FAISS_K)
    context = [chunks[i] for i in indices[0]]

    messages = create_messages(query, context)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

    #------------------------------------
    cache_key = get_cache_key(query)
    ttl = 3600  # 1 hour
    r.setex(cache_key, ttl, answer)
    #------------------------------------

    print("\nResponse:")
    return answer

    
    

def main():
    
    try:
        text_data = load_database_data()
        chunks = split_text(text_data)
        embeddings = generate_embeddings(chunks)
        index = build_or_load_faiss_index(embeddings)
        encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        while True:
            try:
                query = input("\nHow can I help you today😊? (Type 'exit' to quit): ").strip()
                if query.lower().strip() == 'exit':
                    print('Goodbye')
                    break

                #------------------------------------
                cache_key = get_cache_key(query)
                cached_response = r.get(cache_key)
                if cached_response:
                    print("Serving from cache...")
                    print(cached_response)
                    continue
                #------------------------------------

                print(get_response(query, encoder, index, chunks))

            except Exception as e:
                print(f"\n Error processing request: {str(e)}")
    except Exception as e:
        print(f"\nCritical error in main execution: {str(e)}")             


if __name__ == "__main__":
    main()