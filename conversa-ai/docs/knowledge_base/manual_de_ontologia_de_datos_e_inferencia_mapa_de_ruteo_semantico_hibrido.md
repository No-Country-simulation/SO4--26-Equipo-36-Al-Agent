# **MANUAL DE ONTOLOGÍA DE DATOS E INFERENCIA: MAPA DE RUTEO SEMÁNTICO HÍBRIDO**

**Código de Documento:** NP-OR-MAP-2026-V1

**Clasificación:** Confidencial / Uso Interno Obligatorio para el Orquestador LangGraph

**Entidad Operativa:** Nexo Pay S.A.

**Capa de Arquitectura:** Capa de Dominio y Datos Compartidos (Abstracción del Enrutador de IA)

**Última Revisión:** Mayo de 2026

# 1\. Marco conceptual de la ontología y arquitectura del enrutador (*router*)

El sistema Nexo Pay procesa consultas conversacionales a escala masiva a través de una arquitectura híbrida. Para garantizar que las respuestas sean verídicas, seguras y eficientes, el agente de Inteligencia Artificial debe clasificar la entrada del usuario de forma binaria e inmediata en una de las dos capas de procesamiento disponibles: la **Capa de Recuperación Semántica (RAG)** o la **Capa de Ejecución Transaccional (SQL Tools)**.

## 1.1 El riesgo de la frontera difusa y alucinación cruzada

Si el agente conversacional carece de una ontología clara, se expone a fallas críticas de ejecución:

* **Falso Positivo Transaccional:** Intentar responder una pregunta puramente institucional (ej. horarios de clearing bancario) ejecutando código o consultas SQL genéricas sobre las tablas operativas, lo que genera excepciones de base de datos o denegaciones de servicio.  
* **Falso Positivo Semántico:** Intentar responder sobre el estado financiero actual y personalizado de un cliente (ej. saldo disponible o últimas transferencias) leyendo los manuales estáticos del RAG, provocando que el modelo alucine números, saldos o estados de tarjetas ficticios.

# 2\. Clasificación categórica de la información estática y teórica (capa rag)

La **Capa RAG (Retrieval-Augmented Generation)** se alimenta exclusivamente del Vector Store. Comprende toda la información institucional, normativa, comercial, legal y procedimental que no cambia en tiempo real por cada transacción individual, sino que constituye el marco de reglas fijas de Nexo Pay.

## 2.1 Criterios de inclusión en la capa rag

El enrutador derivará la consulta al motor de búsqueda semántica si el input del usuario se encuentra dentro de las siguientes categorías de negocio:

### a. Requisitos de elegibilidad y procesos de alta preventa

* Consultas referidas a las condiciones obligatorias para solicitar productos financieros (edades, historial crediticio previo, documentación formal).  
* Pasos institucionales para la apertura de cuentas del segmento básico o del segmento Premium.

### b. Políticas comerciales, estructura de costos y comisiones

* Preguntas teóricas sobre comisiones fijas por compras en el extranjero, cargos administrativos por extracciones en cajeros automáticos externos o costos de mantenimiento mensual de las membresías.  
* Reglamentos sobre límites máximos de transferencias diarias autorizadas de forma estándar por la plataforma.

### c. Horarios operativos y ventanas de compensación (clearing)

* Consultas sobre el tiempo estimado de acreditación de transferencias inmediatas de red o las ventanas horarias estándar de clearing bancario diferido para operaciones programadas o fines de semana.

### d. Condiciones técnicas de instrumentos de inversión

* Reglas de funcionamiento conceptual del Fondo Común de Inversión (FCI), plazos mínimos de inmovilización de capital para Plazos Fijos Tradicionales y penalizaciones por precancelación anticipada.

### e. Playbooks de emergencia, seguridad y ciberdelito

* Guías paso a paso sobre cómo actuar ante el robo o extravío de un plástico, cómo iniciar un reclamo por desconocimiento de consumo o estafa virtual, y el procedimiento para realizar un Stop Debit de un servicio preautorizado.

### f. Soporte técnico de la interfaz y accesibilidad de la app

* Soluciones manuales a problemas de hardware del usuario, guías de configuración y reenrolamiento de datos biométricos (rostro y huella) y compatibilidad de versiones mínimas de sistemas operativos para descargar la aplicación móvil.

### g. Gobernanza, compliance interno y fallback conversacional

* Interacciones triviales (*Chitchat*), saludos, insultos o mensajes fuera de alcance que deban activar los protocolos de contención emocional, alertas de enmascaramiento de datos sensibles o el cierre automático por ruido operativo.

# 3\. Clasificación categórica de la información dinámica y transaccional (capa sql tools)

La **Capa de Herramientas SQL (SQL Tools)** interactúa directamente con el motor de base de datos relacional en un entorno aislado. Comprende única y exclusivamente los datos mutables, históricos, paramétricos e individuales de la cuenta del usuario que realiza la consulta en tiempo real.

## 3.1 Criterios de inclusión en la capa sql tools

El enrutador interceptará la consulta e invocará la ejecución de funciones programadas si el input del usuario exige conocer o modificar el estado real de sus registros bajo los siguientes dominios:

### a. Estado actual del balance y disponibilidad de fondos

* Consultas en tiempo real sobre el dinero exacto disponible en la cuenta corriente, caja de ahorro o billetera virtual del cliente (*«¿Cuánta plata tengo?»*, *«Decime mi saldo»*, *«¿Se me acreditó el sueldo?»*).

### b. Historial cronológico de movimientos y transacciones recientes

* Solicitudes de visualización, filtrado o auditoría de consumos pasados, transferencias enviadas o recibidas, depósitos realizados o cobros de facturas automáticas (*«Pasame mis últimos movimientos»*, *«Quiero ver si se pagó Netflix ayer»*, *«¿Cuánto gasté en el súper la semana pasada?»*).

### c. Estado de activación y bloqueo de plásticos físicos o virtuales

* Verificación del estado logístico o de seguridad de las tarjetas de débito o crédito asociadas a la identidad del cliente (*«¿Mi tarjeta de débito está activa o bloqueada?»*, *«Fíjate si está habilitada la tarjeta virtual»*).

### d. Estado de seguridad informática y restricciones de acceso de la cuenta

* Diagnóstico operativo sobre si la cuenta del usuario se encuentra activa, suspendida preventivamente por sospecha de fraude, o bloqueada por el ingreso fallido de contraseñas (*«¿Por qué me dice cuenta bloqueada?»*, *«Fíjate si tengo la cuenta suspendida»*).

# 4\. Protocolo de inferencia híbrida y resolución de ambigüedades (multi-intent handling)

Los usuarios de alta escala suelen unificar consultas estáticas y dinámicas en un solo bloque de texto continuo (*«Quiero saber cuál es mi saldo actual y cómo hago para pedir un plazo fijo»*). El enrutador de LangGraph resolverá estas interacciones complejas aplicando las siguientes reglas de negocio de inferencia:

## 4.1 Descomposición jerárquica de intenciones combinadas

Cuando la entrada del cliente contenga intenciones que pertenezcan a ambas capas de la ontología de forma simultánea, el sistema aplicará un orden de ejecución estrictamente secuencial:

1. **Fase 1: Ejecución Dinámica Primero:** El bot invocará prioritariamente la herramienta SQL para capturar los datos reales del cliente (por ejemplo, extraer su balance o el estado de sus tarjetas) para garantizar la personalización del contexto.  
2. **Fase 2: Enriquecimiento Semántico:** El bot acoplará la información transaccional obtenida en la Fase 1 con el fragmento de texto recuperado por el buscador semántico desde el RAG (por ejemplo, las condiciones normativas del plazo fijo).  
3. **Fase 3: Ensamblado de Respuesta Unificada:** El modelo consolidará ambas dimensiones en una única respuesta coherente, evitando derivar al usuario a dos flujos separados.

## 4.2 Resolución de ambigüedades por contexto inmediato

* Si la consulta del usuario es semánticamente ambigua (*«No puedo operar»*), el enrutador priorizará la Capa SQL Tools para diagnosticar el estado del cliente en la base de datos (verificando si su cuenta o tarjeta poseen flags de bloqueo preventivo). Si los registros relacionales están en orden, el bot asumirá que es un problema de la interfaz de usuario y redirigirá el flujo hacia la Capa RAG, recuperando el manual de soporte técnico y accesibilidad de la aplicación.