from flask import Blueprint, request, session, jsonify
from flask import render_template, redirect, url_for
from datetime import datetime

from models import db, User, ClubApplication, Club, MeetingRoom, MeetingRoomMember, MeetingRoomInvite

auth_bp = Blueprint('auth', __name__, url_prefix='/auth') #'auth' 네임스페이스 정의 (이 파일의 모든 주소 앞에 자동으로 /auth가 붙음)
#Ai작성
EXECUTIVE_ROOM_NAME = '회장단-관리자 공용 회의실'


def _sync_executive_meeting_room(login_user):
    if login_user.role_level < 40:
        return

    room = (
        MeetingRoom.query
        .filter_by(room_name=EXECUTIVE_ROOM_NAME, status='active')
        .order_by(MeetingRoom.id.asc())
        .first()
    )

    if room is None:
        room = MeetingRoom(
            room_name=EXECUTIVE_ROOM_NAME,
            description='권한 30 이상 전용 자동 관리 회의실',
            created_by=login_user.id,
            status='active',
        )
        db.session.add(room)
        db.session.flush()

        owner_member = MeetingRoomMember(
            room_id=room.id,
            user_id=login_user.id,
            role='owner',
            is_active=True,
        )
        db.session.add(owner_member)

    # 로그인한 40 권한 사용자는 방에 반드시 포함
    current_member = MeetingRoomMember.query.filter_by(room_id=room.id, user_id=login_user.id).first()
    if current_member is None:
        db.session.add(
            MeetingRoomMember(
                room_id=room.id,
                user_id=login_user.id,
                role='member',
                is_active=True,
            )
        )
    else:
        current_member.is_active = True
        current_member.left_at = None

    # 기존 인원 중 30 미만 강퇴(비활성)
    active_members = MeetingRoomMember.query.filter_by(room_id=room.id, is_active=True).all()
    for member in active_members:
        target_user = User.query.get(member.user_id)
        if target_user is None:
            continue
        if target_user.role_level < 30:
            member.is_active = False
            member.left_at = datetime.now()

    # 30 이상 전체 사용자를 강제 초대(즉시 참여 처리)
    leaders = User.query.filter(User.role_level >= 30).all()
    for leader in leaders:
        member_record = MeetingRoomMember.query.filter_by(
            room_id=room.id,
            user_id=leader.id,
        ).first()

        if member_record is None:
            db.session.add(
                MeetingRoomMember(
                    room_id=room.id,
                    user_id=leader.id,
                    role='member',
                    is_active=True,
                )
            )
        else:
            member_record.is_active = True
            member_record.left_at = None

    # 기존 pending 초대는 강제 초대 정책으로 모두 정리
    pending_invites = MeetingRoomInvite.query.filter_by(room_id=room.id, status='pending').all()
    for invite in pending_invites:
        invite.status = 'rejected'

    db.session.commit()

#ai작성 끝
@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        message = request.args.get('message', '')
        message_type = request.args.get('type', 'info')
        return render_template('register.html', message=message, message_type=message_type)  # 회원가입 폼 페이지 렌더링
    
    # 프론트엔드에서 전달된 데이터 저장
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    student_id = request.form.get('student_id')
    name = request.form.get('name')
    age_raw = request.form.get('age', 0)
    phone = request.form.get('phone')
    grade_raw = request.form.get('grade')
    admission_year = request.form.get('admission_year')
    address = request.form.get('address')
    email = request.form.get('email')

    # 정수형 타입 캐스팅 안전장치 (예외 방지)
    age = int(age_raw) if str(age_raw).isdigit() else 0
    grade = int(grade_raw) if str(grade_raw).isdigit() else 1

    # 1. 데이터 무결성 체크 (ID 및 학번 중복 검사)
    if User.query.filter_by(user_id=user_id).first():
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."}), 400
        
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({"success": False, "message": "이미 가입된 학번입니다."}), 400

    # 2. 원자성(Atomicity)을 보장하는 DB 트랜잭션 구역
    try:
        new_user = User(
            user_id=user_id,
            password=password,  # 암호화 해야할듯
            student_id=student_id,
            name=name,
            age=age,
            phone=phone,
            grade=grade,
            admission_year=admission_year,
            address=address,
            email=email
            # belonging_club과 role_level은 기본값이 정이되어있으며 추후 조정함
        )
        db.session.add(new_user)
        db.session.commit()  # 저장
        
        print(new_user)#디버깅 reper 출력
        
        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 201

    except Exception as e:
        db.session.rollback()  # 에러 발생 시 트랜잭션 롤백
        print(f"문제발생함: {e}")
        return jsonify({"success": False, "message": "서버 내부 오류로 가입에 실패했습니다."}), 500







@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        message = request.args.get('message', '')
        message_type = request.args.get('type', 'info')
        next_url = request.args.get('next', '')
        return render_template('login.html', message=message, message_type=message_type, next_url=next_url)  # 로그인 폼 페이지 렌더링
    
    input_id = request.form.get('user_id')
    input_pwd = request.form.get('password')

    # DB 포인터 조회
    user = User.query.filter_by(user_id=input_id).first()

    # 아이디 존재 여부 및 패스워드 일치 확인
    if user and user.password == input_pwd:

        session['id'] = user.user_id

        if user.role_level >= 40:
            try:
                _sync_executive_meeting_room(user)
            except Exception as e:
                db.session.rollback()
                print(f"[회의실 자동정리 실패] {e}")
        
        print(f"세션 발급 완료: {user.name}(Level {user.role_level}) 로그인")
        next_url = request.form.get('next_url', '').strip()
        # 외부 도메인 오픈 리다이렉트 방지: 같은 서버 경로만 허용
        from urllib.parse import urlparse
        if next_url and urlparse(next_url).netloc == '' and next_url.startswith('/'):
            redirect_url = next_url
        else:
            redirect_url = '/'
        return jsonify({"success": True, "message": f"{user.name}님, 환영합니다!", "redirect_url": redirect_url}), 200
    else:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401
    


    
@auth_bp.route('/logout', methods=['GET'])
def logout():
    # 현재 로그인된 유저의 세션 소멸시키기
    session.clear()
    return redirect(url_for('auth.login', message='로그아웃 되었습니다.', type='info'))