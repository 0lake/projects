(function () {
    'use strict';

    var NS = 'http://www.w3.org/2000/svg';
    var C = 200;           // центр в единицах SVG
    var SCALE = 38;        // единиц SVG на единицу графика
    var X_MIN = -3, X_MAX = 3, Y_MIN = -5, Y_MAX = 3;

    var svg = document.getElementById('graph');
    var shapes = document.getElementById('area-shapes');
    var axes = document.getElementById('axes');
    var pointsLayer = document.getElementById('points');
    var points = [];

    function el(name, attrs) {
        var node = document.createElementNS(NS, name);
        Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
        return node;
    }

    function px(v) { return C + v * SCALE; }
    function py(v) { return C - v * SCALE; }
    function clear(node) { while (node.firstChild) { node.removeChild(node.firstChild); } }

    function currentR() {
        var checked = document.querySelector('input[name="form:r"]:checked');
        return checked ? parseFloat(checked.value) : null;
    }

    function drawShapes(r) {
        clear(shapes);
        if (r === null) { return; }
        var h = r / 2;
        // прямоугольник во II четверти
        shapes.appendChild(el('rect', {
            x: px(-h), y: py(r), width: h * SCALE, height: r * SCALE, 'class': 'shape'
        }));
        // треугольник в IV четверти: (0,0), (R,0), (0,-R/2)
        shapes.appendChild(el('polygon', {
            points: [px(0), py(0), px(r), py(0), px(0), py(-h)].join(' '), 'class': 'shape'
        }));
        // четверть круга в I четверти радиуса R/2
        shapes.appendChild(el('path', {
            d: 'M ' + px(0) + ' ' + py(0) + ' L ' + px(h) + ' ' + py(0) +
               ' A ' + (h * SCALE) + ' ' + (h * SCALE) + ' 0 0 0 ' + px(0) + ' ' + py(h) + ' Z',
            'class': 'shape'
        }));
    }

    function drawAxes(r) {
        clear(axes);
        axes.appendChild(el('line', { x1: 8, y1: C, x2: 392, y2: C, 'class': 'axis' }));
        axes.appendChild(el('line', { x1: C, y1: 8, x2: C, y2: 392, 'class': 'axis' }));
        if (r === null) { return; }
        [-r, -r / 2, r / 2, r].forEach(function (v) {
            axes.appendChild(el('line', { x1: px(v), y1: C - 3, x2: px(v), y2: C + 3, 'class': 'axis' }));
            axes.appendChild(el('line', { x1: C - 3, y1: py(v), x2: C + 3, y2: py(v), 'class': 'axis' }));
            var tx = el('text', { x: px(v), y: C + 18, 'text-anchor': 'middle', 'class': 'tick' });
            tx.textContent = String(v);
            axes.appendChild(tx);
            var ty = el('text', { x: C + 8, y: py(v) + 4, 'class': 'tick' });
            ty.textContent = String(v);
            axes.appendChild(ty);
        });
    }

    function drawPoints(r) {
        clear(pointsLayer);
        points.forEach(function (p) {
            if (r === null || p.r !== r) { return; }
            pointsLayer.appendChild(el('circle', {
                cx: px(p.x), cy: py(p.y), r: 4, 'class': p.hit ? 'dot ok' : 'dot miss'
            }));
        });
    }

    function draw() {
        var r = currentR();
        drawShapes(r);
        drawAxes(r);
        drawPoints(r);
    }

    function setValue(id, value) {
        var input = document.getElementById(id);
        if (input) { input.value = value; }
    }

    svg.addEventListener('click', function (e) {
        var r = currentR();
        if (r === null) { return; }
        // перевод координат клика в систему SVG, не зависит от масштаба страницы
        var pt = svg.createSVGPoint();
        pt.x = e.clientX;
        pt.y = e.clientY;
        var local = pt.matrixTransform(svg.getScreenCTM().inverse());
        var x = (local.x - C) / SCALE;
        var y = (C - local.y) / SCALE;
        if (x < X_MIN || x > X_MAX || y < Y_MIN || y > Y_MAX) { return; }
        setValue('form:x', (Math.round(x * 100) / 100).toString());
        setValue('form:y', (Math.round(y * 100) / 100).toString());
        document.getElementById('form:submit').click();
    });

    window.Area = {
        draw: draw,
        load: function (list) { points = list; draw(); }
    };

    var initial = document.getElementById('initial-points');
    try {
        points = JSON.parse(initial.getAttribute('data-points') || '[]');
    } catch (err) {
        points = [];
    }
    draw();
})();
