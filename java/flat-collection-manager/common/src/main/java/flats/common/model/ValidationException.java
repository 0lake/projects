package flats.common.model;

/**
 * Нарушение требования к полю модели (null, выход за границы и т.п.).
 * Сообщение предназначено для показа пользователю.
 */
public class ValidationException extends IllegalArgumentException {
    private static final long serialVersionUID = 1L;

    /**
     * @param message описание нарушенного требования
     */
    public ValidationException(String message) {
        super(message);
    }
}
