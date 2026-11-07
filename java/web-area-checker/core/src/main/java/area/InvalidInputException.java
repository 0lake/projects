package area;

import java.util.List;

/**
 * Входные данные не прошли проверку. Содержит все найденные проблемы, а не только первую.
 */
public class InvalidInputException extends Exception {
    private static final long serialVersionUID = 1L;

    @SuppressWarnings("serial")
    private final List<String> problems;

    public InvalidInputException(List<String> problems) {
        super(String.join("; ", problems));
        this.problems = List.copyOf(problems);
    }

    /** @return сообщения для пользователя, по одному на каждое неверное поле */
    public List<String> problems() {
        return problems;
    }
}
