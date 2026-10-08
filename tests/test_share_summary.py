import importlib.util
from pathlib import Path
import unittest

script = Path(__file__).resolve().parents[1]/'skills/codex-project-index-recovery/scripts/share_summary.py'
spec = importlib.util.spec_from_file_location('share_summary', script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SummaryTests(unittest.TestCase):
    def test_raw_fields_never_copied(self):
        raw = {'sql_projects': 2, 'json_valid': True, 'candidate_status': 'BLOCKED',
               'candidate_reason': 'private-path-secret', 'files': {'sha256': 'private-fingerprint'},
               'project_names': ['private-project'], 'home': 'private-home', 'threads': ['private-id']}
        result = module.summarize(raw)
        self.assertEqual(result['sql_projects'], 2)
        self.assertTrue(result['json_valid'])
        self.assertEqual(result['candidate_status'], 'BLOCKED')
        self.assertTrue(set(result).isdisjoint({'candidate_reason','files','project_names','home','threads'}))

    def test_wrong_types_cannot_smuggle_data(self):
        result = module.summarize({'sql_projects': 'private-name', 'sql_roots': True,
                                   'sql_assignments': -1, 'json_valid': 'private-path',
                                   'candidate_status': 'private-id'})
        self.assertEqual(set(result), {'summary_format','scope'})

    def test_unknown_fields_and_empty_report(self):
        self.assertEqual(module.summarize({'unexpected': 'private'}), module.summarize({}))

    def test_non_object_report_blocked(self):
        with self.assertRaises(ValueError):
            module.summarize(['private'])

if __name__ == '__main__':
    unittest.main()
