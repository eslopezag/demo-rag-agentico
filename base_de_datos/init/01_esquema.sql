-- Esquema de la tienda. PostgreSQL ejecuta los archivos de esta carpeta en orden
-- alfabético, y sólo la primera vez que crea la base.

CREATE TABLE usuarios (
    id              SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    ciudad          TEXT NOT NULL,
    direccion       TEXT NOT NULL,
    fecha_registro  DATE NOT NULL
);

CREATE TABLE productos (
    id              SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    marca           TEXT NOT NULL,
    categoria       TEXT NOT NULL,
    precio_cop      INTEGER NOT NULL,
    calificacion    NUMERIC(2, 1) NOT NULL,
    num_resenas     INTEGER NOT NULL,
    stock           INTEGER NOT NULL,
    envio_gratis    BOOLEAN NOT NULL,
    descripcion     TEXT NOT NULL
);

CREATE TABLE pedidos (
    id                      SERIAL PRIMARY KEY,
    usuario_id              INTEGER NOT NULL REFERENCES usuarios (id),
    producto_id             INTEGER NOT NULL REFERENCES productos (id),
    cantidad                INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario_cop     INTEGER NOT NULL,
    total_cop               INTEGER NOT NULL,
    estado                  TEXT NOT NULL CHECK (estado IN (
                                'pendiente', 'en_preparacion', 'enviado',
                                'entregado', 'cancelado', 'devuelto')),
    fecha_creacion          TIMESTAMP NOT NULL,
    fecha_envio             TIMESTAMP,
    fecha_entrega_estimada  DATE,
    fecha_entrega           TIMESTAMP,
    transportadora          TEXT,
    numero_guia             TEXT,
    direccion_envio         TEXT NOT NULL,
    ciudad_envio            TEXT NOT NULL,
    notas                   TEXT
);

CREATE INDEX pedidos_usuario_idx ON pedidos (usuario_id, fecha_creacion DESC);
