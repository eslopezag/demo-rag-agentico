-- Carga los CSV que genera Assets/data/build_dataset.py.

COPY usuarios  FROM '/docker-entrypoint-initdb.d/usuarios.csv'  WITH (FORMAT csv, HEADER true);
COPY productos FROM '/docker-entrypoint-initdb.d/productos.csv' WITH (FORMAT csv, HEADER true);
COPY pedidos   FROM '/docker-entrypoint-initdb.d/pedidos.csv'   WITH (FORMAT csv, HEADER true);

-- Los CSV traen ids explícitos: los contadores deben seguir desde el mayor.
SELECT setval('usuarios_id_seq',  (SELECT max(id) FROM usuarios));
SELECT setval('productos_id_seq', (SELECT max(id) FROM productos));
SELECT setval('pedidos_id_seq',   (SELECT max(id) FROM pedidos));

-- Las fechas de los CSV toman como "hoy" el 1 de octubre de 2026 a mediodía.
-- Este bloque las corre para que ese instante sea el momento en que se crea la
-- base: los pedidos pendientes siempre son de ayer o de hoy.
DO $$
DECLARE
    corrimiento INTERVAL := now()::timestamp - TIMESTAMP '2026-10-01 12:00';
    dias        INTEGER  := current_date - DATE '2026-10-01';
BEGIN
    UPDATE pedidos SET
        fecha_creacion         = fecha_creacion + corrimiento,
        fecha_envio            = fecha_envio + corrimiento,
        fecha_entrega          = fecha_entrega + corrimiento,
        fecha_entrega_estimada = fecha_entrega_estimada + dias;
    UPDATE usuarios SET fecha_registro = fecha_registro + dias;
END $$;
