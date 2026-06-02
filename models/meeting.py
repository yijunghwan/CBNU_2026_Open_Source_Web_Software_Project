from models import db

class MeetingRoom(db.Model):
    __tablename__ = "meeting_rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(10), default="active")
    ended_at = db.Column(db.DateTime)


class MeetingRoomMember(db.Model):
    __tablename__ = "meeting_room_members"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("meeting_rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(10), default="member")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)
    left_at = db.Column(db.DateTime)


class MeetingRoomInvite(db.Model):
    __tablename__ = "meeting_room_invites"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("meeting_rooms.id"), nullable=False)
    invited_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(10), default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class MeetingMessage(db.Model):
    __tablename__ = "meeting_messages"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("meeting_rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())