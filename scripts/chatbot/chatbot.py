from groq import Groq
from dotenv import load_dotenv  # Import the load_dotenv function
from sqlalchemy import create_engine, exc as sql_exc
from sqlalchemy import text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import os
import numpy as np
from textwrap import dedent
from typing import List, Tuple
import redis
#from redis_cache import RedisCache

DATABASE_URL = "postgresql://postgres:mdkn@localhost:5432/chatbot"
CHUNK_SIZE = 512
FAISS_K = 3
MODEL_NAME = "deepseek-r1-distill-llama-70b"
EMBEDDINGS_FILE = "embeddings.npy"
FAISS_INDEX_FILE = "faiss_index.index"

#-------------------------------------------------------
# Redis connection with error handling
try:
    r = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )
    r.ping()  # Test connection
except redis.ConnectionError:
    print("Error: Could not connect to Redis. Make sure Redis is running!")
    exit(1)

ttl = 3600
#-----------------------------------------------------------


load_dotenv() # initialize .env file
api_key = os.getenv('GROQ_API_KEY')


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
    splitter = RecursiveCharacterTextSplitter(chunk_size = CHUNK_SIZE)
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
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_FILE)
    return index


def handel_query(query, encoder, index, chunks):
    """process user query"""
    # encode query
    query_embedding = encoder.encode(query)
    #faiss search
    _, indices = index.search(query_embedding.reshape(1, -1), FAISS_K)
    context = [chunks[i] for i in indices[0]]

    return dedent(f"""
    You are a friendly and helpful assistant named Marouf. Your purpose is to answer questions based on the provided context and engage in friendly conversation.

    Context:
    {' '.join(context)}

    Question:
    {query}

    Rules:
    1. If the user greets you (e.g., "hi", "hello"), respond warmly and ask how you can help them.
    2. If the user asks about your name or identity, say: "My name is Marouf, I'm a chatbot programmed by Mohammad Al-Jermy, and I'm here to help you!"
    3. If the user asks a question related to the provided context, answer it based ONLY on the context. If the context doesn't contain relevant information, say: "I don't have enough information to answer this question."
    4. If the user asks about your creator, say: "My creator is Mohammad Al-Jermy, he is a data scientist."
    5. If the user asks a question unrelated to the context (e.g., translation, calculation), politely guide them to ask about something related to the data trivia. For example: "I'm here to help with trivia questions! Feel free to ask me anything about the data."
    6. Always maintain a friendly and approachable tone.
""")


def main():
    
    try:
        text_data = load_database_data()
        chunks = split_text(text_data)
        embeddings = generate_embeddings(chunks)
        index = build_or_load_faiss_index(embeddings)

        encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
        client = Groq(api_key=api_key)

        while True:
            try:
                query = input("\nHow can I help you today😊? (Type 'exit' to quit): ")

                if query.lower().strip() == 'exit':
                    print('Goodbye')
                    break

                #-------------------
                cached = r.get(query)
                if cached:
                    print("Serving from cache...")
                    print(cached)
                    continue
                #--------------------

                prompt = handel_query(query, encoder, index, chunks)

                # For streaming responses
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    #stream=True,
                )

                print("\nResponse:")
                answer = response.choices[0].message.content
                #--------------------
                r.setex(query, ttl, answer)  # Add TTL parameter
                #--------------------
                print(answer)

                '''
                # Properly handle streaming response
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end='', flush=True)
                print() '''
            
            except Exception as e:
                print(f"\n Error processing request: {str(e)}")
    except Exception as e:
        print(f"\nCritical error in main execution: {str(e)}")             


if __name__ == "__main__":
    main()



# # Extract the final answer and remove the <think> section
# full_response = response.choices[0].message.content

# # Remove the <think> section if it exists
# if "<think>" in full_response:
#     # Split the response into <think> and final answer
#     think_start = full_response.find("<think>")
#     think_end = full_response.find("</think>") + len("</think>")
#     final_answer = full_response[think_end:].strip()  # Get everything after </think>
# else:
#     final_answer = full_response  # If no <think> section, use the full response

# # Print the final answer
# print("Response:")
# print(final_answer)
# print("\n")