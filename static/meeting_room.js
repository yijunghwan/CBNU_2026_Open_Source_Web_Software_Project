function OpenCreatePage() {
    document.querySelector(".create_page-bg").style.display = "block";
}

function CloseCreatePage() {
    document.querySelector(".create_page-bg").style.display = "none";
}

const name = document.getElementById("name");
const explain = document.getElementById("explain");

name.addEventListener("input", function () {
    document.getElementById("count1").innerHTML = name.value.length;
});

explain.addEventListener("input", function () {
    document.getElementById("count2").innerHTML = explain.value.length;
});

function CreateMeeting() {
    const card = `
            <div class="card">
          <div class="card1-top">
            <div class="meeting-creator">meeting.creator }}</div>
            <button class="star">☆</button>
          </div>
          <div class="card2-top">
            <div class="card-title">
              <h2>meeting.title }}</h2>
            </div>
            <div class="state">meeting.state }}</div>
          </div>
          <div class="card-body">
            <p>meeting.date }}</p>
            <p>참여자 meeting.participant }}명</p>
            <p>회의록 meeting.message_count }}개</p>
          </div>
        </div>
        `;
    document
        .querySelector(".meeting-list")
        .insertAdjacentHTML("beforeend", card);
    CloseCreatePage();
}