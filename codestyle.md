# Backend Code Style Guide

This guide is based on common Python practices (like PEP 8) and conventions observed in the provided FastAPI/MongoDB application.

---

## 1. General Code

### 1.1. Scope

* Applicable to all backend code (Python, FastAPI, MongoDB, Pydantic).

### 1.2. Naming

* Avoid using meaningless names (e.g., `a_2`).
* Use clear, descriptive names (e.g., `users_collection`, `update_data`).

---

## 2. Conventions

* **Modules/Files:** `snake_case` (e.g., `controller.py`, `model.py`).
* **Functions/Methods that not belongs to the FastAPI wrapper:** `camelStyle` (e.g. `getMaxUID`)
* **Functions/Methods under FastAPI wrapper:** `snake_case` (e.g., `find_max_uid`, `get_token`, `register`).
* **Variables:** `snake_case` (e.g., `token_list`, `user_uid`, `auth_token`).
* **Classes (Pydantic Models):** `PascalCase` (e.g., `UserRegister`, `ContactData`).
* **Constants (if any):** `UPPERCASE_WITH_UNDERSCORES` (e.g., `API_BASE_URL` - though none are strictly defined as constants in the example).
* **Database Collections:** `snake_case` or plural (e.g., `users_collection`, `contacts_collection`).

---

## 3. Formatting

### 3.1. General
* **Indentation:** Use **4 spaces** for indentation (standard Python convention, which is seen in the example code).
* **Line Length:** Try to keep lines below 79 characters (PEP 8 standard).
* **Quotes:** Use **double quotes** (`"`) for strings (e.g., `{"_id": "user_id"}`).

### 3.2. Imports
Imports should be on separate lines and grouped in the following order:

* Standard library imports (e.g., `secrets`, `typing`).
* Third-party library imports (e.g., `fastapi`, `pymongo`, `pydantic`, `bson`).
* Local application/project imports (e.g., `from models.model import ...`).

---

## 4. Function/Endpoint Structure

* **Decorators:** FastAPI decorators should precede the `async def` or `def` function definition.
* **Type Hinting:** **Always** use type hints for function arguments and return values (e.g., `getToken(token: str)`).
* **Dependencies/Headers:** Use FastAPI/Pydantic features like `Header(None)` and data models for handling inputs (e.g., `data: UserUpdate`, `authorization: str = Header(None)`).

### 4.1. RESTful API Design
* **Important:** Follow the RESTful API style.
* `GET`: Fetch the data (resources)
* `POST`: Create new data
* `PUT`: Modify the existing data
* `DELETE`: Delete the existing data
### 4.1. Core Logic

* **Database Connection:** Check for database connection at the beginning of sensitive functions where necessary (`if db is None:`).
* **Validation:** Explicitly check for unique constraints or business logic before performing database writes (e.g., checking if email/phone are already registered in `register`).
* **Authentication/Authorization:** Centralize token-checking logic (e.g., `getToken(authorization)`).

### 4.2. Error Handling (FastAPI)
* **Exceptions:** Use **`HTTPException`** to return standard HTTP error responses to the client with appropriate status codes (e.g., `400`, `401`, `404`, `500`).
* **Try...Except:** Wrap complex or potentially failing operations (like MongoDB calls or token lookups) in a `try...except` block to catch unexpected errors and return a `HTTPException(status_code=500)` for robustness.

---

## 5. Database Interaction (MongoDB)
### 5.1. General
* **Object IDs:** Use `ObjectId(contact_id)` when querying or modifying documents by their `_id` field to correctly convert the string ID from the URL path.
* **UID Generation:** Centralize the logic for generating new, unique UIDs for users (e.g., `findMaxUID()`).

### 5.2. Querying
* **Finders:** Use specific methods like `find_one` for single lookups and `list(collection.find(...))` for multiple results.
* **Updates:** Use MongoDB operators like **`$set`** for updating fields (`{"$set": update_data}`).