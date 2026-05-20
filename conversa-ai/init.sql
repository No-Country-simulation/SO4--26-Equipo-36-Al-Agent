CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Esquemas del Sistema
CREATE SCHEMA IF NOT EXISTS agent_core;
CREATE SCHEMA IF NOT EXISTS fintech_mock;
CREATE SCHEMA IF NOT EXISTS analytics_warehouse;
CREATE SCHEMA IF NOT EXISTS internal_ops;

-- 1. Esquema de Operaciones e infraestructura interna (internal_ops)

-- Tabla de permisos atómicos 
CREATE TABLE internal_ops.permissions (
    permission_id SERIAL PRIMARY KEY,
    codename VARCHAR(100) NOT NULL UNIQUE, -- Formato 'modulo:accion' (ej: 'pipeline:execute')
    name VARCHAR(150) NOT NULL,            -- Nombre legible (ej: 'Gatillar Ingesta Mensual')
    category VARCHAR(50) NOT NULL          -- Agrupador (ej: 'Analítica', 'Seguridad')
);

-- Tabla de roles del sistema
CREATE TABLE internal_ops.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,  -- 'Data Analyst', 'Support Lead', etc.
    description TEXT
);

-- Tabla puente: Relación Muchos a Muchos entre Roles y Permisos
CREATE TABLE internal_ops.role_permissions (
    role_id INTEGER REFERENCES internal_ops.roles(role_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES internal_ops.permissions(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Tabla de usuarios internos (Empleados)
CREATE TABLE internal_ops.users (
    internal_user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES internal_ops.roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Gestión de sesiones y lista negra de JWT
CREATE TABLE internal_ops.sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internal_user_id UUID NOT NULL REFERENCES internal_ops.users(internal_user_id) ON DELETE CASCADE,
    jti VARCHAR(255) UNIQUE NOT NULL, 
    is_revoked BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Optimización de Seguridad
CREATE INDEX idx_internal_users_email ON internal_ops.users(email);
CREATE INDEX idx_internal_permissions_code ON internal_ops.permissions(codename);
CREATE INDEX idx_internal_sessions_jti ON internal_ops.sessions(jti);


-- 1. Esquema transaccional del agente (agent_core)
-- Catálogos del Agente
CREATE TABLE agent_core.cat_channels (
    channel_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE agent_core.cat_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE agent_core.cat_session_statuses (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE agent_core.cat_languages (
    language_id SERIAL PRIMARY KEY,
    language_name VARCHAR(50) NOT NULL UNIQUE,
    iso_code CHAR(2) NOT NULL UNIQUE
);

CREATE TABLE agent_core.cat_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(30) -- 'ia', 'soporte', 'negocio'
);

-- Tablas Operativas (Tickets y Mensajería)
CREATE TABLE agent_core.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) NOT NULL, 
    channel_id INTEGER NOT NULL REFERENCES agent_core.cat_channels(channel_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unq_user_per_channel UNIQUE (external_id, channel_id)
);

CREATE TABLE agent_core.sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES agent_core.users(user_id) ON DELETE CASCADE,
    status_id INTEGER NOT NULL REFERENCES agent_core.cat_session_statuses(status_id) DEFAULT 1,
    language_id INTEGER REFERENCES agent_core.cat_languages(language_id),
    retry_count INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    CONSTRAINT ck_retries_non_negative CHECK (retry_count >= 0)
);

CREATE TABLE agent_core.messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES agent_core.sessions(session_id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES agent_core.cat_roles(role_id),
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Puente OLTP: Muchas etiquetas por sesión/ticket
CREATE TABLE agent_core.session_tags (
    session_id UUID REFERENCES agent_core.sessions(session_id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES agent_core.cat_tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (session_id, tag_id)
);

CREATE TABLE agent_core.feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES agent_core.messages(message_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating IN (1, -1)),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices Operativos (OLTP)
CREATE INDEX idx_sessions_user ON agent_core.sessions(user_id);
CREATE INDEX idx_sessions_status ON agent_core.sessions(status_id);
CREATE INDEX idx_messages_session ON agent_core.messages(session_id);

-- 2. Esquema de simulación de la empresa fintech (fintech_mock)
-- Catálogos de la Fintech
CREATE TABLE fintech_mock.cat_account_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE fintech_mock.cat_transaction_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

-- Tablas de Simulación Bancaria
CREATE TABLE fintech_mock.accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Vínculo lógico con agent_core.users
    type_id INTEGER NOT NULL REFERENCES fintech_mock.cat_account_types(type_id),
    balance NUMERIC(15,2) DEFAULT 0.00,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fintech_mock.transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES fintech_mock.accounts(account_id),
    category_id INTEGER NOT NULL REFERENCES fintech_mock.cat_transaction_categories(category_id),
    amount NUMERIC(15,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fintech_mock.cards (
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES fintech_mock.accounts(account_id),
    last_four CHAR(4),
    is_active BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE
);


-- 3. Esquema analítico del data warehouse (analytics_warehouse)
-- Catálogos analíticos
CREATE TABLE analytics_warehouse.cat_resolution_types (
    resolution_id SERIAL PRIMARY KEY,
    resolution_name VARCHAR(50) NOT NULL UNIQUE
);

-- Dimensión de tiempo
CREATE TABLE analytics_warehouse.dim_time (
    time_id SERIAL PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    hour INTEGER NOT NULL,
    day_of_week VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN DEFAULT FALSE,
    CONSTRAINT unq_time_hour UNIQUE (full_date, hour)
);

-- Dimensión de lenguaje
CREATE TABLE analytics_warehouse.dim_language (
    language_id SERIAL PRIMARY KEY,
    language_name VARCHAR(50) NOT NULL UNIQUE,
    iso_code CHAR(2) NOT NULL UNIQUE
);

-- Dimensión de intents (Acciones del agente)
CREATE TABLE analytics_warehouse.dim_intent (
    intent_id SERIAL PRIMARY KEY,
    intent_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL
);

-- Dimensión del sentimientos
CREATE TABLE analytics_warehouse.dim_sentiment (
    sentiment_id SERIAL PRIMARY KEY,
    label VARCHAR(50) NOT NULL UNIQUE, -- 'Success', 'Neutral', 'Frustrated'
    sentiment_group VARCHAR(20) NOT NULL -- 'Positive', 'Negative', 'Neutral'
);

-- Dimensión de Etiquetas 
CREATE TABLE analytics_warehouse.dim_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(30)
);

-- Tabla de Hechos Principal: Evaluación cada una de las sesiones/tickets
CREATE TABLE analytics_warehouse.fact_sessions_evaluation (
    fact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL, -- Trazabilidad al identificador original
    dim_time_id INTEGER REFERENCES analytics_warehouse.dim_time(time_id),
    dim_language_id INTEGER REFERENCES analytics_warehouse.dim_language(language_id),
    dim_intent_id INTEGER REFERENCES analytics_warehouse.dim_intent(intent_id),
    dim_sentiment_id INTEGER REFERENCES analytics_warehouse.dim_sentiment(sentiment_id),
    resolution_id INTEGER REFERENCES analytics_warehouse.cat_resolution_types(resolution_id),
    
    -- Métricas consolidadas por el Evaluador
    session_duration_seconds INTEGER,
    total_messages INTEGER DEFAULT 0,
    sentiment_score NUMERIC(3,2),
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    is_abandoned BOOLEAN DEFAULT FALSE
);

-- Tabla Puente OLAP: Relación de muchos a muchos para Filtros Rápidos de Etiquetas
CREATE TABLE analytics_warehouse.fact_tag_assignments (
    fact_id UUID REFERENCES analytics_warehouse.fact_sessions_evaluation(fact_id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES analytics_warehouse.dim_tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (fact_id, tag_id)
);

-- Índices Analíticos (Optimización del Dashboard)
CREATE INDEX idx_fact_resolution ON analytics_warehouse.fact_sessions_evaluation(resolution_id);
CREATE INDEX idx_fact_time ON analytics_warehouse.fact_sessions_evaluation(dim_time_id);
CREATE INDEX idx_fact_language ON analytics_warehouse.fact_sessions_evaluation(dim_language_id);
CREATE INDEX idx_fact_tag_assignment_tag ON analytics_warehouse.fact_tag_assignments(tag_id);

-- 4. Inserción de datos semillas (Seeds)
-- Semillas: agent_core
INSERT INTO agent_core.cat_channels (channel_name) VALUES ('whatsapp'), ('telegram');
INSERT INTO agent_core.cat_roles (role_name) VALUES ('user'), ('assistant'), ('system');
INSERT INTO agent_core.cat_session_statuses (status_id, status_name) 
VALUES (1, 'IN_PROGRESS'), (2, 'FINISHED'), (3, 'EVALUATING'), (4, 'COMPLETED'), (5, 'FAILED');
INSERT INTO agent_core.cat_languages (language_name, iso_code) VALUES ('Español', 'es'), ('Portugués', 'pt');
INSERT INTO agent_core.cat_tags (tag_name, category) VALUES 
('frustracion-detectada', 'ia'), 
('bucle-detectado', 'ia'), 
('abandono-neutro', 'ia'), 
('reclamo-tarjeta', 'negocio');

-- Semillas: fintech_mock
INSERT INTO fintech_mock.cat_account_types (type_name) VALUES ('Caja de Ahorro'), ('Cuenta Corriente'), ('Inversiones');
INSERT INTO fintech_mock.cat_transaction_categories (category_name) VALUES ('Comida'), ('Servicios'), ('Transferencia'), ('Sueldo'), ('Varios');

-- Semillas: analytics_warehouse (Dimensiones y Catálogos analíticos)
INSERT INTO analytics_warehouse.cat_resolution_types (resolution_name) VALUES ('SUCCESS'), ('FRUSTRATION'), ('NEUTRAL');
INSERT INTO analytics_warehouse.dim_language (language_name, iso_code) VALUES ('Español', 'es'), ('Portugués', 'pt');

-- Sincronización inicial de etiquetas operativas en el Warehouse mediante el proceso de ETL inicial
INSERT INTO analytics_warehouse.dim_tags (tag_id, tag_name, category) 
VALUES 
(1, 'frustracion-detectada', 'ia'), 
(2, 'bucle-detectado', 'ia'), 
(3, 'abandono-neutro', 'ia'), 
(4, 'reclamo-tarjeta', 'negocio');

-- Semillas: internal_ops
-- Inyección de permisos granulares
INSERT INTO internal_ops.permissions (codename, name, category) VALUES 
('pipeline:execute', 'Gatillar procesamiento por lotes del corpus mensual', 'Analítica'),
('dashboard:view_metrics', 'Visualizar paneles generales en Streamlit', 'Analítica'),
('dashboard:view_sensitive', 'Visualizar logs de chat completos e identificadores', 'Soporte'),
('security:revoke_token', 'Revocar sesiones activas de usuarios internos', 'Seguridad'),
('workflow:optimize', 'Modificar árboles y grafos de decisión del bot', 'Producto');

-- Inyección de roles
INSERT INTO internal_ops.roles (role_name, description) VALUES 
('Data Analyst', 'Responsable de la ejecución del pipeline y salud del warehouse'),
('Support Lead', 'Auditor de calidad y supervisor de alertas de frustración'),
('Product Manager', 'Estratega de flujos conversacionales y sprints'),
('System Admin', 'Superusuario con acceso perimetral total');

-- Mapeo de permisos a roles (tabla puente)
-- Data Analyst: Ejecuta pipeline y ve métricas
INSERT INTO internal_ops.role_permissions (role_id, permission_id) 
SELECT r.role_id, p.permission_id FROM internal_ops.roles r, internal_ops.permissions p
WHERE r.role_name = 'Data Analyst' AND p.codename IN ('pipeline:execute', 'dashboard:view_metrics');

-- Support Lead: Ve métricas y ve datos sensibles de chats para auditar
INSERT INTO internal_ops.role_permissions (role_id, permission_id) 
SELECT r.role_id, p.permission_id FROM internal_ops.roles r, internal_ops.permissions p
WHERE r.role_name = 'Support Lead' AND p.codename IN ('dashboard:view_metrics', 'dashboard:view_sensitive');

-- Product Manager: Ve métricas y optimiza workflows
INSERT INTO internal_ops.role_permissions (role_id, permission_id) 
SELECT r.role_id, p.permission_id FROM internal_ops.roles r, internal_ops.permissions p
WHERE r.role_name = 'Product Manager' AND p.codename IN ('dashboard:view_metrics', 'workflow:optimize');

-- System Admin: Todo
INSERT INTO internal_ops.role_permissions (role_id, permission_id) 
SELECT (SELECT role_id FROM internal_ops.roles WHERE role_name = 'System Admin'), permission_id 
FROM internal_ops.permissions;