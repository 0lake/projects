# Java

Проекты на Java: архитектура приложений, сеть, многопоточность, работа с базой данных, тесты и сборка.

<table>
  <tr>
    <td width="46%">
      <a href="./flat-collection-manager">
        <img src="flat-collection-manager/assets/banner.svg?v=12" alt="Flat Manager: клиент-серверное приложение на Java с авторизацией, многопоточностью и PostgreSQL" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./flat-collection-manager">Flat Manager: клиент-серверное приложение для коллекции квартир</a></h3>
      <p>Многомодульный проект на Gradle: консольный клиент на NIO, сервер с пулами потоков и конвейером на CompletableFuture, хранение в PostgreSQL, регистрация и права владельца. Хранилище подставляется (память или JDBC), поэтому логика тестируется без базы. 58 тестов, включая обмен по настоящему сокету, CI с живым PostgreSQL.</p>
      <p>
        <img src="https://img.shields.io/badge/Java_21-E76F00?style=flat-square&logo=openjdk&logoColor=white" alt="Java">
        <img src="https://img.shields.io/badge/Gradle-02303A?style=flat-square&logo=gradle&logoColor=white" alt="Gradle">
        <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
        <img src="https://img.shields.io/badge/JUnit-25A162?style=flat-square&logo=junit5&logoColor=white" alt="JUnit">
      </p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="46%">
      <a href="./web-area-checker">
        <img src="web-area-checker/assets/banner.svg?v=1" alt="Area Checker: одна задача проверки точки в области на двух веб-стеках" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="./web-area-checker">Area Checker: одна задача на двух веб-стеках</a></h3>
      <p>Проверка попадания точки в область с графиком и историей. Две реализации в одном проекте: сервлеты и JSP, а также JSF с PrimeFaces, CDI и PostgreSQL. Геометрия и валидация вынесены в общее ядро без зависимостей и покрыты тестами на границах фигур, настройки базы берутся из окружения, CI собирает оба WAR-файла.</p>
      <p>
        <img src="https://img.shields.io/badge/Java_17-E76F00?style=flat-square&logo=openjdk&logoColor=white" alt="Java">
        <img src="https://img.shields.io/badge/Jakarta_EE-6C5CE7?style=flat-square&logo=jakartaee&logoColor=white" alt="Jakarta EE">
        <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
        <img src="https://img.shields.io/badge/Gradle-02303A?style=flat-square&logo=gradle&logoColor=white" alt="Gradle">
      </p>
    </td>
  </tr>
</table>

[← Все проекты](../)
