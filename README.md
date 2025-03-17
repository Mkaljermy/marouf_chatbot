# QA Trivia Chatbot

## Overview
This project is a **QA Trivia Chatbot** that answers user questions based on a structured dataset of trivia questions and answers. The chatbot uses a **Retrieval-Augmented Generation (RAG)** model, powered by **Groq API** and **DeepSeek**, to provide accurate and context-aware responses. The backend is built with **FastAPI**, the frontend with **Streamlit**, and the data is stored in **PostgreSQL** with **Redis** for caching.

---

## Features
- **RAG Model**: Combines retrieval (FAISS vector search) and generation (Groq API + DeepSeek) for accurate answers.
- **Caching**: Uses **Redis** to cache responses for faster retrieval.
- **Database**: Stores trivia questions and answers in **PostgreSQL**.
- **Frontend**: Interactive UI built with **Streamlit**.
- **Dockerized**: Easy deployment using **Docker** and **Docker Compose**.

---

## Project Structure
```bash
marouf_chatbot/
├── .dockerignore
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.frontend
├── requirements.txt
├── .env
├── data/
│   ├── init.sql
│   └── trivia_full.csv  # Your dataset
└── scripts/
    ├── api/
    │   ├── api.py
    │   ├── embeddings.npy
    │   └── faiss_index.index
    ├── cache/
    │   └── caching.py
    ├── chatbot/
    │   └── chatbot.py
    └── frontend/
        └── index.py

---

Prerequisites
Docker and Docker Compose installed.

Groq API Key: Sign up at Groq and get your API key.

Python 3.9 or higher.

---

Setup
1. Clone the Repository
git clone https://github.com/your-username/marouf_chatbot.git
cd marouf_chatbot

2. Set Up Environment Variables
Create a .env file in the root directory:
# PostgreSQL
POSTGRES_USER=marouf
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=chatbot

# Redis
REDIS_HOST=redis

# Groq
GROQ_API_KEY=your_groq_api_key_here

3. Build and Run with Docker
docker-compose up --build

4. Access the Services
FastAPI Docs: http://localhost:8000/docs

Streamlit UI: http://localhost:8501

---

Technologies Used
Backend: FastAPI, PostgreSQL, Redis

Frontend: Streamlit

AI: Groq API, DeepSeek, Sentence Transformers, FAISS

Docker: Docker, Docker Compose

