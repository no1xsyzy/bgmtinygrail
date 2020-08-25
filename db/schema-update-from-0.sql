-- bangumi
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    friendly_name VARCHAR(64) NOT NULL UNIQUE,
    cfduid VARCHAR(43) NOT NULL,
    chii_auth VARCHAR(128) NOT NULL,
    gh CHAR(8) NOT NULL,
    ua VARCHAR(128) NOT NULL,
    tinygrail_identity VARCHAR(1000) NOT NULL
);

-- revision
DROP TABLE IF EXISTS db_rev;
CREATE TABLE db_rev (rev integer NOT NULL);
INSERT INTO db_rev (rev)
VALUES
  (1);
