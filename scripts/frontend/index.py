import streamlit as st
import requests
import json
from streamlit_chat import message
import time

# Page config
st.set_page_config(
    page_title="Marouf Trivia Chatbot",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling with enhanced colors and fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background-color: #f0f4f8;
    }
    
    h1, h2, h3 {
        color: #1e3a8a;
        font-weight: 600;
    }
    
    p {
        color: #334155;
        font-size: 16px;
        line-height: 1.6;
    }
    
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 15px;
        font-size: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
    }
    
    .stButton>button {
        border-radius: 20px;
        padding: 10px 24px;
        font-size: 16px;
        background-color: #3b82f6;
        color: white;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    .chat-container {
        border-radius: 12px;
        background-color: #1e293b;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        padding: 25px;
        margin-bottom: 25px;
    }
    
    /* For dark background container text color override */
    .chat-container h3 {
        color: #e2e8f0;
    }
    
    .chat-container p, .chat-container ul, .chat-container li {
        color: #cbd5e1;
    }
    
    /* Styling for chat messages */
    .css-1l4firl, .css-12w0qpk {
        background-color: #f8fafc !important;
        border-radius: 18px !important;
        padding: 15px !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 15px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* User message style */
    .css-1l4firl {
        background-color: #dbeafe !important;
        color: #1e40af !important;
    }
    
    /* Bot message style */
    .css-12w0qpk {
        background-color: #f1f5f9 !important;
        color: #334155 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    
    /* Title styling */
    .title-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .title-container h1 {
        font-size: 42px;
        background: linear-gradient(45deg, #3b82f6, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .emoji-icon {
        font-size: 32px;
        margin-right: 10px;
    }
    
    /* Conversation container is kept lighter for better readability */
    .conversation-container {
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        padding: 25px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chat history
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'chat_visible' not in st.session_state:
    st.session_state['chat_visible'] = False

# Function to clear chat history
def clear_chat():
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['chat_visible'] = False

# Function to get bot response
def get_bot_response(query):
    # Replace this URL with your FastAPI endpoint
    api_url = "http://localhost:8000/chat"
    
    try:
        response = requests.post(
            api_url,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to the server: {str(e)}"

# App title with gradient text
st.markdown("""
<div class="title-container">
    <h1><span class="emoji-icon">🧠</span> Marouf: Trivia Expert</h1>
</div>
""", unsafe_allow_html=True)

# App description with dark background
st.markdown("""
<div class="chat-container">
    <h3>Welcome to Marouf - Your Trivia Question Master!</h3>
    <p>Marouf is a specialized chatbot that answers all your trivia questions with accuracy and flair. 
    Challenge Marouf with your toughest trivia questions about history, science, sports, entertainment, and more!</p>
</div>
""", unsafe_allow_html=True)

# Sample trivia questions with dark background
st.markdown("""
<div class="chat-container">
    <h3>Try asking Marouf:</h3>
    <ul>
        <li>"What was the first country to reach the South Pole?"</li>
        <li>"Who invented the World Wide Web?"</li>
        <li>"What's the largest mammal on Earth?"</li>
        <li>"Which element has the chemical symbol 'Au'?"</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar with options
with st.sidebar:
    st.markdown("""
    <h2 style="color: #3b82f6; margin-bottom: 20px;">Marouf Settings</h2>
    """, unsafe_allow_html=True)
    
    st.button("Clear Chat History", on_click=clear_chat)
    
    st.markdown("---")
    st.markdown('<h3 style="color: #3b82f6;">About Marouf</h3>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color: #334155;">Marouf is powered by:</p>
    <ul style="color: #334155;">
        <li>FastAPI backend</li>
        <li>Sentence-Transformers for embeddings</li>
        <li>FAISS for similarity search</li>
        <li>Redis for caching responses</li>
    </ul>
    <p style="color: #334155; margin-top: 20px;">Put your trivia knowledge to the test with Marouf!</p>
    """, unsafe_allow_html=True)

# Chat input with improved styling
st.markdown('<div style="margin-bottom: 10px;"><p style="color: #3b82f6; font-weight: 500;">Ask Marouf a trivia question:</p></div>', unsafe_allow_html=True)
query = st.text_input("", key="input", placeholder="Type your trivia question here...")

# Send button
col1, col2 = st.columns([6, 1])
with col2:
    send_button = st.button("Ask Marouf")

# Process the query
if send_button and query:
    st.session_state['chat_visible'] = True
    
    # Display user message
    st.session_state.past.append(query)
    
    # Display "typing" indicator
    message_placeholder = st.empty()
    message_placeholder.markdown('<div style="color: #6b7280; margin: 10px 0;">Marouf is thinking...</div>', unsafe_allow_html=True)
    
    # Get response from the chatbot
    output = get_bot_response(query)
    
    # Add response to session state
    st.session_state.generated.append(output)
    
    # Remove the typing indicator
    message_placeholder.empty()

# Display chat history - using a different class for the conversation container
if st.session_state['chat_visible']:
    st.markdown('<h3 style="color: #3b82f6; margin-top: 30px; margin-bottom: 15px;">Your Trivia Session with Marouf</h3>', unsafe_allow_html=True)
    st.markdown('<div class="conversation-container">', unsafe_allow_html=True)
    
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            # User message
            message(st.session_state['past'][i], is_user=True, key=f"user_{i}")
            
            # Bot response
            message(st.session_state['generated'][i], key=f"bot_{i}")
    
    st.markdown('</div>', unsafe_allow_html=True)