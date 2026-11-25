# 리멤픽 / RememPic 홈페이지

`D:\Projects\familyGame`의 Android 앱을 소개하는 한국어·영어 정적 홈페이지입니다. `characterGameHome`의 지원·정책 구성을 참고하고 리멤픽 0.9.0의 현재 소스와 대조해 내용을 작성했습니다. 기존 GitHub Pages 주소와 페이지 경로는 유지합니다.

## 2026-11-20 반영 사항

- 지정한 `familyGame/artifacts/marketing-current/deliverables/website`의 캡처·아이콘·공유 이미지 적용. 기존 8장 교체 및 나머지 게임·사진팩·설정 화면 추가로 총 21장.
- 두 언어 모두 **현재 한국어 앱의 실제 화면**을 사용하며 영어 앱 캡처로 표시하지 않습니다. 원본 PNG는 변경하지 않고 SHA-256으로 검증합니다.
- 브랜드를 리멤픽 / RememPic으로 통일하고 이미지 설명·게임명·링크 공유용 Open Graph 및 Twitter 이미지를 갱신했습니다.
- 사용 가이드, 광고 제거 구매·복원·환불 지원, 개인정보처리방침, 데이터 삭제 및 이용약관을 보완했습니다. 현재 앱에서 제거된 친구 도전 코드 안내를 제거했습니다.
- 기존의 광고·결제·인터넷 권한 없음 설명을 폐기하고 AdMob, Google Play, 기기 데이터, 홈페이지와 이메일의 처리를 구분했습니다.
- 본문 크기와 작은 화면의 정책 가독성을 개선했습니다. 이미지 필터·확대·키보드 탐색·언어 전환·문의 초안·JavaScript 없는 본문을 유지합니다.

## 페이지

| 내용 | 한국어 | 영어 |
| --- | --- | --- |
| 소개·게임·함께 하기 | `index.html` | `index.en.html` |
| 시작 안내·화면 21장 | `guide.html` | `guide.en.html` |
| FAQ·구매/복원/환불·문의 | `support.html` | `support.en.html` |
| 개인정보처리방침 | `privacy.html` | `privacy.en.html` |
| 계정 및 데이터 삭제 | `delete-account.html` | `delete-account.en.html` |
| 이용약관 | `terms.html` | `terms.en.html` |

`404.html`은 두 언어의 홈 복귀 링크를 제공합니다. 모든 경로는 프로젝트 하위 경로에서도 동작합니다. 외부 폰트·사이트 분석·쿠키·문의 저장 서버는 없습니다. 문의 버튼은 이메일 앱에 초안을 열며 사용자가 직접 보내야 전달됩니다.

## 미리보기와 생성

```powershell
python build_site.py
python -m http.server 3260 --bind 127.0.0.1
```

http://127.0.0.1:3260/index.html 에서 확인하거나 `index.html`을 직접 엽니다.

`content.py`는 문구·갤러리, `build_site.py`는 HTML 생성, `styles.css`·`app.js`는 화면·동작, `site-config.json`은 운영 정보를 담당합니다. 생성된 HTML을 직접 수정하면 다음 생성에서 덮어씁니다. 사이트 생성·배포에는 Python 표준 라이브러리만 필요합니다.

이미지 재가져오기와 브라우저 검증에는 별도 가상환경을 사용합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-qa.txt
.\.venv\Scripts\python.exe scripts/prepare_assets.py
```

이미지 가져오기는 패키지의 모든 SHA-256을 확인한 후 복사합니다. 제공된 기존 8장의 WebP는 그대로 유지하고 추가 13장만 480/800px WebP를 생성합니다. 다른 패키지 위치는 `--source`로 전달합니다. 생성 후 사이트 자체는 원본 앱 프로젝트 없이 동작합니다.

## 운영 정보와 정책 검토

운영자 **K-Terang**, 이메일 **greatryuhg@gmail.com**, 사이트 기준 주소 **https://k-ternag.github.io/imageGameHome/** 를 사용합니다. 앱 ID는 `com.photogames.app`입니다. 한국어·영어 홈과 고객지원에서 설치 페이지를 열 수 있습니다. [리멤픽 Google Play 페이지](https://play.google.com/store/apps/details?id=com.photogames.app)

문의 보관은 참고 프로젝트와 동일하게 **처리 완료 후 30일**, 메일함·휴지통 및 별도 첨부 사본 삭제로 작성했습니다. 답변은 지체 없이 처리하고 추가 확인 시 사유·예상 일정을 안내하는 기준입니다. 이는 운영자가 실제로 실행할 절차이며 자동 삭제나 자동 회신을 구현한 것은 아닙니다. 문서 적용 예정일은 `2026-11-20`입니다.

`policiesApproved`는 정책 최종 검토를 마친 뒤 `true`로 설정합니다.

- 아동용 광고 설정: `InterstitialController.kt`는 `AD_AUDIENCE == "children"`일 때 CHILD 처리를 적용합니다. Gradle 기본값은 `unconfirmed`이고 출시 설정에서 `adults`도 허용하므로, README의 가족용 설명만으로 최종 AAB에 CHILD가 적용됐다고 단정하지 않았습니다. 최종 대상 연령·동의·광고 설정을 확인한 뒤 정책의 아동 항목도 맞춰 확정하세요.
- 정책 시행일, 실제 문의 보관·삭제·회신 절차, 최종 앱의 SDK와 권한을 검토하고 `policiesApproved`를 true로 설정하세요.

```powershell
python build_site.py --release
```

`--release` 검사는 정책 승인까지 요구합니다. 일반 생성·배포는 정책 검토 중에도 가능합니다.

광고 판매자 ID는 이 앱의 운영 계정을 확인하지 못해 참고 앱의 `app-ads.txt`를 복사하지 않았습니다. 계정 확정 후 스토어에 등록한 개발자 웹사이트의 도메인 루트에 별도로 제공해야 합니다.

## 검증과 배포 파일

```powershell
python build_site.py
python scripts/verify_site.py
python scripts/verify_config.py
node --check app.js
python build_site.py --output dist
python scripts/verify_site.py dist
```

로컬 서버 실행 후:

```powershell
.\.venv\Scripts\python.exe scripts/browser_check.py --base-url http://127.0.0.1:3260/ --channel msedge
```

설치된 Edge를 이용하며, Playwright Chromium을 설치한 환경에서는 `--channel msedge`를 생략합니다. 한국어·영어 12개 페이지를 320/390/768/1440px에서 검사하고 이미지 로드, 필터·확대·방향키·Escape·포커스 복귀·메뉴·언어 전환·FAQ·메일 초안 및 JavaScript 비활성화 동작을 확인합니다. 메일 검사는 발송 없이 초안 URL만 확인합니다. 보고서·스크린샷은 `artifacts/`, 최종 요약은 `verification.json`입니다.

공개 파일은 `dist/`, 압축본은 `artifacts/familyGameHome-pages.zip`입니다. 루트 소스·설정·가상환경·검증 캡처를 배포하지 않습니다.

기존 `.github/workflows/pages.yml`은 `main` push 또는 수동 실행 시 실제 Pages 주소로 생성·검증하고 `dist/`를 배포합니다. 대상 저장소는 https://github.com/K-Ternag/imageGameHome 입니다. Settings → Pages → Source에서 GitHub Actions를 선택합니다. 기존 `push-home.ps1`은 별도로 업로드할 때 사용할 수 있습니다.

## 앱 소스와 공식 자료

2026-11-20 기준 `app/build.gradle.kts`, `AndroidManifest.xml`, `LocalData.kt`, `PhotoImportResult.kt`, `PacksScreen.kt`, `PhotoApp.kt`, `CommerceUi.kt`, `CommerceStore.kt`, `PlayBillingController.kt`, `InterstitialController.kt`와 최신 마케팅 자료를 확인했습니다. 앱·APK·AAB는 수정하지 않았습니다.

- Google Mobile Ads 25.5.0, Play Billing 9.1.0 사용. 인터넷·네트워크 상태 권한 존재. 광고 ID·AdServices 관련 권한은 Manifest에서 제거.
- 개인 사진 최대 50장, 선택 항목만 1,200px JPEG로 앱 내부 복사. 원본 불변, 복사본 EXIF 제거. 자동 백업 비활성.
- 앱 자체 계정·개발자 백엔드·Drive·날씨 기능 없음. 참고 앱의 Drive·WeatherAPI·나이 선택 기능은 정책에 가져오지 않음.
- 구매·광고 상태는 기기 보관. 이벤트는 코드·시각 최대 80개이며 구매 토큰·영수증·이메일·사진 경로를 로그에 포함하지 않음.
- 광고 제거 구매 복원과 게임 진행 복원, 기기 삭제와 Google 거래 기록·외부 공유·문의 기록 삭제를 구분.

외부 처리·스토어 안내는 [Google Play 사용자 데이터 정책](https://support.google.com/googleplay/android-developer/answer/10144311?hl=en), [광고 SDK 데이터 공개](https://developers.google.com/admob/android/privacy/play-data-disclosure), [광고 연령별 설정](https://developers.google.com/admob/android/targeting), [Google 개인정보처리방침](https://policies.google.com/privacy?hl=ko), [보관·삭제 안내](https://policies.google.com/technologies/retention?hl=ko)를 참고했습니다.

홈페이지 접속 정보와 국외 처리는 [GitHub Pages 접속 데이터](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection), [GitHub 개인정보처리방침](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement)을 참고했습니다. 구매 환불은 [Google Play 공식 환불 안내](https://support.google.com/googleplay/answer/2479637?hl=ko)로 연결합니다. 홈페이지 문서 작성은 Play Console 신고·계정 설정·실결제 검증을 대신하지 않습니다.
