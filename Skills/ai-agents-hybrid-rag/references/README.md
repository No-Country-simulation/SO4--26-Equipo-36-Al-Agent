# Referencias Técnicas - Arquitectura RAG Agéntica

Este directorio consolida las referencias técnicas y estándares de arquitectura que establecen las bases de ingeniería de software para este skill.

---

### 1. Desglose Conceptual de Componentes
* **Referencia de Arquitectura:** Orquestación de Agentes con Estado y Sistemas de Recuperación Híbridos.
* **Objetivo:** Diferenciación estricta de las responsabilidades del stack tecnológico de IA.
* **Componentes de Referencia:**
  * **LangChain (Capa de Abstracción):** Define abstracciones unificadas e interfaces comunes (prompts, schemas, clients, data loaders).
  * **LangGraph (Capa de Ejecución y Orquestación):** Gestiona flujos de control cíclicos, persistencia del estado inmutable mediante StateGraphs, reintentos y enrutamiento dinámico.
  * **LangSmith (Capa de Observabilidad):** Registra trazas detalladas de la ejecución para identificar cuellos de botella y evaluar cuantitativamente el sistema mediante Datasets estructurados.

---

### 2. Diseño de Arquitectura RAG Híbrida
* **Referencia de Implementación:** Ingesta semántica consciente de estructura y recuperación densa/lexical híbrida.
* **Objetivo:** Mitigación de alucinaciones y reducción de latencias y costos a escala industrial.
* **Técnicas Clave de Referencia:**
  * **Structure-Aware Chunking:** Fragmentación que preserva la estructura lógica (Markdown splitters) de tablas, títulos y secciones.
  * **Question-to-Question Matching (Q2Q):** Generación e indexación de preguntas hipotéticas para mejorar significativamente el Hit Rate semántico.
  * **Búsqueda Híbrida + Reranking:** Combinación de búsquedas densas vectoriales y lexicales (BM25) reordenadas mediante modelos de Reranking antes de tocar el LLM.
  * **Nodos Gatekeeper:** Auditoría automatizada que valida la fidelidad lógica de las respuestas frente al contexto recuperado.
