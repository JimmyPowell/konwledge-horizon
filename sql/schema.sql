CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL
);

-- Indexes for performance
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

-- Conversations (multi-turn chat)
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(36) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    title VARCHAR(200) NULL,
    kb_id INT NULL,
    model VARCHAR(128) NULL,
    temperature VARCHAR(16) NULL,
    first_message_at TIMESTAMP NULL DEFAULT NULL,
    last_message_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    INDEX idx_conversations_user (user_id),
    INDEX idx_conversations_kb (kb_id),
    INDEX idx_conversations_last_msg (last_message_at),
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Conversation to multiple KBs mapping
CREATE TABLE IF NOT EXISTS conversation_kbs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    kb_id INT NOT NULL,
    INDEX idx_convkbs_conv (conversation_id),
    INDEX idx_convkbs_kb (kb_id)
);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role VARCHAR(16) NOT NULL,
    content LONGTEXT NULL,
    tokens_prompt INT NULL,
    tokens_completion INT NULL,
    latency_ms INT NULL,
    model VARCHAR(128) NULL,
    error TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_conv (conversation_id),
    INDEX idx_messages_created (created_at),
    CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Knowledge Base metadata (only metadata in MySQL; actual vectors in ChromaDB)
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    owner_id INT NOT NULL,
    visibility VARCHAR(16) NOT NULL DEFAULT 'private', -- private | org | public
    is_active BOOLEAN DEFAULT TRUE,

    chroma_collection VARCHAR(128) NOT NULL,
    embedding_model VARCHAR(128) NULL,
    reranker_model VARCHAR(128) NULL,
    use_reranker BOOLEAN DEFAULT FALSE,

    doc_count INT NOT NULL DEFAULT 0,
    total_size_bytes BIGINT NOT NULL DEFAULT 0,
    last_indexed_at TIMESTAMP NULL DEFAULT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,

    UNIQUE KEY uq_kb_collection (chroma_collection),
    UNIQUE KEY uq_kb_name_owner (owner_id, name),
    INDEX idx_kb_owner (owner_id),
    INDEX idx_kb_visibility (visibility),
    INDEX idx_kb_deleted_at (deleted_at),
    CONSTRAINT fk_kb_owner FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Knowledge documents metadata (raw text and vectors live in ChromaDB)
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(36) NOT NULL UNIQUE,
    kb_id INT NOT NULL,

    filename VARCHAR(255) NOT NULL,
    file_ext VARCHAR(10) NULL,
    mime_type VARCHAR(100) NULL,
    storage_uri VARCHAR(255) NULL,
    size_bytes BIGINT NULL,
    page_count INT NULL,

    status VARCHAR(16) NOT NULL DEFAULT 'uploaded', -- uploaded | processing | processed | failed
    error TEXT NULL,
    processed_at TIMESTAMP NULL DEFAULT NULL,

    vector_source VARCHAR(255) NOT NULL,
    chunk_count INT NOT NULL DEFAULT 0,
    embedding_model VARCHAR(128) NULL,
    ingest_params TEXT NULL,

    uploaded_by INT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,

    UNIQUE KEY uq_doc_vector_source (kb_id, vector_source),
    INDEX idx_kd_kb (kb_id),
    INDEX idx_kd_status (status),
    INDEX idx_kd_deleted_at (deleted_at),
    INDEX idx_kd_uploader (uploaded_by),

    CONSTRAINT fk_kd_kb FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id),
    CONSTRAINT fk_kd_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Optional: KB sharing per user
CREATE TABLE IF NOT EXISTS kb_shared_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kb_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'viewer', -- viewer | editor
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_kb_share (kb_id, user_id),
    INDEX idx_kb_share_user (user_id),

    CONSTRAINT fk_kb_share_kb FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id),
    CONSTRAINT fk_kb_share_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Optional hardening: prevent duplicate KB mapping within a conversation
-- ALTER TABLE conversation_kbs
--   ADD CONSTRAINT uq_conv_kb UNIQUE (conversation_id, kb_id);

-- Optional FK for conversation_kbs
-- ALTER TABLE conversation_kbs
--   ADD CONSTRAINT fk_convkbs_kb FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id);
