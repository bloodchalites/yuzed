-- Создаем основные БД
CREATE DATABASE yuzedo_main;
CREATE DATABASE users_db;
CREATE DATABASE documents_db;
CREATE DATABASE payments_db;

-- Даем права пользователю admin
GRANT ALL PRIVILEGES ON DATABASE yuzedo_main TO admin;
GRANT ALL PRIVILEGES ON DATABASE users_db TO admin;
GRANT ALL PRIVILEGES ON DATABASE documents_db TO admin;
GRANT ALL PRIVILEGES ON DATABASE payments_db TO admin;

-- Простая тестовая таблица
\c yuzedo_main;
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test_table (name) VALUES ('Система ЮЗЭДО запущена');
