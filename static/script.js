/* --- 데이터 상태 및 초기화 (Fictional Korean Data) --- */
const clubData = [
    { name: "AI 퓨처", tag: "AI 연구회", slogan: "인공지능의 미래를 함께", score: 98, members: 120, icon: "🧠" },
    { name: "밴드 '공명'", tag: "음악 동아리", slogan: "세상을 울리다", score: 95, members: 80, icon: "🎸" },
    { name: "코드 크래프터", tag: "SW 개발", slogan: "상상을 코드로", score: 92, members: 150, icon: "💻" },
    { name: "아틀리에", tag: "미술 창작", slogan: "색으로 말하다", score: 89, members: 60, icon: "🎨" },
    { name: "시네마 '몽상가'", tag: "영화 감상/제작", slogan: "스크린의 꿈", score: 85, members: 45, icon: "🎬" },
    { name: "지구 방위대", tag: "환경 봉사", slogan: "우리 지구를 우리 손으로", score: 82, members: 200, icon: "🌱" },
    { name: "댄스 스튜디오 '리듬'", tag: "스트릿 댄스", slogan: "몸짓의 언어", score: 78, members: 70, icon: "🕺" }
];

const postData = [
    { id: 1, type: "공지사항", title: "2024 하반기 코딩 마라톤 공고", club: "SW 퓨처", icon: "📢", meta: "7월 10일 • 조회 1.2k" },
    { id: 2, type: "홍보", title: "[초청] 밴드 '공명' 가을 정기 공연", club: "밴드 공명", icon: "🎸", meta: "어제 • 좋아요 340" },
    { id: 3, type: "홍보", title: "신규 멤버 모집! 지구 방위대와 함께해요!", club: "지구 방위대", icon: "🌱", meta: "3시간 전 • 조회 560" },
    { id: 4, type: "게시글", title: "최신 딥러닝 트렌드 논문 리뷰 세미나", club: "AI 퓨처", icon: "🧠", meta: "1시간 전 • 댓글 45" },
    { id: 5, type: "게시글", title: "우리 동아리 MT 다녀왔어요!", club: "코드 크래프터", icon: "🚌", meta: "어제 • 좋아요 210" }
];

const activityData = [
    { icon: "💬", text: "김철수님이 'SW 퓨처' 게시글에 댓글을 남겼습니다.", time: "방금 전" },
    { icon: "❤️", text: "이영희님이 '밴드 공명' 공연 게시글에 좋아요를 눌렀습니다.", time: "2분 전" },
    { icon: "📸", text: "'아틀리에' 동아리가 새로운 활동 사진을 업로드했습니다.", time: "15분 전" },
    { icon: "➕", text: "'시네마 몽상가' 동아리에 새로운 멤버 2명이 가입했습니다.", time: "30분 전" },
    { icon: "💬", text: "박민수님이 '코드 크래프터' 게시글에 댓글을 남겼습니다.", time: "1시간 전" }
];


/* --- 3D 파티클 배경 (Three.js) --- */
const bgCanvasContainer = document.getElementById('bg-canvas-container');
const bgScene = new THREE.Scene();
const bgCamera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const bgRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
bgRenderer.setSize(window.innerWidth, window.innerHeight);
bgCanvasContainer.appendChild(bgRenderer.domElement);

const pointsGeometry = new THREE.BufferGeometry();
const pointsCount = 1000;
const posArray = new Float32Array(pointsCount * 3);
for (let i = 0; i < pointsCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 5;
}
pointsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const pointsMaterial = new THREE.PointsMaterial({ size: 0.005, color: 0x4facfe });
const pointsMesh = new THREE.Points(pointsGeometry, pointsMaterial);
bgScene.add(pointsMesh);
bgCamera.position.z = 2;

function animateBg() {
    requestAnimationFrame(animateBg);
    pointsMesh.rotation.y += 0.0005;
    bgRenderer.render(bgScene, bgCamera);
}
animateBg();

/* --- 3D 캐러셀 (Three.js + Anime.js) --- */
const carouselCanvasContainer = document.getElementById('carousel-canvas-container');
const carouselScene = new THREE.Scene();
const carouselCamera = new THREE.PerspectiveCamera(45, carouselCanvasContainer.offsetWidth / carouselCanvasContainer.offsetHeight, 0.1, 100);
const carouselRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
carouselRenderer.setSize(carouselCanvasContainer.offsetWidth, carouselCanvasContainer.offsetHeight);
carouselCanvasContainer.appendChild(carouselRenderer.domElement);
carouselCamera.position.z = 5;

// 카드 그룹 및 데이터 연결
const cardGroup = new THREE.Group();
carouselScene.add(cardGroup);
const cards = [];
const cardDataToMatch = clubData; // 7개

cardDataToMatch.forEach((data, index) => {
    // 단순화된 기하학적 카드 (HTML 카드 구현보다 3D 렌더링에 집중)
    const geometry = new THREE.PlaneGeometry(1, 1.5);
    const material = new THREE.MeshBasicMaterial({ 
        color: 0x333333, 
        side: THREE.DoubleSide, 
        transparent: true, 
        opacity: 0.9,
        wireframe: true // 추상적 3D 느낌 강조
    });
    const card = new THREE.Mesh(geometry, material);
    
    const angle = (index / cardDataToMatch.length) * Math.PI * 2;
    const radius = 2.5;
    card.position.x = Math.cos(angle) * radius;
    card.position.y = (Math.random() - 0.5) * 0.5; // 약간의 y축 분산
    card.position.z = Math.sin(angle) * radius;
    card.rotation.y = -angle; // 카메라 바라보게

    // 데이터 속성 추가 (나중에 사용)
    card.userData.clubData = data;
    cards.push(card);
    cardGroup.add(card);
});

// 상호작용 (Drag to Rotate)
let isDragging = false;
let previousMouseX = 0;
let previousMouseY = 0;
let rotationSpeed = 0.002;

carouselCanvasContainer.addEventListener('mousedown', (e) => {
    isDragging = true;
    previousMouseX = e.clientX;
    previousMouseY = e.clientY;
});

window.addEventListener('mouseup', () => {
    isDragging = false;
});

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - previousMouseX;
    const deltaY = e.clientY - previousMouseY;

    cardGroup.rotation.y += deltaX * rotationSpeed;
    // cardGroup.rotation.x += deltaY * rotationSpeed; // x축 회전은 제한

    previousMouseX = e.clientX;
    previousMouseY = e.clientY;
});

// 애니메이션 및 렌더링
function animateCarousel() {
    requestAnimationFrame(animateCarousel);
    // 자동 서서히 회전 (사용자 조작 없을 때)
    if (!isDragging) {
        cardGroup.rotation.y += 0.0001;
    }
    carouselRenderer.render(carouselScene, carouselCamera);
}
animateCarousel();

// Anime.js를 활용한 초기 등장 애니메이션
anime({
    targets: cardGroup.rotation,
    y: [Math.PI, 0],
    duration: 3000,
    easing: 'easeOutExpo'
});

/* --- 데이터 대시보드 및 위젯 --- */
const feedContainer = document.querySelector('.feed-container');
const postGrid = document.querySelector('.post-grid');
const postFilterSelect = document.getElementById('post-filter');

// 실시간 활동 피드 초기 채우기
function populateFeed() {
    activityData.forEach((item, index) => {
        const feedItem = document.createElement('div');
        feedItem.classList.add('feed-item');
        feedItem.innerHTML = `
            <span class="item-icon">${item.icon}</span>
            <div class="item-content">
                <p class="item-text">${item.text}</p>
                <span class="item-meta">${item.time}</span>
            </div>
        `;
        feedContainer.appendChild(feedItem);
    });
    
    // Anime.js로 순차적으로 나타나게 함
    anime({
        targets: '.feed-item',
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 800,
        delay: anime.stagger(100, { start: 500 }), // 지연 시간 스태거
        easing: 'easeOutElastic(1, .8)'
    });
}
populateFeed();

// 인기 게시물 그리드 채우기
function populatePosts(filterType = '전체') {
    postGrid.innerHTML = ''; // 초기화
    const filteredPosts = filterType === '전체' ? postData : postData.filter(post => post.type === filterType);
    
    filteredPosts.forEach(post => {
        const postCard = document.createElement('div');
        postCard.classList.add('post-card');
        postCard.dataset.postId = post.id;
        postCard.innerHTML = `
            <div class="post-card-thumbnail">
                <span class="thumbnail-icon">${post.icon}</span>
            </div>
            <div class="post-card-body">
                <span class="post-category">${post.type}</span>
                <h4 class="post-title">${post.title}</h4>
                <div class="post-meta-row">
                    <span class="post-club">${post.club}</span>
                    <span class="post-meta-data">${post.meta}</span>
                </div>
            </div>
        `;
        
        postGrid.appendChild(postCard);

        // 클릭 시 하이라이트 이벤트
        postCard.addEventListener('click', () => {
            // 다른 카드의 하이라이트 제거
            document.querySelectorAll('.post-card').forEach(card => card.classList.remove('highlighted'));
            postCard.classList.add('highlighted');
        });
    });

    // Anime.js로 카드 등장 애니메이션 (필터 변경 시에도 적용)
    anime({
        targets: '.post-card',
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 600,
        delay: anime.stagger(80, { start: 200 }),
        easing: 'easeOutExpo'
    });
}
populatePosts();

// 필터 변경 이벤트
postFilterSelect.addEventListener('change', (e) => {
    populatePosts(e.target.value);
});

/* --- 추가 상호작용 및 반응성 --- */
window.addEventListener('resize', () => {
    // Three.js 배경 및 캐러셀 크기 조정
    bgCamera.aspect = window.innerWidth / window.innerHeight;
    bgCamera.updateProjectionMatrix();
    bgRenderer.setSize(window.innerWidth, window.innerHeight);
    
    carouselCamera.aspect = carouselCanvasContainer.offsetWidth / carouselCanvasContainer.offsetHeight;
    carouselCamera.updateProjectionMatrix();
    carouselRenderer.setSize(carouselCanvasContainer.offsetWidth, carouselCanvasContainer.offsetHeight);
});