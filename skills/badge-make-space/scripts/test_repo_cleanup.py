"""Exercise deletion boundaries in disposable fixtures, never the real badge files."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('repo_cleanup', Path(__file__).with_name('repo_cleanup.py'))
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='badge_cleanup_test_', dir='/private/tmp')
        self.root = Path(self.temp.name).resolve()
        self.original_root = cleanup.ROOT
        cleanup.ROOT = self.root
        self.put('current.blend', b'complete editable model')
        self.put('old.png', b'old generated capture')
        self.put('second.png', b'another old generated capture')

    def tearDown(self):
        cleanup.ROOT = self.original_root
        self.temp.cleanup()

    def put(self, path, data):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def manifest(self, paths=('old.png',)):
        return {'version': 1, 'root': str(self.root), 'authorization': 'Fixture owner requested obsolete capture cleanup',
                'models': [{'badge': 'Fixture', 'blender': 'current.blend', 'export': None, 'evidence': 'Fixture current model'}],
                'keep': [cleanup.fingerprint('current.blend')],
                'remove': [{**cleanup.fingerprint(p), 'reason': 'Superseded generated capture'} for p in paths]}

    def test_valid_apply_preserves_model_and_receipt(self):
        keep = (self.root / 'current.blend').read_bytes()
        result = cleanup.apply_manifest(self.manifest(), 'audit/receipt.jsonl')
        self.assertFalse((self.root / 'old.png').exists())
        self.assertEqual((self.root / 'current.blend').read_bytes(), keep)
        self.assertEqual(result['removed_files'], 1)
        rows = [json.loads(s) for s in (self.root / 'audit/receipt.jsonl').read_text().splitlines()]
        self.assertEqual([r['event'] for r in rows], ['planned', 'intent', 'removed', 'complete'])
        self.assertIn('sha256', rows[2])

    def test_stale_second_file_prevents_all_deletions(self):
        plan = self.manifest(('old.png', 'second.png'))
        self.put('second.png', b'new owner content')
        with self.assertRaises(ValueError):
            cleanup.apply_manifest(plan, 'audit/receipt.jsonl')
        self.assertTrue((self.root / 'old.png').exists())
        self.assertFalse((self.root / 'audit/receipt.jsonl').exists())

    def test_same_size_changed_content_is_rejected(self):
        plan = self.manifest()
        p = self.root / 'old.png'
        p.write_bytes(b'x' * p.stat().st_size)
        import os
        t = plan['remove'][0]['mtime_ns']
        os.utime(p, ns=(t, t))
        with self.assertRaises(ValueError):
            cleanup.preflight(plan)

    def test_retained_alias_and_overlap_rejected(self):
        plan = self.manifest()
        plan['remove'] = [{**cleanup.fingerprint('current.blend'), 'reason': 'Wrong removal'}]
        with self.assertRaises(ValueError):
            cleanup.preflight(plan)
        alias = self.root / 'alias.blend'
        import os
        os.link(self.root / 'current.blend', alias)
        plan['remove'] = [{**cleanup.fingerprint('alias.blend'), 'reason': 'Alias'}]
        with self.assertRaises(ValueError):
            cleanup.preflight(plan)

    def test_git_and_agent_and_skill_paths_protected(self):
        for directory in ('.git', '.GIT', '.agents', '.codex', '.claude', '.aws', 'skills'):
            path = directory + '/old.png'
            self.put(path, b'protected')
            with self.assertRaises(ValueError):
                cleanup.preflight(self.manifest((path,)))

    def test_source_code_is_not_a_generated_artifact(self):
        self.put('builder.py', b'important source')
        with self.assertRaises(ValueError):
            cleanup.preflight(self.manifest(('builder.py',)))

    def test_escape_and_symlink_are_rejected(self):
        for path in ('../outside.png', str(self.root / 'old.png')):
            with self.assertRaises(ValueError):
                cleanup.inside(path)
        (self.root / 'link').symlink_to('/private/tmp', target_is_directory=True)
        with self.assertRaises(ValueError):
            cleanup.inside('link/anything.png')
        (self.root / 'alias.png').symlink_to(self.root / 'old.png')
        with self.assertRaises(ValueError):
            cleanup.fingerprint('alias.png')

    def test_model_must_be_in_keep_index(self):
        plan = self.manifest()
        plan['models'][0]['blender'] = 'another.blend'
        with self.assertRaises(ValueError):
            cleanup.preflight(plan)

    def test_wrong_repository_and_existing_receipt_are_rejected(self):
        plan = self.manifest()
        plan['root'] = '/another/repo'
        with self.assertRaises(ValueError):
            cleanup.preflight(plan)
        self.put('audit/receipt.jsonl', b'prior audit')
        with self.assertRaises(ValueError):
            cleanup.apply_manifest(self.manifest(), 'audit/receipt.jsonl')
        self.assertTrue((self.root / 'old.png').exists())

    def test_inventory_counts_git_separately_and_skips_links(self):
        self.put('.git/objects/sample', b'git data')
        (self.root / 'outside').symlink_to('/private/tmp', target_is_directory=True)
        result = cleanup.inventory()
        self.assertEqual(result['git_bytes'], len(b'git data'))
        self.assertIn('outside', result['links_not_followed'])
        self.assertFalse(any(r['path'].startswith('outside/') for r in result['files']))


if __name__ == '__main__':
    unittest.main()
