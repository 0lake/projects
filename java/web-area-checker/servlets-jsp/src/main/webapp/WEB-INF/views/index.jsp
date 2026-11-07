<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<c:set var="ctx" value="${pageContext.request.contextPath}"/>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Area Checker</title>
    <link rel="stylesheet" href="${ctx}/css/styles.css">
</head>
<body>
<main class="shell">
    <header class="top">
        <h1>Area Checker</h1>
        <p class="muted">Проверка попадания точки в область. Servlets и JSP.</p>
    </header>

    <div class="layout">
        <section class="card">
            <h2>Точка</h2>
            <form id="check-form" action="${ctx}/controller" method="post" novalidate>
                <div class="field">
                    <label for="x">X, от -5 до 5</label>
                    <input id="x" name="x" type="text" inputmode="decimal" autocomplete="off" placeholder="0">
                </div>

                <div class="field">
                    <span class="label">Y</span>
                    <div class="chips" role="group" aria-label="Значение Y" id="y-group">
                        <c:forEach var="v" begin="-5" end="3">
                            <button type="button" class="chip" data-value="${v}">${v}</button>
                        </c:forEach>
                    </div>
                    <input type="hidden" id="y" name="y">
                </div>

                <div class="field">
                    <span class="label">R</span>
                    <div class="chips" role="group" aria-label="Значение R" id="r-group">
                        <c:forEach var="v" items="${['1','1.5','2','2.5','3']}">
                            <button type="button" class="chip" data-value="${v}">${v}</button>
                        </c:forEach>
                    </div>
                    <input type="hidden" id="r" name="r">
                </div>

                <p id="form-error" class="error" role="alert" hidden></p>

                <button type="submit" class="btn">Проверить</button>
            </form>
            <p class="hint">Точку можно поставить кликом по графику, когда выбран R.</p>
        </section>

        <section class="card graph-card">
            <h2>График</h2>
            <canvas id="graph" width="420" height="420" aria-label="График области"></canvas>
        </section>
    </div>

    <section class="card">
        <div class="row-between">
            <h2>История</h2>
            <form action="${ctx}/controller" method="post">
                <input type="hidden" name="action" value="clear">
                <button type="submit" class="btn ghost">Очистить</button>
            </form>
        </div>
        <jsp:include page="history.jspf"/>
    </section>
</main>
<script>
    window.AREA_HISTORY = [
        <c:forEach var="row" items="${sessionScope.resultStore.all()}" varStatus="s">
        {x: ${row.x}, y: ${row.y}, r: ${row.r}, hit: ${row.hit}}<c:if test="${!s.last}">,</c:if>
        </c:forEach>
    ];
</script>
<script src="${ctx}/js/app.js"></script>
</body>
</html>
