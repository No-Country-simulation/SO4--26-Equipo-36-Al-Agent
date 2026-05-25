"""
Servicio para gestionar la Autenticación de Doble Factor (OTP).
Genera códigos reales, los persiste en DB y los envía por email.
"""

import random
import time
from typing import Tuple

from app.core.email_service import EmailService
from app.core.logging import get_logger
from app.modules.agent.db_service import DBService

logger = get_logger(__name__)

OTP_TTL_SECONDS = 300  # 5 minutos
MAX_ATTEMPTS = 3


class OTPService:
    """
    Servicio para gestionar la Autenticación de Doble Factor (OTP).
    Genera códigos, los envía por email real y los valida contra la DB.
    """

    @staticmethod
    async def generate_and_send_otp(user_id: str, email: str, user_name: str = "") -> bool:
        """
        Genera un código de 6 dígitos, lo persiste en DB y lo envía por email real.
        """
        code = str(random.randint(100000, 999999))

        # Persistir en DB
        await DBService.create_otp_challenge(
            user_id=user_id,
            code=code,
            email=email,
            ttl_seconds=OTP_TTL_SECONDS
        )

        # Enviar por email real
        success = await EmailService.send_otp_email(
            to_email=email,
            otp_code=code,
            user_name=user_name
        )

        if success:
            logger.info(f"OTP generado y enviado a {email} para user_id={user_id}")
        else:
            logger.error(f"Fallo al enviar OTP a {email}")

        return success

    @staticmethod
    async def validate_otp(user_id: str, code: str) -> Tuple[bool, str]:
        """
        Valida el código ingresado por el usuario contra la DB.
        Retorna (es_valido, mensaje_informativo).
        """
        result = await DBService.validate_otp_challenge(user_id, code.strip())

        if result["status"] == "valid":
            return True, "Identidad verificada correctamente."
        elif result["status"] == "expired":
            return False, "El código ha expirado. Por favor, solicitá uno nuevo ingresando tu email."
        elif result["status"] == "invalid_code":
            remaining = MAX_ATTEMPTS - result.get("attempts", 0)
            if remaining <= 0:
                return False, "Superaste el límite de intentos. Por seguridad, la operación fue cancelada. Intentá de nuevo más tarde."
            return False, f"Código incorrecto. Te quedan {remaining} intentos."
        elif result["status"] == "max_attempts":
            return False, "Superaste el límite de intentos. Por seguridad, la operación fue cancelada."
        else:
            return False, "No hay ningún código pendiente de validación. Ingresá tu email para recibir uno nuevo."
