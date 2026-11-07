package area;

import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Разбирает и проверяет входные данные, затем определяет попадание в область.
 * Не зависит ни от сервлетов, ни от JSF, поэтому проверяется обычными тестами.
 */
public final class Checker {
    private static final int MAX_NUMBER_LENGTH = 24;

    private final Region region;
    private final Clock clock;

    public Checker(Region region) {
        this(region, Clock.systemUTC());
    }

    public Checker(Region region, Clock clock) {
        this.region = region;
        this.clock = clock;
    }

    /** @return область, с которой работает проверка */
    public Region region() {
        return region;
    }

    /**
     * Разбирает строки в числа и проверяет диапазоны. Запятая принимается как десятичный разделитель.
     *
     * @throws InvalidInputException если хотя бы одно значение неверно; в исключении все проблемы сразу
     */
    public CheckInput parse(String x, String y, String r) throws InvalidInputException {
        List<String> problems = new ArrayList<>();
        Double xv = number("X", x, problems);
        Double yv = number("Y", y, problems);
        Double rv = number("R", r, problems);

        if (xv != null && !region.xRange().contains(xv)) {
            problems.add("X должен быть от " + format(region.xRange().min()) + " до " + format(region.xRange().max()));
        }
        if (yv != null && !region.yRange().contains(yv)) {
            problems.add("Y должен быть от " + format(region.yRange().min()) + " до " + format(region.yRange().max()));
        }
        if (rv != null && !Radius.isAllowed(rv)) {
            problems.add("R должен быть одним из: 1, 1.5, 2, 2.5, 3");
        }
        if (!problems.isEmpty()) {
            throw new InvalidInputException(problems);
        }
        return new CheckInput(xv, yv, rv);
    }

    /** Определяет попадание точки и фиксирует время проверки. */
    public CheckResult check(CheckInput input) {
        boolean hit = region.contains(input.x(), input.y(), input.r());
        return new CheckResult(input, hit, clock.instant());
    }

    /** Разбор и проверка за один шаг. */
    public CheckResult check(String x, String y, String r) throws InvalidInputException {
        return check(parse(x, y, r));
    }

    private static Double number(String name, String text, List<String> problems) {
        if (text == null || text.isBlank()) {
            problems.add(name + " не указан");
            return null;
        }
        String normalized = text.strip().replace(',', '.');
        if (normalized.length() > MAX_NUMBER_LENGTH) {
            problems.add(name + " слишком длинный");
            return null;
        }
        try {
            double value = Double.parseDouble(normalized);
            if (!Double.isFinite(value)) {
                problems.add(name + " должен быть конечным числом");
                return null;
            }
            return value;
        } catch (NumberFormatException e) {
            problems.add(name + " не число");
            return null;
        }
    }

    private static String format(double value) {
        return value == Math.rint(value) ? String.valueOf((long) value) : String.format(Locale.ROOT, "%s", value);
    }
}
