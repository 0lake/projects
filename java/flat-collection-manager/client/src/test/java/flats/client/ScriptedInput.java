package flats.client;

import flats.client.io.InputSource;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

/**
 * Ввод из заранее заданного списка строк; ведёт себя как консоль.
 */
final class ScriptedInput implements InputSource {
    private final Deque<String> lines;

    ScriptedInput(List<String> lines) {
        this.lines = new ArrayDeque<>(lines);
    }

    @Override
    public String readLine() {
        return lines.pollFirst();
    }

    @Override
    public boolean interactive() {
        return true;
    }

    @Override
    public void close() {
        // нечего закрывать
    }
}
