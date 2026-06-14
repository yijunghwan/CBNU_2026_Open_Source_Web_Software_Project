from datetime import datetime

from models import db, User, MeetingRoom, MeetingRoomMember, MeetingRoomInvite


# AI 생성 함수: 관리자 로그인 시 회장단 공용 회의실 동기화 처리
def _sync_executive_meeting_room(login_user):
    if login_user.role_level < 40:
        return

    executive_room_name = '회장단-관리자 공용 회의실'

    room = (
        MeetingRoom.query
        .filter_by(room_name=executive_room_name, status='active')
        .order_by(MeetingRoom.id.asc())
        .first()
    )

    if room is None:
        room = MeetingRoom(
            room_name=executive_room_name,
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
