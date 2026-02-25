# Phân tích luồng hoạt động dự án odin-slides

## Tổng quan

**odin-slides** là một công cụ CLI bằng Python, sử dụng **OpenAI GPT-3.5 Turbo** để tự động tạo bài trình chiếu PowerPoint (`.pptx`) từ tài liệu Word (`.docx`) hoặc từ prompt của người dùng.

## Kiến trúc Module

```mermaid
graph TD
    A["main.py<br/>Entry Point & CLI"] --> B["utils.py<br/>Đọc file Word, logging, formatting"]
    A --> C["llm_ops.py<br/>Gọi API OpenAI"]
    A --> D["presentation.py<br/>Tạo/chỉnh sửa PPTX"]
    D --> C
    D --> B
    C --> B
```

| Module | Chức năng chính |
|--------|----------------|
| `odin_slides/main.py` | Entry point, parse CLI args, đọc/tóm tắt tài liệu Word |
| `odin_slides/llm_ops.py` | Gọi OpenAI API để tóm tắt nội dung và sinh nội dung slide |
| `odin_slides/presentation.py` | Tạo/cập nhật file PPTX, quản lý vòng lặp tương tác với user |
| `odin_slides/utils.py` | Đọc file `.docx`, format log/message, trích xuất JSON |

---

## Luồng hoạt động chi tiết

### Bước 1: Khởi chạy CLI (`main.py:13-33`)

```bash
odin-slides -t <template.pptx> -o <output_name> [-i <input.docx>] [-s <session.pkl>]
```

| Tham số | Bắt buộc | Mô tả |
|---------|----------|-------|
| `-t` | ✅ | File PPTX làm template (lấy layout/theme) |
| `-o` | ✅ | Tên file output (không cần extension) |
| `-i` | ❌ | File Word đầu vào để tạo slide |
| `-s` | ❌ | File session `.pkl` để phục hồi phiên làm việc |

---

### Bước 2: Xử lý tài liệu đầu vào (`main.py:46-71`)

```mermaid
flowchart TD
    A["Có file input (-i)?"] -->|Có| B["read_word_file()"]
    A -->|Không| G["word_content = rỗng"]
    B --> C{"Số từ > 5000?"}
    C -->|Không| F["Dùng trực tiếp word_content"]
    C -->|Có| D["read_big_word_file()<br/>Chia thành ~10 chunks"]
    D --> E["get_LLM_summarization()<br/>Tóm tắt từng chunk qua GPT"]
    E --> F2["Ghép các bản tóm tắt<br/>thành word_content"]
```

- **Tài liệu nhỏ** (≤ 5000 từ): đọc trực tiếp toàn bộ nội dung
- **Tài liệu lớn** (> 5000 từ): chia thành ~10 phần, mỗi phần được gửi tới GPT để tóm tắt, sau đó ghép lại

---

### Bước 3: Tạo nội dung slide bằng LLM (`presentation.py:224-351`)

Hàm `build_slides_with_llm()` là **trung tâm** của luồng xử lý:

```mermaid
flowchart TD
    A{"Có session file?"} -->|Có| B["Tải session từ .pkl<br/>Phục hồi slide_deck_history"]
    A -->|Không| C{"File output đã tồn tại?"}
    C -->|Có| D["Đọc slide hiện có từ file PPTX<br/>get_latest_slide_deck()"]
    C -->|Không| E["Hỏi user: What shall I do for you?"]
    E --> F["Gửi prompt + word_content<br/>tới get_chat_response()"]
    F --> G["Parse JSON response thành slide_deck"]
    B --> H
    D --> H
    G --> H

    H["VÒNG LẶP TƯƠNG TÁC"]
    H --> I["create_presentation()<br/>Tạo file PPTX"]
    I --> J["Hỏi user: Bạn muốn chỉnh sửa gì?"]
    J --> K{"-1?"}
    K -->|Có| L["Undo: quay lại phiên bản trước"]
    L --> H
    K -->|Không| M["get_latest_slide_deck()<br/>Đọc lại PPTX để bắt thay đổi thủ công"]
    M --> N["get_chat_response()<br/>Gửi yêu cầu chỉnh sửa tới LLM"]
    N --> O["Merge kết quả: thêm/sửa/xóa slide"]
    O --> H
```

> **Lưu ý quan trọng:**
> Dự án hỗ trợ **chỉnh sửa thủ công** file PPTX: sau mỗi vòng lặp, tool sẽ đọc lại file PPTX để phát hiện các thay đổi do user tự sửa bằng PowerPoint.

---

### Bước 4: Gọi OpenAI API (`llm_ops.py`)

Có **2 hàm chính**:

#### `get_LLM_summarization()` — Tóm tắt tài liệu
- Model: `gpt-3.5-turbo`
- Prompt: yêu cầu rút gọn bài viết, giữ nguyên các điểm chính
- Dùng ở Bước 2 khi tài liệu > 5000 từ

#### `get_chat_response()` — Sinh/sửa nội dung slide
- Model: `gpt-3.5-turbo`
- System prompt quy định format JSON response:
  ```json
  [{"slide_number": 1.0, "title": "...", "content": "...", "narration": "..."}]
  ```
- Quy tắc đặc biệt:
  - **Thêm slide**: dùng slide_number thập phân (2.1, 2.2...)
  - **Xóa slide**: đặt slide_number thành số âm
  - **Sửa slide**: giữ nguyên slide_number

---

### Bước 5: Tạo file PPTX (`presentation.py:104-166`)

Hàm `create_presentation()`:
1. Load template PPTX → lấy layout "Title and Content"
2. Xóa tất cả slide cũ trong template
3. Với mỗi slide trong `slide_deck`:
   - Tạo slide mới với layout từ template
   - Đặt **title** và **content** vào placeholder
   - Đặt **narration** vào phần Notes
4. Lưu file → mở file (nếu OS hỗ trợ)

---

### Bước 6: Quản lý Session (`presentation.py:337-350`)

- Khi kết thúc (hoặc lỗi/Ctrl+C), session được lưu vào file `.pkl`
- Session chứa: `slide_deck_history` (lịch sử undo) + `word_content`
- Có thể phục hồi bằng tham số `-s`

---

## Logic merge slide (`presentation.py:296-332`)

Khi LLM trả về kết quả chỉnh sửa:

1. Slide có cùng `slide_number` → **thay thế** bằng phiên bản mới
2. Slide có `slide_number` âm → **xóa** slide tương ứng
3. Slide có `slide_number` thập phân (vd: 2.1) → **chèn** vào giữa
4. Sắp xếp lại theo `slide_number` → đánh số lại từ 1

---

## Tóm tắt luồng end-to-end

```
User chạy CLI
    ↓
Đọc file Word (nếu có) → tóm tắt nếu > 5000 từ
    ↓
User nhập prompt đầu tiên → GPT sinh slide dạng JSON
    ↓
Tạo file PPTX từ template + nội dung slide
    ↓
╔══════════════════════════════════════╗
║  VÒNG LẶP:                          ║
║  1. Hiển thị PPTX cho user xem      ║
║  2. User nhập yêu cầu chỉnh sửa    ║
║  3. Đọc lại PPTX (phát hiện sửa    ║
║     thủ công)                        ║
║  4. GPT xử lý → merge kết quả      ║
║  5. Tạo lại PPTX                    ║
║  (Nhập -1 để undo)                  ║
╚══════════════════════════════════════╝
    ↓
Ctrl+C hoặc lỗi → Lưu session (.pkl)
```
