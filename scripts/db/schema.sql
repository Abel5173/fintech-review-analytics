CREATE TABLE banks (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(100) UNIQUE
);

CREATE TABLE reviews (
    review_id VARCHAR2(100) PRIMARY KEY,
    review_text VARCHAR2(4000),
    sentiment_label VARCHAR2(20),
    sentiment_score NUMBER,
    rating NUMBER,
    review_date DATE,
    bank_id NUMBER,
    CONSTRAINT fk_bank FOREIGN KEY (bank_id) REFERENCES banks(id)
)