# File: main.py
"""
RAG Medical Chatbot với LangChain + Guardrails + Llama-Med42 8B
Tích hợp MongoDB + FAISS + NeMo Guardrails
"""

import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv, find_dotenv
from nemoguardrails import RailsConfig, LLMRails
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests
from langchain.llms.base import LLM
from typing import Optional, List, Any
import sys
from langchain.memory import ConversationSummaryBufferMemory


# Import custom modules
from hf_api_llm import HuggingFaceAPILLM
from rag_system import RAGSystem
from unified_guardrails import UnifiedGuardrails

# Load environment variables
load_dotenv()

nest_asyncio.apply()

class HuggingFaceAPILLM(LLM):
    """Custom LLM to use the Hugging Face Inference API with OpenAI-compatible interface."""
    model_name: str = "m42-health/Llama3-Med42-8B:featherless-ai"
    temperature: float = 0.1
    max_new_tokens: int = 2048
    hf_token: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "huggingface_api"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        token = kwargs.get("hf_token", self.hf_token)
        if not token:
            raise ValueError("Hugging Face token must be provided either at initialization or at runtime.")

        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token,
        )

        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_new_tokens,
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error: API request failed: {e}"

class RAGMedicalChatbot:
    """Main RAG Medical Chatbot class, now simplified to work with NeMo Guardrails."""
    
    def __init__(self):
        """
        Initializes the RAG Medical Chatbot.
        The LLM is initialized without a token; it must be provided at runtime.
        """
        load_dotenv(find_dotenv())
        # LLM is now initialized without a token.
        self.llm = HuggingFaceAPILLM()
        
        # Initialize other components
        self.rag_system = RAGSystem()
        
        # Setup NeMo Guardrails, passing the LLM instance to it
        self._setup_guardrails()

        # Store user-specific conversation memories
        self.user_memories = {} # Key: user_id, Value: ConversationSummaryBufferMemory

        print("✅ RAG Medical Chatbot initialized successfully!")

    def _setup_guardrails(self):
        """Initializes NeMo Guardrails."""
        try:
            # Path to the guardrails configuration
            config_path = os.path.join(os.path.dirname(__file__), 'config')
            config = RailsConfig.from_path(config_path)
            # Pass the LLM instance to Guardrails
            # A fallback token can be set for internal Guardrails actions if needed
            config.models[0].parameters['hf_token_fallback'] = os.environ.get('HUGGINGFACE_TOKEN')
            self.rails = LLMRails(config=config, llm=self.llm)
            print("✅ NeMo Guardrails initialized successfully.")
        except Exception as e:
            print(f"⚠️ Guardrails setup failed: {e}", file=sys.stderr)
            self.rails = None

    def get_or_create_memory(self, user_id: str, hf_token: str):
        """
        Retrieves or creates a conversation memory for a specific user.
        Each user gets their own memory instance.
        """
        if user_id not in self.user_memories:
            # Create a new LLM instance for the memory summary, configured with the user's token
            memory_llm = HuggingFaceAPILLM(hf_token=hf_token)
            self.user_memories[user_id] = ConversationSummaryBufferMemory(
                llm=memory_llm,
                max_token_limit=1024, # Limit the size of the summary
                memory_key="chat_history",
                input_key="question",
                return_messages=True
            )
            print(f"Created new memory for user: {user_id}")
        return self.user_memories[user_id]

    async def run(self, user_message: str, user_id: str = "default_user", hf_token: Optional[str] = None):
        """
        Main entry point for generating a response.
        Requires user_id for session management and hf_token for authentication.
        """
        if not hf_token:
            return "Lỗi: Hugging Face token is required to use the chatbot."

        if not self.rails:
            return "Lỗi: Guardrails is not initialized. Cannot process request."

        try:
            # Get user-specific memory
            memory = self.get_or_create_memory(user_id, hf_token)

            # Update the LLM's token for this request
            self.llm.hf_token = hf_token

            # Let NeMo Guardrails handle the flow
            response = await self.rails.generate_async(prompt=user_message)
            
            # Manually save context to memory after the interaction
            memory.save_context({"question": user_message}, {"output": response})

            return response

        except Exception as e:
            print(f"Error during response generation for user {user_id}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return "Đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại."

async def main():
    """Main function for local testing"""
    
    print("🚀 Starting RAG Medical Chatbot...")
    
    # You need a token to run the chatbot now
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("❌ FATAL: HUGGINGFACE_TOKEN environment variable not set.", file=sys.stderr)
        print("Please set the token in your .env file before running.", file=sys.stderr)
        return

    try:
        chatbot = RAGMedicalChatbot()
        print("🚀 Chatbot đã sẵn sàng! Gõ 'exit' để thoát.")
        
        user_id = "local_test_user"

        while True:
            user_message = input("\n👤 You: ")
            if user_message.lower() in ["exit", "quit", "thoát"]:
                print("👋 Tạm biệt!")
                break
            
            if not user_message.strip():
                continue
            
            print("🤖 Bot: ", end="", flush=True)
            # Pass the token with each call
            response = await chatbot.run(user_message, user_id=user_id, hf_token=hf_token)
            print(response)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Đã đóng chương trình.")