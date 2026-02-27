# PPTX-Slides — AI Presentation Generator

[English](README.md) | **Tiếng Việt**

**PPTX-Slides** là một công cụ mạnh mẽ giúp bạn tạo các bài trình chiếu PowerPoint chuyên nghiệp một cách nhanh chóng bằng cách tận dụng sức mạnh của Google Gemini AI. Bạn có thể tạo slide từ các tệp tài liệu có sẵn hoặc đơn giản là đưa ra các yêu cầu bằng văn bản (prompt).

## ✨ Tính năng chính

- 🚀 **Tạo slide thông minh:** Tạo bài trình chiếu hoàn chỉnh từ các tệp tài liệu đầu vào hoặc ý tưởng ngắn gọn.
- 📄 **Hỗ trợ đa định dạng:** Tải lên tệp **Word (.docx)** hoặc **PDF (.pdf)** để AI tự động tóm tắt và chuyển đổi thành slide.
- 💬 **Chỉnh sửa tương tác:** Sử dụng prompt để yêu cầu AI chỉnh sửa, thêm hoặc xóa slide ngay trên giao diện web.
- 🎨 **Giao diện hiện đại:** UI tối giản, trực quan với chế độ tối (Dark Mode) và hiệu ứng glassmorphism.
- 🎭 **Tùy chọn Theme:** Lựa chọn các chủ để màu sắc khác nhau cho bài trình chiếu.
- 📥 **Tải xuống tức thì:** Xem trước các slide và tải về tệp `.pptx` để sử dụng ngay.

## 📺 Video Demo

![PPPTX Slides Demo Recording](assets/demo_recording.webp)

## 🛠️ Công nghệ sử dụng

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Engine:** [Google Gemini AI](https://ai.google.dev/)
- **Frontend:** HTML5, Modern CSS (Vanilla), JavaScript
- **Xử lý tài liệu:** `python-pptx`, `python-docx`, `PyPDF2`

## 🚀 Cài đặt và Sử dụng

### 1. Cài đặt môi trường

Yêu cầu Python 3.9 trở lên.

```bash
# Clone dự án
git clone https://github.com/viduvan/PPTX-Slides
cd PPTX-Slides

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu hình API Key

Tạo một tệp `.env` trong thư mục gốc hoặc thiết lập biến môi trường:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

### 3. Chạy ứng dụng

```bash
python run.py
```

Sau đó, mở trình duyệt và truy cập: `http://localhost:8000`

## 🤝 Đóng góp

Mọi đóng góp nhằm cải thiện dự án đều được trân trọng! Hãy gửi Issue hoặc Pull Request nếu bạn có ý tưởng mới.

- **Người phát triển:** [ChimSe](https://github.com/viduvan)
- **Giấy phép:** [MIT License](LICENSE)
- **Ngày hoàn thành:** 27/02/2026

---

Đừng quên để lại một 🌟 nếu bạn thấy dự án này hữu ích!