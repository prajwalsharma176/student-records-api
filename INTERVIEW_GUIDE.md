# Interview guide

Use these points only after running and understanding the project. Be accurate about your own contribution and which tests you personally performed.

## 60-second explanation

“I built a student records REST API using Python and Flask, with SQLite for storage. It provides endpoints to create, list, retrieve, update, and delete records. The API validates incoming JSON, uses parameterized SQL queries, and returns appropriate HTTP status codes for errors such as invalid input, missing students, and duplicate email addresses. I can test the endpoints with Postman and check stored records directly using SQL. Automated tests also exercise the complete CRUD flow and error cases against a temporary database.”

## Browser interface

The web interface is served by Flask at `/`. JavaScript uses `fetch` to call the same REST endpoints as Postman. After a successful change, it reloads the student list from the API. The search filters the loaded records in the browser.

## How a request flows

1. A client such as Postman sends an HTTP request, for example `POST /students`, with a JSON body.
2. Flask matches the method and path to a route in `app.py`.
3. The route checks the content type, parses JSON, validates the fields, and returns an error if validation fails.
4. The route executes a parameterized SQL query through Python's `sqlite3` module. SQLite enforces the unique email constraint as well as the required fields and age constraint.
5. On a successful write, the application commits the transaction. It converts the database row to JSON and responds with the correct status code, such as 201 for creation.
6. Flask closes the request's database connection when the application context ends. Data remains in the SQLite file for later requests.

For a GET request, the API reads rows and returns them as JSON. PATCH validates only the fields supplied and updates those fields. DELETE returns 204 when successful; a later GET returns 404.

## Design questions

- **Why Flask?** It is lightweight and provides routing, JSON handling, and an easy test client without requiring a large framework.
- **Why SQLite?** It is built into Python, needs no separate database server, and suits a small local project. A larger concurrent deployment could use PostgreSQL and migrations.
- **What is REST?** An HTTP approach that models data as resources, uses URLs such as `/students/1`, and uses methods and status codes to describe operations and results.
- **How are invalid inputs handled?** The API checks the JSON object, required fields, data types, age range, email format, and unknown fields. Invalid input produces a clear 400 response; non-JSON content produces 415.
- **How are duplicates handled?** SQLite has a case-insensitive unique constraint on email. The API catches the integrity error and returns 409. The database constraint also protects against concurrent requests.
- **How is SQL injection reduced?** User values are passed as SQL parameters, not concatenated into queries. PATCH column names are restricted to a validated allowlist.
- **How did you verify it?** Run the automated tests and use the included Postman requests, then query the SQLite file to confirm the records. The tests use a temporary database so they do not alter local development data.
- **What would you improve?** Add authentication and authorization, pagination, migrations, structured logging, and production deployment configuration.

## Troubleshooting example

If a request returns 400, inspect its JSON and response message, check field names and types, then resend it. For a 409 response, query the database for the email and use a unique value. For a 404, confirm the student ID exists. For a 415, set the content type to `application/json`. Verify a successful update with `SELECT * FROM students WHERE id = 1;`, adjusting the ID to match the request.
