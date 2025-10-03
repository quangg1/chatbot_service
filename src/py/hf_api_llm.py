# File: hf_api_llm.py
import os
from typing import Optional, List, Dict, Any, Iterator
from langchain.llms.base import LLM
from pydantic import Field
from openai import OpenAI


class HuggingFaceAPILLM(LLM):
    """
    Wrapper cho HuggingFace API sử dụng OpenAI client với streaming
    Tích hợp với LangChain và NeMo Guardrails
    """
    
    model_name: str = Field(default="m42-health/Llama3-Med42-8B:featherless-ai")
    max_tokens: int = Field(default=512)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.9)
    hf_token: str = Field(default="")
    client: OpenAI = Field(default=None, exclude=True)  # Exclude from serialization
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.hf_token:
            self.hf_token = os.getenv("HF_TOKEN", os.getenv("HUGGINGFACE_TOKEN", ""))
        if not self.hf_token:
            raise ValueError("HF_TOKEN or HUGGINGFACE_TOKEN environment variable is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.hf_token,
        )
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager=None,
        **kwargs
    ) -> str:
        """Thực hiện API call không streaming"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Xử lý stop sequences nếu có
            if stop and content:
                for stop_seq in stop:
                    if stop_seq in content:
                        content = content.split(stop_seq)[0]
            
            return content.strip() if content else "No response generated"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stream_call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Iterator[str]:
        """Thực hiện API call với streaming"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    
                    # Xử lý stop sequences nếu có
                    if stop:
                        for stop_seq in stop:
                            if stop_seq in content:
                                content = content.split(stop_seq)[0]
                                yield content
                                return
                    
                    yield content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
    
    @property
    def _llm_type(self) -> str:
        return "huggingface_api"
