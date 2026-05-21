# GUÍA DE PRODUCTOS FINANCIEROS, INVERSIONES Y SOPORTE PREVENTA DE NEXO PAY

**Código de Documento:** NP-INV-GUI-2026-V1

**Clasificación:** Confidencial / Uso Interno para Agente ConversaAI y Soporte Humano

**Entidad Operativa:** Nexo Pay S.A.

**Última Revisión:** Mayo de 2026

# 1\. Requisitos y condiciones para acceder a préstamos pre-aprobados

Nexo Pay ofrece líneas de financiamiento de otorgamiento inmediato sujetas a evaluación de riesgo crediticio automatizada. El asistente virtual resolverá consultas preventa utilizando los criterios de elegibilidad comercial establecidos por la entidad.

## 1.1 Criterios mandatorios de elegibilidad comercial

Para que un cliente pueda visualizar y aceptar una oferta de préstamo preaprobado en su cuenta de Nexo Pay, debe cumplir de forma simultánea con las siguientes condiciones:

* **Edad Mínima y Máxima:** El solicitante debe ser una persona humana de entre 18 y 75 años de edad al momento de la solicitud.  
* **Estado de la Cuenta:** El usuario debe poseer una cuenta activa en Nexo Pay, sin bloqueos preventivos de seguridad ni medidas judiciales vigentes.  
* **Historial de Actividad Mínima:** La cuenta Nexo Pay debe registrar movimientos genuinos de ingresos o consumos durante los últimos 3 meses corridos previos a la solicitud.  
* **Calificación Crediticia Interna:** El cliente debe presentar un comportamiento de pago regular en el ecosistema de Nexo Pay y no registrar deudas activas con saldo en mora en el Sistema Financiero (informe consolidado del Banco Central sin calificaciones negativas).

## 1.2 Mecanismo de Consulta y Activación del Préstamo

* **Consulta de Ofertas Disponibles:** El usuario puede preguntar al bot si dispone de saldo preaprobado (*"¿tengo algún préstamo para sacar?"*, *"¿Nexo Pay me puede prestar plata?"*, *"quiero ver mi límite de crédito"*). El asistente virtual consultará el motor de riesgo y, en caso positivo, le informará el monto máximo disponible, el plazo en cuotas y la tasa efectiva correspondiente.  
* **Restricción de Confirmación Obligatoria:** Por normativas de seguridad, el asistente virtual no puede depositar el préstamo directamente mediante una confirmación en el chat de texto. El bot guiará al usuario enviando un acceso directo a la sección de Créditos de la aplicación nativa, donde el cliente deberá firmar digitalmente el contrato y validar su identidad mediante reconocimiento biométrico. El dinero se acreditará de forma inmediata en el saldo disponible del usuario tras este paso.

# 2\. Funcionamiento del fondo común de inversión (fci) de nexo pay

El Fondo Común de Inversión de Nexo Pay es un instrumento de bajo riesgo diseñado para que los usuarios generen rendimientos diarios con el dinero que tienen depositado en su cuenta, sin necesidad de inmovilizar el capital.

## 2.1 Características de liquidez y rescate inmediato

A diferencia de las inversiones bancarias tradicionales, el fondo de dinero de Nexo Pay prioriza la disponibilidad absoluta de los fondos de sus usuarios.

* **Régimen de Rescate Inmediato (Liquidez 24/7):** El dinero invertido en el fondo de Nexo Pay mantiene disponibilidad inmediata. Esto significa que el cliente puede rescatar (retirar) su capital o utilizar el saldo invertido para pagar servicios, realizar transferencias o hacer compras con su tarjeta en cualquier momento del día, los 365 días del año, incluyendo fines de semana y feriados.  
* **Automatización del Rendimiento:** El usuario puede activar desde la aplicación la opción de "Inversión Automática". Bajo esta modalidad, todo saldo que ingrese a la cuenta Nexo Pay comenzará a generar intereses de forma automática al siguiente día hábil, sin interrumpir la operatividad diaria de la billetera virtual.

## 2.2 Tasa nominal anual (tna) y rendimientos diarios

* **Dinámica de la Tasa Nominal Anual (TNA):** La Tasa Nominal Anual del fondo de Nexo Pay es variable y se actualiza diariamente según el rendimiento de los activos subyacentes del mercado financiero. El asistente virtual siempre informará la última TNA registrada del día (*"¿cuánto está pagando el fondo hoy?"*, *"qué tasa tiene la inversión en Nexo Pay"*), aclarando explícitamente que los rendimientos pasados no garantizan rendimientos futuros.  
* **Acreditación de Intereses:** Los rendimientos generados se calculan diariamente y se acreditan de manera neta en el saldo del usuario de lunes a viernes. Los intereses correspondientes a los días sábados, domingos y feriados se acumulan y se liquidan de forma conjunta en el saldo de la cuenta durante el primer día hábil bancario posterior.

# 3\. Alternativas de plazos fijos disponibles en nexo pay

Para los usuarios que buscan una tasa de interés fija asegurada y están dispuestos a inmovilizar sus fondos por un periodo determinado, Nexo Pay ofrece dos modalidades de Plazo Fijo.

## 3.1 Plazo fijo tradicional

* **Periodo Mínimo de Inmovilización:** El Plazo Fijo Tradicional exige un tiempo de retención mínimo obligatorio de **30 días corridos**. El usuario no puede disponer del dinero bajo ningún concepto hasta que se cumpla la fecha de vencimiento establecida.  
* **Condiciones de Tasa:** Ofrece una Tasa Nominal Anual fija y preestablecida al momento de la constitución del depósito. El asistente virtual simulará el rendimiento estimativo si el usuario provee el monto y los días de permanencia deseados.

## 3.2 Plazo fijo precancelable

* **Mecanismo de Cancelación Anticipada:** Esta modalidad permite constituir la inversión a un plazo de 90 días, pero otorga al cliente la opción de retirar el dinero de forma anticipada a partir del **día 30 de la inversión**.  
* **Penalización de Tasa por Precancela:** Si el usuario ejecuta la opción de precancelación (retiro anticipado), la TNA original contratada se reduce de forma automática, aplicándose una tasa de penalización por retiro anticipado que es inferior a la del Plazo Fijo Tradicional. El bot debe advertir esta penalización ante frases como *"quiero sacar la plata de mi plazo fijo antes de tiempo"*.

# 4\. Plazos de acreditación y liquidación de inversiones

Este apartado define con precisión los tiempos técnicos requeridos para que el dinero invertido regrese al saldo operativo de la cuenta de Nexo Pay según el instrumento seleccionado.

## 4.1 Tiempos de acreditación por instrumento financiero

* **Fondo Común de Inversión (Dinero en Cuenta):** El tiempo de acreditación para los rescates del fondo de liquidez de Nexo Pay es de **0 minutos (inmediato)**. Al solicitar el retiro, el saldo pasa instantáneamente a estar disponible para consumos o transferencias.  
* **Plazo Fijo Tradicional y Precancelable:** Los fondos (capital inicial más los intereses netos generados) se acreditan en la cuenta de Nexo Pay de forma automática durante las primeras horas del **día de vencimiento de la inversión**. Si el día de vencimiento corresponde a un día no hábil, la acreditación de los fondos se producirá el primer día hábil bancario siguiente.  
* **Inversiones de Mediano Riesgo (Fondos Complementarios):** En caso de que el usuario decida migrar sus ahorros a fondos de inversión complementarios de renta fija o variable de Nexo Pay, los plazos de liquidación y acreditación en cuenta varían según el reglamento de gestión, operando bajo ventanas estándar de mercado de **24 horas (T+1) o 48 horas hábiles (T+2)** desde el momento de la solicitud de rescate.