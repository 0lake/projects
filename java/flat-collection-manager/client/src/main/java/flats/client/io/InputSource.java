package flats.client.io;

import java.io.IOException;

/**
 * Источник строк команд: консоль или файл скрипта.
 */
public interface InputSource extends AutoCloseable {
    /**
     * @return следующая строка или null, если ввод закончился
     */
    String readLine() throws IOException;

    /**
     * Читает пароль. Консоль не показывает вводимые символы.
     *
     * @return введённый пароль или null, если ввод закончился
     */
    default String readSecret() throws IOException {
        return readLine();
    }

    /** @return true, если источник интерактивный (есть человек, которому показывать подсказки) */
    boolean interactive();

    @Override
    void close() throws IOException;
}
