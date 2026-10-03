"""Interfaz de chat con Chainlit.

ARCHIVO INCOMPLETO: cada bloque marcado con TODO se escribe durante la
sesión. Las instrucciones están en el README, en la sección
"Llenar el código que falta" (paso 4).

    uv run chainlit run app.py -w
"""
import chainlit as cl

from agente import agente
from pedidos import Contexto, buscar_usuario


@cl.password_auth_callback
async def iniciar_sesion(correo_o_id: str, contrasena: str) -> cl.User | None:
    # AUTENTICACIÓN SIMULADA, sólo para esta demostración: aceptamos cualquier
    # contraseña, así que quien escriba un correo ajeno ve los pedidos de otra
    # persona. En producción, esta misma función revisa la contraseña contra un
    # hash guardado (o se cambia por @cl.oauth_callback para entrar con Google o
    # con el SSO de la empresa), y sólo devuelve el cliente si coincide.

    usuario = buscar_usuario(correo_o_id)
    if usuario is None:
        return None  # Chainlit muestra el error en la pantalla de inicio de sesión
    return cl.User(
        identifier=usuario["email"],
        display_name=usuario["nombre"],
        metadata={"usuario_id": usuario["id"]},
    )


@cl.on_chat_start
async def inicio():
    # Al iniciar sesión, Chainlit guardó en la sesión el cl.User que devolvió
    # iniciar_sesion. De ahí sacamos al cliente, nunca de un mensaje del chat.
    usuario = cl.user_session.get("user")
    # El número del cliente viaja en el Contexto, y de ahí lo leen las
    # herramientas de pedidos en cada mensaje. No es un argumento de las
    # herramientas, así que el modelo no lo puede cambiar.
    cl.user_session.set("contexto", Contexto(usuario_id=usuario.metadata["usuario_id"]))

    # TODO: saludar al cliente por su nombre (display_name) con un cl.Message.
    raise NotImplementedError("Completar durante la demostración")


@cl.on_message
async def responder(mensaje: cl.Message):
    # TODO: armar `config` con dos cosas: un thread_id, que aquí es el
    #       identificador de la sesión de Chainlit (una memoria por pestaña), y
    #       cl.LangchainCallbackHandler() en "callbacks", que dibuja en la
    #       interfaz cada llamada a una herramienta con sus argumentos.

    # TODO: llamar al agente con await agente.ainvoke(...), pasándole el mensaje
    #       del cliente, la configuración y context=cl.user_session.get("contexto").

    # TODO: enviar el último mensaje de la respuesta con cl.Message(...).send().
    raise NotImplementedError("Completar durante la demostración")
