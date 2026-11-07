(function () {
    'use strict';
    var el = document.getElementById('time');
    if (!el) { return; }
    function tick() {
        el.textContent = new Date().toLocaleTimeString('ru-RU');
    }
    tick();
    setInterval(tick, 1000);
})();
