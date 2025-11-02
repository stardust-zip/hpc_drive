# 🔐 Auth Module API Documentation

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

Hầu hết endpoints yêu cầu JWT token trong header:

```
Authorization: Bearer {JWT_TOKEN}
```

---

# 📑 Table of Contents

1. [Authentication APIs](#1-authentication-apis)
2. [Student Management APIs](#2-student-management-apis)
3. [Lecturer Management APIs](#3-lecturer-management-apis)
4. [Department Management APIs](#4-department-management-apis)
5. [Class Management APIs](#5-class-management-apis)

---

# 1. Authentication APIs

## 1.1. Login (Api Login Tổng)

**POST** `/login`

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
    "username": "sv_SV001",
    "password": "123456"
    "user_type": "student"

    Hoặc

    "username": "gv_GV001",
    "password": "123456"
    "user_type": "lecturer"

}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "user_type": "student",
    "student_code": "SV001",
    "class_id": 5,
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "account": {
        "username": "sv_SV001",
        "is_admin": false
    },
    "classroom": {
        "id": 5,
        "class_name": "CNTT K15",
        "class_code": "CNTT15"
    }
}
```

**Response Error (401):**

```json
{
    "message": "Thông tin đăng nhập không chính xác"
}
```

---

---

## 1.1. Login Student

**POST** `/login/student`

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
    "username": "sv_SV001",
    "password": "123456"
}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "user_type": "student",
    "student_code": "SV001",
    "class_id": 5,
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "account": {
        "username": "sv_SV001",
        "is_admin": false
    },
    "classroom": {
        "id": 5,
        "class_name": "CNTT K15",
        "class_code": "CNTT15"
    }
}
```

**Response Error (401):**

```json
{
    "message": "Thông tin đăng nhập không chính xác"
}
```

---

## 1.2. Login Lecturer

**POST** `/login/lecturer`

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
    "username": "gv_GV001",
    "password": "123456"
}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Trần Thị B",
    "email": "tranthib@email.com",
    "user_type": "lecturer",
    "lecturer_code": "GV001",
    "department_id": 3,
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "account": {
        "username": "gv_GV001",
        "is_admin": false
    },
    "department": {
        "id": 3,
        "name": "Khoa Công nghệ thông tin",
        "code": "CNTT"
    }
}
```

**Response Error (401):**

```json
{
    "message": "Thông tin đăng nhập không chính xác"
}
```

---

## 1.3. Get Current User Info

**GET** `/me`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success - Student (200):**

```json
{
    "message": "Thông tin user",
    "data": {
        "id": 1,
        "full_name": "Nguyễn Văn A",
        "email": "nguyenvana@email.com",
        "user_type": "student",
        "student_info": {
            "student_code": "SV001",
            "class": {
                "id": 5,
                "class_name": "CNTT K15",
                "class_code": "CNTT15"
            }
        },
        "account": {
            "username": "sv_SV001",
            "is_admin": false
        }
    }
}
```

**Response Success - Lecturer (200):**

```json
{
    "message": "Thông tin user",
    "data": {
        "id": 1,
        "full_name": "Trần Thị B",
        "email": "tranthib@email.com",
        "user_type": "lecturer",
        "lecturer_info": {
            "lecturer_code": "GV001",
            "unit": {
                "id": 3,
                "name": "Khoa CNTT",
                "type": "department"
            }
        },
        "account": {
            "username": "gv_GV001",
            "is_admin": true
        }
    }
}
```

**Response Error (401):**

```json
{
    "message": "Token không hợp lệ",
    "error": "Expired token"
}
```

---

## 1.4. Refresh Token

**POST** `/refresh`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Token được làm mới thành công",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response Error (400):**

```json
{
    "message": "Không thể làm mới token",
    "error": "Invalid token"
}
```

---

## 1.5. Logout

**POST** `/logout`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Đăng xuất thành công"
}
```

**Response Error (500):**

```json
{
    "message": "Có lỗi xảy ra khi đăng xuất",
    "error": "Error message"
}
```

---

# 2. Student Management APIs

## 2.1. Get All Students (Admin Only)

**GET** `/students`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 1,
        "full_name": "Nguyễn Văn A",
        "email": "nguyenvana@email.com",
        "phone": "0123456789",
        "student_code": "SV001",
        "birth_date": "2002-01-15",
        "gender": "Nam",
        "address": "Hà Nội",
        "class_id": 5,
        "classroom": {
            "id": 5,
            "class_name": "CNTT K15",
            "class_code": "CNTT15"
        },
        "account": {
            "username": "sv_SV001",
            "is_admin": false
        }
    }
]
```

---

## 2.2. Create Student (Admin Only)

**POST** `/students`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Nguyễn Văn B",
    "email": "nguyenvanb@email.com",
    "phone": "0987654321",
    "student_code": "SV002",
    "birth_date": "2002-05-20",
    "gender": "Nam",
    "address": "Hà Nội",
    "class_id": 5
}
```

**Response Success (201):**

```json
{
    "message": "Tạo sinh viên thành công",
    "data": {
        "id": 2,
        "full_name": "Nguyễn Văn B",
        "email": "nguyenvanb@email.com",
        "phone": "0987654321",
        "student_code": "SV002",
        "birth_date": "2002-05-20",
        "gender": "Nam",
        "address": "Hà Nội",
        "class_id": 5,
        "created_at": "2024-01-15T10:30:00.000000Z",
        "updated_at": "2024-01-15T10:30:00.000000Z"
    },
    "account_info": {
        "username": "sv_SV002",
        "password": "123456"
    }
}
```

**Response Error (500):**

```json
{
    "message": "Có lỗi xảy ra khi tạo sinh viên",
    "error": "Duplicate entry 'SV002' for key 'student_code'"
}
```

---

## 2.3. Get Student By ID (Admin Only)

**GET** `/students/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone": "0123456789",
    "student_code": "SV001",
    "birth_date": "2002-01-15",
    "gender": "Nam",
    "address": "Hà Nội",
    "class_id": 5,
    "classroom": {
        "id": 5,
        "class_name": "CNTT K15",
        "class_code": "CNTT15",
        "department": {
            "id": 3,
            "name": "Khoa CNTT"
        }
    },
    "account": {
        "id": 1,
        "username": "sv_SV001"
    }
}
```

**Response Error (404):**

```json
{
    "message": "Không tìm thấy sinh viên"
}
```

---

## 2.4. Update Student (Admin Only)

**PUT** `/students/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Nguyễn Văn A (Updated)",
    "email": "nguyenvana.updated@email.com",
    "phone": "0111222333",
    "address": "Hà Nội - Updated",
    "class_id": 6
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật sinh viên thành công",
    "data": {
        "id": 1,
        "full_name": "Nguyễn Văn A (Updated)",
        "email": "nguyenvana.updated@email.com",
        "phone": "0111222333",
        "address": "Hà Nội - Updated",
        "class_id": 6,
        "updated_at": "2024-01-15T11:00:00.000000Z"
    }
}
```

---

## 2.5. Delete Student (Admin Only)

**DELETE** `/students/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Xóa sinh viên thành công"
}
```

**Response Error (404):**

```json
{
    "message": "Không tìm thấy sinh viên"
}
```

---

## 2.6. Get Own Profile (Student)

**GET** `/student/profile`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone": "0123456789",
    "student_code": "SV001",
    "birth_date": "2002-01-15",
    "gender": "Nam",
    "address": "Hà Nội",
    "class_id": 5,
    "classroom": {
        "id": 5,
        "class_name": "CNTT K15",
        "class_code": "CNTT15"
    }
}
```

---

## 2.7. Update Own Profile (Student)

**PUT** `/student/profile`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Nguyễn Văn A",
    "phone": "0999888777",
    "address": "Hà Nội - New Address"
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật thông tin thành công",
    "data": {
        "id": 1,
        "full_name": "Nguyễn Văn A",
        "phone": "0999888777",
        "address": "Hà Nội - New Address"
    }
}
```

---

## 2.8. Get Students By Class ID

**GET** `/student/class/{classId}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 1,
        "full_name": "Nguyễn Văn A",
        "student_code": "SV001",
        "email": "nguyenvana@email.com",
        "class_id": 5
    },
    {
        "id": 2,
        "full_name": "Trần Thị B",
        "student_code": "SV002",
        "email": "tranthib@email.com",
        "class_id": 5
    }
]
```

---

# 3. Lecturer Management APIs

## 3.1. Get All Lecturers (Admin Only)

**GET** `/lecturers`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 1,
        "full_name": "Trần Thị B",
        "email": "tranthib@email.com",
        "phone": "0123456789",
        "lecturer_code": "GV001",
        "gender": "Nữ",
        "address": "Hà Nội",
        "department_id": 3,
        "experience_number": 5,
        "birth_date": "1985-05-15",
        "department": {
            "id": 3,
            "name": "Khoa CNTT",
            "code": "CNTT"
        },
        "account": {
            "username": "gv_GV001",
            "is_admin": true
        }
    }
]
```

---

## 3.2. Create Lecturer (Admin Only)

**POST** `/lecturers`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Nguyễn Văn C",
    "email": "nguyenvanc@email.com",
    "phone": "0987654321",
    "lecturer_code": "GV002",
    "gender": "Nam",
    "address": "Hà Nội",
    "department_id": 3,
    "experience_number": 3,
    "birth_date": "1990-08-20"
}
```

**Response Success (201):**

```json
{
    "message": "Tạo giảng viên thành công",
    "data": {
        "id": 2,
        "full_name": "Nguyễn Văn C",
        "email": "nguyenvanc@email.com",
        "phone": "0987654321",
        "lecturer_code": "GV002",
        "gender": "Nam",
        "address": "Hà Nội",
        "department_id": 3,
        "experience_number": 3,
        "birth_date": "1990-08-20",
        "created_at": "2024-01-15T10:30:00.000000Z"
    },
    "account_info": {
        "username": "gv_GV002",
        "password": "123456"
    }
}
```

---

## 3.3. Get Lecturer By ID (Admin Only)

**GET** `/lecturers/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Trần Thị B",
    "email": "tranthib@email.com",
    "phone": "0123456789",
    "lecturer_code": "GV001",
    "gender": "Nữ",
    "address": "Hà Nội",
    "department_id": 3,
    "experience_number": 5,
    "department": {
        "id": 3,
        "name": "Khoa CNTT",
        "code": "CNTT"
    },
    "account": {
        "username": "gv_GV001",
        "is_admin": true
    },
    "classes": [
        {
            "id": 5,
            "class_name": "CNTT K15",
            "class_code": "CNTT15"
        }
    ]
}
```

---

## 3.4. Update Lecturer (Admin Only)

**PUT** `/lecturers/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Trần Thị B (Updated)",
    "email": "tranthib.updated@email.com",
    "phone": "0111222333",
    "address": "Hà Nội - Updated",
    "experience_number": 6
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật giảng viên thành công",
    "data": {
        "id": 1,
        "full_name": "Trần Thị B (Updated)",
        "email": "tranthib.updated@email.com",
        "phone": "0111222333",
        "experience_number": 6,
        "updated_at": "2024-01-15T11:00:00.000000Z"
    }
}
```

---

## 3.5. Delete Lecturer (Admin Only)

**DELETE** `/lecturers/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Xóa giảng viên thành công"
}
```

---

## 3.6. Update Admin Status (Admin Only)

**PATCH** `/lecturers/{id}/admin-status`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "is_admin": true
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật quyền admin thành công",
    "data": {
        "id": 1,
        "full_name": "Trần Thị B",
        "account": {
            "is_admin": true
        }
    }
}
```

---

## 3.7. Get Own Profile (Lecturer)

**GET** `/lecturer/profile`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 1,
    "full_name": "Trần Thị B",
    "email": "tranthib@email.com",
    "phone": "0123456789",
    "lecturer_code": "GV001",
    "department": {
        "id": 3,
        "name": "Khoa CNTT"
    },
    "classes": [
        {
            "id": 5,
            "class_name": "CNTT K15"
        }
    ]
}
```

---

## 3.8. Update Own Profile (Lecturer)

**PUT** `/lecturer/profile`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "full_name": "Trần Thị B",
    "phone": "0999888777",
    "address": "Hà Nội - New"
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật thông tin thành công",
    "data": {
        "id": 1,
        "full_name": "Trần Thị B",
        "phone": "0999888777",
        "address": "Hà Nội - New"
    }
}
```

---

# 4. Department Management APIs

## 4.1. Get All Departments (Admin Only)

**GET** `/departments`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 1,
        "name": "Trường Đại học",
        "code": "DHK",
        "parent_id": null,
        "level": 1,
        "staff_count": 0,
        "created_at": "2024-01-01T00:00:00.000000Z"
    },
    {
        "id": 3,
        "name": "Khoa Công nghệ thông tin",
        "code": "CNTT",
        "parent_id": 1,
        "level": 2,
        "staff_count": 15,
        "created_at": "2024-01-01T00:00:00.000000Z"
    }
]
```

---

## 4.2. Get Departments Tree (Admin Only)

**GET** `/departments/tree`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 1,
        "name": "Trường Đại học",
        "code": "DHK",
        "level": 1,
        "parent_id": null,
        "staff_count": 0
    },
    {
        "id": 3,
        "name": "├── Khoa CNTT",
        "code": "CNTT",
        "level": 2,
        "parent_id": 1,
        "staff_count": 15
    },
    {
        "id": 5,
        "name": "    ├── Bộ môn Khoa học máy tính",
        "code": "KHMT",
        "level": 3,
        "parent_id": 3,
        "staff_count": 8
    }
]
```

---

## 4.3. Create Department (Admin Only)

**POST** `/departments`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "name": "Khoa Kinh tế",
    "code": "KT",
    "parent_id": 1,
    "level": 2
}
```

**Response Success (201):**

```json
{
    "message": "Tạo department thành công",
    "data": {
        "id": 4,
        "name": "Khoa Kinh tế",
        "code": "KT",
        "parent_id": 1,
        "level": 2,
        "created_at": "2024-01-15T10:30:00.000000Z"
    }
}
```

---

## 4.4. Get Department By ID (Admin Only)

**GET** `/departments/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 3,
    "name": "Khoa CNTT",
    "code": "CNTT",
    "parent_id": 1,
    "level": 2,
    "staff_count": 15,
    "lecturers": [
        {
            "id": 1,
            "full_name": "Trần Thị B",
            "lecturer_code": "GV001"
        }
    ],
    "classes": [
        {
            "id": 5,
            "class_name": "CNTT K15",
            "class_code": "CNTT15"
        }
    ]
}
```

---

## 4.5. Update Department (Admin Only)

**PUT** `/departments/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "name": "Khoa CNTT (Updated)",
    "code": "CNTT_NEW"
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật department thành công",
    "data": {
        "id": 3,
        "name": "Khoa CNTT (Updated)",
        "code": "CNTT_NEW",
        "updated_at": "2024-01-15T11:00:00.000000Z"
    }
}
```

---

## 4.6. Delete Department (Admin Only)

**DELETE** `/departments/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Xóa department thành công"
}
```

**Response Error (500):**

```json
{
    "message": "Có lỗi xảy ra khi xóa department",
    "error": "Không thể xóa department vì còn giảng viên"
}
```

---

# 5. Class Management APIs

## 5.1. Get All Classes (Admin Only)

**GET** `/classes`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
[
    {
        "id": 5,
        "class_name": "CNTT K15",
        "class_code": "CNTT15",
        "school_year": "2023-2024",
        "department_id": 3,
        "lecturer_id": 1,
        "students_count": 45,
        "department": {
            "id": 3,
            "name": "Khoa CNTT"
        },
        "lecturer": {
            "id": 1,
            "full_name": "Trần Thị B",
            "lecturer_code": "GV001"
        }
    }
]
```

---

## 5.2. Create Class (Admin Only)

**POST** `/classes`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "class_name": "CNTT K16",
    "class_code": "CNTT16",
    "school_year": "2024-2025",
    "department_id": 3,
    "lecturer_id": 1
}
```

**Response Success (201):**

```json
{
    "message": "Tạo lớp học thành công",
    "data": {
        "id": 6,
        "class_name": "CNTT K16",
        "class_code": "CNTT16",
        "school_year": "2024-2025",
        "department_id": 3,
        "lecturer_id": 1,
        "created_at": "2024-01-15T10:30:00.000000Z"
    }
}
```

---

## 5.3. Get Class By ID (Admin Only)

**GET** `/classes/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "id": 5,
    "class_name": "CNTT K15",
    "class_code": "CNTT15",
    "school_year": "2023-2024",
    "department_id": 3,
    "lecturer_id": 1,
    "students_count": 45,
    "department": {
        "id": 3,
        "name": "Khoa CNTT",
        "code": "CNTT"
    },
    "lecturer": {
        "id": 1,
        "full_name": "Trần Thị B",
        "lecturer_code": "GV001"
    },
    "students": [
        {
            "id": 1,
            "full_name": "Nguyễn Văn A",
            "student_code": "SV001"
        }
    ]
}
```

---

## 5.4. Get Classes By Faculty (Admin Only)

**GET** `/classes/faculty/{facultyId}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Danh sách lớp theo khoa/phòng ban",
    "data": [
        {
            "id": 5,
            "class_name": "CNTT K15",
            "class_code": "CNTT15",
            "department_id": 3,
            "students_count": 45
        }
    ],
    "source": "database"
}
```

---

## 5.5. Get Classes By Lecturer (Admin Only)

**GET** `/classes/lecturer/{lecturerId}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Danh sách lớp theo giảng viên",
    "data": [
        {
            "id": 5,
            "class_name": "CNTT K15",
            "class_code": "CNTT15",
            "lecturer_id": 1,
            "students_count": 45
        }
    ],
    "source": "cache"
}
```

---

## 5.6. Update Class (Admin Only)

**PUT** `/classes/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request Body:**

```json
{
    "class_name": "CNTT K15 (Updated)",
    "school_year": "2024-2025",
    "lecturer_id": 2
}
```

**Response Success (200):**

```json
{
    "message": "Cập nhật lớp học thành công",
    "data": {
        "id": 5,
        "class_name": "CNTT K15 (Updated)",
        "school_year": "2024-2025",
        "lecturer_id": 2,
        "updated_at": "2024-01-15T11:00:00.000000Z"
    }
}
```

---

## 5.7. Delete Class (Admin Only)

**DELETE** `/classes/{id}`

**Headers:**

```
Authorization: Bearer {JWT_TOKEN}
```

**Response Success (200):**

```json
{
    "message": "Xóa lớp học thành công"
}
```

**Response Error (500):**

```json
{
    "message": "Có lỗi xảy ra khi xóa lớp học",
    "error": "Không thể xóa lớp học vì còn sinh viên"
}
```

---

## Error Codes Summary

| Status Code | Description                             |
| ----------- | --------------------------------------- |
| 200         | Success                                 |
| 201         | Created                                 |
| 400         | Bad Request                             |
| 401         | Unauthorized (Invalid or expired token) |
| 403         | Forbidden (Insufficient permissions)    |
| 404         | Not Found                               |
| 500         | Internal Server Error                   |

---

## Notes

1. **Authentication**: Tất cả endpoints (trừ login) yêu cầu JWT token
2. **Admin Permission**: Endpoints có label "(Admin Only)" chỉ dành cho users có `is_admin = true`
3. **Caching**: Một số endpoints sử dụng Redis cache, có thể có trường `source` trong response
4. **Pagination**: Một số endpoints hỗ trợ pagination (sẽ được cập nhật sau)
5. **Default Password**: Tài khoản mới được tạo có password mặc định là `123456`
