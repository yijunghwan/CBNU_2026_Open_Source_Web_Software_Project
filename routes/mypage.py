from flask import Blueprint, jsonify, render_template, render_template_string, session, redirect, url_for, request
from models import User, ClubApplication, Club, db

mypage_bp = Blueprint('mypage', __name__, url_prefix='/user')


def alert_redirect(message, endpoint='mypage.my_page'):
    # alert 한 번 띄우고 마이페이지로 보내는 용도. GET으로 잘못 들어온 ajax 전용 라우트 막을 때 씀
    return render_template_string(
        """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>알림</title></head>
<body>
<script>
    alert({{ message|tojson }});
    window.location.href = {{ redirect_url|tojson }};
</script>
</body>
</html>
        """,
        message=message,
        redirect_url=url_for(endpoint),
    )


# 로그인 상태 확인. ajax 요청이면 json_mode=True 줘서 401 json으로 막음
def get_login_user(json_mode=False):
    user_id = session.get('id')
    if not user_id:
        if json_mode:
            return None, (jsonify({"success": False, "message": "로그인이 필요합니다."}), 401)
        return None, redirect(url_for('auth.login', message='로그인이 필요합니다.', type='error'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        if json_mode:
            return None, (jsonify({"success": False, "message": "사용자 정보를 찾을 수 없습니다."}), 401)
        return None, redirect(url_for('auth.login', message='사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.', type='error'))

    return user, None



@mypage_bp.route('/mypage')
def my_page():
    user, err = get_login_user()
    if err:
        return err

    message = request.args.get('message', '')
    message_type = request.args.get('type', 'info')

    posts = []
    comments = []

    if user.role_level >= 30:
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()
        return render_template('mypage_30.html', user=user, posts=posts, comments=comments, count=member_count, message=message, message_type=message_type)
    elif user.role_level >= 10 and user.belonging_club != 'N':
        member_count = User.query.filter_by(belonging_club=user.belonging_club).count()
        return render_template('mypage_10.html', user=user, posts=posts, comments=comments, count=member_count, message=message, message_type=message_type)
    else:
        application = ClubApplication.query.filter_by(user_pk=user.id).first()
        applying_club_name = Club.query.get(application.club_id).name if application else None
        return render_template('mypage_0.html', user=user, posts=posts, comments=comments,
                       application=application, club_name=applying_club_name,
                       message=message, message_type=message_type)


# 레벨 0(소속 없는 사람)이 동아리 가입 신청하는 곳
@mypage_bp.route('/apply_0', methods=['GET', 'POST'])
def apply_club():
    user, err = get_login_user()
    if err:
        return err

    if user.role_level >= 10 or user.belonging_club != 'N':
        if request.method == 'GET':
            return alert_redirect("이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다.")
        return jsonify({"success": False, "message": "이미 동아리에 소속되어 있어 가입 신청을 할 수 없습니다."}), 403

    existing_app = ClubApplication.query.filter_by(user_pk=user.id).first()
    if existing_app and existing_app.status == 'PENDING':
        if request.method == 'GET':
            return alert_redirect("이미 가입 심사 대기 중인 동아리가 있습니다. 결과를 기다려주세요.")
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
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"success": True, "message": "성공적으로 가입 신청이 접수되었습니다!"}), 201


# 가입 신청 취소
@mypage_bp.route('/cancel_apply_0', methods=['POST'])
def cancel_apply():
    user, err = get_login_user(json_mode=True)
    if err:
        return err

    if user.role_level >= 10 or user.belonging_club != 'N':
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    application = ClubApplication.query.filter_by(user_pk=user.id).first()
    if not application:
        return jsonify({"success": False, "message": "취소할 가입 신청 내역이 없습니다."}), 404

    db.session.delete(application)
    db.session.commit()
    return jsonify({"success": True, "message": "가입 신청이 정상적으로 취소되었습니다."}), 200


# 반려된 신청 내역 목록에서 지우기
@mypage_bp.route('/apply_cancel_0', methods=['POST'])
def clear_rejection():
    user, err = get_login_user(json_mode=True)
    if err:
        return err

    if user.role_level >= 10 or user.belonging_club != 'N':
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    rejected_app = (
        ClubApplication.query
        .filter_by(user_pk=user.id, status='REJECTED')
        .order_by(ClubApplication.id.desc())
        .first()
    )
    if not rejected_app:
        return jsonify({"success": False, "message": "삭제할 반려 내역이 없습니다."}), 404

    db.session.delete(rejected_app)
    db.session.commit()
    return jsonify({"success": True, "message": "반려 내역을 확인했고 목록에서 제거했습니다."}), 200


# 동아리원/간부 탈퇴. 회장과 관리자(40이상)은 이 경로로 못 나감
@mypage_bp.route('/leave_club_10', methods=['POST'])
def leave_club():
    user, err = get_login_user(json_mode=True)
    if err:
        return err

    if user.role_level >= 40:
        return jsonify({"success": False, "message": "권한 40 이상 사용자는 탈퇴 기능을 사용할 수 없습니다."}), 403
    if user.role_level == 0 or user.belonging_club == 'N':
        return jsonify({"success": False, "message": "소속된 동아리가 없습니다."}), 400
    if user.role_level >= 30:
        return jsonify({"success": False, "message": "회장은 동아리를 바로 탈퇴할 수 없습니다. 직위를 먼저 위임하세요."}), 403
    if user.role_level < 10:
        return jsonify({"success": False, "message": "잘못된 접근입니다."}), 403

    old_club = user.belonging_club
    user.belonging_club = 'N'
    user.role_level = 0
    db.session.commit()
    return jsonify({"success": True, "message": f"{old_club} 동아리에서 정상적으로 탈퇴되었습니다."}), 200


@mypage_bp.route('/change_info', methods=['GET', 'POST'])
def change_info():
    user, err = get_login_user()
    if err:
        return err

    is_verified = session.get('change_info_verified', False)
    clubs = Club.query.order_by(Club.name.asc()).all()
    club_names = [club.name for club in clubs]

    if request.method == 'GET':
        return render_template('change_info.html', user=user, verified=is_verified, club_names=club_names)

    if not is_verified:
        password = request.form.get('password', '')
        if user.password != password:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."}), 401
        session['change_info_verified'] = True
        return jsonify({"success": True, "message": "비밀번호 확인 완료", "redirect": url_for('mypage.change_info')}), 200

    name = request.form.get('name', '').strip()
    age_raw = request.form.get('age', '').strip()
    phone = request.form.get('phone', '').strip()
    grade_raw = request.form.get('grade', '').strip()
    admission_year_raw = request.form.get('admission_year', '').strip()
    address = request.form.get('address', '').strip()
    email = request.form.get('email', '').strip()
    off_raw = request.form.get('off', '0').strip()
    belonging_club_raw = request.form.get('belonging_club', '').strip()

    if not (age_raw.isdigit() and grade_raw.isdigit() and admission_year_raw.isdigit() and off_raw in ('0', '1')):
        return jsonify({"success": False, "message": "나이/학년/입학년도/휴학여부 값이 올바르지 않습니다."}), 400

    user.name = name
    user.age = int(age_raw)
    user.phone = phone
    user.grade = int(grade_raw)
    user.admission_year = int(admission_year_raw)
    user.address = address
    user.email = email
    user.off = int(off_raw)

    if user.role_level >= 40:
        if not belonging_club_raw:
            return jsonify({"success": False, "message": "동아리 값을 입력하세요."}), 400
        if belonging_club_raw != 'N' and belonging_club_raw not in club_names:
            return jsonify({"success": False, "message": "유효하지 않은 동아리 값입니다."}), 400
        user.belonging_club = belonging_club_raw

    db.session.commit()
    session.pop('change_info_verified', None)
    return jsonify({"success": True, "message": "정보가 성공적으로 업데이트되었습니다!"}), 200