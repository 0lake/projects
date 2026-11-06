package flats.client;

import flats.client.io.ConsoleInput;
import flats.client.net.NioServerConnection;

/**
 * Точка входа клиента: {@code ClientMain [host] [port]}.
 */
public final class ClientMain {
    private ClientMain() {
    }

    public static void main(String[] args) throws Exception {
        String host = args.length > 0 ? args[0] : "localhost";
        int port = args.length > 1 ? Integer.parseInt(args[1]) : 5555;
        var app = new ClientApp(new NioServerConnection(host, port), System.out);
        try (var input = new ConsoleInput(System.in)) {
            app.run(input);
        }
    }
}
