

# MANUAL DE PROCEDIMIENTOS DE EMERGENCIA, SEGURIDAD Y MITIGACIÓN DE FRAUDES

**Código de Documento:** NP-SEC-MAN-2026-V4

**Clasificación:** Confidencial / Uso Interno para Agente ConversaAI y Soporte Humano

**Entidad Operativa:** Nexo Pay S.A.

**Última Revisión:** Mayo de 2026

# 1\. Protocolo integral ante compromiso de tarjetas (débito, crédito y virtual)

## 1.1 Denuncia por robo, hurto, extravío o sospecha de clonación de tarjetas

El compromiso físico o virtual de una tarjeta exige una respuesta inmediata para contener el riesgo de pérdidas financieras. El usuario puede manifestar este estado de emergencia en el canal de chat utilizando lenguaje coloquial o técnico (*"perdí mi tarjeta de débito"*, *"me robaron la billetera con la de crédito"*, *"creo que me clonaron la tarjeta en un cajero"*, *"veo consumos de un plástico que no solicité"*).

* **Acción del Asistente Virtual:** Al procesar este pedido, el asistente de IA invocará de forma prioritaria la función de inhabilitación de tarjetas. El sistema registrará el plástico afectado bajo el estado de "Bloqueo Permanente".  
* **Irreversibilidad de la Denuncia:** Por políticas internacionales de mitigación de fraudes de Nexo Pay, una vez que una tarjeta física ha sido denunciada por robo o extravío, su inhabilitación es definitiva. El asistente virtual no está autorizado a reactivar una tarjeta denunciada bajo ninguna circunstancia, previniendo ataques de ingeniería social donde un tercero intenta dar de alta un plástico robado.  
* **Reposición y Logística de Nuevos Plásticos:** La confirmación del bloqueo genera automáticamente una orden de impresión y distribución de un nuevo plástico hacia el domicilio del cliente. La primera reposición anual de la tarjeta de débito está completamente bonificada. Reposiciones consecutivas dentro del mismo año fiscal sufrirán un cargo administrativo que se debitará del saldo disponible de la cuenta.  
* **Emisión de Tarjeta Virtual de Emergencia:** Para garantizar la continuidad transaccional y evitar que el cliente quede financieramente inmovilizado durante los días que demore la entrega del plástico físico, el sistema ofrecerá la habilitación instantánea de una tarjeta virtual con credenciales nuevas y un código de seguridad dinámico de alta expiración.

# 1.2 Desconocimiento de consumos, compras no autorizadas y cargos duplicados

Este procedimiento regula los escenarios donde el usuario mantiene la posesión física de su tarjeta pero visualiza movimientos anómalos o duplicados en su historial de actividad (*"me cobraron dos veces la misma compra"*, *"tengo un gasto en un negocio donde nunca fui"*, *"este consumo está aprobado y yo no compré nada"*).

* **Ventana Temporal para Reclamaciones:** El usuario dispone de un plazo estricto de 30 días corridos, contados a partir de la fecha de ejecución de la transacción, para asentar un desconocimiento formal. Transcurrido dicho plazo, el movimiento se considera aceptado y firme.  
* **Aislamiento del Movimiento en Disputa:** El asistente virtual requerirá que el usuario identifique el movimiento sospechoso presentando las últimas interacciones comerciales de la cuenta para que el cliente seleccione el identificador del incidente.  
* **Auditoría y Etiquetado de Soporte:** Una vez confirmado el fraude potencial por el usuario, el sistema de evaluación asienta el caso en el repositorio analítico e inyecta las etiquetas de categorización de incidentes por fraude y prioridad alta. El dinero en disputa entrará en estado de retención preventiva hasta que el equipo de auditoría humana determine la legitimidad del reclamo.

# 2\. Protocolo operativo ante estafas virtuales y suplantación de identidad (account takeover)

## 2.1 Mitigación de vaciado de cuentas y accesos no autorizados

Este protocolo de máxima prioridad se activa cuando el usuario reporta que terceros han vulnerado sus claves de acceso, o que ha sido víctima de maniobras de fraude telefónico o digital (*"me vaciaron la caja de ahorro"*, *"alguien entró a mi cuenta y mandó plata a otro lado"*, *"me engañaron por teléfono y pasé mis datos de acceso"*).

1. **Congelamiento Preventivo de la Cuenta:** El asistente virtual suspenderá inmediatamente toda capacidad transaccional saliente del cliente cambiando el estado de la cuenta a "Suspendida por Seguridad". Cualquier intento posterior de transferir o retirar fondos desde esa cuenta será rechazado de forma nativa por el sistema.  
2. **Revocación de Sesiones Activas:** El sistema destruirá de inmediato todas las sesiones y tokens de autenticación activos vinculados al usuario, forzando el cierre de sesión en todos los dispositivos móviles y navegadores web registrados.  
3. **Trazabilidad de la Transferencia Fraudulenta:** El sistema aislará los registros de las transferencias salientes ocurridas durante la ventana del incidente para extraer el destino de los fondos, el monto de la estafa y la descripción registrada, confeccionando un Comprobante Técnico de Emergencia.  
4. **Derivación Judicial:** El asistente proveerá al usuario un código único de incidente y le indicará los pasos obligatorios para radicar la denuncia ante las fiscalías especializadas en ciberdelincuencia, informando que la empresa compartirá los registros de conexión del atacante únicamente ante un requerimiento judicial formal.

## 2.2 Exclusiones de responsabilidad financiera por negligencia del usuario

* **Divulgación Voluntaria de Credenciales:** Nexo Pay queda exenta de la obligación de restitución de fondos si las auditorías de accesos demuestran que el compromiso de la cuenta se produjo porque el usuario facilitó deliberadamente sus factores de autenticación (claves secretas o tokens dinámicos) a un tercero, violando las políticas de confidencialidad del servicio.

# 3\. Protocolo para la gestión de débitos automáticos y reversas (stop debit)

## 3.1 Suspensión de cobros inminentes de servicios (Stop Debit)

El usuario posee el derecho de detener un cobro preautorizado asociado a una empresa de servicios adherida a su cuenta de Nexo Pay (*"quiero que no me descuenten la cuota de este mes"*, *"hacer un stop debit a la factura"*, *"frenar el cobro automático de servicios"*).

* **Restricción de Ventana Temporal:** Para que la orden de Stop Debit sea viable para el ciclo de facturación actual, la solicitud debe ser procesada con una antelación mínima de **48 horas hábiles** respecto de la fecha estimada de cobro. Las solicitudes entrantes fuera de esta ventana no podrán frenar el débito y el usuario deberá recurrir al protocolo de reversión posterior.  
* **Efecto de la Orden de Exclusión:** La función de Stop Debit genera una regla de rechazo temporal en el motor de pagos que bloquea las peticiones de cobro entrantes que coincidan con la empresa por el mes calendario en curso, impidiendo que afecte el saldo disponible.  
* **Diferenciación Conceptual de Intenciones:** El asistente debe esclarecer si el usuario desea suspender un único pago (Stop Debit) o si desea que el cobro no se vuelva a ejecutar nunca más en el futuro, caso en el cual el procedimiento correcto es la "Baja Definitiva de la Adhesión al Débito", que rompe el contrato de débito automático de forma permanente.

## 3.2 Derecho de reversión de débitos ya ejecutados

* Si un débito automático ya fue cobrado, el usuario puede solicitar la devolución total del dinero dentro de los 30 días posteriores al cobro. El sistema validará que la transacción exista bajo la categoría de pago de servicios y, de cumplir los requisitos, acreditará el dinero de forma provisional en un plazo máximo de 72 horas hábiles.

# 4\. Protocolo de recuperación ante bloqueo informático de cuenta

## 4.1 Bloqueo por fuerza bruta o errores biométricos

Como contramedida de seguridad para mitigar ataques de adivinación de contraseñas, el motor de autenticación cambia el estado de la cuenta a "Bloqueada por Seguridad" tras registrarse **3 intentos fallidos consecutivos** en el ingreso del PIN o contraseña.

* **Manifestación de Frustración en los Canales:** Los usuarios afectados suelen ingresar manifestando malestar (*"la app me echó y no me deja entrar"*, *"bloquee mi cuenta por poner mal el pin"*, *"necesito sacar plata y me dice cuenta suspendida"*). Esto activa la matriz heurística fijando la resolución en estado crítico de frustración.  
* **Prohibición de Credenciales por Texto Abierto:** Por directrices estrictas de seguridad de la información, el asistente virtual tiene **estrictamente prohibido** recibir contraseñas, códigos o factores biográficos a través del chat de texto plano. El bot jamás debe solicitar ni escribir claves en la conversación.  
* **Procedimiento Seguro de Desbloqueo Fuera de Banda (Out-of-Band):**  
  1. El sistema verifica que la cuenta exista y que efectivamente posea el estado de bloqueo activo.  
  2. El asistente genera un token de autenticación de un solo uso con una vida útil de 10 minutos y lo envía empaquetado en un enlace dinámico directo al correo electrónico verificado del cliente.  
  3. El enlace redirige al usuario al entorno seguro de la aplicación nativa, donde se requerirá una prueba de vida biométrica. Una vez superada, el sistema ejecuta de forma automática el desbloqueo de la cuenta en el entorno operativo.