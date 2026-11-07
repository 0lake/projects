CREATE TABLE IF NOT EXISTS points (
    id         BIGSERIAL        PRIMARY KEY,
    session_id VARCHAR(64)      NOT NULL,
    x          DOUBLE PRECISION NOT NULL,
    y          DOUBLE PRECISION NOT NULL,
    r          DOUBLE PRECISION NOT NULL CHECK (r > 0),
    hit        BOOLEAN          NOT NULL,
    checked_at TIMESTAMPTZ      NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS points_session_idx ON points (session_id, id DESC);
