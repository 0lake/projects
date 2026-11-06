package flats.client.form;

/**
 * Ввод закончился раньше, чем форма была заполнена.
 */
public class InputEnded extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public InputEnded() {
        super("Ввод завершён до окончания заполнения формы");
    }
}
