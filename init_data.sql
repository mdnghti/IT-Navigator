-- Insert specialties
INSERT INTO specialties (code, name, description) VALUES
('F1', 'Прикладна математика', 'Математичне моделювання та обчислювальна математика'),
('F2', 'Інженерія програмного забезпечення', 'Розробка та підтримка програмного забезпечення'),
('F3', 'Комп''ютерні науки', 'Алгоритми, структури даних та теоретичні основи'),
('F4', 'Системний аналіз та Data Science', 'Аналіз даних та машинне навчання'),
('F5', 'Кібербезпека', 'Захист інформації та безпека систем'),
('F6', 'Інформаційні системи та технології', 'Проектування та розробка інформаційних систем'),
('F7', 'Комп''ютерна інженерія', 'Апаратне забезпечення та вбудовані системи')
ON CONFLICT (code) DO NOTHING;

-- Insert general test
INSERT INTO tests (title, test_type, specialty_id) VALUES
('Загальний тест профорієнтації', 'general', NULL)
ON CONFLICT DO NOTHING;

-- Insert admin user (password: admin123)
INSERT INTO users (email, hashed_password, full_name, is_admin) VALUES
('admin@itnav.online', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYdKvJ4B9Ia', 'Admin', true)
ON CONFLICT (email) DO NOTHING;
