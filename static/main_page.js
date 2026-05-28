document.addEventListener('DOMContentLoaded', () => {
    
    const track = document.getElementById('bannerTrack');
    let scrollAmount = 0;
    let autoScrollInterval;

    // 배너를 자동으로 스크롤하는 함수
    function startAutoScroll() {
        autoScrollInterval = setInterval(() => {
            // 오른쪽으로 조금씩 이동
            track.scrollLeft += 1; 
            
            // 만약 끝까지 스크롤 되었다면 다시 처음으로 위치를 되돌림 (무한 루프 느낌)
            if (track.scrollLeft >= (track.scrollWidth - track.clientWidth)) {
                track.scrollLeft = 0;
            }
        }, 20); // 20밀리초마다 실행 (숫자가 작을수록 부드럽고 빠름)
    }

    // 마우스를 올렸을 때는 스크롤을 멈춰서 내용을 볼 수 있게 함
    track.addEventListener('mouseenter', () => {
        clearInterval(autoScrollInterval);
    });

    // 마우스가 영역을 벗어나면 다시 자동 스크롤 시작
    track.addEventListener('mouseleave', () => {
        startAutoScroll();
    });

    // 페이지 로딩 시 자동 스크롤 시작
    startAutoScroll();

});