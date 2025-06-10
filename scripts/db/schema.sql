CREATE TABLE banks (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(100) UNIQUE
);

CREATE TABLE reviews (
    review_id VARCHAR2(100) PRIMARY KEY,
    review_text VARCHAR2(4000),
    rating NUMBER,
    review_date DATE,
    bank_name VARCHAR2(100),
    source VARCHAR2(100),
    processed_text VARCHAR2(4000),
    identified_theme VARCHAR2(200)
);