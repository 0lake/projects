package web;

import area.CheckResult;
import area.Checker;
import area.InvalidInputException;
import area.RectTriangleCircle;
import jakarta.enterprise.context.SessionScoped;
import jakarta.faces.application.FacesMessage;
import jakarta.faces.context.FacesContext;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import java.io.Serializable;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

/**
 * Состояние страницы с формой: значения полей, проверка и история текущей сессии.
 */
@Named("areaBean")
@SessionScoped
public class AreaBean implements Serializable {
    private static final long serialVersionUID = 1L;
    static final int HISTORY_LIMIT = 10;

    private static final Checker CHECKER = new Checker(new RectTriangleCircle());

    @Inject
    @SuppressWarnings("serial")
    private PointRepository repository;

    private String x = "";
    private String y = "";
    private String r = "";

    /** Проверяет точку из формы и сохраняет результат. */
    public void check() {
        FacesContext context = FacesContext.getCurrentInstance();
        try {
            CheckResult result = CHECKER.check(x, y, r);
            repository.save(sessionId(context), result);
        } catch (InvalidInputException e) {
            for (String problem : e.problems()) {
                context.addMessage(null, new FacesMessage(FacesMessage.SEVERITY_ERROR, problem, null));
            }
        } catch (IllegalStateException e) {
            context.addMessage(null, new FacesMessage(FacesMessage.SEVERITY_ERROR,
                    "База данных недоступна, попробуйте позже", null));
        }
        pushPoints(context);
    }

    /** Очищает историю текущей сессии. */
    public void clear() {
        FacesContext context = FacesContext.getCurrentInstance();
        repository.clear(sessionId(context));
        pushPoints(context);
    }

    /** @return последние проверки сессии для таблицы */
    public List<CheckResult> getHistory() {
        return repository.latest(sessionId(FacesContext.getCurrentInstance()), HISTORY_LIMIT);
    }

    /** @return точки истории в виде JSON-массива для графика; только числа и логические значения */
    public String getPointsJson() {
        return toJson(getHistory());
    }

    static String toJson(List<CheckResult> items) {
        return items.stream()
                .map(p -> String.format(Locale.ROOT, "{\"x\":%s,\"y\":%s,\"r\":%s,\"hit\":%b}",
                        p.x(), p.y(), p.r(), p.hit()))
                .collect(Collectors.joining(",", "[", "]"));
    }

    /** Обновляет точки на графике после AJAX-запроса. */
    private void pushPoints(FacesContext context) {
        try {
            org.primefaces.PrimeFaces.current().executeScript("Area.load(" + toJson(getHistory()) + ");");
        } catch (IllegalStateException e) {
            // история недоступна вместе с базой, график остаётся прежним
        }
    }

    private static String sessionId(FacesContext context) {
        return context.getExternalContext().getSessionId(true);
    }

    public String getX() {
        return x;
    }

    public void setX(String x) {
        this.x = x;
    }

    public String getY() {
        return y;
    }

    public void setY(String y) {
        this.y = y;
    }

    public String getR() {
        return r;
    }

    public void setR(String r) {
        this.r = r;
    }

    /** @return допустимые значения R для списка выбора */
    public List<String> getRadiusOptions() {
        return area.Radius.VALUES.stream().map(v -> v == Math.rint(v) ? String.valueOf(v.longValue()) : v.toString())
                .collect(Collectors.toList());
    }
}
