# POLÍTICAS COMERCIALES, ESTRUCTURA DE COSTOS Y LÍMITES OPERATIVOS DE CONVERSA PAY

**Código de Documento:** NP-COM-POL-2026-V1

**Clasificación:** Confidencial / Uso Interno para Agente ConversaAI y Soporte Humano

**Entidad Operativa:** Conversa Pay S.A.

**Última Revisión:** Mayo de 2026

# 1\. Regulación de límites máximos de transferencias y movimientos diarios

## 1.1 Límites estándar para transferencias a cuentas de terceros

Con el objetivo de salvaguardar los fondos de los clientes y mitigar los riesgos de fraude digital por suplantación, Conversa Pay establece techos operativos diarios para la salida de capitales.

* **Límite Diario General:** El monto máximo autorizado para transferir desde una cuenta Conversa Pay hacia cuentas de terceros (ya sean CBU bancarias o CVU virtuales de otras entidades) es de **$500.000 pesos argentinos (ARS)** por día calendario. Este límite se restablece automáticamente a las 00:00 horas de cada día.  
* **Transferencias entre Cuentas Conversa Pay:** Los movimientos de fondos realizados entre cuentas propias del mismo titular o hacia otros usuarios registrados dentro de la comunidad Conversa Pay están completamente liberados y no computan para el límite diario de $500.000 ARS.  
* **Frases de Activación en el Buscador Semántico:** El modelo de embeddings asociará consultas como *"¿cuánto es lo máximo que puedo transferir por día?"*, *"límite de envío de plata en Conversa Pay"*, o *"no me deja mandar más de 500 mil pesos"* de forma directa a este apartado.

## 1.2 Procedimiento de excepción para la ampliación temporal de límites

Si un usuario requiere realizar una operación que exceda el tope diario de $500.000 ARS (por ejemplo, para la compra de un vehículo o un bien inmueble), debe solicitar una extensión de límites.

* **Mecanismo de Autogestión:** La ampliación no puede ser otorgada de forma directa por el chat de texto del asistente virtual por razones de seguridad. El bot redirigirá al usuario a la sección de configuración de seguridad de la aplicación de Conversa Pay.  
* **Validación Biométrica Requerida:** El usuario deberá superar una prueba de vida biométrica y registrar el CBU/CVU de destino con un mínimo de 24 horas de anticipación. Una vez aprobada por el sistema, la extensión del límite operativo tendrá una vigencia estricta de 24 horas corridas.

# 2\. Horarios de operación y compensación bancaria (clearing)

# 2.1 Transferencias inmediatas y disponibilidad del servicio

Conversa Pay está adherida al sistema de pagos del ecosistema financiero nacional, garantizando que la enorme mayoría de las operaciones se procesen en tiempo real.

* **Disponibilidad 24/7:** Las transferencias salientes e ingresantes hacia alias, CBU o CVU operan las 24 horas del día, los 36 como los 7 días de la semana, incluyendo fines de semana y días feriados. El tiempo de acreditación estimado para estas transacciones inmediatas es menor a los 15 segundos.  
* **Alertas de Red Externa:** Si una transferencia inmediata sufre demoras, el asistente virtual informará al usuario que la demora no responde a las reglas de negocio de Conversa Pay, sino a congestiones temporales en la cámara compensadora central (COELSA) o en la entidad receptora de los fondos.

### **2.2 Ventanas de clearing bancario para operaciones programadas**

Existen transacciones específicas (como la liquidación de ciertos fondos de inversión, pago de haberes programados o transferencias consolidadas de empresas) que no se ejecutan por la vía inmediata y quedan sujetas a ventanas de clearing diferido.

* **Horarios de Compensación:** Las ventanas de clearing en días hábiles bancarios están fijadas en tres horarios estrictos: **09:00 horas, 14:00 horas y 18:00 horas**.  
* **Impacto del Horario de Corte:** Toda operación sujeta a clearing que sea cargada por el usuario después de las 18:00 horas, o que se registre durante días no hábiles, será retenida preventivamente y se procesará en la primera ventana de compensación del siguiente día hábil bancario.

# 3\. Estructura de mantenimiento de cuentas y condiciones comerciales

Conversa Pay ofrece dos segmentos de cuentas comerciales para sus usuarios individuales, cuyas reglas de costos y beneficios se detallan a continuación:

## 3.1 Cuenta segmento básico (plan esencial nexo pay)

* **Costo de Mantenimiento:** El costo mensual de apertura, renovación y mantenimiento de la Cuenta Básica es de **$0 ARS (completamente bonificado)**.  
* **Beneficios Incluidos:** Acceso a la billetera virtual, transferencias inmediatas ilimitadas, una tarjeta de débito física provista sin cargo y acceso completo al soporte automatizado del asistente virtual.

## 3.2 Cuenta segmento premium (plan nexo pay gold)

* **Costo de Mantenimiento:** El Plan Premium posee un cargo fijo mensual de **$5.000 ARS**, el cual se debita automáticamente del saldo disponible de la cuenta del usuario el primer día hábil de cada mes calendario.  
* **Beneficios Exclusivos:** Tasas preferenciales de rendimiento en fondos de inversión, reintegros (cashback) del 5% en compras seleccionadas, atención prioritaria con operadores humanos y la bonificación total en redes de cajeros externos.  
* **Política de Saldo Insuficiente:** Si al llegar el día del cobro de la membresía Premium el saldo disponible del usuario es menor a $5.000 ARS, el sistema suspenderá los beneficios exclusivos y migrará la cuenta al Segmento Básico de forma automática. El servicio Premium se reactivará una vez que el cliente regularice su saldo.

# 4\. Comisiones por operaciones internacionales y redes de cajeros externa

## 4.1 Extracciones de efectivo en cajeros automáticos locales (red link y banelco)

Conversa Pay permite a sus clientes retirar dinero en efectivo de sus cuentas utilizando su tarjeta de débito física en cualquier terminal del país.

* **Usuarios del Segmento Básico:** Disponen de **dos (2) extracciones mensuales gratuitas** en cualquier cajero automático. A partir de la tercera extracción del mes, cada operación sufrirá un cargo administrativo fijo de **$350 ARS**, el cual se restará del saldo en el momento de la extracción.  
* **Usuarios del Segmento Premium:** Todas las extracciones de efectivo están bonificadas al 100%, de forma ilimitada, independientemente de la red de cajeros utilizada (Link o Banelco).

## 4.2 Comisiones por compras e interacciones internacionales

Cuando un usuario utiliza su tarjeta Conversa Pay (física o virtual) para adquirir bienes o servicios en el extranjero o en plataformas digitales radicadas fuera del territorio nacional (ej: servicios de streaming, tiendas internacionales, licencias de software), se aplican las siguientes reglas comerciales:

* **Tasa de Comisión Administrativa:** Conversa Pay aplica un cargo del **3% sobre el monto neto de la transacción** en concepto de gastos de procesamiento internacional. Esta comisión se calcula sobre el tipo de cambio oficial mayorista del día de la operación.  
* **Percepción de Impuestos Locales:** El asistente de IA debe informar con precisión que, de acuerdo con las normativas fiscales vigentes del país, las compras internacionales se verán gravadas con los impuestos nacionales correspondientes (Impuesto PAIS, Percepciones de Ganancias y Bienes Personales). Estos cargos tributarios se desglosan en el comprobante comercial de forma separada a la comisión de Conversa Pay.