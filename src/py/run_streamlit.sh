#!/bin/bash

echo "🚀 Starting RAG Medical Chatbot Streamlit App..."
echo ""
echo "📋 Make sure you have:"
echo "   - HuggingFace token in .env file"
echo "   - MongoDB connection working"
echo "   - All dependencies installed"
echo ""
echo "🌐 App will open at: http://localhost:8501"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy env_template.txt to .env and add your token."
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Please install: pip install streamlit"
    exit 1
fi

echo "✅ Starting Streamlit app..."
streamlit run streamlit_app.py
