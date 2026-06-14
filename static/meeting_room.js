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
    if (event.key !== "Enter") {
        return;
    }
    event.preventDefault();
    sendMessage();
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

function hideRoom() {
    chattinginput.style.display = "none";
    leavebutton.style.display = "none";
    invitebutton.style.display = "none";
    invitemodal.style.display = "none";
}

function showRoom() {
    chattinginput.style.display = "flex";
    leavebutton.style.display = "block";
    invitebutton.style.display = "block";
}

function resetRoom() {
    roomId = null;
    role = null;
    lastMessageId = 0;
    chatting.innerHTML = "";
    participantslist.innerHTML = "";
    roomname.textContent = "회의실";
    membercount.textContent = "0";
    participantscount.textContent = "0";
    leavebutton.textContent = "↪ 나가기";
    showRoom();
}

async function request(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        if (response.ok === false) {
            if (result.message) {
                alert(result.message);
            } else {
                alert("오류 발생");
            }
            return null;
        }
        return result;
    } catch (error) {
        alert("연결 불가");
        return null;
    }
}

async function loadRoom(url) {
    const room = await request(url);
    if (room === null) {
        return;
    }
    roomlist.innerHTML = "";
    resetRoom();
    room.forEach(function (room) {
        if (url === "/meeting/invited_rooms") {
            inviteRoom(room);
        } else {
            makeRoom(room);
        }
    });
}

function inviteRoom(data) {
    const room = document.createElement("div");
    let description = data.description;
    if (!description) {
        description = "설명이 없습니다.";
    }
    room.className = "invite";
    room.innerHTML = `
        <div class="invite-title">${data.room_name}</div>
        <div class="invite-description">${description}</div>

        <div class="invite-button">
            <button onclick="accept(${data.invite_id})">수락</button>
            <button onclick="reject(${data.invite_id})">거절</button>
        </div>
    `;
    room.addEventListener("click", function (event) {
        if (event.target.tagName === "BUTTON") {
            return;
        }
        document.querySelectorAll(".invite").forEach(function (item) {
            item.classList.remove("active");
        });
        room.classList.add("active");
        showMeeting(data);
    });
    roomlist.appendChild(room);
}

function makeRoom(data) {
    const room = document.createElement("div");
    let icon = "join-icon";
    if (data.role === "owner") {
        icon = "owner-icon";
    }
    room.className = "room-item";
    room.innerHTML = `
        <div class="room-icon ${icon}"></div>
        <div class="room-text">
            <div class="room-title">${data.room_name}</div>
            <div class="room-info">진행 중 · ${data.member_count}명</div>
        </div>
        <div class="room-status"></div>
    `;
    room.addEventListener("click", function () {
        if (room.classList.contains("active")) {
            room.classList.remove("active");
            resetRoom();
            return;
        }
        document.querySelectorAll(".room-item").forEach(function (item) {
            item.classList.remove("active");
        });
        room.classList.add("active");
        roomId = data.id;
        role = data.role;
        lastMessageId = 0;
        roomname.textContent = data.room_name;
        showRoom();
        if (role === "owner") {
            leavebutton.textContent = "회의실 종료";
        } else {
            leavebutton.textContent = "↪ 나가기";
        }
        loadMessage(roomId);
        loadMember(roomId);
    });
    roomlist.appendChild(room);
}

function showMeeting(data) {
    roomId = null;
    role = null;
    lastMessageId = 0;
    let description = data.description;
    if (description === "") {
        description = "설명이 없습니다.";
    }
    roomname.textContent = data.room_name;
    membercount.textContent = data.member_count;
    participantscount.textContent = data.member_count;
    chattinginput.style.display = "none";
    leavebutton.textContent = "↪ 나가기";
    chatting.innerHTML = `
        <div class="invited-detail">
            <h2>${data.room_name}</h2>

            <div class="invited-section">
                <div class="invited-title">설명</div>
                <div class="invited-value description">
                    ${description}
                </div>
            </div>

            <div class="invited-set">
                <div class="invited-card">
                    <div class="invited-title2">방장</div>
                    <div class="invited-value2">${data.owner_name}</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">인원수</div>
                    <div class="invited-value2">${data.member_count}명</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">생성일</div>
                    <div class="invited-value2">${data.created_at}</div>
                </div>

                <div class="invited-card">
                    <div class="invited-title2">초대 상태</div>
                    <div class="invited-value2">${data.invite_status}</div>
                </div>
            </div>
        </div>
    `;
    showMember(data);
}

function showMember(data) {
    const member = data.members;
    const owner = member.filter(function (member2) {
        return member2.role === "owner";
    });
    const user = member.filter(function (member2) {
        return member2.role !== "owner";
    });
    participantslist.innerHTML = `
        <div class="member-section">
            <h4>방장 ${owner.length}</h4>
            <div class="owner-list"></div>
        </div>

        <div class="member-section">
            <h4>참여자 ${user.length}</h4>
            <div class="member-list"></div>
        </div>
    `;
    const ownerList = document.querySelector(".owner-list");
    const memberList = document.querySelector(".member-list");
    owner.forEach(function (member2) {
        ownerList.innerHTML += `
            <div class="member">
                <div class="member-icon">🟣</div>
                <div>
                    <div class="member-name">${member2.name} 👑</div>
                    <div class="member-status">참여중</div>
                </div>
            </div>
        `;
    });
    user.forEach(function (member2) {
        memberList.innerHTML += `
            <div class="member">
                <div class="member-icon">🔵</div>
                <div>
                    <div class="member-name">${member2.name}</div>
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
    const result = await request("/meeting/create", {
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

async function loadMessage(roomId, newMsg = false) {
    let url = `/meeting/messages/${roomId}`;
    if (newMsg === true) {
        url = `/meeting/messages/${roomId}?last_id=${lastMessageId}`;
    }
    const message = await request(url);
    if (message === null) {
        resetRoom();
        return;
    }
    if (newMsg === false) {
        chatting.innerHTML = "";
    }
    message.forEach(function (data) {
        const div = document.createElement("div");
        if (data.is_mine) {
            div.className = "message mine";
        } else {
            div.className = "message other";
        }
        div.innerHTML = `
            <div class="message-user">${data.user_name}</div>
            <div class="message-text">${data.message}</div>
            <div class="message-time">${data.created_at}</div>
        `;
        chatting.appendChild(div);
        if (data.id > lastMessageId) {
            lastMessageId = data.id;
        }
    });
    if (message.length > 0) {
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
    const result = await request("/meeting/message", {
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
    const member = await request(`/meeting/members/${roomId}`);
    if (member === null) {
        resetRoom();
        return;
    }
    let invite = [];
    if (history === false) {
        const result = await request(`/meeting/invites/${roomId}`);
        if (result === null) {
            return;
        }
        invite = result;
    }
    const owner = member.filter(function (data) {
        return data.role === "owner";
    });
    const normalMember = member.filter(function (data) {
        return data.role !== "owner";
    });
    let inviteSection = "";
    if (history === false) {
        inviteSection = `
            <div class="member-section">
                <h4>초대중 ${invite.length}</h4>
                <div class="invite-member-list"></div>
            </div>
        `;
    }
    participantslist.innerHTML = `
        <div class="member-section">
            <h4>방장 ${owner.length}</h4>
            <div class="owner-list"></div>
        </div>

        <div class="member-section">
            <h4>참여자 ${normalMember.length}</h4>
            <div class="normal-member-list"></div>
        </div>

        ${inviteSection}
    `;
    const ownerList = document.querySelector(".owner-list");
    const memberList = document.querySelector(".normal-member-list");
    owner.forEach(function (data) {
        ownerList.innerHTML += `
            <div class="member">
                <div class="member-icon">🟣</div>
                <div>
                    <div class="member-name">${data.name} 👑</div>
                    <div class="member-status">참여 중</div>
                </div>
            </div>
        `;
    });
    normalMember.forEach(function (data) {
        memberList.innerHTML += `
            <div class="member">
                <div class="member-icon">🔵</div>
                <div>
                    <div class="member-name">${data.name}</div>
                    <div class="member-status">참여 중</div>
                </div>
            </div>
        `;
    });
    if (history === false) {
        const inviteList = document.querySelector(".invite-member-list");
        invite.forEach(function (data) {
            inviteList.innerHTML += `
                <div class="member">
                    <div class="member-icon">🟡</div>
                    <div>
                        <div class="member-name">${data.name}</div>
                        <div class="member-status">대기 중</div>
                    </div>
                </div>
            `;
        });
    }
    membercount.textContent = member.length;
    participantscount.textContent = member.length;
}

function openInvite() {
    if (history===true) {
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
    const result = await request(`/meeting/search_user/${studentId}`);
    if (result === null) {
        invitename.textContent = "";
        inviteId = null;
        return;
    }
    if (result.success === false) {
        invitename.textContent = "";
        inviteId = null;
        return;
    }
    invitename.textContent = result.name;
    inviteId = result.id;
});

async function Invite() {
    if (history === true) {
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
    const result = await request("/meeting/invite", {
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
    if (result.message) {
        alert(result.message);
    } else {
        alert("초대가 완료되었습니다.");
    }
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
        const check = confirm("회의실을 종료하시겠습니까? 종료된 회의실은 복구가 불가능합니다.");
        if (check === false) {
            return;
        }
        const result = await request("/meeting/end", {
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
        if (result.message) {
            alert(result.message);
        } else {
            alert("회의실이 종료되었습니다.");
        }
        activeMyRoom();
        return;
    }
    const check = confirm("회의실에서 나가시겠습니까?");
    if (check === false) {
        return;
    }
    const result = await request("/meeting/leave", {
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
    if (result.message) {
        alert(result.message);
    } else {
        alert("회의실에서 나갔습니다.");
    }
    activeMyRoom();
}

function History() {
    const footer = document.querySelector(".footer");
    const filter = document.querySelector(".filter");
    if (history === true) {
        history = false;
        if (meetingtitle !== null) {
            meetingtitle.textContent = "회의실";
        }
        footer.textContent = "회의실 기록";
        filter.style.display = "flex";
        showRoom();
        activeMyRoom();
        return;
    }
    history = true;
    if (meetingtitle !== null) {
        meetingtitle.textContent = "회의실 기록";
    }
    footer.textContent = "회의실";
    filter.style.display = "none";
    hideRoom();
    loadHistory();
}

async function loadHistory() {
    const room = await request("/meeting/ended_rooms");
    if (room === null) {
        return;
    }
    roomlist.innerHTML = "";
    resetRoom();
    roomname.textContent = "회의실 기록";
    hideRoom();
    room.forEach(function (data) {
        const room2 = document.createElement("div");
        room2.className = "room-item";
        room2.innerHTML = `
            <div class="room-icon join-icon"></div>

            <div class="room-text">
                <div class="room-title">${data.room_name}</div>
                <div class="room-info">
                    종료 · ${data.ended_at}
                </div>
            </div>
        `;
        room2.addEventListener("click", function () {
            if (room2.classList.contains("active")) {
                room2.classList.remove("active");
                roomname.textContent = "회의실 기록";
                membercount.textContent = "0";
                participantscount.textContent = "0";
                chatting.innerHTML = "";
                participantslist.innerHTML = "";
                hideRoom();
                lastMessageId = 0;
                return;
            }
            document.querySelectorAll(".room-item").forEach(function (data) {
                data.classList.remove("active");
            });
            room2.classList.add("active");
            roomId = data.id;
            role = null;
            lastMessageId = 0;
            roomname.textContent = data.room_name;
            loadMessage(roomId);
            loadMember(roomId);
            hideRoom();
        });
        roomlist.appendChild(room2);
    });
}

function activeMyRoom() {
    history = false;
    meetingtitle.textContent = "회의실";
    document.querySelector(".footer").textContent = "회의실 기록";
    document.querySelector(".filter").style.display = "flex";
    document.querySelector(".my-list").classList.add("active");
    document.querySelector(".open-list").classList.remove("active");
    roomsearch.value = "";
    showRoom();
    loadRoom("/meeting/my_rooms");
}

function activeInvitedRoom() {
    history = false;
    meetingtitle.textContent = "회의실";
    document.querySelector(".footer").textContent = "회의실 기록";
    document.querySelector(".filter").style.display = "flex";
    document.querySelector(".open-list").classList.add("active");
    document.querySelector(".my-list").classList.remove("active");
    roomsearch.value = "";
    chattinginput.style.display = "none";
    if (invitebutton !== null) {
        invitebutton.style.display = "block";
    }
    loadRoom("/meeting/invited_rooms");
}

async function accept(inviteId) {
    const result = await request("/meeting/invite/accept", {
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
    if (result.message) {
        alert(result.message);
    } else {
        alert("초대를 수락했습니다.");
    }
    activeMyRoom();
}

async function reject(inviteId) {
    const result = await request("/meeting/invite/reject", {
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
    if (result.message) {
        alert(result.message);
    } else {
        alert("초대를 거절했습니다.");
    }
    activeInvitedRoom();
}

roomsearch.addEventListener("input", function () {
    const search = roomsearch.value.trim().toLowerCase();
    const room = document.querySelectorAll(".room-item, .invite");
    room.forEach(function (item) {
        const data = item.textContent.toLowerCase();
        if (data.includes(search)) {
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