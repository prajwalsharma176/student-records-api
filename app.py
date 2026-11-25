"""A small REST API for managing student records with SQLite."""
import os
import sqlite3

from flask import Flask, g, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, HTTPException


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(DATABASE=os.environ.get('DATABASE_PATH', os.path.join(app.instance_path, 'students.db')))
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
            course TEXT NOT NULL
        )''')
        db().commit()

    def error(message, status):
        return jsonify({'error': message}), status

    def validate(data, partial=False):
        if not isinstance(data, dict):
            return 'Request body must be a JSON object.'
        fields = {'name', 'email', 'age', 'course'}
        unknown = set(data) - fields
        if unknown:
            return 'Unknown fields: ' + ', '.join(sorted(unknown)) + '.'
        if not data:
            return 'Request body must not be empty.'
        missing = fields - set(data)
        if not partial and missing:
            return 'Missing fields: ' + ', '.join(sorted(missing)) + '.'
        for key in ('name', 'email', 'course'):
            if key in data:
                if not isinstance(data[key], str) or not data[key].strip():
                    return f'{key} must be a non-empty string.'
                data[key] = data[key].strip()
                if len(data[key]) > 255:
                    return f'{key} must be at most 255 characters.'
        if 'email' in data:
            email = data['email']
            if email.count('@') != 1 or any(c.isspace() for c in email) or not all(email.split('@')) or '.' not in email.split('@')[1]:
                return 'email must be a valid email address.'
        if 'age' in data and (type(data['age']) is not int or not 1 <= data['age'] <= 120):
            return 'age must be an integer between 1 and 120.'
        return None

    def body(partial=False):
        if not request.is_json:
            return None, error('Content-Type must be application/json.', 415)
        try:
            data = request.get_json()
        except BadRequest:
            return None, error('Malformed JSON body.', 400)
        message = validate(data, partial)
        return (None, error(message, 400)) if message else (data, None)

    def find(student_id):
        return db().execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return error(exc.description, exc.code)

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/students')
    def list_students():
        rows = db().execute('SELECT * FROM students ORDER BY id').fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get('/students/<int:student_id>')
    def get_student(student_id):
        row = find(student_id)
        return jsonify(dict(row)) if row else error('Student not found.', 404)

    @app.post('/students')
    def create_student():
        data, failure = body()
        if failure:
            return failure
        try:
            cursor = db().execute('INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)',
                                  (data['name'], data['email'], data['age'], data['course']))
            db().commit()
        except sqlite3.IntegrityError:
            return error('A student with this email already exists.', 409)
        return jsonify(dict(find(cursor.lastrowid))), 201

    @app.patch('/students/<int:student_id>')
    def update_student(student_id):
        if not find(student_id):
            return error('Student not found.', 404)
        data, failure = body(partial=True)
        if failure:
            return failure
        # Column names come only from the validated allowlist; values are bound parameters.
        columns = ', '.join(f'{key} = ?' for key in data)
        try:
            db().execute(f'UPDATE students SET {columns} WHERE id = ?', (*data.values(), student_id))
            db().commit()
        except sqlite3.IntegrityError:
            return error('A student with this email already exists.', 409)
        return jsonify(dict(find(student_id)))

    @app.delete('/students/<int:student_id>')
    def delete_student(student_id):
        cursor = db().execute('DELETE FROM students WHERE id = ?', (student_id,))
        db().commit()
        if cursor.rowcount == 0:
            return error('Student not found.', 404)
        return '', 204

    return app
