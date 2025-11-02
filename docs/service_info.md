# Service Info

## General
Our team is making a general college management app (with NextJS frontend), and combine of multiple microservice (users, tasks, lms, dispatch, drive,...), with each using a different language.

All other service use user info from the user microservice.
This is the user schema in user serive, we need to follow this.
```json
{
  "sub": 2,
  "user_type": "lecturer", # or student
  "username": "lecturer1",
  "is_admin": false, # only lecturer can be admin
  "email": "lecturer1@system.com",
  "full_name": "Lecturer 1",
  "department_id": 1,
  "class_id": null,
  "iat": 1761899357,
  "exp": 1761902957
}
```

## Drive Service
Our service is the drive microservice, using FastAPI and SQlite. Here is an example schema for our service (Remeber our servive still using FastAPI)

```prisma
model User {
  userId Int @id @unique

  username     String   @unique
  passwordHash String // This model is just for Prisma's reference
  email        String   @unique
  role         UserRole @default(STUDENT)
  createdAt    DateTime @default(now())

  // Relations
  ownedItems   DriveItem[]       @relation("ItemOwner")
  sharedWithMe SharePermission[] @relation("SharedWithUser")

  @@map("users")
}

model DriveItem {
  itemId     String     @id @default(uuid())
  ownerId    Int
  parentId   String?
  name       String
  itemType   ItemType
  isTrashed  Boolean    @default(false)
  trashedAt  DateTime?
  permission Permission @default(PRIVATE)
  createdAt  DateTime   @default(now())
  updatedAt  DateTime   @updatedAt

  // Relations
  owner            User              @relation("ItemOwner", fields: [ownerId], references: [userId], onDelete: Restrict)
  parent           DriveItem?        @relation("FolderChildren", fields: [parentId], references: [itemId], onDelete: SetNull)
  children         DriveItem[]       @relation("FolderChildren")
  fileMetadata     FileMetadata?
  sharePermissions SharePermission[]

  @@unique([ownerId, parentId, name])
  @@map("drive_items")
}

model FileMetadata {
  itemId       String        @id
  mimeType     String
  size         BigInt
  storagePath  String        @unique
  documentType DocumentType?
  version      Int           @default(1)
  createdAt    DateTime      @default(now())
  updatedAt    DateTime      @updatedAt

  // Relations
  driveItem DriveItem @relation(fields: [itemId], references: [itemId], onDelete: Cascade)

  @@map("file_metadata")
}

model SharePermission {
  shareId          String     @id @default(uuid())
  itemId           String
  sharedWithUserId Int
  permissionLevel  ShareLevel
  createdAt        DateTime   @default(now())

  // Relations
  item           DriveItem @relation(fields: [itemId], references: [itemId], onDelete: Cascade)
  sharedWithUser User      @relation("SharedWithUser", fields: [sharedWithUserId], references: [userId], onDelete: Cascade)

  @@unique([itemId, sharedWithUserId])
  @@map("share_permissions")
}

enum UserRole {
  ADMIN
  TEACHER
  STUDENT
}

enum ItemType {
  FILE
  FOLDER
}

enum Permission {
  PRIVATE
  SHARED
}

enum ShareLevel {
  VIEWER
  EDITOR
}

enum DocumentType {
  PDF
  WORD
  EXCEL
  POWERPOINT
  OTHER
}
```

### Drive Service's Features
#### Student/Lecturer
- CRUD DriveItem and Management
- Uploading Files
- Sharing Files
#### Admin
- Manage all DriveItem of ALL users
