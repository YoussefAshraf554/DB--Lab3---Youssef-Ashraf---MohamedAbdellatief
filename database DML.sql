USE library;

INSERT INTO author (author_id, name, country) VALUES
(1, 'colleen Hoover', 'United States'),
(2, 'Amr Abdelhamid', 'Egypt'),
(3, 'Agatha Christie', 'United Kingdom')
;

INSERT INTO book (book_id, title, price, author_id) VALUES
(1, 'The land of Zikola', 14.99, 2),
(2, 'It Starts With Us', 11.50, 1),
(3, 'Murder Is Easy', 12.00, 3),
(4, 'Amarita -land of zicola 2', 9.75, 2),
(5, 'it Ends With Us', 13.25, 1),
(6, 'Murder On Orient Express', 10.99, 3)
;
