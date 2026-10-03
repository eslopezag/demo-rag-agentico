"""Herramientas de pedidos: consultar y cancelar.

ESTE ARCHIVO VIENE HECHO: no hay nada por completar acá.

Las herramientas hablan con PostgreSQL a través de funciones de Python con
parámetros fijos. El modelo elige los valores de esos parámetros (un estado, un
número de pedido, un rango de días); el SQL lo escribimos nosotros y los valores
viajan como parámetros, nunca pegados al texto de la consulta.

El número del cliente tampoco es un parámetro que el modelo pueda llenar: sale de
`Contexto`, que la aplicación arma después de identificar al cliente. Así el
agente sólo ve los pedidos de quien inició la sesión, aunque un mensaje le pida
los de otra persona.
"""
import json
import os
from dataclasses import dataclass
from typing import Literal

import psycopg
from dotenv import load_dotenv
from langchain.tools import ToolRuntime, tool
from psycopg.rows import dict_row

load_dotenv()
URL_BD = os.getenv("URL_BD", "postgresql://tienda:tienda@localhost:5432/tienda")

Estado = Literal["pendiente", "en_preparacion", "enviado", "entregado", "cancelado", "devuelto"]
CANCELABLES = ("pendiente", "en_preparacion")      # los que todavía no salieron de la bodega


@dataclass
class Contexto:
    """Datos de la sesión que la aplicación conoce y el modelo no controla."""
    usuario_id: int


def ejecutar(sql: str, parametros: dict | None = None) -> list[dict]:
    """Ejecuta una consulta y devuelve las filas como diccionarios.

    Al salir del `with`, psycopg confirma los cambios (o los deshace si hubo error).
    """
    with psycopg.connect(URL_BD, row_factory=dict_row) as conexion:
        cursor = conexion.execute(sql, parametros)
        return cursor.fetchall() if cursor.description else []


def buscar_usuario(email_o_id: str) -> dict | None:
    """El cliente con ese correo o ese número, o None si no existe."""
    texto = email_o_id.strip()
    if texto.isdigit():
        filas = ejecutar("SELECT id, nombre, email FROM usuarios WHERE id = %s", (int(texto),))
    else:
        filas = ejecutar("SELECT id, nombre, email FROM usuarios WHERE lower(email) = lower(%s)",
                         (texto,))
    return filas[0] if filas else None


@tool(parse_docstring=True)
def consultar_pedidos(
    runtime: ToolRuntime[Contexto],
    id_pedido: int | None = None,
    estado: Estado | None = None,
    producto: str | None = None,
    ultimos_dias: int | None = None,
    limite: int = 10,
) -> str:
    """Consulta los pedidos del cliente conectado, del más reciente al más antiguo.

    Sin filtros devuelve sus últimos pedidos. Los filtros se pueden combinar.

    Args:
        id_pedido: Número de un pedido concreto, por ejemplo 13225.
        estado: Sólo los pedidos que están en este estado.
        producto: Parte del nombre del producto, por ejemplo "olla" o "taladro".
        ultimos_dias: Sólo los pedidos hechos en los últimos N días.
        limite: Cuántos pedidos devolver como máximo, entre 1 y 20.
    """
    # Cada condición es un texto fijo escrito aquí; los valores van en `parametros`.
    condiciones = ["p.usuario_id = %(usuario_id)s"]
    parametros = {"usuario_id": runtime.context.usuario_id, "limite": max(1, min(limite, 20))}
    if id_pedido is not None:
        condiciones.append("p.id = %(id_pedido)s")
        parametros["id_pedido"] = id_pedido
    if estado is not None:
        condiciones.append("p.estado = %(estado)s")
        parametros["estado"] = estado
    if producto:
        condiciones.append("pr.nombre ILIKE %(producto)s")
        parametros["producto"] = f"%{producto}%"
    if ultimos_dias is not None:
        condiciones.append("p.fecha_creacion >= localtimestamp - make_interval(days => %(dias)s)")
        parametros["dias"] = ultimos_dias

    filas = ejecutar(
        f"""
        SELECT p.id AS pedido, p.estado, pr.nombre AS producto, p.cantidad, p.total_cop,
               p.fecha_creacion, p.fecha_envio, p.fecha_entrega_estimada, p.fecha_entrega,
               p.transportadora, p.numero_guia, p.ciudad_envio, p.notas
        FROM pedidos p JOIN productos pr ON pr.id = p.producto_id
        WHERE {" AND ".join(condiciones)}
        ORDER BY p.fecha_creacion DESC
        LIMIT %(limite)s
        """,
        parametros,
    )
    if not filas:
        return "No encontré pedidos de este cliente con esos filtros."
    return json.dumps(filas, default=str, ensure_ascii=False, indent=1)


@tool(parse_docstring=True)
def cancelar_pedido(runtime: ToolRuntime[Contexto], id_pedido: int, motivo: str) -> str:
    """Cancela un pedido del cliente conectado, si todavía no ha salido de la bodega.

    Sólo se cancelan pedidos en estado pendiente o en_preparacion. Antes de usar
    esta herramienta, confirma con el cliente el número del pedido y el producto.

    Args:
        id_pedido: Número del pedido que el cliente quiere cancelar.
        motivo: Motivo de la cancelación, en palabras del cliente.
    """
    usuario_id = runtime.context.usuario_id
    # Un solo UPDATE revisa dueño y estado: si el pedido ya salió, no toca nada.
    cancelado = ejecutar(
        """
        UPDATE pedidos
        SET estado = 'cancelado',
            notas = concat_ws(' ', notas, 'Cancelado por el cliente desde el asistente. Motivo: '
                              || %(motivo)s)
        WHERE id = %(id)s AND usuario_id = %(usuario_id)s AND estado = ANY(%(cancelables)s)
        RETURNING id
        """,
        {"id": id_pedido, "usuario_id": usuario_id, "motivo": motivo,
         "cancelables": list(CANCELABLES)},
    )
    if cancelado:
        return (f"Pedido {id_pedido} cancelado. El reembolso llega al medio de pago original "
                "en un máximo de 5 días hábiles.")

    actual = ejecutar("SELECT estado FROM pedidos WHERE id = %s AND usuario_id = %s",
                      (id_pedido, usuario_id))
    if not actual:
        return f"El pedido {id_pedido} no está entre los pedidos de este cliente."
    return (f"El pedido {id_pedido} no se puede cancelar porque su estado es "
            f"'{actual[0]['estado']}'. Sólo se cancelan pedidos pendientes o en preparación. "
            "Si ya fue entregado, el cliente puede solicitar una devolución.")
