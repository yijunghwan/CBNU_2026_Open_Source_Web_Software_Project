# CBNU_2026_Open_Source_Web_Software_Project

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