@echo off
echo 🚀 Starting RAG Medical Chatbot Streamlit App...
echo.
echo 📋 Make sure you have:
echo    - HuggingFace token in .env file
echo    - MongoDB connection working
echo    - All dependencies installed
echo.
echo 🌐 App will open at: http://localhost:8501
echo.
pause
"D:\Anaconda\python.exe" -m streamlit run streamlit_app.py --server.fileWatcherType=none
