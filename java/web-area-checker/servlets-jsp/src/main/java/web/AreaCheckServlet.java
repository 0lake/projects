package web;

import area.CheckResult;
import area.Checker;
import area.CircleTriangleSquare;
import area.InvalidInputException;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.util.List;

/**
 * Проверяет попадание точки и показывает страницу результата.
 * Напрямую не вызывается: запрос приходит через {@link ControllerServlet}.
 */
@WebServlet(name = "areaCheck", urlPatterns = "/check")
public class AreaCheckServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    private final transient Checker checker = new Checker(new CircleTriangleSquare());

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // Прямые обращения к /check отправляем в контроллер
        if (req.getDispatcherType() != jakarta.servlet.DispatcherType.FORWARD) {
            resp.sendRedirect(req.getContextPath() + "/controller");
            return;
        }
        if (!"GET".equals(req.getMethod()) && !"POST".equals(req.getMethod())) {
            resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED);
            return;
        }

        try {
            CheckResult result = checker.check(
                    req.getParameter("x"), req.getParameter("y"), req.getParameter("r"));
            HttpSession session = req.getSession();
            ResultStore store = (ResultStore) session.getAttribute(ResultStore.ATTRIBUTE);
            if (store == null) {
                store = new ResultStore();
                session.setAttribute(ResultStore.ATTRIBUTE, store);
            }
            store.add(result);
            req.setAttribute("result", result);
        } catch (InvalidInputException e) {
            resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            req.setAttribute("problems", List.copyOf(e.problems()));
        }
        req.getRequestDispatcher("/WEB-INF/views/result.jsp").forward(req, resp);
    }
}
