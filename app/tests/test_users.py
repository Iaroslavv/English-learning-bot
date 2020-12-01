from app import app, db, mail
import unittest


class TestUsers(unittest.TestCase):
    
    def setUp(self):
        app.config.from_object("config.config_test")
        db.drop_all()
        db.create_all()
        
        mail.init_app(app)
        self.assertEqual(app.debug, False)
        
    def tearDown(self):
        pass
        

if __name__ == "__main__":
    unittest.main()
