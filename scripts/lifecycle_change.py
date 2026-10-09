#!/usr/bin/env python3
"""Explicit, bounded document changes. No shell, approval inference or global hooks.

apply(root, private_state, request) is also the opt-in host tool entry. State must
be caller-owned; a JSON receipt is not proof of origin without a real host trace.
"""
from __future__ import annotations
import argparse
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

import audit_project_docs as audit
import audit_project_transition as transition

SCHEMA = 'projectos-change-v2'
STEPS = ('capture', 'projected_compare', 'drift_guard', 'bounded_write', 'actual_compare')
LIMITS = ['free-text semantics', 'approval authenticity', 'artifact validity',
          'noncooperating concurrent writers between the last check and replacement',
          'cross-file atomicity', 'receipt authenticity without trusted host trace']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binding():
    base = Path(__file__).resolve().parents[1]
    return {str(p.relative_to(base)): sha(p.read_bytes()) for p in sorted(base.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts
            and (p.name == 'SKILL.md' or p.parent.name in {'scripts', 'references'})}


def path_in(root, name):
    p = Path(name)
    if (not isinstance(name, str) or not name or any(c in name for c in ('\n', '\r', '\0'))
            or p.is_absolute() or '..' in p.parts or str(p) != name):
        raise ValueError('Noncanonical relative path: ' + str(name))
    q = root
    for part in p.parts:
        q = q / part
        if q.is_symlink():
            raise ValueError('Symlink input/output: ' + name)
    if q.exists() and (not q.is_file() or q.stat().st_nlink != 1):
        raise ValueError('Input/output must be an unaliased regular file: ' + name)
    return q


def read(root, name):
    p = path_in(root, name)
    return p.read_bytes().decode('utf-8') if p.exists() else None


def hashes(contents):
    return {p: sha(t.encode()) if t is not None else None for p, t in sorted(contents.items())}


def atomic_json(p, data):
    if p.is_symlink() or (p.exists() and (not p.is_file() or p.stat().st_nlink != 1)):
        raise ValueError('Unsafe operation state')
    fd, name = tempfile.mkstemp(dir=p.parent, prefix='.change-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(name, p)
        d = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(name): os.unlink(name)


def projected_snapshot(before, contents):
    after = copy.deepcopy(before)
    for role, view in after['roles'].items():
        text = contents[view['path']]
        spec = before['config'].get('documents', {}).get(role)
        section = spec.get('section') if isinstance(spec, dict) else None
        view['text'] = audit.select_section(text, section)
    after['files'] = {p: hashes({p: contents[p]})[p] for p in before['files']}
    after.pop('digest'); after['digest'] = transition.digest(after)
    return after


def rows(snapshot):
    result = {}
    for role, view in snapshot['roles'].items():
        if role != 'todo' and not audit.is_archive(role): continue
        for rec in audit.task_records(view['path'], view['text'], snapshot['config']):
            result[(role, rec['id'])] = (rec, view['text'].splitlines()[rec['line']-1])
    return result


def validate_change(before, after, request):
    tasks, exits = set(request['task_ids']), set(request['exit_ids'])
    decisions = request['decisions']
    old, new = rows(before), rows(after)
    for key in old.keys() | new.keys():
        prior, current = old.get(key), new.get(key)
        if prior == current: continue
        tid = key[1]
        # Row numbers can shift without a row changing.
        if prior and current and prior[1] == current[1]: continue
        if tid not in tasks:
            raise ValueError('Unrelated task row changed: ' + tid)
        if audit.is_archive(key[0]) and prior:
            raise ValueError('Existing archive row is immutable: ' + tid)
        if prior and current:
            for field in ('acceptance', 'dependencies'):
                if prior[0][field] != current[0][field] and not decisions.get(tid):
                    raise ValueError(field + ' change needs explicit review rationale: ' + tid)
    def exit_map(s):
        p = s['roles'].get('plan')
        return {r['Exit ID']: r for r in transition.exits_from(p['text'], p['path'])[0]} if p else {}
    a, b = exit_map(before), exit_map(after)
    for eid in a.keys() | b.keys():
        prior, current = a.get(eid), b.get(eid)
        if prior and (not current or prior['Requirement'] != current['Requirement']):
            raise ValueError('Exit identity/requirement must be retained: ' + eid)
        if prior and current and all(prior[k] == current[k] for k in transition.EXIT_COLUMNS): continue
        if eid not in exits: raise ValueError('Exit outside declared scope: ' + eid)
        if prior and prior['Status'] != current['Status'] and not decisions.get(eid):
            raise ValueError('Exit disposition needs explicit review rationale: ' + eid)
    report = transition.compare(before, after)
    errors = [f for f in report['findings'] if f['severity'] == 'ERROR']
    if errors: raise ValueError('Projected transition rejected: ' + json.dumps(errors, ensure_ascii=False))
    return report


def contract_paths(root, config):
    """Existing mapped contract owners, plus the conventional legacy location."""
    paths = {audit.rel(p, root) for role, (p, _) in audit.discover(root, config).items()
             if role in {'prd', 'frontend', 'backend', 'flow'}}
    paths.update(p for p in ('docs/CONTRACT.md', 'doc/CONTRACT.md') if (root/p).exists())
    return paths


def header_field(text, field):
    # Only an existing, unambiguous initial metadata header is writable. A
    # similarly named body paragraph/heading never grants modification rights.
    header = text.split('\n\n', 1)[0]
    matches = re.findall(r'^' + re.escape(field) + r': ([^\r\n]*)$', header, re.M)
    if len(matches) != 1:
        raise ValueError('Missing/unsupported/ambiguous metadata field: ' + field)
    return matches[0]


def completion_changed(before, after):
    old, _ = transition.task_index(before); new, _ = transition.task_index(after)
    completed = {'done', 'completed', 'complete'}
    if any(r.get('object_kind', 'task') != 'attempt' and r['status'] in completed
           and (tid not in old or old[tid]['status'] not in completed)
           for tid, r in new.items()):
        return True
    def exits(s):
        p = s['roles'].get('plan')
        return {r['Exit ID']: audit.norm(r['Status']) for r in transition.exits_from(p['text'], p['path'])[0]} if p else {}
    a, b = exits(before), exits(after)
    if any(status == 'satisfied' and a.get(key) != status for key, status in b.items()):
        return True
    def stages(s):
        p = s['roles'].get('plan')
        return {r[0]: r[2] for r in audit.plan_stages(p['text'])} if p else {}
    a, b = stages(before), stages(after)
    return any(status in completed and a.get(key) not in completed for key, status in b.items())


def verification_changes(root, before, original, proposed, request):
    """Explicit provenance operation, never implementation verification itself."""
    paths = contract_paths(root, before['config'])
    reviews = {}
    section_paths = {v['path'] for v in before['config'].get('documents', {}).values() if isinstance(v, dict)}
    for item in request.get('verification_updates', []):
        path = item['path']
        if path not in paths or path in section_paths or path in reviews:
            raise ValueError('Verification update needs one existing whole contract owner: ' + path)
        text = original[path]
        if header_field(text, 'Status').lower() != 'active':
            raise ValueError('Historical/non-Active contract verification cannot be rewritten: ' + path)
        header_field(text, 'Contract Version')
        if header_field(text, 'Last Verified Against') != item['old']:
            raise ValueError('Verification provenance changed since inspection: ' + path)
        sources, evidence = item['sources'], item['evidence']
        if item['status'] != 'unverified' and (not sources or not evidence):
            raise ValueError('Verified/partial provenance needs source and evidence references')
        for name in sources + evidence:
            if name == path or not original.get(name):
                raise ValueError('Verification source/evidence missing, empty or self-referential: ' + name)
            if proposed[name] != original[name]:
                raise ValueError('Verification input cannot change in its recording operation: ' + name)
        def refs(names):
            return ', '.join(name + '@sha256:' + sha(original[name].encode()) for name in names) or 'none'
        value = (item['status'] + '; scope: ' + item['scope'] + '; sources: ' + refs(sources)
                 + '; evidence: ' + refs(evidence))
        line = 'Last Verified Against: ' + item['old']
        lines = text.splitlines(keepends=True)
        index = next(i for i, v in enumerate(lines) if v.rstrip('\r\n') == line)
        ending = lines[index][len(lines[index].rstrip('\r\n')):]
        lines[index] = 'Last Verified Against: ' + value + ending
        proposed[path] = ''.join(lines)
        if proposed[path] == text:
            raise ValueError('Verification fact unchanged; do not refresh it')
        reviews[path] = {'disposition': item['status'], 'scope': item['scope'], 'reason': item['reason'],
                         'sources': hashes({p: original[p] for p in sources}),
                         'evidence': hashes({p: original[p] for p in evidence}),
                         'evidence_validity': 'unverified; inspect actual execution and applicability'}
    # Another metadata operation in this same request must not invalidate an
    # earlier operation's source/evidence revision (including cross-references).
    for item in request.get('verification_updates', []):
        for name in item['sources'] + item['evidence']:
            if proposed[name] != original[name]:
                raise ValueError('Verification input changed by another operation: ' + name)
    if completion_changed(before, projected_snapshot(before, proposed)):
        for path in sorted(paths):
            text = original[path]
            try:
                active = header_field(text, 'Status').lower() == 'active'
            except ValueError:
                active = True  # Unknown lifecycle is not permission to skip review.
            if not active or path in reviews:
                continue
            reason = request['decisions'].get(path)
            if not reason:
                raise ValueError('Completion needs verification-owner disposition: ' + path
                                 + '; update applicable provenance or give decisions[path] reason for retaining it')
            reviews[path] = {'disposition': 'retained', 'reason': reason,
                             'evidence_validity': 'unverified; applicability and unchanged fact require review'}
    return reviews


def capture_inputs(root, request):
    before = transition.capture(root)
    docs = audit.discover(root, before['config'])
    paths = set(before['files']) | set(request['read_paths']) | {e['path'] for e in request['edits']}
    paths.update(audit.rel(p, root) for p, _ in docs.values())
    # Conventional accepted-contract locations absent from the legacy role map.
    paths.update(p for p in ('docs/CONTRACT.md', 'doc/CONTRACT.md') if (root/p).exists())
    paths.add('projectos.audit.json')  # Absence is also a configuration binding.
    for item in request.get('verification_updates', []):
        paths.update([item['path'], *item['sources'], *item['evidence']])
    contents = {p: read(root, p) for p in sorted(paths)}
    if any(hashes(contents).get(p) != h for p, h in before['files'].items()):
        raise ValueError('Input drift during capture')
    writable = {audit.rel(p, root) for role, (p, _) in docs.items()
                if role in {'progress', 'todo', 'plan', 'archive', 'run'} or audit.is_archive(role) or role.startswith('diag:')}
    section_paths = {v['path'] for v in before['config'].get('documents', {}).values() if isinstance(v, dict)}
    for e in request['edits']:
        name = e['path']
        frozen = {audit.rel(p, root) for role, (p, _) in docs.items()
                  if role not in {'progress', 'todo', 'plan', 'archive', 'run'}
                  and not audit.is_archive(role) and not role.startswith('diag:')}
        frozen.update({'docs/CONTRACT.md', 'doc/CONTRACT.md', 'projectos.audit.json'})
        if not name.endswith('.md') or name in frozen:
            raise ValueError('Frozen/non-document path cannot become writable through role mapping: ' + name)
        if name in section_paths:
            raise ValueError('Section-mapped writes are unsupported by this entry; no whole-file permission inferred')
        # New diagnostics are allowed as narrow factual owner additions. No new
        # contract/code/config owners are smuggled into a lifecycle operation.
        diagnostic = Path(name).parent.as_posix() in ('doc/diagnostics', 'docs/diagnostics') and name.endswith('.md')
        if name not in writable and not diagnostic:
            raise ValueError('Write outside lifecycle owners: ' + name)
    return before, contents


def request_check(request):
    required = {'operation_id', 'task_ids', 'exit_ids', 'read_paths', 'edits', 'decisions'}
    if not isinstance(request, dict) or not required <= set(request) or set(request) - required - {'verification_updates'}:
        raise ValueError('Expected operation_id, task_ids, exit_ids, read_paths, edits, decisions; optional verification_updates')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', request['operation_id']): raise ValueError('Invalid operation_id')
    for k in ('task_ids', 'exit_ids', 'read_paths'):
        if not isinstance(request[k], list) or any(not isinstance(x, str) or not x for x in request[k]):
            raise ValueError('Invalid ' + k)
    if not isinstance(request['decisions'], dict) or any(not isinstance(v, str) or not v.strip() for v in request['decisions'].values()):
        raise ValueError('decisions must map affected IDs to nonempty review rationales, not approvals')
    updates = request.get('verification_updates', [])
    if not isinstance(updates, list) or len(updates) > 20:
        raise ValueError('verification_updates must be a bounded list')
    for item in updates:
        if not isinstance(item, dict) or set(item) != {'path', 'old', 'status', 'scope', 'sources', 'evidence', 'reason'}:
            raise ValueError('Verification update needs path, old, status, scope, sources, evidence, reason')
        for k in ('path', 'old', 'status', 'scope', 'reason'):
            if not isinstance(item[k], str) or not item[k].strip() or '\n' in item[k] or '\r' in item[k]:
                raise ValueError('Invalid single-line verification field: ' + k)
        if item['status'] not in {'verified', 'partial', 'unverified'}:
            raise ValueError('Unsupported verification status')
        for k in ('sources', 'evidence'):
            if not isinstance(item[k], list) or any(not isinstance(p, str) or not p for p in item[k]):
                raise ValueError('Invalid verification ' + k)
    if (not isinstance(request['edits'], list) or len(request['edits']) > 100
            or not request['edits'] and not updates):
        raise ValueError('Need explicit replacements or verification updates')
    for e in request['edits']:
        if not isinstance(e, dict) or set(e) != {'path', 'old', 'new'} or any(not isinstance(v, str) for v in e.values()):
            raise ValueError('Each edit needs path, old, new strings')
        if e['old'] == e['new']: raise ValueError('No-op replacement')
    if len(json.dumps(request)) > 1_000_000: raise ValueError('Operation exceeds bounded input size')


def check_current(root, contents):
    if {p: read(root, p) for p in contents} != contents:
        raise ValueError('Input drift; preserve concurrent edits and reconcile before resuming')


def replace_file(root, name, prior, text):
    p = path_in(root, name)
    if read(root, name) != prior: raise ValueError('Input drift immediately before write: ' + name)
    # No directories are implicitly created; caller chooses/creates a factual
    # diagnostic directory normally, or uses an existing mapped owner.
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix='.projectos-write-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            if p.exists(): os.fchmod(f.fileno(), stat.S_IMODE(p.stat().st_mode))
            f.write(text); f.flush(); os.fsync(f.fileno())
        if read(root, name) != prior: raise ValueError('Input drift before replacement: ' + name)
        os.replace(tmp, p)
        d = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def apply(root, state, request):
    """Apply/resume the SAME request/ID; rejected/incomplete is never success."""
    root, state = Path(root), Path(state)
    journal = None; record = None
    try:
        request_check(request)
        if root.is_symlink() or state.is_symlink(): raise ValueError('No symlink roots')
        root, state = root.resolve(strict=True), state.resolve(strict=True)
        if root == state or root.is_relative_to(state): raise ValueError('State must not contain project')
        if not state.is_dir() or state.stat().st_mode & 0o077: raise ValueError('State directory must be private (0700)')
        lock = state/'change.lock'
        fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o077:
                raise ValueError('Unsafe lock')
            fcntl.flock(fd, fcntl.LOCK_EX)
            journal = state/(request['operation_id']+'.json')
            if journal.exists():
                path_in(state, journal.name)
                record = json.loads(journal.read_text(), object_pairs_hook=audit.unique_json_object)
                if (record['request'] != request or record['project_root'] != str(root) or record['binding'] != binding()):
                    raise ValueError('Operation ID/root/package mismatch; never overwrite old journal')
                if record.get('status') == 'applied':
                    check_current(root, record['expected'])
                    return dict(record['receipt'], replayed=True)
            else:
                before, original = capture_inputs(root, request)
                proposed = dict(original)
                for e in request['edits']:
                    p, old, new = e['path'], e['old'], e['new']
                    text = proposed[p]
                    if text is None:
                        if old: raise ValueError('New file requires empty old text')
                        proposed[p] = new
                    else:
                        if not old or text.count(old) != 1: raise ValueError('Old text must match exactly once: ' + p)
                        proposed[p] = text.replace(old, new, 1)
                verification = verification_changes(root, before, original, proposed, request)
                projected = projected_snapshot(before, proposed)
                preview = validate_change(before, projected, request)
                record = {'schema': SCHEMA, 'project_root': str(root), 'binding': binding(), 'request': request,
                          'before': before, 'original': original, 'expected': proposed,
                          'preview': preview, 'verification_review': verification,
                          'status': 'prepared', 'completed_writes': []}
                check_current(root, original)
                atomic_json(journal, record)  # Durable intent before any project write.
            actual = {p: read(root, p) for p in record['original']}
            writes = [p for p in record['original'] if record['original'][p] != record['expected'][p]]
            for p, t in actual.items():
                if t != record['original'][p] and t != record['expected'][p]:
                    raise ValueError('Input drift during resume: ' + p)
            for p in writes:
                if actual[p] == record['expected'][p]: continue  # Completed before interruption.
                check_current(root, actual)
                replace_file(root, p, actual[p], record['expected'][p])
                actual[p] = record['expected'][p]
                record['completed_writes'].append(p)
                atomic_json(journal, record)
            check_current(root, record['expected'])
            after = transition.capture(root)
            report = validate_change(record['before'], after, request)
            # Discovery must not acquire a new owner unnoticed since preparation.
            if set(after['files']) != set(record['before']['files']):
                raise ValueError('Owner discovery changed; manual reconciliation required')
            receipt = {'schema': SCHEMA, 'status': 'applied', 'operation_id': request['operation_id'],
                       'project_root': str(root), 'binding': record['binding'],
                       'request_digest': transition.digest(request), 'before': hashes(record['original']),
                       'after': hashes(record['expected']), 'write_set': writes,
                       'transition': report, 'semantic_acceptance': 'unverified',
                       'review_rationales': request['decisions'], 'limits': LIMITS,
                       'verification_review': record['verification_review'], 'steps': list(STEPS)}
            check_current(root, record['expected'])
            record.update(status='applied', after=after, receipt=receipt)
            atomic_json(journal, record)
            return receipt
        finally:
            os.close(fd)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never erase a previous successful journal, and never roll project back.
        return {'schema': SCHEMA, 'status': 'incomplete' if journal and journal.exists() else 'rejected',
                'error': str(exc), 'operation_id': request.get('operation_id') if isinstance(request, dict) else None,
                'limits': LIMITS}


def receipt_errors(root, receipt, observed=None):
    """Shared complete validator. observed is a trusted point-in-time hash view.

    Without observed, read actual files. A historical receipt may be checked at
    its own trusted return boundary; that does not certify the final workspace.
    """
    try:
        root = Path(root).resolve(strict=True)
        r = receipt
        if (r.get('schema') != SCHEMA or r.get('status') != 'applied'
                or r['project_root'] != str(root) or r['binding'] != binding()
                or r['steps'] != list(STEPS)):
            return ['invalid receipt schema/status/root/package/steps']
        structural = r['transition']
        coverage = structural['coverage']
        if (structural.get('schema') != transition.SCHEMA
                or structural.get('status') not in {'checked', 'review_required'}
                or coverage.get('gaps') != []
                or any(coverage.get(k) is not True for k in ('task_destinations', 'acceptance_changes', 'explicit_exits'))):
            return ['unsupported/incomplete structural receipt coverage']
        a, b = r['before'], r['after']
        if (not isinstance(a, dict) or not a or not isinstance(b, dict) or set(a) != set(b)
                or 'projectos.audit.json' not in b):
            return ['missing/inconsistent complete input bindings']
        for name in b:
            path_in(root, name)
            if any(value is not None and (not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value))
                   for value in (a[name], b[name])):
                return ['unsupported content binding: ' + name]
        if sorted(r['write_set']) != sorted(p for p in a if a[p] != b[p]):
            return ['write set differs from recorded changes']
        current = observed if observed is not None else hashes({p: read(root, p) for p in b})
        return ['stale or unavailable input: ' + p for p in b if p not in current or current[p] != b[p]]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return ['receipt unverified: ' + str(exc)]


def receipt_current(root, receipt):
    """Same complete content validator; authenticity still needs trusted calls."""
    return not receipt_errors(root, receipt)


def capture_receipt_state(root, calls=(), config_arg=None):
    """Mapped-owner snapshot plus contract/config and all recorded related inputs."""
    root = Path(root).resolve(strict=True)
    snapshot = transition.capture(root, config_arg)
    paths = set(snapshot['files']) | contract_paths(root, snapshot['config']) | {'projectos.audit.json'}
    paths.update(audit.rel(p, root) for p, _ in audit.discover(root, snapshot['config']).values())
    for call in calls:
        if call.get('result', {}).get('status') == 'applied':
            paths.update(call['result']['after'])
    snapshot['receipt_files'] = hashes({p: read(root, p) for p in paths})
    if any(snapshot['receipt_files'].get(p) != h for p, h in snapshot['files'].items()):
        raise ValueError('Receipt inputs drifted during observation')
    snapshot.pop('digest'); snapshot['digest'] = transition.digest(snapshot)
    return snapshot


def receipt_chain(before, after, calls):
    """Trusted chronological call chain; final view includes every related read.

    Later calls may supersede earlier outputs only through matching before-state.
    An omitted related input remains tracked. The caller must retain unverified
    boundary observations, even if a direct change is later reversed.
    """
    errors = []
    if before.get('project_root') != after.get('project_root'):
        errors.append('observation roots differ')
    if 'receipt_files' not in before or 'receipt_files' not in after:
        errors.append('missing full receipt observation; mapped owners alone are insufficient')
    expected = dict(before.get('receipt_files', before.get('files', {})))
    owner_expected = dict(before.get('files', {}))
    for call in calls:
        r = call.get('result', {})
        if r.get('status') != 'applied':
            continue  # Rejection is not a write receipt; actual effects still compared.
        problems = receipt_errors(after['project_root'], r, r.get('after'))
        if (not call.get('call_id') or r.get('request_digest') != transition.digest(call.get('request'))
                or r.get('operation_id') != call.get('request', {}).get('operation_id')):
            problems.append('invalid trusted-call request binding')
        if problems:
            errors.extend(problems); continue
        if r.get('replayed'):
            if any(p in expected and expected[p] != h for p, h in r['after'].items()):
                errors.append('stale replay cannot replace a new operation')
            continue
        for p, h in expected.items():
            if p in r['before'] and r['before'][p] != h:
                errors.append('before continuity: ' + p)
        for p, h in owner_expected.items():
            if r['before'].get(p) != h:
                errors.append('owner before continuity: ' + p)
        expected.update(r['after'])
        for p in owner_expected:
            if p in r['after']: owner_expected[p] = r['after'][p]
        coverage = r.get('transition', {}).get('coverage', {})
        if coverage.get('gaps') or r.get('transition', {}).get('status') in {'partial', 'unchecked'}:
            errors.append('entry has unsupported/incomplete structural coverage')
    final = after.get('receipt_files', after.get('files', {}))
    uncovered = sorted(p for p in owner_expected.keys() | after['files'].keys()
                       if owner_expected.get(p) != after['files'].get(p))
    related = sorted(p for p in expected if p not in final or expected[p] != final[p])
    # Validate the last applicable receipt with the SAME complete rules used by
    # receipt_current, against a captured actual final view, never its own hashes.
    last = next((c['result'] for c in reversed(calls) if c.get('result', {}).get('status') == 'applied'), None)
    if last is not None:
        errors.extend(receipt_errors(after['project_root'], last, final))
    return {'status': 'unverified' if errors or uncovered or related else 'covered',
            'errors': sorted(set(errors)), 'uncovered_owners': uncovered,
            'mapped_owner_coverage': 'unverified' if uncovered else 'covered',
            'uncovered_related_inputs': related, 'tracked_related_inputs': sorted(expected),
            'trusted_call_count': len(calls),
            'limits': ['tool-boundary observations only', 'free-text semantics and authority unverified',
                       'caller must supply trusted host log; JSON content is not proof of origin']}


def observe_receipts(root, baseline, calls, prior_failures=(), config_arg=None):
    """One shared observer for private host and Hook, retaining failed boundaries."""
    try:
        current = capture_receipt_state(root, calls, config_arg)
        report = receipt_chain(baseline, current, calls)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        current = None
        report = {'status': 'unverified', 'errors': ['observation unavailable: ' + str(exc)],
                  'uncovered_owners': [], 'mapped_owner_coverage': 'unverified',
                  'uncovered_related_inputs': [], 'trusted_call_count': len(calls)}
    failures = list(prior_failures)
    if report['status'] != 'covered':
        issue = {'errors': report['errors'], 'owners': report['uncovered_owners'],
                 'related': report['uncovered_related_inputs']}
        if issue not in failures: failures.append(issue)
    report['current_status'] = report['status']
    report['historical_unverified_boundaries'] = failures
    if failures: report['status'] = 'unverified'
    return current, report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', type=Path); ap.add_argument('--state', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    args = ap.parse_args()
    result = apply(args.root, args.state, json.loads(args.request.read_text(), object_pairs_hook=audit.unique_json_object))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'applied' else 1

if __name__ == '__main__': raise SystemExit(main())
