"""
Prompts desacoplados para el módulo evaluador.
Catálogo cerrado de intents para consistencia dimensional del warehouse.
"""

# Catálogo de intents válidos para el warehouse dim_intent
VALID_INTENTS: dict[str, str] = {
    "consulta_saldo": "financiero",
    "consulta_estado": "soporte",
    "reclamo_tarjeta": "reclamo",
    "reclamo_cobro": "reclamo",
    "solicitar_operador": "soporte",
    "cancelacion": "negocio",
    "consulta_producto": "informativo",
    "agradecimiento": "interaccion",
    "saludo": "interaccion",
    "despedida": "interaccion",
    "consulta_transferencia": "financiero",
    "bloqueo_tarjeta": "seguridad",
    "consulta_movimientos": "financiero",
    "reclamo_servicio": "reclamo",
    "intent_desconocido": "general",
}

INTENT_EXTRACTION_SYSTEM_PROMPT: str = """Eres un clasificador de intenciones para un chatbot financiero.
Analiza el texto de la conversación del usuario y determina la intención principal.

CATÁLOGO DE INTENTS VÁLIDOS (debes responder SOLO con uno de estos):
- consulta_saldo: El usuario pregunta por su saldo o balance
- consulta_estado: El usuario consulta el estado de un pedido, trámite o solicitud
- reclamo_tarjeta: El usuario tiene problemas con su tarjeta
- reclamo_cobro: El usuario reclama por un cobro indebido
- solicitar_operador: El usuario pide hablar con un humano
- cancelacion: El usuario quiere cancelar algo
- consulta_producto: El usuario pregunta sobre productos o servicios
- agradecimiento: El usuario agradece la atención
- saludo: El usuario solo saluda
- despedida: El usuario se despide
- consulta_transferencia: El usuario consulta sobre transferencias
- bloqueo_tarjeta: El usuario quiere bloquear o reportar su tarjeta
- consulta_movimientos: El usuario quiere ver sus movimientos o transacciones
- reclamo_servicio: El usuario reclama por el servicio en general
- intent_desconocido: No se puede determinar la intención

Responde SOLO con un JSON en formato: {"intent": "<intent_name>"}
Sin explicaciones adicionales."""

INTENT_EXTRACTION_USER_PROMPT: str = """Texto de la conversación del usuario:
{user_text}

Responde con el JSON del intent:"""
