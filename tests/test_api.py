import os
import sqlite3
import tempfile
import unittest

from app import create_app


class StudentAPITest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'test.db')
        self.app = create_app({'TESTING': True, 'DATABASE': self.path})
        self.client = self.app.test_client()
        self.student = {'name': 'Asha Patel', 'email': 'asha@example.com', 'age': 21, 'course': 'Computer Science'}

    def tearDown(self):
        self.temp.cleanup()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student records', response.data)

    def test_crud_and_database(self):
        created = self.client.post('/students', json=self.student)
        self.assertEqual(created.status_code, 201)
        student_id = created.json['id']
        self.assertEqual(self.client.get('/students').json, [created.json])
        self.assertEqual(self.client.get(f'/students/{student_id}').json['name'], 'Asha Patel')
        updated = self.client.patch(f'/students/{student_id}', json={'course': 'Mathematics'})
        self.assertEqual(updated.json['course'], 'Mathematics')
        connection = sqlite3.connect(self.path)
        try:
            self.assertEqual(connection.execute('SELECT course FROM students WHERE id = ?', (student_id,)).fetchone()[0], 'Mathematics')
        finally:
            connection.close()
        self.assertEqual(self.client.delete(f'/students/{student_id}').status_code, 204)
        self.assertEqual(self.client.get(f'/students/{student_id}').status_code, 404)

    def test_validation_and_errors(self):
        for payload in ({}, {'name': 'Only name'}, {**self.student, 'age': True},
                        {**self.student, 'age': 121}, {**self.student, 'email': 'invalid'},
                        {**self.student, 'extra': 'x'}, [], {**self.student, 'name': ' '}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/students', json=payload).status_code, 400)
        self.assertEqual(self.client.post('/students', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/students', data='hello').status_code, 415)
        self.assertEqual(self.client.patch('/students/999', json={'name': 'X'}).status_code, 404)
        self.assertEqual(self.client.delete('/students/999').status_code, 404)
        self.assertEqual(self.client.get('/missing').status_code, 404)

    def test_duplicate_email_create_and_update(self):
        self.client.post('/students', json=self.student)
        duplicate = {**self.student, 'email': 'ASHA@example.com'}
        self.assertEqual(self.client.post('/students', json=duplicate).status_code, 409)
        second = self.client.post('/students', json={**self.student, 'email': 'other@example.com'})
        self.assertEqual(self.client.patch(f"/students/{second.json['id']}", json={'email': 'asha@example.com'}).status_code, 409)


if __name__ == '__main__':
    unittest.main()
