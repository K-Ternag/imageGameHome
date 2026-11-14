"""Exercise the public website at a real HTTP origin with Chromium."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_site import Site, validate_config, missing_policy_fields

parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:3260/')
args=parser.parse_args()
BASE=args.base_url.rstrip('/')+'/'
ART=ROOT/'artifacts'
ART.mkdir(exist_ok=True)
report={'base_url':BASE,'layout_checks':[],'interactions':[],'errors':[]}


def assert_true(condition, message):
    if not condition: raise AssertionError(message)


try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(reduced_motion='reduce',device_scale_factor=1)
        page=context.new_page()
        page.on('pageerror',lambda error:report['errors'].append(str(error)))
        for width in [1440,768,390,320]:
            page.set_viewport_size({'width':width,'height':900 if width>600 else 844})
            for lang in ['ko','en']:
                suffix='.html' if lang=='ko' else '.en.html'
                for name in ['index','guide','support','privacy','delete-account','terms']:
                    filename=name+suffix
                    response=page.goto(urljoin(BASE,filename),wait_until='networkidle')
                    assert_true(response.status==200,filename+' did not return HTTP 200')
                    assert_true(page.locator('h1').count()==1,filename+' h1 count')
                    overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                    assert_true(not overflow,f'{filename} horizontally overflows at {width}px')
                    assert_true(page.locator('html').get_attribute('lang')==lang,'Incorrect document language')
                    report['layout_checks'].append(f'{filename} {width}px')
                    if width in [1440,390] and name=='index':
                        page.screenshot(path=str(ART/f'home-{lang}-{width}.png'),full_page=True)
                    if width==1440 and name=='privacy' and lang=='ko':
                        page.screenshot(path=str(ART/'privacy-ko-desktop.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        for suffix,lang in [('.html','ko'),('.en.html','en')]:
            page.goto(urljoin(BASE,'guide'+suffix),wait_until='networkidle')
            page.locator('footer').scroll_into_view_if_needed()
            for image in page.locator('.gallery-card img').all():
                image.scroll_into_view_if_needed()
                image.evaluate('(img) => img.decode()')
                assert_true(f'assets/{lang}/' in image.get_attribute('src'),'Wrong image language')
            page.locator('[data-filter="together"]').click()
            assert_true(page.locator('.gallery-card:visible').count()==2,'Gallery filter failed')
            first=page.locator('.gallery-card:visible [data-lightbox]').first
            first.click()
            assert_true(page.locator('#lightbox').is_visible(),'Lightbox did not open')
            assert_true(page.locator('#image-position').inner_text()=='1 / 2','Incorrect filtered image list')
            page.keyboard.press('ArrowRight')
            assert_true(page.locator('#image-position').inner_text()=='2 / 2','Next image failed')
            page.keyboard.press('ArrowLeft')
            assert_true(page.locator('#image-position').inner_text()=='1 / 2','Previous image failed')
            page.keyboard.press('Escape')
            assert_true(not page.locator('#lightbox').is_visible(),'Escape failed')
            assert_true(first.evaluate('(node) => node === document.activeElement'),'Focus not restored')
            page.locator('.languages a[hreflang="'+('en' if lang=='ko' else 'ko')+'"]').click()
            assert_true('filter=together' in page.url,'Language link lost the selected filter')
            assert_true(page.locator('.gallery-card:visible').count()==2,'Translated filter not preserved')
            report['interactions'].append(f'{lang}: eight locale images, filter, lightbox, arrows, Escape, focus, language filter')
        page.goto(urljoin(BASE,'index.html#games'),wait_until='networkidle')
        page.locator('[data-filter="puzzle"]').click()
        assert_true(page.locator('.game-card:visible').count()==2,'Game category filter failed')
        page.locator('.languages a[hreflang="en"]').click()
        assert_true(page.url.endswith('?filter=puzzle#games'),'Language link lost anchor or filter')
        report['interactions'].append('Game filter and language link retain section and query')
        page.set_viewport_size({'width':390,'height':844})
        page.goto(urljoin(BASE,'index.html'),wait_until='networkidle')
        assert_true(not page.locator('#navigation').is_visible(),'Mobile nav should start closed')
        page.locator('.menu-toggle').click()
        assert_true(page.locator('#navigation').is_visible(),'Mobile nav failed to open')
        page.keyboard.press('Escape')
        assert_true(not page.locator('#navigation').is_visible(),'Mobile Escape failed')
        page.locator('.menu-toggle').click()
        page.locator('#navigation a[href="index.html#together"]').click()
        assert_true(not page.locator('#navigation').is_visible(),'Mobile menu did not close after link')
        report['interactions'].append('Mobile menu: toggle, Escape, close after navigation')
        page.goto(urljoin(BASE,'support.html'),wait_until='networkidle')
        page.locator('details').first.locator('summary').click()
        assert_true(page.locator('details').first.get_attribute('open') is not None,'FAQ failed')
        config=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
        if not config['supportEmail']:
            assert_true(page.locator('#support-form button').is_disabled(),'Unknown email must not pretend to send')
        if not config['playStoreUrl']:
            assert_true(page.locator('a[href^="https://play.google.com/"]').count()==0,'Unconfirmed store URL leaked')
        report['interactions'].append('FAQ, pending contact, honest store availability')
        # Test the configured-email branch in a route fixture, without changing production config.
        fixture=dict(config,supportEmail='support@example.com',developerName='Test operator',policyEffectiveDate='2026-11-14',
                     supportRetention={'ko':'처리 완료 후 30일','en':'30 days after resolution'},
                     supportResponseTime={'ko':'7일 이내','en':'Within 7 days'},policiesApproved=True)
        validate_config(fixture)
        assert_true(not missing_policy_fields(fixture),'Completed policy should be ready')
        for lang in ['ko','en']:
            site=Site(lang,fixture)
            fixture_url=urljoin(BASE,'support'+('.html' if lang=='ko' else '.en.html'))+'?fixture=1'
            page.route(fixture_url,lambda route,body=site.render('support'):route.fulfill(status=200,content_type='text/html',body=body))
            page.goto(fixture_url,wait_until='networkidle')
            assert_true(page.locator('#support-form button').is_enabled(),'Configured email still disabled')
            page.locator('#message').fill('문의 & details\nSecond line')
            # Observe the actual handler; the test does not reimplement it.
            navigation_attempts=[]
            session=context.new_cdp_session(page)
            session.send('Page.enable')
            session.on('Page.frameRequestedNavigation',lambda event:navigation_attempts.append(event.get('url','')))
            page.locator('#support-form button').click()
            page.wait_for_function("document.querySelector('#form-status').textContent.includes(document.documentElement.lang === 'en' ? 'Nothing has been submitted' : '접수되지 않았습니다')")
            drafts=[url for url in navigation_attempts if url.startswith('mailto:')]
            assert_true(bool(drafts),'No mail draft navigation was observed')
            assert_true('mailto:support@example.com?subject=' in drafts[-1],'Email recipient failed')
            assert_true('%26' in drafts[-1] and '%0A' in drafts[-1],'Email encoding failed')
            session.detach()
            policy=site.render('privacy')
            assert_true('class="policy-notice"' not in policy,'Ready policy still marked draft')
        report['interactions'].append('Configured-contact fixture: static policy identity, mail draft recipient and encoding')
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        plain=nojs.new_page()
        for suffix in ['.html','.en.html']:
            for name in ['index','privacy','delete-account','terms','support']:
                plain.goto(urljoin(BASE,name+suffix),wait_until='networkidle')
                assert_true(plain.locator('main').inner_text().strip(),'Missing no-JS content')
                assert_true(plain.locator('#navigation').is_visible(),'No-JS navigation unavailable')
                assert_true(not plain.evaluate('document.documentElement.scrollWidth > innerWidth + 1'),'No-JS overflow')
        report['interactions'].append('10 no-JavaScript documents: full content and navigation')
        # A configured form must never GET-submit the message if scripts are off.
        fixture_url=urljoin(BASE,'support.html')+'?nojs-fixture=1'
        plain.route(fixture_url,lambda route:route.fulfill(status=200,content_type='text/html',body=Site('ko',fixture).render('support')))
        plain.goto(fixture_url,wait_until='networkidle')
        assert_true(plain.locator('#support-form button').is_disabled(),'No-JS form could submit to static hosting')
        assert_true(plain.locator('a[href="mailto:support@example.com"]').count()>0,'No-JS direct email missing')
        report['interactions'].append('Configured form with JavaScript off: no server submission, direct email available')
        nojs.close()
        context.close()
        browser.close()
except Exception as error:
    report['errors'].append(str(error))
finally:
    report['passed']=not report['errors']
    (ART/'browser-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'layout_checks':len(report['layout_checks']),'interactions':report['interactions'],'errors':report['errors'],'passed':report['passed']},ensure_ascii=False,indent=2))
    raise SystemExit(not report['passed'])
