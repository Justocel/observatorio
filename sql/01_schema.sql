-- sql/01_schema.sql
-- Schema inicial del Observatorio Financiero Argentino.

CREATE TABLE fuentes (
    id              BIGSERIAL   PRIMARY KEY,
    nombre          TEXT        NOT NULL UNIQUE,
    categoria       TEXT        NOT NULL,
    descripcion     TEXT,
    unidad          TEXT        NOT NULL,
    url_origen      TEXT,
    frecuencia_min  INTEGER,
    activa          BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE cotizaciones (
    fuente_id    BIGINT      NOT NULL REFERENCES fuentes(id),
    ts           TIMESTAMPTZ NOT NULL,
    valor        NUMERIC     NOT NULL,
    metadata     JSONB,
    inserted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (fuente_id, ts)
);
