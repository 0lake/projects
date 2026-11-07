package web;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Единая точка входа. Запрос с параметрами x, y и r передаётся на проверку,
 * остальные запросы получают главную страницу. Сама проверка здесь не выполняется.
 */
@WebServlet(name = "controller", urlPatterns = "/controller")
public class ControllerServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        dispatch(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        dispatch(req, resp);
    }

    private void dispatch(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        if ("clear".equals(req.getParameter("action")) && "POST".equals(req.getMethod())) {
            ResultStore store = (ResultStore) req.getSession().getAttribute(ResultStore.ATTRIBUTE);
            if (store != null) {
                store.clear();
            }
            resp.sendRedirect(req.getContextPath() + "/controller");
            return;
        }
        boolean hasInput = req.getParameter("x") != null
                || req.getParameter("y") != null
                || req.getParameter("r") != null;
        String target = hasInput ? "/check" : "/WEB-INF/views/index.jsp";
        req.getRequestDispatcher(target).forward(req, resp);
    }
}
