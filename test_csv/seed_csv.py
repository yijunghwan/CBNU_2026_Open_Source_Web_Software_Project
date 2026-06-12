import os
import sys
import csv
import json
from math import ceil
from sqlalchemy import text

current_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(current_folder)
sys.path.append(root_folder)
os.chdir(root_folder)

from app import app
from models import (
    db,
    User,
    Club,
    ClubApplication,
    ClubBoard,
    Comment,
    promotionBoard,
    MeetingRoom,
    MeetingRoomMember,
    MeetingRoomInvite,
    MeetingMessage,
)


CLUB_POST_TYPES = {
    "CUVIX": [
        "project",
        "notice",
        "study"
    ],
    "EMsys": [
        "embedded",
        "study",
        "notice"
    ],
    "G Dev F.C": [
        "training",
        "match",
        "notice"
    ],
    "Next.Net": [
        "network",
        "seminar",
        "notice"
    ],
    "NOVA": [
        "ai",
        "seminar",
        "notice"
    ],
    "PDA": [
        "appdev",
        "project",
        "notice"
    ],
    "SAMMura": [
        "algorithm",
        "study",
        "notice"
    ],
    "TUX": [
        "linux",
        "opensource",
        "notice"
    ]
}


def _pick_post_type(club_name, index):
    post_types = CLUB_POST_TYPES.get(club_name, [])
    if not post_types:
        return ""
    return post_types[index % len(post_types)]


def _create_role_based_board_posts():
    print("Create role-based board posts")

    notice_templates = [
        """안녕하세요. 이번 주 운영 공지입니다.

1) 정규 세션은 수요일 18:30, 동아리실에서 진행합니다.
2) 출석은 시작 10분 전부터 체크하며, 지각 3회는 결석 1회로 처리합니다.
3) 프로젝트 팀별로 이번 주 목표와 이슈를 문서에 남겨 주세요.
4) 장비 대여가 필요한 팀은 화요일 22:00 전까지 간부진에게 신청해 주세요.

문의 사항은 댓글로 남겨 주시면 확인 후 순차적으로 답변하겠습니다.""",
        """중요 공지 안내드립니다.

다음 주에는 중간 점검 발표가 있습니다. 발표 자료는 팀당 5분 분량으로 준비해 주세요.
필수 포함 항목은 문제 정의, 현재 진행률, 다음 주 목표, 필요한 지원 사항입니다.

발표 순서는 당일 추첨으로 결정하며, 발표 자료는 PDF 형식으로 업로드해 주세요.
준비 과정에서 어려운 점이 있으면 멘토 배정을 요청하셔도 됩니다.""",
        """학기 운영 관련 공지입니다.

이번 달부터 스터디 운영 방식을 개선합니다. 기본 이론 세션 30분, 실습 50분, 피드백 20분으로 구성됩니다.
매주 금요일에는 자율 질의응답 시간을 열어, 팀별로 막힌 부분을 함께 해결할 예정입니다.

동아리 행사 일정과 시험 기간을 함께 고려하여 과제 난이도를 조정하고 있으니,
부담이 큰 경우 반드시 간부에게 사전에 공유해 주세요.""",
    ]

    president_brief_templates = [
        """회장 운영 브리핑 공유합니다.

이번 주에는 신입 부원 적응을 최우선으로 두고 팀 편성을 보완했습니다.
기존 팀에는 역할 편중이 있어, 문서화 담당과 테스트 담당을 분리해 배치했습니다.
다음 주까지 각 팀은 기본 기능 1차 구현을 목표로 진행해 주세요.

특히 협업 도구 사용이 익숙하지 않은 인원은 이번 주 토요일 보충 세션에 참석 바랍니다.""",
        """주간 브리핑입니다.

팀별 진행 속도 차이가 있어, 공통 리스크를 정리해 공유합니다.
1) 일정 산정이 과도하게 낙관적인 경우가 많음
2) 리뷰 요청 시점이 늦어 수정 비용이 커짐
3) 테스트 로그 기록 누락 빈도가 높음

이번 주부터는 최소 단위 기능 완료 시점마다 체크리스트를 갱신해 주세요.
작게 자주 검증하는 방식으로 전체 품질을 올리겠습니다.""",
    ]

    officer_notice_templates = [
        "간부 공지입니다. 스터디 자료는 회차별 폴더에 정리해 주세요. 파일명 규칙을 지켜야 후속 인수인계가 가능합니다.",
        "간부 공지입니다. 신입 Q&A 취합 문서를 오늘 23:00까지 업데이트해 주세요. 중복 질문은 병합해서 관리합니다.",
        "간부 공지입니다. 발표 리허설은 시작 15분 전 입실 기준이며, 발표 장비 점검을 꼭 먼저 진행해 주세요.",
    ]

    officer_log_templates = [
        "이번 주 간부 업무 기록입니다. 출석 관리표 보정, 팀별 일정 리마인드, 스터디 질의 응답 정리를 완료했습니다.",
        "운영 기록 공유합니다. 신규 부원 온보딩 안내서를 개편했고, 공통 에러 대응 문서 초안을 작성했습니다.",
        "활동 기록입니다. 중간 점검 피드백을 반영해 과제 난이도를 재분배하고 멘토링 요청 건을 배정했습니다.",
    ]

    member_templates = [
        "이번 주 활동 공유입니다. 팀 회의에서 기능 분해를 다시 진행했고, 담당 이슈를 문서화했습니다.",
        "스터디 복습 내용을 정리해 공유합니다. 실습 중 막힌 부분은 주말에 추가 학습 후 업데이트하겠습니다.",
        "프로젝트 진행 상황입니다. 기본 기능 구현은 완료했고 예외 케이스 테스트를 진행하고 있습니다.",
    ]

    for club_name in CLUB_POST_TYPES.keys():
        president = (
            User.query
            .filter_by(belonging_club=club_name, role_level=30)
            .order_by(User.id.asc())
            .first()
        )
        officers = (
            User.query
            .filter_by(belonging_club=club_name, role_level=20)
            .order_by(User.id.asc())
            .all()
        )
        members = (
            User.query
            .filter_by(belonging_club=club_name, role_level=10)
            .order_by(User.id.asc())
            .all()
        )

        if president:
            for idx in range(5):
                is_notice = 1 if idx < 3 else 0
                title = (
                    f"[{club_name}] 운영 공지 {idx + 1}"
                    if is_notice
                    else f"[{club_name}] 회장 주간 브리핑 {idx - 2}"
                )
                content = (
                    f"[{club_name}]\n" + notice_templates[idx % len(notice_templates)]
                    if is_notice
                    else f"[{club_name}]\n" + president_brief_templates[(idx - 3) % len(president_brief_templates)]
                )
                db.session.add(
                    ClubBoard(
                        title=title,
                        content=content,
                        author_pk=president.id,
                        club_name=club_name,
                        is_public=1,
                        is_notice=is_notice,
                        post_type=_pick_post_type(club_name, idx),
                    )
                )

        for officer_idx, officer in enumerate(officers):
            for local_idx in range(2):
                is_notice = 1 if local_idx == 0 else 0
                title = (
                    f"[{club_name}] 간부 공지 - {officer.name}"
                    if is_notice
                    else f"[{club_name}] 간부 활동 기록 - {officer.name}"
                )
                content = (
                    officer_notice_templates[(officer_idx + local_idx) % len(officer_notice_templates)]
                    if is_notice
                    else officer_log_templates[(officer_idx + local_idx) % len(officer_log_templates)]
                )
                db.session.add(
                    ClubBoard(
                        title=title,
                        content=content,
                        author_pk=officer.id,
                        club_name=club_name,
                        is_public=1,
                        is_notice=is_notice,
                        post_type=_pick_post_type(club_name, officer_idx + local_idx),
                    )
                )

        # 일반 부원은 0~1개 작성: 짝수 인덱스 부원만 1개 작성
        for member_idx, member in enumerate(members):
            if member_idx % 2 != 0:
                continue

            db.session.add(
                ClubBoard(
                    title=f"[{club_name}] 부원 활동 공유 {member_idx // 2 + 1}",
                    content=member_templates[member_idx % len(member_templates)],
                    author_pk=member.id,
                    club_name=club_name,
                    is_public=1,
                    is_notice=0,
                    post_type=_pick_post_type(club_name, member_idx),
                )
            )

    db.session.commit()


def _create_comment_data():
    print("Create realistic comment data")

    all_users = User.query.order_by(User.id.asc()).all()
    target_commenters = ceil(len(all_users) * 0.30)
    commenters = all_users[:target_commenters]

    all_posts = ClubBoard.query.order_by(ClubBoard.id.asc()).all()
    notice_posts = [post for post in all_posts if post.is_notice == 1]
    normal_posts = [post for post in all_posts if post.is_notice == 0]

    if not all_posts or not commenters:
        return

    notice_comments = [
        "공지 확인했습니다. 팀원들과 일정 공유해 두겠습니다.",
        "출석 기준과 준비물 항목 확인했습니다. 금주 내로 준비 완료하겠습니다.",
        "좋은 공지 감사합니다. 발표 자료 제출 기한만 다시 한번 확인 부탁드립니다.",
        "운영 방향 이해했습니다. 진행 중 이슈는 문서로 정리해서 공유하겠습니다.",
    ]
    normal_comments = [
        "정리 감사합니다. 다음 회의 전에 저희 팀 진행률도 업데이트하겠습니다.",
        "내용 좋네요. 관련 자료 있으면 댓글로 같이 공유해 주세요.",
        "저희도 비슷한 이슈가 있었는데, 다음 시간에 해결 방법 같이 이야기하면 좋겠습니다.",
        "읽고 참고했습니다. 일정 맞춰서 같이 진행해 보겠습니다.",
    ]
    long_notice_comment = (
        "공지 내용 꼼꼼히 확인했습니다. 이번에는 일정 관리 방식이 구체적으로 정리되어 있어서"
        " 팀 내 역할 분배가 훨씬 수월할 것 같습니다. 특히 발표 준비 항목이 명확해져서"
        " 리허설 단계에서 놓치던 부분을 줄일 수 있을 것 같아요."
        " 저희 팀은 금요일 저녁까지 초안 완성 후 주말에 피드백 반영하겠습니다."
    )

    # 1) 모든 게시글에 최소 1개 댓글 보장
    for idx, post in enumerate(all_posts):
        commenter = commenters[idx % len(commenters)]
        base_text = (
            notice_comments[idx % len(notice_comments)]
            if post.is_notice == 1
            else normal_comments[idx % len(normal_comments)]
        )
        db.session.add(Comment(post_id=post.id, author_pk=commenter.id, content=base_text))

    # 2) 공지글 중심으로 추가 댓글 스레드 생성
    for idx, post in enumerate(notice_posts):
        commenter_a = commenters[(idx * 2 + 3) % len(commenters)]
        commenter_b = commenters[(idx * 2 + 9) % len(commenters)]

        db.session.add(
            Comment(
                post_id=post.id,
                author_pk=commenter_a.id,
                content="공지 일정 기준으로 팀 미팅 시간을 재조정했습니다. 변경 내용은 오늘 저녁에 공유드리겠습니다.",
            )
        )

        long_text = long_notice_comment if idx % 3 == 0 else "문의사항 없습니다. 안내해 주신 방식대로 진행하겠습니다."
        db.session.add(Comment(post_id=post.id, author_pk=commenter_b.id, content=long_text))

    # 3) 일반 게시글에도 일부 추가 댓글 부여
    for idx, post in enumerate(normal_posts):
        if idx % 4 != 0:
            continue
        commenter = commenters[(idx + 11) % len(commenters)]
        db.session.add(
            Comment(
                post_id=post.id,
                author_pk=commenter.id,
                content="좋은 공유 감사합니다. 다음 주 진행 내용도 이어서 남겨 주세요.",
            )
        )

    db.session.commit()


def _create_meeting_data():
    print("Create meeting rooms and messages")

    owners = (
        User.query
        .filter(User.role_level.in_([30, 20]))
        .filter(User.belonging_club != "N")
        .order_by(User.role_level.desc(), User.id.asc())
        .limit(10)
        .all()
    )

    for idx, owner in enumerate(owners):
        room = MeetingRoom(
            room_name=f"{owner.belonging_club} 회의실 {idx + 1}",
            description="주간 운영 회의 및 프로젝트 점검 회의",
            created_by=owner.id,
            status="active",
        )
        db.session.add(room)
        db.session.flush()

        db.session.add(
            MeetingRoomMember(
                room_id=room.id,
                user_id=owner.id,
                role="owner",
                is_active=True,
            )
        )

        same_club_candidates = (
            User.query
            .filter(User.belonging_club == owner.belonging_club, User.id != owner.id)
            .order_by(User.role_level.desc(), User.id.asc())
            .limit(6)
            .all()
        )

        active_members = same_club_candidates[:3]
        pending_invites = same_club_candidates[3:5]

        for member in active_members:
            db.session.add(
                MeetingRoomMember(
                    room_id=room.id,
                    user_id=member.id,
                    role="member",
                    is_active=True,
                )
            )

        for invited in pending_invites:
            db.session.add(
                MeetingRoomInvite(
                    room_id=room.id,
                    invited_user_id=invited.id,
                    invited_by=owner.id,
                    status="pending",
                )
            )

        db.session.add(
            MeetingMessage(
                room_id=room.id,
                user_id=owner.id,
                message="이번 주 회의 시작합니다. 공지 사항부터 확인할게요.",
            )
        )

        if active_members:
            db.session.add(
                MeetingMessage(
                    room_id=room.id,
                    user_id=active_members[0].id,
                    message="확인했습니다. 진행 상황 공유드리겠습니다.",
                )
            )

    db.session.commit()


def _create_promotion_posts():
    print("Create promotion posts by presidents")

    presidents = (
        User.query
        .filter_by(role_level=30)
        .filter(User.belonging_club != "N")
        .order_by(User.id.asc())
        .all()
    )

    for idx, president in enumerate(presidents):
        db.session.add(
            promotionBoard(
                title=f"[{president.belonging_club}] 2026-2 신입 부원 모집",
                content=(
                    f"안녕하세요 {president.belonging_club}입니다.\n\n"
                    "2026-2학기 신입 부원을 모집합니다."
                    " 저희 동아리는 정기 스터디, 팀 프로젝트, 선후배 멘토링을 중심으로 운영되며,"
                    " 초보자도 단계별로 성장할 수 있도록 커리큘럼을 구성하고 있습니다.\n\n"
                    "활동 내용: 주 1회 정규 모임, 월 1회 프로젝트 점검, 학기 말 결과 공유회\n"
                    "지원 대상: 꾸준히 참여할 의지가 있는 학부 재학생\n"
                    "문의 방법: 동아리 회장/간부에게 DM 또는 홍보글 댓글\n\n"
                    "관심 있는 분들의 많은 지원 바랍니다."
                ),
                author_pk=president.id,
                club_name=president.belonging_club,
                is_notice=0,
            )
        )

    db.session.commit()


def _apply_board_visibility_policy():
    print("Apply board visibility policy")

    all_posts = ClubBoard.query.order_by(ClubBoard.id.asc()).all()
    if not all_posts:
        return

    posts_by_club = {}
    for post in all_posts:
        posts_by_club.setdefault(post.club_name, []).append(post)

    # 동아리별로 공지글 100% 비공개 + 전체의 약 70% 비공개 적용
    for club_posts in posts_by_club.values():
        notice_posts = [post for post in club_posts if post.is_notice == 1]
        normal_posts = [post for post in club_posts if post.is_notice != 1]

        for post in notice_posts:
            post.is_public = 0

        target_private_count = ceil(len(club_posts) * 0.70)
        current_private_count = len(notice_posts)
        need_private_from_normal = max(0, target_private_count - current_private_count)

        for idx, post in enumerate(normal_posts):
            post.is_public = 0 if idx < need_private_from_normal else 1

    db.session.commit()


def seed_from_csv():
    with app.app_context():
        print("Reset database")
        # MySQL: legacy FK table(eg. club_promotion) can block drop_all order.
        is_mysql = db.engine.dialect.name.startswith("mysql")
        if is_mysql:
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            db.session.execute(text("DROP TABLE IF EXISTS club_promotion"))
        db.drop_all()
        if is_mysql:
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.create_all()

        print("Create clubs")
        club_rows = [
            Club(name=club_name, post_types_json=json.dumps(post_types, ensure_ascii=True))
            for club_name, post_types in CLUB_POST_TYPES.items()
        ]
        db.session.add_all(club_rows)
        db.session.commit()

        users_csv_path = os.path.join(current_folder, 'users.csv')
        apps_csv_path = os.path.join(current_folder, 'apps.csv')
        boards_csv_path = os.path.join(current_folder, 'boards.csv')

        print("Load users.csv")
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
                    off=int(row.get('off', 0) or 0),
                    role_level=int(row['role_level'])
                )
                db.session.add(user)
        db.session.commit()

        print("Load apps.csv")
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

        print("Load boards.csv")
        with open(boards_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author = User.query.filter_by(user_id=row['author_user_id']).first()
                if not author:
                    continue
                board_post = ClubBoard(
                    title=row['title'],
                    content=row['content'],
                    author_pk=author.id,
                    club_name=row['club_name'],
                    is_public=int(row.get('is_public', 0) or 0),
                    is_notice=int(row.get('is_notice', 0) or 0),
                    post_type=(row.get('post_type') or '').strip(),
                )
                db.session.add(board_post)
        db.session.commit()

        _create_role_based_board_posts()
        _apply_board_visibility_policy()
        _create_comment_data()
        _create_meeting_data()
        _create_promotion_posts()

        print("Seed complete")


if __name__ == '__main__':
    seed_from_csv()
