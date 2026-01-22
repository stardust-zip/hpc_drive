# 📋 FINAL REVIEW - HPC Drive Phase 1 Implementation

> **Document Purpose**: Tổng hợp cuối cùng tất cả decisions, scope, technical specs trước khi bắt đầu implementation.

---

## 🎯 EXECUTIVE SUMMARY

### Project Goal
Mở rộng HPC Drive từ **Personal Storage** sang hệ thống quản lý tài liệu toàn diện với:
- **Class Storage** (Kho tài liệu lớp)
- **Department Storage** (Kho tài liệu khoa)
- **Signing Workflow** (Trình ký văn bản)
- **Integration với Công Văn**

### Timeline Estimate
- **Phase 1A - Backend**: 3-4 ngày
- **Phase 1B - Frontend**: 2-3 ngày
- **Phase 1C - Integration & Testing**: 1-2 ngày
- **Total**: 7-10 ngày

### Current Status
✅ **100% Planning Complete** - Ready for implementation

---

## ✅ ARCHITECTURAL DECISIONS

### 1. Database Schema Approach
**Decision:** Thêm `repository_type` vào DriveItem (Single Table Strategy)

**Rationale:**
- ✅ Đơn giản hơn multiple tables
- ✅ Dễ query cross-repository
- ✅ Theo đúng class diagram

**Implementation:**
```python
class DriveItem:
    # Existing fields (giữ nguyên)
    item_id, name, item_type, owner_id, parent_id, is_trashed, ...
    
    # NEW fields
    repository_type: RepositoryType  # PERSONAL | CLASS | DEPARTMENT
    repository_context_id: int | None  # class_id hoặc department_id
    owner_type: OwnerType  # STUDENT | LECTURER | ADMIN
    process_status: ProcessStatus  # PENDING_UPLOAD | SCANNING | READY | INFECTED | ERROR
    is_system_generated: bool  # Folder tự động tạo
    is_locked: bool  # Ngăn xóa/sửa
```

### 2. Integration với Công Văn
**Decision:** Team Công Văn tự quản lý DispatchAttachments

**Rationale:**
- ✅ Loose coupling
- ✅ HPC Drive không dính nghiệp vụ công văn
- ✅ Chỉ expose API: get item info + download

**HPC Drive cung cấp:**
- `GET /api/v1/drive/items/{id}` - Lấy thông tin file
- `GET /api/v1/drive/download/{id}` - Download file

**Team Công Văn làm:**
- Tự tạo OfficialDispatch
- Tự tạo DispatchAttachments (lưu drive_item_id)
- Tự quản lý workflow

### 3. SigningRequest Workflow
**Decision:** KHÔNG auto-create OfficialDispatch

**Workflow:**
1. Giảng viên tạo SigningRequest → DRAFT
2. Submit → PENDING
3. Admin approve → APPROVED (kết thúc tại HPC Drive)
4. Công văn tự gọi API để lấy file nếu cần

**Rationale:**
- ✅ Đơn giản
- ✅ Ít dependency
- ✅ Công văn linh hoạt hơn

---

## 🎯 FEATURE SCOPE

### ✅ Phase 1 - IMPLEMENT

#### 1. Core Models & Schema
- ✅ Update DriveItem (6 fields mới)
- ✅ SigningRequest model
- ✅ Enums: RepositoryType, OwnerType, ProcessStatus, SigningStatus
- ✅ Migration scripts

#### 2. Class Storage
- ✅ Auto-generate folders từ System-Management API
  - Kỳ 1, Kỳ 2, Kỳ 3, Kỳ 4
  - Các môn học (từ Courses API)
  - Thông tin lớp học
- ✅ Upload (chỉ GV dạy lớp đó)
- ✅ Download (GV + Sinh viên)
- ✅ List/View folders
- ✅ Notification khi GV upload

#### 3. Department Storage
- ✅ Auto-generate folders
  - Văn bản quy phạm
  - Ngân hàng đề thi
  - Hồ sơ giảng viên
  - Các Bộ môn (từ Departments API)
  - Luận văn/Đồ án
- ✅ Upload (GV của khoa)
- ✅ Download (GV của khoa)
- ✅ Delete (Admin only)

#### 4. Personal Storage
- ✅ Giữ nguyên functionality hiện tại
- ✅ Update `repository_type = PERSONAL`

#### 5. Signing Workflow
- ✅ Lecturer: Create request, Submit
- ✅ Admin: Approve, Reject
- ✅ Status tracking
- ✅ Notification

#### 6. Malware Scanning
- ✅ Mock (delay 2s → READY)
- ✅ Workflow: PENDING_UPLOAD → SCANNING → READY

#### 7. File Preview
- ✅ PDF viewer (react-pdf)
- ✅ Image viewer (JPG, PNG, GIF, WebP)
- ✅ Text viewer (.txt)
- ✅ Markdown viewer (.md)

#### 8. System-Management Integration
- ✅ Courses API
- ✅ Departments API
- ✅ Class Lecturers API (permission check)
- ✅ Class Students API
- ✅ Notification API (bulk)

#### 9. Frontend Pages
- ✅ Class Storage UI
- ✅ Department Storage UI
- ✅ Signing Workflow UI (My Requests, Pending Approval)
- ✅ File Preview Modal

---

### ❌ Phase 1 - KHÔNG IMPLEMENT

- ❌ Storage Quota management
- ❌ ClamAV malware scanning (chỉ mock)
- ❌ DOCX/XLSX/PPTX preview
- ❌ Video preview
- ❌ FILE_SHARED notification
- ❌ DispatchAttachments model (team công văn làm)
- ❌ Background task queue (dùng inline API calls)

---

## 🔐 PERMISSIONS MODEL

### Class Storage
| Role | Can Upload | Can Download | Can Delete |
|------|-----------|--------------|------------|
| **Admin** | ✅ | ✅ | ✅ |
| **Lecturer (dạy lớp)** | ✅ | ✅ | ✅ |
| **Lecturer (không dạy)** | ❌ | ❌ | ❌ |
| **Student (trong lớp)** | ❌ | ✅ | ❌ |

**Permission Check:**
```python
# Call API: GET /api/v1/classes/lecturer/{lecturerId}
# Check: class_id in response
```

### Department Storage
| Role | Can Upload | Can Download | Can Delete |
|------|-----------|--------------|------------|
| **Admin** | ✅ | ✅ | ✅ |
| **Lecturer (khoa mình)** | ✅ | ✅ | ❌ |
| **Lecturer (khoa khác)** | ❌ | ❌ | ❌ |
| **Student** | ❌ | ❌ | ❌ |

**Permission Check:**
```python
# From JWT: lecturer.department_id
# Check: lecturer.department_id == storage.repository_context_id
```

### Personal Drive
| Role | Can CRUD Own Files | Can View Others |
|------|-------------------|-----------------|
| **Admin** | ✅ | ✅ (all users) |
| **Lecturer** | ✅ | ❌ |
| **Student** | ✅ | ❌ |

---

## 🔗 SYSTEM-MANAGEMENT API INTEGRATION

### 1. Courses API
```
GET /api/v1/attendance/courses
  ?semester_id={int}
  &lecturer_id={int}
  &department_id={int}
```

**Usage:** Auto-generate folder môn học trong Class Storage

### 2. Departments API
```
GET /api/v1/departments
```

**Usage:** Auto-generate folder "Các Bộ môn" trong Department Storage

### 3. Class Lecturers API
```
GET /api/v1/classes/lecturer/{lecturerId}
```

**Usage:** Permission check - GV có dạy lớp này không?

### 4. Class Students API
```
GET /api/v1/student/class/{classId}
```

**Usage:** Lấy danh sách sinh viên để gửi notification

### 5. Notification API
```
POST /api/v1/notifications/send-bulk
```

**Usage:** Gửi notification khi:
- GV upload vào Class Storage → notify sinh viên
- Admin approve/reject SigningRequest → notify GV

**Format:**
```json
{
  "notifications": [
    {
      "user_id": 1,
      "title": "File mới",
      "message": "...",
      "type": "FILE_UPLOAD",
      "priority": "NORMAL",
      "metadata": {...}
    }
  ]
}
```

---

## 🔔 NOTIFICATION TRIGGERS

| Event | Recipients | Type | Priority |
|-------|-----------|------|----------|
| GV upload to Class Storage | Tất cả sinh viên lớp | FILE_UPLOAD | NORMAL |
| Admin approve SigningRequest | Giảng viên requester | SIGNING_APPROVED | HIGH |
| Admin reject SigningRequest | Giảng viên requester | SIGNING_REJECTED | HIGH |

**Implementation:** Inline API calls (không background queue)

**Error Handling:**
```python
try:
    await notify_students(...)
except Exception as e:
    logger.error(f"Notification failed: {e}")
    # Upload vẫn thành công
```

---

## 🗄️ DATABASE SCHEMA CHANGES

### Enums MỚI
```python
class RepositoryType(str, Enum):
    PERSONAL = "PERSONAL"
    CLASS = "CLASS"
    DEPARTMENT = "DEPARTMENT"

class OwnerType(str, Enum):
    STUDENT = "STUDENT"
    LECTURER = "LECTURER"
    ADMIN = "ADMIN"

class ProcessStatus(str, Enum):
    PENDING_UPLOAD = "PENDING_UPLOAD"
    SCANNING = "SCANNING"
    READY = "READY"
    INFECTED = "INFECTED"
    ERROR = "ERROR"

class SigningStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
```

### DriveItem - ADDED Fields
```python
+ repository_type: RepositoryType = RepositoryType.PERSONAL
+ repository_context_id: int | None = None
+ owner_type: OwnerType
+ process_status: ProcessStatus = ProcessStatus.PENDING_UPLOAD
+ is_system_generated: bool = False
+ is_locked: bool = False
```

### SigningRequest - NEW Model
```python
class SigningRequest(Base):
    request_id: UUID (PK)
    drive_item_id: UUID (FK → DriveItem)
    requester_id: int (FK → User)
    approver_id: int (FK → User)
    current_status: SigningStatus = DRAFT
    signed_file_path: str | None
    admin_comment: str | None
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None
```

### User, FileMetadata, SharePermission - GIỮ NGUYÊN

---

## 📁 FILE STRUCTURE

### Backend Changes
```
hpc_drive/
├── src/hpc_drive/
│   ├── models.py                    [MODIFY] Add fields, SigningRequest
│   ├── schemas.py                   [MODIFY] Add Pydantic schemas
│   ├── crud.py                      [MODIFY] Add CRUD functions
│   ├── integrations/                [NEW]
│   │   ├── __init__.py
│   │   └── system_management.py    [NEW] API integration service
│   ├── api/v1/
│   │   ├── router_drive.py          [MODIFY] Update for repository_type
│   │   ├── router_class_storage.py  [NEW]
│   │   ├── router_dept_storage.py   [NEW]
│   │   └── router_signing.py        [NEW]
│   └── migrations/                  [NEW] Alembic migrations
```

### Frontend Changes
```
fe-portal/
├── src/
│   ├── app/authorized/
│   │   ├── class-storage/           [NEW]
│   │   │   └── page.tsx
│   │   ├── department-storage/      [NEW]
│   │   │   └── page.tsx
│   │   └── signing/                 [NEW]
│   │       ├── my-requests/
│   │       └── pending/
│   ├── components/drive/            [NEW]
│   │   ├── FilePreviewModal.tsx
│   │   ├── UploadZone.tsx
│   │   └── FolderTree.tsx
│   └── features/drive/              [NEW]
│       ├── services/driveService.ts
│       ├── types/index.ts
│       └── hooks/useDrive.ts
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 1A: Backend Core (3-4 ngày)

#### Day 1: Models & Database
- [ ] Update `models.py`: Add 6 fields to DriveItem
- [ ] Create `SigningRequest` model
- [ ] Add new Enums
- [ ] Create Alembic migration
- [ ] Run migration, verify schema

#### Day 2: Integration Service
- [ ] Create `integrations/system_management.py`
- [ ] Implement `SystemManagementService` class
- [ ] Test API calls với System-Management
- [ ] Error handling

#### Day 3: Class Storage API
- [ ] Create `router_class_storage.py`
- [ ] `POST /class-storage/auto-generate/{class_id}` - Generate folders
- [ ] `GET /class-storage/{class_id}/items` - List items
- [ ] `POST /class-storage/{class_id}/upload` - Upload + notify
- [ ] `GET /class-storage/my-classes` - List classes
- [ ] Permission checks

#### Day 4: Department Storage + Signing
- [ ] Create `router_dept_storage.py`
- [ ] Department Storage APIs
- [ ] Create `router_signing.py`
- [ ] SigningRequest CRUD
- [ ] Notification integration
- [ ] Test all endpoints

---

### Phase 1B: Frontend (2-3 ngày)

#### Day 5: Class Storage UI
- [ ] Class storage page
- [ ] Folder tree component
- [ ] Upload component (lecturer only)
- [ ] Download handler
- [ ] Routing & navigation

#### Day 6: Department Storage + Signing UI
- [ ] Department storage page
- [ ] Signing request dialog
- [ ] My requests page
- [ ] Pending approval page (admin)
- [ ] Status badges

#### Day 7: File Preview + Polish
- [ ] File preview modal
- [ ] PDF viewer (react-pdf)
- [ ] Image viewer
- [ ] Text/Markdown viewer
- [ ] UI polish, responsive design

---

### Phase 1C: Integration & Testing (1-2 ngày)

#### Day 8: Integration Testing
- [ ] Test với System-Management APIs
- [ ] Test notification flow
- [ ] Test permission checks
- [ ] Test auto-folder generation

#### Day 9: Bug Fixes & Documentation
- [ ] Fix bugs found in testing
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Demo preparation

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

### Environment Setup
- [ ] `SYSTEM_MANAGEMENT_URL` env variable
- [ ] Database backup
- [ ] Test environment ready

### Dependencies
- [ ] `httpx` (async HTTP client)
- [ ] `react-pdf` (frontend)
- [ ] `react-markdown` (frontend)

### API Access
- [ ] Có JWT token để test System-Management APIs
- [ ] Có quyền gọi các endpoints (admin token)

### Team Coordination
- [ ] Đã thông báo team công văn về API endpoints
- [ ] Đã thông báo timeline

---

## ⚠️ RISKS & MITIGATION

### Risk 1: System-Management API Response Format Khác
**Mitigation:** 
- Implement với try-except
- Log response để debug
- Mock data fallback

### Risk 2: Notification API Chậm
**Mitigation:**
- Wrap trong try-except
- Upload vẫn thành công nếu notification fail
- Consider background task Phase 2

### Risk 3: Permission Check Phức Tạp
**Mitigation:**
- Simple check: class_id in lecturer_classes
- Cache lecturer_classes trong session

---

## 📊 SUCCESS METRICS

### Technical Metrics
- [ ] All APIs return 200 OK
- [ ] Auto-folder generation works
- [ ] Notification delivered successfully
- [ ] File preview works for PDF/images/text/markdown
- [ ] Zero critical bugs

### User Metrics
- [ ] GV có thể upload to class storage
- [ ] Sinh viên nhận được notification
- [ ] Admin có thể approve signing request
- [ ] File preview UX smooth

---

## 🎯 FINAL APPROVAL CHECKLIST

### Architecture & Design
- [x] Database schema finalized
- [x] API integration documented
- [x] Permission model clear
- [x] Notification strategy defined

### Scope Management
- [x] Phase 1 scope confirmed
- [x] Phase 2 features deferred
- [x] Dependencies identified

### Technical Readiness
- [x] All API endpoints known
- [x] Integration service designed
- [x] File structure planned
- [x] Timeline estimated

### Stakeholder Alignment
- [x] 12 critical questions answered
- [x] Team công văn coordination plan
- [x] System-Management API access confirmed

---

## ✅ FINAL DECISIONS (User Confirmed)

**1. Database Migration:**
- ✅ **CÓ backup** - BẮT BUỘC
- ✅ Dump DB trước khi migrate: `backup_before_repo_type.sql`
- ✅ Test migration trên dev environment trước

**2. Testing Strategy:**
- ✅ **Có unit tests** cho "xương sống":
  - SystemManagementService
  - Permission check (GV có dạy lớp không)
  - Upload + notify flow
- ✅ KHÔNG cần full coverage UI Phase 1

**3. Deployment:**
- ✅ **Backend trước** - LUÔN LUÔN
- ✅ Workflow: Deploy BE → Test API → FE gắn vào

**4. Documentation:**
- ✅ **CÓ Swagger** - 100%
- ✅ Swagger = giao diện dev + hợp đồng FE/BE + tài liệu sống
- ✅ User guide tiếng Việt

---

## 🚀 READY TO START?

Nếu bạn APPROVE document này, tôi sẽ:

1. ✅ Bắt đầu Day 1: Update models.py
2. ✅ Create migration scripts
3. ✅ Implement SystemManagementService
4. ✅ Create Class Storage APIs
5. ✅ ... theo roadmap

**Bạn có muốn sửa gì CUỐI CÙNG trước khi tôi bắt đầu code không?**
