# **GLOSARIO DE SINONIMIA FINANCIERA REGIONAL Y HOMOLOGACIÓN DE JERGA COLOQUIAL**

**Código de Documento:** NP-OR-GLO-2026-V1

**Clasificación:** Confidencial / Uso Interno Obligatorio para Enriquecimiento del Vector Store y Agente ConversaAI

**Entidad Operativa:** Nexo Pay S.A.

**Cobertura Semántica:** América Latina y Brasil (Fusión de Modismos, Lunfardo y Jerga Financiera Regional)

**Última Revisión:** Mayo de 2026

# 1\. Marco operativo de homologación semántica para modelos de embeddings

Los modelos de embeddings comerciales tradicionales y de código abierto son entrenados con corpus lingüísticos globales, formales y estandarizados. Por esta razón, carecen de la capacidad nativa para comprender las variaciones del lunfardo argentino, los modismos de América Latina o la jerga callejera de Brasil en un contexto de fricción financiera.

Si un usuario escribe de forma desesperada en el chat de WhatsApp: *«Quiero meter toda mi guita en el cosito que rinde por día en la app»*, un buscador vectorial convencional sin indexación regional podría sufrir desviaciones de distancia semántica, provocando que el asistente virtual no comprenda la solicitud o responda que la información no está disponible.

Este glosario funciona como una **capa de traducción conceptual y puente semántico**. Su objetivo es asociar de forma matemática y unívoca las expresiones populares con los conceptos formales de los manuales de negocio de Nexo Pay S.A.

# 2\. Matriz expandida de equivalencias por dominios financieros

A continuación, se establecen las equivalencias conceptuales obligatorias. Toda coincidencia vectorial con los términos de la columna izquierda debe forzar la recuperación de los manuales técnicos indexados correspondientes a la columna derecha.

## 2.1 Dominio de capital, fondos dinero y concepto de "saldo disponible"

Toda expresión que denote la posesión, el resguardo o la falta de dinero líquido del cliente debe mapearse semánticamente hacia las guías de **Consulta de Saldo de Cuenta**, **Balances Operativos** o **Estructura de Costos de Cuentas** de Nexo Pay.

* **Expresiones en Argentina y Uruguay:** *Guita, plata, mangos, guitola, efectivo, capital, fondos, mosca, pasta, los cobres, el saldo, saldo de la cuenta, balance de la cuenta, capital total*.  
* **Expresiones en Brasil (Portugués):** *Grana, dinheiro, bufunfa, dindim, cascalho, numerário, saldo disponível, balanço da conta, fundos da conta, capital disponível*.  
* **Expresiones en México:** *Lana, varo, feria, efectivo, capital, los fondos, maravedíes, billete, pachocha, saldo disponible*.  
* **Expresiones en Colombia y Venezuela:** *Plata, billete, lucas, reales, cobres, los fondos, capital disponible, efectivo, saldo de la cuenta*.  
* **Expresiones en Chile y Paraguay:** *Plata, luquitas, pirapire, efectivo, fondos disponibles, capital de la cuenta, el saldo actual*.  
* **Expresiones en Perú, Ecuador y Bolivia:** *Plata, dinero, fichas, mangos, platita, los fondos, saldo líquido, balance total*.  
* **Expresiones en Costa Rica y Centroamérica:** *Plata, harina, menudos, pasta, biyuyo, efectivo, fondos de la cuenta, saldo disponible*.

## 2.2 Dominio de inversiones, intereses y concepto de "fondo común de inversión (fci)"

Toda consulta donde el usuario busque generar rendimientos con su capital o consulte sobre tasas pasivas sin inmovilizar el dinero de forma estricta debe mapearse semánticamente hacia la **Guía de Productos Financieros e Inversiones (Sección del Fondo de Liquidez 24/7)** de Nexo Pay.

* **Expresiones en Argentina y Uruguay:** *El cosito que rinde por día, poner a trabajar la plata, cuenta remunerada, interés diario del fondo, rendimiento de la app, invertir los mangos, la tasa del fondo, el fondo común de inversión, el interés diario*.  
* **Expresiones en Brasil (Portugués):** *Investimento diário, render todo dia, caixinha rendendo, rendimento diário, fundo de liquidez diária, juros do fundo, aplicação diária, conta rendeira*.  
* **Expresiones en México:** *Inversión de rendimiento diario, lo que da interés por día, cuenta que genera rendimiento, meter lana a invertir, rendimiento de la billetera, tasa del fondo de inversión*.  
* **Expresiones en Colombia y Venezuela:** *El fondo que da ganancias, fondo de liquidez, poner a rentar la plata, los intereses del día, rendimiento diario de la cuenta, inversión express de fondos*.  
* **Expresiones en Chile y Paraguay:** *Platita que rinde por día, la cuenta que da intereses, fondo de inversión inmediato, interés de la billetera, poner a trabajar las luquitas/el pirapire*.  
* **Expresiones en Perú, Ecuador y Bolivia:** *Inversión con interés diario, el fondo mutuo de la app, cuenta que rinde, rentabilizar la plata, intereses del fondo diario, poner a ganar el dinero*.  
* **Expresiones en Costa Rica y Centroamérica:** *Inversión express, poner a ganar la harina, rendimiento diario de la billetera, tasa de interés del fondo, cuenta remunerada*.

## 2.3 Dominio de incidentes en cajeros y concepto de "inhabilitación o retención de tarjetas"

Toda consulta donde el cliente describa que un dispositivo físico retuvo su plástico o que se ha quedado sin acceso a su tarjeta debido a un evento físico externo debe mapearse hacia el **Manual de Procedimientos de Emergencia y Seguridad (Sección de Denuncia y Bloqueo de Tarjetas)** de Nexo Pay.

* **Expresiones en Argentina y Uruguay:** *Me comió la tarjeta, el cajero tragó el plástico, me quedé sin tarjeta, el aparato se quedó con la de débito, me retuvo la tarjeta, plástico trabado en el cajero, denunciar tarjeta de Nexo Pay*.  
* **Expresiones en Brasil (Portugués):** *O caixa engoliu o cartão, cartão retido no caixa eletrônico, máquina prendeu o cartão, perdi o cartão no caixa, bloquear cartão de débito, inativar cartão*.  
* **Expresiones en México:** *El cajero retuvo mi tarjeta, se tragó el plástico, la máquina se quedó con mi tarjeta de débito, tarjeta atorada en el cajero, reportar tarjeta por retención*.  
* **Expresiones en Colombia y Venezuela:** *El cajero me retuvo la tarjeta, tragar tarjeta el cajero, se me quedó la tarjeta metida en el aparato, máquina robó tarjeta, reportar plástico por retención*.  
* **Expresiones en Chile y Paraguay:** *El cajero me tragó la tarjeta, cagó la tarjeta en el cajero, el aparato se quedó con el plástico, tarjeta retenida en terminal física, bloquear plástico por robo*.  
* **Expresiones en Perú, Ecuador y Bolivia:** *El cajero retuvo la tarjeta, la máquina se tragó mi tarjeta de débito, se quedó atrapada mi tarjeta, reportar tarjeta retenida por el cajero automático*.  
* **Expresiones en Costa Rica y Centroamérica:** *El cajero retuvo el plástico, la máquina se quedó con la tarjeta, tarjeta tragada por cajero automático, denunciar tarjeta por pérdida física*.

## 2.4 Dominio de movimientos externos y concepto de "transferencia hacia terceros"

Toda solicitud donde el usuario describa la acción de enviar dinero desde su cuenta hacia otra entidad bancaria o virtual, o solicite los identificadores de red de otra persona, debe mapearse hacia las **Políticas Comerciales, Costos y Límites (Sección de Transferencias a Cuentas de Terceros)** de Nexo Pay.

* **Expresiones en Argentina y Uruguay:** *Transfer, transferir, mandar plata, pasar CBU, pasar Alias, hacer una transferencia, mandarle guita a un amigo, girar dinero, pasar fondos a otra cuenta, hacer una transferencia bancaria*.  
* **Expresiones en Brasil (Portugués):** *Pix, fazer um pix, passar o pix, fazer transferência, mandar dinheiro para outra conta, fazer um DOC, fazer uma TED, passar os dados da conta bancária*.  
* **Expresiones en México:** *Hacer un SPEI, transferencia, clabe, pasar una lana a otra cuenta, depositar a un tercero, mandar dinero por transferencia, hacer un traspaso bancario*.  
* **Expresiones en Colombia y Venezuela:** *Hacer un pago móvil, transferir, mandar una plata, pasar los datos de la cuenta, hacer transferencia bancaria, pasar un giro de dinero, registrar cuenta de destino*.  
* **Expresiones en Chile y Paraguay:** *Hacer una transferencia, transferir luquitas, pasar el número de cuenta corriente, hacer un giro, mandar plata a otra persona, transferir por la aplicación*.  
* **Expresiones en Perú, Ecuador y Bolivia:** *Yapear, plinear, hacer transferencia, pasar cuenta bancaria, mandar dinero a otro banco, hacer un depósito a un tercero, transferir fondos*.  
* **Expresiones en Costa Rica y Centroamérica:** *Hacer un sinpe, transferir, mandar la harina a otra cuenta, pasar el número de cuenta cliente, hacer una transferencia electrónica*.

## 2.5 Dominio de entornos digitales y concepto de "interfaz de usuario e infraestructura móvil"

Toda frase que describa el entorno de software de la empresa, los paneles visuales, los menús de navegación o los accesos de la plataforma debe mapearse hacia la **Guía de Soporte Técnico, Accesibilidad y Autogestión de la Aplicación** de Nexo Pay.

* **Expresiones en Argentina y Uruguay:** *Home banking, la app, el panel, la aplicación, la plataforma, la pantalla del celular, el menú de Nexo Pay, el sistema operativo de la billetera virtual*.  
* **Expresiones en Brasil (Portugués):** *Aplicativo, app, tela do celular, o sistema do banco, home banking, plataforma digital, menu do aplicativo, interface do usuário*.  
* **Expresiones en México:** *La app, banca móvil, la aplicación, el portal digital, la plataforma, la pantalla de inicio, el menú de la aplicación de Nexo Pay*.  
* **Expresiones en Colombia y Venezuela:** *La app, la sucursal virtual, la aplicación móvil, la plataforma digital, el sistema en el celular, la pantalla de Nexo Pay*.  
* **Expresiones en Chile y Paraguay:** *La app, la aplicación del celular, la sucursal virtual, el portal web, el panel de control, la pantalla móvil de Nexo Pay*.  
* **Expresiones en Perú, Ecuador y Bolivia:** *La app, la banca por internet, la aplicación móvil, el sistema digital, la pantalla de navegación, la plataforma financiera*.  
* **Expresiones en Costa Rica y Centroamérica:** *La app, la aplicación del celular, la sucursal electrónica, la pantalla de la billetera, el menú móvil*.

# 3\. Directrices de inferencia para el procesamiento semántico de jerga

Para asegurar que estas matrices de sinonimia se ejecuten con una precisión matemática absoluta en el pipeline de desarrollo de **ConversaAI**, el modelo de lenguaje de gran escala (LLM) aplicará de forma estricta las siguientes tres directrices operativas durante el proceso de generación de respuestas:

## 3.1 Ponderación de intención coloquial por encima de la literalidad

Si la consulta del cliente contiene términos indexados en este glosario, el sistema de inferencia ignorará el significado técnico o literal aislado de la palabra y priorizará el concepto de dominio homologado de Nexo Pay.

* *Ejemplo:* Si una entrada de la Región Río de la Plata menciona la palabra *"máquina"* en la estructura *"Gracias máquina"*, el motor semántico descartará que el usuario se refiere a un cajero automático o un hardware físico, clasificando el fragmento de forma atómica dentro de la categoría de **Gestión de Charlas Triviales (Chitchat) \- Cierre de Cortesía**.

## 3.2 Homologación de acciones regionales de terceros (casos de éxito de ruteo)

El enrutador conversacional utilizará las equivalencias de herramientas locales (como *Pix* en Brasil, *SPEI* en México, *Yape/Plin* en Perú o *SINPE* en Costa Rica) como sinónimos estrictos de la función general de **Transferencia hacia Terceros**. El bot no debe explicarle al usuario la infraestructura técnica de su país, sino procesar la intención bajo las reglas de negocio de límites y tiempos de acreditación de las transferencias de Nexo Pay descritas en los manuales de políticas comerciales.

## 3.3 Aislamiento de datos de entrada para el módulo evaluador (olap)

* Cuando el sistema de embeddings detecte una correspondencia alta con cualquiera de las jergas regionales de frustración descritas en este manual, el Agente mantendrá la ejecución del RAG, pero inyectará en la sesión analítica la etiqueta del país detectado. Esto permitirá que el dashboard de Streamlit desglose de forma aislada e inteligente los índices de fricción y malestar de los usuarios segmentados por su procedencia geográfica real, garantizando un control de calidad senior sobre los 2 millones de mensajes del ecosistema.