# Student Records API

A student management web app and REST API built with Python, Flask, SQL, and SQLite. Use the browser interface to create, search, edit, and delete records, or use the JSON API directly. It includes automated tests and a Postman collection.

## Run locally

Requirements: Python 3.9+ and pip.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app:create_app run --debug
```

Open `http://127.0.0.1:5000/` to use the web interface. Click **Add student**, fill in the form, and save; use **Edit**, **Delete**, or search to manage records. The API runs on the same address. The SQLite database and table are created automatically on startup at `instance/students.db`. Set the `DATABASE_PATH` environment variable before starting the app to use a different database file. Debug mode is for local development only.

## Endpoints

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| POST | `/students` | Create a student | 201, student JSON |
| GET | `/students` | List all students | 200, JSON array |
| GET | `/students/<id>` | Retrieve one student | 200, student JSON |
| PATCH | `/students/<id>` | Update one or more fields | 200, updated JSON |
| DELETE | `/students/<id>` | Delete one student | 204, empty body |

POST requires JSON with all four fields; PATCH accepts any non-empty subset:

```json
{"name":"Asha Patel","email":"asha@example.com","age":21,"course":"Computer Science"}
```

Name, email, and course must be non-empty strings of at most 255 characters. Email must have a basic valid format and be unique (case-insensitive); age must be an integer from 1 through 120. Unknown fields are rejected. Send the `Content-Type: application/json` header.

Example:

```bash
curl -X POST http://127.0.0.1:5000/students -H 'Content-Type: application/json' -d '{"name":"Asha Patel","email":"asha@example.com","age":21,"course":"Computer Science"}'
curl http://127.0.0.1:5000/students
```

Errors use the format `{"error":"message"}`. Invalid input or malformed JSON returns 400, missing records return 404, duplicate emails return 409, and an unsupported content type returns 415.

## Postman

Import `Student_Records_API.postman_collection.json` in Postman. Start the server and run **Create student**, then the other requests. The collection saves the created ID in the `studentId` collection variable. Create another student with a different email if you need another record. The last request deletes the saved record. `baseUrl` defaults to `http://127.0.0.1:5000`.

## Verify with SQL

```bash
sqlite3 instance/students.db
```

```sql
SELECT * FROM students;
SELECT id, name, course FROM students WHERE id = 1;
.quit
```

## Automated tests

```bash
python -m unittest discover -s tests -v
```

Tests use a temporary SQLite database and cover CRUD, SQL persistence, validation, malformed requests, missing records, and duplicate emails.

This is an educational local API; authentication, authorization, pagination, migrations, and production deployment configuration are not included. See `INTERVIEW_GUIDE.md` for the request flow and talking points.
