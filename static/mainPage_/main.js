/* =========================================
           [게시판 드롭다운 토글 로직]
           '게시판' 버튼 클릭 시 카테고리 목록을 열고 닫는 기능을 담당합니다.
        ========================================= */

/**
 * toggleDropdown(e)
 * - '게시판' 버튼(a 태그)의 onclick에서 호출됩니다.
 * - e.preventDefault(): href="#" 클릭 시 페이지가 맨 위로 튀는 기본 동작을 막습니다.
 * - classList.toggle('open'): .open 클래스가 없으면 추가(열기), 있으면 제거(닫기)합니다.
 */
function toggleDropdown(e) {
    e.preventDefault();
    const dropdown = document.getElementById('board-dropdown');
    dropdown.classList.toggle('open');
}

// 드롭다운 외부 영역 클릭 시 자동으로 닫기
// dropdown.contains(e.target): 클릭된 요소가 드롭다운 내부인지 확인합니다.
// 내부가 아닌 경우에만 .open 클래스를 제거하여 목록을 닫습니다.
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('board-dropdown');
    if (dropdown && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});
//게시판 드롭다운  토글 로직 끝

/* =========================================
           [JavaScript 파트 1] 커스텀 커서 로직
           마우스가 움직일 때마다 HTML 요소(.cursor-dot, .cursor-outline)의 좌표를 바꿔줍니다.
        ========================================= */
const cursorDot = document.querySelector('.cursor-dot');
const cursorOutline = document.querySelector('.cursor-outline');

window.addEventListener('mousemove', (e) => {
    const posX = e.clientX; // 현재 마우스의 X(가로) 좌표
    const posY = e.clientY; // 현재 마우스의 Y(세로) 좌표

    // 작은 점은 마우스를 지연 없이 즉각적으로 따라갑니다.
    cursorDot.style.left = `${posX}px`;
    cursorDot.style.top = `${posY}px`;

    // 바깥 테두리는 브라우저의 기본 기능인 animate를 써서 0.5초 동안 서서히 마우스 위치로 이동하게 합니다. (유체 같은 느낌을 줌)
    cursorOutline.animate({
        left: `${posX}px`,
        top: `${posY}px`
    }, { duration: 500, fill: "forwards" });
});

/* =========================================
   [JavaScript 파트 3] Three.js 3D 환경 (캐러셀 + 파티클)
   Three.js는 기본적으로 무대(Scene), 카메라(Camera), 영사기(Renderer) 3개가 필요합니다.
========================================= */
const scene = new THREE.Scene(); // 무대를 만듭니다.
// 안개 효과(FogExp2)를 추가해 멀리 있는 물체가 배경색(#050505)과 자연스럽게 섞이게 만듭니다. (깊이감 증가)
scene.fog = new THREE.FogExp2(0x050505, 0.04);

const container = document.getElementById('canvas-container');
// 카메라를 설치합니다. (시야각 75도, 화면비율, 0.1부터 1000거리까지 렌더링)
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
camera.position.z = 18; // 카메라를 뒤로 18칸 물려서 무대를 넓게 봅니다.
camera.position.y = 2;  // 카메라를 살짝 위로 올립니다.

// 화면을 그려줄 렌더러입니다. antialias: true는 테두리의 계단 현상을 부드럽게 깎아줍니다.
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio); // 고해상도(레티나 등) 모니터에서도 선명하게 보이게 합니다.
container.appendChild(renderer.domElement); // 완성된 캔버스를 HTML에 집어넣습니다.

/* --- [파티클(별가루) 배경 추가] --- */
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1000; // 별가루 1000개
const posArray = new Float32Array(particlesCount * 3); // x, y, z 좌표를 담아야 하므로 3배수 배열 생성

for (let i = 0; i < particlesCount * 3; i++) {
    // -30 ~ +30 공간 안에 무작위(Math.random)로 점들을 뿌려줍니다.
    posArray[i] = (Math.random() - 0.5) * 60;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

const particlesMaterial = new THREE.PointsMaterial({
    size: 0.08, color: 0x00d4ff, transparent: true, opacity: 0.8,
    // AdditiveBlending: 겹쳐질수록 빛이 더해져서 더 밝게 빛나는(홀로그램스러운) 효과를 만듭니다.
    blending: THREE.AdditiveBlending
});
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh); // 무대에 파티클을 올립니다.

/* --- [홀로그램 배너 캐러셀] --- */
const carouselGroup = new THREE.Group(); // 배너들을 하나로 묶을 그룹
scene.add(carouselGroup);

const bannerCount = 8;
const radius = 13; // 원의 반지름 (카메라에서 얼마나 떨어질지 결정)
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

// 이미지 배열과 순서를 맞춰서 작성하세요
const bannerURLs = [
    '/board/anotherclub/CUVIX',       // CUVIC 배너 클릭 시 이동할 URL
    '/board/anotherclub/EMsys',       // EMSYS 배너 클릭 시 이동할 URL
    '/board/anotherclub/G Dev F.C',        // G.DEV.FC 배너 클릭 시 이동할 URL
    '/board/anotherclub/Next.Net',     // NEST.NET 배너 클릭 시 이동할 URL
    '/board/anotherclub/NOVA',        // NOVA 배너 클릭 시 이동할 URL
    '/board/anotherclub/PDA',         // PDA 배너 클릭 시 이동할 URL
    '/board/anotherclub/SAMMura',     // SAMMaru 배너 클릭 시 이동할 URL
    '/board/anotherclub/TUX',         // TUX 배너 클릭 시 이동할 URL
];

const textureLoader = new THREE.TextureLoader();

for (let i = 0; i < bannerCount; i++) {
    // 원을 360도(Math.PI * 2)로 10등분하여 각 배너의 각도를 정합니다.
    const angle = (i / bannerCount) * Math.PI * 2;
    const geometry = new THREE.BoxGeometry(4.5, 7, 0.1);

    /*유현석이 수정(배너에 이미지 추가) */
    const texture = textureLoader.load(bannerImages[i]);
    const material = new THREE.MeshBasicMaterial({
        map: texture,          // 이미지를 텍스처로 사용
        transparent: true,
        opacity: 0.9
    });
    const mesh = new THREE.Mesh(geometry, material);

    // 배너의 네온 테두리를 만들기 위해 도형의 '모서리 선(Edges)'만 추출합니다.
    const edges = new THREE.EdgesGeometry(geometry);
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0xffffff, // 모든 배너 모서리 흰색으로 통일
        linewidth: 2
    });
    const line = new THREE.LineSegments(edges, lineMaterial);
    mesh.add(line); // 테두리를 배너 위에 덮어씌웁니다.

    // 삼각함수(cos, sin)를 이용해서 배너들을 원형(반지름 13)으로 둥글게 배치합니다.
    mesh.position.x = Math.cos(angle) * radius;
    mesh.position.z = Math.sin(angle) * radius;

    // 모든 배너가 일직선상에 있지 않고, 위아래로 물결치듯 배치되게 합니다.
    mesh.position.y = Math.sin(angle * 3) * 1.5;

    // 각각의 배너가 항상 중앙(카메라 쪽)을 쳐다보도록 각도를 틀어줍니다.
    mesh.rotation.y = -angle + Math.PI / 2;

    //각 배너에 URL 링크 설정
    mesh.userData.url = bannerURLs[i];


    carouselGroup.add(mesh); // 그룹에 조립된 배너를 추가합니다.
}

/* --- [마우스 드래그 상호작용] --- */
let isDragging = false;
let previousMouseX = 0; let previousMouseY = 0;
let targetRotationY = 0; // 목표 좌우 회전값
let targetRotationX = 0; // 목표 상하 기울기값
const autoRotateSpeed = 0.002; // 가만히 둬도 자동으로 돌아가는 속도

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


// 사용자가 브라우저 창 크기를 줄이거나 늘리면, 카메라 비율과 화면 캔버스 크기를 다시 세팅해 찌그러지지 않게 합니다.
window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

/* --- [메인 애니메이션 루프] --- */
const clock = new THREE.Clock(); // 시간 측정기 (흘러간 시간을 구함)

function animate() {
    // 1초에 60번(60프레임)씩 이 함수를 스스로 계속 호출해서 끊김 없는 애니메이션을 만듭니다.
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime(); // 사이트가 켜진 후 몇 초가 지났는지 잽니다.

    if (!isDragging) {
        targetRotationY += autoRotateSpeed; // 드래그 중이 아니면 천천히 자동 회전합니다.
    }

    // ★Lerp(선형 보간): 현재 각도에서 목표 각도(targetRotation)로 한번에 빡! 움직이지 않고 10%(0.1)씩 부드럽게 다가가서 관성이 있는 것처럼 연출합니다.
    carouselGroup.rotation.y += (targetRotationY - carouselGroup.rotation.y) * 0.1;
    carouselGroup.rotation.x += (targetRotationX - carouselGroup.rotation.x) * 0.1;

    // 파티클 뭉치가 전체적으로 서서히 돌아가면서 위아래로 천천히 떠다니도록 만듭니다 (우주 공간 느낌).
    particlesMesh.rotation.y = elapsedTime * 0.05;
    particlesMesh.position.y = Math.sin(elapsedTime * 0.5) * 2;

    // 각각의 배너들도 시간(elapsedTime)에 따라 Math.sin 파동 곡선을 타며 둥둥 떠다니는 애니메이션을 적용합니다.
    carouselGroup.children.forEach((banner, idx) => {
        banner.position.y = Math.sin(elapsedTime * 2 + idx) * 0.5;
    });

    // 최종적으로 변동된 카메라와 무대의 상황을 화면(캔버스)에 찍어냅니다.
    renderer.render(scene, camera);
}
animate(); // 무한 반복 함수 최초 실행!

/* =========================================
   [자바스크립트 파트 5: Intersection Observer (스크롤 애니메이션)]
========================================= */
const boardSection = document.getElementById('board-section');

// IntersectionObserver는 스크롤을 내리다 특정 요소가 '화면에 들어왔는지' 감지해주는 최신 자바스크립트 API입니다.
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        // isIntersecting은 요소가 화면(viewport) 안으로 들어오면 true가 됩니다.
        if (entry.isIntersecting) {
            // 화면에 들어왔다면 요소에 'is-visible' 클래스를 붙여줍니다. 
            // (이 클래스가 붙으면 위쪽 CSS에 정의해둔 애니메이션이 발동하여 카드가 슈웅 나타납니다.)
            boardSection.classList.add('is-visible');

            // 카드가 한 번 나타났으면 그 이후엔 스크롤을 올렸다 내려도 다시 실행할 필요 없으니 감시를 끕니다.
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 }); // threshold 0.3: 요소의 전체 크기 중 30%가 화면에 보일 때 작동하라는 뜻입니다.

// 위에서 설정한 규칙대로 boardSection 감시를 시작합니다.
observer.observe(boardSection);