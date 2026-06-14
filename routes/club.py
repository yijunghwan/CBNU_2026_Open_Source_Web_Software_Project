from io import BytesIO  # 엑셀 파일처리를 위한 임포트
import json

from flask import Blueprint, jsonify, render_template, request, send_file, session, redirect, url_for
from openpyxl import Workbook

from models import db, User, ClubApplication, Club


def load_post_types(club):
    try:
        types = json.loads(club.post_types_json or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        types = []
    return list(dict.fromkeys(t.strip() for t in types if t.strip()))


def save_post_types(club, post_types):
    cleaned = list(dict.fromkeys(t.strip() for t in post_types if t.strip()))
    club.post_types_json = json.dumps(cleaned, ensure_ascii=False)


club_bp = Blueprint('club', __name__, url_prefix='/club')


def msg_redirect(message, message_type='info'):
    return redirect(url_for('club.club_admin', message=message, type=message_type))


# 회장(레벨 30 이상)인지 확인하는 용도.
# ajax 요청이면 json_mode=True 줘서 json으로 막고, 일반 페이지는 그냥 리다이렉트
def check_president(json_mode=False):
    user_id = session.get('id')
    if not user_id:
        if json_mode:
            return None, (jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401)
        return None, redirect(url_for('auth.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        if json_mode:
            return None, (jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 401)
        return None, redirect(url_for('auth.login'))

    if user.role_level < 30:
        if json_mode:
            return None, (jsonify({'success': False, 'message': '회장만 접근할 수 있습니다.'}), 403)
        return None, msg_redirect("회장만 접근할 수 있습니다.", 'error')

    return user, None


# 회장 관리 페이지. 여기서 자기 자신으로 리다이렉트하면 무한루프라 인증을 직접 풀어씀
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
        post_types=load_post_types(club),
        applications=application_rows,
        members=members,
        member_count=len(members),
        message=message,
        message_type=message_type,
    )


@club_bp.route('/admin/club/post-types', methods=['GET'])
def get_post_types():
    user, err = check_president(json_mode=True)
    if err:
        return err

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    return jsonify({
        'success': True,
        'club': club.name,
        'post_types': load_post_types(club),
    }), 200


@club_bp.route('/admin/club/post-types/add', methods=['POST'])
def add_post_type():
    user, err = check_president(json_mode=True)
    if err:
        return err

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    raw_type = request.form.get('post_type')
    if raw_type is None and request.is_json:
        raw_type = (request.get_json(silent=True) or {}).get('post_type')

    is_form = 'application/x-www-form-urlencoded' in (request.content_type or '')
    if not raw_type:
        if is_form:
            return msg_redirect('추가할 글 유형(post_type)을 입력하세요.', 'error')
        return jsonify({'success': False, 'message': '추가할 글 유형(post_type)을 입력하세요.'}), 400

    new_type = raw_type.strip()
    post_types = load_post_types(club)
    if not new_type or new_type in post_types:
        if is_form:
            return msg_redirect('이미 존재하거나 잘못된 글 유형입니다.', 'error')
        return jsonify({'success': False, 'message': '이미 존재하거나 잘못된 글 유형입니다.'}), 400

    post_types.append(new_type)
    save_post_types(club, post_types)
    db.session.commit()

    print(f"[글유형 추가] {club.name}: {load_post_types(club)}")
    if is_form:
        return msg_redirect('글 유형이 추가되었습니다.', 'success')
    return jsonify({'success': True, 'message': '글 유형이 추가되었습니다.', 'post_types': load_post_types(club)}), 200


@club_bp.route('/admin/club/post-types/delete', methods=['POST'])
def delete_post_type():
    user, err = check_president(json_mode=True)
    if err:
        return err

    club = Club.find_by_name(user.belonging_club)
    if not club:
        return jsonify({'success': False, 'message': '소속 동아리를 찾을 수 없습니다.'}), 404

    raw_type = request.form.get('post_type')
    if raw_type is None and request.is_json:
        raw_type = (request.get_json(silent=True) or {}).get('post_type')

    is_form = 'application/x-www-form-urlencoded' in (request.content_type or '')
    if not raw_type:
        if is_form:
            return msg_redirect('삭제할 글 유형(post_type)을 입력하세요.', 'error')
        return jsonify({'success': False, 'message': '삭제할 글 유형(post_type)을 입력하세요.'}), 400

    target_type = raw_type.strip()
    current_types = load_post_types(club)
    if target_type not in current_types:
        if is_form:
            return msg_redirect('해당 글 유형이 존재하지 않습니다.', 'error')
        return jsonify({'success': False, 'message': '해당 글 유형이 존재하지 않습니다.'}), 404

    current_types.remove(target_type)
    save_post_types(club, current_types)
    db.session.commit()

    print(f"[글유형 삭제] {club.name}: {load_post_types(club)}")
    if is_form:
        return msg_redirect('글 유형이 삭제되었습니다.', 'success')
    return jsonify({'success': True, 'message': '글 유형이 삭제되었습니다.', 'post_types': load_post_types(club)}), 200


# 가입 신청 승인 -> 신청자를 동아리원(레벨 10)으로 넣어줌
@club_bp.route('/admin/club/application/<int:application_id>/approve', methods=['POST'])
def approve_application(application_id):
    user, err = check_president()
    if err:
        return err

    application = ClubApplication.query.get(application_id)
    if not application:
        return msg_redirect("신청 내역을 찾을 수 없습니다.", 'error')
    club = Club.find_by_name(user.belonging_club)
    if not club or application.club_id != club.id:
        return msg_redirect("해당 신청을 처리할 권한이 없습니다.", 'error')

    applicant = User.query.get(application.user_pk)
    if not applicant:
        return msg_redirect("신청한 사용자를 찾을 수 없습니다.", 'error')

    applicant.belonging_club = user.belonging_club
    applicant.role_level = 10
    db.session.delete(application)
    db.session.commit()
    return msg_redirect(f"{applicant.name}님의 가입이 승인되었습니다.", 'success')


# 가입 신청 반려
@club_bp.route('/admin/club/application/<int:application_id>/reject', methods=['POST'])
def reject_application(application_id):
    user, err = check_president()
    if err:
        return err

    application = ClubApplication.query.get(application_id)
    if not application:
        return msg_redirect("신청 내역을 찾을 수 없습니다.", 'error')
    club = Club.find_by_name(user.belonging_club)
    if not club or application.club_id != club.id:
        return msg_redirect("해당 신청을 처리할 권한이 없습니다.", 'error')

    reject_reason = request.form.get('memo2', '').strip() or '심사 결과 반려'
    application.status = 'REJECTED'
    application.memo2 = reject_reason
    db.session.commit()
    return msg_redirect("신청이 반려되었습니다.", 'success')


# 동아리원 -> 간부
@club_bp.route('/admin/club/member/<int:user_pk>/promote/member', methods=['POST'])
def promote_member(user_pk):
    user, err = check_president()
    if err:
        return err

    target_user = User.query.get(user_pk)
    if not target_user:
        return msg_redirect("대상 사용자를 찾을 수 없습니다.", 'error')
    if target_user.belonging_club != user.belonging_club:
        return msg_redirect("같은 동아리원만 변경할 수 있습니다.", 'error')
    if target_user.role_level >= 40:
        return msg_redirect("권한 40 사용자는 간부로 변경할 수 없습니다.", 'error')

    target_user.role_level = 20
    db.session.commit()
    return msg_redirect(f"{target_user.name}님이 간부로 임명되었습니다.", 'success')


# 다시 일반 회원으로 내리기
@club_bp.route('/admin/club/member/<int:user_pk>/demote', methods=['POST'])
def demote_member(user_pk):
    user, err = check_president()
    if err:
        return err

    target_user = User.query.get(user_pk)
    if not target_user:
        return msg_redirect("대상 사용자를 찾을 수 없습니다.", 'error')
    if target_user.belonging_club != user.belonging_club:
        return msg_redirect("같은 동아리원만 변경할 수 있습니다.", 'error')
    if target_user.role_level >= 40:
        return msg_redirect("권한 40 사용자는 일반 회원으로 변경할 수 없습니다.", 'error')

    target_user.role_level = 10
    db.session.commit()
    return msg_redirect(f"{target_user.name}님이 일반 회원으로 강등되었습니다.", 'success')


# 회장 위임. 위임하면 기존 회장(자기 자신 포함)은 자동으로 일반 회원으로 내려감
@club_bp.route('/admin/club/member/<int:user_pk>/promote/president', methods=['POST'])
def promote_president(user_pk):
    user, err = check_president()
    if err:
        return err

    target_user = User.query.get(user_pk)
    if not target_user:
        return msg_redirect("대상 사용자를 찾을 수 없습니다.", 'error')
    if target_user.belonging_club != user.belonging_club:
        return msg_redirect("같은 동아리원만 변경할 수 있습니다.", 'error')
    if target_user.id == user.id:
        return msg_redirect("자기 자신을 회장으로 다시 임명할 수 없습니다.", 'error')
    if target_user.role_level >= 40:
        return msg_redirect("권한 40 사용자는 회장으로 변경할 수 없습니다.", 'error')

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
    return msg_redirect(f"{target_user.name}님이 회장으로 임명되었습니다.", 'success')


# 동아리원 명단 엑셀로 받기
@club_bp.route('/admin/club/export', methods=['POST'])
def export_members():
    user, err = check_president()
    if err:
        return err

    selected_fields = request.form.getlist('fields') or [
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