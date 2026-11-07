<%@ page contentType="text/html;charset=UTF-8" isErrorPage="true" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ошибка</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/styles.css">
</head>
<body>
<main class="shell narrow">
    <section class="card">
        <h1>Что-то пошло не так</h1>
        <p class="muted">Страница не найдена или запрос не удалось обработать.</p>
        <a class="btn" href="${pageContext.request.contextPath}/controller">На главную</a>
    </section>
</main>
</body>
</html>
