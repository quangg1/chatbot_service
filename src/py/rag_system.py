# File: rag_system.py
"""
RAG System với MongoDB + FAISS
"""

import os
import numpy as np
import re
import hashlib
import pickle
from typing import List, Dict, Any
from pymongo import MongoClient
from FlagEmbedding import BGEM3FlagModel


class RAGSystem:
    """RAG Document Retrieval System dùng MongoDB Atlas Vector Search"""

    def __init__(self):
        print("📚 Initializing RAG System (MongoDB Vector Search)...")

        # MongoDB connection
        self.client_mongo = MongoClient("mongodb+srv://hailoaidientich:quang01012004@cluster0.qsitilq.mongodb.net/Health_Care_App")
        self.db = self.client_mongo[os.getenv("MONGO_DB", "Health_Care_App")]
        self.embedding_col = self.db[os.getenv("MONGO_COLLECTION", "embedding")]

        # Initialize embedding model
        self.model = BGEM3FlagModel("BAAI/bge-m3")

        # Embedding cache
        self.cache_dir = "embedding_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.embedding_cache = {}

        # Backward-compatibility: legacy code may reference `rag_system.all_docs`
        # In the MongoDB-backed implementation, we do not pre-load documents.
        # Keep an empty list to avoid AttributeError.
        self.all_docs = []

        print("✅ RAG System initialized with MongoDB Atlas Vector Search!")
    def retrieve_and_build_context(self, input_dict: Dict[str, Any]) -> str:
        """
        Hàm chính được gọi bởi LangChain để thực hiện RAG retrieval.
        Nhận input_dict, lấy query, gọi retrieve_documents, và sau đó gọi build_context.
        """
        query = input_dict.get("question", "")
        intent = input_dict.get("intent", "general")
        
        if not query.strip():
            return "Không có truy vấn người dùng."

        print(f"Retrieving for query: {query} with intent: {intent}")
        
        # 1. Retrieve documents
        # Sử dụng k=5 (hoặc giá trị mặc định)
        docs = self.retrieve_documents(query, k=5) 
        
        # 2. Build context string (Sử dụng các tham số đã tùy chỉnh)
        context = self.build_context(
            docs=docs, 
            intent=intent, 
            original_query=query, 
            char_limit=2000, 
            max_docs=4
        )
        
        return context

    def embed_query(self, text: str) -> List[float]:
        """Embed query text with caching"""
        # Create cache key
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        # Check cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_embedding = pickle.load(f)
                    return cached_embedding
            except Exception:
                pass
        
        # Generate embedding
        out = self.model.encode(
            [text], return_dense=True, return_sparse=False, return_colbert_vecs=False
        )
        q = np.array(out["dense_vecs"][0], dtype=np.float32).tolist()
        
        # Cache the result
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(q, f)
        except Exception:
            pass
            
        return q

    def retrieve_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve similar documents từ MongoDB Atlas"""
        query_vec = self.embed_query(query)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "default",   # Tên index bạn tạo
                    "path": "embedding",
                    "queryVector": query_vec,
                    "numCandidates": 500,  # Tăng để có nhiều candidates hơn
                    "limit": k
                }
            },
            {
                "$project": {
                    "productId": 1,
                    "text": 1,
                    "title": 1,
                    "type": 1,
                    "source": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]


        results = list(self.embedding_col.aggregate(pipeline))
        return [
            {
                "productId": r.get("productId"),
                "text": r.get("text", ""),
                "title": r.get("title"),
                "type": r.get("type"),
                "source": r.get("source"),
                "score": float(r.get("score", 0))
            }
            for r in results
        ]

    def build_context(
        self,
        docs: List[Dict],
        intent: str = "general",
        original_query: str | None = None,
        char_limit: int = 2000,  # Tăng để giữ nhiều thông tin hơn
        max_docs: int = 4  # Tăng số docs để có nhiều thông tin hơn
    ) -> str:
        """Build context từ retrieved documents với filtering thông minh"""
        if not docs:
            # If asking FAQ and nothing retrieved, attempt FAQ fallback retrieval
            if intent == "faq" and original_query:
                faq_docs = self._retrieve_faq_fallback(original_query, k=max_docs)
                if faq_docs:
                    docs = faq_docs
                else:
                    return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
            else:
                return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

        # Filter documents based on relevance and intent
        relevant_docs = self._filter_relevant_docs(docs, intent)
        
        if not relevant_docs:
            return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

        # Intent-based filtering
        if intent == "price":
            relevant_docs = self._filter_price_docs(relevant_docs)
        elif intent == "product":
            relevant_docs = self._filter_product_docs(relevant_docs)
        elif intent == "medical":
            relevant_docs = self._filter_medical_docs(relevant_docs)
        elif intent == "faq":
            relevant_docs = self._filter_faq_docs(relevant_docs)

        # For FAQ: if no relevant FAQ docs found, try a dedicated fallback retrieval
        if intent == "faq" and not relevant_docs and original_query:
            faq_docs = self._retrieve_faq_fallback(original_query, k=max_docs)
            if faq_docs:
                relevant_docs = faq_docs

        # Allow more FAQ docs to carry route examples
        max_docs_local = 8 if intent == "faq" else max_docs
        parts = []
        for d in relevant_docs[:max_docs_local]:
            text = d.get("text", "")

            if intent == "price" and ("₫" in text or "giá" in text.lower()):
                # Giữ nguyên thông tin giá
                pass
            elif len(text) > char_limit:
                text = text[:char_limit].rsplit(" ", 1)[0] + "..."

            label = d.get("type") or ("faq" if d.get("source") == "FAQ_END_USER.md" else "doc")
            pid = d.get("productId")
            title = d.get("title")
            prefix = f"[FAQ]" if label == "faq" else (f"[Sản phẩm ID: {pid}]" if pid else "[Doc]")
            if title and label == "faq":
                parts.append(f"{prefix} {title}: {text}")
            else:
                parts.append(f"{prefix} {text}")

        return "\n".join(parts)
    
    def _filter_relevant_docs(self, docs: List[Dict], intent: str) -> List[Dict]:
        if not docs:
            return []

        max_score = max(d.get("score", 0) for d in docs)
        # Lower threshold for FAQ to be more inclusive
        if intent == "faq":
            threshold = max(0.1, 0.45 * max_score)
        else:
            threshold = max(0.2, 0.6 * max_score)  # ít nhất 20%, hoặc 60% của max_score

        high_score_docs = [d for d in docs if d.get("score", 0) >= threshold]
        return high_score_docs or sorted(docs, key=lambda x: x.get("score",0), reverse=True)[:3]

    def _filter_price_docs(self, docs: List[Dict]) -> List[Dict]:
        """Filter documents for price-related content"""
        price_patterns = [
            r"[\d\.,]+ ?₫", r"[\d\.,]+ ?vnđ", r"[\d\.,]+ ?vnd", r"giá", r"price", r"cost"
        ]
        return [d for d in docs if any(re.search(p, d.get("text", ""), re.IGNORECASE) for p in price_patterns)]

    def _filter_product_docs(self, docs: List[Dict]) -> List[Dict]:
        """Filter documents for product-related content"""
        product_patterns = [
            r"sản phẩm", r"thuốc", r"medicine", r"product", r"công dụng", r"tác dụng"
        ]
        return [d for d in docs if any(re.search(p, d.get("text", ""), re.IGNORECASE) for p in product_patterns)]

    def _filter_medical_docs(self, docs: List[Dict]) -> List[Dict]:
        """Filter documents for medical-related content"""
        medical_patterns = [
            r"triệu chứng", r"symptom", r"bệnh", r"disease", r"điều trị", r"treatment"
        ]
        return [d for d in docs if any(re.search(p, d.get("text", ""), re.IGNORECASE) for p in medical_patterns)]

    def _filter_faq_docs(self, docs: List[Dict]) -> List[Dict]:
        """Filter documents that are FAQ/website info (type==faq or keywords)"""
        filtered = []
        faq_keywords = [
            r"trang web", r"website", r"đường dẫn", r"điều khoản", r"quyền riêng tư", r"chính sách",
            r"liên hệ", r"đăng nhập", r"đăng ký", r"tài khoản", r"giỏ hàng", r"thanh toán",
            r"tin tức", r"health care", r"faq", r"trợ năng", r"xử lý sự cố", r"troubleshooting"
        ]
        for d in docs:
            if d.get("type") == "faq" or d.get("source") == "FAQ_END_USER.md":
                filtered.append(d)
                continue
            text = d.get("text", "")
            if any(re.search(p, text, re.IGNORECASE) for p in faq_keywords):
                filtered.append(d)
        return filtered or docs

    def _retrieve_faq_fallback(self, query: str, k: int = 4) -> List[Dict]:
        """Fallback: retrieve FAQ docs only by local cosine similarity if vector search didn't return them."""
        try:
            q_vec = self.embed_query(query)
            # Pull a reasonable window of FAQ docs
            cursor = self.embedding_col.find(
                {"$or": [{"type": "faq"}, {"source": "FAQ_END_USER.md"}]},
                {"text": 1, "embedding": 1, "productId": 1, "type": 1, "source": 1, "title": 1}
            )
            docs = list(cursor)
            if not docs:
                return []
            import numpy as _np
            q = _np.array(q_vec, dtype=_np.float32)
            qn = q / (_np.linalg.norm(q) + 1e-8)
            scored = []
            for d in docs:
                emb = d.get("embedding")
                if not emb:
                    continue
                v = _np.array(emb, dtype=_np.float32)
                vn = v / (_np.linalg.norm(v) + 1e-8)
                score = float(vn.dot(qn))
                scored.append({
                    "productId": d.get("productId"),
                    "text": d.get("text", ""),
                    "title": d.get("title"),
                    "type": d.get("type"),
                    "source": d.get("source"),
                    "score": score,
                })
            scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return scored[:k]
        except Exception:
            return []

    def extract_price_info(self, docs: List[Dict]) -> str:
        """Extract price information từ documents with expanded regex"""
        price_info = []
        # Expanded price patterns
        price_patterns = [
            r"([\d\.,]+ ?₫)",  # Vietnamese dong
            r"([\d\.,]+ ?vnđ)",  # Vietnamese dong
            r"([\d\.,]+ ?vnd)",  # Vietnamese dong
            r"([\d\.,]+ ?đ)",  # Vietnamese dong short
            r"([\d\.,]+ ?USD)",  # US Dollar
            r"([\d\.,]+ ?usd)",  # US Dollar lowercase
            r"([\d\.,]+ ?\$)",  # Dollar symbol
            r"giá[:\s]*([\d\.,]+)",  # Price with "giá" prefix
            r"price[:\s]*([\d\.,]+)",  # Price with "price" prefix
        ]
        
        for d in docs:
            text = d.get("text", "")
            for pattern in price_patterns:
                price_match = re.search(pattern, text, re.IGNORECASE)
                if price_match:
                    product_name_match = re.search(
                        r"Tên sản phẩm: (.*?)(?=\n|$|,)", text
                    )
                    product_name = (
                        product_name_match.group(1).strip()
                        if product_name_match
                        else d["productId"]
                    )
                    price_info.append(f"- {product_name}: {price_match.group(1)}")
                    break  # Only take first price found

        return (
            "\n".join(price_info)
            if price_info
            else "Không tìm thấy thông tin giá trong dữ liệu."
        )

    def test_retrieval(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Test retrieval accuracy and return detailed results"""
        print(f"🔍 Testing retrieval for query: '{query}'")
        
        # Retrieve documents
        docs = self.retrieve_documents(query, k)
        
        # Build context
        context = self.build_context(docs, "general")
        
        # Analyze results
        result = {
            "query": query,
            "total_docs": len(docs),
            "high_score_docs": len([d for d in docs if d.get("score", 0) >= 0.2]),
            "avg_score": sum(d.get("score", 0) for d in docs) / len(docs) if docs else 0,
            "max_score": max(d.get("score", 0) for d in docs) if docs else 0,
            "min_score": min(d.get("score", 0) for d in docs) if docs else 0,
            "docs": docs,
            "context": context,
            "product_ids": [d.get("productId") for d in docs]
        }
        
        print(f"📊 Results: {result['total_docs']} docs, avg score: {result['avg_score']:.3f}")
        print(f"🎯 Product IDs: {result['product_ids']}")
        
        return result

    def document_count(self) -> int:
        """Return number of documents in the embeddings collection.
        Provides a safe fallback if estimation is not available.
        """
        try:
            return self.embedding_col.estimated_document_count()
        except Exception:
            try:
                return self.embedding_col.count_documents({})
            except Exception:
                return 0
