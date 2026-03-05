# Model Relay Desktop

<picture>
    <img alt="Model Relay Desktop" src="../icons/hero-img_f0bb32.png?raw=true">
</picture>

[![English](https://img.shields.io/badge/docs-English-purple)](README.en.md) [![简体中文](https://img.shields.io/badge/文档-简体中文-yellow)](../README.md) [![日本語](https://img.shields.io/badge/ドキュ-日本語-b7003a)](README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](README.fr.md) [![Documentação em Português (Brasil)](https://img.shields.io/badge/docs-Português-purple)](README.pt.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](README.de.md) [![Документация на русском языке](https://img.shields.io/badge/доки-Русский-darkblue)](README.ru.md)

## 소개

Model Relay Desktop은 Windows와 macOS용 로컬 프록시 기반 IDE 고정 모델 서비스 제공자 솔루션입니다.

**참고: 현재 이 프로젝트는 openai 형식의 api만 지원합니다. 다른 형식은 openai 형식으로 변환 후 사용하십시오.**

<details>
  <summary>당신은 아무것도 볼 수 없습니다~~</summary>
  <br>
  <p>Model Relay Desktop: local model relay desktop tool.</p>
 </details>

## 목차

- [Model Relay Desktop](#model-relay-desktop)
  - [소개](#소개)
  - [목차](#목차)
  - [변경 로그](#변경-로그)
    - [v1.2.0 (최신)](#v120-최신)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.0](#v100)
  - [빠른 시작](#빠른-시작)
    - [Windows 사용자 (GUI 원클릭 실행 방식)](#windows-사용자-gui-원클릭-실행-방식)
    - [macOS 사용자 (애플리케이션 설치)](#macos-사용자-애플리케이션-설치)
      - [설치 방법](#설치-방법)
      - [사용 방법](#사용-방법)
  - [macOS “패키지가 손상되었습니다” 문제 해결](#macos-패키지가-손상되었습니다-문제-해결)
    - [그래픽 인터페이스 해결 방법](#그래픽-인터페이스-해결-방법)
    - [CLI(명령어) 해결 방법](#cli명령어-해결-방법)
  - [스크립트로 시작하기](#스크립트로-시작하기)
    - [0단계: 환경 준비](#0단계-환경-준비)
      - [Windows](#windows)
        - [1단계: 자체 서명 인증서 생성](#1단계-자체-서명-인증서-생성)
        - [2단계: Windows에서 CA 인증서 신뢰 설정](#2단계-windows에서-ca-인증서-신뢰-설정)
        - [3단계: Hosts 파일 수정](#3단계-hosts-파일-수정)
        - [4단계: 로컬 프록시 서버 실행 (Python)](#4단계-로컬-프록시-서버-실행-python)
        - [5단계: Trae IDE 구성](#5단계-trae-ide-구성)
      - [macOS](#macos)
  - [😎 최신 상태 유지](#-최신-상태-유지)
  - [참고 자료](#참고-자료)

---

## 변경 로그

### v1.2.0 (최신)

- 🔄 **모델 매핑 아키텍처 리팩토링** - "1:1 매핑"에서 "통합 매핑 모델" 아키텍처로 변경
  - trae 측은 통합 매핑 모델 ID 사용, MTGA는 구성 그룹을 통해 실제 백엔드 모델 전환
  - 프록시 서버는 모델 ID 매핑과 Model Relay Desktop 인증 검증 지원
  - 전역 구성은 매핑 모델 ID 및 Model Relay Desktop 인증 Key 설정 지원
- ⚡ **구성 그룹 관리 최적화** - 구성 그룹 필드 및 검증 로직 리팩토링
  - 구성 그룹 이름을 선택 사항으로 변경, API URL, 실제 모델 ID, API Key는 필수 입력으로 변경
  - 대상 모델 ID 필드 제거, 전역 매핑 구성으로 대체
  - 구성 그룹 테이블 헤더 이름 변경, 이전 구성 파일과 하위 호환성 유지
- 🧪 **자동화 테스트 기능 추가** - 완전한 모델 연결 테스트 체계 구축
  - 구성 저장 후 모델 연결 자동 테스트 (GET `/v1/models/{모델id}`)
  - 수동 상태 확인 기능 추가, 채팅 완성 테스트 지원 (POST `/v1/chat/completions`)
  - 상세 테스트 로그 출력, 응답 내용 및 토큰 소모 통계 포함
- 🎯 **사용자 경험 향상** - 상태 확인 버튼 및 상세 안내 추가
  - 상태 확인 버튼에 툴팁 지원, 토큰 소모 위험 설명 포함
  - 비동기 테스트로 UI 차단 방지, 완성된 오류 처리 메커니즘
  - API Key 보안 표시(마스킹 처리)

<details>
<summary>히스토리 버전</summary>

### v1.1.1

- 🐛 **hosts 수정 기능 문제 수정** - hosts 파일 수정 시 줄바꿈 문자 이상 문제 해결

### v1.1.0

- ✨ **새로운 사용자 데이터 관리 기능** - 단일 파일 버전 사용자 데이터 지속적 저장 지원
  - 데이터 저장 위치: Windows `%APPDATA%\MTGA\`, macOS/Linux `~/.mtga/`
  - 백업, 복원, 사용자 데이터 삭제 지원
  - 구성 파일, SSL 인증서, hosts 백업 자동 지속화
- 🔧 **단일 파일 빌드 최적화** - `build_onefile.bat` 개선, 버전 번호 변수화 지원
- 🎯 **사용자 인터페이스 개선** - 구성 그룹 목록 새로고침 버튼 추가, 인터페이스 레이아웃 최적화
- 📖 **문서 보완** - 단일 파일 빌드 가이드 추가, 프로젝트 문서 업데이트

### v1.0.0

- ✅ **Mac OS 지원** - macOS 애플리케이션 설치 방식 지원
- 🔄 **기본 제공업체 변경** - DeepSeek에서 OpenAI로 변경
- 📦 **파일 리팩토링** - ds 관련 파일을 `*_ds.*` 형식으로 변경하여 보관
- 🌐 **API URL 형식 변경** - `https://your-api.example.com/v1`에서 `https://your-api.example.com`로 변경

</details>

---

## 빠른 시작

### Windows 사용자 (GUI 원클릭 실행 방식)

1. [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases)에서 최신 버전의 `Model-Relay-Desktop-v{버전}-x64.exe` 다운로드
2. 다운로드한 exe 파일 실행 (관리자 권한 필요)
3. 열린 그래픽 인터페이스에서 API URL과 모델 ID 입력
   - **API URL은 도메인만 입력 (포트 번호는 선택 사항, 모르면 입력하지 않음), 뒤의 경로는 입력하지 않음, 예: `https://your-api.example.com`**
   - **멀티모달 기능을 활성화하려면, 모델 이름을 내장된 멀티모달 모델 이름에 매핑할 수 있습니다:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
4. "모든 서비스 일괄 시작" 버튼 클릭
5. 프로그램이 자동으로 다음 작업을 완료할 때까지 대기:
   - 인증서 생성 및 설치
   - hosts 파일 수정
   - 프록시 서버 시작
6. 완료 후, [5단계: Trae IDE 설정](#5단계-trae-ide-설정)에 따라 IDE 설정 진행

> [!NOTE]
>
> - 첫 실행 시 방화벽 접근 권한 허용이 필요할 수 있음
> - 단일 파일 버전은 사용자 데이터 지속성 저장을 지원하며, 설정과 인증서가 자동으로 저장됨

### macOS 사용자 (애플리케이션 설치)

#### 설치 방법

1. [GitHub Releases](https://github.com/xiaoliuzhuan/model-relay-desktop/releases)에서 최신 버전의 `Model-Relay-Desktop-v{버전}-aarch64.dmg` 다운로드
2. DMG 파일 더블 클릭, 시스템이 자동으로 설치 패키지 마운트
3. `Model Relay Desktop.app`을 `Applications` 폴더로 드래그
4. 런치패드 또는 Applications 폴더에서 애플리케이션 시작

#### 사용 방법

1. `Model Relay Desktop.app`을 실행합니다 (첫 실행 시 시스템 환경설정에서 실행 허용이 필요할 수 있음)
2. 그래픽 인터페이스에서 다음을 입력합니다:
   - **API URL**: 사용자의 API 서비스 주소 (예: `https://your-api.example.com`)
   - **멀티모달 기능을 활성화하려면, 모델 이름을 내장된 멀티모달 모델 이름에 매핑할 수 있습니다:**
   - <img width="247" height="76" alt="model mapping" src="../images/model-mapping.png?raw=true" />
   - <img width="380" height="141" alt="model mapping effects" src="../images/model-mapping-effects.png?raw=true" />
3. "모든 서비스 일괄 시작" 버튼을 클릭합니다
4. 프로그램이 자동으로 완료합니다:
   - SSL 인증서 생성 및 시스템 키체인에 설치
   - `/etc/hosts` 파일 수정 (관리자 권한 필요)
5. 열린 키체인 창에서 생성된 인증서를 신뢰하도록 수동 설정 필요, 기본 이름은 `MTGA_CA`
6. 로컬 프록시 서버 시작
7. 아래의 [Trae IDE 설정](#5-단계-trae-ide-설정)에 따라 설정 완료

> [!NOTE]
> 목표 언어: 한국어

> - 인증서 설치 및 hosts 수정은 관리자 권한이 필요합니다.
> - “패키지가 손상되었습니다”라는 메시지가 나타나면 [macOS “패키지가 손상되었습니다” 문제 해결](#macos-패키지가-손상되었습니다-문제-해결)을 참고하세요.

## macOS “패키지가 손상되었습니다” 문제 해결

`Model Relay Desktop.app` 실행 시 다음과 같은 메시지가 나타나면:

<img width="244" height="223" alt="app corrupted" src="../images/app-corrupted.png?raw=true" />

**취소** 버튼을 클릭하세요. 그 후 아래 방법을 따라 문제를 해결할 수 있습니다.

### 그래픽 인터페이스 해결 방법

1. [Sentinel Releases](https://github.com/alienator88/Sentinel/releases/latest)에서 `Sentinel.dmg`를 다운로드합니다.
2. `Sentinel.dmg` 파일을 더블 클릭하여 열고, `Sentinel.app`를 `Applications` 폴더로 드래그합니다.
3. 런치패드 또는 Applications 폴더에서 `Sentinel.app`를 실행합니다.
4. 본 프로젝트의 `Model Relay Desktop.app`를 `Sentinel.app`의 왼쪽 창으로 드래그합니다.
   - <img width="355.33" height="373.33" alt="sentinel add app" src="../images/sentinel-add-app.png?raw=true" />

`Model Relay Desktop.app`가 자동으로 처리되고 실행됩니다.

### CLI(명령어) 해결 방법

1. `Model Relay Desktop.app`의 전체 경로를 찾습니다. 예: `/Applications/Model Relay Desktop.app`
2. 터미널(Terminal) 앱을 실행합니다.
3. 아래 명령어를 실행하여 `Model Relay Desktop.app`를 서명 해제합니다:
   ```zsh
   xattr -d com.apple.quarantine <앱 전체 경로>
   ```
   위 명령어는 `Model Relay Desktop.app`에서 `com.apple.quarantine` 확장 속성을 제거합니다.
4. `Model Relay Desktop.app`를 실행합니다.

---

## 스크립트로 시작하기

### 0단계: 환경 준비

#### Windows

- Windows 10 이상 시스템
- 관리자 권한 보유
- Python 환경 설치, Python 3.10 이상 권장
- Git 설치

##### 1단계: 자체 서명 인증서 생성

Git Bash 열기:

```bash
# ca 디렉토리로 이동
cd "mtga/ca"

# 1. CA 인증서 생성 (ca.crt 및 ca.key)
./genca.sh
```

`./genca.sh` 실행 시 "Do you want to generate ca cert and key? [yes/no]" 질문에 `y` 입력 후 엔터. 이후 일부 정보 입력 요청:

- `Country Name (2 letter code) []`: `CN` 입력 (또는 다른 국가 코드)
- 기타 필드(State, Locality, Organization, Common Name for CA)는 필요에 따라 입력 또는 공백, `X` 입력 권장. Common Name은 `MTGA_CA` 등 입력 가능. 이메일은 공백 가능.

```bash
# 2. api.openai.com 서버 인증서 생성 (api.openai.com.crt 및 api.openai.com.key)
#  이 스크립트는 동일 디렉토리의 api.openai.com.subj 및 api.openai.com.cnf 구성 파일을 사용합니다.
./gencrt.sh api.openai.com
```

실행 완료 후 `mtga\ca` 디렉토리에서 다음 중요 파일 확인:

- `ca.crt` (사용자 정의 CA 인증서)
- `ca.key` (사용자 정의 CA 개인 키 - **유출 금지**)
- `api.openai.com.crt` (로컬 프록시 서버용 SSL 인증서)
- `api.openai.com.key` (로컬 프록시 서버용 SSL 개인 키 - **유출 금지**)

##### 2단계: Windows에서 CA 인증서 신뢰 설정

1.  `mtga\ca\ca.crt` 파일 찾기.
2.  `ca.crt` 파일 더블 클릭, 인증서 뷰어 열기.
3.  "인증서 설치..." 버튼 클릭.
4.  "현재 사용자" 또는 "로컬 컴퓨터" 선택. "로컬 컴퓨터" 권장 (관리자 권한 필요), 모든 사용자에게 적용.
5.  다음 대화 상자에서 "모든 인증서를 다음 저장소에 저장" 선택, "찾아보기..." 클릭.
6.  "신뢰할 수 있는 루트 인증 기관" 선택, "확인" 클릭.
7.  "다음" 클릭, "완료" 클릭. 보안 경고 팝업 시 "예" 선택.

##### 3단계: Hosts 파일 수정

**⚠️경고: 이 단계를 실행하면 기존 OpenAI API에 더 이상 접근할 수 없습니다. 웹사이트 사용에는 영향이 없습니다.**

관리자 권한으로 Hosts 파일을 수정하여 `api.openai.com`을 로컬 머신으로 가리키도록 설정해야 합니다.

1.  Hosts 파일 경로: `C:\Windows\System32\drivers\etc\hosts`
2.  관리자 권한으로 메모장(또는 다른 텍스트 편집기)을 사용해 이 파일을 엽니다.
3.  파일 끝에 다음 줄을 추가합니다:
    ```
    127.0.0.1 api.openai.com
    ```
4.  파일을 저장합니다.

##### 4단계: 로컬 프록시 서버 실행 (Python)

**프록시 서버 실행 전:**

1.  **의존성 설치**:
    ```bash
    pip install Flask requests
    ```
2.  **스크립트 구성**:
    - `trae_proxy.py` 파일을 엽니다.
    - **`TARGET_API_BASE_URL` 수정**: 실제로 연결하려는 사이트의 OpenAI 형식 API 기본 URL로 변경합니다 (예: `"https://your-api.example.com"`).
    - **인증서 경로 확인**: 스크립트는 기본적으로 `mtga\ca`에서 `api.openai.com.crt`와 `api.openai.com.key`를 읽습니다. 인증서가 이 경로에 없으면 `CERT_FILE`과 `KEY_FILE` 값을 수정하거나, 이 두 파일을 스크립트가 지정한 `CERT_DIR`로 복사하세요.

**프록시 서버 실행:**

명령 프롬프트(cmd) 또는 PowerShell을 **관리자 권한으로 실행** (포트 443을 수신해야 하므로)한 후 다음을 실행합니다:

```bash
python trae_proxy.py
```

모든 것이 순조롭다면 서버 시작 로그를 볼 수 있어야 합니다.

##### 5단계: Trae IDE 구성

1.  Trae IDE를 열고 로그인합니다.
2.  AI 대화 상자에서 오른쪽 하단의 모델 아이콘을 클릭하고 끝에 있는 "모델 추가"를 선택합니다.
3.  **공급자**: `OpenAI`를 선택합니다.
4.  **모델**: "사용자 정의 모델"을 선택합니다.
5.  **모델 ID**: Python 스크립트에서 `CUSTOM_MODEL_ID`로 정의한 값을 입력합니다 (예: `my-custom-local-model`).
6.  **API 키**:
    - 대상 API에 API 키가 필요하고 Trae가 이를 `Authorization: Bearer <key>`로 전달하는 경우, 여기에 입력한 키가 Python 프록시에 의해 전달됩니다.
    - Trae에서 OpenAI를 구성할 때 API 키는 `remove_reasoning_content` 구성과 관련이 있습니다. 우리의 Python 프록시는 이 로직을 처리하지 않으며, 단순히 Authorization 헤더를 전달합니다. 대상 API에 필요한 키나 임의의 `sk-xxxx` 형식 키를 입력해 볼 수 있습니다.

7.  "모델 추가"를 클릭합니다.
8.  AI 채팅 상자로 돌아가서 오른쪽 하단에서 방금 추가한 사용자 정의 모델을 선택합니다.

이제 Trae를 통해 이 사용자 정의 모델과 상호작용할 때, 요청은 로컬 Python 프록시를 거쳐 구성한 `TARGET_API_BASE_URL`로 전달되어야 합니다.

**문제 해결 팁:**

- **포트 충돌**: 443 포트가 이미 사용 중인 경우(예: IIS, Skype 또는 기타 서비스), Python 스크립트가 시작되지 않습니다. 해당 포트를 사용하는 서비스를 중지하거나 Python 스크립트와 Nginx(사용하는 경우)가 다른 포트를 수신하도록 수정해야 합니다(그러나 이는 Trae가 `https://api.openai.com`의 443 포트에 대한 액세스를 하드코딩하기 때문에 더 복잡해집니다).
- **방화벽**: Windows 방화벽이 Python이 443 포트에서의 인바운드 연결을 수신하도록 허용하는지 확인하세요(비록 로컬 연결 `127.0.0.1`이라도 일반적으로 방화벽을 특별히 구성할 필요는 없지만, 확인할 가치가 있습니다).
- **인증서 문제**: Trae가 SSL/TLS 관련 오류를 보고하는 경우, CA 인증서가 "신뢰할 수 있는 루트 인증 기관"에 올바르게 설치되었는지, 그리고 Python 프록시가 `api.openai.com.crt`와 `.key`를 올바르게 로드하는지仔細히 확인하세요.
- **프록시 로그**: Python 스크립트는 문제 진단에 도움이 될 수 있는 일부 로그를 출력합니다.

이 솔루션은 vproxy + nginx를 직접 사용하는 방식보다 더 통합되어 있으며, TLS 종료와 프록시 로직을 모두 하나의 Python 스크립트에 넣어 Windows에서 프로토타입 검증을 빠르게 수행하는 데 더 적합합니다.

#### macOS

-> [Mac OS 스크립트 시작 방법](README_macOS_cli.md)

---

## 😎 최신 상태 유지

저장소 오른쪽 상단의 Star 및 Watch 버튼을 클릭하여 최신 소식을 받아보세요.

![star to keep latest](https://github.com/xiaoliuzhuan/model-relay-desktop/blob/main/images/star-to-keep-latest.gif?raw=true)

---

## 참고 자료

`ca` 디렉토리는 `wkgcass/vproxy` 저장소에서 참조되었으며, 대단히 감사합니다!
