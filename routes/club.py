from io import BytesIO #엑셀 파일처리를 위한 임포트
import json

from flask import Blueprint, jsonify, render_template, request, send_file, session, redirect, url_for
from openpyxl import Workbook

from models import db, User, ClubApplication, Club


def _load_post_types(club):
    try:
        loaded = json.loads(club.post_types_json or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        loaded = []

    post_types = []
    for item in loaded:
        text = str(item).strip()
        if text and text not in post_types:
            post_types.append(text)

    return post_types


def _save_post_types(club, post_types):
    cleaned = []
    for item in post_types:
        text = str(item).strip()
        if text and text not in cleaned:
            cleaned.append(text)

    club.post_types_json = json.dumps(cleaned, ensure_ascii=False)


# 동아리 관련 기능 네임스페이스 ('/club')
club_bp = Blueprint('club', __name__, url_prefix='/club')


# 동아리 회장 전용 관리 페이지 조회
@club_bp.route('/admin/club', methods=['GET'])
def club_admin():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return "회장만 접근할 수 있습니다.", 403
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return "소속 동아리를 찾을 수 없습니다.", 404

    applications = (
        ClubApplication.query
        .filter_by(club_id=club.id)
        .order_by(ClubApplication.id.desc())
        .all()
    )

    application_rows = []
    for application in applications:
        applicant = User.query.get(application.user_pk)
        if not applicant:
            continue
        application_rows.append({
            'application': application,
            'applicant': applicant,
        })

    members = (
        User.query
        .filter_by(belonging_club=user.belonging_club)
        .order_by(User.role_level.desc(), User.name.asc())
        .all()
    )

    message = request.args.get('message', '')
    message_type = request.args.get('type', 'info')

    return render_template(
        'admin_club.html',
        user=user,
        club=club,
        post_types=_load_post_types(club),
        applications=application_rows,
        members=members,
        member_count=len(members),
        message=message,
        message_type=message_type,
    )


def _redirect_with_message(message, message_type='info'):
    return redirect(url_for('club.club_admin', message=message, type=message_type))


def _get_president_user():
    user_id = session.get('id')
    if not user_id:
        return None, (jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401)

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return None, (jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 401)

    if user.role_level < 30:
        return None, (jsonify({'success': False, 'message': '회장만 접근할 수 있습니다.'}), 403)

    return user, None


def _is_form_request():
    return request.content_type is not None and 'application/x-www-form-urlencoded' in request.content_type


@club_bp.route('/admin/club/post-types', methods=['GET'])
def get_post_types():
    user, error_response = _get_president_user()
    if error_response:
        return error_response

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    return jsonify({
        'success': True,
        'club': club.name,
        'post_types': _load_post_types(club),
    }), 200


@club_bp.route('/admin/club/post-types/add', methods=['POST'])
def add_post_type():
    user, error_response = _get_president_user()
    if error_response:
        return error_response

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    raw_type = request.form.get('post_type')
    if raw_type is None and request.is_json:
        payload = request.get_json(silent=True) or {}
        raw_type = payload.get('post_type')

    if not raw_type:
        if _is_form_request():
            return _redirect_with_message('추가할 글 유형(post_type)을 입력하세요.', 'error')
        return jsonify({'success': False, 'message': '추가할 글 유형(post_type)을 입력하세요.'}), 400

    post_types = _load_post_types(club)
    new_type = str(raw_type).strip()
    if not new_type or new_type in post_types:
        if _is_form_request():
            return _redirect_with_message('이미 존재하거나 잘못된 글 유형입니다.', 'error')
        return jsonify({'success': False, 'message': '이미 존재하거나 잘못된 글 유형입니다.'}), 400

    post_types.append(new_type)
    _save_post_types(club, post_types)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        if _is_form_request():
            return _redirect_with_message('글 유형 추가 중 오류가 발생했습니다.', 'error')
        return jsonify({'success': False, 'message': '글 유형 추가 중 오류가 발생했습니다.'}), 500

    if _is_form_request():
        print(f"[글유형 추가] {club.name}: {_load_post_types(club)}")
        return _redirect_with_message('글 유형이 추가되었습니다.', 'success')

    print(f"[글유형 추가] {club.name}: {_load_post_types(club)}")
    return jsonify({
        'success': True,
        'message': '글 유형이 추가되었습니다.',
        'post_types': _load_post_types(club),
    }), 200


@club_bp.route('/admin/club/post-types/delete', methods=['POST'])
def delete_post_type():
    user, error_response = _get_president_user()
    if error_response:
        return error_response

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    raw_type = request.form.get('post_type')
    if raw_type is None and request.is_json:
        payload = request.get_json(silent=True) or {}
        raw_type = payload.get('post_type')

    if not raw_type:
        if _is_form_request():
            return _redirect_with_message('삭제할 글 유형(post_type)을 입력하세요.', 'error')
        return jsonify({'success': False, 'message': '삭제할 글 유형(post_type)을 입력하세요.'}), 400

    target_type = str(raw_type).strip()
    current_types = _load_post_types(club)
    if target_type not in current_types:
        if _is_form_request():
            return _redirect_with_message('해당 글 유형이 존재하지 않습니다.', 'error')
        return jsonify({'success': False, 'message': '해당 글 유형이 존재하지 않습니다.'}), 404

    current_types.remove(target_type)
    _save_post_types(club, current_types)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        if _is_form_request():
            return _redirect_with_message('글 유형 삭제 중 오류가 발생했습니다.', 'error')
        return jsonify({'success': False, 'message': '글 유형 삭제 중 오류가 발생했습니다.'}), 500

    if _is_form_request():
        print(f"[글유형 삭제] {club.name}: {_load_post_types(club)}")
        return _redirect_with_message('글 유형이 삭제되었습니다.', 'success')

    print(f"[글유형 삭제] {club.name}: {_load_post_types(club)}")
    return jsonify({
        'success': True,
        'message': '글 유형이 삭제되었습니다.',
        'post_types': _load_post_types(club),
    }), 200


# 동아리 가입 신청 승인 처리
@club_bp.route('/admin/club/application/<int:application_id>/approve', methods=['POST'])
def approve_application(application_id):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return _redirect_with_message("회장만 접근할 수 있습니다.", 'error')
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    application = ClubApplication.query.get(application_id)
    if not application:
        return _redirect_with_message("신청 내역을 찾을 수 없습니다.", 'error')
    club = Club.find_by_name(user.belonging_club)
    if not club or application.club_id != club.id:
        return _redirect_with_message("해당 신청을 처리할 권한이 없습니다.", 'error')

    applicant = User.query.get(application.user_pk)
    if not applicant:
        return _redirect_with_message("신청한 사용자를 찾을 수 없습니다.", 'error')

    try:
        applicant.belonging_club = user.belonging_club
        applicant.role_level = 10
        db.session.delete(application)
        db.session.commit()
        return _redirect_with_message(f"{applicant.name}님의 가입이 승인되었습니다.", 'success')
    except Exception:
        db.session.rollback()
        return _redirect_with_message("승인 처리 중 오류가 발생했습니다.", 'error')


# 동아리 가입 신청 반려 처리
@club_bp.route('/admin/club/application/<int:application_id>/reject', methods=['POST'])
def reject_application(application_id):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return _redirect_with_message("회장만 접근할 수 있습니다.", 'error')
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    application = ClubApplication.query.get(application_id)
    if not application:
        return _redirect_with_message("신청 내역을 찾을 수 없습니다.", 'error')
    club = Club.find_by_name(user.belonging_club)
    if not club or application.club_id != club.id:
        return _redirect_with_message("해당 신청을 처리할 권한이 없습니다.", 'error')

    reject_reason = request.form.get('memo2', '').strip()
    if not reject_reason:
        reject_reason = '심사 결과 반려'

    try:
        application.status = 'REJECTED'
        application.memo2 = reject_reason
        db.session.commit()
        return _redirect_with_message("신청이 반려되었습니다.", 'success')
    except Exception:
        db.session.rollback()
        return _redirect_with_message("반려 처리 중 오류가 발생했습니다.", 'error')


# 동아리원을 간부로 임명 처리
@club_bp.route('/admin/club/member/<int:user_pk>/promote/member', methods=['POST'])
def promote_member(user_pk):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return _redirect_with_message("회장만 접근할 수 있습니다.", 'error')
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    target_user = User.query.get(user_pk)
    if not target_user:
        return _redirect_with_message("대상 사용자를 찾을 수 없습니다.", 'error')
    if target_user.belonging_club != user.belonging_club:
        return _redirect_with_message("같은 동아리원만 변경할 수 있습니다.", 'error')
    if target_user.role_level >= 40:
        return _redirect_with_message("권한 40 사용자는 간부로 변경할 수 없습니다.", 'error')

    try:
        target_user.role_level = 20
        db.session.commit()
        return _redirect_with_message(f"{target_user.name}님이 간부로 임명되었습니다.", 'success')
    except Exception:
        db.session.rollback()
        return _redirect_with_message("간부 임명 중 오류가 발생했습니다.", 'error')


# 동아리원을 회장으로 위임 처리
@club_bp.route('/admin/club/member/<int:user_pk>/promote/president', methods=['POST'])
def promote_president(user_pk):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return _redirect_with_message("회장만 접근할 수 있습니다.", 'error')
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    target_user = User.query.get(user_pk)
    if not target_user:
        return _redirect_with_message("대상 사용자를 찾을 수 없습니다.", 'error')
    if target_user.belonging_club != user.belonging_club:
        return _redirect_with_message("같은 동아리원만 변경할 수 있습니다.", 'error')
    if target_user.id == user.id:
        return _redirect_with_message("자기 자신을 회장으로 다시 임명할 수 없습니다.", 'error')
    if target_user.role_level >= 40:
        return _redirect_with_message("권한 40 사용자는 회장으로 변경할 수 없습니다.", 'error')

    try:
        previous_presidents = (
            User.query
            .filter(
                User.belonging_club == user.belonging_club,
                User.role_level == 30,
                User.id != target_user.id,
            )
            .all()
        )
        for president in previous_presidents:
            president.role_level = 10

        if user.role_level == 30:
            user.role_level = 10
        target_user.role_level = 30
        db.session.commit()
        return _redirect_with_message(f"{target_user.name}님이 회장으로 임명되었습니다.", 'success')
    except Exception:
        db.session.rollback()
        return _redirect_with_message("회장 임명 중 오류가 발생했습니다.", 'error')


# 동아리원 정보 엑셀 다운로드
@club_bp.route('/admin/club/export', methods=['POST'])
def club_excel():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if user.role_level < 30:
        return _redirect_with_message("회장만 접근할 수 있습니다.", 'error')
    # ----------------------------------------
    # 권한 확인: 로그인, 사용자 DB, 회장 확인

    selected_fields = request.form.getlist('fields')
    if not selected_fields:
        selected_fields = [
            'user_id', 'student_id', 'name', 'age', 'phone', 'grade',
            'admission_year', 'address', 'email', 'off', 'role_level', 'belonging_club'
        ]

    field_labels = {
        'user_id': '아이디',
        'student_id': '학번',
        'name': '이름',
        'age': '나이',
        'phone': '휴대폰번호',
        'grade': '학년',
        'admission_year': '입학년도',
        'address': '주소',
        'email': '이메일',
        'off': '휴학여부',
        'role_level': '권한레벨',
        'belonging_club': '동아리',
    }

    members = (
        User.query
        .filter_by(belonging_club=user.belonging_club)
        .order_by(User.role_level.desc(), User.name.asc())
        .all()
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Club Members'
    sheet.append([field_labels[field] for field in selected_fields])

    for member in members:
        sheet.append([getattr(member, field) for field in selected_fields])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    file_name = f"{user.belonging_club}_members.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=file_name,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )