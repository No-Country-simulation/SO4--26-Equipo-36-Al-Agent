"""
Servicio de persistencia transaccional (OLTP) para el Agent Core.
Se encarga de guardar y recuperar usuarios, sesiones, mensajes, feedback, OTP y ratings.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from sqlalchemy import select, update, and_
from sqlalchemy.sql import func

from app.core.database import async_session_maker
from app.common.models import User, Session, Message, Feedback, OTPChallenge, SessionRating
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
        channel_id = 1 asume web_chat por defecto.
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
    async def save_message(session_id: str, role_id: int, content: str, tokens_used: int = 0, message_id: Optional[str] = None) -> str:
        """
        Guarda un mensaje en la tabla agent_core.messages.
        role_id: 1=user, 2=assistant, 3=system
        Retorna el message_id generado o el provisto.
        """
        async with async_session_maker() as db_session:
            message = Message(
                session_id=session_id,
                role_id=role_id,
                content=content,
                tokens_used=tokens_used
            )
            if message_id:
                message.message_id = message_id
            db_session.add(message)
            await db_session.commit()
            await db_session.refresh(message)
            return str(message.message_id)

    @staticmethod
    async def get_real_session_id(external_id: str) -> Optional[str]:
        """
        Busca el session_id real (UUID) basado en el external_id (client_session_id).
        Retorna el ID de la sesión más reciente o None.
        """
        async with async_session_maker() as db_session:
            stmt = select(User).filter(User.external_id == external_id)
            result = await db_session.execute(stmt)
            user = result.scalars().first()

            if not user:
                return None

            stmt = select(Session).filter(Session.user_id == user.user_id).order_by(Session.start_time.desc())
            result = await db_session.execute(stmt)
            sess = result.scalars().first()

            return str(sess.session_id) if sess else None

    @staticmethod
    async def save_feedback(message_id: str, rating: int, comment: str = None) -> bool:
        """Guarda el feedback del usuario para un mensaje específico."""
        async with async_session_maker() as db_session:
            feedback = Feedback(
                message_id=message_id,
                rating=rating,
                comment=comment
            )
            db_session.add(feedback)
            await db_session.commit()
            return True

    @staticmethod
    async def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por email en la tabla agent_core.users.
        Retorna un dict con datos del usuario o None si no existe.
        """
        async with async_session_maker() as db_session:
            stmt = select(User).filter(User.email == email.lower().strip())
            result = await db_session.execute(stmt)
            user = result.scalars().first()

            if user:
                return {
                    "user_id": str(user.user_id),
                    "email": user.email,
                    "phone": user.phone,
                    "full_name": user.full_name,
                    "external_id": user.external_id,
                }
            return None

    @staticmethod
    async def create_otp_challenge(
        user_id: str, code: str, email: str, ttl_seconds: int = 300
    ) -> None:
        """Crea un challenge OTP en la base de datos."""
        async with async_session_maker() as db_session:
            # Invalidar OTPs previos de este usuario
            stmt = (
                update(OTPChallenge)
                .where(and_(
                    OTPChallenge.user_id == user_id,
                    OTPChallenge.is_used == False
                ))
                .values(is_used=True)
            )
            await db_session.execute(stmt)

            # Crear nuevo challenge
            challenge = OTPChallenge(
                user_id=user_id,
                code=code,
                email_sent_to=email,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            )
            db_session.add(challenge)
            await db_session.commit()

    @staticmethod
    async def validate_otp_challenge(user_id: str, code: str) -> Dict[str, Any]:
        """
        Valida un código OTP contra la DB.
        Retorna dict con status: 'valid', 'expired', 'invalid_code', 'max_attempts', 'not_found'
        """
        async with async_session_maker() as db_session:
            stmt = (
                select(OTPChallenge)
                .filter(
                    OTPChallenge.user_id == user_id,
                    OTPChallenge.is_used == False
                )
                .order_by(OTPChallenge.created_at.desc())
                .limit(1)
            )
            result = await db_session.execute(stmt)
            challenge = result.scalars().first()

            if not challenge:
                return {"status": "not_found"}

            # Verificar expiración
            if datetime.now(timezone.utc) > challenge.expires_at:
                challenge.is_used = True
                await db_session.commit()
                return {"status": "expired"}

            # Verificar intentos
            if challenge.attempts >= 3:
                challenge.is_used = True
                await db_session.commit()
                return {"status": "max_attempts"}

            # Verificar código
            if challenge.code != code:
                challenge.attempts += 1
                await db_session.commit()
                return {"status": "invalid_code", "attempts": challenge.attempts}

            # Éxito
            challenge.is_used = True
            await db_session.commit()
            return {"status": "valid"}

    @staticmethod
    async def close_session(session_id: str) -> None:
        """Marca una sesión como FINISHED (status_id=2) con end_time."""
        async with async_session_maker() as db_session:
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(
                    status_id=2,
                    end_time=func.current_timestamp()
                )
            )
            await db_session.execute(stmt)
            await db_session.commit()
            logger.info(f"Sesión {session_id} cerrada.")

    @staticmethod
    async def save_session_rating(
        session_id: str, rating: int, comment: str = None
    ) -> bool:
        """Guarda el rating de estrellas (1-5) para una sesión."""
        async with async_session_maker() as db_session:
            session_rating = SessionRating(
                session_id=session_id,
                rating=rating,
                comment=comment
            )
            db_session.add(session_rating)
            await db_session.commit()
            return True
