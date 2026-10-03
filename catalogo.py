"""Catálogo: indexar los productos en Qdrant y buscarlos por significado.

ARCHIVO INCOMPLETO: cada bloque marcado con TODO se escribe durante la
sesión, en el orden en que están. Las instrucciones están en el README, en
la sección "Llenar el código que falta" (pasos 1 y 2).

El archivo no corre hasta completar los TODO: el primero crea `productos`, que
las líneas siguientes usan.

    uv run python -i catalogo.py     # para probar mientras se escribe
"""
import os
from typing import Literal

import pandas as pd
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import models

load_dotenv()

# 1. Leer el catálogo
# TODO: leer datos/productos.xlsx con pandas y guardarlo en `productos`.
#       Antes de seguir, mirar la tabla: productos.head() y
#       productos["categoria"].value_counts().

# 2. Un documento por producto: el texto se compara, los metadatos se filtran
# TODO: recorrer productos.to_dict("records") y armar la lista `documentos`.
#       page_content: el nombre y la descripción, que es lo que se compara por
#       significado. metadata: las demás columnas (precio, categoría, stock...),
#       que es lo que se filtra con reglas exactas.

# 3. Embeddings a través de OpenRouter
# TODO: crear `embeddings` con OpenAIEmbeddings apuntando a OpenRouter:
#       model="openai/text-embedding-3-small", base_url de OpenRouter, la clave
#       de la variable de entorno, y check_embedding_ctx_length=False porque
#       OpenRouter recibe texto, no tokens.

# 4. Base de datos vectorial en memoria
# TODO: crear `vector_store` con QdrantVectorStore.from_documents(...),
#       location=":memory:" y collection_name="productos". Aquí es donde se
#       calculan los embeddings de los 1051 productos.

# Dado: las categorías que existen en el catálogo. El tipo entra en la firma de
# la herramienta, así que el modelo sólo puede elegir una de estas.
Categoria = Literal[tuple(sorted(productos["categoria"].unique()))]


@tool(parse_docstring=True)
def buscar_productos(
    consulta: str,
    categoria: Categoria | None = None,
    precio_min: int | None = None,
    precio_max: int | None = None,
    calificacion_min: float | None = None,
    solo_disponibles: bool = True,
) -> str:
    """Busca productos del catálogo por significado y los filtra por sus datos.

    Escribe la consulta como la descripción del producto ideal, con sinónimos y
    características, aunque el cliente lo haya dicho con otras palabras.

    Args:
        consulta: Descripción del producto buscado, por ejemplo "guantes para entrenar en el gimnasio".
        categoria: Categoría del catálogo. Úsala sólo si es claro que el pedido del cliente pertenece a una de las categorías.
        precio_min: Precio mínimo en pesos colombianos.
        precio_max: Precio máximo en pesos colombianos.
        calificacion_min: Calificación mínima, de 1 a 5.
        solo_disponibles: Si es True, sólo productos con inventario.
    """
    # Dado: los filtros de Qdrant. Cada argumento que llenó el modelo agrega una
    # regla exacta sobre los metadatos, y los que llegan vacíos no agregan nada.
    # La búsqueda descarta los productos que incumplen alguna regla y ordena por
    # significado los que quedan.
    condiciones = []
    if categoria:
        condiciones.append(models.FieldCondition(
            key="metadata.categoria", match=models.MatchValue(value=categoria)))
    if precio_min or precio_max:
        condiciones.append(models.FieldCondition(
            key="metadata.precio_cop", range=models.Range(gte=precio_min, lte=precio_max)))
    if calificacion_min:
        condiciones.append(models.FieldCondition(
            key="metadata.calificacion", range=models.Range(gte=calificacion_min)))
    if solo_disponibles:
        condiciones.append(models.FieldCondition(
            key="metadata.stock", range=models.Range(gt=0)))

    # TODO: buscar con vector_store.similarity_search(consulta, k=5, ...),
    #       pasando models.Filter(must=condiciones).

    # TODO: devolver el texto que va a leer el modelo: los metadatos de cada
    #       resultado y un pedazo de la descripción. Si no hubo resultados,
    #       devolver un aviso en vez de una lista vacía.
    raise NotImplementedError("Completar durante la demostración")


if __name__ == "__main__":
    print(buscar_productos.invoke({"consulta": "materiales de arte para pintar y dibujar",
                                   "precio_max": 100_000}))
