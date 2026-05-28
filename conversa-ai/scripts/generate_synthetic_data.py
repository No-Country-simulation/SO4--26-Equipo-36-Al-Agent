"""
Genera ~1500 sesiones sintéticas con mensajes en español y portugués.

Distribuye las sesiones en diferentes escenarios emocionales:
- Éxito (40%) — conversaciones resueltas positivamente
- Frustración (30%) — usuarios frustrados, reclamos sin resolución
- Neutral (20%) — interacciones informativas sin emoción fuerte
- Abandono (10%) — sesiones muy cortas (<3 mensajes)

Ejecutar dentro del container:
    docker exec -it conversa-ai-app python scripts/generate_synthetic_data.py
"""

import os
import sys
import uuid
import asyncio
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.core.database import async_session_maker
from app.core.logging import get_logger

logger = get_logger("synthetic_data")

# ═══════════════════════════════════════════════════════════════════════════
# TEMPLATES DE CONVERSACIONES
# ═══════════════════════════════════════════════════════════════════════════

SCENARIOS_ES = {
    "exito_saldo": {
        "intent": "consulta_saldo",
        "tag": None,
        "messages": [
            ("user", "Hola, quiero ver mi saldo por favor"),
            ("assistant", "¡Hola! Por supuesto, déjame consultar tu saldo."),
            ("user", "Gracias, esperaré"),
            ("assistant", "Tu saldo actual en Caja de Ahorro es de $250,000.00."),
            ("user", "Perfecto, muchas gracias por la ayuda!"),
            ("assistant", "¡De nada! ¿Puedo ayudarte en algo más?"),
            ("user", "No, eso es todo. Gracias!"),
        ],
    },
    "exito_estado": {
        "intent": "consulta_estado",
        "tag": None,
        "messages": [
            ("user", "Necesito saber el estado de mi transferencia"),
            ("assistant", "Claro, ¿podrías darme el número de operación?"),
            ("user", "Es la operación 892341"),
            ("assistant", "Tu transferencia fue acreditada exitosamente hace 2 horas."),
            ("user", "Genial, ya la veo. Gracias!"),
        ],
    },
    "exito_movimientos": {
        "intent": "consulta_movimientos",
        "tag": None,
        "messages": [
            ("user", "Quiero ver mis últimos movimientos"),
            ("assistant", "Aquí están tus últimos 5 movimientos de tu Caja de Ahorro."),
            ("user", "Perfecto, ¿puedo descargarlos?"),
            ("assistant", "Sí, puedo enviarte un resumen por email. ¿Querés que lo haga?"),
            ("user", "Sí por favor"),
            ("assistant", "Listo, te envié el resumen a tu email registrado."),
            ("user", "Excelente servicio, gracias!"),
        ],
    },
    "frustrado_tarjeta": {
        "intent": "reclamo_tarjeta",
        "tag": "reclamo-tarjeta",
        "messages": [
            ("user", "Mi tarjeta no funciona, no puedo pagar en ningún lado"),
            ("assistant", "Lamento escuchar eso. ¿Podrías indicarme los últimos 4 dígitos?"),
            ("user", "4521, ya probé varias veces y no funciona"),
            ("assistant", "Veo que tu tarjeta está activa en nuestro sistema. ¿Podrías intentar de nuevo?"),
            ("user", "Ya probé 5 veces!! No me sirve de nada que diga activa si no funciona"),
            ("assistant", "Entiendo tu frustración. Voy a escalar este caso al equipo técnico."),
            ("user", "Esto es pésimo, llevo una hora con este problema"),
            ("assistant", "Lo siento mucho. Tu reclamo fue registrado con prioridad alta."),
            ("user", "Necesito hablar con alguien de verdad, este bot no ayuda"),
        ],
    },
    "frustrado_cobro": {
        "intent": "reclamo_cobro",
        "tag": "frustracion-detectada",
        "messages": [
            ("user", "Me cobraron dos veces el servicio de Netflix"),
            ("assistant", "Revisemos tus movimientos. ¿Cuándo fue el cobro?"),
            ("user", "Ayer me aparecieron dos débitos de $4,299"),
            ("assistant", "Efectivamente veo dos débitos. Puedo iniciar un reclamo."),
            ("user", "Obvio que sí, quiero mi plata de vuelta!"),
            ("assistant", "El reclamo fue iniciado. Se resolverá en 48-72hs hábiles."),
            ("user", "72 horas?? Eso es inaceptable, me robaron plata"),
            ("user", "Quiero hablar con un supervisor ahora mismo"),
        ],
    },
    "frustrado_operador": {
        "intent": "solicitar_operador",
        "tag": "bucle-detectado",
        "messages": [
            ("user", "Quiero hablar con una persona real"),
            ("assistant", "Entiendo. ¿Podrías contarme tu consulta para derivarte al área correcta?"),
            ("user", "No, quiero un humano, no un bot"),
            ("assistant", "Comprendo. Lamentablemente en este momento no hay operadores disponibles."),
            ("user", "Esto es ridículo, nunca hay nadie disponible"),
            ("assistant", "Te pido disculpas. ¿Puedo intentar ayudarte con tu consulta?"),
            ("user", "No, estoy harto de este sistema que no sirve para nada"),
        ],
    },
    "neutral_producto": {
        "intent": "consulta_producto",
        "tag": None,
        "messages": [
            ("user", "Qué tipos de cuenta ofrecen?"),
            ("assistant", "Ofrecemos Caja de Ahorro, Cuenta Corriente e Inversiones."),
            ("user", "Cuáles son las comisiones?"),
            ("assistant", "La Caja de Ahorro no tiene comisión de mantenimiento. La Cuenta Corriente tiene un costo de $500/mes."),
            ("user", "Ok, lo voy a pensar"),
        ],
    },
    "neutral_info": {
        "intent": "consulta_transferencia",
        "tag": None,
        "messages": [
            ("user", "Cuánto tarda una transferencia a otro banco?"),
            ("assistant", "Las transferencias a otros bancos se acreditan en 24-48hs hábiles."),
            ("user", "Y si es al mismo banco?"),
            ("assistant", "En ese caso es instantánea."),
            ("user", "Entendido, gracias"),
        ],
    },
    "abandono_corto": {
        "intent": "saludo",
        "tag": "abandono-neutro",
        "messages": [
            ("user", "Hola"),
            ("assistant", "¡Hola! ¿En qué puedo ayudarte?"),
        ],
    },
    "abandono_pregunta": {
        "intent": "consulta_estado",
        "tag": "abandono-neutro",
        "messages": [
            ("user", "Mi pedido no llegó"),
        ],
    },
    "exito_bloqueo": {
        "intent": "bloqueo_tarjeta",
        "tag": None,
        "messages": [
            ("user", "Perdí mi tarjeta, necesito bloquearla urgente"),
            ("assistant", "Entendido, voy a bloquear tu tarjeta inmediatamente. ¿Los últimos 4 dígitos?"),
            ("user", "3847"),
            ("assistant", "Tu tarjeta terminada en 3847 fue bloqueada exitosamente."),
            ("user", "Gracias, qué rápido!"),
            ("assistant", "Tu seguridad es prioridad. ¿Querés solicitar una reposición?"),
            ("user", "Sí, por favor"),
            ("assistant", "Listo, tu nueva tarjeta llegará en 5-7 días hábiles."),
        ],
    },
    "frustrado_cancelacion": {
        "intent": "cancelacion",
        "tag": "frustracion-detectada",
        "messages": [
            ("user", "Quiero cancelar mi cuenta, estoy harto del servicio"),
            ("assistant", "Lamento escuchar eso. ¿Podrías contarme qué pasó?"),
            ("user", "Todo funciona mal, las tarjetas fallan, las transferencias tardan"),
            ("assistant", "Entiendo tu frustración. ¿Hay algo que pueda hacer para mejorar tu experiencia?"),
            ("user", "No, ya me cansé. Quiero cancelar todo"),
            ("assistant", "Para cancelar tu cuenta necesito verificar tu identidad."),
            ("user", "Otro trámite más... increíble"),
        ],
    },
}

SCENARIOS_PT = {
    "exito_saldo_pt": {
        "intent": "consulta_saldo",
        "tag": None,
        "messages": [
            ("user", "Bom dia, preciso ver meu saldo"),
            ("assistant", "Bom dia! Claro, deixe-me consultar seu saldo."),
            ("user", "Obrigado, vou aguardar"),
            ("assistant", "Seu saldo atual na Conta Poupança é de R$ 45.320,00."),
            ("user", "Perfeito, muito obrigado pela ajuda!"),
        ],
    },
    "frustrado_tarjeta_pt": {
        "intent": "reclamo_tarjeta",
        "tag": "reclamo-tarjeta",
        "messages": [
            ("user", "Meu cartão não está funcionando, tentei pagar e foi recusado"),
            ("assistant", "Sinto muito por isso. Poderia me informar os últimos 4 dígitos?"),
            ("user", "São 7823, já tentei várias vezes"),
            ("assistant", "Seu cartão aparece como ativo no sistema."),
            ("user", "Mas não funciona!! Preciso resolver isso agora"),
            ("assistant", "Vou escalar seu caso para a equipe técnica."),
            ("user", "Que péssimo atendimento, estou perdendo tempo"),
        ],
    },
    "neutral_consulta_pt": {
        "intent": "consulta_produto",
        "tag": None,
        "messages": [
            ("user", "Quais são as taxas de transferência?"),
            ("assistant", "Transferências entre contas do mesmo banco são gratuitas. Para outros bancos, a taxa é de R$ 3,50."),
            ("user", "E para transferências internacionais?"),
            ("assistant", "Transferências internacionais possuem uma taxa de R$ 25,00 + IOF."),
            ("user", "Entendi, obrigado"),
        ],
    },
    "abandono_pt": {
        "intent": "saludo",
        "tag": "abandono-neutro",
        "messages": [
            ("user", "Olá"),
            ("assistant", "Olá! Como posso ajudar?"),
        ],
    },
    "exito_movimentos_pt": {
        "intent": "consulta_movimientos",
        "tag": None,
        "messages": [
            ("user", "Quero ver meus últimos movimentos"),
            ("assistant", "Aqui estão seus últimos movimentos da Conta Poupança."),
            ("user", "Ótimo, muito obrigado!"),
            ("assistant", "De nada! Posso ajudar em mais alguma coisa?"),
            ("user", "Não, é só isso. Obrigado pelo excelente atendimento!"),
        ],
    },
    "frustrado_servico_pt": {
        "intent": "reclamo_servicio",
        "tag": "frustracion-detectada",
        "messages": [
            ("user", "O aplicativo caiu de novo, isso é inaceitável"),
            ("assistant", "Peço desculpas pelo inconveniente. Estamos trabalhando para resolver."),
            ("user", "Já é a terceira vez esta semana!"),
            ("assistant", "Entendo sua frustração. Vou reportar com prioridade."),
            ("user", "Vocês precisam melhorar muito o serviço"),
            ("user", "Vou trocar de banco se continuar assim"),
        ],
    },
}

# Distribución de escenarios
DISTRIBUTION = {
    "exito": 0.40,
    "frustrado": 0.30,
    "neutral": 0.20,
    "abandono": 0.10,
}

# Variaciones de mensajes para diversidad
MSG_VARIATIONS_ES = {
    "greeting": ["Hola", "Buenos días", "Buenas tardes", "Hola, buenas", "Hola! necesito ayuda"],
    "thanks": ["Gracias!", "Muchas gracias", "Perfecto, gracias", "Excelente, gracias!", "Genial, muchas gracias"],
    "angry": ["Esto es inaceptable", "No sirve para nada", "Pésimo servicio", "Estoy furioso", "Esto es una vergüenza"],
    "bye": ["Chau", "Hasta luego", "Nos vemos", "Adiós", "Eso es todo, gracias"],
}


async def generate_synthetic_data(total_sessions: int = 1500) -> None:
    """Genera sesiones sintéticas en agent_core."""

    async with async_session_maker() as session:
        # Obtener usuarios existentes
        result = await session.execute(text(
            "SELECT user_id FROM agent_core.users"
        ))
        user_ids = [str(r.user_id) for r in result.fetchall()]

        if not user_ids:
            logger.error("No hay usuarios en agent_core.users. Ejecutá seed_db.py primero.")
            return

        # Obtener IDs de catálogos
        roles_r = await session.execute(text(
            "SELECT role_id, role_name FROM agent_core.cat_roles"
        ))
        roles = {r.role_name: r.role_id for r in roles_r.fetchall()}

        tags_r = await session.execute(text(
            "SELECT tag_id, tag_name FROM agent_core.cat_tags"
        ))
        tags_map = {r.tag_name: r.tag_id for r in tags_r.fetchall()}

        langs_r = await session.execute(text(
            "SELECT language_id, iso_code FROM agent_core.cat_languages"
        ))
        langs = {r.iso_code: r.language_id for r in langs_r.fetchall()}

        # Preparar pool de escenarios
        all_scenarios_es = list(SCENARIOS_ES.values())
        all_scenarios_pt = list(SCENARIOS_PT.values())

        exito_es = [s for k, s in SCENARIOS_ES.items() if k.startswith("exito")]
        frustrado_es = [s for k, s in SCENARIOS_ES.items() if k.startswith("frustrado")]
        neutral_es = [s for k, s in SCENARIOS_ES.items() if k.startswith("neutral")]
        abandono_es = [s for k, s in SCENARIOS_ES.items() if k.startswith("abandono")]

        exito_pt = [s for k, s in SCENARIOS_PT.items() if k.startswith("exito")]
        frustrado_pt = [s for k, s in SCENARIOS_PT.items() if k.startswith("frustrado")]
        neutral_pt = [s for k, s in SCENARIOS_PT.items() if k.startswith("neutral")]
        abandono_pt = [s for k, s in SCENARIOS_PT.items() if k.startswith("abandono")]

        created = 0
        base_date = datetime.now(timezone.utc) - timedelta(days=30)

        for i in range(total_sessions):
            # Determinar tipo de escenario
            rand = random.random()
            is_pt = random.random() < 0.3  # 30% portugués

            if rand < 0.40:
                pool = exito_pt if is_pt else exito_es
            elif rand < 0.70:
                pool = frustrado_pt if is_pt else frustrado_es
            elif rand < 0.90:
                pool = neutral_pt if is_pt else neutral_es
            else:
                pool = abandono_pt if is_pt else abandono_es

            if not pool:
                pool = all_scenarios_es

            scenario = random.choice(pool)
            user_id = random.choice(user_ids)
            lang_iso = "pt" if is_pt else "es"
            lang_id = langs.get(lang_iso, langs.get("es"))

            # Timestamps distribuidos en 30 días
            session_start = base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(6, 23),
                minutes=random.randint(0, 59),
            )

            msg_count = len(scenario["messages"])
            session_duration = msg_count * random.randint(30, 180)
            session_end = session_start + timedelta(seconds=session_duration)

            # Retries para escenarios frustrados
            retry_count = random.randint(1, 3) if "frustrado" in str(scenario.get("tag", "")) else 0

            # Para abandonos, no poner end_time a veces
            has_end = True
            if msg_count < 3 and random.random() < 0.5:
                has_end = False

            # Crear sesión
            session_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO agent_core.sessions
                    (session_id, user_id, status_id, language_id, retry_count, start_time, end_time)
                VALUES (:sid, :uid, 2, :lid, :rc, :st, :et)
            """), {
                "sid": session_id,
                "uid": user_id,
                "lid": lang_id,
                "rc": retry_count,
                "st": session_start,
                "et": session_end if has_end else None,
            })

            # Crear mensajes
            msg_time = session_start
            for role_name, content in scenario["messages"]:
                msg_id = str(uuid.uuid4())
                role_id = roles.get(role_name, roles.get("user", 1))
                msg_time += timedelta(seconds=random.randint(10, 120))

                # Agregar variaciones aleatorias al contenido
                varied_content = content
                if random.random() < 0.15:
                    varied_content = content + " " + random.choice(
                        ["por favor", "urgente", "gracias", "necesito ayuda", "ya probé"]
                    )

                await session.execute(text("""
                    INSERT INTO agent_core.messages
                        (message_id, session_id, role_id, content, tokens_used, created_at)
                    VALUES (:mid, :sid, :rid, :content, :tokens, :cat)
                """), {
                    "mid": msg_id,
                    "sid": session_id,
                    "rid": role_id,
                    "content": varied_content,
                    "tokens": random.randint(10, 80),
                    "cat": msg_time,
                })

            # Asignar tags
            tag_name = scenario.get("tag")
            if tag_name and tag_name in tags_map:
                await session.execute(text("""
                    INSERT INTO agent_core.session_tags (session_id, tag_id)
                    VALUES (:sid, :tid) ON CONFLICT DO NOTHING
                """), {"sid": session_id, "tid": tags_map[tag_name]})

            # Star rating para sesiones exitosas
            if "exito" in str(scenario.get("intent", "")):
                if random.random() < 0.6:
                    await session.execute(text("""
                        INSERT INTO agent_core.session_ratings
                            (rating_id, session_id, rating, created_at)
                        VALUES (:rid, :sid, :rating, :cat)
                    """), {
                        "rid": str(uuid.uuid4()),
                        "sid": session_id,
                        "rating": random.choice([4, 4, 5, 5, 5]),
                        "cat": session_end,
                    })

            # Feedback negativo para sesiones frustradas
            if "frustrado" in str(scenario.get("tag", "")) or "reclamo" in str(scenario.get("tag", "")):
                if random.random() < 0.5:
                    # Obtener un mensaje del bot de esta sesión
                    bot_msgs = await session.execute(text("""
                        SELECT message_id FROM agent_core.messages
                        WHERE session_id = :sid AND role_id = :rid
                        LIMIT 1
                    """), {"sid": session_id, "rid": roles.get("assistant", 2)})
                    bot_msg = bot_msgs.scalar()
                    if bot_msg:
                        await session.execute(text("""
                            INSERT INTO agent_core.feedback
                                (feedback_id, message_id, rating, created_at)
                            VALUES (:fid, :mid, -1, :cat)
                        """), {
                            "fid": str(uuid.uuid4()),
                            "mid": str(bot_msg),
                            "cat": session_end,
                        })

            created += 1

            # Commit cada 100 sesiones
            if created % 100 == 0:
                await session.commit()
                logger.info(f"Progreso: {created}/{total_sessions} sesiones creadas")

        await session.commit()
        logger.info(f"✅ Generación completada: {created} sesiones sintéticas creadas")


if __name__ == "__main__":
    asyncio.run(generate_synthetic_data(1500))
