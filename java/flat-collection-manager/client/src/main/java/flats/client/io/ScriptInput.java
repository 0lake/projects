package flats.client.io;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Ввод из файла скрипта.
 */
public final class ScriptInput implements InputSource {
    private final BufferedReader reader;

    public ScriptInput(Path file) throws IOException {
        this.reader = Files.newBufferedReader(file, StandardCharsets.UTF_8);
    }

    @Override
    public String readLine() throws IOException {
        return reader.readLine();
    }

    @Override
    public boolean interactive() {
        return false;
    }

    @Override
    public void close() throws IOException {
        reader.close();
    }
}
