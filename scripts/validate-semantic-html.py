#!/usr/bin/env python3
"""Limited validator for the proposed static RAY/PRISM/LENS HTML serialization.

This is not a general HTML sanitizer, ADF converter, browser, or semantic reviewer.
Run: python scripts/validate-semantic-html.py ray-html/assets/intent-example.html
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
BAD_TAGS = {'script', 'iframe', 'object', 'embed', 'form', 'base'}
SECTIONS = {
    'ray': ('data-ray-field', ['result', 'angle', 'why']),
    'prism': ('data-prism-section', ['problem', 'requirements', 'invariants', 'solution', 'measures', 'traceability', 'open-questions']),
    'lens': ('data-lens-section', ['limits', 'execution', 'needs', 'signals', 'handoff']),
}
GRADES = {'1': 'Consider', '2': 'Prefer', '3': 'Strong', '4': 'Required'}

class ArtifactParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.docs = []
        self.sections = []
        self.events = []
        self.errors = []
        self.titles = []
        self.body_text = []
        self.lang = None
        self.charset = None
        self.tracked = []

    def handle_starttag(self, tag, attrs_list):
        attrs = dict(attrs_list)
        if tag in BAD_TAGS:
            self.errors.append(f'Forbidden active tag <{tag}>')
        for name, value in attrs_list:
            if re.fullmatch(r'on[a-z]+', name, re.I):
                self.errors.append(f'Forbidden active attribute {name}')
            if isinstance(value, str) and value.strip().lower().startswith('javascript:'):
                self.errors.append(f'Forbidden javascript URL in {name}')
        if tag == 'link':
            self.errors.append('External stylesheet/link elements are not self-contained')
        if tag == 'img' and (attrs.get('src', '').startswith(('http:', 'https:', '//'))):
            self.errors.append('Remote image found in standalone HTML')
        if tag == 'html': self.lang = attrs.get('lang')
        if tag == 'meta' and 'charset' in attrs: self.charset = attrs['charset'].lower()
        if tag == 'main': self.docs.append(attrs)
        for key in ['data-ray-field', 'data-prism-section', 'data-lens-section']:
            if key in attrs:
                self.sections.append((key, attrs[key]))
        if tag in ('li', 'tr', 'p') or 'data-trace' in attrs:
            self.tracked.append({'tag': tag, 'attrs': attrs, 'text': [], 'depth': len(self.stack)})
        if tag not in VOID:
            self.stack.append(tag)
        self.events.append(('open', tag, attrs))

    def handle_data(self, data):
        self.body_text.append(data)
        for entry in self.tracked:
            entry['text'].append(data)

    def handle_entityref(self, name):
        self.handle_data('&' + name + ';')

    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack:
            self.errors.append(f'Unexpected closing tag </{tag}>')
            return
        if self.stack[-1] != tag:
            self.errors.append(f'Unexpected closing tag </{tag}> (expected </{self.stack[-1]}>)')
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag: self.stack.pop()
                if self.stack: self.stack.pop()
        else:
            self.stack.pop()
        closing = [x for x in self.tracked if x['tag'] == tag and x['depth'] == len(self.stack)]
        for item in closing:
            item['text'] = ' '.join(''.join(item['text']).split())
            self.events.append(('item', tag, item))
            self.tracked.remove(item)


def analyze(text, expected=None):
    parser = ArtifactParser()
    parser.feed(text)
    parser.close()
    errors = list(parser.errors)
    if parser.stack:
        errors.append('Unclosed HTML tags: ' + ', '.join(parser.stack[-5:]))
    if not re.match(r'\s*<!doctype html>', text, re.I):
        errors.append('Missing HTML5 doctype')
    if parser.lang is None or not parser.lang.strip(): errors.append('Missing html language')
    if parser.charset != 'utf-8': errors.append('Missing UTF-8 meta charset')
    if len(parser.docs) != 1:
        errors.append(f'Expected exactly one <main>, found {len(parser.docs)}')
        return {'ok': False, 'errors': errors, 'skill': None}
    attrs = parser.docs[0]
    skill = attrs.get('data-skill')
    if skill not in SECTIONS: errors.append('Unrecognized data-skill on main')
    if expected and skill != expected: errors.append(f'Expected skill {expected}, found {skill}')
    if skill in SECTIONS:
        if attrs.get('data-format') != f'{skill}/v1':
            errors.append(f'Invalid data-format for {skill}')
        key, want = SECTIONS[skill]
        got = [v for k,v in parser.sections if k == key]
        if got != want: errors.append(f'{skill} sections not in contract order: {got}')
    items = [x[2] for x in parser.events if x[0] == 'item']
    if skill == 'ray':
        decisions = [x for x in items if x['attrs'].get('data-grade') is not None]
        if not decisions and 'data-angle="open"' not in text:
            errors.append('RAY needs graded Angle items or open Angle marker')
        for d in decisions:
            grade = d['attrs'].get('data-grade')
            if grade not in GRADES:
                errors.append(f'Invalid RAY grade {grade}')
                continue
            label = d['attrs'].get('data-grade-label')
            if label and label != GRADES[grade]: errors.append(f'Mismatched grade label for {grade}')
            if f'[{grade}:{GRADES[grade]}]' not in d['text']:
                errors.append(f'Grade {grade} not visible as [{grade}:{GRADES[grade]}]')
    if skill == 'prism':
        ids = [x['attrs']['data-prism-id'] for x in items if 'data-prism-id' in x['attrs']]
        if len(ids) != len(set(ids)): errors.append('Duplicate PRISM ID')
        for letter in ('R', 'I', 'S', 'M'):
            if not any(re.fullmatch(letter + r'[1-9]\d*', v) for v in ids):
                errors.append(f'Missing PRISM {letter}#')
        for val in ids:
            if not re.fullmatch(r'[RISM][1-9]\d*', val): errors.append(f'Invalid PRISM ID {val}')
        for d in items:
            if d['attrs'].get('data-prism-id', '').startswith('S'):
                if d['attrs'].get('data-decision-state') not in ('fixed','preferred','open'):
                    errors.append('S# requires fixed/preferred/open decision state')
        traces = [x['attrs']['data-trace'] for x in items if 'data-trace' in x['attrs']]
        for tr in traces:
            for target in tr.split():
                if target not in ids: errors.append(f'Traceability refers to missing PRISM {target}')
        if not traces: errors.append('Missing traceability markers')
    if skill == 'lens':
        for k in ('data-source-spec','data-source-status','data-delivery-target','data-status'):
            if not attrs.get(k): errors.append(f'Missing {k}')
        if attrs.get('data-status') not in ('draft','blocked','approved'):
            errors.append('Invalid LENS status')
        coverage = [x for x in items if 'data-requirement' in x['attrs']]
        works = [x for x in items if 'data-work-id' in x['attrs'] and 'data-prism-links' in x['attrs']]
        signals = [x for x in items if 'data-work-id' in x['attrs'] and 'data-measures' in x['attrs']]
        cov_ids = [x['attrs']['data-requirement'] for x in coverage]
        work_ids = [x['attrs']['data-work-id'] for x in works]
        signal_ids = [x['attrs']['data-work-id'] for x in signals]
        if not coverage: errors.append('LENS missing requirement coverage')
        if not works: errors.append('LENS missing W# work units')
        if len(cov_ids) != len(set(cov_ids)): errors.append('Duplicate requirement coverage')
        if len(work_ids) != len(set(work_ids)): errors.append('Duplicate W#')
        for c in coverage:
            if not re.fullmatch(r'R[1-9]\d*',c['attrs']['data-requirement']): errors.append('Invalid R# coverage')
            if c['attrs'].get('data-delivery') not in ('Now','Later','Outside this delivery'):
                errors.append('Invalid coverage delivery classification')
        for w in works:
            a=w['attrs'];wid=a['data-work-id'];deps=a.get('data-depends-on','')
            if not re.fullmatch(r'W[1-9]\d*',wid):errors.append(f'Invalid work ID {wid}')
            if not a.get('data-prism-links'):errors.append(f'No PRISM links for {wid}')
            for dep in re.findall(r'W[1-9]\d*',deps):
                if dep not in work_ids:errors.append(f'{wid}: unknown dependency {dep}')
            for req in re.findall(r'R[1-9]\d*',a.get('data-prism-links','')):
                if req not in cov_ids: errors.append(f'{wid}: unknown requirement {req}')
            if wid not in signal_ids:errors.append(f'{wid}: missing Signal row')
        for c in coverage:
            if c['attrs'].get('data-delivery')=='Now':
                req=c['attrs']['data-requirement']
                if not any(req in w['attrs'].get('data-prism-links','').split() for w in works):
                    errors.append(f'Now requirement {req} has no work unit')
        for s in signals:
            if not re.fullmatch(r'W[1-9]\d*',s['attrs']['data-work-id']):errors.append('Invalid signal work ID')
            if not re.search(r'\bM[1-9]\d*\b',s['attrs'].get('data-measures','')):errors.append('Signal has no M#')
        for n in [x for x in items if 'data-need-id' in x['attrs']]:
            if n['attrs'].get('data-need-type') not in ('Blocker','Risk','Question'):errors.append('Need requires Blocker/Risk/Question')
            if attrs.get('data-status')=='approved' and n['attrs'].get('data-need-type')=='Blocker': errors.append('Approved plan has unresolved Blocker')
        if attrs.get('data-status')=='approved' and attrs.get('data-source-status')!='approved':
            errors.append('Approved plan requires approved source spec')
    return {'ok': not errors, 'errors': errors, 'skill': skill, 'status': attrs.get('data-status'), 'sections':len(parser.sections)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('path',type=Path)
    ap.add_argument('--skill',choices=('ray','prism','lens'))
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    try: result=analyze(args.path.read_text(encoding='utf-8'),expected=args.skill)
    except (OSError,UnicodeError) as exc:
        print(f'Cannot read HTML: {exc}',file=sys.stderr);return 2
    if args.json: print(json.dumps(result,indent=2))
    else:
        print(f'{args.path}: {"PASS" if result["ok"] else "FAIL"} ({result.get("skill")})')
        for error in result['errors']: print(f'  - {error}')
    return 0 if result['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
