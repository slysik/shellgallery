import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata_manager import MetadataManager

class TestMetadataManager(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = 'test_data'
        self.metadata_file = os.path.join(self.test_data_dir, 'metadata.json')
        os.makedirs(self.test_data_dir, exist_ok=True)
        self.metadata_manager = MetadataManager(data_dir=self.test_data_dir)

    def tearDown(self):
        if os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)
        if os.path.exists(self.test_data_dir):
            os.rmdir(self.test_data_dir)

    def test_save_and_get_item(self):
        item = {'id': '123', 'title': 'Test Item'}
        self.metadata_manager.save_item(item, 'test_category')
        retrieved_item = self.metadata_manager.get_by_id('123')
        self.assertEqual(retrieved_item['title'], 'Test Item')

    def test_get_all(self):
        item1 = {'id': '1', 'title': 'Item 1'}
        item2 = {'id': '2', 'title': 'Item 2'}
        self.metadata_manager.save_item(item1, 'cat1')
        self.metadata_manager.save_item(item2, 'cat2')
        all_items = self.metadata_manager.get_all()
        self.assertEqual(len(all_items), 2)

if __name__ == '__main__':
    unittest.main()
