package flats.client.io;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/**
 * Ввод с клавиатуры.
 */
public final class ConsoleInput implements InputSource {
    private final BufferedReader reader;

    public ConsoleInput(InputStream in) {
        this.reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
    }

    @Override
    public String readLine() throws IOException {
        return reader.readLine();
    }

    @Override
    public String readSecret() throws IOException {
        var console = System.console();
        if (console == null) {
            return readLine();
        }
        char[] chars = console.readPassword();
        return chars == null ? null : new String(chars);
    }

    @Override
    public boolean interactive() {
        return true;
    }

    @Override
    public void close() {
        // стандартный ввод закрывать не нужно
    }
}
