# Hướng dẫn dịch (cho worker)

Dịch sách "Project Management, 2nd Edition" (Abdullah Oguz) sang tiếng Việt để làm bản song ngữ.

## Việc của mỗi task
1. Đọc `chunks/NN.json`: object `{ "pXXXX": "đoạn tiếng Anh", ... }`.
2. Ghi `out/NN.json`: **cùng đúng bộ khóa**, giá trị là bản dịch tiếng Việt. KHÔNG chép lại tiếng Anh, không thêm khóa, không bỏ khóa.
   File lớn: được phép ghi thành nhiều lượt (ví dụ dịch từng phần rồi gộp bằng script Python nhỏ), nhưng kết quả cuối là một file JSON hợp lệ, UTF-8, `ensure_ascii=False`.
3. Chạy `python3 tools/check.py NN` cho đến khi báo `OK`.
4. Commit chỉ file `out/NN.json`, message: `Dịch chunk NN`.

## Quy tắc dịch
- Văn phong sách giáo khoa quản trị dự án tiếng Việt: rõ ràng, tự nhiên, không dịch word-by-word. Dịch đủ ý, không tóm tắt, không bỏ câu.
- Theo bảng thuật ngữ `GLOSSARY.md`. Lần đầu gặp thuật ngữ quan trọng trong chunk có thể giữ tiếng Anh trong ngoặc: "bên liên quan (stakeholder)".
- Giữ nguyên: tên riêng, tên tổ chức, tên tài liệu/sách, tên phần mềm và menu/nút bấm (MS Project: "Task", "Gantt Chart View"…), viết tắt (PMBOK, PMO, WBS, ROI…), số liệu, công thức, ký hiệu chú thích `[1]`, URL, định dạng Markdown (`**đậm**`, `*nghiêng*`, liên kết), ký tự `↵`.
- Câu hỏi trắc nghiệm: dịch cả câu hỏi và phương án, giữ nhãn a), b), c)…
- Đoạn là prompt/đầu ra AI, mã hoặc yêu cầu kỹ thuật: vẫn dịch phần văn xuôi, giữ nguyên mã.
- Đoạn chỉ có tên riêng/tiêu đề không cần dịch: giữ nguyên chuỗi gốc.
