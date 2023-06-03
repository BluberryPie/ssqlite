CREATE TABLE X (id INTEGER PRIMARY KEY, name VARCHAR(255)); -- target
INSERT INTO X(id, name) VALUES(1, 'Alice');
INSERT INTO X(id, name) VALUES(2, 'Bob');
UPDATE X SET name='April' WHERE id=1;
UPDATE X SET name='Aaron' WHERE id=1;
DELETE FROM X WHERE name='Aaron';
INSERT INTO X(id, name) VALUES(3, 'Charles');
INSERT INTO X(id, name) VALUES(4, 'David');
UPDATE X SET name='Brendan' WHERE id=2;
UPDATE X SET name='Danielle' WHERE name='David';
INSERT INTO X(id, name) VALUES(5, 'Eve');
INSERT INTO X(id, name) VALUES(6, 'Francis');
DELETE FROM X WHERE id=4;
INSERT INTO X(id, name) VALUES(7, 'Gerrard');