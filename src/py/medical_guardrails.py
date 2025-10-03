# File: medical_guardrails.py
"""
Medical Guardrails cho input/output validation và intent detection
"""

import re
from typing import Dict, Any, List
from typing import Tuple
import numpy as np

class MedicalGuardrails:
    """Medical Guardrails System"""
    
    def __init__(self):
        # Input validation patterns - Enhanced security
        self.blocked_patterns = [
            # Prompt injection patterns
            r"ignore\s+previous\s+instructions",
            r"forget\s+everything",
            r"you\s+are\s+now",
            r"system\s+prompt",
            r"jailbreak",
            r"bypass",
            r"hack",
            r"admin",
            r"root",
            r"sudo",
            r"override",
            r"disable\s+safety",
            r"ignore\s+guidelines",
            r"act\s+as\s+if",
            r"pretend\s+to\s+be",
            r"roleplay",
            r"simulate",
            r"imagine\s+you\s+are",
            r"forget\s+your\s+role",
            r"new\s+instructions",
            r"updated\s+instructions",
            # Vietnamese prompt injection patterns
            r"bỏ\s+qua\s+(chỉ\s*dẫn|hướng\s*dẫn|quy\s*tắc)",
            r"phớt\s*lờ\s+(chỉ\s*dẫn|hướng\s*dẫn)",
            r"lờ\s*đi\s+(chỉ\s*dẫn|hướng\s*dẫn)",
            r"vượt\s+qua\s+(bảo\s*mật|giới\s+hạn|an\s*toàn)",
            r"vô\s*hiệu\s*hóa\s+an\s*toàn",
            r"đóng\s+vai",
            r"giả\s*vờ\s+là",
            r"giả\s*lập",
            r"tưởng\s+tượng\s+bạn\s+là",
            r"quên\s+vai\s+trò",
            r"prompt\s+hệ\s+thống",
            r"hệ\s+thống\s+prompt",
            r"quyền\s+quản\s+trị",
            r"chế\s+độ\s+quản\s+trị",
            r"in\s+ra\s+\"?hack\"?",
            # More Vietnamese variants
            r"bỏ\s*qua\s*luật",
            r"phớt\s*lờ\s*luật",
            r"vượt\s*qua\s*hệ\s*thống",
            r"tiết\s*lộ\s*prompt",
            r"hiển\s*thị\s*prompt",
            r"xem\s*nội\s*dung\s*hệ\s*thống",
            r"lệnh\s*ẩn",
            r"mặc\s*kệ\s*an\s*toàn"
        ]
        
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            r"sex\s+with",
            r"sexual\s+relationship",
            r"how\s+to\s+have\s+sex",
            r"sexual\s+positions",
            r"porn",
            r"pornography",
            r"nude",
            r"naked",
            r"strip",
            r"masturbat",
            r"orgasm",
            r"erotic",
            r"fetish",
            r"kinky",
            r"bdsm",
            r"rape",
            r"molest",
            r"pedophil",
            r"incest",
            r"bestiality",
            r"prostitution",
            r"escort",
            r"hooker",
            # Vietnamese sexual/inappropriate
            r"quan\s*hệ\s*tình\s*dục",
            r"tư\s*thế\s*tình\s*dục",
            r"xem\s*phim\s*đen",
            r"phim\s*sex",
            r"khiêu\s*dâm",
            r"kích\s*dục",
            r"dâm\s*ôn",
            r"dâm\s*loạn",
            r"loạn\s*luân",
            r"ấu\s*dâm"
        ]
        
        # Illegal activities patterns
        self.illegal_patterns = [
            r"how\s+to\s+make\s+bomb",
            r"how\s+to\s+kill",
            r"how\s+to\s+murder",
            r"suicide\s+methods",
            r"how\s+to\s+commit\s+suicide",
            r"self\s+harm\s+methods",
            r"cut\s+myself",
            r"overdose",
            r"poison",
            r"weapon",
            r"gun",
            r"knife",
            r"violence",
            r"terrorism",
            r"bomb\s+making",
            r"drug\s+manufacturing",
            r"how\s+to\s+cook\s+meth",
            r"cocaine\s+production",
            r"hack\s+into",
            r"steal\s+money",
            r"fraud",
            r"scam",
            r"identity\s+theft",
            # Vietnamese illegal/harmful
            r"cách\s*làm\s*bom",
            r"cách\s*giết\s*người",
            r"tự\s*sát",
            r"tự\s*hại",
            r"khủng\s*bố",
            r"chế\s*tạo\s*ma\s*túy",
            r"lừa\s*đảo",
            r"gian\s*lận"
        ]
        
        # Emergency keywords
        self.emergency_keywords = [
            "emergency", "urgent", "severe pain", "chest pain", "heart attack",
            "stroke", "difficulty breathing", "unconscious", "bleeding heavily",
            "overdose", "suicide", "self harm", "crisis",
            # Vietnamese
            "khẩn cấp", "cấp cứu", "đau ngực", "khó thở", "bất tỉnh",
            "chảy máu nhiều", "ngộ độc", "tự tử", "tự hại"
        ]
        
        # Intent detection keywords
        self.price_keywords = [
            "bao nhiêu", "bao nhiêu tiền", "giá", "giá bán", "giá cả", "đơn giá",
            "₫", "vnđ", "vnd", "đ", "đắt", "rẻ", "cost", "price", "expensive", "cheap",
            "tiền", "chi phí", "khuyến mãi", "giảm giá", "sale", "ưu đãi", "bảng giá"
        ]
        
        self.product_keywords = [
            "sản phẩm", "thuốc", "thuốc nào", "loại nào", "nhãn hiệu", "brand", "model",
            "medicine", "product", "công dụng", "tác dụng", "benefit", "effect",
            "thành phần", "ingredient", "hàm lượng", "dosage", "liều", "liều lượng",
            "cách dùng", "hướng dẫn sử dụng", "how to use",
            "chống chỉ định", "tác dụng phụ", "bảo quản", "hạn dùng", "hạn sử dụng",
            "mua", "mua ở đâu", "đặt mua", "bán", "cửa hàng", "nhà thuốc",
            "SKU", "mã sản phẩm"
        ]

        # Website/FAQ intent keywords (expanded, includes short forms)
        self.faq_keywords = [
            # Vietnamese website/navigation/policy/help
            "trang web", "website", "đường dẫn", "điều khoản", "quyền riêng tư", "chính sách",
            "hỗ trợ", "liên hệ", "đăng nhập", "đăng ký", "đăng xuất", "tài khoản", "giỏ hàng", "thanh toán",
            "tin tức", "trợ năng", "xử lý sự cố", "quên mật khẩu", "đặt lại mật khẩu", "khôi phục mật khẩu",
            "/login", "/register", "/account", "/cart", "/checkout", "/privacy", "/terms", "/contact",
            # English
            "privacy", "terms", "policy", "contact", "login", "register", "logout", "forgot password",
            "reset password", "account", "cart", "checkout", "routes", "navigation", "faq",
            # Brand/Persona
            "health care", "HEALTH CARE"
        ]

        # Additional site/UX keywords beyond faq/product/price
        self.web_extra_keywords = [
            "website", "trang web", "trang chủ", "menu", "điều hướng", "đường dẫn",
            "route", "navigation", "ui", "ux", "giao diện", "liên hệ", "hỗ trợ",
            "support", "help", "policy", "terms", "privacy", "cookies"
        ]

        # Unified web keywords = faq ∪ product ∪ price ∪ extras
        self.web_keywords = sorted(list({
            *self.faq_keywords, *self.product_keywords, *self.price_keywords, *self.web_extra_keywords
        }))
        
        self.medical_keywords = [
            # English
            "symptom", "symptoms", "disease", "illness", "pain", "fever", "headache",
            "medicine", "medication", "treatment", "diagnosis", "doctor",
            "hospital", "health", "medical", "condition", "therapy", "anatomy",
            "structure", "organ", "liver", "kidney", "heart", "lung", "stomach",
            # Vietnamese
            "triệu chứng", "bệnh", "đau", "sốt", "đau đầu", "điều trị", "khám",
            "giải phẫu", "cấu tạo", "cơ thể", "cơ quan", "gan", "thận", "tim",
            "phổi", "dạ dày", "ruột", "máu", "da", "mắt", "tai", "mũi", "miệng",
            "xương", "cơ", "khớp", "gan mật", "tiêu hóa", "hô hấp"
        ]
        
        # Medical disclaimer
        self.medical_disclaimer = (
            "\n\n⚠️ Tuyên bố miễn trừ y tế: Thông tin này chỉ mang tính chất giáo dục và "
            "không thay thế cho lời khuyên, chẩn đoán hay điều trị y tế chuyên nghiệp. "
            "Hãy tham khảo ý kiến bác sĩ khi cần."
        )

        # Semantic representative phrases per intent (can be expanded)
        self.intent_phrases: Dict[str, List[str]] = {
            "greeting": [
                "xin chào", "chào bạn", "cảm ơn", "tạm biệt", "hello", "hi"
            ],
            "price": [
                "giá bao nhiêu", "chi phí", "khuyến mãi", "so sánh giá", "price", "cost"
            ],
            "product": [
                "công dụng của thuốc", "thành phần sản phẩm", "cách dùng thuốc", "tác dụng phụ",
                "chống chỉ định", "thuốc này là gì", "product details"
            ],
            "medical": [
                "triệu chứng bệnh", "giải phẫu gan", "cấu tạo cơ thể", "điều trị chung", "phòng ngừa bệnh"
            ],
            "followup": [
                "giải thích thêm", "chi tiết hơn", "ví dụ thêm", "nói rõ hơn", "tiếp tục"
            ],
            "non_medical": [
                "hack wifi", "cách nấu ăn", "tin tức bóng đá", "tải phim"
            ],
            "general": [
                "giúp tôi", "tư vấn giúp", "hỗ trợ"
            ],
            "faq": [
                "trang web hoạt động thế nào", "đường dẫn các trang", "cách đăng nhập",
                "chính sách quyền riêng tư", "điều khoản dịch vụ", "liên hệ ở đâu",
                "chatbot dùng ra sao", "ứng dụng health care là gì", "đăng nhập", "đăng ký",
                "quên mật khẩu", "login", "register", "forgot password"
            ],
            "web": [
                "đăng nhập", "đăng ký", "giá", "sản phẩm", "trang web", "/login", "/products",
                "/privacy", "/terms", "quên mật khẩu", "account", "checkout", "price", "product",
                "điều khoản", "quyền riêng tư", "liên hệ", "hỗ trợ"
            ],
        }

        # Lazy embedding model reference (reuse from RAG if available)
        self._embed_model = None
        # Precomputed representative embeddings and index
        self._rep_texts: List[str] = []
        self._rep_vecs: np.ndarray | None = None
        self._rep_intents: List[str] = []
        # Small LRU cache for query embeddings
        self._q_cache: Dict[str, np.ndarray] = {}
        self._q_cache_order: List[str] = []
        self._q_cache_limit: int = 64

    def _get_embed_model(self):
        if self._embed_model is None:
            try:
                from FlagEmbedding import BGEM3FlagModel
                self._embed_model = BGEM3FlagModel("BAAI/bge-m3")
            except Exception:
                self._embed_model = None
        return self._embed_model

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        model = self._get_embed_model()
        if model is None:
            return np.zeros((len(texts), 768), dtype=np.float32)
        out = model.encode(texts, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        arr = np.array(out["dense_vecs"], dtype=np.float32)
        return arr

    def _embed_query_cached(self, text: str) -> np.ndarray:
        if text in self._q_cache:
            return self._q_cache[text]
        vec = self._embed_texts([text])[0]
        self._q_cache[text] = vec
        self._q_cache_order.append(text)
        if len(self._q_cache_order) > self._q_cache_limit:
            oldest = self._q_cache_order.pop(0)
            self._q_cache.pop(oldest, None)
        return vec

    def _ensure_rep_embeddings(self) -> bool:
        if self._rep_vecs is not None and len(self._rep_texts) > 0:
            return True
        try:
            intents = list(self.intent_phrases.keys())
            rep_texts = [p for intent in intents for p in self.intent_phrases[intent]]
            if not rep_texts:
                return False
            rep_vecs = self._embed_texts(rep_texts)
            self._rep_texts = rep_texts
            self._rep_vecs = rep_vecs
            self._rep_intents = [intent for intent in intents for _ in self.intent_phrases[intent]]
            return True
        except Exception:
            return False

    def _semantic_intent(self, query: str) -> Tuple[str, float]:
        """Compute semantic similarity to representative phrases and return best intent and score.

        Optimizations:
        - Skip entirely for trivial greetings or very short queries (< 3 words) to avoid unnecessary embedding.
        - Precompute representative phrase embeddings once and cache query embeddings.
        """
        try:
            ql = query.strip().lower()
            # Cheap short-circuit: trivial greeting/thanks/bye → no semantic
            trivial_markers = ["xin chào", "chào", "hello", "hi", "cảm ơn", "thank you", "thanks", "tạm biệt", "bye"]
            if any(m in ql for m in trivial_markers):
                return ("general", 0.0)
            # Skip extremely short inputs (<= 2 words) to save compute
            if len([w for w in ql.split() if w.strip()]) <= 2:
                return ("general", 0.0)

            if not self._ensure_rep_embeddings():
                return ("general", 0.0)
            q_vec = self._embed_query_cached(query)
            rep_vecs = self._rep_vecs
            if rep_vecs is None or rep_vecs.size == 0:
                return ("general", 0.0)

            # cosine similarity
            q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
            rep_norm = rep_vecs / (np.linalg.norm(rep_vecs, axis=1, keepdims=True) + 1e-8)
            sims = rep_norm @ q_norm

            # Find best by grouping using precomputed intent index
            best_intent = "general"
            best_score = -1.0
            for idx, intent in enumerate(self._rep_intents):
                score = float(sims[idx])
                if score > best_score:
                    best_score = score
                    best_intent = intent
            return (best_intent, best_score)
        except Exception:
            return ("general", 0.0)
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """Validate user input for security and safety"""
        if not user_input or not user_input.strip():
            return {
                "is_valid": False,
                "reason": "empty_input",
                "response": "Bạn vui lòng nhập câu hỏi để mình hỗ trợ nhé."
            }
        
        user_input_lower = user_input.lower()
        
        # Check for prompt injection
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_input_lower):
                return {
                    "is_valid": False,
                    "reason": "prompt_injection",
                    "response": "Xin lỗi, mình không thể thực hiện yêu cầu này. Bạn có thể hỏi về sức khỏe/y tế nhé."
                }
        
        # Check for inappropriate content
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, user_input_lower):
                return {
                    "is_valid": False,
                    "reason": "inappropriate_content",
                    "response": "Mình chỉ hỗ trợ nội dung về sức khỏe và y tế. Bạn vui lòng đặt câu hỏi phù hợp nhé."
                }
        
        # Check for illegal activities
        for pattern in self.illegal_patterns:
            if re.search(pattern, user_input_lower):
                return {
                    "is_valid": False,
                    "reason": "illegal_content",
                    "response": "Xin lỗi, mình không thể hỗ trợ nội dung gây hại hoặc bất hợp pháp. Bạn có thể hỏi về sức khỏe/y tế nhé."
                }
        
        # Check for emergency
        if any(keyword in user_input_lower for keyword in self.emergency_keywords):
            return {
                "is_valid": True,
                "is_emergency": True,
                "response": "🚨 Có dấu hiệu khẩn cấp. Vui lòng gọi 115 hoặc đến cơ sở y tế gần nhất ngay. Mình không thể hỗ trợ cấp cứu."
            }
        
        # Check input length
        if len(user_input) > 1000:
            return {
                "is_valid": False,
                "reason": "input_too_long",
                "response": "Câu hỏi hơi dài. Bạn rút gọn giúp mình để hỗ trợ tốt hơn nhé."
            }
        
        # Check if it's a valid medical question; if not, allow friendly small-talk
        if not self._is_valid_medical_question(user_input_lower):
            # Allow friendly small-talk; avoid misreading questions like "tôi tên là gì"
            # If it seems like a question ("?" or "là gì") then don't override here.
            if "?" in user_input_lower or "là gì" in user_input_lower:
                return {"is_valid": True, "is_emergency": False}

            # Detect simple small-talk like introducing name
            name_patterns = [
                r"tên\s*tôi\s*là\s+([\w\s]+)",
                r"tôi\s*tên\s*là\s+([\w\s]+)",
                r"mình\s*tên\s*là\s+([\w\s]+)",
                r"my\s+name\s+is\s+([\w\s]+)"
            ]
            detected_name = None
            for pat in name_patterns:
                m = re.search(pat, user_input_lower)
                if m:
                    candidate = m.group(1).strip()
                    # Filter common interrogatives
                    if candidate in {"gì", "ai", "đâu", "gì?", "ai?", "đâu?"}:
                        continue
                    detected_name = candidate.title()
                    break

            friendly = "Rất vui được gặp bạn! 😊 Mình là trợ lý y tế. Bạn muốn hỏi gì về sức khỏe, thuốc men hoặc sản phẩm y tế?"
            if detected_name:
                friendly = f"Chào {detected_name}! 😊 Rất vui được gặp bạn. Mình là trợ lý y tế. Bạn muốn hỏi gì về sức khỏe, thuốc men hoặc sản phẩm y tế?"

            return {
                "is_valid": True,
                "is_emergency": False,
                "override_response": friendly
            }
        
        return {"is_valid": True, "is_emergency": False}
    
    def _is_valid_medical_question(self, query: str) -> bool:
        """Check if the question is related to medical/health topics"""
        
        # First check for greeting patterns - allow these through
        greeting_patterns = [
            "xin chào", "chào", "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "chào bạn", "chào bot", "chào chatbot", "hello bot", "hi bot", "hey bot",
            "cảm ơn", "thank you", "thanks", "cảm ơn bạn", "thank you bot",
            "tạm biệt", "goodbye", "bye", "see you", "hẹn gặp lại",
            "bạn khỏe không", "how are you", "bạn thế nào", "how are you doing",
            "làm gì", "what are you doing", "bạn đang làm gì"
        ]
        
        # Check for greeting patterns first
        if any(pattern in query for pattern in greeting_patterns):
            return True
        
        medical_keywords = [
            # General health
            "sức khỏe", "health", "y tế", "medical", "bệnh", "disease", "illness",
            "triệu chứng", "symptom", "đau", "pain", "sốt", "fever", "ho", "cough",
            "thuốc", "medicine", "medication", "điều trị", "treatment", "therapy",
            "chẩn đoán", "diagnosis", "bác sĩ", "doctor", "bệnh viện", "hospital",
            "phòng khám", "clinic", "dược sĩ", "pharmacist", "nhà thuốc", "pharmacy",
            
            # Body parts and systems
            "tim", "heart", "phổi", "lung", "gan", "liver", "thận", "kidney",
            "dạ dày", "stomach", "ruột", "intestine", "máu", "blood", "da", "skin",
            "mắt", "eye", "tai", "ear", "mũi", "nose", "miệng", "mouth",
            "răng", "tooth", "xương", "bone", "cơ", "muscle", "khớp", "joint",
            
            # Medical conditions
            "tiểu đường", "diabetes", "huyết áp", "blood pressure", "tim mạch", "cardiovascular",
            "ung thư", "cancer", "viêm", "inflammation", "nhiễm trùng", "infection",
            "dị ứng", "allergy", "hen suyễn", "asthma", "đau đầu", "headache",
            "mất ngủ", "insomnia", "trầm cảm", "depression", "lo âu", "anxiety",
            
            # Medications and treatments
            "kháng sinh", "antibiotic", "giảm đau", "painkiller", "vitamin", "khoáng chất",
            "thuốc cảm", "cold medicine", "thuốc ho", "cough medicine", "thuốc sốt", "fever medicine",
            "kem", "cream", "thuốc mỡ", "ointment", "thuốc nhỏ", "drops", "thuốc xịt", "spray",
            
            # Products and prices
            "sản phẩm", "product", "giá", "price", "cost", "mua", "buy", "bán", "sell",
            "công dụng", "benefit", "tác dụng", "effect", "cách dùng", "how to use",
            "liều lượng", "dosage", "tác dụng phụ", "side effect", "chống chỉ định", "contraindication"
        ]
        
        # Check if query contains medical OR web keywords to allow site questions
        keywords = self.medical_keywords + self.web_keywords
        return any(keyword in query for keyword in keywords)
    
    def detect_intent(self, query: str) -> str:
        """Keyword-only intent detection (expanded vocabulary)."""
        return self._fallback_intent_detection(query)
    
    def _fallback_intent_detection(self, query: str) -> str:
        """Fallback intent detection using keywords only"""
        query_lower = query.lower()

        # First: domain keywords take precedence
        has_price = any(keyword in query_lower for keyword in self.price_keywords)
        has_product = any(keyword in query_lower for keyword in self.product_keywords)
        has_medical = any(keyword in query_lower for keyword in self.medical_keywords)
        has_web = any(keyword in query_lower for keyword in self.web_keywords)
        has_faq = any(keyword in query_lower for keyword in self.faq_keywords) 

        # Top-level web intent
        if has_web and not has_medical:
            return "web"

        if has_price and (has_product or has_medical):
            return "price"
        if has_product:
            return "product"
        if has_price:
            return "price"
        if has_medical:
            return "medical"
        if has_faq:
            return "faq"

        # Then: greeting only if no domain keywords and it's truly short/non-question
        greeting_patterns = [
            "xin chào", "chào", "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "chào bạn", "chào bot", "chào chatbot", "hello bot", "hi bot", "hey bot",
            "cảm ơn", "thank you", "thanks", "cảm ơn bạn", "thank you bot",
            "tạm biệt", "goodbye", "bye", "see you", "hẹn gặp lại",
            "bạn khỏe không", "how are you", "bạn thế nào", "how are you doing",
            "làm gì", "what are you doing", "bạn đang làm gì"
        ]
        if any(pattern in query_lower for pattern in greeting_patterns):
            is_short = len(query_lower) <= 40
            ask_markers = ["?", "cho hỏi", "vui lòng", "muốn hỏi", "tư vấn"]
            has_question = any(m in query_lower for m in ask_markers)
            if is_short and not has_question:
                return "greeting"

        # Semantic fallback: use embeddings to choose best intent if keywords fail
        best_intent, score = self._semantic_intent(query)
        if score >= 0.45:
            return best_intent

        return "general"
    
    def validate_output(self, response: str, is_medical: bool = True) -> str:
        """Validate and enhance output"""
        if not response or not response.strip():
            return "Xin lỗi, mình chưa có câu trả lời phù hợp. Bạn thử hỏi cách khác giúp mình nhé."
        
        # Check for harmful content
        harmful_patterns = [
            r"tự\s+chẩn\s+đoán",
            r"không\s+cần\s+bác\s+sĩ",
            r"tự\s+điều\s+trị",
            r"bỏ\s+qua\s+bác\s+sĩ"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response.lower()):
                if "tham khảo ý kiến bác sĩ" not in response.lower():
                    response += "\n\n⚠️ Lưu ý: Luôn tham khảo ý kiến bác sĩ trước khi quyết định điều trị."
        
        # Add medical disclaimer
        if is_medical and ("disclaimer" not in response.lower() and "tuyên bố" not in response.lower()):
            # Ensure newline separation
            if not response.endswith("\n"):
                response += "\n"
            response += self.medical_disclaimer
        
        # Limit response length
        if len(response) > 2000:
            response = response[:2000].rstrip() + "...\n\n[Phản hồi đã được rút gọn]"
        
        return response
    
    def is_medical_question(self, user_message: str) -> bool:
        """Check if the question is medical-related"""
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in self.medical_keywords)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text using LLM when available, fallback to regex."""
        # Try LLM-based extraction via LangChainIntentClassifier
        try:
            from intent_classifier import LangChainIntentClassifier
            clf = LangChainIntentClassifier()
            result = clf.classify(text)
            ent = result.get("entities") or {}
            # Normalize structure
            normalized = {
                "symptoms": ent.get("symptom") or ent.get("symptoms") or [],
                "medications": ent.get("medication") or ent.get("medications") or [],
                "conditions": ent.get("condition") or ent.get("conditions") or [],
                "product_name": ent.get("product_name") or ent.get("product") or "",
            }
            # Ensure lists
            for k in ["symptoms", "medications", "conditions"]:
                v = normalized.get(k)
                if isinstance(v, str):
                    normalized[k] = [v]
                elif not isinstance(v, list):
                    normalized[k] = []
            if not isinstance(normalized.get("product_name"), str):
                normalized["product_name"] = ""
            return normalized
        except Exception:
            pass

        # Regex fallback
        entities = {
            "symptoms": [],
            "medications": [],
            "conditions": [],
            "product_name": ""
        }
        text_lower = text.lower()
        symptom_patterns = [
            r"đau\s+([\wàáạãảăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ-]+)",
            r"sốt\s+([\wàáạãảăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ-]+)",
            r"ho\s+([\wàáạãảăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ-]+)",
        ]
        for pattern in symptom_patterns:
            entities["symptoms"].extend(re.findall(pattern, text_lower))
        return entities
