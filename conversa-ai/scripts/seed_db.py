import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import async_session_maker
from app.core.logging import get_logger
from sqlalchemy import text

logger = get_logger("seed_db")

async def seed_data():
    logger.info("Iniciando seeding de base de datos...")
    
    async with async_session_maker() as session:
        try:
            # Insertar cat_channels si no existe
            await session.execute(text("INSERT INTO agent_core.cat_channels (channel_id, channel_name) VALUES (1, 'web') ON CONFLICT DO NOTHING;"))
            
            # Insertar cat_roles si no existe
            await session.execute(text("INSERT INTO agent_core.cat_roles (role_id, role_name) VALUES (1, 'user'), (2, 'assistant') ON CONFLICT DO NOTHING;"))
            
            # Insertar cat_session_statuses
            await session.execute(text("INSERT INTO agent_core.cat_session_statuses (status_id, status_name) VALUES (1, 'active'), (2, 'closed') ON CONFLICT DO NOTHING;"))
            
            # Insertar un usuario demo en agent_core.users
            await session.execute(text("""
                INSERT INTO agent_core.users (user_id, external_id, channel_id) 
                VALUES ('00000000-0000-0000-0000-000000000001', 'demo_user', 1) 
                ON CONFLICT DO NOTHING;
            """))
            
            # Insertar cuenta de tipo (Caja de Ahorro)
            await session.execute(text("INSERT INTO fintech_mock.cat_account_types (type_id, type_name) VALUES (1, 'Caja de Ahorro en Pesos') ON CONFLICT DO NOTHING;"))
            
            # Insertar categorías de transacción
            await session.execute(text("INSERT INTO fintech_mock.cat_transaction_categories (category_id, category_name) VALUES (1, 'Transferencia'), (2, 'Pago de Servicios'), (3, 'Compra Tarjeta') ON CONFLICT DO NOTHING;"))
            
            # Insertar cuenta para el demo user con $45,291.00
            await session.execute(text("""
                INSERT INTO fintech_mock.accounts (account_id, user_id, type_id, balance) 
                VALUES ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', 1, 45291.00)
                ON CONFLICT DO NOTHING;
            """))
            
            # Insertar transacciones
            await session.execute(text("""
                INSERT INTO fintech_mock.transactions (account_id, category_id, amount, description) 
                VALUES ('11111111-1111-1111-1111-111111111111', 1, -1500.00, 'Transferencia a Juan'),
                       ('11111111-1111-1111-1111-111111111111', 2, -3200.00, 'Pago Edenor'),
                       ('11111111-1111-1111-1111-111111111111', 3, -12000.00, 'Compra en MercadoLibre')
            """))
            
            # Insertar tarjeta
            await session.execute(text("""
                INSERT INTO fintech_mock.cards (account_id, last_four, is_active) 
                VALUES ('11111111-1111-1111-1111-111111111111', '4921', TRUE)
            """))
            
            await session.commit()
            logger.info("Seeding completado con éxito.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error durante el seeding: {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
