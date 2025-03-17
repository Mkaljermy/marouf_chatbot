CREATE TABLE IF NOT EXISTS qa_trivia (
    id SERIAL PRIMARY KEY,
    question TEXT,
    answers TEXT
);

COPY qa_trivia(question, answers)
FROM '/tmp/trivia_full.csv' DELIMITER ',' CSV HEADER;