import unittest
from courses import units

class Curriculum(unittest.TestCase):
    def test_course_links(self):
        self.assertEqual(len(units), 10)
        for u in units:
            self.assertTrue(u['formula'] and u['note'])
            self.assertTrue(all(0 <= i < u['id'] for i in u['prereq']))

