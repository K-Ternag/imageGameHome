# 사진게임 / Photo Games 홈페이지

`D:\Projects\familyGame`의 Android 앱을 소개하는 한국어·영어 정적 홈페이지입니다. `foutFoldHome`의 소개·지원·정책 페이지 구성을 참고하되, 사진게임의 실제 기능에 맞춰 새로 만들었습니다. GitHub Pages 프로젝트 하위 경로에서 동작하며 외부 폰트·분석 스크립트·쿠키·백엔드가 없습니다.

## 미리보기

`index.html`을 직접 열거나 다음 명령으로 실행합니다.

```powershell
python -m http.server 3260 --bind 127.0.0.1
```

- 한국어: http://127.0.0.1:3260/index.html
- 영어: http://127.0.0.1:3260/index.en.html

## 포함 페이지

| 페이지 | 한국어 | 영어 |
| --- | --- | --- |
| 앱 소개·8가지 게임·함께 하기 | `index.html` | `index.en.html` |
| 이미지 8장 분류·확대·원본 보기 | `guide.html` | `guide.en.html` |
| 출시 안내·FAQ·이메일 문의 | `support.html` | `support.en.html` |
| 개인정보처리방침 | `privacy.html` | `privacy.en.html` |
| 계정 및 데이터 삭제 | `delete-account.html` | `delete-account.en.html` |
| 이용약관 | `terms.html` | `terms.en.html` |

별도 `404.html`, 파비콘, 검색 설명, 언어 링크, 반응형 레이아웃, 키보드 이미지 탐색, 동작 줄이기와 인쇄 스타일을 포함합니다. 주요 본문·정책·FAQ는 JavaScript 없이도 읽을 수 있습니다. 설치 URL이 없으면 출시 안내로 연결되며 개발 패키지명으로 설치 주소를 만들지 않습니다.

## 이미지

- 한국어 원본: `D:\Projects\familyGame\artifacts\marketing-v2\website`
- 영어 원본: `D:\Projects\familyGame\artifacts\website-en-v1\images`
- 복사본: `assets/ko/originals`, `assets/en/originals`
- 웹용 파생 이미지: 각 언어의 `screens` 안 480px·800px WebP
- 원본 해시: 각 언어의 `manifest.json`

한국어는 실제 개발 버전 캡처입니다. 영어는 사용자가 제공한 **영문 문구로 편집한 홍보용 이미지**이며 실행 중인 영어 앱의 캡처가 아닙니다. 페이지에 이를 명시하고 영문 앱 지원을 약속하지 않습니다. 일부 한국어 함께 하기 캡처의 과거 ‘같은 문제’ 문구와 달리, 현재 앱은 참가자별 다른 문제·같은 난이도를 사용하므로 본문에서 현재 동작을 설명합니다. 원본 PNG는 수정하지 않았습니다.

이미지 재가져오기만 Pillow가 필요합니다. 이미 포함된 이미지를 이용한 사이트 생성·배포는 Python 표준 라이브러리만 사용합니다.

```powershell
python scripts/prepare_assets.py
python scripts/prepare_assets.py --locale en --source D:\Projects\familyGame\artifacts\website-en-v1\images
```

## 운영 정보 변경

`site-config.json`을 수정하고 `python build_site.py`를 실행합니다. 설정은 HTML 본문에 반영되므로 JavaScript를 끈 상태에서도 연락처·정책을 확인할 수 있습니다. 생성된 HTML을 직접 편집하면 다음 생성 때 덮어씁니다. 문구의 원본은 `content.py`, 레이아웃은 `build_site.py`, 스타일과 동작은 `styles.css`, `app.js`입니다.

| 설정 | 입력 내용 |
| --- | --- |
| `developerName` | Play 등록정보와 일치하는 실제 운영자·개발자명 |
| `supportEmail` | 실제 문의·개인정보 요청을 수신할 이메일 |
| `siteUrl` | 최종 홈페이지 주소, 예: `https://사용자.github.io/저장소/` |
| `playStoreUrl` | 공개된 실제 Play URL. 현재 미정이므로 빈 값 유지 |
| `productionApplicationId` | 확정된 배포 패키지명. 현재 개발 ID로 대체하지 않음 |
| `policyEffectiveDate` | 확정된 정책 시행일 `YYYY-MM-DD` |
| `supportRetention.ko/en` | 문의 이메일·첨부·처리 기록의 실제 보유 기간과 삭제 절차 |
| `supportResponseTime.ko/en` | 문의·권리 행사 요청의 실제 처리 기한 |
| `policiesApproved` | 실제 운영 및 배포 앱과 내용을 확인한 뒤 `true` |

참고 홈페이지의 로컬 `site-config.js`와 공개본(2026-11-14 확인) 모두 운영자·지원 이메일이 비어 있어 추측하지 않았습니다. 운영 정보가 없으면 정책에 검토본 안내를 표시하고 문의 전송 버튼은 비활성화합니다. 이메일이 입력되면 문의 버튼은 **메일 초안만 열며**, 사용자가 이메일 앱에서 전송해야 합니다. 웹 서버 접수나 자동 데이터 삭제 기능은 아닙니다. 한국어·영어의 보유 정책과 처리 기한을 모두 설정해야 검토본 표시가 사라집니다.

사용자가 제공한 개발자명 **K-Terang**, 지원 이메일 **greatryuhg@gmail.com**을 반영했습니다. 두 언어의 정책·지원·삭제 안내에 정적으로 표시되며 JavaScript가 있는 환경에서 이메일 초안 기능이 활성화됩니다. 개인정보처리방침 시행일, 문의 보유·삭제 기간, 처리 기한과 최종 정책 검토는 아직 미정입니다.

## GitHub Pages 배포

대상 저장소는 https://github.com/K-Ternag/imageGameHome 입니다. 기본 Pages 주소는 https://k-ternag.github.io/imageGameHome/ 로 설정했습니다. 저장소 업로드와 Pages 게시 성공은 별개이므로 아래 설정과 Actions 결과를 확인하세요.

이 작업 환경에서는 `.git/config`와 `index.lock` 쓰기가 거부되었고, GitHub 연결도 파일 생성에 `403 Resource not accessible by integration`을 반환하여 아직 원격 업로드하지 못했습니다. Git 쓰기 권한이 있는 일반 PowerShell에서 `./push-home.ps1`을 실행하면 생성·검증 후 원격을 확인하고 커밋·push합니다. 스크립트는 원격에 새 이력이 생긴 경우 확인 없이 덮어쓰지 않습니다.

**권장: GitHub Actions**

1. 사이트 전용 저장소의 `main` 브랜치에 프로젝트를 올립니다.
2. Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 선택합니다.
3. Actions → **Publish GitHub Pages** → Run workflow를 실행하거나 `main`에 push합니다.
4. 워크플로가 생성·검증한 `dist/`만 배포합니다. README·설정 파일·검증 캡처 등 개발 파일은 배포하지 않습니다.
5. 실제 Pages 주소는 빌드에 자동 전달되어 canonical, 언어별 URL, sitemap 및 중첩 경로 404의 기준 주소에 사용됩니다.

**빌드 없이 branch에서 게시**

`siteUrl`을 먼저 설정하고 `python build_site.py`를 실행한 뒤 생성된 루트 HTML, `assets/`, `styles.css`, `app.js`, `.nojekyll`, `robots.txt`, `sitemap.xml`을 올립니다. Pages에서 **Deploy from a branch → main → /(root)**를 고릅니다. 두 배포 방식을 동시에 활성화하지 마세요.

공개 주소가 생긴 뒤 홈·양쪽 언어 정책·삭제·지원 페이지가 로그인 없이 열리는지 확인합니다. [GitHub 공식 워크플로 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)를 기준으로 구성했습니다.

## Play Console 등록용 URL과 남은 운영 작업

| 등록 항목 | URL |
| --- | --- |
| 개발자 웹사이트 | `{홈페이지주소}/index.html` |
| 개인정보처리방침 | `{홈페이지주소}/privacy.html` |
| 영어 개인정보처리방침 | `{홈페이지주소}/privacy.en.html` |
| 데이터 삭제 안내 | `{홈페이지주소}/delete-account.html` |
| 고객지원 | `{홈페이지주소}/support.html` 및 실제 지원 이메일 |

- 운영자·문의처·시행일·문의 보관 및 처리 기한을 확정해야 정식 정책으로 제출할 수 있습니다. 확인용 명령은 `python build_site.py --release`입니다. 미정 정보가 있으면 항목을 표시하고 실패합니다. Play URL은 출시 전에는 없어도 되지만, 실제 배포 패키지명·사이트 URL은 이 검사에 필요합니다.
- 현재 앱은 계정 생성 기능이 없습니다. 계정 삭제 요건이 있는 앱처럼 가짜 탈퇴 양식을 만들지 않았습니다. 데이터 보안 양식의 계정 생성 항목은 출시 앱의 실제 동작에 맞게 작성하세요. 삭제 안내 페이지는 로컬 사진·기록 삭제와 문의 정보 삭제 방법을 제공합니다. [Google 계정 삭제 요건](https://support.google.com/googleplay/android-developer/answer/13327111?hl=ko)
- 개인정보처리방침은 Play Console뿐 아니라 **앱 자체에서도** 링크 또는 전문을 제공해야 합니다. 현재 소스의 ‘사진·저장 안내’는 짧은 안내이므로 정식 방침 링크/전문 연결은 앱에서 별도로 해야 합니다. 이 작업은 홈페이지 폴더만 수정했습니다. [Google 사용자 데이터 정책](https://support.google.com/googleplay/android-developer/answer/10144311?hl=ko)
- 현재 확인한 v0.8.0의 Manifest에는 인터넷·전체 갤러리 권한이 없고 광고·결제·분석 SDK가 없습니다. 가격 검토 문서는 출시 기능으로 간주하지 않았습니다. 실제 출시 AAB에 SDK가 추가되면 홈페이지 정책과 데이터 보안 응답을 다시 맞춰야 합니다. 광고 SDK가 없으므로 다른 앱의 `app-ads.txt`는 복사하지 않았습니다.
- ‘가족과 함께’라는 문구만으로 아동 대상 여부·연령 등급을 임의 확정하지 않았습니다. Play 대상 연령·콘텐츠 등급은 실제 제품과 출시 대상에 맞춰 작성하세요.
- 문의 이메일을 확정한 뒤 실제 메일 수신·회신·삭제 처리 절차를 운영자가 확인해야 합니다. 정책 HTML 제작만으로 Play 등록이나 운영 절차가 완료되지는 않습니다.

## 검증

```powershell
python build_site.py
python scripts/verify_site.py
python scripts/verify_config.py
node --check app.js
python build_site.py --output dist
python scripts/verify_site.py dist
```

브라우저 검증에는 이미 설치된 Python Playwright와 Chromium을 사용합니다. 로컬 서버 실행 후 `python scripts/browser_check.py --base-url http://127.0.0.1:3260/`를 실행하면 한국어·영어 12개 페이지의 화면폭별 넘침, JS 오류, 이미지 로드, 언어 전환·필터·확대·메뉴·FAQ·JavaScript 없는 문서를 확인합니다. 결과와 캡처는 Git에서 제외한 `artifacts/`에 저장합니다. 단순 경로 검사와 실제 브라우저 결과를 구분하여 기록합니다.

이번 환경에서는 Playwright가 Windows 접근 권한 오류(`WinError 5`, 드라이버 통신용 파이프 생성)로 시작되지 않아 브라우저 검증은 수행하지 못했습니다. `artifacts/browser-verification.json`에 실패가 기록되어 있으며, 화면·상호작용이 검증됐다는 의미로 해석하면 안 됩니다. HTML·경로·앵커·언어별 이미지·해시·설정 검사는 통과했습니다. 재실행 가능한 브라우저 검사 스크립트는 포함했습니다.

바로 업로드할 공개 파일은 `dist/`, 동일 내용의 압축본은 `artifacts/familyGameHome-pages.zip`입니다. canonical/sitemap에는 설정된 Pages 주소를 사용하며 Actions에서는 실제 배포 주소를 자동 반영합니다. 호스팅 주소를 바꾸면 `siteUrl`도 변경하고 다시 생성하세요.

## 소스 확인 근거

2026-11-14 기준 `familyGame/README.md`, `app/build.gradle.kts`, `AndroidManifest.xml`, `LocalData.kt`, `PhotoApp.kt`, `PacksScreen.kt` 및 이미지 사용 안내를 확인했습니다. 개인 사진은 선택 항목만 최대 1,200px JPEG로 복사하며 GPS/EXIF를 제거합니다. 기록 초기화는 열린 레벨·별·사진팩을 남기고, 전체 삭제는 Android 앱 데이터 삭제로 안내합니다. 클라우드 백업이 있는 참고 앱의 정책을 그대로 가져오지 않았습니다.
