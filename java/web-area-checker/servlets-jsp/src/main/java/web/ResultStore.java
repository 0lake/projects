package web;

import area.CheckResult;
import java.io.Serializable;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

/**
 * История проверок одной сессии. Хранит ограниченное число записей, чтобы сессия не росла бесконечно.
 */
public final class ResultStore implements Serializable {
    private static final long serialVersionUID = 1L;
    public static final String ATTRIBUTE = "resultStore";
    public static final int LIMIT = 100;

    private final ArrayDeque<CheckResult> items = new ArrayDeque<>();

    /** Добавляет результат; при переполнении удаляет самый старый. */
    public synchronized void add(CheckResult result) {
        items.addFirst(result);
        while (items.size() > LIMIT) {
            items.removeLast();
        }
    }

    /** @return копия истории, новые записи первыми */
    public synchronized List<CheckResult> all() {
        return new ArrayList<>(items);
    }

    public synchronized void clear() {
        items.clear();
    }
}
