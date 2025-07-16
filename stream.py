import streamlit as st
import requests

# ---- Page Config ----
st.set_page_config(page_title="Azure RAG Chat", layout="centered")

# ---- Custom Chat UI Styling ----
st.markdown("""
    <style>
        .chat-box {
            height: 70vh;
            overflow-y: scroll;
            padding: 1rem;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 10px;
        }
        .user-msg, .bot-msg {
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 15px;
            max-width: 75%;
        }
        .user-msg {
            margin-left: auto;
            background-color: #007bff;
            color: white;
        }
        .bot-msg {
            margin-right: auto;
            background-color: #e5e5e5;
            color: black;
        }
        .scroll-container {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            height: 100%;
        }
        .chat-title {
            font-size: 28px;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Session State ----
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed" not in st.session_state:
    st.session_state.indexed = False

# ---- Sidebar File Upload ----
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Indexing document..."):
            res = requests.post("http://localhost:8000/upload/", files={
                "file": (uploaded_file.name, uploaded_file, "application/pdf")
            })
        if res.ok and res.json().get("status") == "success":
            st.session_state.indexed = True
            st.session_state.messages = []
            st.success("Document uploaded and indexed.")
        else:
            st.error("Failed to upload and index document.")

# ---- Main Title ----
st.markdown('<div class="chat-title">💬 Ask Questions from Document</div>', unsafe_allow_html=True)

# ---- Chat Container ----
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        css_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Input Form ----
query = st.text_input("Ask your question", key="user_input", placeholder="Type here and hit Enter...", label_visibility="collapsed")

if query:
    if not st.session_state.indexed:
        st.warning("Please upload a document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.spinner("Thinking..."):
            res = requests.post("http://localhost:8000/ask/", json={"question": query})
        if res.ok:
            answer = res.json().get("answer", "No answer.")
            st.session_state.messages.append({"role": "bot", "content": answer})
        else:
            st.session_state.messages.append({"role": "bot", "content": "⚠️ Something went wrong."})
        st.experimental_rerun()  # Refresh to update chat
