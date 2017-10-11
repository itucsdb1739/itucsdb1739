DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  username     VARCHAR(50) UNIQUE,
  password     VARCHAR(150),
  email        VARCHAR(100) UNIQUE,
  name         VARCHAR(200),
  confirmed_at timestamp DEFAULT NULL,
  deleted      BOOLEAN   DEFAULT FALSE,
  is_staff     BOOLEAN   DEFAULT FALSE
);
CREATE INDEX user_username_index ON users USING btree (username);
CREATE INDEX user_email_index ON users USING btree (email);
INSERT INTO users (
  username, email, name, is_staff
) VALUES
  ('admin', 'admin@tester.com', 'LightMdb Admin', TRUE),
  ('tonystark', 'tonystark@tester.com', 'Tony Stark', FALSE),
  ('elonmusk', 'elonmusk@tester.com', 'Elon Musk', FALSE),
  ('thor', 'mjolnir@tester.com', 'Thor Odinson', FALSE);
