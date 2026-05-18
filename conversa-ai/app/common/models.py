"""
Mapea todas las tablas definidas en init.sql a modelos ORM de SQLAlchemy.
Organizado por esquema:
  - agent_core: Catálogos + Tablas operativas (OLTP)
  - fintech_mock: Simulación de la fintech
  - analytics_warehouse: Data warehouse analítico (OLAP con modelado estrella)
"""

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy del sistema."""
    pass

# 1. ESQUEMA: agent_core (OLTP - Transaccional del Agente)
class CatChannel(Base):
    """Catálogo de canales de mensajería (WhatsApp, Telegram)."""
    __tablename__ = "cat_channels"
    __table_args__ = {"schema": "agent_core"}

    channel_id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String(50), nullable=False, unique=True)

    # Relaciones
    users = relationship("User", back_populates="channel")


class CatRole(Base):
    """Catálogo de roles de mensajes (user, assistant, system)."""
    __tablename__ = "cat_roles"
    __table_args__ = {"schema": "agent_core"}

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(20), nullable=False, unique=True)

    # Relaciones
    messages = relationship("Message", back_populates="role")

# Los estados de las sesiones/tickets de conversación del agente.
class CatSessionStatus(Base):
    """Catálogo de estados de sesión (IN_PROGRESS, FINISHED, etc.)."""
    __tablename__ = "cat_session_statuses"
    __table_args__ = {"schema": "agent_core"}

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String(30), nullable=False, unique=True)

    # Relaciones
    sessions = relationship("Session", back_populates="status")


class CatLanguage(Base):
    """Catálogo de idiomas soportados (Español, Portugués)."""
    __tablename__ = "cat_languages"
    __table_args__ = {"schema": "agent_core"}

    language_id = Column(Integer, primary_key=True, autoincrement=True)
    language_name = Column(String(50), nullable=False, unique=True)
    iso_code = Column(String(2), nullable=False, unique=True)

    # Relaciones
    sessions = relationship("Session", back_populates="language")


class CatTag(Base):
    """Catálogo de etiquetas para clasificación (IA, soporte, negocio)."""
    __tablename__ = "cat_tags"
    __table_args__ = {"schema": "agent_core"}

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(50), nullable=False, unique=True)
    category = Column(String(30))

    # Relaciones (tabla puente)
    sessions = relationship("Session", secondary="agent_core.session_tags", back_populates="tags")


class User(Base):
    """Usuarios del sistema, identificados por external_id + canal."""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("external_id", "channel_id", name="unq_user_per_channel"),
        {"schema": "agent_core"},
    )

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                     server_default=func.uuid_generate_v4())
    external_id = Column(String(100), nullable=False)
    channel_id = Column(Integer, ForeignKey("agent_core.cat_channels.channel_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # Relaciones
    channel = relationship("CatChannel", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Sesiones/tickets de conversación del agente."""
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("retry_count >= 0", name="ck_retries_non_negative"),
        Index("idx_sessions_user", "user_id"),
        Index("idx_sessions_status", "status_id"),
        {"schema": "agent_core"},
    )

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                        server_default=func.uuid_generate_v4())
    user_id = Column(UUID(as_uuid=True), ForeignKey("agent_core.users.user_id", ondelete="CASCADE"),
                     nullable=False)
    status_id = Column(Integer, ForeignKey("agent_core.cat_session_statuses.status_id"),
                       nullable=False, server_default="1")
    language_id = Column(Integer, ForeignKey("agent_core.cat_languages.language_id"))
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(TIMESTAMP(timezone=True))
    start_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    end_time = Column(TIMESTAMP(timezone=True))

    # Relaciones
    user = relationship("User", back_populates="sessions")
    status = relationship("CatSessionStatus", back_populates="sessions")
    language = relationship("CatLanguage", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    tags = relationship("CatTag", secondary="agent_core.session_tags", back_populates="sessions")


class Message(Base):
    """Mensajes individuales dentro de una sesión/ticket."""
    __tablename__ = "messages"
    __table_args__ = (
        Index("idx_messages_session", "session_id"),
        {"schema": "agent_core"},
    )

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                        server_default=func.uuid_generate_v4())
    session_id = Column(UUID(as_uuid=True),
                        ForeignKey("agent_core.sessions.session_id", ondelete="CASCADE"),
                        nullable=False)
    role_id = Column(Integer, ForeignKey("agent_core.cat_roles.role_id"), nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # Relaciones
    session = relationship("Session", back_populates="messages")
    role = relationship("CatRole", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")


class SessionTag(Base):
    """Tabla puente OLTP: Muchas etiquetas por sesión/ticket."""
    __tablename__ = "session_tags"
    __table_args__ = {"schema": "agent_core"}

    session_id = Column(UUID(as_uuid=True),
                        ForeignKey("agent_core.sessions.session_id", ondelete="CASCADE"),
                        primary_key=True)
    tag_id = Column(Integer,
                    ForeignKey("agent_core.cat_tags.tag_id", ondelete="CASCADE"),
                    primary_key=True)


class Feedback(Base):
    """Feedback del usuario (like/dislike) sobre mensajes individuales."""
    __tablename__ = "feedback"
    __table_args__ = {"schema": "agent_core"}

    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                         server_default=func.uuid_generate_v4())
    message_id = Column(UUID(as_uuid=True),
                        ForeignKey("agent_core.messages.message_id", ondelete="CASCADE"),
                        nullable=False)
    rating = Column(Integer, nullable=False)  # CHECK (rating IN (1, -1))
    comment = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # Relaciones
    message = relationship("Message", back_populates="feedback")

# 2. ESQUEMA: fintech_mock (Simulación de operaciones de la fintech)
class CatAccountType(Base):
    """Catálogo de tipos de cuenta (Caja de Ahorro, Cuenta Corriente, etc.)."""
    __tablename__ = "cat_account_types"
    __table_args__ = {"schema": "fintech_mock"}

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), nullable=False, unique=True)

    # Relaciones
    accounts = relationship("Account", back_populates="account_type")


class CatTransactionCategory(Base):
    """Catálogo de categorías de transacciones (Comida, Servicios, etc.)."""
    __tablename__ = "cat_transaction_categories"
    __table_args__ = {"schema": "fintech_mock"}

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False, unique=True)

    # Relaciones
    transactions = relationship("Transaction", back_populates="category")


class Account(Base):
    """Cuentas bancarias simuladas, vinculadas lógicamente a agent_core.users."""
    __tablename__ = "accounts"
    __table_args__ = {"schema": "fintech_mock"}

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                        server_default=func.uuid_generate_v4())
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Vínculo lógico (sin FK física)
    type_id = Column(Integer, ForeignKey("fintech_mock.cat_account_types.type_id"), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # Relaciones
    account_type = relationship("CatAccountType", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    cards = relationship("Card", back_populates="account")


class Transaction(Base):
    """Transacciones bancarias simuladas."""
    __tablename__ = "transactions"
    __table_args__ = {"schema": "fintech_mock"}

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                            server_default=func.uuid_generate_v4())
    account_id = Column(UUID(as_uuid=True),
                        ForeignKey("fintech_mock.accounts.account_id"), nullable=False)
    category_id = Column(Integer,
                         ForeignKey("fintech_mock.cat_transaction_categories.category_id"),
                         nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # Relaciones
    account = relationship("Account", back_populates="transactions")
    category = relationship("CatTransactionCategory", back_populates="transactions")


class Card(Base):
    """Tarjetas bancarias simuladas."""
    __tablename__ = "cards"
    __table_args__ = {"schema": "fintech_mock"}

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                     server_default=func.uuid_generate_v4())
    account_id = Column(UUID(as_uuid=True),
                        ForeignKey("fintech_mock.accounts.account_id"), nullable=False)
    last_four = Column(String(4))
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    # Relaciones
    account = relationship("Account", back_populates="cards")

# 3. ESQUEMA: analytics_warehouse (OLAP - Modelado de Estrella)
class CatResolutionType(Base):
    """Catálogo de tipos de resolución (SUCCESS, FRUSTRATION, NEUTRAL)."""
    __tablename__ = "cat_resolution_types"
    __table_args__ = {"schema": "analytics_warehouse"}

    resolution_id = Column(Integer, primary_key=True, autoincrement=True)
    resolution_name = Column(String(50), nullable=False, unique=True)

    # Relaciones
    evaluations = relationship("FactSessionsEvaluation", back_populates="resolution")


class DimTime(Base):
    """Dimensión de tiempo para el warehouse analítico."""
    __tablename__ = "dim_time"
    __table_args__ = (
        UniqueConstraint("full_date", "hour", name="unq_time_hour"),
        {"schema": "analytics_warehouse"},
    )

    time_id = Column(Integer, primary_key=True, autoincrement=True)
    full_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    day_of_week = Column(String(15), nullable=False)
    is_weekend = Column(Boolean, default=False)

    # Relaciones
    evaluations = relationship("FactSessionsEvaluation", back_populates="dim_time")


class DimLanguage(Base):
    """Dimensión conformada de idioma para el warehouse."""
    __tablename__ = "dim_language"
    __table_args__ = {"schema": "analytics_warehouse"}

    language_id = Column(Integer, primary_key=True, autoincrement=True)
    language_name = Column(String(50), nullable=False, unique=True)
    iso_code = Column(String(2), nullable=False, unique=True)

    # Relaciones
    evaluations = relationship("FactSessionsEvaluation", back_populates="dim_language")


class DimIntent(Base):
    """Dimensión de intenciones del usuario detectadas por IA."""
    __tablename__ = "dim_intent"
    __table_args__ = {"schema": "analytics_warehouse"}

    intent_id = Column(Integer, primary_key=True, autoincrement=True)
    intent_name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)

    # Relaciones
    evaluations = relationship("FactSessionsEvaluation", back_populates="dim_intent")


class DimSentiment(Base):
    """Dimensión de sentimientos (Success, Neutral, Frustrated)."""
    __tablename__ = "dim_sentiment"
    __table_args__ = {"schema": "analytics_warehouse"}

    sentiment_id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(50), nullable=False, unique=True)
    sentiment_group = Column(String(20), nullable=False)

    # Relaciones
    evaluations = relationship("FactSessionsEvaluation", back_populates="dim_sentiment")


class DimTag(Base):
    """Dimensión de etiquetas analíticas (sincronizadas desde agent_core)."""
    __tablename__ = "dim_tags"
    __table_args__ = {"schema": "analytics_warehouse"}

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(50), nullable=False, unique=True)
    category = Column(String(30))

    # Relaciones (tabla puente OLAP)
    evaluations = relationship(
        "FactSessionsEvaluation",
        secondary="analytics_warehouse.fact_tag_assignments",
        back_populates="tags",
    )


class FactSessionsEvaluation(Base):
    """Tabla de hechos principal: evaluación consolidada de cada sesión."""
    __tablename__ = "fact_sessions_evaluation"
    __table_args__ = (
        Index("idx_fact_resolution", "resolution_id"),
        Index("idx_fact_time", "dim_time_id"),
        Index("idx_fact_language", "dim_language_id"),
        {"schema": "analytics_warehouse"},
    )

    fact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                     server_default=func.uuid_generate_v4())
    session_id = Column(UUID(as_uuid=True), nullable=False)  # Trazabilidad al ID original
    dim_time_id = Column(Integer,
                         ForeignKey("analytics_warehouse.dim_time.time_id"))
    dim_language_id = Column(Integer,
                             ForeignKey("analytics_warehouse.dim_language.language_id"))
    dim_intent_id = Column(Integer,
                           ForeignKey("analytics_warehouse.dim_intent.intent_id"))
    dim_sentiment_id = Column(Integer,
                              ForeignKey("analytics_warehouse.dim_sentiment.sentiment_id"))
    resolution_id = Column(Integer,
                           ForeignKey("analytics_warehouse.cat_resolution_types.resolution_id"))

    # Métricas consolidadas por el Evaluador
    session_duration_seconds = Column(Integer)
    total_messages = Column(Integer, default=0)
    sentiment_score = Column(Numeric(3, 2))
    positive_feedback_count = Column(Integer, default=0)
    negative_feedback_count = Column(Integer, default=0)
    is_abandoned = Column(Boolean, default=False)

    # Relaciones
    dim_time = relationship("DimTime", back_populates="evaluations")
    dim_language = relationship("DimLanguage", back_populates="evaluations")
    dim_intent = relationship("DimIntent", back_populates="evaluations")
    dim_sentiment = relationship("DimSentiment", back_populates="evaluations")
    resolution = relationship("CatResolutionType", back_populates="evaluations")
    tags = relationship(
        "DimTag",
        secondary="analytics_warehouse.fact_tag_assignments",
        back_populates="evaluations",
    )


class FactTagAssignment(Base):
    """Tabla puente OLAP: relación muchos-a-muchos entre hechos y etiquetas."""
    __tablename__ = "fact_tag_assignments"
    __table_args__ = (
        Index("idx_fact_tag_assignment_tag", "tag_id"),
        {"schema": "analytics_warehouse"},
    )

    fact_id = Column(UUID(as_uuid=True),
                     ForeignKey("analytics_warehouse.fact_sessions_evaluation.fact_id",
                                ondelete="CASCADE"),
                     primary_key=True)
    tag_id = Column(Integer,
                    ForeignKey("analytics_warehouse.dim_tags.tag_id", ondelete="CASCADE"),
                    primary_key=True)
