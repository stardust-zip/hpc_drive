# Learning Service Intergration


## Tài liệu Tích hợp Service Lưu trữ Giáo trình (HPC Drive)

**Tổng quan:**
Module Giáo trình (Curriculum) trên `hpc_drive` cho phép lưu trữ tài liệu môn học tách biệt.

* **Giảng viên:** Có quyền Upload và Xóa file trong môn học.
* **Sinh viên:** Chỉ được Xem/Tải file nếu đã đăng ký môn học đó (Hệ thống Drive sẽ tự động gọi lại API của Learning Service để kiểm tra việc đăng ký môn).

### 1. Cấu hình

* **Base URL của Drive Service:** `http://hpc_drive:7777` (hoặc cấu hình trong `.env`).
* **Yêu cầu Header:** Bắt buộc gửi kèm `Authorization: Bearer <user_token>` của người dùng hiện tại để Drive xác định danh tính (Lecturer/Student).

### 2. Cơ chế Xác thực Sinh viên (Lưu ý quan trọng)

Khi Sinh viên gọi API lấy danh sách file, `hpc_drive` sẽ tự động gọi ngược lại Learning Service qua API sau để kiểm tra quyền:

* `GET /api/v1/attendance/students/{student_id}/courses`
* **Yêu cầu:** Team Learning đảm bảo API này hoạt động và trả về danh sách môn học có field `code` (mã môn).

---

## 3. Danh sách API (Endpoints)

**A. Upload Tài liệu (Dành cho Giảng viên)**

* **URL:** `POST /api/v1/curriculum/{subject_code}/upload`
* **Ví dụ:** `POST /api/v1/curriculum/INT3306/upload`
* **Body (Multipart):** `file` (Binary file)
* **Response:**
```json
{
    "item_id": "uuid-...",
    "name": "slide_chuong_1.pdf",
    "storage_path": "..."
}

```



**B. Lấy danh sách Tài liệu (Dành cho cả GV và SV)**

* **URL:** `GET /api/v1/curriculum/{subject_code}`
* **Ví dụ:** `GET /api/v1/curriculum/INT3306`
* **Cơ chế:**
* Nếu là GV: Trả về toàn bộ file.
* Nếu là SV: Drive sẽ check xem SV có môn `INT3306` không. Nếu không -> Trả về lỗi 403.


* **Response:** Danh sách các file trong thư mục môn học.

**C. Xóa Tài liệu (Chỉ GV)**

* **URL:** `DELETE /api/v1/curriculum/{item_id}`
