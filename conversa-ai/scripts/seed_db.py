"""
Script de seed grande para poblar la base de datos fintech_mock y agent_core.
Crea usuarios ficticios + el usuario real (Facundo) con cuentas, tarjetas y transacciones.

Ejecutar dentro del container:
  docker exec -it conversa-ai-app python scripts/seed_db.py
"""

import os
import sys
import uuid
import asyncio
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.core.database import async_session_maker
from app.core.logging import get_logger

logger = get_logger("seed_db")

# ============================================================================
# Datos ficticios de usuarios (9 ficticios + 1 real)
# ============================================================================
FAKE_USERS = [
    {"full_name": "María Elena Rodríguez", "email": "maria.rodriguez@test.com", "phone": "+5491155667788", "external_id": "maria_rodriguez"},
    {"full_name": "Carlos Alberto Pérez", "email": "carlos.perez@test.com", "phone": "+5491144556677", "external_id": "carlos_perez"},
    {"full_name": "Ana Lucía Martínez", "email": "ana.martinez@test.com", "phone": "+5491133445566", "external_id": "ana_martinez"},
    {"full_name": "Diego Alejandro López", "email": "diego.lopez@test.com", "phone": "+5491122334455", "external_id": "diego_lopez"},
    {"full_name": "Valentina Gómez Silva", "email": "valentina.gomez@test.com", "phone": "+5491111223344", "external_id": "valentina_gomez"},
    {"full_name": "Matías Hernández", "email": "matias.hernandez@test.com", "phone": "+5491100112233", "external_id": "matias_hernandez"},
    {"full_name": "Luciana Torres Vega", "email": "luciana.torres@test.com", "phone": "+5491199001122", "external_id": "luciana_torres"},
    {"full_name": "Sebastián Morales", "email": "sebastian.morales@test.com", "phone": "+5491188990011", "external_id": "sebastian_morales"},
    {"full_name": "Camila Ruiz Díaz", "email": "camila.ruiz@test.com", "phone": "+5491177889900", "external_id": "camila_ruiz"},
]


def _get_real_user_data() -> dict:
    """Carga los datos personales reales desde el archivo protegido."""
    try:
        from scripts.seed_personal_data import REAL_USER
        return REAL_USER
    except ImportError:
        logger.warning(
            "No se encontró scripts/seed_personal_data.py. "
            "Usando datos de fallback para el usuario principal."
        )
        return {
            "full_name": "Usuario Principal Demo",
            "email": "demo@conversapay.com",
            "phone": "+5491100000000",
            "external_id": "demo_user_principal",
        }


# Descripciones realistas de transacciones por categoría
TRANSACTION_TEMPLATES = {
    1: [  # Comida
        ("Mercado Libre - Supermercado", -4500.00),
        ("Rappi - Pedido #4521", -2200.00),
        ("Carrefour Express", -8750.00),
        ("McDonald's Corrientes", -3100.00),
        ("Cafetería La Biela", -1800.00),
    ],
    2: [  # Servicios
        ("Edenor - Factura Mayo", -5200.00),
        ("Metrogas - Servicio mensual", -3800.00),
        ("Personal - Línea móvil", -6500.00),
        ("Spotify Premium", -2999.00),
        ("Netflix Argentina", -4299.00),
    ],
    3: [  # Transferencia
        ("Transferencia recibida - CBU", 15000.00),
        ("Transferencia enviada a Juan", -8000.00),
        ("Transferencia recibida - Alias", 45000.00),
        ("Transferencia a cuenta propia", -20000.00),
    ],
    4: [  # Sueldo
        ("Acreditación de haberes - Mayo 2026", 380000.00),
        ("Acreditación de haberes - Abril 2026", 365000.00),
        ("Bono SAC - Junio 2026", 190000.00),
    ],
    5: [  # Varios
        ("Farmacia del Pueblo", -2100.00),
        ("MercadoPago - QR", -5600.00),
        ("Retiro cajero Link", -15000.00),
        ("Devolución compra", 3200.00),
    ],
}


async def seed_database():
    """Puebla la base de datos con datos realistas."""
    real_user = _get_real_user_data()
    all_users = FAKE_USERS + [real_user]

    async with async_session_maker() as session:
        # Verificar si ya hay datos en fintech_mock
        result = await session.execute(text("SELECT COUNT(*) FROM fintech_mock.accounts"))
        count = result.scalar()
        if count and count > 0:
            logger.warning(f"Ya existen {count} cuentas en fintech_mock. Limpiando para re-seed...")
            await session.execute(text("DELETE FROM fintech_mock.transactions"))
            await session.execute(text("DELETE FROM fintech_mock.cards"))
            await session.execute(text("DELETE FROM fintech_mock.accounts"))
            # Limpiar usuarios que vamos a re-crear (excepto los que tienen sesiones activas)
            external_ids = [u["external_id"] for u in all_users]
            await session.execute(text("""
                DELETE FROM agent_core.users 
                WHERE external_id = ANY(:ids)
                AND user_id NOT IN (SELECT user_id FROM agent_core.sessions)
            """), {"ids": external_ids})
            await session.commit()

        created_user_ids = []

        for i, user_data in enumerate(all_users):
            is_real = (i == len(all_users) - 1)  # El último es el real

            # 1. Crear usuario en agent_core
            user_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO agent_core.users (user_id, external_id, channel_id, full_name, email, phone)
                VALUES (:uid, :eid, 1, :fname, :email, :phone)
                ON CONFLICT (external_id, channel_id) 
                DO UPDATE SET full_name = :fname, email = :email, phone = :phone
                RETURNING user_id
            """), {
                "uid": user_id,
                "eid": user_data["external_id"],
                "fname": user_data["full_name"],
                "email": user_data["email"],
                "phone": user_data["phone"],
            })
            await session.commit()

            # Recuperar el user_id real (puede ser el existente si ya estaba)
            result = await session.execute(text("""
                SELECT user_id FROM agent_core.users 
                WHERE external_id = :eid AND channel_id = 1
            """), {"eid": user_data["external_id"]})
            user_id = str(result.scalar())
            created_user_ids.append(user_id)

            # 2. Crear cuentas en fintech_mock
            accounts_to_create = []

            if is_real:
                # Facundo: Caja de Ahorro + Cuenta Corriente
                accounts_to_create = [
                    (1, 250000.00),   # Caja de Ahorro: $250,000
                    (2, 85000.00),    # Cuenta Corriente: $85,000
                ]
            else:
                # Usuarios ficticios: balance random
                num_accounts = random.randint(1, 2)
                for t in random.sample([1, 2], num_accounts):
                    balance = round(random.uniform(5000, 500000), 2)
                    accounts_to_create.append((t, balance))

            account_ids = []
            for type_id, balance in accounts_to_create:
                acc_id = str(uuid.uuid4())
                await session.execute(text("""
                    INSERT INTO fintech_mock.accounts (account_id, user_id, type_id, balance)
                    VALUES (:aid, :uid, :tid, :bal)
                """), {"aid": acc_id, "uid": user_id, "tid": type_id, "bal": balance})
                account_ids.append(acc_id)
            await session.commit()

            # 3. Crear tarjetas
            for acc_id in account_ids:
                num_cards = 2 if is_real else random.randint(1, 2)
                for _ in range(num_cards):
                    card_id = str(uuid.uuid4())
                    last_four = str(random.randint(1000, 9999))
                    is_active = True
                    is_blocked = False if is_real else (random.random() < 0.1)
                    await session.execute(text("""
                        INSERT INTO fintech_mock.cards (card_id, account_id, last_four, is_active, is_blocked)
                        VALUES (:cid, :aid, :lf, :ia, :ib)
                    """), {
                        "cid": card_id,
                        "aid": acc_id,
                        "lf": last_four,
                        "ia": is_active,
                        "ib": is_blocked,
                    })
                await session.commit()

            # 4. Crear transacciones
            num_transactions = 15 if is_real else random.randint(5, 12)
            for t in range(num_transactions):
                acc_id = random.choice(account_ids)
                category_id = random.choice([1, 2, 3, 4, 5])
                desc, amount = random.choice(TRANSACTION_TEMPLATES[category_id])

                # Variar montos ligeramente
                amount_variation = amount * random.uniform(0.8, 1.3)
                amount_final = round(amount_variation, 2)

                # Dates distribuidas en los últimos 60 días
                days_ago = random.randint(0, 60)
                tx_date = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))

                await session.execute(text("""
                    INSERT INTO fintech_mock.transactions (account_id, category_id, amount, description, created_at)
                    VALUES (:aid, :cid, :amt, :desc, :dat)
                """), {
                    "aid": acc_id,
                    "cid": category_id,
                    "amt": amount_final,
                    "desc": desc,
                    "dat": tx_date,
                })
            await session.commit()

            label = "🔒 REAL" if is_real else "👤 FICTICIO"
            logger.info(
                f"  {label}: {user_data['full_name']} — "
                f"{len(accounts_to_create)} cuentas, {num_transactions} transacciones"
            )

        logger.info("=" * 60)
        logger.info(f"SEED COMPLETADO: {len(all_users)} usuarios creados")
        logger.info(f"  Total cuentas estimadas: {sum(len(a) for a in [[1,2]]*len(all_users))}")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())
