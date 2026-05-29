"""
Genera ~120 sesiones sintéticas con datos coherentes en OLTP (agent_core) Y OLAP (analytics_warehouse).

Distribución:
- Éxito (40%) — POS sentiment, SUCCESS resolution
- Frustración (25%) — NEG sentiment, FRUSTRATION resolution  
- Neutral (20%) — NEU sentiment, NEUTRAL resolution
- Abandono (15%) — NEU sentiment, NEUTRAL resolution, is_abandoned=True

Las sesiones se marcan status=4 (COMPLETED) para que el ETL real las ignore.
El pipeline ETL solo procesará sesiones reales del chatbot (status=2 FINISHED).

Ejecutar: docker exec conversa-ai-app python scripts/generate_synthetic_data.py
"""
import os, sys, uuid, asyncio, random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy import text
from app.core.database import async_session_maker
from app.core.logging import get_logger

logger = get_logger("synthetic_data")

# ═══════════════════════════════════════════════════════════════
# ESCENARIOS DE CONVERSACIÓN
# ═══════════════════════════════════════════════════════════════

SCENARIOS_ES = {
    "exito_saldo": {
        "intent": "consulta_saldo", "category": "consultas", "tag": None, "sentiment": "POS",
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
        "intent": "consulta_estado", "category": "consultas", "tag": None, "sentiment": "POS",
        "messages": [
            ("user", "Necesito saber el estado de mi transferencia"),
            ("assistant", "Claro, ¿podrías darme el número de operación?"),
            ("user", "Es la operación 892341"),
            ("assistant", "Tu transferencia fue acreditada exitosamente hace 2 horas."),
            ("user", "Genial, ya la veo. Gracias!"),
        ],
    },
    "exito_movimientos": {
        "intent": "consulta_movimientos", "category": "consultas", "tag": None, "sentiment": "POS",
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
    "exito_bloqueo": {
        "intent": "bloqueo_tarjeta", "category": "operaciones", "tag": None, "sentiment": "POS",
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
    "exito_transferencia": {
        "intent": "consulta_transferencia", "category": "consultas", "tag": None, "sentiment": "POS",
        "messages": [
            ("user", "Necesito hacer una transferencia a otra cuenta"),
            ("assistant", "Claro, ¿a qué CBU o alias querés transferir?"),
            ("user", "Al alias juan.perez.mp"),
            ("assistant", "Perfecto. ¿Qué monto querés transferir?"),
            ("user", "$15,000"),
            ("assistant", "Transferencia de $15,000 realizada exitosamente."),
            ("user", "Genial, muchas gracias!"),
        ],
    },
    "frustrado_tarjeta": {
        "intent": "reclamo_tarjeta", "category": "reclamos", "tag": "reclamo-tarjeta", "sentiment": "NEG",
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
        "intent": "reclamo_cobro", "category": "reclamos", "tag": "frustracion-detectada", "sentiment": "NEG",
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
        "intent": "solicitar_operador", "category": "soporte", "tag": "bucle-detectado", "sentiment": "NEG",
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
    "frustrado_cancelacion": {
        "intent": "cancelacion", "category": "operaciones", "tag": "frustracion-detectada", "sentiment": "NEG",
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
    "frustrado_app": {
        "intent": "reclamo_servicio", "category": "reclamos", "tag": "frustracion-detectada", "sentiment": "NEG",
        "messages": [
            ("user", "La app se cayó otra vez, no puedo entrar a mi cuenta"),
            ("assistant", "Disculpá las molestias. Estamos al tanto del problema."),
            ("user", "Es la tercera vez esta semana!"),
            ("assistant", "Entiendo tu frustración. El equipo técnico está trabajando en una solución."),
            ("user", "Voy a cambiar de banco si sigue así"),
        ],
    },
    "neutral_producto": {
        "intent": "consulta_producto", "category": "consultas", "tag": None, "sentiment": "NEU",
        "messages": [
            ("user", "Qué tipos de cuenta ofrecen?"),
            ("assistant", "Ofrecemos Caja de Ahorro, Cuenta Corriente e Inversiones."),
            ("user", "Cuáles son las comisiones?"),
            ("assistant", "La Caja de Ahorro no tiene comisión. La Cuenta Corriente tiene un costo de $500/mes."),
            ("user", "Ok, lo voy a pensar"),
        ],
    },
    "neutral_info": {
        "intent": "consulta_transferencia", "category": "consultas", "tag": None, "sentiment": "NEU",
        "messages": [
            ("user", "Cuánto tarda una transferencia a otro banco?"),
            ("assistant", "Las transferencias a otros bancos se acreditan en 24-48hs hábiles."),
            ("user", "Y si es al mismo banco?"),
            ("assistant", "En ese caso es instantánea."),
            ("user", "Entendido, gracias"),
        ],
    },
    "neutral_horarios": {
        "intent": "consulta_producto", "category": "consultas", "tag": None, "sentiment": "NEU",
        "messages": [
            ("user", "Cuáles son los horarios de atención?"),
            ("assistant", "Nuestro chat está disponible 24/7. Las sucursales atienden de 10 a 15hs."),
            ("user", "Y los feriados?"),
            ("assistant", "Los feriados las sucursales permanecen cerradas, pero el chat sigue activo."),
            ("user", "Perfecto, gracias por la info"),
        ],
    },
    "abandono_corto": {
        "intent": "saludo", "category": "general", "tag": "abandono-neutro", "sentiment": "NEU",
        "messages": [("user", "Hola"), ("assistant", "¡Hola! ¿En qué puedo ayudarte?")],
    },
    "abandono_pregunta": {
        "intent": "consulta_estado", "category": "consultas", "tag": "abandono-neutro", "sentiment": "NEU",
        "messages": [("user", "Mi pedido no llegó")],
    },
}

SCENARIOS_PT = {
    "exito_saldo_pt": {
        "intent": "consulta_saldo", "category": "consultas", "tag": None, "sentiment": "POS",
        "messages": [
            ("user", "Bom dia, preciso ver meu saldo"),
            ("assistant", "Bom dia! Claro, deixe-me consultar seu saldo."),
            ("user", "Obrigado, vou aguardar"),
            ("assistant", "Seu saldo atual na Conta Poupança é de R$ 45.320,00."),
            ("user", "Perfeito, muito obrigado pela ajuda!"),
        ],
    },
    "exito_movimentos_pt": {
        "intent": "consulta_movimientos", "category": "consultas", "tag": None, "sentiment": "POS",
        "messages": [
            ("user", "Quero ver meus últimos movimentos"),
            ("assistant", "Aqui estão seus últimos movimentos da Conta Poupança."),
            ("user", "Ótimo, muito obrigado!"),
            ("assistant", "De nada! Posso ajudar em mais alguma coisa?"),
            ("user", "Não, é só isso. Obrigado pelo excelente atendimento!"),
        ],
    },
    "frustrado_tarjeta_pt": {
        "intent": "reclamo_tarjeta", "category": "reclamos", "tag": "reclamo-tarjeta", "sentiment": "NEG",
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
    "frustrado_servico_pt": {
        "intent": "reclamo_servicio", "category": "reclamos", "tag": "frustracion-detectada", "sentiment": "NEG",
        "messages": [
            ("user", "O aplicativo caiu de novo, isso é inaceitável"),
            ("assistant", "Peço desculpas pelo inconveniente. Estamos trabalhando para resolver."),
            ("user", "Já é a terceira vez esta semana!"),
            ("assistant", "Entendo sua frustração. Vou reportar com prioridade."),
            ("user", "Vocês precisam melhorar muito o serviço"),
            ("user", "Vou trocar de banco se continuar assim"),
        ],
    },
    "neutral_consulta_pt": {
        "intent": "consulta_produto", "category": "consultas", "tag": None, "sentiment": "NEU",
        "messages": [
            ("user", "Quais são as taxas de transferência?"),
            ("assistant", "Transferências entre contas do mesmo banco são gratuitas. Para outros bancos, R$ 3,50."),
            ("user", "E para transferências internacionais?"),
            ("assistant", "Transferências internacionais possuem uma taxa de R$ 25,00 + IOF."),
            ("user", "Entendi, obrigado"),
        ],
    },
    "abandono_pt": {
        "intent": "saludo", "category": "general", "tag": "abandono-neutro", "sentiment": "NEU",
        "messages": [("user", "Olá"), ("assistant", "Olá! Como posso ajudar?")],
    },
}

# Pools por categoría
def _build_pools(scenarios: dict) -> dict:
    pools = {"exito": [], "frustrado": [], "neutral": [], "abandono": []}
    for k, v in scenarios.items():
        for cat in pools:
            if k.startswith(cat):
                pools[cat].append(v)
                break
    return pools

SENTIMENT_GROUP = {"POS": "Positive", "NEG": "Negative", "NEU": "Neutral"}
RESOLUTION_MAP = {"exito": "SUCCESS", "frustrado": "FRUSTRATION", "neutral": "NEUTRAL", "abandono": "NEUTRAL"}

# Pesos horarios para simular picos en horario laboral
HOUR_WEIGHTS = [1]*6 + [3,4,5,6,8,10,10,9,8,7,6,5,4,3,2,2,1,1]  # 00h-23h


async def generate_synthetic_data(total_sessions: int = 120) -> None:
    """Genera sesiones sintéticas en agent_core Y analytics_warehouse."""
    async with async_session_maker() as session:
        # Obtener usuarios existentes y si son anónimos o no
        result = await session.execute(text("SELECT user_id, email FROM agent_core.users"))
        users_data = [{"user_id": str(r.user_id), "is_authenticated": bool(r.email)} for r in result.fetchall()]
        if not users_data:
            logger.error("No hay usuarios en agent_core.users. Ejecutá seed_db.py primero.")
            return

        # Catálogos OLTP
        roles_r = await session.execute(text("SELECT role_id, role_name FROM agent_core.cat_roles"))
        roles = {r.role_name: r.role_id for r in roles_r.fetchall()}

        tags_r = await session.execute(text("SELECT tag_id, tag_name FROM agent_core.cat_tags"))
        tags_map = {r.tag_name: r.tag_id for r in tags_r.fetchall()}

        langs_r = await session.execute(text("SELECT language_id, iso_code FROM agent_core.cat_languages"))
        langs = {r.iso_code: r.language_id for r in langs_r.fetchall()}

        # Catálogos OLAP
        res_r = await session.execute(text(
            "SELECT resolution_id, resolution_name FROM analytics_warehouse.cat_resolution_types"
        ))
        resolution_ids = {r.resolution_name: r.resolution_id for r in res_r.fetchall()}

        lang_olap_r = await session.execute(text(
            "SELECT language_id, iso_code FROM analytics_warehouse.dim_language"
        ))
        lang_olap = {r.iso_code: r.language_id for r in lang_olap_r.fetchall()}

        # Pools de escenarios
        pools_es = _build_pools(SCENARIOS_ES)
        pools_pt = _build_pools(SCENARIOS_PT)

        created = 0
        base_date = datetime.now(timezone.utc) - timedelta(days=30)

        for i in range(total_sessions):
            # Tipo de escenario
            rand = random.random()
            if rand < 0.40:
                scenario_type = "exito"
            elif rand < 0.65:
                scenario_type = "frustrado"
            elif rand < 0.85:
                scenario_type = "neutral"
            else:
                scenario_type = "abandono"

            is_pt = random.random() < 0.30
            pool = (pools_pt if is_pt else pools_es).get(scenario_type, [])
            if not pool:
                pool = pools_es.get(scenario_type, list(SCENARIOS_ES.values()))
            scenario = random.choice(pool)

            selected_user = random.choice(users_data)
            user_id = selected_user["user_id"]
            is_authenticated = selected_user["is_authenticated"]
            
            lang_iso = "pt" if is_pt else "es"
            lang_id = langs.get(lang_iso, langs.get("es"))
            msg_count = len(scenario["messages"])

            # Timestamps distribuidos en 30 días con pesos horarios
            day_offset = random.randint(0, 30)
            hour = random.choices(range(24), weights=HOUR_WEIGHTS, k=1)[0]
            session_start = base_date + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59))
            session_duration = msg_count * random.randint(30, 180)
            session_end = session_start + timedelta(seconds=session_duration)

            # Abandonos: sin end_time a veces
            is_abandoned = scenario_type == "abandono"
            if is_abandoned and random.random() < 0.5:
                session_end = None

            retry_count = random.randint(1, 3) if scenario_type == "frustrado" else 0

            # ── OLTP: Crear sesión (status=4 COMPLETED) ───────────────
            session_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO agent_core.sessions
                    (session_id, user_id, status_id, language_id, retry_count, start_time, end_time)
                VALUES (:sid, :uid, 4, :lid, :rc, :st, :et)
            """), {
                "sid": session_id, "uid": user_id, "lid": lang_id,
                "rc": retry_count, "st": session_start, "et": session_end,
            })

            # ── OLTP: Mensajes ────────────────────────────────────────
            msg_time = session_start
            for role_name, content in scenario["messages"]:
                msg_id = str(uuid.uuid4())
                role_id = roles.get(role_name, roles.get("user", 1))
                msg_time += timedelta(seconds=random.randint(10, 120))
                varied = content
                if random.random() < 0.15:
                    varied += " " + random.choice(["por favor", "urgente", "gracias", "necesito ayuda", "ya probé"])
                await session.execute(text("""
                    INSERT INTO agent_core.messages
                        (message_id, session_id, role_id, content, tokens_used, created_at)
                    VALUES (:mid, :sid, :rid, :content, :tokens, :cat)
                """), {
                    "mid": msg_id, "sid": session_id, "rid": role_id,
                    "content": varied, "tokens": random.randint(10, 80), "cat": msg_time,
                })

            # ── OLTP: Tags ────────────────────────────────────────────
            tag_name = scenario.get("tag")
            if tag_name and tag_name in tags_map:
                await session.execute(text("""
                    INSERT INTO agent_core.session_tags (session_id, tag_id)
                    VALUES (:sid, :tid) ON CONFLICT DO NOTHING
                """), {"sid": session_id, "tid": tags_map[tag_name]})

            # ── OLTP: Star rating (éxitos) ────────────────────────────
            pos_fb, neg_fb = 0, 0
            star_rating = None
            if scenario_type == "exito" and random.random() < 0.6:
                star_rating = random.choice([4, 4, 5, 5, 5])
                await session.execute(text("""
                    INSERT INTO agent_core.session_ratings (rating_id, session_id, rating, created_at)
                    VALUES (:rid, :sid, :rating, :cat)
                """), {
                    "rid": str(uuid.uuid4()), "sid": session_id,
                    "rating": star_rating, "cat": session_end or session_start,
                })
                pos_fb = random.randint(1, 3)

            # ── OLTP: Feedback negativo (frustrados) ──────────────────
            if scenario_type == "frustrado" and random.random() < 0.5:
                bot_msgs = await session.execute(text("""
                    SELECT message_id FROM agent_core.messages
                    WHERE session_id = :sid AND role_id = :rid LIMIT 1
                """), {"sid": session_id, "rid": roles.get("assistant", 2)})
                bot_msg = bot_msgs.scalar()
                if bot_msg:
                    await session.execute(text("""
                        INSERT INTO agent_core.feedback (feedback_id, message_id, rating, created_at)
                        VALUES (:fid, :mid, -1, :cat)
                    """), {
                        "fid": str(uuid.uuid4()), "mid": str(bot_msg),
                        "cat": session_end or session_start,
                    })
                    neg_fb = random.randint(1, 2)

            # ══════════════════════════════════════════════════════════
            # OLAP: Insertar directamente en analytics_warehouse
            # ══════════════════════════════════════════════════════════

            # dim_time
            days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dt = session_start
            dow = days_names[dt.weekday()]
            time_result = await session.execute(text("""
                INSERT INTO analytics_warehouse.dim_time
                    (full_date, year, month, day, hour, day_of_week, is_weekend)
                VALUES (:fd, :y, :m, :d, :h, :dow, :we)
                ON CONFLICT (full_date, hour) DO UPDATE SET full_date = EXCLUDED.full_date
                RETURNING time_id
            """), {
                "fd": dt.date(), "y": dt.year, "m": dt.month, "d": dt.day,
                "h": dt.hour, "dow": dow, "we": dt.weekday() >= 5,
            })
            time_id = time_result.scalar()

            # dim_intent
            intent_name = scenario.get("intent", "intent_desconocido")
            intent_cat = scenario.get("category", "general")
            intent_result = await session.execute(text("""
                INSERT INTO analytics_warehouse.dim_intent (intent_name, category)
                VALUES (:name, :cat)
                ON CONFLICT (intent_name) DO UPDATE SET category = EXCLUDED.category
                RETURNING intent_id
            """), {"name": intent_name, "cat": intent_cat})
            intent_id = intent_result.scalar()

            # dim_sentiment
            sent_label = scenario.get("sentiment", "NEU")
            sent_group = SENTIMENT_GROUP[sent_label]
            sent_result = await session.execute(text("""
                INSERT INTO analytics_warehouse.dim_sentiment (label, sentiment_group)
                VALUES (:label, :grp)
                ON CONFLICT (label) DO UPDATE SET sentiment_group = EXCLUDED.sentiment_group
                RETURNING sentiment_id
            """), {"label": sent_label, "grp": sent_group})
            sentiment_id = sent_result.scalar()

            # resolution
            resolution_name = RESOLUTION_MAP[scenario_type]
            resolution_id = resolution_ids.get(resolution_name)

            # Sentiment score coherente
            score_ranges = {"POS": (0.75, 0.95), "NEG": (0.65, 0.90), "NEU": (0.45, 0.65)}
            score_min, score_max = score_ranges[sent_label]
            sentiment_score = round(random.uniform(score_min, score_max), 2)

            # fact_sessions_evaluation
            fact_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO analytics_warehouse.fact_sessions_evaluation (
                    fact_id, session_id, dim_time_id, dim_language_id,
                    dim_intent_id, dim_sentiment_id, resolution_id,
                    session_duration_seconds, total_messages, sentiment_score,
                    positive_feedback_count, negative_feedback_count, is_abandoned, is_authenticated, is_read
                ) VALUES (
                    :fid, :sid, :tid, :lid, :iid, :seid, :rid,
                    :dur, :msgs, :score, :pos, :neg, :aband, :auth, TRUE
                )
            """), {
                "fid": fact_id, "sid": session_id, "tid": time_id,
                "lid": lang_olap.get(lang_iso), "iid": intent_id,
                "seid": sentiment_id, "rid": resolution_id,
                "dur": session_duration, "msgs": msg_count,
                "score": sentiment_score, "pos": pos_fb, "neg": neg_fb,
                "aband": is_abandoned, "auth": is_authenticated,
            })

            # fact_tag_assignments
            if tag_name and tag_name in tags_map:
                # Buscar tag_id en dim_tags del OLAP
                olap_tag = await session.execute(text("""
                    SELECT tag_id FROM analytics_warehouse.dim_tags WHERE tag_name = :name
                """), {"name": tag_name})
                olap_tag_id = olap_tag.scalar()
                if olap_tag_id:
                    await session.execute(text("""
                        INSERT INTO analytics_warehouse.fact_tag_assignments (fact_id, tag_id)
                        VALUES (:fid, :tid) ON CONFLICT DO NOTHING
                    """), {"fid": fact_id, "tid": olap_tag_id})

            created += 1
            if created % 50 == 0:
                await session.commit()
                logger.info(f"Progreso: {created}/{total_sessions} sesiones creadas")

        await session.commit()
        logger.info(f"✅ Generación completada: {created} sesiones (OLTP + OLAP)")


if __name__ == "__main__":
    asyncio.run(generate_synthetic_data(120))
