# File: streamlit_app.py
"""
Streamlit Web App cho RAG Medical Chatbot
Giao diện đẹp để demo cho giáo viên (Phiên bản UI/UX nâng cao)
"""

import streamlit as st
import time
import hashlib
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Import chatbot components
from main import RAGMedicalChatbot
from unified_guardrails import UnifiedGuardrails

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="RAG Medical Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Enhanced UI/UX ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* Color Palette & Global Styles */
    :root {
        --primary-color: #6a11cb;
        --secondary-color: #2575fc;
        --background-color: #0c102a;
        --sidebar-bg: rgba(12, 16, 42, 0.8);
        --card-bg: rgba(255, 255, 255, 0.05);
        --text-color: #EAEAEA;
        --text-muted: #A0AEC0;
        --accent-color: #00D4FF;
        --success-color: #34D399;
        --danger-color: #EF4444;
        --font-family: 'Poppins', sans-serif;
    }

    body {
        font-family: var(--font-family);
        color: var(--text-color);
        background-color: var(--background-color);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--background-color); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-color); }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 { font-weight: 700; }

    /* Chat Messages */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 18px;
        max-width: 75%;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .chat-message .avatar {
        font-size: 1.5rem;
        padding-top: 5px;
    }

    .user-message {
        background: rgba(37, 117, 252, 0.2);
        align-self: flex-end;
        margin-left: auto;
    }
    .bot-message {
        background: rgba(106, 17, 203, 0.2);
        align-self: flex-start;
    }
    .emergency-message {
        background: rgba(239, 68, 68, 0.3);
        border-color: var(--danger-color);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Sidebar Styling */
    .st-emotion-cache-16txtl3 {
        background: var(--sidebar-bg);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Card Styling */
    .stats-card, .auth-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stats-card:hover, .auth-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(37, 117, 252, 0.5), rgba(106, 17, 203, 0.5));
        color: white;
        border: 1px solid var(--secondary-color);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        border-color: var(--accent-color);
        box-shadow: 0 0 15px var(--accent-color);
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "hf_token" not in st.session_state:
    st.session_state.hf_token = os.getenv("HF_TOKEN", "")
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "profile" not in st.session_state:
    st.session_state.profile = {"name": ""}

# --- File-based User & Chat Persistence ---
DATA_DIR = Path(__file__).parent / "user_data"
USERS_FILE = DATA_DIR / "users.json"
CHATS_DIR = DATA_DIR / "chats"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHATS_DIR.mkdir(parents=True, exist_ok=True)

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _load_users() -> dict:
    if not USERS_FILE.exists(): return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def register_user(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    uname = username.strip().lower()
    if not uname or not password:
        return False, "Tên đăng nhập và mật khẩu không được trống."
    if uname in users:
        return False, "Tên đăng nhập đã tồn tại."
    users[uname] = {"password_hash": _hash_password(password)}
    _save_users(users)
    return True, "Đăng ký thành công! Vui lòng chuyển qua tab Đăng nhập."

def authenticate_user(username: str, password: str) -> bool:
    users = _load_users()
    uname = username.strip().lower()
    user = users.get(uname)
    if not user: return False
    return user.get("password_hash") == _hash_password(password)

def get_user_data_path(username: str, file_prefix: str) -> Path:
    return CHATS_DIR / f"{username.strip().lower()}_{file_prefix}.json"

def load_from_json(path: Path, default_value):
    if not path.exists(): return default_value
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_value

def save_to_json(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        st.error(f"Lỗi lưu dữ liệu: {e}")

# --- Chatbot Initialization and Sync ---
def sync_messages_to_chatbot(messages: list):
    """Build chatbot conversation_history from user-assistant message pairs."""
    if not st.session_state.chatbot: return
    pairs = []
    for i in range(0, len(messages) - 1, 2):
        if messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
            pairs.append({"user": messages[i]["content"], "bot": messages[i+1]["content"]})
    st.session_state.chatbot.conversation_history = pairs[-10:] # Keep last 10 turns

def initialize_chatbot():
    """Initialize chatbot with loading spinner."""
    if st.session_state.chatbot: return True
    if not st.session_state.hf_token:
        st.info("Vui lòng nhập Hugging Face token trong sidebar để bắt đầu.")
        return False
    try:
        with st.spinner("🚀 Đang khởi tạo RAG Medical Chatbot..."):
            st.session_state.chatbot = RAGMedicalChatbot(hf_token=st.session_state.hf_token)
        st.success("✅ Chatbot đã sẵn sàng!")
        if st.session_state.is_authenticated and st.session_state.messages:
            sync_messages_to_chatbot(st.session_state.messages)
        return True
    except Exception as e:
        st.error(f"❌ Lỗi khởi tạo chatbot: {e}")
        st.session_state.chatbot = None
        return False

# --- UI Components ---
def display_message(msg):
    """Display a single chat message with new styling."""
    role = msg["role"]
    content = msg["content"]
    is_emergency = msg.get("is_emergency", False)

    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="avatar">👤</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    elif is_emergency:
        st.markdown(f"""
        <div class="chat-message emergency-message">
             <div class="avatar">🚨</div>
             <div><strong>KHẨN CẤP:</strong> {content}</div>
        </div>
        """, unsafe_allow_html=True)
    else: # Bot message
        st.markdown(f"""
        <div class="chat-message bot-message">
            <div class="avatar">🤖</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)

def handle_logout():
    """Save data and reset session state on logout."""
    if st.session_state.auth_user:
        save_to_json(get_user_data_path(st.session_state.auth_user, "chat"), st.session_state.messages)
        save_to_json(get_user_data_path(st.session_state.auth_user, "profile"), st.session_state.profile)

    st.session_state.is_authenticated = False
    st.session_state.auth_user = None
    st.session_state.messages = []
    st.session_state.profile = {"name": ""}
    st.session_state.chatbot = None # Reset chatbot on logout
    st.rerun()

def draw_sidebar():
    """Draws the sidebar content."""
    with st.sidebar:
        # Authentication
        st.markdown("## 🔐 Tài khoản")
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        if not st.session_state.is_authenticated:
            auth_tab, register_tab = st.tabs(["Đăng nhập", "Đăng ký"])
            with auth_tab:
                username = st.text_input("Tên đăng nhập", key="login_username")
                password = st.text_input("Mật khẩu", type="password", key="login_password")
                if st.button("Đăng nhập", use_container_width=True):
                    if authenticate_user(username, password):
                        st.session_state.is_authenticated = True
                        st.session_state.auth_user = username.strip().lower()
                        st.session_state.messages = load_from_json(
                            get_user_data_path(st.session_state.auth_user, "chat"), []
                        )
                        st.session_state.profile = load_from_json(
                            get_user_data_path(st.session_state.auth_user, "profile"), {"name": ""}
                        )
                        st.success("Đăng nhập thành công!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu.")
            with register_tab:
                r_username = st.text_input("Tên đăng nhập mới", key="register_username")
                r_password = st.text_input("Mật khẩu", type="password", key="register_password")
                if st.button("Đăng ký", use_container_width=True):
                    ok, msg = register_user(r_username, r_password)
                    st.toast(msg, icon="✅" if ok else "❌")

        else:
            st.success(f"👋 Chào, {st.session_state.profile.get('name') or st.session_state.auth_user}!")
            if st.button("Đăng xuất", use_container_width=True):
                handle_logout()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Tools & Settings Expander
        with st.expander("🛠️ Cài đặt & Công cụ", expanded=False):
            if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
                st.session_state.messages = []
                if st.session_state.chatbot:
                    st.session_state.chatbot.conversation_history = []
                st.toast("Đã xóa lịch sử!", icon="🗑️")
                st.rerun()

            st.markdown("##### 🔑 Hugging Face Token")
            hf_token_input = st.text_input(
                "Nhập HF token", type="password", value=st.session_state.hf_token,
                help="Token chỉ lưu trong phiên này. Cần thiết để khởi tạo mô hình."
            )
            if st.button("Lưu Token", use_container_width=True):
                new_token = (hf_token_input or "").strip()
                if new_token:
                    st.session_state.hf_token = new_token
                    os.environ["HF_TOKEN"] = new_token
                    st.session_state.chatbot = None # Force re-init
                    st.success("Đã lưu token! Chatbot sẽ được khởi tạo lại.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Token trống. Vui lòng nhập token hợp lệ.")

        st.markdown("---")

        # Information
        st.markdown("## 📚 Thông tin")
        st.info("""
        - **Mô hình**: Llama-Med42 8B
        - **Kiến trúc**: RAG (Retrieval-Augmented Generation)
        - **Bảo vệ**: Tích hợp Guardrails
        - **Tính năng**: Streaming, Memory, Phân tích giá...
        """)
        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:var(--text-muted);'>Made with ❤️ for Education</div>",
            unsafe_allow_html=True
        )


# --- Main Application ---
def main():
    """Main Streamlit app execution."""
    # Header
    user_label = st.session_state.profile.get("name") or st.session_state.auth_user or ""
    sub_header = f"Xin chào, {user_label}" if user_label else "Trợ lý Y tế Thông minh"
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 RAG Medical Chatbot</h1>
        <p>{sub_header}</p>
    </div>
    """, unsafe_allow_html=True)

    draw_sidebar()

    # Require authentication to chat
    if not st.session_state.is_authenticated:
        st.info("💡 Vui lòng đăng nhập từ thanh bên để bắt đầu trò chuyện.")
        return

    # Initialize chatbot after login
    if not initialize_chatbot():
        st.stop()

    # Main layout: Chat on left, System Info on right
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 💬 Cuộc trò chuyện")
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.messages:
                display_message(message)

        # Chat input
        if prompt := st.chat_input("Nhập câu hỏi y tế của bạn..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                display_message({"role": "user", "content": prompt})

            with st.status("🤖 Bot đang suy nghĩ...", expanded=True):
                st.write("🔍 Tìm kiếm thông tin...")
                response_text = ""
                placeholder = st.empty()
                
                try:
                    for chunk in st.session_state.chatbot.generate_response_stream(prompt):
                        response_text += chunk
                        placeholder.markdown(response_text)
                        time.sleep(0.01)
                except Exception as e:
                    response_text = f"Xin lỗi, đã có lỗi xảy ra: {e}"
                    placeholder.markdown(response_text)

            # Update chat with final response
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Save history and rerun to display final message correctly
            if st.session_state.auth_user:
                save_to_json(
                    get_user_data_path(st.session_state.auth_user, "chat"),
                    st.session_state.messages
                )
            st.rerun()

    with col2:
        st.markdown("### 📈 Thông tin hệ thống")
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)

        if st.session_state.chatbot:
            st.success("🟢 Hệ thống hoạt động")
            doc_count = "N/A"
            try:
                if hasattr(st.session_state.chatbot, "rag_system"):
                    col = st.session_state.chatbot.rag_system.embedding_col
                    doc_count = col.count_documents({})
            except Exception:
                doc_count = "N/A" # Handle connection errors or other issues

            st.markdown(f"""
                **📚 Kho tri thức:** `{doc_count}` documents<br>
                **🧠 Bộ nhớ ngắn hạn:** `{len(st.session_state.chatbot.conversation_history)}/10` lượt<br>
                **👤 Người dùng:** `{st.session_state.auth_user}`<br>
            """, unsafe_allow_html=True)
        else:
            st.error("🔴 Hệ thống chưa sẵn sàng")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Gợi ý câu hỏi")
        sample_questions = [
            "Triệu chứng của bệnh tiểu đường là gì?",
            "Làm thế nào để sử dụng vitamin D hiệu quả?",
            "Giá của thuốc cảm cúm thông thường?",
            "Giới thiệu kem chống nắng cho da nhạy cảm."
        ]
        for q in sample_questions:
            if st.button(q, use_container_width=True, key=q):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-muted); padding: 1rem;">
        <p>⚠️ Thông tin chỉ mang tính chất tham khảo, không thay thế chẩn đoán y tế chuyên nghiệp.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()