// 드롭다운 열기/닫기 토글
function toggleDropdown(event, dropdownId) {
    event.preventDefault();

    const target = document.getElementById(dropdownId);
    const isOpen = target.classList.contains('open');

    // 열려있는 모든 드롭다운 닫기
    document.querySelectorAll('.app-navbar .dropdown.open').forEach(function(el) {
        el.classList.remove('open');
    });

    // 클릭한 드롭다운이 닫혀 있었으면 열기
    if (!isOpen) {
        target.classList.add('open');
    }
}

// 드롭다운 외부 클릭 시 닫기
document.addEventListener('click', function(event) {
    if (!event.target.closest('.app-navbar .dropdown')) {
        document.querySelectorAll('.app-navbar .dropdown.open').forEach(function(el) {
            el.classList.remove('open');
        });
    }
});
