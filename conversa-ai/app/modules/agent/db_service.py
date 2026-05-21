from sqlalchemy import select
from app.core.database import async_session_maker
from app.common.models import User, Session, Message
from app.core.logging import get_logger

logger = get_logger(__name__)

class DBService:
    """
    Servicio de persistencia transaccional (OLTP) para el Agent Core.
    Se encarga de guardar y recuperar usuarios, sesiones y mensajes.
    """
    
    @staticmethod
    async def get_or_create_user_and_session(external_id: str, channel_id: int = 1):
        """
        Recupera o crea un usuario y una sesión activa para el canal especificado.
        channel_id = 1 asume WhatsApp por defecto.
        Retorna (user_id_str, session_id_str)
        """
        async with async_session_maker() as db_session:
            # 1. Obtener o crear User
            stmt = select(User).filter(User.external_id == external_id, User.channel_id == channel_id)
            result = await db_session.execute(stmt)
            user = result.scalars().first()
            
            if not user:
                user = User(external_id=external_id, channel_id=channel_id)
                db_session.add(user)
                await db_session.commit()
                await db_session.refresh(user)
                logger.info(f"Creado nuevo usuario en DB: {user.user_id}")
            
            # 2. Obtener sesión activa (status_id = 1 es IN_PROGRESS) o crear una
            stmt = select(Session).filter(Session.user_id == user.user_id, Session.status_id == 1)
            result = await db_session.execute(stmt)
            session_obj = result.scalars().first()
            
            if not session_obj:
                session_obj = Session(user_id=user.user_id, status_id=1)
                db_session.add(session_obj)
                await db_session.commit()
                await db_session.refresh(session_obj)
                logger.info(f"Creada nueva sesión en DB: {session_obj.session_id}")
                
            return str(user.user_id), str(session_obj.session_id)

    @staticmethod
    async def save_message(session_id: str, role_id: int, content: str, tokens_used: int = 0) -> str:
        """
        Guarda un mensaje en la tabla agent_core.messages.
        role_id: 1=user, 2=assistant, 3=system
        Retorna el message_id generado.
        """
        async with async_session_maker() as db_session:
            message = Message(
                session_id=session_id,
                role_id=role_id,
                content=content,
                tokens_used=tokens_used
            )
            db_session.add(message)
            await db_session.commit()
            await db_session.refresh(message)
            return str(message.message_id)

    @staticmethod
    async def save_feedback(message_id: str, rating: int, comment: str = None) -> bool:
        """
        Guarda el feedback del usuario para un mensaje específico.
        """
        from app.common.models import Feedback
        async with async_session_maker() as db_session:
            feedback = Feedback(
                message_id=message_id,
                rating=rating,
                comment=comment
            )
            db_session.add(feedback)
            await db_session.commit()
            return True
