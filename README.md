# CBNU_2026_Open_Source_Web_Software_Project
<img width="1919" height="940" alt="image" src="https://github.com/user-attachments/assets/aeff955b-d317-430f-b842-d39e1bd1808a" />

## 프로젝트 기술 스택 정리

### 1) 백엔드 프레임워크
- Flask
	- 라우팅, 요청/응답 처리, 세션, 템플릿 렌더링
	- 주요 사용: Blueprint, request, session, jsonify, render_template, redirect, url_for

### 2) ORM 및 데이터베이스
- Flask-SQLAlchemy
	- 모델 정의, 관계 설정, 트랜잭션 처리, 테이블 생성
- PyMySQL
	- MySQL 연결 드라이버
	- SQLAlchemy URI에서 mysql+pymysql 형태로 사용

### 3) 템플릿 문법
- Jinja2 (Flask 기본 템플릿 엔진)
	- 변수 출력: {{ ... }}
	- 제어문/지시문: {% ... %}
	- 주석: {# ... #}
	- 주요 사용: if, for, set, include, url_for

### 4) 파일/문서 처리
- openpyxl
	- 동아리원 정보 엑셀 파일 생성 및 다운로드 처리

### 5) 보안/암호화 관련
- cryptography
	- 현재 코드에서 직접 import 하지는 않음
	- MySQL 인증 방식(예: caching_sha2_password) 환경에서 PyMySQL과 함께 필요할 수 있는 보조 의존성

### 6) 파이썬 표준 라이브러리
- datetime, os, sys, csv, io.BytesIO, urllib.parse.quote_plus

## 권장 설치 패키지

아래 패키지를 설치하면 현재 프로젝트 실행에 필요한 핵심 의존성을 갖출 수 있습니다.

- flask
- flask-sqlalchemy
- pymysql
- openpyxl
- cryptography

## 프로젝트 구조

```
.
├── app.py              # 앱 진입점, Blueprint 등록
├── config.py           # DB/시크릿 키 등 환경설정
├── models/             # SQLAlchemy 모델 (user, club, board, meeting 등)
├── routes/             # Blueprint 라우터 (auth, board, club, meeting, mypage, promtion, check)
├── templates/          # Jinja2 HTML 템플릿
├── static/             # CSS / JS / 이미지
│   ├── mainPage_/      # 메인 화면 전용 에셋
│   ├── loginPage_/     # 로그인 화면 전용 에셋
│   └── registerPage_/  # 회원가입 화면 전용 에셋
└── test_csv/           # 초기 데이터 시드(CSV) 및 적재 스크립트
```

자세한 트리는 `파일구조.txt` 참고.

## 실행 방법

```bash
# 가상환경 (선택)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 의존성 설치
pip install flask flask-sqlalchemy pymysql openpyxl cryptography

# config.py 의 DB 접속 정보를 환경에 맞게 수정한 뒤 실행
python app.py
```

## HTTP 상태 코드

```
200: 성공
201: 생성 성공(회원가입처럼 새 리소스 생성)
400: 잘못된 요청(사용자 입력 오류, 중복 아이디 등)
401: 인증 필요/로그인 실패
403: 권한 없음
404: 대상 없음
500: 서버 내부 오류
```
