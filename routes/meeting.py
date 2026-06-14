from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from datetime import datetime

from models import (
    db,
    User,
    MeetingRoom,
    MeetingRoomMember,
    MeetingRoomInvite,
    MeetingMessage,
)

meeting_bp = Blueprint("meeting", __name__, url_prefix="/meeting")


def get_user():
    login_id = session.get("id")
    if login_id is None:
        return None
    return User.query.filter_by(user_id=login_id).first()


def error_response(message, status_code=400):
    return jsonify({"success": False, "message": message}), status_code


def check_member(room_id, user_id):
    return MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=user_id, is_active=True
    ).first()


def check_owner(room_id, user_id):
    return MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=user_id, role="owner", is_active=True
    ).first()


def get_owner(room_id):
    owner_member = MeetingRoomMember.query.filter_by(
        room_id=room_id, role="owner", is_active=True
    ).first()
    if owner_member is None:
        return None
    return User.query.get(owner_member.user_id)


@meeting_bp.route("/", methods=["GET"])
def meeting_page():
    user = get_user()
    if user is None:
        return redirect(url_for("auth.login", message="로그인이 필요합니다.", type="error"))

    return render_template("meeting_room.html")

@meeting_bp.route("/create", methods=["POST"])
def create_meeting_room():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    if title == "":
        return error_response("방 이름을 입력하세요.")
    room = MeetingRoom(
        room_name=title, description=description, created_by=user.id, status="active"
    )
    db.session.add(room)
    db.session.flush()
    member = MeetingRoomMember(
        room_id=room.id, user_id=user.id, role="owner", is_active=True
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"success": True, "message": "회의실이 생성되었습니다."})


@meeting_bp.route("/my_rooms", methods=["GET"])
def get_my_rooms():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    members = MeetingRoomMember.query.filter_by(user_id=user.id, is_active=True).all()
    result = []
    for member in members:
        room = MeetingRoom.query.get(member.room_id)
        if room is None:
            continue
        if room.status != "active":
            continue
        member_count = MeetingRoomMember.query.filter_by(
            room_id=room.id, is_active=True
        ).count()
        result.append(
            {
                "id": room.id,
                "room_name": room.room_name,
                "description": room.description,
                "member_count": member_count,
                "role": member.role,
            }
        )
    return jsonify(result)


@meeting_bp.route("/invited_rooms", methods=["GET"])
def get_invited_rooms():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    invites = MeetingRoomInvite.query.filter_by(
        invited_user_id=user.id, status="pending"
    ).all()
    result = []
    for invite in invites:
        room = MeetingRoom.query.get(invite.room_id)
        if room is None:
            continue
        if room.status != "active":
            continue
        owner = get_owner(room.id)
        room_members = MeetingRoomMember.query.filter_by(
            room_id=room.id, is_active=True
        ).all()
        members = []
        for member in room_members:
            member_user = User.query.get(member.user_id)
            if member_user is None:
                continue
            members.append(
                {
                    "id": member_user.id,
                    "name": member_user.name,
                    "user_id": member_user.user_id,
                    "role": member.role,
                }
            )
        result.append(
            {
                "id": room.id,
                "room_name": room.room_name,
                "description": room.description,
                "invite_id": invite.id,
                "owner_name": owner.name,
                "member_count": len(members),
                "created_at": room.created_at.strftime("%Y-%m-%d %H:%M"),
                "invite_status": "대기중",
                "members": members,
            }
        )
    return jsonify(result)


@meeting_bp.route("/message", methods=["POST"])
def send_message():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    room_id = data.get("room_id")
    message = data.get("message", "").strip()
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    member = check_member(room_id, user.id)
    if member is None:
        return error_response("권한이 없습니다.", 403)
    chat = MeetingMessage(room_id=room_id, user_id=user.id, message=message)
    db.session.add(chat)
    db.session.commit()
    return jsonify({"success": True, "message": "메시지가 저장되었습니다."})


@meeting_bp.route("/messages/<int:room_id>", methods=["GET"])
def get_messages(room_id):
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    member_record = MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=user.id
    ).first()
    if member_record is None:
        return error_response("권한이 없습니다.", 403)
    if room.status == "active" and member_record.is_active is not True:
        return error_response("권한이 없습니다.", 403)
    last_id = request.args.get("last_id", 0, type=int)
    query = MeetingMessage.query.filter_by(room_id=room_id)
    if last_id > 0:
        query = query.filter(MeetingMessage.id > last_id)
    messages = query.order_by(MeetingMessage.created_at.asc()).all()
    result = []
    for msg in messages:
        message_user = User.query.get(msg.user_id)
        result.append(
            {
                "id": msg.id,
                "message": msg.message,
                "user_name": message_user.name if message_user else "알 수 없음",
                "created_at": msg.created_at.strftime("%H:%M"),
                "is_mine": msg.user_id == user.id,
            }
        )
    return jsonify(result)


@meeting_bp.route("/members/<int:room_id>", methods=["GET"])
def get_room_members(room_id):
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    member_check = MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=user.id
    ).first()
    if member_check is None:
        return error_response("권한이 없습니다.", 403)
    if room.status == "ended":
        members = MeetingRoomMember.query.filter_by(room_id=room_id).all()
    else:
        members = MeetingRoomMember.query.filter_by(
            room_id=room_id, is_active=True
        ).all()
    result = []
    for member in members:
        member_user = User.query.get(member.user_id)
        if member_user is None:
            continue
        result.append(
            {
                "id": member_user.id,
                "name": member_user.name,
                "user_id": member_user.user_id,
                "role": member.role,
            }
        )
    return jsonify(result)


@meeting_bp.route("/search_user/<student_id>", methods=["GET"])
def search_user(student_id):
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    searched_user = User.query.filter_by(student_id=student_id).first()
    if searched_user is None:
        return jsonify(
            {"success": False, "message": "해당 학번의 사용자를 찾을 수 없습니다."}
        )
    return jsonify(
        {"success": True, "id": searched_user.id, "name": searched_user.name}
    )


@meeting_bp.route("/invite", methods=["POST"])
def invite_user():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    room_id = data.get("room_id")
    invited_user_id = data.get("user_id")
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    owner = check_owner(room_id, user.id)
    if owner is None:
        return error_response("방장만 초대할 수 있습니다.", 403)
    already_active_member = MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=invited_user_id, is_active=True
    ).first()
    if already_active_member:
        return error_response("이미 참여 중인 사용자입니다.")
    pending_invite = MeetingRoomInvite.query.filter_by(
        room_id=room_id, invited_user_id=invited_user_id, status="pending"
    ).first()
    if pending_invite:
        return error_response("이미 초대 중인 사용자입니다.")
    invite = MeetingRoomInvite(
        room_id=room_id,
        invited_user_id=invited_user_id,
        invited_by=user.id,
        status="pending",
    )
    db.session.add(invite)
    db.session.commit()
    return jsonify({"success": True, "message": "초대가 완료되었습니다."})


@meeting_bp.route("/invites/<int:room_id>", methods=["GET"])
def get_invites(room_id):
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    member = check_member(room_id, user.id)
    if member is None:
        return error_response("권한이 없습니다.", 403)
    invites = MeetingRoomInvite.query.filter_by(room_id=room_id, status="pending").all()
    result = []
    for invite in invites:
        invited_user = User.query.get(invite.invited_user_id)
        if invited_user is None:
            continue
        result.append(
            {
                "id": invite.id,
                "user_id": invited_user.id,
                "name": invited_user.name,
                "student_id": invited_user.student_id,
                "status": invite.status,
            }
        )
    return jsonify(result)


@meeting_bp.route("/invite/accept", methods=["POST"])
def accept_invite():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    invite_id = data.get("invite_id")
    invite = MeetingRoomInvite.query.get(invite_id)
    if invite is None:
        return error_response("초대 정보를 찾을 수 없습니다.", 404)
    if invite.invited_user_id != user.id:
        return error_response("권한이 없습니다.", 403)
    room = MeetingRoom.query.get(invite.room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    existing_member = MeetingRoomMember.query.filter_by(
        room_id=invite.room_id, user_id=user.id
    ).first()
    invite.status = "accepted"
    if existing_member:
        existing_member.is_active = True
        existing_member.left_at = None
        db.session.commit()
        return jsonify({"success": True, "message": "초대를 수락했습니다."})
    member = MeetingRoomMember(
        room_id=invite.room_id, user_id=user.id, role="member", is_active=True
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"success": True, "message": "초대를 수락했습니다."})


@meeting_bp.route("/invite/reject", methods=["POST"])
def reject_invite():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    invite_id = data.get("invite_id")
    invite = MeetingRoomInvite.query.get(invite_id)
    if invite is None:
        return error_response("초대 정보를 찾을 수 없습니다.", 404)
    if invite.invited_user_id != user.id:
        return error_response("권한이 없습니다.", 403)
    invite.status = "rejected"
    db.session.commit()
    return jsonify({"success": True, "message": "초대를 거절했습니다."})


@meeting_bp.route("/leave", methods=["POST"])
def leave_room():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    room_id = data.get("room_id")
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    member = MeetingRoomMember.query.filter_by(
        room_id=room_id, user_id=user.id, is_active=True
    ).first()
    if member is None:
        return error_response("권한이 없습니다.", 403)
    if member.role == "owner":
        return error_response("방장은 나갈 수 없습니다.", 403)
    member.is_active = False
    member.left_at = datetime.now()
    db.session.commit()
    return jsonify({"success": True, "message": "회의실에서 나갔습니다."})


@meeting_bp.route("/end", methods=["POST"])
def end_room():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)
    data = request.get_json()
    room_id = data.get("room_id")
    room = MeetingRoom.query.get(room_id)
    if room is None:
        return error_response("회의실을 찾을 수 없습니다.", 404)
    owner = check_owner(room_id, user.id)
    if owner is None:
        return error_response("방장만 회의실을 종료할 수 있습니다.", 403)
    room.status = "ended"
    room.ended_at = datetime.now()
    pending_invites = MeetingRoomInvite.query.filter_by(
        room_id=room_id, status="pending"
    ).all()
    for invite in pending_invites:
        invite.status = "rejected"
    db.session.commit()
    return jsonify({"success": True, "message": "회의실이 종료되었습니다."})


@meeting_bp.route("/ended_rooms", methods=["GET"])
def get_history():
    user = get_user()
    if user is None:
        return error_response("로그인이 필요합니다.", 401)

    members = MeetingRoomMember.query.filter_by(user_id=user.id).all()
    result = []
    for member in members:
        room = MeetingRoom.query.get(member.room_id)
        if room is None:
            continue
        if room.status != "ended":
            continue
        result.append(
            {
                "id": room.id,
                "room_name": room.room_name,
                "description": room.description,
                "role": member.role,
                "joined_at": member.joined_at.strftime("%Y-%m-%d %H:%M"),
                "left_at": (
                    member.left_at.strftime("%Y-%m-%d %H:%M")
                    if member.left_at
                    else None
                ),
                "ended_at": (
                    room.ended_at.strftime("%Y-%m-%d %H:%M") if room.ended_at else None
                ),
            }
        )
    return jsonify(result)
