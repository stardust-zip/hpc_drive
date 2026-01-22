# 🚀 Migration Guide - Day 1

## ✅ Completed So Far

1. ✅ Updated `src/hpc_drive/models.py`:
   - Added 4 new enums: `RepositoryType`, `OwnerType`, `ProcessStatus`, `SigningStatus`
   - Added 6 new fields to `DriveItem` model
   - Created `SigningRequest` model

2. ✅ Created migration script: `scripts/migrate_add_repository_type.py`

---

## 📋 Next Steps - Run Migration

### Step 1: Backup Database (BẮT BUỘC)

```bash
cd /home/dudo/hpc_drive/hpc_drive
sqlite3 drive.db ".backup backup_before_repo_type.sql"
ls -lh backup_before_repo_type.sql
```

**Xác nhận:** File backup đã được tạo

---

### Step 2: Run Migration Script

```bash
cd /home/dudo/hpc_drive/hpc_drive
python scripts/migrate_add_repository_type.py
```

**Khi được hỏi "Proceed with migration? (yes/no):", nhập `yes`**

---

### Step 3: Verify Migration

```bash
# Check drive_items table schema
sqlite3 drive.db "PRAGMA table_info(drive_items);"

# Check signing_requests table
sqlite3 drive.db "PRAGMA table_info(signing_requests);"

# Count records
sqlite3 drive.db "SELECT COUNT(*) FROM drive_items;"
sqlite3 drive.db "SELECT COUNT(*) FROM signing_requests;"
```

**Expected:**
- `drive_items` table có thêm 6 columns mới
- `signing_requests` table được tạo
- Số records không thay đổi (existing data preserved)

---

## 🔄 Rollback (Nếu cần)

```bash
cd /home/dudo/hpc_drive/hpc_drive

# Restore from backup
rm drive.db
sqlite3 drive.db ".restore backup_before_repo_type.sql"
```

---

## ✅ After Migration Success

Mark trong `task.md`:
- [x] Update models.py
- [x] Create migration script
- [x] Backup database
- [x] Run migration
- [x] Verify schema

**Next:** Day 2 - Create Integration Service

---

## 🐛 Troubleshooting

### Error: "table drive_items already has column X"
→ Migration đã chạy trước đó. Check schema với:
```bash
sqlite3 drive.db "PRAGMA table_info(drive_items);"
```

### Error: "backup file not found"
→ Chạy lại Step 1 để tạo backup

### Error: "syntax error"
→ Check Python syntax:
```bash
python -m py_compile scripts/migrate_add_repository_type.py
```
