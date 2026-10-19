#!/usr/bin/env python3
"""Dependency-free structural and offline audit of a Storycraft page."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.anchors=[];self.remote=[];self.invalid=[];self.scripts=[];self.styles=0
    def handle_starttag(self,tag, attrs):
        at=dict(attrs)
        if 'id' in at:self.ids.append(at['id'])
        if tag=='script':
            self.scripts.append(at.get('src','inline'))
        if tag=='style':self.styles+=1
        if tag in ('script','link','img','iframe','video','audio','source'):
            for key in ('src','href','poster'):
                value=at.get(key,'')
                if value.startswith(('http://','https://','//')):
                    self.remote.append((tag,key,value))
        if tag=='a':
            href=at.get('href','')
            if href.startswith('#'):
                self.anchors.append(href[1:])
        for key,value in attrs:
            if key.lower().startswith('on'):
                self.invalid.append(f'inline event handler {key} on {tag}')


def check_file(p:Path):
    content=p.read_text(encoding='utf-8')
    parser=Audit();parser.feed(content)
    bad=[]
    for id in set(parser.ids):
        if parser.ids.count(id)>1:bad.append(f'duplicate id #{id}')
    for name in parser.anchors:
        if name and name not in parser.ids:bad.append(f'missing anchor #{name}')
    if not parser.styles:bad.append('missing embedded styles')
    if parser.remote:bad.append(f'external runtime dependencies: {parser.remote}')
    if parser.invalid:bad.extend(parser.invalid)
    if 'http-equiv="refresh"' in content.lower():bad.append('unexpected page redirect')
    for pat in (r'<script[^>]+src\s*=',r'@import\s+url\s*\(',r'url\(\s*[\"\']?https?://',r'\bfetch\s*\(',r'\bXMLHttpRequest\s*\('):
        if re.search(pat,content,re.I):bad.append(f'possible remote runtime dependency: {pat}')
    if '<meta name="viewport"' not in content:bad.append('missing responsive viewport')
    if 'prefers-reduced-motion' not in content:bad.append('missing reduced-motion styling')
    if not content.lstrip().lower().startswith('<!doctype html>'):bad.append('missing HTML5 doctype')
    return bad


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('html',nargs='+',type=Path)
    args=ap.parse_args();failed=False
    for file in args.html:
        issues=check_file(file)
        print(('FAIL' if issues else 'PASS')+' '+str(file))
        for item in issues:print('  - '+item)
        failed |=bool(issues)
    return 1 if failed else 0

if __name__=='__main__':raise SystemExit(main())
