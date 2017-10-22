DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
  id            SERIAL PRIMARY KEY,
  password      VARCHAR(255),
  email         VARCHAR(100) UNIQUE,
  name          VARCHAR(200),
  locale        VARCHAR(6),
  confirmed_at  TIMESTAMP DEFAULT NULL,
  deleted       BOOLEAN   DEFAULT FALSE,
  is_teacher    BOOLEAN   DEFAULT FALSE,
  is_staff      BOOLEAN   DEFAULT FALSE
);
CREATE INDEX user_email_index ON users USING btree (email);
INSERT INTO users (
  email, name, is_teacher, is_staff
) VALUES
  ('admin@tester.com', 'LightMdb Admin', False, TRUE),
  ('teacher@tester.com', 'Mr. Teacher', TRUE, False),
  ('tonystark@tester.com', 'Tony Stark', FALSE, FALSE),
  ('elonmusk@tester.com', 'Elon Musk', FALSE, FALSE),
  ('mjolnir@tester.com', 'Thor Odinson', FALSE, FALSE),
  ('bruce@tester.com', 'Bruce Banner', TRUE, FALSE);

DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS event_categories;
CREATE TABLE event_categories (
  id        SERIAL PRIMARY KEY,
  slug      VARCHAR(200) UNIQUE,
  name      VARCHAR(200) UNIQUE,
  tr_name   VARCHAR(200) DEFAULT NULL,
  ru_name   VARCHAR(200) DEFAULT NULL
);
CREATE INDEX category_slug_index ON event_categories USING BTREE (slug);
INSERT INTO event_categories (
  slug, name, tr_name, ru_name
) VALUES
  ('academic-calendar', 'Academic Calendar', 'Akademik Takvim', 'Академический Календарь'),
  ('cs-news', 'Computer and Informatics: Announcements', 'Bilgisayar Bilişim: Duyurular', 'Компьютерная Инженерия: Объявления'),
  ('cs-events', 'Computer and Informatics: Events', 'Bilgisayar Bilişim: Etkinlikler', 'Компьютерная Инженерия: Мероприятия');

CREATE TABLE events (
  id        SERIAL PRIMARY KEY,
  summary   VARCHAR(255) NOT NULL,
  date      TIMESTAMP DEFAULT NULL,
  end_date  TIMESTAMP DEFAULT NULL,
  category  INTEGER REFERENCES event_categories ON DELETE CASCADE,
  url       VARCHAR(255) DEFAULT NULL
);
