# 🛡️ Security & Guardrails Documentation

## Tổng quan bảo mật

RAG Medical Chatbot được trang bị hệ thống guardrails đa lớp để đảm bảo an toàn và tuân thủ đạo đức y tế.

## 🔒 Các lớp bảo vệ

### 1. Input Validation Layer

#### 🚫 Prompt Injection Protection
```python
blocked_patterns = [
    "ignore previous instructions",
    "forget everything", 
    "you are now",
    "system prompt",
    "jailbreak",
    "bypass",
    "hack",
    "admin",
    "root",
    "sudo",
    "override",
    "disable safety",
    "ignore guidelines",
    "act as if",
    "pretend to be",
    "roleplay",
    "simulate",
    "imagine you are",
    "forget your role",
    "new instructions",
    "updated instructions"
]
```

#### 🚫 Inappropriate Content Filter
```python
inappropriate_patterns = [
    "sex with",
    "sexual relationship",
    "how to have sex",
    "sexual positions",
    "porn", "pornography",
    "nude", "naked",
    "strip", "masturbat",
    "orgasm", "erotic",
    "fetish", "kinky",
    "bdsm", "rape",
    "molest", "pedophil",
    "incest", "bestiality",
    "prostitution", "escort"
]
```

#### 🚫 Illegal Activities Filter
```python
illegal_patterns = [
    "how to make bomb",
    "how to kill", "how to murder",
    "suicide methods",
    "how to commit suicide",
    "self harm methods",
    "cut myself", "overdose",
    "poison", "weapon",
    "gun", "knife", "violence",
    "terrorism", "bomb making",
    "drug manufacturing",
    "how to cook meth",
    "cocaine production",
    "hack into", "steal money",
    "fraud", "scam",
    "identity theft"
]
```

### 2. Medical Content Validation

#### ✅ Valid Medical Keywords
```python
medical_keywords = [
    # General health
    "sức khỏe", "health", "y tế", "medical",
    "bệnh", "disease", "illness",
    "triệu chứng", "symptom",
    "đau", "pain", "sốt", "fever",
    "thuốc", "medicine", "medication",
    "điều trị", "treatment", "therapy",
    
    # Body parts and systems
    "tim", "heart", "phổi", "lung",
    "gan", "liver", "thận", "kidney",
    "dạ dày", "stomach", "ruột", "intestine",
    "máu", "blood", "da", "skin",
    "mắt", "eye", "tai", "ear",
    
    # Medical conditions
    "tiểu đường", "diabetes",
    "huyết áp", "blood pressure",
    "tim mạch", "cardiovascular",
    "ung thư", "cancer",
    "viêm", "inflammation",
    "nhiễm trùng", "infection",
    
    # Medications and treatments
    "kháng sinh", "antibiotic",
    "giảm đau", "painkiller",
    "vitamin", "khoáng chất",
    "thuốc cảm", "cold medicine",
    "kem", "cream", "thuốc mỡ", "ointment"
]
```

### 3. System Prompt Protection

#### 🎯 Strict Medical Guidelines
```
GIỚI HẠN NGHIÊM NGẶT:
- CHỈ trả lời câu hỏi về sức khỏe, y tế, thuốc men, sản phẩm y tế
- KHÔNG trả lời câu hỏi về tình dục, bạo lực, hoạt động bất hợp pháp
- KHÔNG cung cấp thông tin có thể gây hại
- LUÔN duy trì tính chuyên nghiệp y tế
```

### 4. Output Validation Layer

#### ✅ Response Filtering
- Kiểm tra nội dung có hại trong response
- Tự động thêm medical disclaimer
- Giới hạn độ dài response
- Kiểm tra tính chuyên nghiệp y tế

## 🚨 Emergency Detection

### Khẩn cấp y tế
```python
emergency_keywords = [
    "emergency", "urgent", "severe pain",
    "chest pain", "heart attack", "stroke",
    "difficulty breathing", "unconscious",
    "bleeding heavily", "overdose",
    "suicide", "self harm", "crisis",
    "khẩn cấp", "cấp cứu"
]
```

**Response**: Tự động chuyển hướng đến dịch vụ cấp cứu

## 📊 Validation Flow

```
User Input
    ↓
1. Empty Input Check
    ↓
2. Prompt Injection Check
    ↓
3. Inappropriate Content Check
    ↓
4. Illegal Activities Check
    ↓
5. Emergency Detection
    ↓
6. Medical Content Validation
    ↓
7. Input Length Check
    ↓
Valid Input → Generate Response
    ↓
8. Output Validation
    ↓
9. Medical Disclaimer
    ↓
Final Response
```

## 🛠️ Implementation Details

### MedicalGuardrails Class
```python
class MedicalGuardrails:
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        # Multi-layer validation
        # Returns validation result with reason and response
    
    def _is_valid_medical_question(self, query: str) -> bool:
        # Check if query contains medical keywords
    
    def validate_output(self, response: str, is_medical: bool = True) -> str:
        # Validate and enhance output
```

### Response Types
```python
# Valid responses
{"is_valid": True, "is_emergency": False}

# Blocked responses
{
    "is_valid": False,
    "reason": "prompt_injection|inappropriate_content|illegal_content|non_medical_question",
    "response": "Appropriate rejection message"
}

# Emergency responses
{
    "is_valid": True,
    "is_emergency": True,
    "response": "Emergency guidance message"
}
```

## 🔧 Customization

### Thêm patterns mới
```python
# Trong medical_guardrails.py
self.blocked_patterns.append(r"new_pattern")
self.inappropriate_patterns.append(r"new_inappropriate")
self.illegal_patterns.append(r"new_illegal")
```

### Thêm medical keywords
```python
# Trong _is_valid_medical_question method
medical_keywords.extend([
    "new_medical_term",
    "another_medical_term"
])
```

## 📈 Monitoring & Logging

### Security Events
- Prompt injection attempts
- Inappropriate content requests
- Illegal activity queries
- Non-medical questions
- Emergency situations

### Response Tracking
- Validation results
- Response types
- Error messages
- User behavior patterns

## 🎯 Best Practices

### 1. Regular Updates
- Cập nhật patterns định kỳ
- Thêm keywords mới
- Cải thiện detection accuracy

### 2. Testing
- Test prompt injection scenarios
- Validate inappropriate content blocking
- Check emergency detection
- Verify medical content filtering

### 3. Monitoring
- Theo dõi security events
- Phân tích user behavior
- Cải thiện response quality

## 🚀 Future Enhancements

### 1. AI-based Detection
- Sử dụng ML model để detect harmful content
- Semantic analysis cho better accuracy
- Context-aware filtering

### 2. Dynamic Patterns
- Tự động cập nhật patterns
- Learning từ user interactions
- Adaptive security measures

### 3. Advanced Analytics
- Security dashboard
- Threat intelligence
- Behavioral analysis

## ⚠️ Important Notes

1. **Không bao giờ disable guardrails** trong production
2. **Luôn test** các patterns mới trước khi deploy
3. **Monitor** security events thường xuyên
4. **Cập nhật** patterns định kỳ
5. **Backup** cấu hình guardrails

## 📞 Support

Nếu phát hiện lỗ hổng bảo mật hoặc cần hỗ trợ:
- Tạo issue trong repository
- Liên hệ team phát triển
- Báo cáo security incident

---

**Lưu ý**: Tài liệu này được cập nhật thường xuyên để phản ánh các cải tiến bảo mật mới nhất.
