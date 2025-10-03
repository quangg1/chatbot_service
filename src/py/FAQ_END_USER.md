# Câu hỏi thường gặp (FAQ) dành cho Người Dùng Cuối (End User)

Tài liệu này giúp bạn sử dụng ứng dụng Health Care một cách dễ dàng và an toàn. Nội dung chỉ dành cho người dùng cuối, không chứa thông tin kỹ thuật nhạy cảm hay bí mật hệ thống.

## 1) Tổng quan ứng dụng
- ỨNG DỤNG TÊN LÀ HEALTH CARE
- Ứng dụng hỗ trợ mua sắm sản phẩm chăm sóc sức khỏe, xem tin tức y tế, và nhận tư vấn nhanh thông qua chatbot.
- Giao diện chính gồm: Trang chủ, Danh mục sản phẩm, Chi tiết sản phẩm, Giỏ hàng, Thanh toán, Tài khoản, Liên hệ, và Chính sách/Điều khoản.

## 2) Điều hướng nhanh (đường dẫn trang)
- Trang chủ: `/`
- Sản phẩm: `/products`
- Chi tiết sản phẩm: `/product/:id` (vào từ danh sách sản phẩm)
- Giỏ hàng: `/cart`
- Thanh toán: `/checkout`
- Đăng nhập: `/login`
- Đăng ký: `/register`
- Tài khoản (cần đăng nhập): `/account`
- Tin tức sức khỏe: `/health-news`
- Chính sách quyền riêng tư: `/privacy`
- Điều khoản dịch vụ: `/terms`
- Liên hệ: `/contact`
- Xóa tài khoản (cần đăng nhập): `/delete-account`
- Trò chuyện với trợ lý (cần đăng nhập, vai trò khách hàng): `/chat`

Lưu ý: Một số đường dẫn yêu cầu bạn đăng nhập đúng vai trò. Nếu bạn chưa đăng nhập, hệ thống sẽ chuyển bạn tới trang đăng nhập phù hợp.

## 3) Tạo tài khoản (Đăng ký)
- Vào trang Đăng ký: `/register`.
- Điền thông tin cần thiết: tên người dùng, email, mật khẩu và các trường yêu cầu khác.
- Kiểm tra lại thông tin và nhấn Đăng ký.
- Sau khi đăng ký thành công, bạn có thể đăng nhập để sử dụng đầy đủ tính năng.

Mẹo an toàn:
- Sử dụng mật khẩu mạnh, không dùng lại mật khẩu ở các dịch vụ khác.
- Không chia sẻ mã xác thực hay thông tin đăng nhập với người khác.

## 4) Đăng nhập
- Vào trang Đăng nhập: `/login`.
- Nhập email và mật khẩu đã đăng ký.
- Sau khi đăng nhập thành công, bạn sẽ thấy tên tài khoản và có thể truy cập trang `Tài khoản`, `Giỏ hàng`, `Thanh toán`, và `Trợ lý Chat`.

Nếu quên mật khẩu:
- Sử dụng tính năng quên mật khẩu (nếu hiển thị) hoặc liên hệ bộ phận hỗ trợ tại trang `/contact`.

## 5) Quản lý tài khoản
- Truy cập: `/account` (cần đăng nhập).
- Bạn có thể xem/cập nhật thông tin cá nhân, địa chỉ nhận hàng mặc định, và các thiết lập liên quan.
- Xóa tài khoản: vào `/delete-account` (cần xác nhận).

Cảnh báo: Xóa tài khoản là không thể hoàn tác. Hãy cân nhắc trước khi xác nhận.

## 6) Mua sắm & Thanh toán
- Duyệt sản phẩm tại `/products` hoặc tìm kiếm trong trang chủ.
- Chọn sản phẩm để vào trang chi tiết `/product/:id`, điều chỉnh số lượng và thêm vào giỏ.
- Vào giỏ hàng `/cart` để kiểm tra và cập nhật số lượng.
- Nhấn Thanh toán để sang `/checkout`:
  - Kiểm tra địa chỉ giao hàng (có thể chọn vị trí trên bản đồ nếu được hỗ trợ).
  - Chọn phương thức thanh toán (nếu được cung cấp).
  - Xác nhận đơn hàng.

Mẹo:
- Kiểm tra kỹ thông tin người nhận và địa chỉ trước khi đặt hàng.
- Theo dõi tình trạng đơn hàng qua email hoặc mục tài khoản (nếu có).

## 7) Chatbot hỗ trợ tức thì
- Bong bóng chat hiển thị ở góc dưới (bên phải) trên mọi trang sau khi bạn đăng nhập với vai trò khách hàng.
- Nhấn bong bóng để mở cửa sổ chat mini, đặt câu hỏi về sản phẩm, cách dùng, chính sách, v.v.
- Nhấn “Mở rộng sang trang chat đầy đủ” để xem lịch sử chi tiết tại `/chat`.
- Chatbot có thể tham chiếu tới các câu hỏi trước đó để trả lời liền mạch hơn.

Lưu ý:
- Chatbot mang tính hỗ trợ, không thay thế lời khuyên y tế chuyên môn. Trong trường hợp khẩn cấp, hãy gọi 115 hoặc tới cơ sở y tế gần nhất.
- Nếu dịch vụ chatbot chưa sẵn sàng, bạn sẽ nhận được thông báo và có thể thử lại sau.

## 8) Tin tức sức khỏe
- Truy cập `/health-news` để xem các bài viết sức khỏe tổng hợp.
- Chọn bài viết để xem chi tiết (nếu có trang chi tiết kèm nội dung an toàn).

## 9) Quyền riêng tư & Điều khoản
- Quyền riêng tư: xem tại `/privacy`.
- Điều khoản dịch vụ: xem tại `/terms`.

Nội dung này trình bày cách chúng tôi xử lý dữ liệu người dùng và các điều kiện khi sử dụng dịch vụ. Vui lòng đọc kỹ trước khi sử dụng.

## 10) Bảo mật tài khoản
- Không chia sẻ thông tin đăng nhập với bất kỳ ai.
- Luôn đăng xuất khỏi thiết bị công cộng sau khi sử dụng.
- Tránh nhấp vào các liên kết lạ mạo danh dịch vụ.
- Nếu nghi ngờ tài khoản bị truy cập trái phép, hãy đổi mật khẩu ngay và liên hệ hỗ trợ.

## 11) Lưu trữ cục bộ và cookie
- Ứng dụng có thể lưu một số dữ liệu tối thiểu trên trình duyệt (ví dụ: trạng thái đăng nhập, một phần lịch sử chat của riêng bạn) để nâng cao trải nghiệm.
- Bạn có thể xóa dữ liệu trình duyệt trong phần cài đặt của trình duyệt nếu muốn.

Chúng tôi không hiển thị hay công khai bất kỳ khóa/bí mật hệ thống nào trên giao diện người dùng.

## 12) Đơn hàng (Orders)
- Xem giỏ hàng tại `/cart`, cập nhật số lượng hoặc xóa sản phẩm.
- Sau khi đặt, bạn sẽ nhận thông báo xác nhận (trên UI hoặc email nếu có).
- Hủy đơn: vui lòng liên hệ tại `/contact` (nếu đơn chưa được xử lý).
- Theo dõi đơn: kiểm tra email hoặc mục tài khoản (nếu có cung cấp).

## 13) Thanh toán (Payments)
- Phương thức thanh toán khả dụng sẽ hiển thị tại `/checkout`.
- Nếu thanh toán thất bại: kiểm tra thẻ/tài khoản, kết nối mạng, hoặc thử lại sau.
- Tuyệt đối không chia sẻ thông tin thẻ với bất kỳ ai. Chúng tôi không yêu cầu bạn gửi thông tin nhạy cảm qua chat/email.

## 14) Giao hàng (Shipping)
- Vui lòng nhập địa chỉ chính xác, số điện thoại liên hệ.
- Thời gian giao hàng phụ thuộc địa chỉ và đơn vị vận chuyển.
- Nếu giao hàng chậm: kiểm tra mục tài khoản (nếu có) hoặc liên hệ `/contact`.

## 15) Đổi trả & Hoàn tiền (Returns & Refunds)
- Điều kiện đổi trả/hoàn tiền (nếu áp dụng) sẽ được nêu trong `Điều khoản` và/hoặc trên trang chi tiết sản phẩm.
- Vui lòng giữ nguyên tem/nhãn và hóa đơn (nếu có) khi yêu cầu đổi trả.

## 16) Khuyến mãi & Mã giảm giá
- Nếu có, mã giảm giá sẽ được áp dụng tại giỏ hàng hoặc trang thanh toán.
- Mỗi mã có điều kiện riêng (thời hạn, số lượng tối thiểu, sản phẩm áp dụng...).

## 17) Trợ năng & Tương thích (Accessibility)
- Ứng dụng hỗ trợ trên trình duyệt hiện đại (Chrome, Edge, Firefox...).
- Mẹo: Phóng to cỡ chữ trong trình duyệt hoặc dùng chế độ cao tương phản (nếu cần) để dễ đọc hơn.

## 18) Xử lý sự cố (Troubleshooting)
- Không đăng nhập được: kiểm tra email/mật khẩu, thử đặt lại mật khẩu, kiểm tra kết nối mạng.
- Trang không hiển thị đúng: làm mới trang (Ctrl/Cmd + R), xóa cache trình duyệt, thử trình duyệt khác.
- Lỗi khi đặt hàng/thanh toán: thử lại sau vài phút; nếu vẫn lỗi, liên hệ `/contact`.
- Chatbot chậm/không phản hồi: đợi thêm hoặc thử lại sau; nếu kéo dài, dùng trang `/contact`.

## 19) Câu hỏi khác
- Không vào được trang yêu cầu đăng nhập? Hãy đăng nhập lại tại `/login` và thử lại.
- Không nhận được email? Kiểm tra thư mục Spam/Quảng cáo.
- Cần hỗ trợ thêm? Truy cập `/contact`.

---

Nếu bạn có thêm câu hỏi, hãy liên hệ qua trang `/contact`. Chúng tôi luôn sẵn sàng hỗ trợ.
