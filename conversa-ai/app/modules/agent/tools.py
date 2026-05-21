from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker
from app.common.models import Account, Transaction, Card, CatAccountType, CatTransactionCategory
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_account_balance(user_id: str) -> str:
    """
    Obtiene el saldo de todas las cuentas bancarias del usuario.
    """
    logger.info(f"Ejecutando tool: get_account_balance para user_id={user_id}")
    async with async_session_maker() as session:
        # Cast de string a UUID se hace automáticamente en asyncpg/sqlalchemy, o filtramos como string
        # En la tabla Account, user_id es UUID.
        stmt = select(Account).options(selectinload(Account.account_type)).filter(Account.user_id == user_id)
        result = await session.execute(stmt)
        accounts = result.scalars().all()
        
        if not accounts:
            return "No se encontraron cuentas bancarias para este usuario."
            
        res = "Saldos actuales:\n"
        for acc in accounts:
            res += f"- {acc.account_type.type_name}: ${acc.balance:,.2f}\n"
        return res


async def get_recent_transactions(user_id: str, limit: int = 5) -> str:
    """
    Obtiene las últimas transacciones bancarias del usuario en todas sus cuentas.
    """
    logger.info(f"Ejecutando tool: get_recent_transactions para user_id={user_id}")
    async with async_session_maker() as session:
        # Primero obtener las cuentas
        stmt_acc = select(Account.account_id).filter(Account.user_id == user_id)
        result_acc = await session.execute(stmt_acc)
        account_ids = result_acc.scalars().all()
        
        if not account_ids:
            return "No se encontraron cuentas bancarias, por lo tanto no hay transacciones."
            
        stmt_txn = (
            select(Transaction)
            .options(selectinload(Transaction.category))
            .filter(Transaction.account_id.in_(account_ids))
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        result_txn = await session.execute(stmt_txn)
        transactions = result_txn.scalars().all()
        
        if not transactions:
            return "No tenés movimientos recientes."
            
        res = f"Últimos {len(transactions)} movimientos:\n"
        for t in transactions:
            date_str = t.created_at.strftime("%Y-%m-%d")
            res += f"- {date_str} | {t.category.category_name} | ${t.amount:,.2f} | {t.description}\n"
        return res


async def get_card_status(user_id: str) -> str:
    """
    Obtiene el estado de las tarjetas bancarias vinculadas al usuario.
    """
    logger.info(f"Ejecutando tool: get_card_status para user_id={user_id}")
    async with async_session_maker() as session:
        stmt_acc = select(Account.account_id).filter(Account.user_id == user_id)
        result_acc = await session.execute(stmt_acc)
        account_ids = result_acc.scalars().all()
        
        if not account_ids:
            return "No se encontraron tarjetas, ya que el usuario no tiene cuentas."
            
        stmt_cards = select(Card).filter(Card.account_id.in_(account_ids))
        result_cards = await session.execute(stmt_cards)
        cards = result_cards.scalars().all()
        
        if not cards:
            return "No tenés tarjetas emitidas a tu nombre."
            
        res = "Estado de tus Tarjetas:\n"
        for c in cards:
            estado = "Bloqueada" if c.is_blocked else ("Activa" if c.is_active else "Inactiva")
            res += f"- Tarjeta terminada en {c.last_four}: {estado}\n"
        return res


# Mapeo de herramientas por nombre de intención
FINTECH_TOOLS = {
    "get_account_balance": get_account_balance,
    "get_recent_transactions": get_recent_transactions,
    "get_card_status": get_card_status,
}
