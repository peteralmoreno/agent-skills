#!/usr/bin/env python3
"""Optional local browser QA for a self-contained Storycraft HTML.

Requires: Python package playwright and Chromium (system browser or playwright install).
Produces full-page screenshots and a machine-readable QA report.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

WIDTHS = [("desktop", 1440, 900), ("tablet", 834, 990), ("mobile", 390, 844), ("narrow", 320, 740)]


def inspect(page):
    return page.evaluate("""() => {
      const W=window.innerWidth;
      const overflow=document.documentElement.scrollWidth-W;
      const clipped=[];
      document.querySelectorAll('.specimen,.point,.journeybox,.chapter,.stage,.source-link,.button,.destination').forEach(el=>{
        const rect=el.getBoundingClientRect();
        if(rect.width && (rect.left < -2 || rect.right > W + 2))
          clipped.push({tag:el.tagName,cls:el.className,left:Math.round(rect.left),right:Math.round(rect.right)});
      });
      const badAnchors=[...document.querySelectorAll('a[href^="#"]')]
        .filter(el=>el.getAttribute('href').length>1 && !document.getElementById(el.getAttribute('href').slice(1)))
        .map(el=>el.getAttribute('href'));
      const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
      const repeatedIDs=ids.filter((x,i)=>ids.indexOf(x)!==i);
      return {width:W,documentWidth:document.documentElement.scrollWidth,overflow,clipped,badAnchors,repeatedIDs};
    }""")


def check(html_file: Path, outdir: Path, browser_executable: str | None):
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    results={"source": str(html_file),"viewports":{},"console_errors":[],"page_errors":[],"runtime_requests":[],"interaction":{}}
    with sync_playwright() as pw:
        opts={"headless":True}
        if browser_executable:
            opts['executable_path']=browser_executable
        browser=pw.chromium.launch(**opts)
        for name,width,height in WIDTHS:
            ctx=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
            page=ctx.new_page()
            page.on('console',lambda msg: results['console_errors'].append(msg.text) if msg.type=='error' else None)
            page.on('pageerror',lambda err: results['page_errors'].append(str(err)))
            page.on('request',lambda req: results['runtime_requests'].append(req.url) if req.url.startswith(('http://','https://')) else None)
            # set_content works in sandboxed environments that block file:// navigation;
            # the generated HTML is self-contained and must not require a filesystem base.
            page.set_content(html_file.read_text(encoding='utf-8'), wait_until='load')
            page.screenshot(path=str(outdir / f'{html_file.stem}-{name}.png'),full_page=True,animations='disabled')
            results['viewports'][name]=inspect(page)
            if name=='desktop':
                if page.locator('#replay').count():
                    page.locator('#replay').click()
                    try:
                        page.wait_for_function("!document.getElementById('replay').disabled",timeout=15000)
                        results['interaction']['replay']='pass'
                    except Exception as e:
                        results['interaction']['replay']=f'fail: {e}'
                alternates=page.locator('.diversions .text-node:last-child')
                if alternates.count():
                    b=alternates.first
                    chosen=b.get_attribute('data-node-id')
                    b.click()
                    selected=page.locator('#detail-title').inner_text()
                    expected=b.inner_text()
                    results['interaction']['alternate']={"node":chosen,"inspector":selected,"pass":selected.strip()==expected.strip()}
                page.screenshot(path=str(outdir / f'{html_file.stem}-selected.png'),full_page=False)
            ctx.close()
        browser.close()
    failed = (bool(results['console_errors'] or results['page_errors'] or results['runtime_requests']) or
              any(r['overflow'] > 2 or r['clipped'] or r['badAnchors'] or r['repeatedIDs'] for r in results['viewports'].values()) or
              any(v == 'fail' or (isinstance(v,str) and v.startswith('fail:')) or (isinstance(v,dict) and not v.get('pass',False)) for v in results['interaction'].values()))
    results['passed'] = not failed
    (outdir / f'{html_file.stem}-qa.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('html',type=Path)
    ap.add_argument('--out-dir',type=Path,default=Path('storycraft-previews'))
    ap.add_argument('--chromium',type=str,help='Path to local Chromium executable if Playwright browsers are not installed')
    a=ap.parse_args()
    file=a.html.expanduser().resolve()
    if not file.exists():
        print(f'Missing HTML: {file}',file=sys.stderr);return 2
    try:
        result=check(file,a.out_dir.expanduser().resolve(),a.chromium)
    except ImportError:
        print('Install Playwright first: python -m pip install playwright; python -m playwright install chromium',file=sys.stderr);return 2
    except Exception as e:
        print(f'Browser QA unavailable: {e}',file=sys.stderr);return 2
    print(json.dumps({"passed":result['passed'],"viewports":result['viewports'],"interaction":result['interaction'],"page_errors":result['page_errors'],"runtime_requests":result['runtime_requests']},indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
