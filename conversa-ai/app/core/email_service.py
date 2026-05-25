"""
Servicio de envío de emails asíncrono para OTP y notificaciones.
Usa aiosmtplib para envío real vía SMTP (Gmail).
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Servicio asíncrono para envío de emails."""

    @staticmethod
    async def send_otp_email(to_email: str, otp_code: str, user_name: str = "") -> bool:
        """
        Envía un email real con el código OTP al usuario.
        Retorna True si el envío fue exitoso, False si falló.
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning(
                f"[SMTP NO CONFIGURADO] OTP para {to_email}: {otp_code}. "
                "Configurá SMTP_USER y SMTP_PASSWORD en .env para envío real."
            )
            return True  # En desarrollo, simular éxito

        greeting = f"Hola {user_name}" if user_name else "Hola"

        html_content = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #050505; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; margin: 0;">
                    CONVERSA <span style="color: #ccff00; background: #050505; padding: 2px 8px;">PAY</span>
                </h1>
            </div>

            <div style="background: #050505; color: #ffffff; padding: 30px; border: 2px solid #333;">
                <p style="margin: 0 0 20px 0; font-size: 16px;">{greeting},</p>

                <p style="margin: 0 0 15px 0; font-size: 14px; color: #cccccc;">
                    Recibimos una solicitud de verificación de identidad para acceder a tu información financiera
                    a través de nuestro asistente virtual.
                </p>

                <div style="background: #1a1a1a; border: 2px solid #ccff00; padding: 20px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0 0 8px 0; font-size: 12px; color: #ccff00; text-transform: uppercase; letter-spacing: 2px;">
                        Tu código de verificación
                    </p>
                    <p style="margin: 0; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #ffffff;">
                        {otp_code}
                    </p>
                </div>

                <p style="margin: 20px 0 0 0; font-size: 12px; color: #888888;">
                    Este código expira en 5 minutos. Si no solicitaste este código, ignorá este email.
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <p style="font-size: 11px; color: #999999;">
                    Conversa Pay S.A. — Este es un email automático, no respondas a este mensaje.
                </p>
            </div>
        </div>
        """

        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = f"Conversa Pay — Tu código de verificación: {otp_code}"

        # Versión texto plano
        text_content = (
            f"{greeting},\n\n"
            f"Tu código de verificación de Conversa Pay es: {otp_code}\n\n"
            f"Este código expira en 5 minutos.\n"
            f"Si no solicitaste este código, ignorá este email.\n\n"
            f"— Conversa Pay"
        )
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info(f"Email OTP enviado exitosamente a {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email OTP a {to_email}: {e}")
            # Fallback: loguear el código para desarrollo
            logger.warning(f"[FALLBACK] OTP para {to_email}: {otp_code}")
            return False
