<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<c:set var="ctx" value="${pageContext.request.contextPath}"/>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Результат</title>
    <link rel="stylesheet" href="${ctx}/css/styles.css">
</head>
<body>
<main class="shell narrow">
    <section class="card">
        <c:choose>
            <c:when test="${not empty problems}">
                <h1>Данные не приняты</h1>
                <ul class="error-list">
                    <c:forEach var="p" items="${problems}">
                        <li><c:out value="${p}"/></li>
                    </c:forEach>
                </ul>
            </c:when>
            <c:otherwise>
                <h1>${result.hit ? 'Попадание' : 'Мимо'}</h1>
                <dl class="facts">
                    <dt>X</dt><dd><c:out value="${result.x}"/></dd>
                    <dt>Y</dt><dd><c:out value="${result.y}"/></dd>
                    <dt>R</dt><dd><c:out value="${result.r}"/></dd>
                    <dt>Время (UTC)</dt><dd><c:out value="${result.checkedAt}"/></dd>
                </dl>
            </c:otherwise>
        </c:choose>
        <a class="btn" href="${ctx}/controller">Назад</a>
    </section>

    <section class="card">
        <h2>История</h2>
        <jsp:include page="history.jspf"/>
    </section>
</main>
</body>
</html>
