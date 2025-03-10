CREATE TABLE test_data (
    id SERIAL PRIMARY KEY,
    value INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO test_data (value) VALUES (10), (20), (30), (40), (50);
