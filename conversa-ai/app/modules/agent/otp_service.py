import random
import time
from typing import Dict, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)

# En un entorno real, esto se guardaría en Redis con un TTL de 5 minutos
# Formato: { "user_id": ("123456", timestamp_expiracion, intentos_fallidos) }
_otp_store: Dict[str, Tuple[str, float, int]] = {}

OTP_TTL_SECONDS = 300 # 5 minutos
MAX_ATTEMPTS = 3

class OTPService:
    """
    Servicio para gestionar la Autenticación de Doble Factor (OTP).
    """
    
    @staticmethod
    def generate_and_send_otp(user_id: str, phone_number: str) -> bool:
        """
        Genera un código de 6 dígitos y simula el envío por WhatsApp.
        """
        code = str(random.randint(100000, 999999))
        expiration = time.time() + OTP_TTL_SECONDS
        
        _otp_store[user_id] = (code, expiration, 0)
        
        # Simulación de envío por WhatsApp
        logger.info(f"[SIMULACIÓN WHATSAPP] Enviando OTP {code} al número {phone_number}")
        return True

    @staticmethod
    def validate_otp(user_id: str, code: str) -> Tuple[bool, str]:
        """
        Valida el código ingresado por el usuario.
        Retorna (es_valido, mensaje_informativo).
        """
        if user_id not in _otp_store:
            return False, "No hay ningún código pendiente de validación o ya expiró."
            
        stored_code, expiration, attempts = _otp_store[user_id]
        
        if time.time() > expiration:
            del _otp_store[user_id]
            return False, "El código ha expirado. Por favor, solicitá uno nuevo."
            
        if stored_code != code.strip():
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                del _otp_store[user_id]
                return False, "Superaste el límite de intentos. Operación cancelada por seguridad."
            
            _otp_store[user_id] = (stored_code, expiration, attempts)
            return False, f"Código incorrecto. Te quedan {MAX_ATTEMPTS - attempts} intentos."
            
        # Validación exitosa
        del _otp_store[user_id]
        return True, "Validación exitosa."
