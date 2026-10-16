"""Real browser against the built V2 app and disposable local database."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright


def main():
    with tempfile.TemporaryDirectory() as folder:
        env=os.environ.copy();env.update(DATABASE_URL='sqlite:///'+Path(folder,'browser.sqlite3').as_posix(),APP_ENV='local',AUTH_MODE='local',AI_PROVIDER='disabled')
        process=subprocess.Popen([sys.executable,'start.py','--port','8190'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(40):
                try:
                    if urlopen('http://127.0.0.1:8190/health',timeout=2).status==200:break
                except Exception:time.sleep(.5)
            else:raise RuntimeError('App failed readiness check')
            with sync_playwright() as p:
                browser=p.chromium.launch();page=browser.new_page();page.goto('http://127.0.0.1:8190')
                page.get_by_label('Make',exact=True).fill('Browser Demo');page.get_by_label('Model',exact=True).fill('City');page.get_by_label('Price (£)',exact=True).fill('12000');page.get_by_role('button',name='Save vehicle',exact=True).click()
                page.get_by_role('heading',name='Browser Demo City',exact=True).wait_for()
                page.get_by_label('Fictional customer',exact=True).fill('Fictional buyer');page.get_by_label('Message',exact=True).fill('Demo visit');page.get_by_role('button',name='Save enquiry',exact=True).click()
                page.get_by_text('Fictional buyer · stock #1',exact=True).wait_for()
                assert page.get_by_role('button',name='Save follow-up',exact=True).is_enabled()
                page.set_viewport_size({'width':390,'height':844})
                assert page.locator('body').evaluate('(e)=>e.scrollWidth<=window.innerWidth')
                browser.close()
        finally:
            process.terminate();process.wait(timeout=15)
    print('Browser stock/enquiry and narrow-layout checks passed')


if __name__=='__main__':main()
