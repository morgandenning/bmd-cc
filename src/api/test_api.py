import os
import unittest
import tempfile

from api import app, init_db, query_db

TEST_DB = 'test.db'


class ApiTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        
        self.app = app.test_client()
        
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])


    def test_index(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)

    def test_not_found(self):
        r = self.app.get('/999')
        self.assertEqual(r.status_code, 404)

    def test_found(self):
        with app.app_context():
            state = """. . .
T  . """
            query_db('insert into worlds (id, state) values (?, ?)', [1, state])

            r = self.app.get('/1')

            self.assertEqual(r.status_code, 200)

    def test_invalid_chars_returns_400(self):
            state = """. . .
T  .A"""
            r = self.app.post('/', data=state, headers={'Content-Type': 'plain/text'})

            self.assertEqual(r.status_code, 400)
            self.assertEqual('invalid characters found', r.get_json().get('message'))


if __name__ == '__main__':
    unittest.main()
