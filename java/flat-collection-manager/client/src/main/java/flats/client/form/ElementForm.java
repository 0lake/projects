package flats.client.form;

import flats.client.io.InputSource;
import flats.common.model.Coordinates;
import flats.common.model.FlatDraft;
import flats.common.model.House;
import flats.common.model.Validation;
import flats.common.model.ValidationException;
import flats.common.model.View;

import java.io.IOException;
import java.io.PrintStream;
import java.io.UncheckedIOException;
import java.util.function.Function;

/**
 * Пошаговый ввод квартиры. В интерактивном режиме при ошибке поле запрашивается заново,
 * в скрипте ошибка прерывает команду, чтобы испорченный скрипт не создал неверные данные.
 */
public final class ElementForm {
    private final InputSource input;
    private final PrintStream out;

    public ElementForm(InputSource input, PrintStream out) {
        this.input = input;
        this.out = out;
    }

    /**
     * Запрашивает все поля.
     *
     * @throws ValidationException если в скрипте встретилось неверное значение
     * @throws InputEnded          если ввод закончился
     */
    public FlatDraft read() {
        String name = ask("Введите название квартиры:", Validation::requireNotBlank);
        Long x = ask("Введите координату x (целое число):", Long::parseLong);
        Float y = ask("Введите координату y (число больше " + (int) Coordinates.MIN_Y + "):", text -> {
            float value = Float.parseFloat(text);
            if (!(value > Coordinates.MIN_Y)) {
                throw new ValidationException("Значение должно быть больше " + (int) Coordinates.MIN_Y);
            }
            return value;
        });
        Integer area = askOptional("Введите площадь (целое число больше 0, пустая строка если не задана):",
                text -> positive(Integer.parseInt(text)));
        int rooms = ask("Введите количество комнат (целое число больше 0):",
                text -> positive(Integer.parseInt(text)));
        int height = ask("Введите высоту потолков (целое число больше 0):",
                text -> positive(Integer.parseInt(text)));
        Float kitchen = ask("Введите площадь кухни (число больше 0):", text -> {
            float value = Float.parseFloat(text);
            if (!(value > 0)) {
                throw new ValidationException("Значение должно быть больше 0");
            }
            return value;
        });
        View view = ask("Введите вид из окна (" + View.names() + "):",
                text -> View.valueOf(text.toUpperCase()));
        String houseName = ask("Введите название дома:", text -> text);
        Integer year = ask("Введите год постройки дома (целое число больше 0):",
                text -> positive(Integer.parseInt(text)));
        Long perFloor = ask("Введите количество квартир на этаже (целое число больше 0):",
                text -> positive(Long.parseLong(text)));
        long lifts = ask("Введите количество лифтов (целое число больше 0):",
                text -> positive(Long.parseLong(text)));
        return new FlatDraft(name, new Coordinates(x, y), area, rooms, height, kitchen, view,
                new House(houseName, year, perFloor, lifts));
    }

    private static int positive(int value) {
        Validation.positive(value, "значение");
        return value;
    }

    private static long positive(long value) {
        Validation.positive(value, "значение");
        return value;
    }

    private <T> T ask(String prompt, Function<String, T> parser) {
        while (true) {
            String line = prompt(prompt);
            try {
                return parser.apply(line.strip());
            } catch (IllegalArgumentException e) {
                fail(e);
            }
        }
    }

    private <T> T askOptional(String prompt, Function<String, T> parser) {
        while (true) {
            String line = prompt(prompt).strip();
            if (line.isEmpty()) {
                return null;
            }
            try {
                return parser.apply(line);
            } catch (IllegalArgumentException e) {
                fail(e);
            }
        }
    }

    private String prompt(String prompt) {
        if (input.interactive()) {
            out.print(prompt + " ");
            out.flush();
        }
        try {
            String line = input.readLine();
            if (line == null) {
                throw new InputEnded();
            }
            return line;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private void fail(IllegalArgumentException e) {
        String reason = e instanceof NumberFormatException ? "Некорректное число" : e.getMessage();
        if (!input.interactive()) {
            throw new ValidationException("Ошибка в скрипте: " + reason);
        }
        out.println(reason + ". Повторите ввод.");
    }
}
