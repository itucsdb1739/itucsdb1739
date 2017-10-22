DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  password     VARCHAR(255),
  email        VARCHAR(100) UNIQUE,
  name         VARCHAR(200),
  locale       VARCHAR(6),
  confirmed_at timestamp DEFAULT NULL,
  deleted      BOOLEAN   DEFAULT FALSE,
  is_teacher   BOOLEAN   DEFAULT FALSE,
  is_staff     BOOLEAN   DEFAULT FALSE
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
