import unittest
from main import YaUploader

class UnitTest(unittest.TestCase):
    def test_create_folder_new(self):
        test_class = YaUploader("здесь должен быть токен")
        self.assertEqual(test_class.create_folder('my_n'), 201)

    def test_create_folder_already_exists(self):
        test_class = YaUploader("здесь должен быть токен")
        self.assertEqual(test_class.create_folder('my_photos'), 409)

    def test_create_folder_wrong_token(self):
        test_class = YaUploader("здесь должен быть неправильный токен")
        self.assertEqual(test_class.create_folder('my_photos'), 401)

if __name__ == '__main__':
    unittest.main()