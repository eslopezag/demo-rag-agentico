"""Revisa que todo esté listo antes de la demostración.

    uv run python probar_conexion.py

ESTE ARCHIVO VIENE HECHO. Prueba, en orden: la base de datos, el modelo de chat y
los embeddings de OpenRouter. Cada prueba cuesta menos de un centavo de dólar.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def paso(nombre, prueba):
    try:
        print(f"OK     {nombre}: {prueba()}")
    except Exception as error:  # noqa: BLE001 - queremos ver cualquier falla
        print(f"FALLA  {nombre}: {type(error).__name__}: {error}")


def base_de_datos():
    from pedidos import ejecutar
    fila = ejecutar("SELECT (SELECT count(*) FROM productos) AS productos, "
                    "(SELECT count(*) FROM pedidos) AS pedidos")[0]
    return f"{fila['productos']} productos, {fila['pedidos']} pedidos"


def chat():
    from langchain_openrouter import ChatOpenRouter
    modelo = ChatOpenRouter(model=os.getenv("MODELO", "anthropic/claude-haiku-4.5"))
    return modelo.invoke("Responde sólo: listo").content


def embeddings():
    from langchain_openai import OpenAIEmbeddings
    emb = OpenAIEmbeddings(model="openai/text-embedding-3-small",
                           base_url="https://openrouter.ai/api/v1",
                           api_key=os.environ["OPENROUTER_API_KEY"],
                           check_embedding_ctx_length=False)
    return f"vector de {len(emb.embed_query('olla arrocera'))} números"


if __name__ == "__main__":
    if os.environ.pop("SSLKEYLOGFILE", None):
        print("AVISO  SSLKEYLOGFILE estaba definida (la pone Avast en Windows) y tumba las "
              "conexiones HTTPS de Python. Esta prueba la quitó; para la app, quítenla de la "
              "terminal. Ver README, sección Problemas conocidos.")
    paso("PostgreSQL", base_de_datos)
    paso("Chat en OpenRouter", chat)
    paso("Embeddings en OpenRouter", embeddings)
