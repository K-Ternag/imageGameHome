"""Generate a portable static website (standard library only).

Edit content.py, this file, and site-config.json; generated HTML is committed for
branch-based GitHub Pages and direct file previews. CI publishes only dist/.
"""
import argparse
import datetime
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse
from content import SCREENS, GAMES, FAQ, PRIVACY, DELETION, TERMS

ROOT = Path(__file__).resolve().parent
PAGES = ['index', 'guide', 'support', 'privacy', 'delete-account', 'terms']
TITLES = {
    'index': ('사진으로 만나는, 여덟 가지 즐거움', 'Little photos. Lots of play.'),
    'guide': ('화면 둘러보기', 'Take a look inside'),
    'support': ('무엇을 도와드릴까요?', 'How can we help?'),
    'privacy': ('개인정보처리방침', 'Privacy policy'),
    'delete-account': ('계정 및 데이터 삭제', 'Account & data deletion'),
    'terms': ('이용약관', 'Terms of use'),
}
DESCRIPTIONS = {
    'index': ('사진 퍼즐부터 순간 기억까지. 8가지 게임, 게임별 100레벨, 한 기기로 함께하는 리멤픽을 만나보세요.', 'Eight photo games, 100 levels each, your own photo packs, and pass-and-play for 2–4 people. Meet RememPic for Android.'),
    'guide': ('리멤픽의 홈, 게임 선택, 퍼즐, 순간 기억, 함께 하기 화면을 둘러보세요.', 'Explore RememPic: home, game selection, puzzles, memory games, and together mode.'),
    'support': ('리멤픽 이용 방법과 자주 묻는 질문, 출시 및 고객지원 안내.', 'Help with RememPic, frequently asked questions, availability, and email support.'),
    'privacy': ('리멤픽의 사진 접근, 기기 내 저장, 공유, 홈페이지 및 문의 정보 처리에 관한 개인정보처리방침.', 'How RememPic handles selected photos, local data, sharing, website visits, and support messages.'),
    'delete-account': ('리멤픽의 개인 사진, 사진팩, 게임 기록 및 모든 앱 데이터 삭제 방법.', 'How to remove personal photos, packs, game records, and all local RememPic data.'),
    'terms': ('리멤픽 앱과 홈페이지의 이용 조건, 사진의 권리, 기록과 공유 안내.', 'Terms for the RememPic app and website, photo rights, local records, and sharing.'),
}


def escape(value):
    return html.escape(str(value), quote=True)


def validate_config(config):
    if config['supportEmail'] and not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', config['supportEmail']):
        raise ValueError('supportEmail must be a plain email address.')
    if config['playStoreUrl'] and not re.fullmatch(r'https://play\.google\.com/store/apps/details\?id=[A-Za-z0-9_.]+', config['playStoreUrl']):
        raise ValueError('playStoreUrl must be the actual Google Play app URL.')
    if config['productionApplicationId'] and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+', config['productionApplicationId']):
        raise ValueError('Invalid productionApplicationId.')
    if config['siteUrl']:
        parsed = urlparse(config['siteUrl'])
        if parsed.scheme != 'https' or not parsed.hostname or parsed.query or parsed.fragment or parsed.username:
            raise ValueError('siteUrl must be a public HTTPS base URL without query or fragment.')
    if config['policyEffectiveDate']:
        datetime.date.fromisoformat(config['policyEffectiveDate'])


def missing_policy_fields(config):
    missing = [key for key in ['developerName', 'supportEmail', 'policyEffectiveDate'] if not config[key].strip()]
    for field in ['supportRetention', 'supportResponseTime']:
        missing.extend(f'{field}.{lang}' for lang in ['ko', 'en'] if not config[field][lang].strip())
    if config['policiesApproved'] is not True:
        missing.append('policiesApproved')
    return missing


class Site:
    def __init__(self, lang, config):
        self.lang, self.config = lang, config
        self.i = 0 if lang == 'ko' else 1
        self.base = config['siteUrl'].rstrip('/') + '/' if config['siteUrl'] else ''

    def t(self, ko, en):
        return ko if self.i == 0 else en

    def f(self, page):
        return page + ('.html' if self.i == 0 else '.en.html')

    def contact(self):
        email = self.config['supportEmail']
        return f'<a class="contact-email" href="mailto:{escape(email)}">{escape(email)}</a>' if email else self.t('<span class="muted">지원 이메일 준비 중</span>', '<span class="muted">Support email coming soon</span>')

    def values(self):
        c = self.config
        return dict(version=escape(c['reviewedAppVersion']), developer=escape(c['developerName'] or self.t('운영자 정보 준비 중', 'Operator details pending')),
                    contact=self.contact(), retention=escape(c['supportRetention'][self.lang] or self.t('문의 기록의 보유 기간과 삭제 절차는 확정 후 안내합니다.', 'The retention period and deletion procedure for support messages are awaiting confirmation.')),
                    response=escape(c['supportResponseTime'][self.lang] or self.t('요청 처리 기한은 확정 후 안내합니다.', 'Response times are awaiting confirmation.')),
                    delete=self.f('delete-account'), support=self.f('support'), privacy=self.f('privacy'))

    def store_button(self):
        url = self.config['playStoreUrl']
        if url:
            return f'<a class="button primary store-link" href="{escape(url)}"><span aria-hidden="true">▶</span> {self.t("Google Play에서 다운로드", "Get it on Google Play")}</a>'
        return f'<a class="button primary" href="{self.f("support")}#availability"><span class="status-dot" aria-hidden="true"></span>{self.t("Google Play 출시 준비 중", "Coming to Google Play")}</a>'

    def image(self, index, eager=False):
        stem, _, title, alt = SCREENS[index]
        loading = 'eager' if eager else 'lazy'
        priority = ' fetchpriority="high"' if eager else ''
        return f'<img src="assets/{self.lang}/screens/{stem}-480.webp" srcset="assets/{self.lang}/screens/{stem}-480.webp 480w, assets/{self.lang}/screens/{stem}-800.webp 800w" sizes="(max-width: 600px) 75vw, 320px" width="1080" height="2400" alt="{escape(alt[self.i])}" loading="{loading}" decoding="async"{priority}>'

    def screen(self, index, css='', eager=False):
        stem, _, title, alt = SCREENS[index]
        return f'<a class="screen-link {css}" href="assets/{self.lang}/originals/{stem}.png" data-lightbox data-title="{escape(title[self.i])}" data-preview="assets/{self.lang}/screens/{stem}-800.webp" aria-label="{escape(title[self.i])} · {self.t("크게 보기", "Enlarge image")}">{self.image(index, eager)}<span class="zoom-hint" aria-hidden="true">↗</span></a>'

    def image_note(self):
        return self.t('현재 한국어 앱의 실제 화면입니다. 문제와 점수는 플레이 예시입니다.', 'Actual screens from the current Korean app. Gameplay and scores are examples. App language support is not implied.')

    def header(self, page):
        links = [(self.f('index')+'#games', self.t('8가지 게임', 'The games')),
                 (self.f('index')+'#together', self.t('함께 하기', 'Play together')),
                 (self.f('guide'), self.t('화면 둘러보기', 'Explore')),
                 (self.f('support'), self.t('고객지원', 'Support'))]
        nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if url == self.f(page) else '')+f'>{label}</a>' for url, label in links)
        langs = ''.join(f'<a href="{page}{suffix}" lang="{lang}" hreflang="{lang}"'+(' aria-current="page"' if lang == self.lang else '')+f'>{label}</a>' for lang, suffix, label in [('ko','.html','한국어'),('en','.en.html','EN')])
        return f'''<a class="skip-link" href="#main">{self.t('본문 바로가기', 'Skip to content')}</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="{self.f('index')}"><img class="brand-icon" src="assets/favicon-64.png" alt="" width="48" height="48"><span>{self.t('리멤픽', 'RememPic')}<small>little photos, lots of play</small></span></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">{self.t('메뉴', 'Menu')} <span aria-hidden="true">☰</span></button>
<nav id="navigation" aria-label="{self.t('주 메뉴', 'Main navigation')}">{nav}<div class="languages" aria-label="Language">{langs}</div></nav></div></header>'''

    def footer(self):
        items = [('privacy', self.t('개인정보처리방침','Privacy policy')), ('delete-account',self.t('데이터 삭제','Data deletion')),('terms',self.t('이용약관','Terms of use')),('support',self.t('고객지원','Support'))]
        links = ''.join(f'<a href="{self.f(key)}">{title}</a>' for key,title in items)
        return f'''<footer class="site-footer"><div class="wrap"><div class="footer-main"><div><a class="footer-brand" href="{self.f('index')}">{self.t('리멤픽', 'RememPic')} <span aria-hidden="true">✦</span></a><p>{self.t('한 장의 사진에서 시작되는, 즐거운 시간.', 'A little photo. A little time. A lot of fun.')}</p></div><nav class="footer-links" aria-label="{self.t('서비스 안내','Service information')}">{links}</nav></div><div class="footer-bottom"><span>© {datetime.date.today().year} {escape(self.config['developerName'] or self.t('리멤픽','RememPic'))}</span><span>{self.t('Android 9 이상 · 나의 사진, 나의 기기에', 'Android 9+ · Your photos stay on your device')}</span></div></div></footer>'''

    def faq(self, count=None):
        return '<div class="faq-list">'+''.join(f'<details><summary>{q[self.i]}<span aria-hidden="true">+</span></summary><p>{a[self.i]}</p></details>' for q,a in FAQ[:count])+'</div>'

    def home(self):
        t = self.t
        cards = ''.join(f'<article class="game-card" data-category="{cat}"><div class="game-top"><span class="game-symbol {cat}" aria-hidden="true">{symbol}</span></div><h3>{title[self.i]}</h3><p>{desc[self.i]}</p><span class="game-level">{t("100개의 작은 도전", "100 little challenges")}</span></article>' for i,(cat,symbol,title,desc) in enumerate(GAMES))
        filters = ''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(i==0).lower()}">{label}</button>' for i,(key,label) in enumerate([('all',t('모두 보기','All games')),('memory',t('기억하기','Remember')),('puzzle',t('맞추기','Piece together')),('observe',t('찾아보기','Look closer'))]))
        stats = [('8',t('서로 다른 게임','different games')),('100',t('게임마다 100레벨','levels per game')),('2–4',t('한 기기로 함께','players, one device')),('180',t('기본 제공 사진','built-in photos'))]
        return f'''
<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow"><span aria-hidden="true">✦</span> {t('사진 한 장, 놀이가 되다','A LITTLE PHOTO. A NEW WAY TO PLAY.')}</span><h1>{t('사진으로 만나는,<br><em>여덟 가지 즐거움.</em>','Little photos.<br><em>Lots of play.</em>')}</h1><p class="hero-description">{t('한 조각씩 맞추고, 잠깐 보고 기억하고.<br>익숙한 사진이 새로운 놀이가 되는 시간.<br>혼자서도, 소중한 사람들과 함께해도 좋아요.','Piece it together. Look a little closer. Remember a little more.<br>Turn everyday photos into playful moments,<br>on your own or with your favorite people.')}</p><div class="hero-actions">{self.store_button()}<a class="text-link" href="{self.f('guide')}">{t('먼저 둘러보기','Take a peek')}</a></div><p class="hero-meta">{t('Android 9 이상 <span>·</span> 로그인 없이 <span>·</span> 오프라인 플레이', 'Android 9+ <span>·</span> No account <span>·</span> Offline play')}</p></div>
<div class="hero-art"><span class="orbit orbit-one" aria-hidden="true"></span><span class="orbit orbit-two" aria-hidden="true"></span><span class="doodle-star star-one" aria-hidden="true">✦</span><span class="doodle-star star-two" aria-hidden="true">✳</span>{self.screen(1,'hero-phone back-phone')}{self.screen(0,'hero-phone front-phone',True)}<span class="floating-note"><span aria-hidden="true">☺</span> {t('오늘은, 같이 한 판?','A little play today?')}</span></div></div><div class="wrap hero-caption">{self.image_note()}</div></section>
<section class="stats-band" aria-label="{t('리멤픽 한눈에 보기','RememPic at a glance')}"><div class="wrap stats-grid">{''.join(f'<div><strong>{n}</strong><span>{label}</span></div>' for n,label in stats)}</div></section>
<section class="section wrap" id="games"><div class="section-heading"><div><span class="eyebrow">EIGHT WAYS TO PLAY</span><h2>{t('오늘은 어떤 재미를<br>골라볼까요?','What will you<br>play today?')}</h2></div><p>{t('기억하고, 찾아보고, 맞추고.<br>쉬운 시작부터 마스터까지, 내 속도로 즐겨요.','Remember, discover, and piece things together.<br>From easy beginnings to a new personal best.')}</p></div><div class="filter-bar" role="group" aria-label="{t('게임 분류','Filter games')}" data-filter-group="games" hidden>{filters}</div><div class="games-grid" id="game-grid">{cards}</div><p class="small-note">{t('게임별 1–100레벨 · 쉬움 / 보통 / 어려움 / 마스터 · 일반 레벨은 시간 제한 없이, 10레벨마다 시간 도전', 'Levels 1–100 in each game · Easy / Normal / Hard / Master · Untimed regular levels, a timed challenge every tenth level')}</p></section>
<section class="play-story"><div class="wrap story-grid"><div class="story-screens">{self.screen(2,'story-phone')}{self.screen(4,'story-phone offset-phone')}</div><div class="story-copy"><span class="eyebrow">SMALL MOMENTS, HAPPY DISCOVERIES</span><h2>{t('조금만 더 보면,<br>새로운 재미가 보여요.','A closer look.<br>A happy discovery.')}</h2><p>{t('빈칸에 쏙 들어맞는 퍼즐 한 조각.<br>조금 전 봤던 사진이 떠오르는 순간.<br>작은 성공을 하나씩 모아보세요.','That last puzzle piece finding its place.<br>A familiar photo coming back to mind.<br>Little wins, one happy moment at a time.')}</p><ul class="check-list"><li>{t('동물부터 꽃, 풍경까지 기본 사진 180장','180 included photos, from animals to flowers and landscapes')}</li><li>{t('힌트와 게임 방법을 필요할 때 바로','Hints and instructions when you need them')}</li><li>{t('큰 글씨·동작 줄이기 설정으로 편안하게','Large text and reduced-motion settings')}</li></ul><a class="text-link" href="{self.f('guide')}">{t('게임 화면 더 보기','See more game screens')}</a></div></div></section>
<section class="section wrap together-section" id="together"><div class="together-copy"><span class="eyebrow">PASS THE PHONE, SHARE THE FUN</span><h2>{t('혼자도 좋지만,<br><em>함께라서 더 즐겁게.</em>','Good on your own.<br><em>Lovely together.</em>')}</h2><p>{t('한 기기를 둘러앉아, 차례차례 즐겨요.<br>2~4명이 같은 난이도의 서로 다른 문제에 도전하고<br>마지막에는 각자의 점수를 함께 확인해요.','Gather around one device and take turns.<br>2–4 players, different questions at the same difficulty.<br>Then see how everyone did.')}</p><ol class="steps"><li><span>01</span><div><strong>{t('이름과 난이도를 정해요','Choose names and difficulty')}</strong><p>{t('가족도 친구도, 2명부터 4명까지.','Bring a friend, or the whole family. Up to four players.')}</p></div></li><li><span>02</span><div><strong>{t('내 차례에 한 판씩 즐겨요','Play, then pass it on')}</strong><p>{t('같은 난이도, 각자에게 새로운 문제.','The same difficulty, fresh questions for each person.')}</p></div></li><li><span>03</span><div><strong>{t('점수를 보고, 한 판 더!','Compare scores. Play again!')}</strong><p>{t('같은 멤버로 새로운 문제에 다시 도전해요.','Keep the group and start a fresh round.')}</p></div></li></ol></div><div class="together-art">{self.screen(6,'together-phone')}<span class="player-label label-one">{t('내 차례!','My turn!')} <span aria-hidden="true">✦</span></span><span class="player-label label-two">{t('다음은 나!','I’m next!')} <span aria-hidden="true">☺</span></span></div></section>
<section class="photo-note"><div class="wrap photo-note-grid"><div><span class="eyebrow">YOUR PHOTOS, YOUR LITTLE WORLD</span><h2>{t('우리 집 강아지도,<br>여행의 한 장면도.','Your favorite pet.<br>Your favorite place.')}</h2><p>{t('내 사진팩을 만들면 익숙한 사진이 게임 속으로.<br>직접 고른 사진만 이 기기에 저장해요.','Make a personal pack and bring familiar photos into play.<br>Only the photos you choose, stored on your device.')}</p><a class="text-link" href="{self.f('privacy')}">{t('사진과 개인정보 보호 안내','How we handle your photos')}</a></div><div class="photo-facts"><div><span aria-hidden="true">▧</span><strong>{t('내 사진은 최대 50장','Up to 50 personal photos')}</strong><p>{t('원본은 그대로, 앱 안에 복사본만.','Your originals stay just as they are.')}</p></div><div><span aria-hidden="true">⌂</span><strong>{t('사진은 나의 기기에','Your photos stay with you')}</strong><p>{t('개발자 서버에 업로드하지 않아요.','No upload to a developer server.')}</p></div><div><span aria-hidden="true">↗</span><strong>{t('공유할 때도 마음 편히','Share a little victory')}</strong><p>{t('결과 카드에는 개인 사진을 넣지 않아요.','Result cards leave personal photos out.')}</p></div></div></div></section>
<section class="section wrap faq-section"><div><span class="eyebrow">A FEW THINGS TO KNOW</span><h2>{t('궁금한 이야기','A few helpful answers')}</h2><a class="text-link" href="{self.f('support')}">{t('고객지원 바로가기','Visit support')}</a></div>{self.faq(4)}</section>
<section class="cta-section wrap"><span class="eyebrow">MAKE A LITTLE TIME FOR PLAY</span><h2>{t('오늘의 사진이,<br>오늘의 즐거움이 되도록.','Make room for<br>a little more play.')}</h2>{self.store_button()}<p>{t('리멤픽 · 사진으로 즐기는 8가지 게임','RememPic · Eight ways to play with photos')}</p><span class="cta-star" aria-hidden="true">✳</span></section>'''

    def guide(self):
        t=self.t
        filters=''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(i==0).lower()}">{label}</button>' for i,(key,label) in enumerate([('all',t('전체 화면','All screens')),('start',t('시작하기','Getting started')),('play',t('게임하기','In play')),('together',t('함께 하기','Together')),('photos',t('내 사진팩','Photo packs')),('settings',t('설정','Settings'))]))
        cards=''.join(f'<figure class="gallery-card" data-category="{cat}">{self.screen(i, eager=i<2)}<figcaption><h2>{title[self.i]}</h2></figcaption></figure>' for i,(_,cat,title,alt) in enumerate(SCREENS))
        return f'<section class="page-intro wrap"><a class="breadcrumb" href="{self.f("index")}">← {t("홈으로", "Back home")}</a><span class="eyebrow">A PEEK INSIDE</span><h1>{TITLES["guide"][self.i]}</h1><p>{t("시작하는 순간부터 함께 웃는 결과까지.<br>사진을 누르면 더 크게 볼 수 있어요.", "From the first tap to a shared little victory.<br>Select an image to take a closer look.")}</p><p class="image-disclosure">{self.image_note()}</p></section>{self.quick_start()}<section class="wrap gallery-section" id="screens"><div class="filter-bar" role="group" aria-label="{t("화면 분류", "Filter screens")}" data-filter-group="gallery" hidden>{filters}</div><p class="filter-status" aria-live="polite" data-filter-status></p><div class="gallery-grid">{cards}</div><p class="small-note">{t("기본 제공 사진으로 촬영한 실제 화면 21장입니다. 함께 하기는 같은 난이도에서 참가자별 다른 문제를 출제합니다.", "21 actual screens using supplied sample photos. Together mode gives each player different questions at the same difficulty.")}</p></section>'

    def quick_start(self):
        t = self.t
        cards = [
            (t('처음 한 판', 'Your first game'), t('게임하기에서 8가지 게임 중 하나와 열린 레벨을 고르세요. 물음표 버튼에서 규칙을 확인하고, 필요하면 힌트로 연습해 보세요.', 'Choose one of eight games and an unlocked level. Open the question-mark help for the rules, or use a hint to practice.')),
            (t('내 사진으로', 'Use your photos'), t('사진팩에서 이름을 정해 새 팩을 만들고 사진 선택기로 사진을 추가하세요. 내 사진만 쓰거나 기본 사진과 섞을 수 있습니다.', 'Create a named pack in Photo packs and add pictures with the photo picker. Use your photos alone or mix them with built-in photos.')),
            (t('편안하게 즐기기', 'Make it comfortable'), t('홈의 설정에서 효과음·진동·큰 글씨·동작 줄이기를 조절하세요. 기록 초기화는 레벨·별·사진팩을 남깁니다.', 'Adjust sound, vibration, large text and reduced motion in Settings. Resetting records keeps levels, stars and packs.')),
        ]
        return '<section class="wrap quick-start" aria-label="'+t('시작 가이드', 'Getting started')+'">'+''.join('<article><h2>'+title+'</h2><p>'+body+'</p></article>' for title, body in cards)+'</section>'

    def support_resources(self):
        t = self.t
        return f'''<section class="support-block" id="purchases"><h2>{t('구매·복원·환불', 'Purchases, restoration & refunds')}</h2><p>{t('설정 → 광고 없이 즐기기에서 가격을 확인하고, 구매했던 Google 계정으로 구매 복원을 이용하세요. 구매 복원은 사진과 게임 진행을 복구하지 않습니다.', 'Check the price in Settings → Play without ads and restore with your purchasing Google account. Purchase restoration does not recover photos or game progress.')}</p><div class="help-links"><a href="https://support.google.com/googleplay/answer/2479637?hl={self.lang}">{t('Google Play 환불 안내', 'Google Play refund guidance')}</a><a href="{self.f('terms')}#refund">{t('구매 이용 조건', 'Purchase terms')}</a></div></section><section class="support-block"><h2>{t('필요한 안내 바로 찾기', 'Find the right guide')}</h2><div class="help-links"><a href="{self.f('guide')}">{t('사진팩·게임 시작 방법', 'Photo packs and getting started')}</a><a href="{self.f('delete-account')}">{t('사진·기록·문의 정보 삭제', 'Delete photos, records or support data')}</a><a href="{self.f('privacy')}#ads">{t('광고와 개인정보 선택', 'Ads and privacy choices')}</a></div></section>'''

    def support(self):
        t=self.t
        email=self.config['supportEmail']
        availability = (f'<p>{t("Google Play에서 설치할 수 있습니다.", "Find the app on Google Play.")}</p>'+self.store_button()) if self.config['playStoreUrl'] else f'<p>{t("공개 Google Play 주소를 준비하고 있습니다. 설치 링크가 확정되면 이 홈페이지에서 안내할게요.", "We’re preparing the public Google Play listing. A download link will appear here once it is confirmed.")}</p><span class="availability-badge">{t("출시 준비 중", "Coming soon")}</span>'
        options = [t('앱 이용 문의','App help'),t('오류 제보','Report an issue'),t('구매·복원·환불 문의','Purchase, restore or refund'),t('개인정보 문의','Privacy question'),t('문의 정보 삭제 요청','Delete support data')]
        # Remains disabled without JavaScript so private messages cannot be sent
        # as a default HTML form GET request to a static hosting server.
        disabled=' disabled'
        return f'''<section class="page-intro wrap"><span class="eyebrow">HERE TO HELP</span><h1>{TITLES['support'][self.i]}</h1><p>{t('작은 궁금증부터 사진과 기록 관리까지.<br>필요한 안내를 여기서 찾아보세요.','From your first game to managing photos and records.<br>Find a little help right here.')}</p></section><div class="wrap support-layout"><div><section class="support-block" id="availability"><span class="eyebrow">GET REMEMPIC</span><h2>{t('출시 및 설치 안내','Availability & installation')}</h2>{availability}<p class="muted">Android 9+ · {t('스마트폰에서 즐기는 리멤픽','Photo games for your Android phone')}</p></section>{self.support_resources()}<section class="support-block" id="faq"><h2>{t('자주 묻는 질문','Frequently asked questions')}</h2>{self.faq()}</section></div><aside class="contact-card" id="contact"><span class="eyebrow">SAY HELLO</span><h2>{t('도움이 더 필요하다면','Need a little more help?')}</h2><p>{self.contact()}</p><p class="muted">{t('앱 버전, 기기 모델, 문제가 생긴 상황을 알려주시면 도움이 됩니다. 개인 사진·비밀번호는 보내지 마세요.','Include the app version, device model, and what happened. Please leave out personal photos and passwords.')}</p><p class="small-note">{escape(self.config["supportResponseTime"][self.lang])}</p><form id="support-form" data-email="{escape(email)}"><label for="topic">{t('문의 종류','Topic')}</label><select id="topic" name="topic">{''.join(f'<option>{v}</option>' for v in options)}</select><label for="message">{t('문의 내용','Message')}</label><textarea id="message" name="message" rows="5" maxlength="2000" required placeholder="{t('어떤 도움이 필요하신가요?', 'How can we help?')}"></textarea><button type="submit" class="button primary"{disabled}>{t('이메일 초안 열기','Open email draft') if email else t('문의 이메일 준비 중','Support email coming soon')}</button><p id="form-status" class="small-note" role="status">{t('이 사이트에 접수되지 않습니다. 이메일 앱에서 직접 전송해야 전달됩니다.', 'Nothing is submitted to this website. Send the draft from your email app to deliver it.')}</p></form><noscript><p>{t('문의 초안 작성에는 JavaScript가 필요합니다. 위 이메일로 직접 문의할 수 있습니다.', 'The draft composer requires JavaScript. You can write directly to the email address above.')}</p></noscript><div class="contact-legal"><a href="{self.f('delete-account')}">{t('사진·기록 삭제 방법','Delete photos and records')}</a><a href="{self.f('privacy')}">{t('개인정보처리방침','Privacy policy')}</a></div></aside></div>'''

    def legal(self, page):
        t=self.t
        source={'privacy':PRIVACY,'delete-account':DELETION,'terms':TERMS}[page][self.lang]
        values=self.values()
        pending=missing_policy_fields(self.config)
        labels={'developerName':t('운영자명','operator name'),'supportEmail':t('지원 이메일','support email'),'policyEffectiveDate':t('시행일','effective date'),'supportRetention.ko':t('문의 보유·삭제 정책(한국어)','support retention and deletion (Korean)'),'supportRetention.en':t('문의 보유·삭제 정책(영어)','support retention and deletion (English)'),'supportResponseTime.ko':t('요청 처리 기한(한국어)','response times (Korean)'),'supportResponseTime.en':t('요청 처리 기한(영어)','response times (English)'),'policiesApproved':t('정책 최종 검토','final policy review')}
        pending_text=', '.join(labels[key] for key in pending)
        banner='' if not pending else f'<div class="policy-notice"><strong>{t("정책 검토본", "Draft policy")}</strong><p>{t("확인 중인 항목: ", "Still to be finalized: ")}{pending_text}. {t("확정 후 정식 정책을 이 페이지에 안내합니다.", "The final policy will be published here once these details are confirmed.")}</p></div>'
        toc=''.join(f'<a href="#{key}">{heading}</a>' for key,heading,body in source)
        sections=''.join(f'<section id="{key}"><h2>{heading}</h2>{body.format(**values)}</section>' for key,heading,body in source)
        package=f'<div><dt>{t("앱 식별자", "App identifier")}</dt><dd>{escape(self.config["productionApplicationId"])}</dd></div>' if self.config['productionApplicationId'] else ''
        identity=f'<dl class="policy-meta"><div><dt>{t("대상 앱", "App")}</dt><dd>리멤픽 / RememPic</dd></div><div><dt>{t("운영자", "Operator")}</dt><dd>{values["developer"]}</dd></div><div><dt>{t("문의", "Contact")}</dt><dd>{self.contact()}</dd></div><div><dt>{t("시행일", "Effective date")}</dt><dd>{escape(self.config["policyEffectiveDate"] or t("확정 예정", "To be confirmed"))}</dd></div>{package}</dl>'
        return f'<div class="wrap legal-layout"><aside class="legal-nav"><a class="breadcrumb" href="{self.f("index")}">← {t("홈으로", "Back home")}</a><span class="eyebrow">{t("이 페이지에서", "ON THIS PAGE")}</span><nav aria-label="{t("문서 목차", "On this page")}">{toc}</nav><button type="button" class="print-button" data-print hidden>{t("문서 인쇄", "Print document")}</button></aside><article class="legal-document"><span class="eyebrow">{dict(privacy="YOUR PHOTOS, YOUR PRIVACY",terms="TERMS OF USE").get(page,"YOU’RE IN CONTROL")}</span><h1>{TITLES[page][self.i]}</h1>{banner}{identity}{sections}<div class="legal-end">{t("관련 안내", "Related pages")} · <a href="{self.f("privacy")}">{t("개인정보처리방침", "Privacy policy")}</a> · <a href="{self.f("delete-account")}">{t("데이터 삭제", "Data deletion")}</a> · <a href="{self.f("support")}">{t("고객지원", "Support")}</a></div></article></div>'

    def render(self,page):
        title=TITLES[page][self.i]+' · '+self.t('리멤픽','RememPic')
        desc=DESCRIPTIONS[page][self.i]
        canonical=f'<link rel="canonical" href="{escape(self.base+self.f(page))}"><meta property="og:url" content="{escape(self.base+self.f(page))}"><meta property="og:image" content="{escape(self.base)}assets/og-{self.lang}.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{escape(self.t("리멤픽 · 사진으로 즐기는 여덟 가지 재미", "RememPic · Eight ways to play with photos"))}"><meta name="twitter:image" content="{escape(self.base)}assets/og-{self.lang}.png">' if self.base else ''
        alternate=''.join(f'<link rel="alternate" hreflang="{lang}" href="{escape(self.base+page+suffix)}">' for lang,suffix in [('ko','.html'),('en','.en.html'),('x-default','.en.html')])
        body=self.home() if page=='index' else self.guide() if page=='guide' else self.support() if page=='support' else self.legal(page)
        return f'''<!doctype html>
<html lang="{self.lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="theme-color" content="#f8f7ff"><title>{escape(title)}</title><meta name="description" content="{escape(desc)}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="{self.t('ko_KR','en_US')}"><meta name="twitter:card" content="summary_large_image">{canonical}{alternate}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css"><script src="app.js" defer></script></head>
<body data-page="{page}">{self.header(page)}<main id="main">{body}</main>{self.footer()}
<dialog id="lightbox" aria-labelledby="lightbox-title"><div class="lightbox-bar"><h2 id="lightbox-title"></h2><button type="button" id="close-lightbox" aria-label="{self.t('확대 이미지 닫기','Close enlarged image')}">×</button></div><div class="lightbox-stage"><button type="button" id="previous-image" aria-label="{self.t('이전 이미지','Previous image')}">←</button><img id="lightbox-image" alt=""><button type="button" id="next-image" aria-label="{self.t('다음 이미지','Next image')}">→</button></div><div class="lightbox-bottom"><span id="image-position" aria-live="polite"></span><a id="original-image" href="assets/{self.lang}/originals/01-home.png" target="_blank" rel="noopener">{self.t('원본 이미지 열기','Open original image')}</a></div><p class="lightbox-note">{self.image_note()}</p></dialog></body></html>'''


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT)
    parser.add_argument('--site-url',default=None)
    parser.add_argument('--release',action='store_true',help='Fail when required policy and release information is missing.')
    args=parser.parse_args()
    config=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
    if args.site_url:
        config['siteUrl']=args.site_url
    validate_config(config)
    missing=missing_policy_fields(config)
    if args.release:
        missing += [key for key in ['siteUrl','productionApplicationId'] if not config[key]]
        if missing:
            raise SystemExit('Release information still needed: '+', '.join(missing))
    out=args.output.resolve()
    if not out.is_relative_to(ROOT):
        raise SystemExit('Output must remain inside this website project.')
    out.mkdir(parents=True,exist_ok=True)
    if out != ROOT:
        for name in ['styles.css','app.js']:
            shutil.copy2(ROOT/name,out/name)
        shutil.copytree(ROOT/'assets',out/'assets',dirs_exist_ok=True)
    for lang in ['ko','en']:
        site=Site(lang,config)
        for page in PAGES:
            (out/site.f(page)).write_text(site.render(page)+'\n',encoding='utf-8')
    base=config['siteUrl'].rstrip('/')+'/' if config['siteUrl'] else ''
    (out/'.nojekyll').touch()
    # An absolute base makes the GitHub Pages 404 useful even for nested invalid URLs.
    base_tag=f'<base href="{escape(base)}">' if base else ''
    not_found=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">{base_tag}<title>페이지를 찾을 수 없어요 · RememPic</title><link rel="stylesheet" href="styles.css"><link rel="icon" href="assets/favicon.svg"></head><body><main class="not-found"><span class="eyebrow">404 · A LITTLE DETOUR</span><h1>페이지를 찾을 수 없어요.</h1><p lang="en">This page may have moved. Let’s head back home.</p><div class="hero-actions"><a class="button primary" href="index.html">한국어 홈으로</a><a class="button secondary" href="index.en.html" lang="en">English home</a></div></main></body></html>'
    (out/'404.html').write_text(not_found+'\n',encoding='utf-8')
    if base:
        urls=[base+Site(lang,config).f(page) for lang in ['ko','en'] for page in PAGES]
        (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{escape(url)}</loc></url>' for url in urls)+'</urlset>\n',encoding='utf-8')
        (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'sitemap.xml\n',encoding='utf-8')
    else:
        (out/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf-8')
        (out/'sitemap.xml').unlink(missing_ok=True)
    print(f'Generated 12 bilingual pages + 404 in {out}')
    if missing:
        print('Policy draft pending: '+', '.join(missing))


if __name__=='__main__':
    main()
