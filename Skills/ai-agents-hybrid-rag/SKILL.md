# Especificación Técnica de Habilidad
**Código de Skill:** SKL-AI-RAG-001  
**Versión:** 1.1.0  
**Estándar:** ISO/IEC 26514 / IEEE 29148 / Agile DoD  

---

### 1. Ficha de Identificación del Skill

| Atributo | Definición Técnica |
| --- | --- |
| **Habilidad Principal** | Arquitectura y Orquestación de Sistemas RAG Agénticos Híbridos |
| **Objetivo de Dominio** | Capacitar al usuario para ejecutar, iterar y optimizar sistemas conversacionales escalables utilizando LangGraph, LangChain y LangSmith, combinando recuperación semántica (RAG) y ejecución transaccional (SQL). |
| **Tipo de Proyecto** | Ingeniería de Inteligencia Artificial / Arquitectura de Backend |
| **Complejidad** | Alta |

---

### 2. Descripción y Filosofía de Diseño

El skill de **Arquitectura RAG Agéntica** se enfoca en la creación de soluciones basadas en el procesamiento de lenguaje natural y recuperación de información híbrida, bajo los siguientes principios:

* **Modularidad:** Componentes de orquestación desacoplados y granulares. Separación estricta de responsabilidades:
  * **LangChain** como el *vocabulario* (plantillas de prompts, esquemas y abstracciones de herramientas).
  * **LangGraph** como el *control de flujo* determinista y de lógica cíclica mediante estados estructurados.
  * **LangSmith** como la *capa de visibilidad y observabilidad* para monitorear trazas, latencia y consumo de tokens.
* **Idempotencia:** Resultados consistentes ante ejecuciones repetidas mediante el uso de grafos de estado (`StateGraph`) donde la memoria es predecible, auditable e inmutable fuera de sus nodos.
* **Reusabilidad:** Lógica aplicable a múltiples casos de uso mediante la parametrización de `PromptTemplates` almacenados de forma independiente a la lógica de ejecución de código.

#### 2.1. Resiliencia y Observabilidad (Patrones Aplicables)

Dependiendo del contexto de la **inferencia del Agente IA**, se deben integrar los siguientes mecanismos para garantizar robustez:

* **Flujo de Control y Fallbacks Circulares:** Aristas condicionales (*Conditional Edges*) para evaluar la calidad del contexto antes de generar una respuesta. Es obligatorio implementar un **Servicio LLM con Fallback Circular**: Si el modelo principal (ej. Groq) sufre un timeout o caída, el sistema debe cambiar automáticamente a un LLM de respaldo (ej. Hugging Face) para garantizar el SLA y nunca dejar al usuario "en visto". Lógica de reintento (*Retry Logic*) estricta.
* **Persistencia y Fallos:** Puntos de control (*Checkpointers*) en el grafo para pausar la ejecución (*Human-in-the-Loop*) o recuperar sesiones ante caídas del servidor.
* **Trazabilidad y Logging Estructurado:** Trazas estructuradas nativas (*Traces*) en LangSmith para auditar el árbol de decisión. Integración de logging estructurado (JSON) inyectando siempre el `session_id` y `user_id` para depurar fallos en alta concurrencia.
* **Métricas de Éxito:** Definición clara de OKRs analíticos (Reducción de alucinaciones < 3%) y KPIs técnicos (Latencia de recuperación < 500ms, Precisión del Reranker).

---

### 3. Requerimientos del Skill

#### 3.1. Requerimientos Funcionales (RF)

* **[RF-01] Inicialización de Entorno:** El practicante debe ser capaz de inicializar un entorno base de LangGraph configurando el Estado (`TypedDict`) y mapeando Nodos y Aristas.
* **[RF-02] Ingesta Vectorial Semántica:** El sistema debe procesar un corpus documental aplicando fragmentación consciente de la estructura (ej. utilizando `MarkdownHeaderTextSplitter` de LangChain) y emparejamiento pregunta-a-pregunta (*Question-to-Question matching*).
* **[RF-03] Validación de Salida (Gatekeeper):** Generar una salida consistente validada por un nodo auditor que asegure que la respuesta responde al *input* del usuario y se fundamenta 100% en el contexto recuperado sin alucinaciones.

#### 3.2. Requerimientos No Funcionales (RNF)

* **[RNF-01] Escalabilidad:** Crecimiento en volumen sin degradar el rendimiento, implementando búsqueda híbrida descentralizada mediante ChromaDB y PostgreSQL.
* **[RNF-02] Mantenibilidad:** El proceso de enrutamiento (Router) debe ser comprensible en menos de 15 minutos, manteniendo los prompts separados de los nodos.
* **[RNF-03] Seguridad:** Aplicación del principio de menor privilegio, limitando a las herramientas (Tools) los accesos de solo lectura a la base de datos relacional.
* **[RNF-04] Disponibilidad:** Resistencia a fallos de inferencia mediante la captura de excepciones dentro de los nodos y derivación hacia respuestas de contingencia estáticas.

---

### 4. Criterios de Aceptación (Definition of Done)

Se considera que el dominio de **Arquitectura RAG Agéntica** está completo si:

* **Validación Lógica:** Cumple con el 100% de los RF listados en el diseño del grafo.
* **Resiliencia:** El sistema maneja al menos 3 escenarios de error (falta de contexto, error de parseo de herramientas, timeout de API) corrigiendo su propio estado o activando un *graceful fallback* sin colapsar el proceso principal de FastAPI.
* **Calidad Técnica:** El entregable posee pruebas cuantitativas (Datasets) en LangSmith que validan matemáticamente la precisión de las respuestas antes del despliegue en producción.
* **Autonomía:** El usuario replica y orquesta un pipeline RAG con un mínimo de 3 nodos funcionales desde cero en menos de 4 horas.

---

### 5. Ecosistema de Herramientas (Stack)

* **Herramienta Principal:** LangGraph (Orquestador de flujos cíclicos con estado).
* **Librerías / Dependencias:** `langchain`, `langchain-core`, `langsmith`, `chromadb`, Framework de API (FastAPI), Motores LLM (Groq, OpenAI).
* **Entorno de Ejecución:** Entornos virtuales de Python en Linux (Fedora), Docker Compose para servicios de apoyo, Terminal CLI.

---

### 6. Metodología de Práctica (Paso a Paso)

1. **Fase de Setup:** Configuración de dependencias en `requirements.txt` y credenciales de LangSmith/LLM en variables de entorno.
2. **Fase de Construcción:** Implementación de la lógica modular: definición de Tools, diseño del `StateGraph`, fragmentación estructural del corpus y creación de los índices vectoriales.
3. **Fase de Refactor:** Optimización siguiendo los patrones de resiliencia (implementación de Nodos Auditores y ruteo híbrido para separar intención SQL de RAG).
4. **Fase de QA:** Ejecución masiva contra un dataset de validación en LangSmith para auditar el desempeño algorítmico y verificar los Criterios de Aceptación.

---

### 7. Antipatrones (Lo que NO se debe hacer)

* ⚠️ **[Antipatrón 1]:** Intentar forzar la lógica cíclica o de agentes conversacionales utilizando Cadenas (`Chains` lineales) de LangChain en lugar de LangGraph, generando código espagueti.
* ⚠️ **[Antipatrón 2]:** Omitir la validación estructural del texto en la ingesta (Chunking ciego por tokens), destruyendo la semántica y el contexto de las tablas o encabezados.
* ⚠️ **[Antipatrón 3]:** Ignorar la capa de observabilidad (LangSmith), operando en "vuelo a ciegas" ante alucinaciones o degradación de la inferencia.
* ⚠️ **[Antipatrón 4]:** Redirigir consultas transaccionales puras (ej. estado de saldos) hacia el RAG vectorial en lugar de utilizar herramientas deterministas vinculadas a bases relacionales.

---

### 8. Evaluación y KPIs

| Métrica | Meta |
| --- | --- |
| **Tasa de Alucinación (Error Rate)** | < 3% en inferencias auditadas |
| **Precisión de Recuperación (Hit Rate)** | > 92% en Top-3 de fragmentos |
| **Latencia P95 del Pipeline** | < 1.5 segundos |
| **Cumplimiento de RF** | 100% |

---

### 9. Arquitectura y Buenas Prácticas de Grado Industrial

Para garantizar un sistema de inferencia sólido, predecible y capaz de escalar sin romperse, se establece el siguiente núcleo de mejores prácticas:

#### 9.1. Capa de Ingesta y Recuperación

**1. Fragmentación Estructural (Structure-Aware Chunking):**
* **Lo que recordaste:** Cortar de forma inteligente tras cada título o tabla.
* **El detalle técnico:** No fragmentar el texto a ciegas cada 500 tokens. Utilizar herramientas como `MarkdownHeaderTextSplitter` para que el sistema respete los límites lógicos del documento. Si cortás una tabla a la mitad, el modelo pierde la capacidad de entender esa estructura relacional.

**2. Búsqueda Híbrida y Reranking:**
* **Lo que recordaste:** Combinar semántica con palabras clave.
* **El detalle técnico:** La similitud vectorial (conceptos abstractos) tiene puntos ciegos con identificadores exactos (ej. códigos de error, nombres propios). Al combinar la búsqueda densa con la búsqueda BM25 (palabras clave) y pasar esos resultados por un modelo de **Re-ordenamiento (Reranker)**, te asegurás de que solo los fragmentos con mayor relevancia matemática lleguen a la ventana de contexto del LLM, ahorrando tokens y reduciendo alucinaciones.

**3. Inversión de Índices (Question-to-Question Matching):**
* **La práctica complementaria:** En lugar de indexar únicamente la prosa de los manuales, usá un modelo rápido durante la ingesta para que lea cada fragmento y genere 5 preguntas hipotéticas que ese texto podría responder. Cuando el usuario consulte algo, el buscador emparejará su pregunta contra tus preguntas pre-generadas. La coincidencia matemática entre dos preguntas es infinitamente superior a la coincidencia entre una pregunta y un bloque de texto denso.

#### 9.2. Capa de Orquestación y Lógica (LangGraph y LangChain)

**4. Enrutamiento Dinámico (Router de Intenciones):**
* **Lo que recordaste:** Un router para detectar qué quiere el usuario.
* **El detalle técnico:** Es el primer nodo de tu grafo. Debe decidir de forma determinista si la pregunta se resuelve leyendo un documento estático (RAG) o si requiere ejecutar una herramienta (*Tool*) que consulte tablas operativas mediante SQL. Esto evita colisiones y falsos positivos.

**5. Separación de Vocabulario y Lógica (Abstracción):**
* **La práctica:** Nunca hardcodear las instrucciones (*prompts*) dentro de la lógica de ejecución del código. Utilizar `PromptTemplates` almacenados en un repositorio central o gestionados desde la nube. Esto permite iterar y mejorar la comunicación del modelo sin tener que recompilar la aplicación.

**6. Modelado de Ciclos y Manejo de Estado (StateGraph):**
* **La práctica:** Abandonar las cadenas de texto lineales. Al utilizar LangGraph, la conversación debe circular como un objeto de Estado inmutable. Si el nodo de recuperación no encuentra información relevante, una **Arista Condicional** debe evaluar la situación y permitir que el sistema retroceda, reformule la pregunta de búsqueda y vuelva a intentar, en lugar de rendirse o alucinar de inmediato.

#### 9.3. Capa de Control y Observabilidad (LangSmith y Defensas)

**7. Nodos Auditores (Gatekeepers):**
* **La práctica:** Antes de devolverle la respuesta final al usuario, el flujo debe pasar por un nodo evaluador automatizado. Este nodo aplica un control lógico estricto verificando dos cosas: *¿La respuesta generada responde directamente a la intención original?* y *¿Está fundamentada al 100% en el contexto recuperado?* Si detecta información inventada, el grafo rechaza la salida y obliga al modelo a reescribir.

**8. Trazabilidad y Pruebas Cuantitativas (Evaluation Datasets):**
* **La práctica:** Tratar los fallos de IA (alucinaciones, evasiones) como bugs de software. Utilizar LangSmith para registrar la traza completa (*trace*) de cada ejecución. Además, establecer un conjunto de pruebas (*datasets* de validación con preguntas difíciles) para medir matemáticamente la precisión, latencia y consumo de tokens cada vez que se modifique un prompt o la lógica de *chunking*.

#### 9.4. Memoria Episódica en ChromaDB (Privacidad y Aislamiento Multi-Tenant)

**9. Colecciones Vectoriales Separadas:**
* **La práctica:** No mezclar manuales técnicos con recuerdos de usuarios. En ChromaDB, instanciar dos colecciones aisladas: `nexopay_knowledge_base` (estática, global y de solo lectura) y `user_long_term_memory` (dinámica y conversacional). Esto evita filtraciones de privacidad y alucinaciones cruzadas.

**10. Búsqueda Condicionada por Metadatos:**
* **La práctica:** Al insertar recuerdos episódicos (ej. *"Prefiere fondos de liquidez en lugar de plazos fijos"*), se debe inyectar un diccionario de metadatos con el `user_id`. Al momento de consultar, el sistema fuerza un filtrado estricto: *"Buscar este vector, PERO SÓLO donde el user_id coincida"*. 

**11. Estrategia de Actualización Semántica (Upsert) y Extracción de Hechos:**
* **La práctica:** Para evitar que la colección de memoria se vuelva un basurero inmanejable de recuerdos contradictorios con el tiempo, se implementa un nodo asíncrono (`UpdateMemoryNode`) al final del grafo. En lugar de una sumarización ciega y costosa, este nodo realiza **Extracción de Entidades** atómicas. Si el usuario cambia de preferencia, el sistema realiza una **búsqueda de similitud previa** y aplica una **Actualización Semántica (Upsert)**, pisando el vector viejo con el dato nuevo. Esto mantiene el perfil vivo, coherente y optimizado en tokens.

---

### 10. Recursos y Documentación Oficial

* [Documentación Oficial de LangGraph](https://langchain-ai.github.io/langgraph/)
* [Documentación de Evaluación en LangSmith](https://docs.smith.langchain.com/)
* [Guía de Abstracciones y Prompts de LangChain](https://python.langchain.com/)
