#!/usr/bin/env python3
"""Render an authored story JSON as standalone accessible HTML in three visual styles.

Presentation only. No remote assets, application execution, or source mutations.
Example:
    python scripts/render_story.py examples/burrito-blaster.story.json --style morrito --out burrito-morrito.html
"""
from __future__ import annotations

import argparse
import base64
from html import escape
import json
from pathlib import Path
from typing import Optional
import re
from urllib.parse import urlparse
import sys

STYLES = ('dark', 'morrito', 'gilded')
STYLE_CHOICES = (*STYLES, 'all')
ID_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{0,63}$')


def html(value: object) -> str:
    return escape(str(value), quote=True)


def require_text(obj: dict, key: str, where: str, limit: int = 2000) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{where}.{key} must be nonblank text')
    if len(value) > limit:
        raise ValueError(f'{where}.{key} is too long (max {limit})')
    return value.strip()


def validate_story(model: dict) -> None:
    if not isinstance(model, dict):
        raise ValueError('Story must be a JSON object')
    if model.get('schema_version') != 1:
        raise ValueError('schema_version must be integer 1')
    for field in ('title', 'eyebrow', 'summary', 'source_note'):
        require_text(model, field, 'story', 4000 if field == 'summary' else 500)
    if 'hero_label' in model:
        require_text(model, 'hero_label', 'story', 80)
    if 'badge' in model:
        require_text(model, 'badge', 'story', 36)
    if model.get('hero_symbol', 'spark') not in ('spark', 'burrito', 'leaf', 'compass'):
        raise ValueError('story.hero_symbol must be spark, burrito, leaf, or compass')
    for kind, limit in [('highlights', 5), ('chapters', 8), ('sources', 30), ('callouts', 5)]:
        values = model.get(kind, [])
        if not isinstance(values, list) or len(values) > limit:
            raise ValueError(f'{kind} must be a list of at most {limit} entries')
        for i, entry in enumerate(values):
            if not isinstance(entry, dict):
                raise ValueError(f'{kind}[{i}] must be an object')
    for i, v in enumerate(model.get('callouts', [])):
        if v.get('kind') not in ('important', 'uncertain'):
            raise ValueError(f'callouts[{i}].kind must be important or uncertain')
        require_text(v, 'title', f'callouts[{i}]', 150)
        require_text(v, 'text', f'callouts[{i}]', 900)
    for i, v in enumerate(model.get('highlights', [])):
        for key in ('eyebrow', 'title', 'description'):
            require_text(v, key, f'highlights[{i}]')
    for i, v in enumerate(model.get('chapters', [])):
        for key in ('eyebrow', 'title', 'body'):
            require_text(v, key, f'chapters[{i}]', 6000)
        if not isinstance(v.get('points', []), list) or not all(isinstance(p, str) and p.strip() for p in v.get('points', [])):
            raise ValueError(f'chapters[{i}].points must be a list of nonblank text')
    for i, v in enumerate(model.get('sources', [])):
        require_text(v, 'label', f'sources[{i}]')
        url = require_text(v, 'url', f'sources[{i}]')
        parts = urlparse(url)
        if parts.scheme.lower() not in ('https', 'http', 'mailto') or (parts.scheme.lower() != 'mailto' and not parts.netloc):
            raise ValueError(f'sources[{i}].url requires an explicit https:, http:, or mailto: URL')
    flow = model.get('flow')
    if flow is None:
        return
    if not isinstance(flow, dict):
        raise ValueError('flow must be an object, or absent')
    for key in ('title', 'description'):
        require_text(flow, key, 'flow')
    nodes = flow.get('nodes')
    edges = flow.get('edges')
    route = flow.get('primary_path')
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 20:
        raise ValueError('flow.nodes must contain 2–20 nodes')
    if not isinstance(edges, list) or len(edges) > 50:
        raise ValueError('flow.edges must be a list of at most 50 edges')
    if not isinstance(route, list) or not 2 <= len(route) <= len(nodes):
        raise ValueError('flow.primary_path must contain 2 or more node IDs')
    ids: set[str] = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise ValueError(f'flow.nodes[{i}] must be an object')
        node_id = require_text(node, 'id', f'flow.nodes[{i}]')
        if not ID_PATTERN.fullmatch(node_id) or node_id in ids:
            raise ValueError(f'flow.nodes[{i}].id must be unique safe ID (got {node_id!r})')
        ids.add(node_id)
        for key in ('title', 'summary', 'detail'):
            require_text(node, key, f'flow.nodes[{i}]', 4000)
    pairs = set()
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValueError(f'flow.edges[{i}] must be an object')
        src, dst = edge.get('from'), edge.get('to')
        if src not in ids or dst not in ids:
            raise ValueError(f'flow.edges[{i}] references nonexistent node')
        require_text(edge, 'label', f'flow.edges[{i}]', 300)
        pairs.add((src, dst))
    if any(x not in ids for x in route) or len(route) != len(set(route)):
        raise ValueError('flow.primary_path must contain distinct known node IDs')
    for src, dst in zip(route, route[1:]):
        if (src, dst) not in pairs:
            raise ValueError(f'Primary route declares {src} -> {dst} but no such edge exists')
    if any(node['id'] not in route and not any(e['to'] == node['id'] or e['from'] == node['id'] for e in edges) for node in nodes):
        raise ValueError('Unconnected nodes are not allowed')


BASE_CSS = r'''
:root{--bg:#0b111b;--panel:#142131;--panel2:#182a3e;--edge:#2c3e56;--ink:#eef4f9;--muted:#9cacc0;--soft:#778ba1;--accent:#80c7ef;--accentInk:#0b2031;--good:#73c4a1;--warn:#f9c36b;--shell:1180px;--radius:18px;--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;--serif:Georgia,"Palatino Linotype",serif;--mono:ui-monospace,SFMono-Regular,Consolas,monospace;color-scheme:dark}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65;-webkit-font-smoothing:antialiased}button,a{touch-action:manipulation}button{font:inherit}a{color:inherit}a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:4px}.shell{width:min(var(--shell),calc(100% - 56px));margin:0 auto}
.topbar{padding:20px 0;display:flex;align-items:center;justify-content:space-between;gap:20px;border-bottom:1px solid var(--edge)}.brand{display:flex;align-items:center;gap:12px;text-decoration:none;font-weight:750;letter-spacing:.015em;font-size:15px}.mark{width:34px;height:34px;display:grid;place-items:center;border:1px solid var(--edge);border-radius:11px;background:var(--panel);color:var(--accent)}.mark svg{width:22px;height:22px}.topnote{font:11px var(--mono);color:var(--soft);letter-spacing:.12em;text-transform:uppercase}
.hero{display:grid;grid-template-columns:minmax(0,1.17fr) minmax(320px,.83fr);gap:clamp(34px,5vw,80px);align-items:center;padding:86px 0 80px}.eyebrow,.overline{font:700 11px var(--mono);letter-spacing:.15em;text-transform:uppercase;color:var(--accent)}h1,h2,h3,p{margin-top:0}.hero h1{font-size:clamp(47px,6.5vw,88px);letter-spacing:-.055em;line-height:1.035;margin:20px 0 26px;max-width:12ch;text-wrap:balance}.lede{font-size:clamp(16px,1.55vw,20px);line-height:1.65;color:var(--muted);max-width:60ch;margin:0 0 27px}.actions{display:flex;align-items:center;flex-wrap:wrap;gap:13px}.button{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:44px;padding:11px 18px;border-radius:10px;border:1px solid var(--edge);background:var(--panel);font-weight:750;font-size:13px;text-decoration:none;cursor:pointer;color:var(--ink);transition:transform .16s ease,background .16s ease,border-color .16s ease}.button.primary{border-color:var(--accent);background:var(--accent);color:var(--accentInk)}.button:hover{transform:translateY(-2px)}.button:disabled{cursor:wait;opacity:.75}.hero-note{font:12px/1.5 var(--mono);color:var(--soft);margin-top:20px;max-width:60ch}
.specimen{position:relative;border:1px solid var(--edge);background:linear-gradient(145deg,var(--panel),var(--bg));border-radius:calc(var(--radius) + 3px);box-shadow:0 30px 100px #0003;overflow:hidden;min-width:0}.specimen-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:15px 22px;border-bottom:1px solid var(--edge);font:700 10px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--soft)}.specimen-badge{border:1px solid var(--edge);padding:4px 7px;border-radius:999px;color:var(--accent);white-space:nowrap;max-width:65%;overflow:hidden;text-overflow:ellipsis}.specimen-center{padding:32px 25px 28px;text-align:center;position:relative}.orbit{width:138px;height:138px;margin:0 auto 23px;border-radius:50%;border:1px solid var(--edge);display:grid;place-items:center;background:radial-gradient(circle at 45% 45%,var(--panel2),var(--bg));box-shadow:0 0 0 17px #ffffff05,0 0 0 18px var(--edge)}.orbit svg{width:67px;height:67px;stroke:var(--accent);fill:none;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}.specimen-kicker{font:750 10px var(--mono);letter-spacing:.12em;color:var(--accent);text-transform:uppercase;margin-bottom:8px}.specimen-center h2{font-size:23px;letter-spacing:-.035em;margin:0 0 8px}.specimen-center p{font-size:13px;line-height:1.5;color:var(--muted);max-width:38ch;margin:0 auto}.specimen-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--edge)}.specimen-step{padding:18px 16px;min-width:0;border-right:1px solid var(--edge)}.specimen-step:last-child{border-right:0}.specimen-step b{display:block;font:800 12px var(--mono);color:var(--accent);margin-bottom:5px}.specimen-step span{font-size:12px;color:var(--ink);line-height:1.4;display:block;overflow-wrap:anywhere}
.keypoints{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}.point{border:1px solid var(--edge);background:var(--panel);padding:26px 25px;border-radius:var(--radius);min-width:0}.point .n{font:800 10px var(--mono);letter-spacing:.14em;color:var(--accent);text-transform:uppercase}.point h3{font-size:20px;letter-spacing:-.025em;line-height:1.25;margin:12px 0 8px}.point p{font-size:14px;color:var(--muted);margin:0;line-height:1.55}
.section{padding:90px 0 0;scroll-margin-top:30px}.sectionhead{display:flex;justify-content:space-between;align-items:end;gap:30px;margin-bottom:26px}.sectionhead h2{font-size:clamp(29px,4vw,48px);letter-spacing:-.05em;line-height:1.13;margin:12px 0 0;max-width:18ch}.sectionhead p{max-width:49ch;color:var(--muted);margin:0;font-size:15px}.journeybox{border:1px solid var(--edge);background:var(--panel);border-radius:var(--radius);padding:30px}.journey-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:22px}.journey-head .hint{font:11px var(--mono);color:var(--soft)}
.sequence{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(var(--stage-count),minmax(0,1fr));gap:31px}.sequence>li{position:relative;min-width:0}.sequence>li:not(:last-child)::after{content:'→';position:absolute;top:44%;right:-28px;font-size:24px;font-weight:850;color:var(--accent);line-height:1;pointer-events:none}.stage{display:block;width:100%;height:100%;min-height:195px;text-align:left;padding:24px 20px;background:var(--bg);border:1px solid var(--edge);border-radius:13px;color:var(--ink);cursor:pointer;transition:border-color .15s,transform .15s,box-shadow .15s;overflow-wrap:anywhere}.stage:hover{border-color:var(--accent);transform:translateY(-2px)}.stage[aria-pressed="true"]{border:2px solid var(--accent);background:var(--panel2);box-shadow:0 0 0 3px #ffffff06}.stage .idx{display:grid;place-items:center;width:32px;height:32px;border:1px solid var(--edge);border-radius:9px;font:800 12px var(--mono);color:var(--accent);margin-bottom:21px}.stage b{display:block;font-size:16px;line-height:1.25;margin-bottom:9px}.stage .summary{display:block;color:var(--muted);font-size:12px;line-height:1.5}
.diversions{display:grid;gap:10px;margin-top:22px}.diversion{border:1px dashed var(--edge);padding:12px 15px;border-radius:10px;display:flex;align-items:center;gap:9px;flex-wrap:wrap;color:var(--muted);font:12px/1.55 var(--mono)}.diversion strong{color:var(--accent);font-weight:700}.diversion .flow-label{font:750 10px var(--mono);letter-spacing:.08em;color:var(--soft);text-transform:uppercase}.text-node{padding:3px 9px;border:1px solid var(--edge);background:var(--bg);border-radius:7px;font:750 11px var(--mono);cursor:pointer;color:var(--ink)}.text-node:hover{border-color:var(--accent)}.passive-node{display:inline-block;padding:3px 9px;border:1px solid var(--edge);background:var(--bg);border-radius:7px;color:var(--ink)}.route-arrow{color:var(--accent);font-size:17px}
.detail-area{display:grid;grid-template-columns:minmax(0,1fr) minmax(225px,.45fr);gap:22px;margin-top:24px;padding-top:22px;border-top:1px solid var(--edge)}.inspector{min-width:0}.inspector-label{font:750 10px var(--mono);color:var(--accent);text-transform:uppercase;letter-spacing:.13em}.inspector h3{margin:10px 0 8px;font-size:25px;letter-spacing:-.035em}.inspector p{margin:0 0 8px;color:var(--muted);font-size:14px;line-height:1.6}.inspector .detail{color:var(--ink)}.destinations{border-left:1px solid var(--edge);padding-left:22px;min-width:0}.destinations h4{margin:0 0 12px;font:750 10px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--soft)}.destinations .empty{color:var(--muted);font-size:13px}.destination{display:block;width:100%;text-align:left;border:1px solid var(--edge);border-radius:9px;background:var(--bg);color:var(--ink);padding:10px 12px;cursor:pointer;margin-bottom:9px;line-height:1.3}.destination strong{display:block;font-size:12px}.destination small{display:block;font-size:11px;color:var(--muted);margin-top:4px}.destination:hover{border-color:var(--accent)}
.chapters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px;margin-top:24px}.chapter{border:1px solid var(--edge);border-radius:var(--radius);padding:28px 28px 25px;background:var(--panel);min-width:0}.chapter .chapter-number{font:750 10px var(--mono);color:var(--accent);text-transform:uppercase;letter-spacing:.13em}.chapter h3{font-size:23px;letter-spacing:-.032em;line-height:1.2;margin:12px 0}.chapter p{font-size:14px;color:var(--muted);margin-bottom:16px}.chapter ul{padding-left:20px;margin:0;color:var(--ink);font-size:13px;line-height:1.75}.chapter li{padding-left:4px}.chapter li+li{margin-top:5px}
.source-list{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}.source-link{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--edge);background:var(--panel);border-radius:10px;padding:11px 13px;font-size:13px;text-decoration:none}.source-link:hover{border-color:var(--accent)}.source-note{font-size:12px;color:var(--soft);margin-top:15px}.footer{margin-top:100px;padding:35px 0 55px;border-top:1px solid var(--edge);font:11px/1.7 var(--mono);color:var(--soft);display:flex;gap:20px;justify-content:space-between;flex-wrap:wrap}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:1180px){.hero{grid-template-columns:1fr;gap:40px;padding:56px 0}.specimen{max-width:570px}.sequence{grid-template-columns:1fr;gap:29px}.sequence>li:not(:last-child)::after,.sequence>li:nth-child(odd):not(:last-child)::after{content:'↓';top:auto;bottom:-27px;left:calc(50% - 9px);right:auto}.stage{min-height:130px}.section{padding-top:70px}}
@media(max-width:700px){.shell{width:min(100% - 32px,var(--shell))}.topbar{padding:15px 0}.topnote{font-size:9px}.hero{padding:42px 0 50px}.hero h1{font-size:clamp(40px,11.5vw,64px)}.keypoints{grid-template-columns:1fr}.point{padding:23px}.sectionhead{display:block}.sectionhead p{margin-top:14px}.journeybox{padding:19px 15px}.journey-head{align-items:start;flex-wrap:wrap}.sequence{grid-template-columns:1fr;gap:30px}.sequence>li:not(:last-child)::after,.sequence>li:nth-child(odd):not(:last-child)::after{content:'↓';top:auto;bottom:-27px;left:calc(50% - 9px);right:auto}.stage{min-height:0;padding:18px;display:grid;grid-template-columns:36px 1fr;column-gap:12px}.stage .idx{grid-row:span 2;margin:0}.stage b{align-self:end;margin:0 0 3px}.stage .summary{align-self:start}.detail-area{grid-template-columns:1fr}.destinations{border-left:0;border-top:1px solid var(--edge);padding:18px 0 0}.chapters{grid-template-columns:1fr}.chapter{padding:23px}.specimen-steps{gap:0}.specimen-step{padding:13px 12px}}
@media(max-width:360px){.hero h1{font-size:40px}.specimen-center{padding:25px 18px}.orbit{width:112px;height:112px}.specimen-step{padding:12px 8px}.specimen-step span{font-size:11px}.sequence{gap:29px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.button,.stage{transition:none!important}.button:hover,.stage:hover{transform:none!important}}
@media print{body{background:white;color:black}.hero,.section{padding-top:24px}.button{display:none}.journeybox,.specimen,.stage,.point,.chapter{box-shadow:none!important;break-inside:avoid}.footer{margin-top:30px}}
'''

DARK_CSS = r'''
:root{--bg:#0a1119;--panel:#13202e;--panel2:#1b3041;--edge:#2b3e4d;--ink:#f4f7fb;--muted:#a1b3c4;--soft:#7f97aa;--accent:#80c7ef;--accentInk:#072033;--good:#86d9ba;--radius:17px;color-scheme:dark}
body{background:radial-gradient(ellipse 950px 520px at 84% 0,#1f426044,transparent 67%),linear-gradient(180deg,#090f16,#101925);background-attachment:fixed}.hero h1{background:linear-gradient(140deg,#fff 0%,#dceaf5 65%,#8cc9eb);background-clip:text;color:transparent}.specimen-center{background:radial-gradient(ellipse 280px 200px at 50% 50%,#2b546b33,transparent 75%)}.point:first-child{background:linear-gradient(145deg,#1b3748,var(--panel))}.stage[aria-pressed="true"] .idx{background:var(--accent);color:#061d2b}.footer{letter-spacing:.02em}
'''

MORRITO_CSS = r'''
:root{--bg:#eaf6fd;--panel:#fffdf4;--panel2:#fff0aa;--edge:#191919;--ink:#173452;--muted:#344757;--soft:#536c81;--accent:#1262c7;--accentInk:#191919;--good:#248b42;--warn:#f1a83f;--radius:13px;--sans:"Arial Rounded MT Bold","Trebuchet MS",system-ui,sans-serif;color-scheme:light}
body{font-weight:550;background-color:#eaf6fd;background-image:linear-gradient(#2480aa12 1px,transparent 1px),linear-gradient(90deg,#2480aa12 1px,transparent 1px);background-size:28px 28px}.topbar{background:#2d91ed;color:#fff;border:3px solid #191919;border-top:0;border-radius:0 0 10px 10px;padding:13px 17px;box-shadow:5px 5px #191919}.brand,.topnote{color:#fff}.mark{background:#ffcf2c;color:#191919;border:3px solid #191919;border-radius:5px;box-shadow:3px 3px #191919}.eyebrow,.overline{color:#155eb8;font-weight:900}.hero{padding-top:60px}.hero h1{color:#153454;font-weight:950;letter-spacing:-.055em;text-shadow:2px 3px #b6d9f2}.lede{color:#2e4554;font-weight:650}.button{border:3px solid #191919;background:#fffdf4;color:#191919;border-radius:7px;box-shadow:3px 3px #191919;font-weight:900}.button.primary{background:#ffcf2c;color:#191919;border:3px solid #191919}.button:active{transform:translate(2px,2px);box-shadow:1px 1px #191919}.specimen,.point,.journeybox,.chapter{border:4px solid #191919;box-shadow:7px 7px #191919;background:#fffdf4}.specimen{background:#fffdf4}.specimen-bar{border-bottom:3px solid #191919;background:#2d91ed;color:#fff}.specimen-badge{color:#191919;background:#ffcf2c;border:2px solid #191919;border-radius:6px}.orbit{border:4px solid #191919;box-shadow:0 0 0 12px #ffe69d,0 0 0 15px #191919;background:#dff5b7}.orbit svg{stroke:#248b42}.specimen-kicker{color:#1262c7}.specimen-steps{border-top:4px solid #191919;background:#e8f5ff}.specimen-step{border-right:3px solid #191919}.specimen-step b{color:#1262c7}.point h3,.sectionhead h2,.chapter h3{font-weight:900}.point .n{color:#1262c7}.sectionhead p{color:#364653}.journeybox{background:#f5fbff}.journey-head .hint{color:#3e5565}.stage{border:3px solid #191919;border-radius:8px;background:#fffdf4;color:#21394b;box-shadow:4px 4px #191919}.stage[aria-pressed="true"]{background:#ffed9d;border:3px solid #1262c7;box-shadow:4px 4px #191919}.stage .idx{background:#ffcf2c;border:2px solid #191919;color:#191919;border-radius:5px}.stage .summary{color:#344757}.sequence>li:not(:last-child)::after{color:#248b42;font-weight:1000}.diversion{border:3px dashed #191919;background:#fff6cf;color:#253f4f}.text-node,.passive-node,.destination{border:2px solid #191919;border-radius:5px;background:#fffdf4;color:#191919;box-shadow:2px 2px #191919}.route-arrow{color:#248b42}.inspector-label{color:#1262c7}.inspector p{color:#334758}.inspector .detail{color:#1b3344}.destinations{border-color:#191919}.destinations h4{color:#506174}.chapter{background:#fffdf4}.chapter p{color:#344757}.source-link{border:3px solid #191919;border-radius:7px;box-shadow:3px 3px #191919;background:#fffdf4}.theme-star{display:inline-block;margin-right:7px;font-size:22px;color:#ffcf2c;-webkit-text-stroke:1px #191919;text-shadow:2px 2px #191919;vertical-align:-2px}.hero-note{color:#394e5b;font-weight:700}
@media(max-width:700px){.topbar{border-radius:0 0 6px 6px;padding:11px}.specimen,.point,.journeybox,.chapter{box-shadow:4px 4px #191919}}
@media print{.topbar{color:#191919;background:white}.brand,.topnote{color:#191919}.specimen,.point,.journeybox,.chapter,.stage{box-shadow:none}}
'''

GILDED_CSS = r'''
:root{--bg:#e5dcc4;--panel:#d9d1b9;--panel2:#eee4c8;--edge:#827d68;--ink:#292d29;--muted:#454b41;--soft:#626858;--accent:#664d22;--accentInk:#f7e6aa;--good:#4c6347;--warn:#997331;--radius:3px;--sans:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;color-scheme:light}
body{background-color:#e5dcc4;background-image:radial-gradient(ellipse at 50% 9%,#fff8e5 0,transparent 70%),repeating-linear-gradient(0deg,#564e3107 0,#564e3107 1px,transparent 1px,transparent 4px)}.topbar{margin-top:12px;background:linear-gradient(#282039,#0e1020);padding:12px 22px;border:2px solid #8c806f;box-shadow:inset 1px 1px #74697c,inset -1px -1px #090916}.brand{font-family:var(--serif);color:#f1dfaa;letter-spacing:.11em;text-transform:uppercase;font-size:14px}.topnote{color:#e2d2a7}.mark{background:linear-gradient(#423454,#1a1524);border:1px solid #d4c48b;color:#f7e1a1;border-radius:1px;box-shadow:inset 1px 1px #a393bd}.hero{padding:65px 0 52px;gap:45px}.eyebrow,.overline{font-family:var(--serif);letter-spacing:.2em;color:#65532e;font-weight:800}.hero h1{font:700 clamp(46px,6.4vw,80px)/1.08 var(--serif);letter-spacing:.016em;text-transform:uppercase;color:#363b30;text-shadow:0 1px #fff8e6;margin-top:22px}.lede{font-family:var(--serif);font-size:clamp(17px,1.7vw,21px);line-height:1.65;color:#42473d}.button{border:2px solid #9b907a;border-radius:2px;background:linear-gradient(#4a385b,#241a32);color:#f8e6a9;box-shadow:inset 1px 1px #8d78a1,inset -1px -1px #120c17,1px 2px #332c2860;font-family:var(--serif);font-weight:800;letter-spacing:.03em}.button.primary{background:linear-gradient(#4b395e,#261b34);color:#ffe7a6;border-color:#98835b}.button:hover{background:linear-gradient(#604b74,#352640)}.specimen,.point,.journeybox,.chapter{border:1px solid #6b715d;border-radius:3px;background:linear-gradient(130deg,#dfdac6,#cfcab5);box-shadow:inset 1px 1px #fff7df,inset -1px -1px #a49e87,2px 3px #4d43384b}.specimen-bar{background:linear-gradient(#d4cfbd,#bbbda8);color:#3e443d;border-bottom:1px solid #7b7e70;font-family:var(--serif)}.specimen-badge{color:#ffe4a3;background:#281d37;border:1px solid #726c60;border-radius:1px}.specimen-center{padding:29px 22px}.orbit{border:2px solid #7b775c;background:radial-gradient(circle,#faf0d2,#c4bda1);box-shadow:0 0 0 12px #b8aa7d39,0 0 0 13px #8d855c60}.orbit svg{stroke:#5b653f}.specimen-kicker{color:#74572a;font-family:var(--serif)}.specimen-center h2,.sectionhead h2,.point h3,.chapter h3{font-family:var(--serif);letter-spacing:0}.specimen-steps{border-top:1px solid #8b8974;background:linear-gradient(#dad5c2,#c7c5af)}.specimen-step{border-right:1px solid #8b8974}.specimen-step b{color:#725628}.specimen-center p{color:#41483c}.point .n{font-family:var(--serif);color:#775b2a}.sectionhead h2{font-size:clamp(34px,4vw,48px);font-weight:700}.sectionhead p{color:#4a4e43}.journeybox{background:linear-gradient(#d7d4bf,#c7c9b1)}.journey-head .hint{color:#606953}.stage{border:1px solid #7f856e;border-radius:2px;background:linear-gradient(#ede9d6,#d7d7c1);color:#2b3129;box-shadow:inset 1px 1px #fffdf0,inset -1px -1px #aaa995,1px 2px #514e4238}.stage[aria-pressed="true"]{border:2px solid #69502b;background:linear-gradient(#fff4c9,#e5dbb0);box-shadow:inset 1px 1px #fff9df,2px 3px #514e4238}.stage .idx{border:1px solid #8f815b;border-radius:1px;background:#312741;color:#f1d68e;font-family:var(--serif)}.stage b{font-family:var(--serif);font-size:18px}.stage .summary{color:#505749}.sequence>li:not(:last-child)::after{color:#705b35}.diversion{background:#e9e2c9;border:1px dashed #837960;color:#3e4839}.text-node,.passive-node,.destination{border:1px solid #8f907b;border-radius:1px;background:#ede8d3;color:#2a302b}.route-arrow{color:#77592d}.inspector-label{font-family:var(--serif);color:#6b532e}.inspector h3{font-family:var(--serif)}.inspector p{color:#3c433a}.inspector .detail{color:#262c27}.destinations{border-color:#7b7d6a}.destinations h4{color:#525b4a;font-family:var(--serif)}.chapter p{color:#41483f}.source-link{border:1px solid #807e6a;background:linear-gradient(#e4dfc8,#cecab2);border-radius:2px;box-shadow:inset 1px 1px #fff7e7}.footer{border-top:2px double #8c7954;color:#59604e;font-family:var(--serif);letter-spacing:.05em}.hero-note{color:#60654e;font-family:var(--serif)}@media(max-width:360px){.hero h1{font-size:36px;overflow-wrap:anywhere;letter-spacing:-.01em}}.theme-star{display:inline-block;margin-right:8px;color:#a9823e;font-size:21px}
@media print{.topbar{background:white}.brand,.topnote{color:#2a2b25}.button{color:#333;background:white}.specimen,.point,.journeybox,.chapter{box-shadow:none}}
'''

SYMBOL_SVGS = {
    'spark': '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M48 10 57 39 86 48 57 57 48 86 39 57 10 48 39 39Z"/><path d="M14 14v13m-7-6h14M79 72v16m-8-8h16"/></svg>',
    'burrito': '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M30 20c12-7 28-7 40 2l10 8-28 45-34-17c-6-4-8-10-5-16Z"/><path d="M30 20c8 3 15 8 20 15l-29 26c-6-3-9-7-10-13M70 22c-5 15-12 28-20 41M39 24l26 22M29 31l24 21"/><path d="M21 13 12 7M81 65l9 8M76 10l6-8"/></svg>',
    'leaf': '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M24 70c-4-28 10-47 51-52 2 31-15 56-43 57-3 0-6-2-8-5Z"/><path d="M23 80c13-22 27-35 45-47"/><path d="M46 55c-2-8-4-13-5-19M49 52c7 1 14 2 19 3"/></svg>',
    'compass': '<svg viewBox="0 0 96 96" aria-hidden="true"><circle cx="48" cy="48" r="32"/><path d="m60 35-8 17-17 8 8-17Z"/><path d="M48 8v7M48 81v7M8 48h7M81 48h7"/></svg>',
}

MARK_SVG = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" aria-hidden="true"><path d="M12 21V10M12 16c-6 0-8-3-8-8 6 0 8 2 8 8ZM12 12c0-5 3-8 8-9 1 6-1 9-8 9Z"/></svg>'''


# Local theme assets are embedded into the output file: no network dependency.
ASSET_ROOT = Path(__file__).resolve().parents[1] / 'assets'


def inline_asset(name: str) -> str:
    if name not in ('morrito-star.svg','morrito-scene.svg','gilded-sword.svg',
                    'gilded-wand.svg','gilded-bird.svg', 'morrito-question-block.svg',
                    'gilded-curious-bird.svg'):
        raise ValueError('Unknown decorative asset')
    return (ASSET_ROOT / name).read_text(encoding='utf-8')


def title_html(value: str) -> str:
    # Split presentation spans only. The visible and accessible wording is unchanged.
    first, sep, last = value.rpartition(' ')
    if sep:
        return html(first + sep) + '<span class="title-emphasis">' + html(last) + '</span>'
    return '<span class="title-emphasis">' + html(value) + '</span>'


def pipe_html(variant: str, cls: str = 'route-pipe') -> str:
    if variant not in ('green','orange','red','blue'):
        variant = 'blue'
    # Three-dimensional tube, embossed lip and a translucent glint.
    return (f'<span class="{cls} pipe-{variant}" aria-hidden="true">'
            '<svg viewBox="0 0 78 30" focusable="false">'
            '<rect class="tube" x="6" y="7" width="66" height="16" rx="2"/>'
            '<path class="shine" d="M10 11H68"/>'
            '<rect class="collar collar-left" x="2" y="3" width="11" height="24" rx="2"/>'
            '<rect class="collar collar-right" x="65" y="3" width="11" height="24" rx="2"/>'
            '<path class="collar-glint" d="M5 6v15M68 6v15"/>'
            '</svg></span>')


def route_variant(target: str) -> str:
    # Decorative channel only. The *edge label* remains the authority.
    return 'orange' if target.lower() in ('pause','retry','wait') else 'red' if target.lower() in ('stop','failed','fail','abort') else 'green' if target.lower() in ('complete','completed','success','done') else 'blue'


def highlight_html(items: list[dict]) -> str:
    return '\n'.join(
        f'<article class="point"><div class="n">{html(e["eyebrow"])}</div>'
        f'<h3>{html(e["title"])}</h3><p>{html(e["description"])}</p></article>' for e in items
    )


def callouts_html(items: list[dict], style: str) -> str:
    if not items:
        return ''
    parts = []
    for c in items:
        kind = c['kind']
        if kind == 'important':
            ico = inline_asset('morrito-star.svg') if style == 'morrito' else inline_asset('gilded-sword.svg') if style == 'gilded' else '✦'
        else:
            # Curiosity has its own illustrated block / bird; it is not an error state.
            ico = (inline_asset('morrito-question-block.svg') if style == 'morrito' else
                   gilded_curiosity_markup() if style == 'gilded' else '?')
        parts.append(f'<article class="story-callout {kind}"><div class="callout-symbol" aria-hidden="true">{ico}</div>'
                     f'<div><div class="callout-kicker">{html(kind)}</div><h3>{html(c["title"])}</h3>'
                     f'<p>{html(c["text"])}</p></div></article>')
    return '<section class="story-callouts shell-less" aria-label="Context notes">' + ''.join(parts) + '</section>'


def presenter_bird_path() -> Optional[Path]:
    """Find the original Presenter PNG. Prefer bundled assets, then installed skills.

    This never makes a network call. A separate explicit one-time importer can
    place the original PNG in assets/ when the Presenter skill is not installed.
    """
    import os

    skill = ASSET_ROOT.parent
    # An explicit project/user override wins over a cached or bundled original.
    override = os.environ.get('STORYCRAFT_PRESENTER_BIRD')
    roots = [Path(override).expanduser()] if override else []
    roots.append(ASSET_ROOT / 'gilded-bird.png')
    skills = ('driftmap-presenter', 'presenter-driftmap')
    parents = (skill.parent, Path.cwd(), Path.cwd() / 'agent-skills',
               Path.cwd() / '.agents' / 'skills', Path.cwd() / '.claude' / 'skills',
               Path.cwd() / '.omp' / 'skills',
               Path.home() / '.agents' / 'skills',
               Path.home() / '.claude' / 'skills',
               Path.home() / '.omp' / 'skills')
    winhome = os.environ.get('USERPROFILE')
    if winhome:
        parents += tuple(Path(winhome) / d / 'skills' for d in ('.agents', '.claude', '.omp'))
    for parent in parents:
        for name in skills:
            roots.append(parent / name / 'assets' / 'gilded-bird.png')
    for path in roots:
        if path.is_file():
            raw = path.read_bytes()
            if raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw) <= 4_000_000:
                return path
    return None


def gilded_bird_markup() -> str:
    """Embed the Presenter mascot when available, or use bundled SVG fallback."""
    path = presenter_bird_path()
    if path:
        raw = path.read_bytes()
        return ('<img class="riding-bird" src="data:image/png;base64,' +
                base64.b64encode(raw).decode('ascii') + '" alt="" aria-hidden="true">')
    return inline_asset('gilded-bird.svg').replace('<svg ', '<svg class="riding-bird" ', 1)


def gilded_curiosity_markup() -> str:
    """The SAME bird as the hero, scaled small, with a separate '?' medallion."""
    return ('<span class="bird-curiosity">' + gilded_bird_markup() +
            '<span class="bird-curiosity-question" aria-hidden="true">?</span></span>')


def specimen_html(model: dict, style: str) -> str:
    hits = model.get('highlights', [])[:3]
    contents = '\n'.join(f'<div class="specimen-step"><b>{i+1:02d}</b><span>{html(h["title"])}</span></div>' for i, h in enumerate(hits))
    if not hits:
        contents = '<div class="specimen-step"><b>01</b><span>Discover</span></div><div class="specimen-step"><b>02</b><span>Understand</span></div><div class="specimen-step"><b>03</b><span>Explore</span></div>'
    symbol = SYMBOL_SVGS[model.get('hero_symbol','spark')]
    if style == 'gilded':
        symbol = gilded_bird_markup()
    corner_star = '<span class="specimen-corner-star" aria-hidden="true">' + inline_asset('morrito-star.svg') + '</span>' if style == 'morrito' else ''
    return (f'<aside class="specimen" aria-label="Concept snapshot">'
            f'<div class="specimen-bar"><span>{html(model.get("hero_label", "Concept preview"))}</span>'
            f'<span class="specimen-badge">{html(model.get("badge","Concept"))}</span></div>'
            f'<div class="specimen-center">{corner_star}<div class="orbit">{symbol}</div>'
            f'<div class="specimen-kicker">The story at a glance</div><h2>{html(model.get("panel_title","A closer look"))}</h2>'
            f'<p>{html(model.get("panel_body",model["summary"]))}</p></div>'
            f'<div class="specimen-steps">{contents}</div></aside>')


def flow_html(model: dict, style: str) -> str:
    flow = model.get('flow')
    if not flow:
        return ''
    nodes = {n['id']: n for n in flow['nodes']}
    primary = flow['primary_path']
    edges = flow['edges']
    primary_pairs = set(zip(primary,primary[1:]))
    stage_markup = '\n'.join(
      f'<li><button class="stage" type="button" data-node-id="{html(nid)}" aria-pressed="{"true" if i == 0 else "false"}">'
      f'<span class="idx">{i+1:02d}</span><b>{html(nodes[nid]["title"])}</b>'
      f'<span class="summary">{html(nodes[nid]["summary"])}</span></button>'
      f'{pipe_html("green", "pipe-connector") if style == "morrito" and i < len(primary)-1 else ""}</li>'
      for i,nid in enumerate(primary)
    )
    alternatives = [e for e in edges if (e['from'],e['to']) not in primary_pairs]
    extra = []
    for e in alternatives:
        variant = route_variant(e['to'])
        cls = 'paused' if variant == 'orange' else 'stopped' if variant == 'red' else 'other'
        pipe1 = pipe_html(variant) if style == 'morrito' else '<span class="route-arrow" aria-hidden="true">→</span>'
        pipe2 = pipe_html(variant) if style == 'morrito' else '<span class="route-arrow" aria-hidden="true">→</span>'
        extra.append(f'<div class="diversion {cls}"><span class="flow-label">Declared route</span>'
                     f'<div class="route-components"><button type="button" class="text-node" data-node-id="{html(e["from"])}">{html(nodes[e["from"]]["title"])}</button>'
                     f'{pipe1}<strong>{html(e["label"])}</strong>{pipe2}'
                     f'<button type="button" class="text-node" data-node-id="{html(e["to"])}">{html(nodes[e["to"]]["title"])}</button></div></div>')
    extra_markup = ''.join(extra)
    ornament = '<span class="section-ornament" aria-hidden="true">'+inline_asset('gilded-sword.svg')+'</span>' if style == 'gilded' else ''
    wand = '<span class="wand-mark" aria-hidden="true">'+inline_asset('gilded-wand.svg')+'</span>' if style == 'gilded' else ''
    first=nodes[primary[0]]
    initial_dest=''.join(f'<button type="button" class="destination" data-node-id="{html(e["to"])}"><strong>{html(nodes[e["to"]]["title"])}</strong><small>{html(e["label"])}</small></button>' for e in edges if e['from'] == primary[0]) or '<p class="empty">No next stages.</p>'
    return (f'<section class="section" id="journey" aria-labelledby="journey-title"><div class="sectionhead">'
            f'<div><div class="overline">Explore · interactive story</div><h2 id="journey-title">{ornament}{html(flow["title"])}</h2></div><p>{html(flow["description"])}</p></div>'
            f'<div class="journeybox"><div class="journey-head"><span class="hint">Select a stage to inspect its details · primary route shown in order</span>'
            f'<button class="button" type="button" id="replay"><span aria-hidden="true">▶</span> Replay the primary route</button></div>'
            f'<ol class="sequence{" long" if len(primary)>5 else ""}" style="--stage-count:{len(primary)}">{stage_markup}</ol>'
            f'{f"<div class=\"diversions\" aria-label=\"Additional declared routes\">{extra_markup}</div>" if extra else ""}'
            f'<div class="detail-area"><div class="inspector"><div class="inspector-label">{wand}Stage inspector · presentation only</div>'
            f'<h3 id="detail-title">{html(first["title"])}</h3><p id="detail-summary">{html(first["summary"])}</p>'
            f'<p class="detail" id="detail-body">{html(first["detail"])}</p></div>'
            f'<div class="destinations"><h4>Possible next stages</h4><div id="destinations">{initial_dest}</div></div></div>'
            f'<p class="sr-only" id="interaction-status" aria-live="polite"></p></div></section>')


def chapters_html(model: dict) -> str:
    chapters=model.get('chapters',[])
    if not chapters:return ''
    pieces=[]
    for i,ch in enumerate(chapters):
        points=''.join(f'<li>{html(p)}</li>' for p in ch.get('points',[]))
        pieces.append(f'<article class="chapter"><div class="chapter-number">{html(ch["eyebrow"])} · {i+1:02d}</div><h3>{html(ch["title"])}</h3><p>{html(ch["body"])}</p>{f"<ul>{points}</ul>" if points else ""}</article>')
    return ('<section class="section" id="chapters"><div class="sectionhead"><div><div class="overline">Further reading</div>'
            '<h2>The details behind the idea</h2></div><p>Short chapters make the story useful beyond the opening headline.</p></div>'
            f'<div class="chapters">{"".join(pieces)}</div></section>')


def sources_html(model: dict) -> str:
    sources=model.get('sources',[])
    if not sources:return ''
    markup=''.join(f'<a class="source-link" href="{html(x["url"])}" target="_blank" rel="noopener noreferrer">{html(x["label"])} <span aria-hidden="true">↗</span></a>' for x in sources)
    return f'<section class="section" id="sources"><div class="overline">Further resources · provided links</div><h2>Continue exploring</h2><div class="source-list">{markup}</div></section>'


JS = r'''
(()=>{'use strict';
 const data=JSON.parse(document.getElementById('story-data').textContent);
 if(!data.flow)return;
 const flow=data.flow,nodes=Object.fromEntries(flow.nodes.map(n=>[n.id,n]));
 const stages=[...document.querySelectorAll('.stage')];
 const dest=document.getElementById('destinations');
 const heading=document.getElementById('detail-title');
 const summary=document.getElementById('detail-summary');
 const body=document.getElementById('detail-body');
 const status=document.getElementById('interaction-status');
 const replay=document.getElementById('replay');
 let active=flow.primary_path[0],busy=false;
 function select(id){
   if(!nodes[id])return;
   active=id;const n=nodes[id];
   heading.textContent=n.title;summary.textContent=n.summary;body.textContent=n.detail;
   stages.forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.nodeId===id)));
   dest.replaceChildren();
   const outgoing=flow.edges.filter(e=>e.from===id);
   if(!outgoing.length){const p=document.createElement('p');p.className='empty';p.textContent='This route ends here.';dest.append(p)}
   outgoing.forEach(edge=>{
      const b=document.createElement('button');b.type='button';b.className='destination';b.dataset.nodeId=edge.to;
      const strong=document.createElement('strong');strong.textContent=nodes[edge.to].title;
      const small=document.createElement('small');small.textContent=edge.label;
      b.append(strong,small);b.addEventListener('click',()=>select(edge.to));dest.append(b);
   });
   status.textContent='Selected '+n.title+'. '+outgoing.length+' possible next stage'+(outgoing.length===1?'':'s')+'.';
 }
 document.querySelectorAll('[data-node-id]').forEach(el=>{
   if(!el.closest('#destinations'))el.addEventListener('click',()=>{if(!busy)select(el.dataset.nodeId)});
 });
 replay?.addEventListener('click',async()=>{
   if(busy)return;busy=true;replay.disabled=true;
   const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
   const delay=reduce?70:480;
   for(const id of flow.primary_path){select(id);await new Promise(resolve=>setTimeout(resolve,delay))}
   replay.disabled=false;busy=false;
   status.textContent='Primary route preview finished. No real-world action was performed.';
 });
})();
'''


def render_story(model: dict, style: str) -> str:
    validate_story(model)
    if style not in STYLES:
        raise ValueError(f'Unknown style {style!r}')
    theme = {'dark':DARK_CSS,'morrito':MORRITO_CSS,'gilded':GILDED_CSS}[style] + '\n' + (ASSET_ROOT / (style+'-presenter.css')).read_text(encoding='utf-8')
    shared_css = (ASSET_ROOT / 'common-story.css').read_text(encoding='utf-8')
    path_anchor = '#journey' if model.get('flow') else '#chapters' if model.get('chapters') else '#top'
    points = highlight_html(model.get('highlights', []))
    callouts = callouts_html(model.get('callouts', []), style)
    flow_data = json.dumps({'flow': model.get('flow')},ensure_ascii=False,separators=(',',':'))
    # Prevent untrusted strings from terminating our JSON script tag.
    flow_data = flow_data.replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    style_title={'dark':'Dark','morrito':'Morrito','gilded':'Gilded'}[style]
    page_title=html(model['title'])
    display_title=title_html(model['title'])
    brand_icon=inline_asset('morrito-star.svg') if style=='morrito' else inline_asset('gilded-sword.svg') if style=='gilded' else MARK_SVG
    hero_note_icon='<span class=\"important-icon\" aria-hidden=\"true\">'+inline_asset('morrito-star.svg')+'</span>' if style=='morrito' else ''
    copy=(f'<span>Storycraft · {html(style_title)} style · presentation only</span>'
          f'<span>{html(model["source_note"])}</span>')
    # Morrito has ONE contiguous illustrated footer. Do not stack a second turf/earth footer.
    if style == 'morrito':
        footer=(f'<footer class="footer morrito-footer">'
                f'<div class="story-scene" aria-hidden="true">{inline_asset("morrito-scene.svg")}</div>'
                f'<div class="footer-copy shell">{copy}</div></footer>')
    else:
        footer=f'<footer class="footer shell">{copy}</footer>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html(model['summary'][:155])}"><meta name="color-scheme" content="{'dark' if style=='dark' else 'light'}"><title>{page_title} · Storycraft</title><style>{BASE_CSS}\n{shared_css}\n{theme}</style></head>
<body class="style-{style}"><div class="shell"><header class="topbar"><a href="#top" class="brand"><span class="mark">{brand_icon}</span><span>STORYCRAFT <span aria-hidden="true">·</span> {html(style_title)}</span></a><span class="topnote">A human-first story</span></header><main id="top"><section class="hero" aria-labelledby="page-title"><div class="hero-copy"><div class="eyebrow">{html(model['eyebrow'])}</div><h1 id="page-title">{display_title}</h1><p class="lede">{html(model['summary'])}</p><div class="actions"><a class="button primary" href="{path_anchor}">Explore the story <span aria-hidden="true">↗</span></a>{'<a class="button" href="#chapters">Read the details</a>' if model.get('chapters') and model.get('flow') else ''}</div><p class="hero-note">{hero_note_icon}{html(model['source_note'])}</p></div>{specimen_html(model,style)}</section>{f'<section class="keypoints" aria-label="Highlights">{points}</section>' if points else ''}{callouts}{flow_html(model,style)}{chapters_html(model)}{sources_html(model)}</main></div>{footer}<script type="application/json" id="story-data">{flow_data}</script><script>{JS}</script></body></html>'''


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('story', type=Path, help='Authored story JSON (see examples)')
    ap.add_argument('--style', choices=STYLE_CHOICES, default='dark', help='One style or all three')
    ap.add_argument('--out', type=Path, help='Output HTML for a single style')
    ap.add_argument('--out-dir', type=Path, help='Destination directory (required when --style all)')
    ap.add_argument('--force', action='store_true', help='Replace existing generated HTML, after inspection')
    args = ap.parse_args()
    try:
        source = args.story.expanduser().resolve()
        if not source.is_file():
            raise ValueError(f'Cannot find source: {source}')
        model = json.loads(source.read_text(encoding='utf-8'))
        validate_story(model)
        if args.style == 'all' and args.out:
            raise ValueError('--out applies to single-style output only; use --out-dir with --style all')
        if args.style == 'all' and not args.out_dir:
            raise ValueError('--style all requires --out-dir')
        selected = STYLES if args.style == 'all' else (args.style,)
        source_name = source.stem.replace('.story', '')
        outputs = []
        for style in selected:
            if args.out:
                dest = args.out.expanduser().resolve()
            elif args.out_dir:
                dest = (args.out_dir / f'{source_name}-{style}.html').expanduser().resolve()
            else:
                dest = source.with_name(f'{source_name}-{style}.html').resolve()
            if dest == source:
                raise ValueError('Output must not overwrite source')
            if dest.exists() and not args.force:
                raise ValueError(f'Output already exists: {dest}; inspect it first, then use --force if intended')
            outputs.append((style, dest, render_story(model, style)))
        for style, dest, result in outputs:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(result, encoding='utf-8')
            print(f'Rendered {style} story: {dest}')
        return 0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
