package flats.server;

import static org.junit.Assert.assertEquals;

import flats.common.TestData;
import flats.common.protocol.CommandType;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import org.junit.Test;

public class ConcurrencyTest {
    @Test
    public void parallelAddsKeepMemoryAndStoreInSync() throws Exception {
        var s = new ServerFixture();
        s.register("anna", "secret1");
        ExecutorService pool = Executors.newFixedThreadPool(8);
        List<Future<?>> tasks = new ArrayList<>();
        for (int i = 0; i < 400; i++) {
            int n = i;
            tasks.add(pool.submit(() -> {
                s.run("anna", "secret1", CommandType.ADD, null, TestData.draft("f" + n, 10 + n, 1));
                s.run("anna", "secret1", CommandType.SHOW);
            }));
        }
        for (Future<?> task : tasks) {
            task.get();
        }
        pool.shutdown();
        assertEquals(400, s.collection.size());
        assertEquals(400, s.flats.findAll().size());
        long distinctIds = s.flats.findAll().stream().map(f -> f.id()).collect(Collectors.toSet()).size();
        assertEquals(400, distinctIds);
    }

    @Test
    public void parallelRemoveOfSameElementSucceedsOnce() throws Exception {
        var s = new ServerFixture();
        s.register("anna", "secret1");
        s.run("anna", "secret1", CommandType.ADD, null, TestData.draft("x", 10, 1));
        long id = s.flats.findAll().get(0).id();
        ExecutorService pool = Executors.newFixedThreadPool(8);
        List<Future<Boolean>> results = new ArrayList<>();
        for (int i = 0; i < 16; i++) {
            results.add(pool.submit(() ->
                    s.run("anna", "secret1", CommandType.REMOVE_BY_ID, String.valueOf(id), null).isOk()));
        }
        int successes = 0;
        for (Future<Boolean> result : results) {
            if (result.get()) {
                successes++;
            }
        }
        pool.shutdown();
        assertEquals(1, successes);
    }
}
