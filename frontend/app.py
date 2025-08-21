import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PDF Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark minimalist theme
st.markdown("""
<style>
    .stApp {
        background-color: #0f1419;
        color: #ffffff;
    }
    
    .main {
        background-color: #0f1419;
        padding-top: 2rem;
    }
    
    .stChatMessage {
        background-color: #1a1f26;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid #2a2f36;
        color: #ffffff !important;
    }
    
    .stChatMessage p {
        color: #ffffff !important;
    }
    
    .stSidebar {
        background-color: #1a1f26;
    }
    
    .stSelectbox > div > div {
        background-color: #1a1f26;
        color: #ffffff;
        border: 1px solid #2a2f36;
    }
    
    .stButton > button {
        background-color: #2d3748;
        color: #ffffff;
        border: 1px solid #4a5568;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #4a5568;
        border-color: #718096;
    }
    
    .stChatInput > div > div > textarea {
        background-color: #1a1f26 !important;
        color: #ffffff !important;
        border: 1px solid #2a2f36 !important;
        border-radius: 8px !important;
    }
    
    .stChatInput > div > div > textarea::placeholder {
        color: #a0a0a0 !important;
    }
    
    .stChatInput > div > div > textarea:focus {
        border-color: #4a5568 !important;
        box-shadow: 0 0 0 1px #4a5568 !important;
    }
    
    .app-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: #ffffff;
        font-weight: 300;
        opacity: 0.8;
    }
    
    .chat-input-container {
        padding: 1rem 0;
    }
    
    .sidebar-content {
        padding: 1rem;
    }
    
    .model-info {
        color: #ffffff;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .error-message {
        color: #ffffff;
        background-color: #2d1b1b;
        padding: 8px;
        border-radius: 4px;
        margin: 4px 0;
        border-left: 3px solid #ff6b6b;
    }
    
    /* Chat message content styling */
    [data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }
    
    [data-testid="stChatMessageContent"] p {
        color: #ffffff !important;
    }
    
    [data-testid="stChatMessageContent"] div {
        color: #ffffff !important;
    }
    
    /* Caption styling */
    .stCaption {
        color: #ffffff !important;
        opacity: 0.7;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #1a1f26 !important;
        color: #ffffff !important;
        border: 1px solid #2a2f36 !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #1a1f26 !important;
        color: #ffffff !important;
        border: 1px solid #2a2f36 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def call_backend_api(prompt, model="qwen3"):
    """
    Call backend API with the prompt
    """
    try:
        # Backend API endpoint
        backend_url = "http://backend:8000"
        
        # Prepare payload
        payload = {
            "model": model,
            "text": prompt
        }
        
        # Make POST request
        response = requests.post(
            f"{backend_url}/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=360  # 360 second timeout
        )
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                # Handle different possible response formats
                if isinstance(result, dict):
                    return result.get('response', result.get('text', str(result)))
                else:
                    return str(result)
            except json.JSONDecodeError:
                return response.text
        else:
            return f"Error: Backend returned status code {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to backend service. Please make sure the backend is running."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The backend might be processing a heavy task."
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"

def main():
    # Simple header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📚 PDF Research Assistant</div>
        <div class="app-subtitle">Intelligent document analysis and research support</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Minimal sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        model = st.selectbox(
            "Model:",
            ["qwen3:1.7b", "qwen3"],
            key="model_selector"
        )
        
        # Backend status check
        try:
            _ = requests.get("http://backend:8000/healthcheck", timeout=2)
            st.markdown('<div class="model-info">✅ Backend: Connected</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="model-info">❌ Backend: Disconnected</div>', unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("Clear Chat", use_container_width=True, key="clear_chat_button"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message.get("error"):
                    st.markdown(f'<div class="error-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])
                if message["role"] == "assistant":
                    st.caption(f"Qwen3 • {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Ask me about PDF documents or research tasks...", key="main_chat_input"):
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                no_think_prompt = f"nothink/ {prompt}"
                response = call_backend_api(no_think_prompt, model)
            
            # Check if response is an error
            is_error = isinstance(response, str) and response.startswith("Error:")
            
            if is_error:
                st.markdown(f'<div class="error-message">{response}</div>', unsafe_allow_html=True)
            else:
                st.markdown(response.replace("</think>\n", "").replace("<think>\n", ""))
            
            timestamp = datetime.now().strftime("%H:%M")
            st.caption(f"Qwen3 • {timestamp}")
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.replace("</think>\n", "").replace("<think>\n", ""),
                "timestamp": timestamp,
                "error": is_error
            })

if __name__ == "__main__":
    main()