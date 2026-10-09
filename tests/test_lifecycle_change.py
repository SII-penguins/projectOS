"""Observable safety and useful-success contracts for the explicit write path."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import lifecycle_change as change
import test_projectos_tools as fixtures
from test_transition_audit import EXIT_TABLE

class ChangeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'project'; self.root.mkdir()
        self.state = Path(self.tmp.name)/'state'; self.state.mkdir(mode=0o700)
        fixtures.ProjectOSToolsTest().make_base_project(self.root)
        p = self.root/'doc/IMPLEMENTATION_PLAN.md'; p.write_text(p.read_text()+EXIT_TABLE)
        self.req = dict(operation_id='one', task_ids=['T-001'], exit_ids=[], read_paths=[], decisions={},
                        edits=[dict(path='TODO.md', old='| Ready |', new='| Blocked |')])
    def contents(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def run_change(self, r=None):return change.apply(self.root,self.state,r or self.req)
    def test_useful_success_real_before_after_and_replay(self):
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'applied',r)
        self.assertIn('| Blocked |',(self.root/'TODO.md').read_text())
        self.assertNotEqual(before,self.contents());self.assertTrue(change.receipt_current(self.root,r))
        self.assertEqual(r['semantic_acceptance'],'unverified');self.assertEqual(len(r['steps']),5)
        after=self.contents();self.assertTrue(self.run_change()['replayed']);self.assertEqual(after,self.contents())

    def typed_history(self, outcome='ABORTED', kind='run/attempt', identity='R-017'):
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        archive.write_text('| ID | Object | Status | Evidence |\n| --- | --- | --- | --- |\n'
                           f'| {identity} | {kind} | {outcome} | receipt.json: observed outcome, not task acceptance |\n')
        return archive

    def test_existing_typed_terminal_attempt_does_not_block_fact_sync(self):
        archive=self.typed_history(); history=archive.read_bytes()
        result=self.run_change()
        self.assertEqual(result['status'],'applied',result)
        self.assertEqual(archive.read_bytes(),history)
        self.assertTrue(change.receipt_current(self.root,result))
        self.assertEqual(result['semantic_acceptance'],'unverified')

    def test_untyped_or_explicit_task_failure_is_not_reinterpreted_as_run(self):
        archive=self.typed_history(kind='task',outcome='FAILED')
        before=self.contents(); result=self.run_change()
        self.assertEqual(result['status'],'rejected',result)
        self.assertEqual(self.contents(),before)
        archive.write_text(archive.read_text().replace(' | Object','').replace(' | task','')
                           .replace('| --- | --- | --- | --- |','| --- | --- | --- |'))
        before=self.contents();result=self.run_change()
        self.assertEqual(result['status'],'rejected',result)
        self.assertEqual(self.contents(),before)

    def test_running_or_unknown_archive_attempt_is_not_certified_terminal(self):
        for outcome,kind in [('RUNNING','run'),('awaiting evidence','attempt'),('Done','milestone')]:
            with self.subTest(outcome=outcome,kind=kind):
                self.typed_history(outcome,kind)
                before=self.contents();result=self.run_change()
                self.assertEqual(result['status'],'rejected',result)
                self.assertEqual(self.contents(),before)

    def test_task_cannot_be_relabelled_as_failed_run_to_drop_obligation(self):
        todo=self.root/'TODO.md'; row=next(l for l in todo.read_text().splitlines(True) if l.startswith('| T-001 |'))
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        archive.write_text('| ID | Object | Status | Evidence |\n| --- | --- | --- | --- |\n')
        old=archive.read_text()
        self.req['edits']=[dict(path='TODO.md',old=row,new=''),dict(path='doc/archive/TASKS.md',old=old,
            new=old+'| T-001 | run | FAILED | receipt.json |\n')]
        before=self.contents();result=self.run_change()
        self.assertEqual(result['status'],'rejected',result)
        self.assertIn('OBJECT_KIND_CHANGED',result['error'])
        self.assertEqual(self.contents(),before)

    def test_completed_attempt_does_not_trigger_task_verification_update(self):
        self.contract()
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        archive.write_text('| ID | Object | Status | Evidence |\n| --- | --- | --- | --- |\n')
        old=archive.read_text(); self.req['task_ids'].append('R-017')
        self.req['edits'].append(dict(path='doc/archive/TASKS.md',old=old,
            new=old+'| R-017 | run | COMPLETED | receipt.json: completion of attempt, no acceptance claim |\n'))
        result=self.run_change()
        self.assertEqual(result['status'],'applied',result)
        self.assertEqual(result['verification_review'],{})

    def test_new_typed_archive_record_cannot_hide_active_or_unknown_object(self):
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        old='| ID | Object | Status | Evidence |\n| --- | --- | --- | --- |\n'
        archive.write_text(old)
        self.req['task_ids'].append('R-017')
        for kind,outcome in [('attempt','RUNNING'),('run','unknown'),('milestone','Done')]:
            with self.subTest(kind=kind,outcome=outcome):
                request=copy.deepcopy(self.req)
                request['edits'].append(dict(path='doc/archive/TASKS.md',old=old,
                    new=old+f'| R-017 | {kind} | {outcome} | receipt.json |\n'))
                before=self.contents();result=self.run_change(request)
                self.assertEqual(result['status'],'rejected',result)
                self.assertEqual(self.contents(),before)
    def test_replaced_requirement_is_rejected_without_writes(self):
        self.req['exit_ids']=['S1-G1'];self.req['edits']=[dict(path='doc/IMPLEMENTATION_PLAN.md',old='Check passes | Open',new='Weaker target | Open')]
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'rejected');self.assertEqual(before,self.contents())
    def test_undeclared_task_row_cannot_change(self):
        self.req['task_ids']=[];before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())
    def test_frozen_and_outside_paths_rejected(self):
        for name in ('doc/PRD.md','../outside.md','/tmp/outside.md','projectos.audit.json','code.py'):
            r=copy.deepcopy(self.req);r['edits']=[dict(path=name,old='',new='overwritten')]
            before=self.contents();self.assertEqual(self.run_change(r)['status'],'rejected');self.assertEqual(before,self.contents())
    def test_aliases_rejected(self):
        p=self.root/'TODO.md';text=p.read_text();p.unlink();outside=Path(self.tmp.name)/'outside';outside.write_text(text)
        p.symlink_to(outside);self.assertEqual(self.run_change()['status'],'rejected');p.unlink();os.link(outside,p)
        self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(outside.read_text(),text)
    def test_acceptance_and_dependency_changes_need_rationale(self):
        for old,new in [('Check passes','File exists'),('| None |','| Approval required |')]:
            r=copy.deepcopy(self.req);r['edits']=[dict(path='TODO.md',old=old,new=new)]
            before=self.contents();result=self.run_change(r);self.assertEqual(result['status'],'rejected',result);self.assertEqual(before,self.contents())
    def test_explicit_scoped_review_is_not_authorization(self):
        self.req['edits']=[dict(path='TODO.md',old='Check passes',new='Check passes and evidence recorded')]
        self.req['decisions']={'T-001':'Existing accepted gate retained; add evidence recording.'}
        r=self.run_change();self.assertEqual(r['status'],'applied',r);self.assertEqual(r['semantic_acceptance'],'unverified')
        self.assertTrue(r['transition']['findings'])
    def test_unique_old_text_required(self):
        self.req['edits'][0]['old']='|';before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())
    def test_prewrite_drift_never_overwrites(self):
        real=change.atomic_json
        def drifting(p,data):
            real(p,data)
            if data['status']=='prepared': (self.root/'TODO.md').write_text('Concurrent writer\n')
        with patch.object(change,'atomic_json',side_effect=drifting):r=self.run_change()
        self.assertEqual(r['status'],'incomplete');self.assertEqual((self.root/'TODO.md').read_text(),'Concurrent writer\n')
        self.assertNotIn('receipt',json.loads((self.state/'one.json').read_text()))
    def two_writes(self):
        self.req['edits'].append(dict(path='PROGRESS.md',old='Next Action:',new='Current blocker: Await input\nNext Action:'))
    def test_partial_write_resume_finishes_only_missing(self):
        self.two_writes();real=change.replace_file;calls=[]
        def interrupted(root,p,old,new):
            calls.append(p)
            if len(calls)==2:raise OSError('simulated interrupted write')
            real(root,p,old,new)
        before=self.contents()
        with patch.object(change,'replace_file',side_effect=interrupted):r=self.run_change()
        self.assertEqual(r['status'],'incomplete');self.assertNotEqual(before,self.contents())
        self.assertNotIn('receipt',json.loads((self.state/'one.json').read_text()))
        remaining=[]
        with patch.object(change,'replace_file',side_effect=lambda *a:(remaining.append(a[1]),real(*a))[1]):r=self.run_change()
        self.assertEqual(r['status'],'applied',r);self.assertEqual(len(remaining),1)
    def test_resumed_drift_is_preserved_without_rollback(self):
        self.two_writes();real=change.replace_file;n=[]
        def fail(*args):
            if n:raise OSError('stop')
            real(*args);n.append(args[1])
        with patch.object(change,'replace_file',side_effect=fail):self.run_change()
        (self.root/'TODO.md').write_text('new concurrent task state\n');before=self.contents()
        self.assertEqual(self.run_change()['status'],'incomplete');self.assertEqual(before,self.contents())
    def test_after_compare_cannot_be_omitted(self):
        real=change.validate_change;n=[]
        def fail(*args):
            if n:raise ValueError('actual compare failed')
            n.append(1);return real(*args)
        with patch.object(change,'validate_change',side_effect=fail):r=self.run_change()
        self.assertEqual(r['status'],'incomplete');self.assertNotIn('receipt',json.loads((self.state/'one.json').read_text()))
        self.assertEqual(self.run_change()['status'],'applied')
    def test_stale_receipt_and_changed_id_payload_rejected(self):
        r=self.run_change();(self.root/'TODO.md').write_text((self.root/'TODO.md').read_text()+'later\n')
        self.assertFalse(change.receipt_current(self.root,r));self.assertEqual(self.run_change()['status'],'incomplete')
        self.req['edits'][0]['new']='| Ready |';self.assertNotEqual(self.run_change()['status'],'applied')
    def test_missing_steps_and_version_binding_not_valid(self):
        r=self.run_change();r['steps'].pop();self.assertFalse(change.receipt_current(self.root,r))
        r=self.run_change();r['binding']={};self.assertFalse(change.receipt_current(self.root,r))
    def test_unsupported_structure_is_explicitly_partial(self):
        p=self.root/'doc/IMPLEMENTATION_PLAN.md';p.write_text(p.read_text().replace(EXIT_TABLE,''))
        r=self.run_change();self.assertEqual(r['status'],'applied');self.assertFalse(r['transition']['coverage']['explicit_exits'])
        self.assertEqual(r['transition']['status'],'partial')
    def test_archive_existing_row_preserved_and_resume_no_duplicate(self):
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        archive.write_text('| ID | Status | Evidence |\n| --- | --- | --- |\n| T-999 | Done | old.log |\n')
        self.req['task_ids'].append('T-999');self.req['edits']=[dict(path='doc/archive/TASKS.md',old='old.log',new='new.log')]
        before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())

    def test_trusted_chain_detects_bypass_fake_file_and_stale_receipt(self):
        before=change.capture_receipt_state(self.root)
        (self.root/'TODO.md').write_text((self.root/'TODO.md').read_text().replace('| Ready |','| Blocked |'))
        (self.root/'fake-receipt.json').write_text('{"status":"applied"}')
        after=change.capture_receipt_state(self.root)
        self.assertEqual(change.receipt_chain(before,after,[])['status'],'unverified')
    def test_chain_rejects_posthoc_noop_and_missing_steps(self):
        before=change.capture_receipt_state(self.root);request=copy.deepcopy(self.req);r=self.run_change()
        after=change.capture_receipt_state(self.root);call={'call_id':'host1','request':request,'result':r}
        self.assertEqual(change.receipt_chain(before,after,[call])['status'],'covered')
        bad=copy.deepcopy(call);bad['result']['steps'].pop()
        self.assertEqual(change.receipt_chain(before,after,[bad])['status'],'unverified')
        bad=copy.deepcopy(call);bad['result']['before']=r['after']
        self.assertEqual(change.receipt_chain(before,after,[bad])['status'],'unverified')
        (self.root/'TODO.md').write_text((self.root/'TODO.md').read_text()+'later change\n')
        self.assertEqual(change.receipt_chain(before,change.capture_receipt_state(self.root),[call])['status'],'unverified')
    def test_archive_append_resume_does_not_duplicate_and_obligation_disposition_preserved(self):
        archive=self.root/'doc/archive/TASKS.md';archive.parent.mkdir(exist_ok=True)
        archive.write_text('| ID | Status | Evidence |\n| --- | --- | --- |\n')
        todo=(self.root/'TODO.md').read_text();row=next(x for x in todo.splitlines(True) if '| T-001 |' in x)
        self.req.update(exit_ids=['S1-G1'],decisions={'S1-G1':'Check result recorded in check.log, acceptance review still required'},edits=[
          dict(path='TODO.md',old=row,new=''),
          dict(path='doc/archive/TASKS.md',old='| --- | --- | --- |\n',new='| --- | --- | --- |\n| T-001 | Done | check.log |\n'),
          dict(path='doc/IMPLEMENTATION_PLAN.md',old='| Open | T-001 | |',new='| Satisfied | T-001 | check.log |')])
        r=self.run_change();self.assertEqual(r['status'],'applied',r)
        self.run_change();self.assertEqual(archive.read_text().count('| T-001 |'),1)
    def test_section_mapped_owner_does_not_grant_whole_file(self):
        (self.root/'projectos.audit.json').write_text(json.dumps({'documents':{'todo':{'path':'TODO.md','section':'Tasks'}}}))
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'rejected');self.assertEqual(before,self.contents())

    def test_mapping_cannot_grant_code_or_frozen_owner_writes(self):
        for name in ('counter.py','docs/CONTRACT.md','doc/PRD.md'):
            p=self.root/name;p.parent.mkdir(exist_ok=True);p.write_text('frozen input\n')
            (self.root/'projectos.audit.json').write_text(json.dumps({'documents':{'progress':None,'todo':name,'plan':None,'archive':None}}))
            req=copy.deepcopy(self.req);req['edits']=[dict(path=name,old='frozen input',new='replacement')]
            before=self.contents();r=self.run_change(req);self.assertEqual(r['status'],'rejected',r);self.assertEqual(before,self.contents())

    def contract(self, status='Active'):
        p=self.root/'docs/CONTRACT.md';p.parent.mkdir(exist_ok=True)
        p.write_text('Status: '+status+'\nCanonical For: accepted behavior\nLast Reconciled: 2026-10-03\nContract Version: 1\nLast Verified Against: pending implementation\n\nFrozen requirement: retain punctuation.\n')
        (self.root/'implementation.py').write_text('def result(): return 1\n')
        (self.root/'check.txt').write_text('one bounded assertion passed\n')
        return p

    def verification(self, status='verified'):
        return {'path':'docs/CONTRACT.md','old':'pending implementation','status':status,
                'scope':'one result assertion only','sources':['implementation.py'],'evidence':['check.txt'],
                'reason':'actual bounded evidence reviewed; no wider claim'}

    def test_metadata_operation_preserves_all_other_bytes_and_binds_evidence(self):
        p=self.contract();old=p.read_text();self.req['verification_updates']=[self.verification()]
        r=self.run_change();self.assertEqual(r['status'],'applied',r)
        new=p.read_text();self.assertEqual(old.split('Last Verified Against:')[0],new.split('Last Verified Against:')[0])
        self.assertEqual(old.split('\n\n')[1],new.split('\n\n')[1])
        self.assertIn(change.sha((self.root/'implementation.py').read_bytes()),new)
        self.assertIn(change.sha((self.root/'check.txt').read_bytes()),new)
        self.assertIn('unverified',r['verification_review']['docs/CONTRACT.md']['evidence_validity'])
        self.assertTrue(change.receipt_current(self.root,r))

    def test_completion_requires_explicit_verification_owner_disposition(self):
        self.contract();self.req['exit_ids']=['S1-G1'];self.req['decisions']={'S1-G1':'Bounded check'}
        self.req['edits']=[dict(path='doc/IMPLEMENTATION_PLAN.md',old='| Open | T-001 | |',new='| Satisfied | T-001 | check.txt |')]
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'rejected');self.assertIn('verification-owner disposition',r['error']);self.assertEqual(before,self.contents())
        self.req['decisions']['docs/CONTRACT.md']='Unrelated contract; this exit checks another owner. Keep provenance unverified.'
        r=self.run_change();self.assertEqual(r['status'],'applied',r)
        self.assertIn('pending implementation',(self.root/'docs/CONTRACT.md').read_text())
        self.assertEqual(r['verification_review']['docs/CONTRACT.md']['disposition'],'retained')

    def test_partial_and_unverified_are_not_promoted_to_complete(self):
        p=self.contract();self.req['verification_updates']=[self.verification('partial')]
        r=self.run_change();self.assertEqual(r['status'],'applied',r);self.assertIn('Last Verified Against: partial;',p.read_text())
        self.assertIn('| Open |',(self.root/'doc/IMPLEMENTATION_PLAN.md').read_text())
        old=change.header_field(p.read_text(),'Last Verified Against')
        self.req.update(operation_id='unverified',edits=[],verification_updates=[dict(self.verification('unverified'),old=old,sources=[],evidence=[],scope='No applicable implementation evidence')])
        r=self.run_change();self.assertEqual(r['status'],'applied',r);self.assertIn('Last Verified Against: unverified;',p.read_text())
        self.assertEqual(r['semantic_acceptance'],'unverified')

    def test_missing_evidence_cannot_write_verified_metadata(self):
        self.contract();item=self.verification();item['evidence']=['missing.txt'];self.req['verification_updates']=[item]
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'rejected');self.assertEqual(before,self.contents())
        item['evidence']=[];self.assertEqual(self.run_change()['status'],'rejected')

    def test_historical_contract_is_not_refreshed(self):
        self.contract('Archived');self.req['verification_updates']=[self.verification()]
        before=self.contents();r=self.run_change();self.assertEqual(r['status'],'rejected');self.assertEqual(before,self.contents())

    def test_metadata_does_not_grant_contract_body_or_other_header_writes(self):
        self.contract();self.req['verification_updates']=[self.verification()]
        for old,new in [('Frozen requirement','Weakened requirement'),('Status: Active','Status: Archived'),('Contract Version: 1','Contract Version: 2')]:
            self.req['edits']=[dict(path='docs/CONTRACT.md',old=old,new=new)]
            before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())

    def test_ambiguous_or_body_only_verification_field_is_rejected(self):
        p=self.contract();self.req['verification_updates']=[self.verification()]
        p.write_text(p.read_text().replace('Last Verified Against: pending implementation','Last Verified Against: pending implementation\nLast Verified Against: pending implementation'))
        self.assertEqual(self.run_change()['status'],'rejected')
        p.write_text(p.read_text().replace('Contract Version: 1\n','Contract Version: 1\n\n'))
        self.assertEqual(self.run_change()['status'],'rejected')

    def test_related_read_drift_reaches_complete_coverage(self):
        p=self.contract();before=change.capture_receipt_state(self.root);request=copy.deepcopy(self.req);r=self.run_change()
        call={'call_id':'host1','request':request,'result':r}
        p.write_text(p.read_text().replace('pending implementation','uncovered later verification'))
        self.assertFalse(change.receipt_current(self.root,r))
        after=change.capture_receipt_state(self.root,[call]);c=change.receipt_chain(before,after,[call])
        self.assertEqual(c['mapped_owner_coverage'],'covered');self.assertEqual(c['status'],'unverified')
        self.assertIn('docs/CONTRACT.md',c['uncovered_related_inputs'])

    def test_genuine_successive_metadata_operations_supersede_old_receipt(self):
        p=self.contract();before=change.capture_receipt_state(self.root);self.req['verification_updates']=[self.verification('partial')]
        first=copy.deepcopy(self.req);r1=self.run_change();self.assertEqual(r1['status'],'applied',r1)
        self.req.update(operation_id='two',edits=[],verification_updates=[dict(self.verification(),old=change.header_field(p.read_text(),'Last Verified Against'))])
        r2=self.run_change();self.assertEqual(r2['status'],'applied',r2);self.assertFalse(change.receipt_current(self.root,r1));self.assertTrue(change.receipt_current(self.root,r2))
        calls=[{'call_id':'a','request':first,'result':r1},{'call_id':'b','request':copy.deepcopy(self.req),'result':r2}]
        self.assertEqual(change.receipt_chain(before,change.capture_receipt_state(self.root,calls),calls)['status'],'covered')

    def test_later_receipt_cannot_hide_prior_uncovered_metadata_change(self):
        p=self.contract();before=change.capture_receipt_state(self.root);req=copy.deepcopy(self.req);r1=self.run_change()
        p.write_text(p.read_text().replace('pending implementation','direct untracked claim'))
        self.req.update(operation_id='two',edits=[],verification_updates=[dict(self.verification(),old='direct untracked claim')])
        r2=self.run_change();self.assertEqual(r2['status'],'applied',r2)
        calls=[{'call_id':'a','request':req,'result':r1},{'call_id':'b','request':copy.deepcopy(self.req),'result':r2}]
        c=change.receipt_chain(before,change.capture_receipt_state(self.root,calls),calls)
        self.assertTrue(change.receipt_current(self.root,r2));self.assertEqual(c['status'],'unverified');self.assertIn('before continuity: docs/CONTRACT.md',c['errors'])

    def test_observed_bypass_then_restore_remains_unverified(self):
        p=self.contract();before=change.capture_receipt_state(self.root);old=p.read_text()
        p.write_text(old.replace('pending implementation','direct edit'))
        _,bad=change.observe_receipts(self.root,before,[])
        p.write_text(old)
        _,restored=change.observe_receipts(self.root,before,[],bad['historical_unverified_boundaries'])
        self.assertEqual(restored['current_status'],'covered');self.assertEqual(restored['status'],'unverified')

    def test_missing_full_observation_or_input_is_not_success(self):
        self.contract();before=change.capture_receipt_state(self.root);req=copy.deepcopy(self.req);r=self.run_change();calls=[{'call_id':'a','request':req,'result':r}]
        after=change.capture_receipt_state(self.root,calls);after['receipt_files'].pop('docs/CONTRACT.md')
        self.assertEqual(change.receipt_chain(before,after,calls)['status'],'unverified')
        before.pop('receipt_files');self.assertEqual(change.receipt_chain(before,after,calls)['status'],'unverified')

    def test_later_call_omitting_old_related_input_does_not_drop_tracking(self):
        self.contract();before=change.capture_receipt_state(self.root);self.req['read_paths']=['implementation.py'];first=copy.deepcopy(self.req);r1=self.run_change()
        self.req.update(operation_id='two',read_paths=[],edits=[dict(path='TODO.md',old='| Blocked |',new='| Ready |')]);r2=self.run_change()
        calls=[{'call_id':'a','request':first,'result':r1},{'call_id':'b','request':copy.deepcopy(self.req),'result':r2}]
        (self.root/'implementation.py').write_text('changed source\n')
        c=change.receipt_chain(before,change.capture_receipt_state(self.root,calls),calls)
        self.assertEqual(c['status'],'unverified');self.assertIn('implementation.py',c['uncovered_related_inputs'])

    def test_new_config_invalidates_absent_config_binding(self):
        before=change.capture_receipt_state(self.root);req=copy.deepcopy(self.req);r=self.run_change();calls=[{'call_id':'a','request':req,'result':r}]
        (self.root/'projectos.audit.json').write_text('{}')
        self.assertFalse(change.receipt_current(self.root,r))
        self.assertEqual(change.receipt_chain(before,change.capture_receipt_state(self.root,calls),calls)['status'],'unverified')

    def test_verification_reference_cannot_inject_another_header_line(self):
        self.contract();name='check\nStatus: Archived.txt';(self.root/name).write_text('evidence')
        item=self.verification();item['evidence']=[name];self.req['verification_updates']=[item]
        before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())

    def test_metadata_updates_cannot_change_each_others_evidence(self):
        p=self.contract();other=self.root/'doc/PRD.md';other.write_text(p.read_text())
        first=self.verification();first['evidence']=['doc/PRD.md']
        second=dict(self.verification(),path='doc/PRD.md')
        self.req['verification_updates']=[first,second]
        before=self.contents();self.assertEqual(self.run_change()['status'],'rejected');self.assertEqual(before,self.contents())

if __name__=='__main__':unittest.main()
