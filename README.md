# Taller: asistente de compras con RAG agéntico

Van a construir el chatbot de **Tienda Cóndor**, un comercio electrónico
ficticio. El asistente busca productos del catálogo por significado, informa en
qué va un pedido y cancela pedidos que todavía no han salido de la bodega.

Tres archivos de este repositorio están **incompletos a propósito**:
`catalogo.py`, `agente.py` y `app.py`. Cada bloque por escribir está marcado con
un comentario `# TODO:` que dice qué va ahí. El resto del proyecto viene hecho.

| Pieza | Herramienta |
|---|---|
| Dependencias y entorno | [uv](https://docs.astral.sh/uv/) |
| Agente, herramientas y memoria | [LangChain](https://docs.langchain.com/) (`create_agent`) |
| Modelo de chat y embeddings | [OpenRouter](https://openrouter.ai/) |
| Búsqueda semántica | [Qdrant](https://qdrant.tech/), en memoria |
| Pedidos, clientes y productos | PostgreSQL en Docker |
| Interfaz de chat | [Chainlit](https://docs.chainlit.io/) |

## Aviso antes de empezar

Correr este proyecto en su computador exige varias cosas que no son parte de la
sesión: instalar uv, instalar Docker Desktop y dejarlo andando, crear una cuenta
de OpenRouter con saldo, y manejar la terminal cuando algo falle. Si llegan a un
error que no saben resolver, **déjenlo ahí**. La sesión funciona igual: el
docente corre la aplicación en pantalla, y ustedes pueden leer el código,
escribir los bloques que faltan y guardar el repositorio para intentarlo después
con calma.

Si quieren intentarlo, el gasto en OpenRouter es de centavos de dólar.

## Preparación

Necesitan [uv](https://docs.astral.sh/uv/getting-started/installation/),
[Docker Desktop](https://www.docker.com/products/docker-desktop/) abierto y una
clave de [OpenRouter](https://openrouter.ai/keys) con saldo.

```bash
git clone https://github.com/eslopezag/demo-rag-agentico.git
cd demo-rag-agentico
uv sync                          # crea .venv con las dependencias de uv.lock
cp .env.example .env             # y pongan su clave de OpenRouter en .env
```

## La base de datos

Los pedidos, los clientes y los productos viven en PostgreSQL, y Docker lo
levanta ya cargado. Desde la carpeta del proyecto:

```bash
cd base_de_datos
docker compose up -d             # crea la base y carga los CSV (tarda unos segundos)
cd ..
uv run python probar_conexion.py # las tres líneas deben decir OK
```

`probar_conexion.py` revisa la base de datos, el modelo de chat y los
embeddings. Si las tres dicen OK, el entorno está listo.

Otros comandos de la base, desde `base_de_datos/`:

| Comando | Qué hace |
|---|---|
| `docker compose down` | La apaga y conserva los datos |
| `docker compose down -v` | La borra; el próximo `up` la carga desde cero |
| `PUERTO_BD=5433 docker compose up -d` | La levanta en otro puerto, si el 5432 está ocupado (cambien también el puerto de `URL_BD` en `.env`) |

Cancelar un pedido desde el chat cambia la base de verdad. Para volver al estado
inicial: `docker compose down -v && docker compose up -d`.

## Los archivos

| Archivo | Qué es | En la sesión |
|---|---|---|
| `base_de_datos/` | `docker-compose.yml` y los scripts que crean y llenan PostgreSQL | Viene hecho |
| `datos/productos.xlsx` | El catálogo: una fila por producto, con su descripción | Viene hecho |
| `pedidos.py` | Las herramientas `consultar_pedidos` y `cancelar_pedido`, y `buscar_usuario` | Viene hecho |
| `probar_conexion.py` | Revisa la base de datos, el chat y los embeddings | Viene hecho |
| `catalogo.py` | Indexa el catálogo en Qdrant y define `buscar_productos` | **Se completa** |
| `agente.py` | El modelo, las instrucciones, las herramientas y la memoria | **Se completa** |
| `app.py` | La interfaz de Chainlit | **Se completa** |

Vale la pena abrir `pedidos.py` antes de escribir nada: ahí está el ejemplo de
una herramienta segura. El SQL lo escribimos nosotros con parámetros fijos, el
modelo sólo elige valores, y el número del cliente llega por el `Contexto` de la
sesión en vez de ser un argumento que el modelo pueda inventar.

## Llenar el código que falta

Escriban los tres archivos en este orden, porque cada uno importa al anterior.

### 1. `catalogo.py`: del Excel a Qdrant

Cuatro `TODO` antes de la herramienta:

1. Leer `datos/productos.xlsx` con pandas en la variable `productos`. Mírenla
   antes de seguir: `productos.head()` y `productos["categoria"].value_counts()`.
2. Armar la lista `documentos`, un `Document` de LangChain por producto. En
   `page_content` va el texto que se compara por significado (el nombre y la
   descripción); en `metadata`, las columnas que se filtran con reglas exactas
   (precio, categoría, calificación, inventario).
3. Crear `embeddings` con `OpenAIEmbeddings` apuntando a OpenRouter.
4. Crear `vector_store` con `QdrantVectorStore.from_documents(...)`,
   `location=":memory:"`. Aquí se calculan los embeddings de los 1051
   productos, y tarda unos segundos.

Mientras escriben, prueben el archivo en la consola de Python:

```bash
uv run python -i catalogo.py
>>> for d in vector_store.similarity_search("mi perro tiene los dientes sucios", k=3):
...     print(d.metadata["nombre"])
```

Debería traer el cepillo dental para mascotas, aunque la pregunta no diga
"cepillo". Esa es la búsqueda semántica.

El archivo no corre hasta llenar el primer `TODO`: falla con
`NameError: productos`, porque las líneas siguientes usan esa variable.

### 2. `catalogo.py`: la herramienta `buscar_productos`

La firma, el docstring y los filtros de Qdrant vienen escritos. Léanlos: el tipo
y la descripción de cada argumento son lo único que el modelo ve de la
herramienta, y cada argumento que el modelo llena agrega una regla exacta sobre
los metadatos.

Quedan dos `TODO`: hacer la búsqueda con `vector_store.similarity_search(...)`
pasándole `models.Filter(must=condiciones)`, y devolver el texto que va a leer
el modelo. Al llenarlos, borren el `raise NotImplementedError` del final.

```bash
uv run python catalogo.py        # corre la prueba del final del archivo
```

### 3. `agente.py`: modelo, herramientas y memoria

Las instrucciones del sistema vienen escritas. Quedan dos `TODO`: crear `modelo`
con `ChatOpenRouter`, y armar `agente` con `create_agent(...)`, con las tres
herramientas, `context_schema=Contexto` y `checkpointer=InMemorySaver()`.

Antes de armar el agente, prueben el modelo solo para ver el problema que
resuelve el RAG:

```bash
uv run python -i agente.py
>>> modelo.invoke("¿En qué va mi pedido de la olla?").content
```

El archivo trae un bucle de chat en la terminal. Escriban `salir` para salir:

```
Tú: Mi perro tiene los dientes sucios, ¿qué me recomiendan?
Tú: ¿Cuánto cuesta el primero?
Tú: ¿Tengo pedidos pendientes?
```

La segunda pregunta sólo funciona gracias al `checkpointer`.

### 4. `app.py`: la interfaz de Chainlit

`iniciar_sesion` y las dos primeras líneas de `inicio` vienen escritas. Quedan
el saludo al cliente y la función `responder`: armar el `config` con un
`thread_id` y `cl.LangchainCallbackHandler()`, llamar a `agente.ainvoke(...)` con
el contexto de la sesión, y mandar la respuesta con `cl.Message(...).send()`.

```bash
uv run chainlit run app.py -w
```

Chainlit abre `http://localhost:8000` con una pantalla de inicio de sesión.
Escriban el correo o el número de un cliente, por ejemplo
`laura.gomez@correo.test` o `1`, y cualquier contraseña: la demostración no la
revisa. Para entrar como otro cliente, cierren sesión desde el menú del avatar,
arriba a la derecha.

### 5. Pruebas

Entren como `laura.gomez@correo.test` y prueben estos mensajes, mirando en la
interfaz las llamadas a las herramientas y los argumentos que eligió el modelo:

| Mensaje | Qué mirar |
|---|---|
| "Mi hijo quiere tocar batería, ¿qué accesorios hay por menos de 200 mil?" | La consulta que escribió el modelo y el filtro `precio_max=200000`. "Batería" aquí es el instrumento, y la búsqueda por significado no trae las baterías eléctricas del catálogo |
| "Busco un regalo para una amiga que acaba de tener un bebé, que esté bien calificado" | `categoria="Bebés"` y `calificacion_min`, aunque el cliente no los nombró así |
| "¿Dónde está mi pedido del auricular?" | El agente lee la nota del intento de entrega fallido y la explica |
| "Quiero cancelar el pedido de la olla" | El agente confirma antes de cancelar. Respondan "sí" |
| "Cancela también el del auricular" | Ese pedido ya salió: la herramienta se niega y el agente lo explica |
| "Muéstrame el pedido 13188" | Es de otro cliente. La herramienta filtra por el cliente de la sesión y no lo encuentra |
| "Busco un iPhone 17" | No está en el catálogo. El agente debería decirlo en vez de inventarlo |

## Los datos

- **Productos (1051):** nombre, descripción, marca y categoría son reales, del
  [catálogo público de Shopify](https://huggingface.co/datasets/Shopify/product-catalogue)
  (licencia Apache-2.0), filtrado a los productos en español. Precio en pesos,
  calificación, reseñas e inventario son inventados.
- **Clientes (250) y pedidos (3236):** inventados, con notas en lenguaje natural
  ("La transportadora reportó un intento de entrega fallido...").
- La base corre las fechas al crearse, así que los pedidos más recientes son de
  hoy.

Dos clientes sirven para las pruebas:

| Cliente | Pedidos |
|---|---|
| 1 · Laura Gómez · `laura.gomez@correo.test` | uno de cada estado: pendiente (olla arrocera), en preparación (guantes Adidas), enviado con un intento de entrega fallido (auricular Jabra), entregado (morral) y cancelado (silla) |
| 2 · Andrés Martínez · `andres.martinez@correo.test` | un taladro pendiente y un collar para perro entregado |

## Problemas conocidos

- **`OPENSSL_Uplink ... no OPENSSL_Applink` y Python se cierra.** Pasa en Windows
  con Avast: el antivirus define la variable `SSLKEYLOGFILE` y el OpenSSL de
  Python se cae al abrir una conexión HTTPS. Quítenla en la terminal antes de
  correr la aplicación:
  - PowerShell: `Remove-Item Env:SSLKEYLOGFILE`
  - Git Bash: `unset SSLKEYLOGFILE`
- **`No module named 'asyncpg'` al abrir el chat.** Su `.env` dice
  `DATABASE_URL`. Chainlit lee esa variable para guardar el historial de los
  chats en PostgreSQL, y para eso necesita `asyncpg`. Cámbienle el nombre a
  `URL_BD`, como en `.env.example`.
- **Chainlit no arranca y pide `CHAINLIT_AUTH_SECRET`.** Copien la línea
  `CHAINLIT_AUTH_SECRET=...` de `.env.example` a su `.env`. Es un secreto fijo y
  público, sólo para esta demostración; en producción cada despliegue genera el
  suyo con `chainlit create-secret`.
- **El puerto 5432 está ocupado** por otro PostgreSQL: levanten la base con
  `PUERTO_BD=5433 docker compose up -d` y cambien el puerto en `URL_BD`.
- **Los embeddings fallan con un error de formato:** agreguen
  `model_kwargs={"encoding_format": "float"}` a `OpenAIEmbeddings`.
- **El modelo no llama las herramientas o responde en inglés:** prueben otro
  `MODELO` en `.env`. Necesitan uno con soporte de herramientas (*tool calling*).

## Volver a empezar

Para dejar los tres archivos incompletos otra vez, sin perder la base de datos
ni el entorno:

```bash
git restore catalogo.py agente.py app.py
```

Al final de la sesión, el docente comparte el repositorio con la solución
completa de los tres archivos.
