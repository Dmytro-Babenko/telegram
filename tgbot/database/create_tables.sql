CREATE TABLE clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    first_name VARCHAR(10) NOT NULL,
    last_name VARCHAR(10),
    user_name VARCHAR(10),
    phone_number VARCHAR(15),
    CONSTRAINT un_telegram_id UNIQUE (telegram_id)
);

CREATE TABLE orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    type_id VARCHAR(10) NOT NULL,
    subject_id VARCHAR(20) NOT NULL,
    order_date DATETIME NOT NULL,
    univ_id VARCHAR(30),
    theme_or_variant VARCHAR(50),
    FOREIGN KEY (client_id) REFERENCES clients (id)
        ON UPDATE CASCADE,
    FOREIGN KEY (type_id) REFERENCES types (id)
        ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
        ON UPDATE CASCADE, 
    FOREIGN KEY (univ_id) REFERENCES universities (id)
        ON UPDATE CASCADE 
);

CREATE TABLE universities(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    univ_name VARCHAR(30),
    CONSTRAINT un_univ_name UNIQUE (univ_name)
);

CREATE TABLE types(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typy_name VARCHAR(20),
    kind_name CHAR(2)
);

CREATE TABLE subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sub_name VARCHAR(50)
)

