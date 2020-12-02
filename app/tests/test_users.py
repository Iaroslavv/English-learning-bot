from app import app, db, mail
import unittest
from unittest.mock import patch
from app.telegram_bot.synonyms import find_synonym


class TestUsers(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.config_test")
        app.testing = True
        self.app = app.test_client()
        db.create_all()

        mail.init_app(app)
        self.assertEqual(app.debug, False)
     
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    # helper methods
    def register(self, name: str, email: str, password: str, confirm: str):
        data = dict(name=name, email=email, password=password, confirm=confirm)
        return self.app.post("/signup", data=data, follow_redirects=True)

    def login(self, email: str, password: str):
        data = dict(email=email, password=password)
        return self.app.post("/login", data=data, follow_redirects=True)
    
    def logout(self):
        return self.app.get("/logout", follow_redirects=True)

    # tests
    def test_valid_signup(self):
        response = self.register("Aleksey", "alex@yan.ru", "alloh", "alloh")
        self.assertEqual(response.status_code, 200)
    
    def test_valid_login(self):
        response = self.login("alex@yan.ru", "allog")
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        self.assertEqual(self.logout().status_code, 200)

    def test_rapidapi_query(self):
        with patch("requests.get") as mocked_get:
            url = "https://wordsapiv1.p.rapidapi.com/words/hello/synonyms"
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.ok = True
            mocked_get.return_value = ['hi', 'how-do-you-do', 'howdy', 'hullo']
            synonym = find_synonym("hello")

            self.assertTrue(find_synonym(url))
            self.assertEqual(synonym, ['hi', 'how-do-you-do', 'howdy', 'hullo'])


if __name__ == "__main__":
    unittest.main()
