const input = document.querySelector(".create-modal input");
const textarea = document.querySelector(".create-modal textarea");

const titlecount = document.querySelector(".title-count");
const descriptioncount = document.querySelector(".description-count");

const meetingtitle = document.querySelector(".meetings-info h2, .meetings-info h3");

const roomname = document.querySelector(".room-name");
const membercount = document.querySelector(".member-count");
const participantscount = document.querySelector(".participants-count");

const roomlist = document.querySelector(".list");
const messageinput = document.querySelector(".message-input");
const chatting = document.querySelector(".chatting");
const chattinginput = document.querySelector(".chatting-input");
const participantslist = document.querySelector(".participants-list");

const invitesearch = document.querySelector(".invite-search");
const invitename = document.querySelector(".invite-name");
const invitebutton = document.querySelector(".participants-info .top button");
const invitemodal = document.querySelector(".invite-modal");

const leavebutton = document.querySelector(".leave-button button");

const roomsearch = document.querySelector(".room-search");

let roomId = null;
let role = null;
let inviteId = null;
let lastMessageId = 0;
let history = false;

input.addEventListener("input", function () {
    titlecount.textContent = input.value.length;
});

textarea.addEventListener("input", function () {
    descriptioncount.textContent = textarea.value.length;
});

messageinput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

function openModal() {
    document.querySelector(".modal-layout").style.display = "flex";
}

function closeModal() {
    document.querySelector(".modal-layout").style.display = "none";
    input.value = "";
    textarea.value = "";
    titlecount.textContent = "0";
    descriptioncount.textContent = "0";
}

function hideRoomAction() {
    chattinginput.style.display = "none";
    leavebutton.style.display = "none";

    if (invitebutton) {
        invitebutton.style.display = "none";
    }

    if (invitemodal) {
        invitemodal.style.display = "none";
    }
}

function showRoomAction() {
    chattinginput.style.display = "flex";
    leavebutton.style.display = "block";

    if (invitebutton) {
        invitebutton.style.display = "block";
    }
}

function resetRoomView() {
    roomId = null;
    role = null;
    lastMessageId = 0;

    roomname.textContent = "회의실";
    membercount.textContent = "0";
    participantscount.textContent = "0";

    chatting.innerHTML = "";
    participantslist.innerHTML = "";

    showRoomAction();
    leavebutton.textContent = "↪ 나가기";
}

async function requestJson(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            alert(result.message || "요청 처리 중 오류가 발생했습니다.");
            return null;
        }

        return result;
    } catch (error) {
        alert("서버와 연결할 수 없습니다.");
        return null;
    }
}

async function loadRoom(url) {
    const rooms = await requestJson(url);

    if (rooms === null) {
        return;
    }

    roomlist.innerHTML = "";
    resetRoomView();

    rooms.forEach(function (room) {
        const roomItem = document.createElement("div");

        if (url === "/meeting/invited_rooms") {
            roomItem.className = "invite";

            roomItem.innerHTML = `
                <div class="invite-title">${room.room_name}</div>
                <div class="invite-description">${room.description || "설명이 없습니다."}</div>

                <div class="invite-button">
                    <button onclick="accept(${room.invite_id})">수락</button>
                    <button onclick="reject(${room.invite_id})">거절</button>
                </div>
            `;

            roomItem.addEventListener("click", function (event) {
                if (event.target.tagName === "BUTTON") {
                    return;
                }

                document.querySelectorAll(".invite").forEach(function (item) {
                    item.classList.remove("active");
                });

                roomItem.classList.add("active");
                showRoom(room);
            });

            roomlist.appendChild(roomItem);
            return;
        }

        roomItem.className = "room-item";

        roomItem.innerHTML = `
            <div class="room-icon ${room.role === "owner" ? "owner-icon" : "join-icon"}"></div>
            <div class="room-text">
                <div class="room-title">${room.room_name}</div>
                <div class="room-info">진행 중 · ${room.member_count || 0}명</div>
            </div>
            <div class="room-status"></div>
        `;

        roomItem.addEventListener("click", function () {
            if (roomItem.classList.contains("active")) {
                roomItem.classList.remove("active");
                resetRoomView();
                return;
            }

            document.querySelectorAll(".room-item").forEach(function (item) {
                item.classList.remove("active");
            });

            roomItem.classList.add("active");

            roomId = room.id;
            role = room.role;
            lastMessageId = 0;

            roomname.textContent = room.room_name;
            showRoomAction();

            if (role === "owner") {
                leavebutton.textContent = "회의실 종료";
            } else {
                leavebutton.textContent = "↪ 나가기";
            }

            loadMessage(roomId);
            loadMember(roomId);
        });

        roomlist.appendChild(roomItem);
    });
}

function showRoom(room) {
    roomId = null;
    role = null;
    lastMessageId = 0;

    roomname.textContent = room.room_name;
    membercount.textContent = room.member_count || 0;
    participantscount.textContent = room.member_count || 0;

    chattinginput.style.display = "none";
    leavebutton.textContent = "↪ 나가기";

    chatting.innerHTML = `
        <div class="invited-detail">
            <h2>${room.room_name}</h2>

            <div class="invited-section">
                <div class="invited-title">설명</div>
                <div class="invited-value description">
                    ${room.description || "설명이 없습니다."}
                </div>
            </div>

            <div class="invited-set">
                <div class="invited-card">
                    <div class="invited-title2">방장</div>
                    <div class="invited-value2">${room.owner_name || "알 수 없음"}</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">인원수</div>
                    <div class="invited-value2">${room.member_count || 0}명</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">생성일</div>
                    <div class="invited-value2">${room.created_at || "-"}</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">초대 상태</div>
                    <div class="invited-value2">${room.invite_status || "대기중"}</div>
                </div>
            </div>
        </div>
    `;

    showMember(room);
}

function showMember(room) {
    const roomMembers = room.members || [];

    const owners = roomMembers.filter(function (member) {
        return member.role === "owner";
    });

    const members = roomMembers.filter(function (member) {
        return member.role !== "owner";
    });

    participantslist.innerHTML = `
        <div class="member-section">
            <h4>방장 ${owners.length}</h4>
            <div class="owner-list"></div>
        </div>

        <div class="member-section">
            <h4>참여자 ${members.length}</h4>
            <div class="member-list"></div>
        </div>
    `;

    const ownerList = document.querySelector(".owner-list");
    const memberList = document.querySelector(".member-list");

    owners.forEach(function (member) {
        ownerList.innerHTML += `
            <div class="member">
                <div class="member-icon">🟣</div>
                <div>
                    <div class="member-name">${member.name} 👑</div>
                    <div class="member-status">참여중</div>
                </div>
            </div>
        `;
    });

    members.forEach(function (member) {
        memberList.innerHTML += `
            <div class="member">
                <div class="member-icon">🔵</div>
                <div>
                    <div class="member-name">${member.name}</div>
                    <div class="member-status">참여중</div>
                </div>
            </div>
        `;
    });
}

async function createRoom() {
    const roomTitle = input.value.trim();
    const roomDescription = textarea.value.trim();

    if (roomTitle === "") {
        alert("방 이름을 입력하세요.");
        return;
    }

    const result = await requestJson("/meeting/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: roomTitle,
            description: roomDescription
        })
    });

    if (result === null) {
        return;
    }

    alert("회의실 생성 성공");
    closeModal();
    activeMyRoom();
}

async function loadMessage(roomId, onlyNew = false) {
    let url = `/meeting/messages/${roomId}`;

    if (onlyNew) {
        url = `/meeting/messages/${roomId}?last_id=${lastMessageId}`;
    }

    const messages = await requestJson(url);

    if (messages === null) {
        resetRoomView();
        return;
    }

    if (!onlyNew) {
        chatting.innerHTML = "";
    }

    messages.forEach(function (msg) {
        const messageItem = document.createElement("div");

        if (msg.is_mine) {
            messageItem.className = "message mine";
        } else {
            messageItem.className = "message other";
        }

        messageItem.innerHTML = `
            <div class="message-user">${msg.user_name}</div>
            <div class="message-text">${msg.message}</div>
            <div class="message-time">${msg.created_at}</div>
        `;

        chatting.appendChild(messageItem);

        if (msg.id > lastMessageId) {
            lastMessageId = msg.id;
        }
    });

    if (messages.length > 0) {
        chatting.scrollTop = chatting.scrollHeight;
    }
}

async function sendMessage() {
    const message = messageinput.value.trim();

    if (roomId === null) {
        alert("회의실을 선택하세요.");
        return;
    }

    if (message === "") {
        return;
    }

    const result = await requestJson("/meeting/message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            room_id: roomId,
            message: message
        })
    });

    if (result === null) {
        return;
    }

    messageinput.value = "";
    loadMessage(roomId);
}

async function loadMember(roomId) {
    const members = await requestJson(`/meeting/members/${roomId}`);

    if (members === null) {
        resetRoomView();
        return;
    }

    let invites = [];

    if (!history) {
        const result = await requestJson(`/meeting/invites/${roomId}`);

        if (result === null) {
            return;
        }

        invites = result;
    }

    const owners = members.filter(function (member) {
        return member.role === "owner";
    });

    const normalMembers = members.filter(function (member) {
        return member.role !== "owner";
    });

    let inviteSection = "";

    if (!history) {
        inviteSection = `
            <div class="member-section">
                <h4>초대중 ${invites.length}</h4>
                <div class="invite-member-list"></div>
            </div>
        `;
    }

    participantslist.innerHTML = `
        <div class="member-section">
            <h4>방장 ${owners.length}</h4>
            <div class="owner-list"></div>
        </div>

        <div class="member-section">
            <h4>참여자 ${normalMembers.length}</h4>
            <div class="normal-member-list"></div>
        </div>

        ${inviteSection}
    `;

    const ownerList = document.querySelector(".owner-list");
    const normalMemberList = document.querySelector(".normal-member-list");

    owners.forEach(function (member) {
        ownerList.innerHTML += `
            <div class="member">
                <div class="member-icon">🟣</div>
                <div>
                    <div class="member-name">${member.name} 👑</div>
                    <div class="member-status">참여 중</div>
                </div>
            </div>
        `;
    });

    normalMembers.forEach(function (member) {
        normalMemberList.innerHTML += `
            <div class="member">
                <div class="member-icon">🔵</div>
                <div>
                    <div class="member-name">${member.name}</div>
                    <div class="member-status">참여 중</div>
                </div>
            </div>
        `;
    });

    if (!history) {
        const inviteMemberList = document.querySelector(".invite-member-list");

        invites.forEach(function (invite) {
            inviteMemberList.innerHTML += `
                <div class="member">
                    <div class="member-icon">🟡</div>
                    <div>
                        <div class="member-name">${invite.name}</div>
                        <div class="member-status">대기 중</div>
                    </div>
                </div>
            `;
        });
    }

    membercount.textContent = members.length;
    participantscount.textContent = members.length;
}

function openInvite() {
    if (history) {
        return;
    }

    if (roomId === null) {
        alert("회의실을 선택하세요.");
        return;
    }

    if (invitemodal.style.display === "block") {
        invitemodal.style.display = "none";
    } else {
        invitemodal.style.display = "block";
    }

    invitesearch.value = "";
    invitename.textContent = "";
    inviteId = null;
}

invitesearch.addEventListener("input", async function () {
    const studentId = invitesearch.value.trim();

    if (studentId.length < 4) {
        invitename.textContent = "";
        inviteId = null;
        return;
    }

    const result = await requestJson(`/meeting/search_user/${studentId}`);

    if (result === null || !result.success) {
        invitename.textContent = "";
        inviteId = null;
        return;
    }

    invitename.textContent = result.name;
    inviteId = result.id;
});

async function Invite() {
    if (history) {
        return;
    }

    if (roomId === null) {
        alert("회의실을 선택하세요.");
        return;
    }

    if (inviteId === null) {
        alert("초대할 사용자를 선택하세요.");
        return;
    }

    const result = await requestJson("/meeting/invite", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            room_id: roomId,
            user_id: inviteId
        })
    });

    if (result === null) {
        return;
    }

    alert(result.message || "초대가 완료되었습니다.");

    invitesearch.value = "";
    invitename.textContent = "";
    inviteId = null;

    loadMember(roomId);
}

async function leaveRoom() {
    if (roomId === null) {
        alert("회의실을 선택하세요.");
        return;
    }

    if (role === "owner") {
        const ok = confirm("회의실을 종료하시겠습니까? 종료된 회의실은 복구가 불가능합니다.");

        if (!ok) {
            return;
        }

        const result = await requestJson("/meeting/end", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                room_id: roomId
            })
        });

        if (result === null) {
            return;
        }

        alert(result.message || "회의실이 종료되었습니다.");
        activeMyRoom();
        return;
    }

    const ok = confirm("회의실에서 나가시겠습니까?");

    if (!ok) {
        return;
    }

    const result = await requestJson("/meeting/leave", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            room_id: roomId
        })
    });

    if (result === null) {
        return;
    }

    alert(result.message || "회의실에서 나갔습니다.");
    activeMyRoom();
}

function History() {
    const footer = document.querySelector(".footer");
    const filter = document.querySelector(".filter");

    if (history) {
        history = false;

        if (meetingtitle) {
            meetingtitle.textContent = "회의실";
        }

        footer.textContent = "회의실 기록";
        filter.style.display = "flex";

        showRoomAction();
        activeMyRoom();

        return;
    }

    history = true;

    if (meetingtitle) {
        meetingtitle.textContent = "회의실 기록";
    }

    footer.textContent = "회의실";
    filter.style.display = "none";

    hideRoomAction();
    loadHistory();
}

async function loadHistory() {
    const rooms = await requestJson("/meeting/ended_rooms");

    if (rooms === null) {
        return;
    }

    roomlist.innerHTML = "";
    resetRoomView();

    roomname.textContent = "회의실 기록";

    hideRoomAction();

    rooms.forEach(function (room) {
        const roomItem = document.createElement("div");

        roomItem.className = "room-item";

        roomItem.innerHTML = `
            <div class="room-icon join-icon"></div>

            <div class="room-text">
                <div class="room-title">${room.room_name}</div>
                <div class="room-info">
                    종료 · ${room.ended_at || "-"}
                </div>
            </div>
        `;

        roomItem.addEventListener("click", function () {
            if (roomItem.classList.contains("active")) {
                roomItem.classList.remove("active");

                roomname.textContent = "회의실 기록";
                membercount.textContent = "0";
                participantscount.textContent = "0";

                chatting.innerHTML = "";
                participantslist.innerHTML = "";

                hideRoomAction();

                lastMessageId = 0;

                return;
            }

            document.querySelectorAll(".room-item").forEach(function (item) {
                item.classList.remove("active");
            });

            roomItem.classList.add("active");

            roomId = room.id;
            role = null;
            lastMessageId = 0;

            roomname.textContent = room.room_name;

            loadMessage(roomId);
            loadMember(roomId);

            hideRoomAction();
        });

        roomlist.appendChild(roomItem);
    });
}

function activeMyRoom() {
    history = false;

    if (meetingtitle) {
        meetingtitle.textContent = "회의실";
    }

    document.querySelector(".footer").textContent = "회의실 기록";
    document.querySelector(".filter").style.display = "flex";

    document.querySelector(".my-list").classList.add("active");
    document.querySelector(".open-list").classList.remove("active");

    roomsearch.value = "";

    showRoomAction();

    loadRoom("/meeting/my_rooms");
}

function activeInvitedRoom() {
    history = false;

    if (meetingtitle) {
        meetingtitle.textContent = "회의실";
    }

    document.querySelector(".footer").textContent = "회의실 기록";
    document.querySelector(".filter").style.display = "flex";

    document.querySelector(".open-list").classList.add("active");
    document.querySelector(".my-list").classList.remove("active");

    roomsearch.value = "";
    chattinginput.style.display = "none";

    if (invitebutton) {
        invitebutton.style.display = "block";
    }

    loadRoom("/meeting/invited_rooms");
}

async function accept(inviteId) {
    const result = await requestJson("/meeting/invite/accept", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            invite_id: inviteId
        })
    });

    if (result === null) {
        return;
    }

    alert(result.message || "초대를 수락했습니다.");
    activeMyRoom();
}

async function reject(inviteId) {
    const result = await requestJson("/meeting/invite/reject", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            invite_id: inviteId
        })
    });

    if (result === null) {
        return;
    }

    alert(result.message || "초대를 거절했습니다.");
    activeInvitedRoom();
}

roomsearch.addEventListener("input", function () {
    const keyword = roomsearch.value.trim().toLowerCase();

    const roomItems = document.querySelectorAll(".room-item, .invite");

    roomItems.forEach(function (item) {
        const text = item.textContent.toLowerCase();

        if (text.includes(keyword)) {
            item.style.display = "";
        } else {
            item.style.display = "none";
        }
    });
});

setInterval(function () {
    if (roomId !== null && role !== null) {
        loadMessage(roomId, true);
    }
}, 1000);

activeMyRoom();