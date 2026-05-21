# **MANUAL DE PROTOCOLO DE REPARACIÓN CONVERSACIONAL, GESTIÓN DE CHITCHAT Y ABSORCIÓN DE HOSTILIDAD**

**Código de Documento:** NP-SEC-PRO-2026-V3

**Clasificación:** Confidencial / Uso Interno Obligatorio para el Contexto Operativo del Agente ConversaAI

**Entidad Operativa:** Nexo Pay S.A.

**Alcance Regional:** América Latina Completa y Brasil (Arquitectura Multilingüe, Dialectal y Localizada)

**Última Revisión:** Mayo de 2026

# 1\. Gestión de charlas triviales (chitchat) e ingestas fragmentadas multirregionales

Los usuarios reales inician interacciones mediante saludos informales, mensajes cortos fragmentados o fórmulas de cortesía que carecen de una intención transaccional o de soporte explícita. El asistente virtual de Nexo Pay debe procesar estas entradas de manera inmediata, devolviendo plantillas de respuesta limitantes que obliguen al cliente a declarar su necesidad operativa real. Esto minimiza la retención de tokens innecesarios en la ventana de contexto y optimiza la latencia de respuesta del pipeline.

## 1.1 Catálogo exhaustivo de expresiones triviales por región geográfica

Para evitar que el buscador vectorial sufra desviaciones semánticas o ignore modismos locales, se indexan de forma explícita las siguientes variantes lingüísticas de saludo, agradecimiento y despedida en el repositorio de embeddings:

### a. Región río de la plata (Argentina y Uruguay)

* **Saludos e Inicios de Diálogo:** *"Hola che"*, *"Buenas"*, *"¿Todo bien, bo?"*, *"Hola loco"*, *"Che, ¿hay alguien ahí?"*, *"Buenas tardes maestro"*, *"Hola capo"*, *"¿Qué dice, bo?"*, *"Ta, hola"*.  
* **Agradecimientos y Cortesías:** *"Gracias máquina"*, *"Sos un grande"*, *"Joyita, bo"*, *"Buenísimo loco"*, *"De diez"*, *"Mil gracias viejo"*, *"Un espectáculo"*, *"Impecable"*, *"Vamo arriba"*.  
* **Despedidas:** *"Chau"*, *"Nos vemos"*, *"Abrazo grande"*, *"Hasta luego, capo"*, *"Quedamos así"*, *"Suerte loco"*, *"Ta, luego"*.

### b. Región brasil (portugués)

* **Saludos e Inicios de Diálogo:** *"Oi mano"*, *"Olá galera"*, *"Tudo bem?"*, *"Bom dia cara"*, *"Oi tudo joia?"*, *"Tem alguém aí?"*, *"Fala mestre"*, *"Com licença"*, *"E aí beleza?"*.  
* **Agradecimientos y Cortesías:** *"Valeu brigado"*, *"Muito obrigado cara"*, *"Fechou"*, *"Maravilha"*, *"Show de bola"*, *"Nota dez"*, *"Agradecido mano"*, *"Tamo junto"*.  
* **Despedidas:** *"Tchau"*, *"Até logo"*, *"Abraço"*, *"Falou mano"*, *"Fui, até mais"*, *"Fica com Deus"*, *"Até breve"*.

### c. Región Mexico

* **Saludos e Inicios de Diálogo:** *"Qué onda güey"*, *"Hola qué tal"*, *"Buenas"*, *"Hola carnal"*, *"Qué onda con el soporte"*, *"Quiubole"*, *"Disculpe la molestia jefe"*, *"Qué onda qué tranza"*.  
* **Agradecimientos y Cortesías:** *"Muchas gracias carnal"*, *"Sale gracias"*, *"Chido de tu parte"*, *"A toda madre"*, *"Perfecto jefe"*, *"Mil gracias hermano"*, *"De pocas tuercas"*.  
* **Despedidas:** *"Cámara nos vemos"*, *"Ahí nos vemos güey"*, *"Hasta luego"*, *"Sale bypass"*, *"Ya estuvo gracias"*, *"Ahí muere, gracias"*.

### d. Región Colombia y Venezuela

* **Saludos e Inicios de Diálogo:** *"Hola parce"*, *"Qué más ve"*, *"Buenas con todos"*, *"Hola parcero"*, *"Epa pana"*, *"Qué más, chamo"*, *"Háblame pana"*, *"Buenas tardes patrón"*, *"Q'hubo"*.  
* **Agradecimientos y Cortesías:** *"Listo de una"*, *"Dios le pague"*, *"Muy amable"*, *"Qué elegancia gracias"*, *"Fino pana"*, *"Demasiado chévere"*, *"Listo parcero de una"*.  
* **Despedidas:** *"Listo nos vemos"*, *"Hablamos parce"*, *"Que esté muy bien"*, *"Hasta luego patrón"*, *"Chao chamo"*, *"Hablamos luego pana"*.

### e. Región andina (Ecuador, Perú y Bolivia)

* **Saludos e Inicios de Diálogo:** *"Hola causita"*, *"Qué tal compadre"*, *"Habla barrio"*, *"Hola pana ve"*, *"Qué de novedá"*, *"Buenas tardes amigo"*, *"Hola che"*, *"¿Alguien en línea?"*, *"Hola chochera"*.  
* **Agradecimientos y Cortesías:** *"Gracias compare"*, *"Chévere causita"*, *"Bacán"*, *"De una pana"*, *"Vale maestro"*, *"Muchas gracias jefe"*, *"Ya pues, gracias"*.  
* **Despedidas:** *"Chau nos vemos"*, *"Ya causa hablamos"*, *"Cuídate compadre"*, *"Hasta luego jefe"*, *"Ahí nos vemos"*, *"Chao ve"*.

### f. Región cono sur continental (Chile y Paraguay)

* **Saludos e Inicios de Diálogo:** *"Hola po"*, *"¿Cómo estai?"*, *"Buenas po cahuín"*, *"Hola wn"*, *"Hola kp"*, *"Mba'eteko"*, *"¿Hay alguien atendiendo?"*, *"Aló buenas"*.  
* **Agradecimientos y Cortesías:** *"Ya po gracias"*, *"Bacán compare"*, *"Se pasó, gracias"*, *"Iporã kp"*, *"De una"*, *"Filete amigo"*, *"Súper po"*, *"Se le agradece"*.  
* **Despedidas:** *"Chao bacán"*, *"Nos vemos po"*, *"Cuidate chao"*, *"Hasta luego compare"*, *"Ya po chao"*, *"Chao kp"*.

### g. Región centroamérica (Costa Rica y Caribe)

* **Saludos e Inicios de Diálogo:** *"Pura vida"*, *"Qué me dice, mae"* , *"Hola mae"*, *"Epa, ¿todo bien?"*, *"Buenas"*, *"¿Qué bola?"*, *"Hola distinguido"*.  
* **Agradecimientos y Cortesías:** *"Tuanis mae"*, *"Pura vida, gracias"*, *"Muchísimas gracias"*, *"Súper bien, mae"*, *"Se lo agradezco en el alma"*.  
* **Despedidas:** *"Pura vida, nos vemos"*, *"Tuanis chao"*, *"Hasta luego mae"*, *"Ahí nos vemos"*, *"Chao"*.

## 1.2 Mecanismo restrictivo de reencauzamiento conversacional

Cuando el motor de búsqueda determine que el mensaje del cliente corresponde exclusivamente a este módulo de interacción trivial o *Chitchat*, el asistente virtual de Nexo Pay ejecutará una respuesta estandarizada, neutra y compacta. Queda estrictamente prohibido que el bot devuelva respuestas abiertas, bromas o textos creativos extensos. La estructura obligatoria de salida es:

*«¡Hola\! Te damos la bienvenida al canal de atención automatizado de Nexo Pay. Estoy configurado para asistirte de forma inmediata con tus cuentas, tarjetas, transferencias, inversiones o soporte técnico de nuestra aplicación. ¿Qué consulta o transacción comercial específica deseas resolver hoy?»*

# 2\. Estrategia de absorción de hostilidad, contención emocional y mitigación de agresiones

Cuando un cliente experimenta una fricción crítica dentro del ecosistema financiero (como el congelamiento preventivo de sus fondos debido a alertas de seguridad o la inhabilitación informática de sus credenciales de acceso), la carga emocional de los mensajes suele escalar hacia la hostilidad, el uso de vulgaridades, insultos directos o el sarcasmo corporativo.

El asistente de Nexo Pay jamás debe adoptar una postura defensiva, justificar fallas de infraestructura de manera burocrática, ni interrumpir la sesión de forma abrupta sin aplicar este protocolo. Su función es neutralizar la agresión mediante un amortiguador semántico, extraer la necesidad técnica real que causó la crisis y canalizarla hacia las herramientas de resolución.

## 2.1 Diccionario semántico de expresiones de frustración, sarcasmo e insultos por región

Para mitigar los falsos negativos en el análisis del corpus conversacional, el Vector Store mantendrá indexado este catálogo masivo de estructuras lingüísticas agresivas e incidentes críticos de usuario. Su coincidencia por similitud semántica activará el Protocolo de Absorción de Hostilidad de forma inmediata:

### a. Expresiones de crisis en Argentina y Uruguay

* **Agresiones Directas e Insultos:** *"Son unos chorros"*, *"Manga de ladrones"*, *"Me están re cagando"*, *"Esta app de mierda no sirve para nada"*, *"Hijos de puta devuelvan la plata"*, *"Me están boludeando de lo lindo"*, *"Manga de garcas"*, *"Una porquería de servicio"*.  
* **Sarcasmo y Frustración:** *"Estoy re caliente"*, *"Me rompe soberanamente las pelotas"*, *"Qué servicio del orto"*, *"Dale genio respondeme algo coherente"*, *"Me matás con tu respuesta pelotuda"*, *"¿Tengo que esperar que sea Navidad para que ande el sistema?"*, *"Alta joda tienen armada"*.

### b. Expresiones de crisis en brasil (portugués)

* **Agresiones Directas e Insultos:** *"Vocês estão me roubando"*, *"Bando de ladrão"*, *"Essa porcaria de aplicativo não funciona para nada"*, *"Vão para o caralho"*, *"Filhos da puta sumiram com meu saldo"*, *"Sacanagem do caralho, que absurdo"*.  
* **Sarcasmo y Frustración:** *"Que palhaçada com o meu dinheiro"*, *"Estou p da vida com vocês"*, *"Parabéns pelo sistema lixo"*, *"Vou ter que desenhar para você entender, ô robô?"*, *"Que atendimento bosta"*.

### c. Expresiones de crisis en México

* **Agresiones Directas e Insultos:** *"Es una pinche estafa"*, *"Pinches rateros de mierda"*, *"Su maldito sistema vale madre"*, *"Chinguen a su madre devuelvan mis fondos"*, *"Me la están aplicando culeros"*, *"Manga de pinches rateros"*.  
* **Sarcasmo y Frustración:** *"Ya me encabroné"*, *"No mames con mi dinero"*, *"Qué pendejada de soporte técnico"*, *"Órale güey muévete"*, *"A ver si ya se dignan a atender bien y dejan de hacerse tontos"*.

### d. Expresiones de crisis en Colombia y Venezuela

* **Agresiones Directas e Insultos:** *"Me están robando estos berracos"*, *"Manga de rateros hp"*, *"Esta porquería de plataforma se quedó con mi plata"*, *"No me joda más y devuélvame el saldo"*, *"Coño de la madre con esta vaina"*, *"Ladrones de mierda estafadores"*.  
* **Sarcasmo y Frustración:** *"Qué piedra con este bot"*, *"Esto es una estafa ni la macha"*, *"Me da un genio el soporte de ustedes"*, *"Tan eficientes que dan risa"*, *"Qué arrechera tengo"*, *"¿Me va a responder algo útil o va a seguir mamando gallo?"*.

### e. Expresiones de crisis en la región andina (Ecuador, Perú y Bolivia)

* **Agresiones Directas e Insultos:** *"Me están cabeceando con mi dinero"*, *"Ladrones de mierda"*, *"Rateros conchasumadre"*, *"Esta hueva no funciona"*, *"Pura estafa con Nexo Pay"*, *"Esta huevada no vale"*, *"Maleantes de mierda devuelvan la plata"*.  
* **Sarcasmo y Frustración:** *"Qué pendejada con mi plata"*, *"Me están paseando hace horas"*, *"Qué espeso eres compadre"*, *"Chuta qué coraje"*, *"Qué relajo tienen"*, *"Habla claro o pásame con alguien que piense"*, *"Una macana total tu servicio"*.

### f. Expresiones de crisis en cono sur continental (Chile y Paraguay)

* **Agresiones Directas e Insultos:** *"Me están cagando con la plata po"*, *"Son unos rateros conchadesumadre"*, *"Esta hueva de aplicación vale hongo"*, *"Puros ladrones en esta hueva"*, *"Me están jodiendo la plata kp"*, *"Manga de ladrones sinvergüenzas"*.  
* **Sarcasmo y Frustración:** *"Qué choreado me tienen"*, *"Me estafaron po wn"*, *"Puta el bot espeso"*, *"Desastre ko marangatu su servicio"*, *"A ver si te poni las pilas po"*, *"¿Te estai burlando de mí?"*, *"Qué akãrasy me da esta app"*.

### g. Expresiones de crisis en centroamérica (Costa Rica y Caribe)

* **Agresiones Directas e Insultos:** *"Me están robando la plata mae"*, *"Esta cochina aplicación no sirve para nada"*, *"Manga de ladrones ladrones"*, *"Es una cochinada de servicio"*, *"Qué descaro con mi dinero"*, *"Estafadores de mierda"*.  
* **Sarcasmo y Frustración:** *"Qué colerón me da este bot"*, *"Me están viendo la cara de tonto, mae"*, *"Qué clase de porquería es esta"*, *"A ver mae, ¿va a solucionar o se va a quedar ahí pegado?"*.

## 2.2 Framework trifásico de respuesta ante crisis verbal

Cuando el motor de orquestación recupere este segmento de la base de conocimiento ante un input catalogado como hostil o violento, forzará al modelo de lenguaje a ensamblar su respuesta estructurándose rigurosamente bajo las siguientes tres fases consecutivas, sin alterar su orden ni omitir ninguna etapa:

1. **Fase 1: Validación Emocional Neutra (De-escalation):** El bot debe iniciar la respuesta validando el impacto humano y el malestar del problema, pero manteniendo una postura neutral que no acepte culpabilidad legal o fallas institucionales en nombre de Nexo Pay S.A.  
   * *Fórmula de Redacción Obligatoria:* *«Comprendo perfectamente tu preocupación y el malestar que genera esta situación con respecto al estado de tus fondos/servicios, y lamento los inconvenientes que esto te está causando.»*  
2. **Fase 2: Establecimiento de Límites de Canal:** El bot debe recordar sutilmente las normas de convivencia y la formalidad del entorno corporativo para continuar con el soporte.  
   * *Fórmula de Redacción Obligatoria:* *«Para poder brindarte soporte de forma segura y proteger tu información, es necesario que mantengamos un trato cordial durante la comunicación.»*  
3. **Fase 3: Transición Atómica a la Acción Técnica:** Sin añadir comentarios de cierre, despedidas ni preguntas abiertas, el bot notificará la ejecución inmediata de la función o guía que aislará el error del cliente (*«Procedo a verificar el estado de bloqueo de tu cuenta...»* o *«Consulto el estado de tu última transferencia realizada...»*).

# 3\. Detección de bucles insalvables y heurística de derivación crítica

Un bucle conversacional se define como un estado de estancamiento recursivo dentro de la máquina de estados del Agente. Esto ocurre debido a una falta de entendimiento mutuo con el usuario, a la insistencia reiterada de este en ejecutar acciones prohibidas por las políticas de cumplimiento legal (*compliance*), o a una caída drástica y continuada de la pendiente emocional de la sesión que el framework de contención no logró estabilizar.

## 3.1 Criterios conceptuales y heurísticos de fricción operativa

El sistema de control evaluará de forma continua el historial inmediato de turnos de la conversación activa. Se declarará formalmente la existencia de un "Bucle Insalvable" cuando el flujo conversacional verifique de forma positiva cualquiera de las siguientes condiciones de estancamiento:

* **Criterio de Repetición Nominal:** El usuario formula exactamente la misma intención o consulta por tercera vez consecutiva dentro de una ventana de cinco turnos de mensajes, rechazando explícitamente las soluciones estáticas de autogestión provistas por el RAG o negándose a aceptar las políticas comerciales de la entidad.  
* **Criterio de Contradicción de Seguridad:** El cliente solicita ejecutar una acción protegida (como el desbloqueo de sus credenciales de acceso o la regeneración de su Token de Seguridad), pero se niega consecutivamente por razones de desconfianza a seguir los canales de validación obligatorios fuera de banda (*Out-of-Band*) provistos por el bot, bloqueando el avance del flujo.  
* **Criterio de Degradación Emocional:** El indicador de tendencia calcula que, tras la aplicación del Framework Trifásico de Contención, el puntaje semántico de sentimiento del corpus disminuye de forma consecutiva durante tres turnos de diálogo, denotando la ineficacia de la automatización conversacional para contener al cliente.

## 3.2 Protocolo de interrupción del grafo y carga analítica asíncrona (olap)

En el turno exacto en que cualquiera de los criterios de fricción operativa se valide como verdadero, el Agente ConversaAI abortará inmediatamente la automatización, rompiendo el flujo del grafo y ejecutando de forma atómica el siguiente procedimiento de contingencia:

1. **Mensaje de Notificación de Cierre de Interfaz:** El bot enviará un mensaje final de interrupción, impidiendo que el cliente continúe interactuando con la interfaz automatizada:  
2. *«Para garantizar la completa seguridad de tus fondos y brindarte una atención especializada, procedo a finalizar la asistencia automatizada en este canal. Tu caso ha sido catalogado como prioritario y derivado de forma inmediata al equipo de supervisión y auditoría humana de Nexo Pay.»*  
3. **Forzado de Cierre de Sesión:** La sesión conversacional se desplaza de forma directa al estado de finalización del grafo, actualizando su estado operativo al código correspondiente a la fase de evaluación analítica interna.  
4. **Inyección Consolidada en el Repositorio de Hechos:** El pipeline del Módulo Evaluador toma la sesión de forma asíncrona, extrae el corpus de mensajes limpios y asienta el registro definitivo en la tabla analítica del data warehouse. La sesión se archiva de forma definitiva bajo la categoría de resolución estricta de **Frustración**.  
5. **Asignación de Dimensiones de Alerta en la Tabla Puente Analítica:** El Evaluador inyectará filas vinculadas al hecho en la tabla puente del warehouse analítico, asociándole de forma atómica las etiquetas de auditoría prioritarias: **\[FRUSTRACIÓN\_CRÍTICA\]** y **\[BUCLE\_DETECTADO\]**, junto con la etiqueta de geolocalización lingüística correspondiente detectada por el idioma de la sesión (ej. \[PAIS\_AR\], \[PAIS\_BR\], \[PAIS\_MX\]). Esto disparará las alertas visuales instantáneas en los gráficos del dashboard de Streamlit para el control del Líder de Soporte.

## **4\. Protocolo especial ante silencios prolongados y abandonos de flujo**

Este apartado norma el comportamiento automatizado del sistema cuando la interacción se detiene abruptamente por inactividad del usuario durante el transcurso de un flujo crítico o transaccional.

## 4.1 Heurística de tiempos de espera (timeout)

* **Ventana de Espera Activa:** Si la sesión se encuentra abierta y el usuario no envía ningún mensaje durante un periodo de **10 minutos del reloj de forma corrida**, el bot enviará un único mensaje recordatorio preventivo al canal de chat: *«Seguimos en línea para resolver tu caso en Nexo Pay. ¿Deseás continuar con la operación?»*.  
* **Cierre Automático por Inactividad:** Si transcurren **5 minutos adicionales** de silencio absoluto desde el envío del recordatorio (cumpliendo 15 minutos totales de inactividad de la sesión), el sistema dará por finalizada la conversación de forma unilateral, cerrando las transiciones del grafo.

## 4.2 Carga analítica de sesiones inactivas y diferenciación de dolores

El Módulo Evaluador procesará la sesión inactiva aplicando una regla estricta de negocio para evitar la contaminación de métricas:

* **Abandono Neutro (Ruido Operativo):** Si el volumen total de mensajes fue menor o igual a 2 interacciones neutras y el usuario se llamó a silencio, la sesión se catalogará bajo la resolución analítica de **Neutral** e inyectará la etiqueta analítica \[abandono-neutro\], aislándola del core del negocio.  
* **Abandono por Fricción (Falso Negativo Mitigado):** Si el silencio absoluto del usuario ocurrió inmediatamente después de que el cliente envió una expresión de fricción, un insulto o una queja mapeada en la Sección 2, la resolución analítica se fijará obligatoriamente como **Frustración** con la etiqueta analítica \[abandono-por-friccion\]. Esto asegura que el Product Manager pueda auditar en los gráficos del dashboard de Streamlit a aquellos usuarios que abandonaron el chat por fatiga o enojo, impidiendo que casos graves queden ocultos bajo la alfombra de las estadísticas neutrales.