import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest
import uuid
import shutil

script = Path(__file__).resolve().parents[1]/'skills/codex-project-index-recovery/scripts/diagnose.py'
spec = importlib.util.spec_from_file_location('recovery', script)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RecoveryTests(unittest.TestCase):
    def test_preserves_deletions_and_settings(self):
        p = [{'id':'current','name':'Current','created_at_ms':1,'updated_at_ms':2}]
        j = {'local-projects':{},'migration':{'done':True},'other':'keep'}
        candidate = m.make_candidate(j,p,[],[('chat','current'),('unassigned',None)])
        self.assertEqual(list(candidate['local-projects']), ['current'])
        self.assertEqual(candidate['migration'],j['migration'])
        self.assertEqual(candidate['other'],'keep')
        self.assertNotIn('unassigned',candidate['thread-project-assignments'])
        self.assertEqual(j['local-projects'],{})

    def test_conflicts_and_orphans_blocked(self):
        p = [{'id':'p','name':'P','created_at_ms':1,'updated_at_ms':2}]
        for j in ({'local-projects':{'old':{}}}, {'thread-project-assignments':{'x':{}}},
                  {'app-server-pending-project-deletions-by-host':{'local':['p']}}):
            with self.assertRaises(ValueError): m.make_candidate(j,p,[],[])
        with self.assertRaises(ValueError): m.make_candidate({},p,[],[('x','missing')])
        with self.assertRaises(ValueError): m.make_candidate({},p,[{'project_id':'missing'}],[])
        with self.assertRaises(ValueError): m.make_candidate({'projectless-thread-ids':['x']},p,[],[('x','p')])

    def test_disjoint_projectless_preserved(self):
        p = [{'id':'p','name':'P','created_at_ms':1,'updated_at_ms':2}]
        j={'projectless-thread-ids':['current-chat'],'thread-projectless-output-directories':{'current-chat':'private-output'}}
        result=m.make_candidate(j,p,[],[('current-chat',None),('assigned','p')])
        self.assertEqual(result['projectless-thread-ids'],j['projectless-thread-ids'])
        self.assertEqual(result['thread-projectless-output-directories'],j['thread-projectless-output-directories'])

    def test_corrupt_json(self):
        with self.assertRaises(ValueError): json.loads('{"x":1,"x":2}',object_pairs_hook=m.unique)
        with self.assertRaises(ValueError): m.make_candidate(None,[],[],[])

    def test_empty_wrong_field_types_blocked(self):
        p = [{'id':'p','name':'P','created_at_ms':1,'updated_at_ms':2}]
        for j in ({'local-projects': []}, {'thread-project-assignments': ''}, {'project-order': {}}):
            with self.assertRaises(ValueError): m.make_candidate(j,p,[],[])

    def test_snapshot_no_source_write(self):
        artifact_parent = (Path(__file__).resolve().parents[1]/'.test-artifacts').resolve()
        root = (artifact_parent/uuid.uuid4().hex).resolve()
        self.assertEqual(root.parent, artifact_parent)
        root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, root)
        home=root/'home'
        home.mkdir(parents=True)
        (home/m.NAMES[0]).write_text('{"local-projects":{},"migration":true}',encoding='utf-8')
        c=sqlite3.connect(home/'state_5.sqlite')
        c.executescript('CREATE TABLE projects(id TEXT,name TEXT,position INTEGER,created_at_ms INTEGER,updated_at_ms INTEGER); CREATE TABLE project_roots(project_id TEXT,path TEXT,position INTEGER); CREATE TABLE threads(id TEXT,project_id TEXT); INSERT INTO projects VALUES("p","P",0,1,2); INSERT INTO threads VALUES("t","p");')
        c.close()
        before={n:m.fingerprint(home/n) for n in m.NAMES}
        report=m.diagnose(home,root/'out',True)
        self.assertEqual(report['sql_projects'],1)
        self.assertEqual(report['candidate_status'],'PREPARED_PRIVATE_NOT_APPLIED')
        self.assertEqual(before,{n:m.fingerprint(home/n) for n in m.NAMES})
        with self.assertRaises(ValueError): m.diagnose(home,home/'unsafe',True)

if __name__ == '__main__': unittest.main()
