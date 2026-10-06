import json
from pathlib import Path
import tempfile
import unittest

from validate_submission import load_vocabularies, validate_submission


class OperationNumberTypeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent
        self.vocabularies = load_vocabularies(self.root / 'vocabularies.json')

    def errors_for(self, difficulty, operation_number):
        operation = {'operation_number': operation_number}
        if difficulty == 'easy':
            operation.update(o1='hole_making', o2='DRILLING')
        else:
            operation.update(tool_type='twist_drill', tool_diameter_mm=12.0)
        suffix = 'sequence' if difficulty == 'easy' else 'tools'
        payload = {
            'part_id': 'test_part',
            'summary': {'number_of_operations': 1},
            'operations': [operation],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / f'test_part_{suffix}.json'
            path.write_text(json.dumps(payload), encoding='utf-8')
            return validate_submission(path, difficulty, self.vocabularies)

    def test_boolean_operation_number_is_invalid(self):
        for difficulty in ('easy', 'hard'):
            with self.subTest(difficulty=difficulty):
                self.assertTrue(self.errors_for(difficulty, True))

    def test_floating_operation_number_is_invalid(self):
        for difficulty in ('easy', 'hard'):
            with self.subTest(difficulty=difficulty):
                self.assertTrue(self.errors_for(difficulty, 1.0))

    def test_integer_operation_number_is_valid(self):
        for difficulty in ('easy', 'hard'):
            with self.subTest(difficulty=difficulty):
                self.assertEqual(self.errors_for(difficulty, 1), [])

    def test_public_reference_sequences_stay_valid(self):
        for difficulty in ('easy', 'hard'):
            paths = sorted((self.root / 'Test_Data' / 'reference_solution' / difficulty).glob('*.json'))
            self.assertEqual(len(paths), 30)
            for path in paths:
                with self.subTest(difficulty=difficulty, path=path.name):
                    self.assertEqual(validate_submission(path, difficulty, self.vocabularies), [])


if __name__ == '__main__':
    unittest.main()
