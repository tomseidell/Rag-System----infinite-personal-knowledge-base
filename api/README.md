# API reference

All HTTP endpoints of the backend are created in the routers in `api/modules/*/router.py` and registered in `api/routes.py`. There are **12 endpoints** in total. Exact API documentation can also be found via the /swagger endpoint.

## Authentication

Login works with an email and a password. The server answers with two cookies and **no token in the response body**:

| Cookie          | Lifetime                                   | Used for                                     |
| --------------- | ------------------------------------------ | -------------------------------------------- |
| `access_token`  | 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`) | every endpoint under `/document` and `/chat` |
| `refresh_token` | 30 days (`REFRESH_TOKEN_EXPIRE_MINUTES`)   | only `POST /user/refresh`                    |

- Both cookies are `HttpOnly` and `SameSite=Strict`. They are `Secure` when `COOKIE_SECURE=true`.
- Browsers send them automatically. With curl, store and send them with `-c cookies.txt` and `-b cookies.txt`.
- Every refresh issues a **new pair** of tokens. The server keeps only a hash of the latest refresh token, so an older one stops working.
- Every document and chat query is limited to the signed-in user. Another user's document answers `404`, not `403`.

## Rate limit

Every request counts against a limit of **100 requests per minute and IP address**, stored in Redis. `/health` and `/metrics` are excluded.

## Endpoints

**Who:** `public` = no login needed · `user` = valid `access_token` cookie · `refresh cookie` = valid `refresh_token` cookie.

### System

| Method | Path      | Who    | What it does                                                         |
| ------ | --------- | ------ | -------------------------------------------------------------------- |
| `GET`  | `/`       | public | Welcome message: `{"message": "Welcome to FastAPI Project"}`         |
| `GET`  | `/health` | public | `{"status": "healthy"}`, used for health checks and not rate limited |

### Users (`/user`)

| Method | Path             | Who            | What it does                                          |
| ------ | ---------------- | -------------- | ----------------------------------------------------- |
| `POST` | `/user/register` | public         | Create an account. Returns the new user, status `201` |
| `POST` | `/user/login`    | public         | Check the credentials and set both cookies            |
| `POST` | `/user/refresh`  | refresh cookie | Issue a new pair of cookies                           |
| `POST` | `/user/logout`   | public         | Delete both cookies in the browser                    |

### Documents (`/document`)

All document endpoints need a login. Only PDF files are accepted.

| Method   | Path                               | Who  | What it does                                                            |
| -------- | ---------------------------------- | ---- | ----------------------------------------------------------------------- |
| `POST`   | `/document/`                       | user | Upload a PDF and start the processing, status `201`                     |
| `GET`    | `/document/`                       | user | List your documents, newest first, 20 per page                          |
| `GET`    | `/document/{document_id}/status`   | user | Current processing step                                                 |
| `GET`    | `/document/{document_id}/download` | user | Download the original PDF                                               |
| `DELETE` | `/document/{document_id}`          | user | Delete the document, its chunks, its vectors and the file, status `204` |

**Upload** (`POST /document/`, `multipart/form-data`)

| Part    | Type                     | Rules                                                 |
| ------- | ------------------------ | ----------------------------------------------------- |
| `file`  | file                     | required, extension `.pdf`, smaller than 10 MB        |
| `title` | string (query parameter) | optional, defaults to the file name without extension |

The answer comes back immediately. Reading, chunking and embedding run in the background.

#### Status values

`GET /document/{id}/status` returns `{ "status": "...", "message": "..." }`.

| `status`      | Meaning                                        |
| ------------- | ---------------------------------------------- |
| `reading_pdf` | text is being extracted from the PDF           |
| `chunking`    | the text is being split into chunks            |
| `embedding`   | chunks are being embedded and stored           |
| `completed`   | the document is searchable in the chat         |
| `failed`      | processing stopped, `message` holds the reason |

### Chat (`/chat`)

| Method | Path     | Who  | What it does                                                           |
| ------ | -------- | ---- | ---------------------------------------------------------------------- |
| `POST` | `/chat/` | user | Ask a question about your documents, answer arrives as an event stream |

A question that was already asked by the same user within the last hour is answered from the Redis cache.

## Errors

Every error has the shape `{"detail": "..."}`. Input / validation errors from the services add an `operation` field.

| Status | When                                                                                  | Example `detail`                                 |
| ------ | ------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `400`  | invalid input: file too large, not a PDF, missing file name                           | `inserted file is not pdf`                       |
| `401`  | no or invalid cookie, wrong password, wrong token type                                | `Not authenticated`, `Invalid Email or Password` |
| `404`  | document, document status or user does not exist (or belongs to someone else)         | `document not found`                             |
| `409`  | the email is already registered                                                       | `User already exists: me@example.com`            |
| `422`  | the request body does not match the schema (generated by FastAPI, `detail` is a list) |                                                  |
| `429`  | rate limit exceeded                                                                   | `Too many requests, try again later.`            |
| `500`  | database, storage, Redis or Qdrant failure, or an unexpected error                    | `An error occured`                               |

The error handlers are registered in `api/exception_handlers.py`.
