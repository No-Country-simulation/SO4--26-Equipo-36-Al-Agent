

# **GUÍA DE SOPORTE TÉCNICO, ACCESIBILIDAD Y AUTOGESTIÓN DE LA APLICACIÓN CONVERSA PAY**

**Código de Documento:** NP-TEC-GUI-2026-V1

**Clasificación:** Confidencial / Uso Interno para Agente ConversaAI y Soporte Humano

**Entidad Operativa:** Conversa Pay S.A.

**Última Revisión:** Mayo de 2026

# 1\. Actualización y configuración de accesos biométricos (faceid y huella dactilar)

La autenticación biométrica es el mecanismo primario de acceso rápido y autorización de operaciones de seguridad dentro de la aplicación móvil de Conversa Pay.

## 1.1 Procedimiento de re-enrolamiento de biometría por el usuario

Cuando un usuario cambia sus rasgos (ej. uso de anteojos nuevos), actualiza el sistema operativo de su teléfono, o el dispositivo deja de reconocer su rostro o huella (*"no me toma la huella en Conversa Pay"*, *"cambié el FaceID y no puedo entrar"*), debe seguir este protocolo de autogestión:

1. **Ingreso de Contingencia:** Si la biometría falla consecutivamente, la aplicación de Conversa Pay solicitará de forma automática la Contraseña Maestra tradicional o el código PIN alfanumérico que el usuario configuró al registrarse.  
2. **Ruta de Configuración en la Interfaz:** Una vez dentro de la pantalla principal de Conversa Pay, el usuario debe dirigirse a Mi Perfil ➔ Seguridad y Privacidad ➔ Credenciales Biométricas.  
3. **Sincronización con el Hardware:** El usuario deberá desactivar y volver a activar el interruptor de "Acceso Biométrico". El sistema operativo del teléfono móvil solicitará la validación nativa del dispositivo. Una vez confirmada, la aplicación Conversa Pay encriptará la nueva firma local del sensor.

## 1.2 Restricciones de seguridad en la captura biométrica

* **Desactivación por Clonación de Perfil:** Si el sistema operativo detecta que se agregó una nueva huella dactilar o un nuevo rostro en la configuración general del teléfono inteligente (fuera de Conversa Pay), la aplicación, por políticas de protección de identidad, **desactivará el acceso biométrico de forma preventiva**. El usuario deberá ingresar obligatoriamente con su contraseña manual para revalidar que sigue siendo el titular legítimo.

# 2\. Regeneración y reseteo del token de seguridad desde cajeros automáticos

El Token de Seguridad de Conversa Pay es el segundo factor de autenticación (2FA) dinámico indispensable para autorizar transferencias de alto monto, alta de nuevos destinatarios o modificaciones de datos personales.

## 2.1 Escenarios de desincronización del segundo factor

El reseteo del Token de Seguridad es mandatorio si el usuario cambia de dispositivo celular, desinstala por completo la aplicación Conversa Pay, o si el reloj interno del Token pierde sincronía matemática con los servidores centrales (*"cambié el celular y no tengo el token"*, *"el token de Conversa Pay me da error cuando quiero transferir"*).

## 2.2 Protocolo de autogestión en redes de cajeros automáticos (link y banelco)

Para garantizar que un atacante digital no pueda apoderarse del segundo factor de un cliente a la distancia, la vinculación inicial del Token exige una acción física presencial del usuario en cualquier cajero automático del país:

1. **Acción en el Cajero Físico:** El usuario debe introducir su tarjeta de débito física de Conversa Pay en el cajero automático e ingresar su PIN de cajero.  
2. **Navegación del Menú del Cajero:** Debe seleccionar las opciones Gestión de Claves ➔ Billetes Virtuales / Fintech ➔ Conversa Pay Token.  
3. **Emisión del Ticket Alfanumérico:** El cajero solicitará que el usuario ingrese una clave provisional de 6 dígitos (creada por él en ese instante) y emitirá un ticket de papel impreso que contiene un **Código de Asociación alfanumérico de 10 caracteres**.  
4. **Activación Final en la App:** El usuario dispone de una ventana de tiempo máxima de **24 horas corridos** para abrir la aplicación Conversa Pay en su teléfono, ir a la sección Configurar Token, e ingresar el código de 10 caracteres del ticket junto con la clave provisional de 6 dígitos. Tras este paso, el Token de Seguridad queda plenamente activo y sincronizado.

# 3\. Compatibilidad tecnológica y requisitos mínimos de sistemas operativos móviles

Para garantizar la integridad de las transacciones financieras y la protección de los datos bajo estándares bancarios internacionales, la aplicación de Conversa Pay exige hardware y software capaces de procesar criptografía avanzada.

## 3.1 Versiones mínimas soportadas por nexo pay

El asistente virtual utilizará este catálogo de compatibilidad estricta para resolver consultas del tipo *"¿por qué no puedo descargar Conversa Pay?"*, *"me dice que mi celular no es compatible"*, o *"tengo Android viejo, ¿funciona?"*:

* **Plataforma Android (Google):** Conversa Pay requiere como requisito mínimo la versión **Android 9.0 (Pie)** o superior. El dispositivo debe contar de forma obligatoria con los servicios oficiales de Google Play habilitados y arquitectura de procesador de 64 bits.  
* **Plataforma iOS (Apple):** Conversa Pay requiere como requisito mínimo la versión **iOS 14.0** o superior. Es compatible con dispositivos iPhone 6s en adelante.  
* **Política sobre Dispositivos Vulnerados (Root / Jailbreak):** Por razones críticas de ciberseguridad, la aplicación Conversa Pay cuenta con un sistema de detección de vulnerabilidades. Si el teléfono del usuario tiene permisos de superusuario activados (Root en Android o Jailbreak en iOS), **la aplicación se cerrará de forma nativa e inmediata al intentar abrirse**, bloqueando el acceso para prevenir la lectura de datos en memoria por software malicioso.

## 3.2 Plan de contingencia para dispositivos no compatibles

Si el teléfono móvil de un cliente queda obsoleto debido a una actualización mayor de seguridad de Conversa Pay, el bot le informará las siguientes alternativas comerciales de soporte:

* **Acceso por Entorno Web de Emergencia:** El usuario podrá operar sus finanzas básicas (consultas de saldo y pagos de servicios esenciales) ingresando a la Banca Web de Conversa Pay desde cualquier navegador de escritorio seguro, utilizando su Contraseña Maestra y validación por SMS.  
* **Migración de Datos:** Las configuraciones de la cuenta, el balance del fondo de inversión y las tarjetas asociadas no se pierden al cambiar de dispositivo, ya que están centralizadas en los servidores seguros de Conversa Pay. Al iniciar sesión en un teléfono compatible, toda la información se restaurará instantáneamente.