import os
import asyncio
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import sys
import re # Import the regex module

# --- Path Setup ---
PY_LOCAL_PATH = os.path.join(os.path.dirname(__file__), '..', 'py')
PY_LOCAL_PATH = os.path.abspath(PY_LOCAL_PATH)
if PY_LOCAL_PATH not in sys.path:
    sys.path.insert(0, PY_LOCAL_PATH)

# --- Import Chatbot ---
try:
    from main import RAGMedicalChatbot
except Exception as e:
    print(f"FATAL: Failed to import RAGMedicalChatbot: {e}", file=sys.stderr)
    sys.exit(1)

# --- Flask App Initialization ---
app = Flask(__name__)
# CORRECT CORS SETUP: Apply CORS to all routes for the specific frontend origin.
# This will automatically handle OPTIONS preflight requests and add the necessary headers to all other responses.
CORS(app, resources={r"/api-chat": {"origins": "http://localhost:5173"}})

# --- Singleton Chatbot Instance ---
# Initialize the chatbot once when the server starts.
# The token is no longer needed at initialization.
try:
    print("--- Initializing Chatbot Singleton ---")
    chatbot_instance = RAGMedicalChatbot()
    print("--- Chatbot Singleton Initialized ---")
except Exception as e:
    print(f"FATAL: Could not initialize chatbot instance: {e}", file=sys.stderr)
    chatbot_instance = None

# --- Helper Function to Format Links ---
def format_links(text):
    # Regex to find paths like /login, /products, etc.
    path_regex = r"\/[a-zA-Z0-9-]+"
    
    found_paths = re.findall(path_regex, text)
    
    if found_paths:
        # Process longer paths first to avoid partial replacements
        unique_paths = sorted(list(set(found_paths)), key=len, reverse=True)
        for path in unique_paths:
            # Create a user-friendly name from the path
            link_name = path.lstrip('/').replace('-', ' ').title()
            markdown_link = f"[{link_name}]({path})"
            
            # More robust replacement that handles surrounding quotes or spaces
            # This looks for the path not preceded or followed by other path-like characters
            text = re.sub(r'(?<!\w)' + re.escape(path) + r'(?!\w)', markdown_link, text)
            
    return text

# --- API Routes ---
@app.route('/api-chat', methods=['POST']) # No longer need to handle OPTIONS manually
async def handle_chat():
    # The manual OPTIONS check is no longer needed, CORS() handles it.
    if not chatbot_instance:
        return jsonify({"error": "Chatbot is not available."}), 500

    data = request.get_json()
    query = data.get('message')
    user_id = data.get('user_id', 'default_user')
    hf_token = data.get('hf_token') # User's token from the frontend

    if not query:
        return jsonify({"error": "Message is required"}), 400
    if not hf_token:
        return jsonify({"error": "Hugging Face token is required"}), 400

    try:
        # Pass the user's message, ID, and token to the chatbot instance
        response = await chatbot_instance.run(
            user_message=query, 
            user_id=user_id, 
            hf_token=hf_token
        )
        # The response from `run` is a string, format it before sending
        formatted_response = format_links(response)
        return jsonify({"message": formatted_response})
    except Exception as e:
        print(f"Error during chat processing: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to process chat message"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "chatbot_initialized": chatbot_instance is not None
    })

# --- Main Execution ---
if __name__ == "__main__":
    # Chạy Flask server thay vì script một lần
    # Sử dụng Gunicorn hoặc Waitress trong production
    port = int(os.environ.get("CHATBOT_PY_PORT", 8003))
    app.run(host='0.0.0.0', port=port, debug=False)



