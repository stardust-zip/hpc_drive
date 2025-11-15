# Trash Management API

This document outlines the API endpoints for managing the trash feature in HPC Drive.

## 1. Move an Item to Trash

Moves an item (file or folder) to the trash. If a folder is moved to trash, all of its contents (children, grandchildren, etc.) are also moved to the trash.

- **Endpoint:** `PATCH /api/v1/drive/items/{item_id}/trash`
- **Method:** `PATCH`
- **URL Parameters:**
  - `item_id` (string, required): The UUID of the item to move to trash.
- **Request Body:** None
- **Success Response:**
  - **Code:** `200 OK`
  - **Content:** A `DriveItemResponse` object for the trashed item.
    ```json
    {
      "item_id": "...",
      "name": "My Folder",
      "item_type": "FOLDER",
      "parent_id": null,
      "owner_id": 1,
      "created_at": "...",
      "updated_at": "...",
      "is_trashed": true,
      "trashed_at": "...",
      "file_metadata": null
    }
    ```
- **Error Responses:**
  - `404 Not Found`: If the item does not exist or the user does not have permission.
  - `400 Bad Request`: If the item is already in the trash.

## 2. Restore an Item from Trash

Restores an item from the trash. If a folder is restored, all of its contents are also restored.

- **Endpoint:** `PATCH /api/v1/drive/items/{item_id}/restore`
- **Method:** `PATCH`
- **URL Parameters:**
  - `item_id` (string, required): The UUID of the item to restore.
- **Request Body:** None
- **Success Response:**
  - **Code:** `200 OK`
  - **Content:** A `DriveItemResponse` object for the restored item.
- **Error Responses:**
  - `404 Not Found`: If the item does not exist or the user does not have permission.
  - `400 Bad Request`: If the item is not in the trash.

## 3. List Trashed Items

Retrieves a list of all items currently in the user's trash, ordered by the date they were trashed (most recent first).

- **Endpoint:** `GET /api/v1/drive/trash`
- **Method:** `GET`
- **URL Parameters:** None
- **Request Body:** None
- **Success Response:**
  - **Code:** `200 OK`
  - **Content:** A list of `DriveItemResponse` objects.
    ```json
    [
      {
        "item_id": "...",
        "name": "Old File.txt",
        "item_type": "FILE",
        /* ... other fields ... */
      },
      {
        "item_id": "...",
        "name": "Another Folder",
        "item_type": "FOLDER",
        /* ... other fields ... */
      }
    ]
    ```

## 4. Permanently Delete an Item

Permanently deletes a single item from the trash. This action is irreversible. If the item is a file, it will be deleted from the disk. If it is a folder, all its contents will also be permanently deleted.

- **Endpoint:** `DELETE /api/v1/drive/trash/{item_id}`
- **Method:** `DELETE`
- **URL Parameters:**
  - `item_id` (string, required): The UUID of the item to permanently delete.
- **Request Body:** None
- **Success Response:**
  - **Code:** `200 OK`
  - **Content:**
    ```json
    {
      "detail": "Item 'My File.txt' and its contents permanently deleted."
    }
    ```
- **Error Responses:**
  - `404 Not Found`: If the item does not exist or the user does not have permission.
  - `400 Bad Request`: If the item is not in the trash.

## 5. Empty Trash

Permanently deletes all items in the user's trash. This action is irreversible and will delete all corresponding files from the disk.

- **Endpoint:** `DELETE /api/v1/drive/trash`
- **Method:** `DELETE`
- **URL Parameters:** None
- **Request Body:** None
- **Success Response:**
  - **Code:** `200 OK`
  - **Content:**
    ```json
    {
      "detail": "Trash has been successfully emptied."
    }
    ```
  - If the trash is already empty, the response will be:
    ```json
    {
      "detail": "Trash is already empty."
    }
    ```
