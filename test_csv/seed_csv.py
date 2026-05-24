import os
import sys
import csv

# ==========================================
# 🌟 [핵심] 폴더 경로 및 모듈 인식 문제 해결
# ==========================================
# 1. 현재 스크립트가 있는 폴더(test_csv)와 최상단 부모 폴더의 절대 경로를 계산합니다.
current_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(current_folder)

# 2. 파이썬이 app.py와 models 폴더를 찾을 수 있도록 시스템 경로에 최상단 폴더를 추가합니다.
sys.path.append(root_folder)

# 3. SQLite DB 파일이 원래 있던 최상단에 정상적으로 연결되도록, 실행 위치를 최상단으로 강제 이동합니다.
os.chdir(root_folder)

# 이제 에러 없이 부모 폴더의 모듈을 가져올 수 있습니다!
from app import app
from models import db, User, Club, ClubApplication


def seed_from_csv():
    with app.app_context():
        print("🧹 기존 데이터베이스를 초기화합니다...")
        db.drop_all()
        db.create_all()

        print("🏢 동아리 3개(EMSYS, RCV, GDSC)를 생성합니다...")
        clubs = {
            'EMSYS': Club(name='EMSYS'),
            'RCV': Club(name='RCV'),
            'GDSC': Club(name='GDSC')
        }
        db.session.add_all(clubs.values())
        db.session.commit()

        # CSV 파일들이 test_csv 폴더 안에 있으므로, 절대 경로를 합쳐서 열어줍니다.
        users_csv_path = os.path.join(current_folder, 'users.csv')
        apps_csv_path = os.path.join(current_folder, 'apps.csv')

        print("👥 users.csv 파일을 읽어 18명의 유저를 주입합니다...")
        with open(users_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user = User(
                    user_id=row['user_id'],
                    password=row['password'],
                    student_id=row['student_id'],
                    name=row['name'],
                    age=int(row['age']),
                    phone=row['phone'],
                    grade=int(row['grade']),
                    admission_year=int(row['admission_year']),
                    address=row['address'],
                    email=row['email'],
                    belonging_club=row['belonging_club'],
                    role_level=int(row['role_level'])
                )
                db.session.add(user)
        db.session.commit()

        print("📝 apps.csv 파일을 읽어 가입 신청 내역을 주입합니다...")
        with open(apps_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user = User.query.filter_by(user_id=row['applicant_id']).first()
                club = Club.query.filter_by(name=row['target_club']).first()
                
                if user and club:
                    app_record = ClubApplication(
                        user_pk=user.id,
                        club_id=club.id,
                        status=row['status'],
                        memo=row['memo']
                    )
                    db.session.add(app_record)
        db.session.commit()

        print("🌟 CSV 대량 데이터 주입이 완벽하게 완료되었습니다!")

if __name__ == '__main__':
    seed_from_csv()