from flask import Blueprint, jsonify, render_template, render_template_string, session, redirect, url_for, request
from models import User, ClubApplication, Club, db

mypage_bp = Blueprint('mypage', __name__, url_prefix='/user')



#팝업 압림창 용
def _alert_and_redirect(message, redirect_endpoint='mypage.my_page'):
    return render_template_string(
        """
<!DOCTYPE html>
<html>
<head><meta charset=\"UTF-8\"><title>알림</title></head>
<body>
<script>
    alert({{ message|tojson }});
    window.location.href = {{ redirect_url|tojson }};
</script>
</body>
</html>
        """,
        message=message,
        redirect_url=url_for(redirect_endpoint),
    )


@mypage_bp.route('/mypage')
def my_page():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login', message='사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.', type='error'))

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB 확인

    message = request.args.get('message', '')
    message_type = request.args.get('type', 'info')

    #추후 여기에 내가 쓴글 관련 데이터도 받아와야함
    posts = []
    comments = []

    # 권한별 분기 및 전용 HTML 렌더링
    if user.role_level >= 30:
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()#동아리 정보 출력을 위하여
        return render_template('mypage_30.html', user=user, posts=posts, comments=comments, count=member_count, message=message, message_type=message_type)
        
    elif user.role_level >= 10 and user.belonging_club != 'N':
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()#동아리 정보 출력을 위하여2
        return render_template('mypage_10.html', user=user, posts=posts, comments=comments, count=member_count, message=message, message_type=message_type)
        
    else:
        application = ClubApplication.query.filter_by(user_pk=user.id).first()#가입 신청내역 출력을 위하여
        applying_club_name = Club.query.get(application.club_id).name if application else None#가입 신청한 동아리가 있으면 이름을, 없으면 None을 넘겨줌 프론트엔드에서 none이면 가입 신청내역 없다고 해야할듯
        
        return render_template('mypage_0.html', user=user, posts=posts, comments=comments,
                       application=application, club_name=applying_club_name,
                       message=message, message_type=message_type)



# 비동아리원(0) 전용 동아리 가입 신청
@mypage_bp.route('/apply_0', methods=['GET', 'POST'])
def apply_club_0():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login', message='사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.', type='error'))

    if user.role_level >= 10 or user.belonging_club != 'N':
        if request.method == 'GET':
            return _alert_and_redirect("이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다.")
        return jsonify({"success": False, "message": "이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다."}), 403

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 비동아리원 확인

    existing_app = ClubApplication.query.filter_by(user_pk=user.id).first()
    if existing_app and existing_app.status == 'PENDING':
        if request.method == 'GET':
            return _alert_and_redirect("이미 가입 심사 대기 중인 동아리가 있습니다. 결과를 기다려주세요.")
        return jsonify({"success": False, "message": "이미 가입 심사 대기 중인 동아리가 있습니다. 결과를 기다려주세요."}), 400

    if request.method == 'GET':
        clubs = Club.query.all()
        return render_template('apply.html', user=user, clubs=clubs)

    club_id = request.form.get('club_id')
    memo = request.form.get('memo')

    new_app = ClubApplication(
        user_pk=user.id,
        club_id=int(club_id),
        status='PENDING',
        memo=memo
    )

    try:
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"success": True, "message": "성공적으로 가입 신청이 접수되었습니다!"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 신청에 실패했습니다."}), 500


# 비동아리원전용 가입 신청 취소
@mypage_bp.route('/cancel_apply_0', methods=['POST'])
def cancel_apply_0():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return jsonify({"success": False, "message": "사용자 정보를 찾을 수 없습니다."}), 401

    if user.role_level >= 10 or user.belonging_club != 'N':
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 비동아리원 확인

    application = ClubApplication.query.filter_by(user_pk=user.id).first()
    
    if not application:
        return jsonify({"success": False, "message": "취소할 가입 신청 내역이 없습니다."}), 404

    try:
        db.session.delete(application)  
        db.session.commit()             
        return jsonify({"success": True, "message": "가입 신청이 정상적으로 취소되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 취소에 실패했습니다."}), 500


# 비동아리원 전용 반려 내역 확인(삭제)
@mypage_bp.route('/apply_cancel_0', methods=['POST'])
def apply_cancel_0():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return jsonify({"success": False, "message": "사용자 정보를 찾을 수 없습니다."}), 401

    if user.role_level >= 10 or user.belonging_club != 'N':
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 비동아리원 확인

    rejected_app = (
        ClubApplication.query
        .filter_by(user_pk=user.id, status='REJECTED')
        .order_by(ClubApplication.id.desc())
        .first()
    )

    if not rejected_app:
        return jsonify({"success": False, "message": "삭제할 반려 내역이 없습니다."}), 404

    try:
        db.session.delete(rejected_app)
        db.session.commit()
        return jsonify({"success": True, "message": "반려 내역을 확인했고 목록에서 제거했습니다."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 처리에 실패했습니다."}), 500



# 동아리원/간부 전용 동아리 탈퇴
@mypage_bp.route('/leave_club_10', methods=['POST'])
def leave_club_10():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return jsonify({"success": False, "message": "사용자 정보를 찾을 수 없습니다."}), 401

    if user.role_level == 0 or user.belonging_club == 'N':
        return jsonify({"success": False, "message": "소속된 동아리가 없습니다."}), 400
    if user.role_level >= 30:
        return jsonify({"success": False, "message": "회장은 동아리를 바로 탈퇴할 수 없습니다. 직위를 먼저 위임하세요."}), 403

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 동아리원/간부 확인(회장 제외)

    # 간부/동아리원만 탈퇴 가능
    if user.role_level < 10:
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    # 핵심 연산: 동아리 소속을 'N'으로 바꾸고 권한을 0(비동아리원)으로 강등
    try:
        old_club = user.belonging_club # 탈퇴 메시지용으로 잠시 저장
        
        user.belonging_club = 'N'
        user.role_level = 0
        
        db.session.commit() # 변경사항 DB 저장
        return jsonify({"success": True, "message": f"{old_club} 동아리에서 정상적으로 탈퇴되었습니다."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 탈퇴 처리에 실패했습니다."}), 500
    


@mypage_bp.route('/change_info', methods=['GET', 'POST'])
def change_info():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login', message='사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.', type='error'))

    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB 확인

    is_verified = session.get('change_info_verified', False)

    #일단 get요청수행
    if request.method == 'GET':
        return render_template('change_info.html', user=user, verified=is_verified)

    # 정보 수정 진입 전 비밀번호 재확인
    if not is_verified:
        password = request.form.get('password', '')
        if user.password != password:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."}), 401

        session['change_info_verified'] = True
        return jsonify({"success": True, "message": "비밀번호 확인 완료", "redirect": url_for('mypage.change_info')}), 200

    #정보 변경 프론트엔드에서 받아오기 strip으로 공백제거
    name = request.form.get('name', '').strip()
    age_raw = request.form.get('age', '').strip()
    phone = request.form.get('phone', '').strip()
    grade_raw = request.form.get('grade', '').strip()
    admission_year_raw = request.form.get('admission_year', '').strip()
    address = request.form.get('address', '').strip()
    email = request.form.get('email', '').strip()
    off_raw = request.form.get('off', '0').strip()

    if not (age_raw.isdigit() and grade_raw.isdigit() and admission_year_raw.isdigit() and off_raw in ('0', '1')):
        return jsonify({"success": False, "message": "나이/학년/입학년도/휴학여부 값이 올바르지 않습니다."}), 400

    try:
        user.name = name
        user.age = int(age_raw)
        user.phone = phone
        user.grade = int(grade_raw)
        user.admission_year = int(admission_year_raw)
        user.address = address
        user.email = email
        user.off = int(off_raw)
        
        db.session.commit()
        session.pop('change_info_verified', None)
        return jsonify({"success": True, "message": "정보가 성공적으로 업데이트되었습니다!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "서버 오류로 정보 업데이트에 실패했습니다."}), 500