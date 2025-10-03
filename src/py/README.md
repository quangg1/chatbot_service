# RAG Medical Chatbot với LangChain + Guardrails + Llama-Med42 8B

Dự án chatbot y tế tiên tiến sử dụng RAG (Retrieval-Augmented Generation) với Llama-Med42 8B, tích hợp LangChain và NeMo Guardrails để đảm bảo an toàn và tối ưu hóa.

## Tính năng chính

- 🤖 **Llama-Med42 8B**: Model y tế chuyên biệt qua HuggingFace API
- 🔍 **RAG System**: Tích hợp MongoDB + FAISS cho retrieval
- 🛡️ **NeMo Guardrails**: Bảo vệ an toàn và kiểm soát nội dung
- 🔗 **LangChain**: Tích hợp và tối ưu hóa workflow
- ⚕️ **Medical Safety**: Kiểm tra khẩn cấp y tế và disclaimer
- 💰 **Price Intelligence**: Phân tích và so sánh giá sản phẩm
- 🎯 **Intent Detection**: Phân loại câu hỏi (price/product/general)
- 🔄 **Fallback Mechanism**: Fallback cho câu hỏi general

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình HuggingFace Token

1. Lấy token từ [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. Copy file `env_template.txt` thành `.env`
3. Điền token vào file `.env`:

```bash
cp env_template.txt .env
# Chỉnh sửa .env và thêm token của bạn
HF_TOKEN=your_actual_token_here
```

### 3. Chạy ứng dụng

#### 🌐 Web Interface (Khuyến nghị cho demo)
```bash
streamlit run streamlit_app.py
```
Hoặc sử dụng script:
- **Windows**: `run_streamlit.bat`
- **Linux/Mac**: `./run_streamlit.sh`

#### 💻 Command Line Interface
```bash
python main.py
```

## Cấu trúc dự án

```
Colab_Notebooks/
├── main.py                 # File chính chạy RAG chatbot (CLI)
├── streamlit_app.py        # Streamlit web app (UI)
├── hf_api_llm.py          # HuggingFace API wrapper
├── rag_system.py          # RAG system với MongoDB + FAISS
├── medical_guardrails.py  # Medical guardrails và intent detection
├── actions.py              # Custom actions cho Guardrails
├── config.yml              # Cấu hình Guardrails
├── flows.co                # Colang flows cho Guardrails
├── requirements.txt        # Dependencies
├── run_streamlit.bat       # Script khởi động Windows
├── .streamlit/
│   └── config.toml         # Cấu hình Streamlit
├── STREAMLIT_README.md     # Hướng dẫn Streamlit
├── SECURITY_README.md      # Tài liệu bảo mật chi tiết
└── README.md              # Hướng dẫn này
```

## 🔁 Quy trình (flow) xử lý của Chatbot

Luồng dưới đây áp dụng cho cả CLI (`main.py`) và UI (`streamlit_app.py`), với vài khác biệt nhỏ về hiển thị.

1) Giao diện → Thu nhận câu hỏi người dùng
- UI gọi `RAGMedicalChatbot.generate_response_stream(user_message)` để stream từng chunk trả lời.

2) Guardrails đầu vào (Input validation)
- `UnifiedGuardrails.validate_input(user_message)` → ủy quyền cho `MedicalGuardrails.validate_input`:
  - Chặn prompt injection, nội dung không phù hợp, hành vi bất hợp pháp.
  - Nhận diện khẩn cấp (emergency) và trả lời cố định nếu phát hiện.
  - Cho phép small-talk an toàn (ví dụ giới thiệu tên) qua `override_response`.

3) Cập nhật profile người dùng ngắn gọn (nếu có)
- `RAGMedicalChatbot._update_user_profile(user_message)` trích tên, lưu `user_profile`.

4) Phân loại intent 2 tầng (Intent → Sub-intent)
- Tầng 1: `UnifiedGuardrails.detect_intent(query)` (thực thi `MedicalGuardrails.detect_intent`).
  - Nếu có bất kỳ từ khóa thuộc hợp nhất website (web_keywords = faq ∪ product ∪ price ∪ extra routes), intent sẽ là `web`.
  - Nếu câu hỏi mang tính y khoa, intent sẽ là `medical` (hoặc các intent khác nếu không phải web).
- Tầng 2 (khi intent = `web`): suy diễn sub-intent trong `main.py`:
  - Nếu chứa từ khóa giá → `price`
  - Else nếu chứa từ khóa sản phẩm → `product`
  - Else mặc định → `faq`

5) Truy xuất tài liệu (Retrieval)
- Nếu sub-intent = `faq`:
  - Ưu tiên `RAGSystem._retrieve_faq_fallback(query, k=8)` (lọc chỉ tài liệu `type="faq"` hoặc `source="FAQ_END_USER.md"` bằng cosine nội bộ), nếu rỗng sẽ fallback `retrieve_documents`.
- Với `product`/`price`/`medical`/`general`:
  - `RAGSystem.retrieve_documents(query, k=5)` sử dụng `$vectorSearch` trên MongoDB Atlas.

6) Xây dựng ngữ cảnh (Context)
- `RAGSystem.build_context(docs, intent, original_query=...)`:
  - Lọc theo intent (price/product/medical/faq) và ngưỡng điểm phù hợp.
  - Với `faq`: ưu tiên nhiều mảnh (tối đa 8), hiển thị rõ nhãn `[FAQ] <title>: <text>` để giữ route như `/login`, `/privacy`,…
  - Nếu `faq` mà không có kết quả, tự động fallback `_retrieve_faq_fallback` lần nữa.

7) Chọn Prompt và sinh câu trả lời (Generation)
- Nhánh đặc biệt:
  - `price` → `self.price_prompt`
  - `followup` → `self.followup_prompt` (mở rộng dựa trên câu trả lời liền trước)
- Nhánh hợp nhất: `self.answer_by_intent_prompt` (điều kiện hóa theo intent/sub-intent, kèm ràng buộc grounding):
  - Với `product`/`price`: nếu không có ngữ cảnh liên quan thì trả đúng câu: "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
  - Với `faq`: thêm tiền tố cố định “Tôi là Chatbot Web HEALTH CARE…” khi có ngữ cảnh để ổn định phong cách trả lời.
- Tất cả đều dùng streaming qua `HuggingFaceAPILLM.stream_call`.

8) Hậu xử lý và Guardrails đầu ra (Output validation)
- `UnifiedGuardrails.validate_output(response, is_medical=...)` → ủy quyền `MedicalGuardrails.validate_output`:
  - Tự động thêm medical disclaimer cho câu trả lời y khoa (không áp dụng với `greeting`/`faq`).
  - Làm sạch và cắt độ dài an toàn.

9) Bộ nhớ hội thoại ngắn hạn (Conversation memory)
- `RAGMedicalChatbot._add_to_history(user, bot)` lưu tối đa N lượt gần nhất.
- `_update_memory` trích xuất nhẹ entities/chủ đề/sản phẩm để giữ mạch.

10) Hoàn tất streaming → UI hiển thị
- Streamlit thêm từng chunk và cập nhật lịch sử, hiển thị trạng thái.

Sơ đồ rút gọn
```
User → validate_input → (emergency? small-talk?) → detect_intent →
  if web → sub-intent (faq/price/product)
Retrieval (faq-only or vectorSearch) → build_context → select prompt → stream LLM →
validate_output → update memory/history → UI render
```

## ⚙️ LangChain trong quy trình (tích hợp tối ưu)

Vai trò của LangChain: quản lý prompt và backbone pipeline (Runnable chains), giúp tái sử dụng và mở rộng dễ dàng, đồng thời vẫn giữ routing/guardrails tùy biến.

- Thành phần chính (trong `main.py`):
  - `self.system_prompt`, `self.price_prompt`, `self.followup_prompt`, `self.answer_by_intent_prompt`
  - `_setup_chains()` khởi tạo 3 chain dạng Runnable:
    - `answer_chain`: `answer_by_intent_prompt → LLM.stream_call`
    - `price_chain`: `price_prompt → LLM.stream_call`
    - `followup_chain`: `followup_prompt → LLM.stream_call`

- Dòng chảy khi có LangChain:
  1) Guardrails (input) → Intent tầng 1 (`web`) và sub-intent (`faq/product/price`)
  2) Retrieval (FAQ-only hoặc vectorSearch) → `build_context`
  3) Chọn chain theo nhánh:
     - price → `price_chain`
     - followup → `followup_chain`
     - còn lại → `answer_chain` (điều kiện hóa bằng intent/sub-intent, có grounding)
  4) Streaming qua `HuggingFaceAPILLM.stream_call` (OpenAI-compatible)
  5) Guardrails (output) + memory

- Lợi ích:
  - Tách rõ Prompt → LLM → Parser (ở đây stream trực tiếp), dễ kiểm thử/ghi log
  - Thay đổi prompt/logic mà không đụng tới routing retrieval
  - Mở rộng thêm chain (ví dụ: `medical_chain`, `summarize_chain`) mà không ảnh hưởng luồng chính

Gợi ý tinh chỉnh nâng cao:
- Thêm `StrOutputParser()` khi cần hậu xử lý không-stream, hoặc kết hợp Runnable parallel cho multi-query retrieval.
- Dùng `RunnableBranch` để chọn chain theo intent thay vì if-else (giữ hiện tại để dễ đọc và kiểm soát).

## 🧩 Danh sách hàm/chức năng chính theo module

- `main.py / class RAGMedicalChatbot`
  - `generate_response_stream(user_message)`
  - `_update_user_profile`, `_should_reuse_products`, `_extract_product_names_from_docs`
  - `_build_conversation_context`, `_build_memory_context`, `_update_memory`, `_add_to_history`
  - `_generate_price_response`, `_generate_followup_response`, `_generate_greeting_response`, `_generate_rag_response`

- `medical_guardrails.py / class MedicalGuardrails`
  - `validate_input(user_input)` → kiểm tra an toàn đầu vào
  - `detect_intent(query)` → phát hiện intent (hợp nhất `web` + các intent khác)
  - `_fallback_intent_detection`, `_semantic_intent` (tối ưu từ khóa + ngữ nghĩa)
  - `validate_output(response, is_medical)` → chèn disclaimer y tế và lọc an toàn

- `unified_guardrails.py / class UnifiedGuardrails`
  - Khởi tạo NeMo từ `config.yml` + `flows.co` khi có, fallback an toàn nếu thiếu
  - `validate_input`, `validate_output`, `detect_intent`, `extract_entities`
  - `is_rails_active`, `get_rails`, `run_flow` (tùy chọn)

- `rag_system.py / class RAGSystem`
  - `embed_query(text)` → tính embedding (cache cục bộ)
  - `retrieve_documents(query, k)` → `$vectorSearch` MongoDB Atlas
  - `_retrieve_faq_fallback(query, k)` → chỉ lấy tài liệu FAQ bằng cosine nội bộ
  - `build_context(docs, intent, original_query)` → lọc/ngắt đoạn theo intent, ưu tiên FAQ
  - `extract_price_info(docs)` → tiện ích trích giá

- `hf_api_llm.py / class HuggingFaceAPILLM`
  - `stream_call(prompt)` → streaming từ HF Router (OpenAI-compatible)
  - `_call(prompt)` → non-streaming (nếu cần)

- `embed_faq.py`
  - Đọc `FAQ_END_USER.md` → tách section → embed BGE-M3 → upsert vào MongoDB `embedding` với `type='faq'`, `source='FAQ_END_USER.md'`.

## ✅ Quy tắc quan trọng (ràng buộc)
- `product/price` bắt buộc có ngữ cảnh (grounding). Nếu thiếu → trả về câu chuẩn “Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.”
- `faq` chỉ dùng tài liệu website/FAQ; không thêm medical disclaimer.
- Nhân cách (persona): “Chatbot Web HEALTH CARE”, luôn thể hiện rõ khi câu hỏi thuộc nhóm website.

## 🛡️ Tính năng bảo mật

### Guardrails đa lớp:

1. **🚫 Prompt Injection Protection**: Chặn các cố gắng jailbreak và bypass
2. **🚫 Inappropriate Content Filter**: Lọc nội dung tình dục và không phù hợp
3. **🚫 Illegal Activities Filter**: Chặn thông tin về hoạt động bất hợp pháp
4. **✅ Medical Content Validation**: Chỉ cho phép câu hỏi y tế hợp lệ
5. **🚨 Emergency Detection**: Tự động phát hiện tình huống khẩn cấp
6. **📝 Medical Disclaimer**: Tự động thêm disclaimer y tế
7. **🔒 Professional Boundaries**: Duy trì ranh giới chuyên môn y tế

### Security Features:

- **Multi-layer validation**: Kiểm tra input qua nhiều lớp
- **Pattern-based filtering**: Sử dụng regex patterns để detect harmful content
- **Medical keyword validation**: Chỉ accept câu hỏi y tế
- **Output sanitization**: Làm sạch response trước khi trả về
- **Emergency routing**: Tự động chuyển hướng tình huống khẩn cấp

### Custom Actions:

- `validate_input()`: Kiểm tra input đa lớp
- `check_medical_emergency()`: Kiểm tra tình huống khẩn cấp
- `add_medical_disclaimer()`: Thêm disclaimer y tế
- `log_conversation()`: Ghi log cuộc hội thoại

## Sử dụng

1. Khởi động chatbot: `python main.py`
2. Nhập câu hỏi y tế của bạn
3. Bot sẽ trả lời với thông tin y tế an toàn và chính xác
4. Gõ `exit` hoặc `quit` để thoát

## Ví dụ sử dụng

```
You: Tôi bị đau đầu, có nên uống thuốc gì không?
Bot: Đau đầu có thể do nhiều nguyên nhân khác nhau. Tôi khuyên bạn nên:
1. Nghỉ ngơi và uống đủ nước
2. Tránh ánh sáng mạnh và tiếng ồn
3. Có thể dùng paracetamol theo hướng dẫn

⚠️ Medical Disclaimer: This information is for educational purposes only...

You: Tôi bị đau ngực dữ dội!
Bot: This appears to be a medical emergency. Please call emergency services immediately (911 in the US, 115 in Vietnam) or go to the nearest emergency room. I cannot provide emergency medical care.
```

## 📚 Tài liệu bổ sung

- **STREAMLIT_README.md**: Hướng dẫn chi tiết về Streamlit web app
- **SECURITY_README.md**: Tài liệu bảo mật và guardrails đầy đủ

## Lưu ý quan trọng

- ⚠️ **Không thay thế bác sĩ**: Chatbot chỉ cung cấp thông tin giáo dục
- 🚨 **Khẩn cấp**: Luôn gọi cấp cứu cho tình huống khẩn cấp
- 🔒 **Bảo mật**: Không chia sẻ thông tin cá nhân y tế
- 📊 **Logging**: Cuộc hội thoại được ghi log để cải thiện
- 🛡️ **Guardrails**: Hệ thống bảo vệ đa lớp chống prompt injection và nội dung có hại

## Troubleshooting

### Lỗi API Token
```
ValueError: HUGGINGFACE_TOKEN environment variable is required
```
**Giải pháp**: Kiểm tra file `.env` và đảm bảo token được thiết lập đúng.

### Lỗi kết nối API
```
API Error: Connection timeout
```
**Giải pháp**: Kiểm tra kết nối internet và token HuggingFace.

### Lỗi dependencies
```
ModuleNotFoundError: No module named 'nemoguardrails'
```
**Giải pháp**: Chạy `pip install -r requirements.txt`

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## License

MIT License - Xem file LICENSE để biết thêm chi tiết.
