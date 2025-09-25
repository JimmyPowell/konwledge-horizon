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
