from flask import Blueprint, request, session, jsonify
from flask import render_template, redirect, url_for

from models import db, User, ClubApplication, Club
from routes.ai_generated.executive_room_sync import _sync_executive_meeting_room

auth_bp = Blueprint('auth', __name__, url_prefix='/auth') #'auth' 네임스페이스 정의 (이 파일의 모든 주소 앞에 자동으로 /auth가 붙음)
#해당 파일은 회원가입 로그아웃 로그인 담당 라우터 입니다.
#로그인후 세션에 유저 db의 pk를 받는 방식입니다.

#Ai작성


# AI 생성 함수는 분리 파일(routes/ai_generated/executive_room_sync.py)에서 관리

#ai작성 끝 ->회의실이 저의 담당파트가 아니라 ai 썻습니다 관리자가 로그인시 강제로 회장단 조교단 회의실을 강제로 만드는 목적입니다.


#회원가입 라우터 대충 프론트엔드로부터 post 요청시에 데이터 받아서 
@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        message = request.args.get('message', '')
        message_type = request.args.get('type', 'info')
        return render_template('register.html', message=message, message_type=message_type)  # 회원가입 폼 페이지 렌더링
    
    # 프론트에서 넘어온 폼 데이터 받기
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

    # 숫자 아니면 기본값으로 (age 0, grade 1)
    age = int(age_raw) if str(age_raw).isdigit() else 0
    grade = int(grade_raw) if str(grade_raw).isdigit() else 1

    # 아이디/학번 중복이면 막기
    if User.query.filter_by(user_id=user_id).first():
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."}), 400
        
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({"success": False, "message": "이미 가입된 학번입니다."}), 400

    # db에 던지기
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


    return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 201






#로그인 라우터 -> 프론트엔드에서 post 요청시에 데이터 받아서 db에서 아이디 패스워드 일치하는지 확인하고 세션 발급
@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        message = request.args.get('message', '')
        message_type = request.args.get('type', 'info')
        next_url = request.args.get('next', '')
        return render_template('login.html', message=message, message_type=message_type, next_url=next_url)  # 로그인 폼 페이지 렌더링
    
    input_id = request.form.get('user_id')#프론트엔드에서 받기
    input_pwd = request.form.get('password')

    user = User.query.filter_by(user_id=input_id).first()#db에서 가져오기

    if user and user.password == input_pwd:#평문 비교임 암호화 해야할듯

        session['id'] = user.user_id#세션에 아이디 저장 중요! 앞으로 여기서 가져와서 db에 접근

        if user.role_level >= 40:
            _sync_executive_meeting_room(user)#ai가 작성한 함수입니다. 회장단 조교단 회의실을 강제로 만드는 목적입니다.
        
        return jsonify({"success": True, "message": f"{user.name}, 로그인 성공", "redirect_url": '/'}), 200
    else:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401
    


    
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()#세션 날려버림
    return redirect(url_for('auth.login', message='로그아웃 되었습니다.', type='info'))