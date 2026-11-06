package flats.server.store.jdbc;

/**
 * Ошибка работы с базой данных.
 */
public class StorageException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public StorageException(String message, Throwable cause) {
        super(message, cause);
    }
}
