(function () {
    'use strict';

    var X_MIN = -5, X_MAX = 5;
    var Y_VALUES = [-5, -4, -3, -2, -1, 0, 1, 2, 3];

    var form = document.getElementById('check-form');
    var xInput = document.getElementById('x');
    var yInput = document.getElementById('y');
    var rInput = document.getElementById('r');
    var errorBox = document.getElementById('form-error');
    var canvas = document.getElementById('graph');
    var ctx = canvas.getContext('2d');
    var history = window.AREA_HISTORY || [];

    function css(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    function selectChip(groupId, input, value) {
        var chips = document.querySelectorAll('#' + groupId + ' .chip');
        chips.forEach(function (chip) {
            chip.setAttribute('aria-pressed', String(chip.dataset.value === String(value)));
        });
        input.value = value === null ? '' : String(value);
    }

    ['y-group', 'r-group'].forEach(function (id) {
        var input = id === 'y-group' ? yInput : rInput;
        document.getElementById(id).addEventListener('click', function (e) {
            var chip = e.target.closest('.chip');
            if (!chip) { return; }
            selectChip(id, input, chip.dataset.value);
            if (input === rInput) { draw(); }
        });
    });

    function showError(message) {
        errorBox.textContent = message;
        errorBox.hidden = !message;
    }

    function validate() {
        var problems = [];
        var x = xInput.value.trim().replace(',', '.');
        xInput.classList.remove('invalid');
        if (x === '' || isNaN(Number(x))) {
            problems.push('X должен быть числом');
        } else if (Number(x) < X_MIN || Number(x) > X_MAX) {
            problems.push('X должен быть от -5 до 5');
        }
        if (yInput.value === '') { problems.push('Выберите Y'); }
        if (rInput.value === '') { problems.push('Выберите R'); }
        if (problems.length && /^X/.test(problems[0])) { xInput.classList.add('invalid'); }
        showError(problems.join('. '));
        return problems.length === 0;
    }

    form.addEventListener('submit', function (e) {
        if (!validate()) { e.preventDefault(); }
    });

    // ---------- график ----------

    var SIZE = canvas.width;
    var CENTER = SIZE / 2;
    var SCALE = 38;            // пикселей на единицу
    var UNIT_MAX = 5.5;

    function toPx(x, y) { return [CENTER + x * SCALE, CENTER - y * SCALE]; }

    function currentR() {
        var r = parseFloat(rInput.value);
        return isNaN(r) ? null : r;
    }

    function drawArea(r) {
        var h = r / 2;
        ctx.fillStyle = css('--accent');
        ctx.globalAlpha = 0.28;
        ctx.beginPath();
        // квадрат в III четверти
        var a = toPx(-r, -r), b = toPx(0, 0);
        ctx.rect(a[0], a[1], b[0] - a[0], b[1] - a[1]);
        ctx.fill();
        // четверть круга во II четверти
        var o = toPx(0, 0);
        ctx.beginPath();
        ctx.moveTo(o[0], o[1]);
        ctx.arc(o[0], o[1], h * SCALE, Math.PI, 1.5 * Math.PI);
        ctx.closePath();
        ctx.fill();
        // треугольник в I четверти
        var p1 = toPx(h, 0), p2 = toPx(0, h);
        ctx.beginPath();
        ctx.moveTo(o[0], o[1]);
        ctx.lineTo(p1[0], p1[1]);
        ctx.lineTo(p2[0], p2[1]);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
    }

    function drawAxes(r) {
        var line = css('--muted');
        ctx.strokeStyle = line;
        ctx.fillStyle = line;
        ctx.lineWidth = 1;
        ctx.font = '12px system-ui, sans-serif';

        ctx.beginPath();
        ctx.moveTo(8, CENTER); ctx.lineTo(SIZE - 8, CENTER);
        ctx.moveTo(CENTER, 8); ctx.lineTo(CENTER, SIZE - 8);
        ctx.stroke();

        var labels = r === null ? [] : [-r, -r / 2, r / 2, r];
        labels.forEach(function (v) {
            var px = toPx(v, 0), py = toPx(0, v);
            ctx.beginPath();
            ctx.moveTo(px[0], CENTER - 3); ctx.lineTo(px[0], CENTER + 3);
            ctx.moveTo(CENTER - 3, py[1]); ctx.lineTo(CENTER + 3, py[1]);
            ctx.stroke();
            ctx.fillText(String(v), px[0] - 8, CENTER + 18);
            ctx.fillText(String(v), CENTER + 8, py[1] + 4);
        });
        ctx.fillText('x', SIZE - 16, CENTER - 8);
        ctx.fillText('y', CENTER + 8, 18);
    }

    function drawPoints(r) {
        history.forEach(function (p) {
            // показываем только точки, посчитанные для выбранного R
            if (r === null || p.r !== r) { return; }
            var xy = toPx(p.x, p.y);
            ctx.beginPath();
            ctx.arc(xy[0], xy[1], 4, 0, 2 * Math.PI);
            ctx.fillStyle = p.hit ? css('--ok') : css('--miss');
            ctx.fill();
        });
    }

    function draw() {
        ctx.clearRect(0, 0, SIZE, SIZE);
        var r = currentR();
        if (r !== null) { drawArea(r); }
        drawAxes(r);
        drawPoints(r);
    }

    canvas.addEventListener('click', function (e) {
        var r = currentR();
        if (r === null) {
            showError('Сначала выберите R');
            return;
        }
        var rect = canvas.getBoundingClientRect();
        var scaleX = SIZE / rect.width;
        var px = (e.clientX - rect.left) * scaleX;
        var py = (e.clientY - rect.top) * scaleX;
        var x = (px - CENTER) / SCALE;
        var y = (CENTER - py) / SCALE;

        if (x < X_MIN || x > X_MAX) { showError('X вне допустимого диапазона'); return; }
        var nearest = Y_VALUES.reduce(function (best, v) {
            return Math.abs(v - y) < Math.abs(best - y) ? v : best;
        });
        xInput.value = (Math.round(x * 100) / 100).toString();
        selectChip('y-group', yInput, nearest);
        showError('');
        form.submit();
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
    draw();
})();
