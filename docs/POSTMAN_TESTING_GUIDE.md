# 🧪 Hướng Dẫn Test API HPC Drive - Postman

## ⚡ SETUP NHANH (5 phút)

### Bước 1: Chạy Migration Database
```bash
cd /home/dudo/hpc_drive/hpc_drive

# Backup
sqlite3 drive.db ".backup backup_before_repo_type.sql"

# Chạy migration
python scripts/migrate_add_repository_type.py
# Nhập: yes
```

### Bước 2: Start HPC Drive Server
```bash
cd /home/dudo/hpc_drive/hpc_drive
uvicorn src.hpc_drive.main:app --reload --port 7777
```

**Kiểm tra:** http://localhost:7777/docs (Swagger UI)

---

## 🔑 LẤY JWT TOKEN

### Login System-Management
```
POST http://localhost:8080/api/v1/login
Content-Type: application/json

{
  "username": "lecturer1",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGci....",
  "token_type": "bearer"
}
```

**📋 Copy `access_token` này!**

### Setup Postman Environment

Tạo Environment "HPC Drive":
- `base_url`: `http://localhost:7777`
- `auth_url`: `http://localhost:8080`
- `token`: `<paste_token_here>`
- `system_management_url`: `http://localhost:8080` (hoặc docker: `http://auth-service:8080`)

**⚠️ Quan trọng:** Nếu chạy bằng Docker, HPC Drive cần biết đúng URL của System-Management:
```bash
# File .env trong hpc_drive/
SYSTEM_MANAGEMENT_URL=http://localhost:8080
# Hoặc nếu Docker network:
SYSTEM_MANAGEMENT_URL=http://auth-service:8080
```

---

## 📝 TEST API

### ✅ TEST 1: CLASS STORAGE

#### 1.1. Lấy Danh Sách Lớp Của Tôi
```
GET {{base_url}}/api/v1/class-storage/my-classes
Authorization: Bearer {{token}}
```

**Kết quả mong đợi:**
```json
[
  {
    "class_id": 1,
    "class_name": "CNTT K15",
    "role": "LECTURER",
    "has_upload_permission": true
  }
]
```

**✅ Check:** Lớp hiển thị đúng với lecturer đang dạy

---

#### 1.2. Tự Động Tạo Thư Mục Lớp
```
POST {{base_url}}/api/v1/class-storage/auto-generate/1
Authorization: Bearer {{token}}
```

**📌 `1` = class_id từ bước 1.1**

**Kết quả:**
```json
{
  "class_id": 1,
  "folders_created": [
    {"name": "Class_1_Root", "path": "/"},
    {"name": "Thông tin lớp học", "path": "/Thông tin lớp học"},
    {"name": "Kỳ 1", "path": "/Kỳ 1"},
    {"name": "Kỳ 2", "path": "/Kỳ 2"}
  ],
  "message": "Successfully created X folders"
}
```

**✅ Check:**
- Folders được tạo (Root, Kỳ 1-4, Thông tin lớp)
- Môn học tự động fetch từ System-Management

**⚠️ Chỉ chạy 1 lần!** Lần 2 sẽ báo lỗi "already exist"

---

#### 1.3. Xem Danh Sách Files/Folders
```
GET {{base_url}}/api/v1/class-storage/1/items
Authorization: Bearer {{token}}
```

**Kết quả:**
```json
[
  {
    "item_id": "abc-123-...",
    "name": "Kỳ 1",
    "item_type": "FOLDER",
    "is_system_generated": true,
    "is_locked": true
  }
]
```

---

#### 1.4. Upload File
```
POST {{base_url}}/api/v1/class-storage/1/upload
Authorization: Bearer {{token}}
Content-Type: multipart/form-data

Body (form-data):
  file: [Chọn file PDF/image]
  parent_id: [Optional - ID folder từ 1.3]
```

**Kết quả:**
```json
{
  "message": "File uploaded successfully",
  "item_id": "def-456...",
  "filename": "slide_bai1.pdf",
  "size": 123456
}
```

**✅ Check:**
- File upload thành công
- **Notification tự động gửi đến sinh viên** (check logs server)
- File lưu vào `uploads/class_storage/1/`

**🧪 Test Permission:**
- Login bằng student account → Upload → **Should FAIL (403)**
- Login GV khác lớp → Upload → **Should FAIL (403)**

---

### ✅ TEST 2: DEPARTMENT STORAGE

#### 2.1. Lấy Thông Tin Khoa Của Tôi
```
GET {{base_url}}/api/v1/department-storage/my-department
Authorization: Bearer {{token}}
```

**Kết quả:**
```json
{
  "department_id": 1,
  "department_name": "Khoa Công nghệ thông tin",
  "has_upload_permission": true,
  "is_own_department": true
}
```

**✅ Check:** Department ID đúng với JWT token

---

#### 2.2. Upload File Vào Khoa
```
POST {{base_url}}/api/v1/department-storage/1/upload
Authorization: Bearer {{token}}
Content-Type: multipart/form-data

Body:
  file: [Chọn file]
```

**Kết quả:**
```json
{
  "message": "File uploaded successfully",
  "item_id": "ghi-789...",
  "filename": "quy_che.pdf"
}
```

**🧪 Test Permission:**
- Login GV khoa KHÁC → Upload dept 1 → **Should FAIL (403)**
- Login student → **Should FAIL (403)**

---

#### 2.3. Xem Files Trong Khoa
```
GET {{base_url}}/api/v1/department-storage/1/items
Authorization: Bearer {{token}}
```

---

### ✅ TEST 3: SIGNING WORKFLOW

#### 3.1. Tạo Yêu Cầu Ký
**Yêu cầu:** Phải có file PDF đã upload (dùng item_id từ test 1.4 hoặc 2.2)

```
POST {{base_url}}/api/v1/signing/request
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "drive_item_id": "def-456..."
}
```

**Kết quả:**
```json
{
  "request_id": "jkl-012...",
  "drive_item_id": "def-456...",
  "current_status": "DRAFT",
  "file_name": "slide_bai1.pdf",
  "requester_name": "lecturer1"
}
```

**✅ Check:** Status = DRAFT

**🧪 Test Validation:**
- Dùng file KHÔNG phải PDF → **Should FAIL (400)**
- Dùng file không tồn tại → **Should FAIL (404)**

---

#### 3.2. Submit Yêu Cầu
```
PUT {{base_url}}/api/v1/signing/jkl-012.../submit
Authorization: Bearer {{token}}
```

**Kết quả:**
```json
{
  "request_id": "jkl-012...",
  "current_status": "PENDING"
}
```

**✅ Check:** Status: DRAFT → PENDING

---

#### 3.3. Xem Yêu Cầu Của Tôi
```
GET {{base_url}}/api/v1/signing/my-requests
Authorization: Bearer {{token}}
```

**Kết quả:**
```json
[
  {
    "request_id": "jkl-012...",
    "current_status": "PENDING",
    "file_name": "slide_bai1.pdf",
    "created_at": "2026-01-22T..."
  }
]
```

---

#### 3.4. [ADMIN] Xem Yêu Cầu Đang Chờ
**⚠️ Cần login bằng ADMIN account trước!**

```
POST {{auth_url}}/api/v1/login
{
  "username": "admin",
  "password": "admin_password"
}
# Copy admin token mới
```

```
GET {{base_url}}/api/v1/signing/pending
Authorization: Bearer {{admin_token}}
```

**Kết quả:**
```json
[
  {
    "request_id": "jkl-012...",
    "current_status": "PENDING",
    "requester_name": "lecturer1",
    "file_name": "slide_bai1.pdf"
  }
]
```

**🧪 Test:** Login bằng lecturer → GET /pending → **Should FAIL (403)**

---

#### 3.5. [ADMIN] Phê Duyệt
```
PUT {{base_url}}/api/v1/signing/jkl-012.../approve
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "admin_comment": "Đã duyệt - OK"
}
```

**Kết quả:**
```json
{
  "request_id": "jkl-012...",
  "current_status": "APPROVED",
  "approver_id": 1,
  "approver_name": "admin",
  "admin_comment": "Đã duyệt - OK",
  "approved_at": "2026-01-22T..."
}
```

**✅ Check:**
- Status: PENDING → APPROVED
- approver_id được set
- approved_at có timestamp
- **Notification GỬI ĐẾN lecturer requester** (check logs)

---

#### 3.6. [ADMIN] Từ Chối (Alternative)
```
PUT {{base_url}}/api/v1/signing/jkl-012.../reject
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "admin_comment": "Từ chối - sai format"
}
```

**Kết quả:**
```json
{
  "current_status": "REJECTED",
  "admin_comment": "Từ chối - sai format"
}
```

**✅ Check:** Notification gửi với lý do từ chối

---

## 📊 CHECKLIST HOÀN CHỈNH

### Setup
- [ ] Migration chạy thành công
- [ ] Server start port 7777
- [ ] Swagger UI accessible

### Authentication
- [ ] Login System-Management (port 8080)
- [ ] JWT token hoạt động
- [ ] Invalid token → 401

### Class Storage (5 tests)
- [ ] Get my classes
- [ ] Auto-generate folders (chỉ 1 lần)
- [ ] List items
- [ ] Upload file (lecturer)
- [ ] Notification sent (check logs)
- [ ] Student cannot upload (403)

### Department Storage (3 tests)
- [ ] Get my department
- [ ] Upload to own department
- [ ] Cannot upload to other dept (403)

### Signing Workflow (6 tests)
- [ ] Create request (DRAFT)
- [ ] Submit (PENDING)
- [ ] List my requests
- [ ] Admin list pending
- [ ] Admin approve + notification
- [ ] Admin reject + notification

### Error Handling
- [ ] 401 - No/invalid token
- [ ] 403 - Wrong permissions
- [ ] 404 - Not found
- [ ] 400 - Validation errors

---

## 🐛 TROUBLESHOOTING

### Lỗi 401 Unauthorized
**Nguyên nhân:** Token hết hạn (default 1 giờ)

**Giải pháp:**
```
POST http://localhost:8080/api/v1/login
# Lấy token mới
```

### Lỗi 403 Forbidden
**Check:**
- User role đúng chưa? (STUDENT/LECTURER/ADMIN)
- Department ID khớp chưa?
- Có permission không?

### Lỗi 500 Internal Server Error
**Check logs server:**
```bash
# Terminal đang chạy uvicorn
# Xem error details
```

### Migration lỗi
```bash
# Restore backup
rm drive.db
sqlite3 drive.db ".restore backup_before_repo_type.sql"

# Chạy lại
python scripts/migrate_add_repository_type.py
```

### Notification không gửi
**Check:**
1. System-Management service chạy chưa?
2. Xem logs HPC Drive server
3. Upload vẫn thành công (notification = non-blocking)

---

## 📝 TIPS

### Sử dụng Postman Collection Variables

```javascript
// Pre-request Script (Tab "Pre-request Script")
// Tự động refresh token nếu hết hạn
pm.sendRequest({
    url: pm.environment.get("auth_url") + "/api/v1/login",
    method: 'POST',
    header: 'Content-Type: application/json',
    body: {
        mode: 'raw',
        raw: JSON.stringify({
            username: "lecturer1",
            password: "your_password"
        })
    }
}, function (err, res) {
    pm.environment.set("token", res.json().access_token);
});
```

### Save Request Examples
- Mỗi test thành công → Save as Example
- Dễ review sau này

### Test Flow Thực Tế
1. **Morning:** Lecturer upload materials
2. **Students:** Receive notification → Download
3. **Afternoon:** Lecturer create signing request
4. **Admin:** Approve → Notification sent

---

**✅ Sau khi test xong 14 endpoints → Backend Phase 1A HOÀN THÀNH 100%!**
