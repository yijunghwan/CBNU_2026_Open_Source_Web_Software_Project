// 게시판 드롭다운 열고 닫기
function toggleDropdown(e) {
    e.preventDefault();
    const dropdown = document.getElementById('board-dropdown');
    dropdown.classList.toggle('open');
}

// 바깥 클릭하면 닫기
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('board-dropdown');
    if (dropdown && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

// 커스텀 커서
const cursorDot = document.querySelector('.cursor-dot');
const cursorOutline = document.querySelector('.cursor-outline');

window.addEventListener('mousemove', (e) => {
    const posX = e.clientX;
    const posY = e.clientY;

    cursorDot.style.left = `${posX}px`;
    cursorDot.style.top = `${posY}px`;

    // 테두리는 살짝 늦게 따라오게
    cursorOutline.animate({
        left: `${posX}px`,
        top: `${posY}px`
    }, { duration: 500, fill: "forwards" });
});

// Three.js 배경 (캐러셀 + 파티클)
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x050505, 0.04);

const container = document.getElementById('canvas-container');
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
camera.position.z = 18;
camera.position.y = 2;

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

// 파티클 배경
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1000;
const posArray = new Float32Array(particlesCount * 3);

for (let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 60;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

const particlesMaterial = new THREE.PointsMaterial({
    size: 0.08, color: 0x00d4ff, transparent: true, opacity: 0.8,
    blending: THREE.AdditiveBlending
});
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

// 배너 캐러셀
const carouselGroup = new THREE.Group();
scene.add(carouselGroup);

const bannerCount = 8;
const radius = 13;
const bannerImages = [
    '/static/mainPage_/banner_image/CUVIC.png',
    '/static/mainPage_/banner_image/EMSYS.png',
    '/static/mainPage_/banner_image/G.DEV.FC.png',
    '/static/mainPage_/banner_image/NEST.NET.png',
    '/static/mainPage_/banner_image/NOVA.png',
    '/static/mainPage_/banner_image/pda.png',
    '/static/mainPage_/banner_image/SAMMaru.png',
    '/static/mainPage_/banner_image/TUX.png',
];

// 이미지 배열과 순서 맞춰서 작성
const bannerURLs = [
    '/board/anotherclub/CUVIX',
    '/board/anotherclub/EMsys',
    '/board/anotherclub/G Dev F.C',
    '/board/anotherclub/Next.Net',
    '/board/anotherclub/NOVA',
    '/board/anotherclub/PDA',
    '/board/anotherclub/SAMMura',
    '/board/anotherclub/TUX',
];

const textureLoader = new THREE.TextureLoader();

for (let i = 0; i < bannerCount; i++) {
    const angle = (i / bannerCount) * Math.PI * 2;
    const geometry = new THREE.BoxGeometry(4.5, 7, 0.1);

    /*유현석이 수정(배너에 이미지 추가) */
    const texture = textureLoader.load(bannerImages[i]);
    const material = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        opacity: 0.9
    });
    const mesh = new THREE.Mesh(geometry, material);

    // 네온 테두리용 모서리 선
    const edges = new THREE.EdgesGeometry(geometry);
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0xffffff,
        linewidth: 2
    });
    const line = new THREE.LineSegments(edges, lineMaterial);
    mesh.add(line);

    // 원형으로 배치
    mesh.position.x = Math.cos(angle) * radius;
    mesh.position.z = Math.sin(angle) * radius;
    mesh.position.y = Math.sin(angle * 3) * 1.5; // 위아래로 물결치듯
    mesh.rotation.y = -angle + Math.PI / 2;      // 중앙을 바라보게

    mesh.userData.url = bannerURLs[i];

    carouselGroup.add(mesh);
}

// 마우스 드래그
let isDragging = false;
let previousMouseX = 0; let previousMouseY = 0;
let targetRotationY = 0;
let targetRotationX = 0;
const autoRotateSpeed = 0.002; // 가만히 둬도 도는 속도

const getPointerPosition = (e) => {
    if (e.touches && e.touches.length > 0) {
        return { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }
    if (e.changedTouches && e.changedTouches.length > 0) {
        return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
    }
    if (typeof e.clientX === 'number' && typeof e.clientY === 'number') {
        return { x: e.clientX, y: e.clientY };
    }
    return null;
};

const onPointerDown = (e) => {
    isDragging = true;
    // 터치(모바일)와 마우스(PC) 모두 호환되도록 좌표를 가져옵니다.
    const point = getPointerPosition(e);
    if (!point) return;
    previousMouseX = point.x;
    previousMouseY = point.y;

    // 클릭해서 드래그 중일 땐 커스텀 커서 테두리가 1.5배 커지며 파랗게 변하게 합니다.
    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1.5)';
    cursorOutline.style.backgroundColor = 'rgba(0, 212, 255, 0.2)';
};
const onPointerMove = (e) => {
    if (!isDragging) return; // 드래그 중이 아니면 멈춥니다.
    const point = getPointerPosition(e);
    if (!point) return;
    const currentX = point.x;
    const currentY = point.y;

    // 방금 전 마우스 위치와 현재 위치의 차이(이동 거리)를 계산합니다.
    const deltaX = currentX - previousMouseX;
    const deltaY = currentY - previousMouseY;

    targetRotationY += deltaX * 0.005; // 마우스를 좌우로 민 만큼 목표 회전값 증가
    targetRotationX += deltaY * 0.002;

    // 상하로 3D 공간 전체가 너무 뒤집어지면 어색하므로 최대 각도(-0.2 ~ 0.2)를 제한합니다.
    targetRotationX = Math.max(-0.2, Math.min(0.2, targetRotationX));

    previousMouseX = currentX;
    previousMouseY = currentY;
};
const onPointerUp = () => {
    isDragging = false;
    targetRotationX = 0; // 드래그를 놓으면 위아래 기울어진 화면이 다시 제자리로 돌아옵니다.

    cursorOutline.style.transform = 'translate(-50%, -50%) scale(1)';
    cursorOutline.style.backgroundColor = 'transparent';
};

// 캔버스 위에 이벤트 리스너(마우스와 터치 감지기)를 달아줍니다.
container.addEventListener('mousedown', onPointerDown);
window.addEventListener('mousemove', onPointerMove);
window.addEventListener('mouseup', onPointerUp);
container.addEventListener('touchstart', onPointerDown);
window.addEventListener('touchmove', onPointerMove);
window.addEventListener('touchend', onPointerUp);

//각 배너를 클릭하면 지정된 URL로 이동하는 로직
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

// 드래그인지 클릭인지 구분하기 위한 변수
let mouseDownPos = { x: 0, y: 0 };
let suppressClickAfterTouch = false;

const moveToBannerUrl = (clientX, clientY) => {
    // 캔버스 안에서의 포인터 위치를 -1 ~ 1 범위로 정규화
    const rect = container.getBoundingClientRect();
    mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;

    // 광선을 쏴서 충돌한 오브젝트 목록을 가져옴
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(carouselGroup.children, true);

    if (intersects.length > 0) {
        // 충돌한 오브젝트의 최상위 부모(배너 mesh)를 찾음
        let target = intersects[0].object;
        while (target.parent && target.parent !== carouselGroup) {
            target = target.parent;
        }

        const url = target.userData.url;
        if (url) {
            window.location.href = url;  // URL로 이동!
        }
    }
};

container.addEventListener('mousedown', (e) => {
    mouseDownPos = { x: e.clientX, y: e.clientY };
});

container.addEventListener('touchstart', (e) => {
    const point = getPointerPosition(e);
    if (!point) return;
    mouseDownPos = { x: point.x, y: point.y };
}, { passive: true });

container.addEventListener('click', (e) => {
    if (suppressClickAfterTouch) return;

    // 마우스가 5px 이상 움직였으면 드래그로 판단 → 이동 안 함
    const dx = e.clientX - mouseDownPos.x;
    const dy = e.clientY - mouseDownPos.y;
    if (Math.sqrt(dx * dx + dy * dy) > 5) return;

    moveToBannerUrl(e.clientX, e.clientY);
});

container.addEventListener('touchend', (e) => {
    const point = getPointerPosition(e);
    if (!point) return;

    // 터치가 조금이라도 이동했으면 드래그로 판단
    const dx = point.x - mouseDownPos.x;
    const dy = point.y - mouseDownPos.y;
    if (Math.sqrt(dx * dx + dy * dy) > 8) return;

    // 모바일에서 click이 이어서 발생하는 경우 중복 이동 방지
    suppressClickAfterTouch = true;
    setTimeout(() => {
        suppressClickAfterTouch = false;
    }, 350);

    moveToBannerUrl(point.x, point.y);
}, { passive: true });


// 창 크기 바뀌면 비율과 캔버스 크기 재설정
window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// 메인 애니메이션 루프
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    if (!isDragging) {
        targetRotationY += autoRotateSpeed; // 드래그 중이 아니면 자동 회전
    }

    // Lerp: 목표 각도로 10%씩 부드럽게 다가가게 (관성 느낌)
    carouselGroup.rotation.y += (targetRotationY - carouselGroup.rotation.y) * 0.1;
    carouselGroup.rotation.x += (targetRotationX - carouselGroup.rotation.x) * 0.1;

    // 파티클 전체 회전 + 둥둥 떠다니기
    particlesMesh.rotation.y = elapsedTime * 0.05;
    particlesMesh.position.y = Math.sin(elapsedTime * 0.5) * 2;

    // 배너도 sin 파동으로 둥둥
    carouselGroup.children.forEach((banner, idx) => {
        banner.position.y = Math.sin(elapsedTime * 2 + idx) * 0.5;
    });

    // 최종적으로 변동된 카메라와 무대의 상황을 화면(캔버스)에 찍어냅니다.
    renderer.render(scene, camera);
}
animate();

// 스크롤해서 게시판 섹션이 보이면 애니메이션 실행
const boardSection = document.getElementById('board-section');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            boardSection.classList.add('is-visible');
            observer.unobserve(entry.target); // 한 번만 실행
        }
    });
}, { threshold: 0.3 });

observer.observe(boardSection);