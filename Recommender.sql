create schema recommender;
use recommender;

ALTER TABLE movies DROP COLUMN genres;

ALTER TABLE people DROP COLUMN knownForTitles,
DROP COLUMN primaryProfession;

ALTER TABLE people
MODIFY COLUMN nconst VARCHAR(255),
ADD PRIMARY KEY (nconst);

ALTER TABLE movies
MODIFY COLUMN tconst VARCHAR(255),
ADD PRIMARY KEY (tconst);

ALTER TABLE ratings
MODIFY COLUMN tconst VARCHAR(255),
ADD CONSTRAINT fk_ratings_movies FOREIGN KEY (tconst) REFERENCES movies(tconst),
ADD PRIMARY KEY (tconst);

ALTER TABLE relations
ADD COLUMN credits_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
ADD PRIMARY KEY (credits_id);

ALTER TABLE relations
MODIFY COLUMN credits_id VARCHAR(10);

UPDATE relations
SET credits_id = CONCAT('cr', credits_id + 1000000);

ALTER TABLE relations
MODIFY COLUMN tconst VARCHAR(255),
ADD CONSTRAINT fk_relations_tconst FOREIGN KEY (tconst) REFERENCES movies(tconst),
MODIFY COLUMN nconst VARCHAR(255),
ADD CONSTRAINT fk_relations_nconst FOREIGN KEY (nconst) REFERENCES people(nconst);

ALTER TABLE genres
MODIFY COLUMN tconst VARCHAR(255),
ADD CONSTRAINT fk_genres_movies FOREIGN KEY (tconst) REFERENCES movies(tconst);

ALTER TABLE knownFor
MODIFY COLUMN knownForTitle VARCHAR(255),
ADD CONSTRAINT fk_knownFor_movies FOREIGN KEY (knownForTitle) REFERENCES movies(tconst),
MODIFY COLUMN nconst VARCHAR(255),
ADD CONSTRAINT fk_knownFor_people FOREIGN KEY (nconst) REFERENCES people(nconst);

SELECT p.primaryName, COUNT(r.tconst) AS movie_count
FROM relations AS r
JOIN PEOPLE AS p ON r.nconst = p.nconst
WHERE r.profession IN ('actor')
GROUP BY p.primaryName
ORDER BY movie_count DESC
LIMIT 20;

SELECT p.primaryName, COUNT(r.tconst)
 AS movie_count
FROM relations AS r
JOIN PEOPLE AS p ON r.nconst = p.nconst
WHERE r.profession IN ('actress')
GROUP BY p.primaryName
ORDER BY movie_count DESC
LIMIT 10;

SELECT p.primaryName, COUNT(r.tconst) 
AS movie_count
FROM relations AS r
JOIN PEOPLE AS p ON r.nconst = p.nconst
WHERE r.profession IN ('director')
GROUP BY p.primaryName
ORDER BY movie_count DESC
LIMIT 10;

SELECT g.genre, COUNT(m.tconst) AS movie_count
FROM movies AS m
JOIN genres AS g USING (tconst)
GROUP BY g.genre
ORDER BY movie_count DESC
LIMIT 10;

SELECT p.primaryName, COUNT(r.tconst) AS movie_count
FROM relations AS r
JOIN PEOPLE AS p USING (nconst)
WHERE r.profession IN ('writers')
GROUP BY p.primaryName
ORDER BY movie_count DESC
LIMIT 20;
# Top 10 most popular movies 
# by weighted average ratings
SELECT m.originalTitle, r.averageRating, 
r.numVotes FROM movies AS m
LEFT JOIN ratings AS r USING (tconst)
ORDER BY r.averageRating*r.numVotes DESC
LIMIT 10;

SELECT m.*, GROUP_CONCAT(g.genre) AS genres
FROM Movies AS m
JOIN genres AS g ON m.tconst = g.tconst
WHERE m.tconst = 'tt0029284'
GROUP BY m.tconst;

SELECT * FROM people limit 10;

SELECT * FROM relations limit 10;
SELECT p.*, GROUP_CONCAT(m.primaryTitle) AS knownForTitles
FROM people AS p
JOIN knownFor AS kf ON p.nconst = kf.nconst
JOIN movies AS m ON kf.knownForTitle = m.tconst
WHERE p.nconst = 'nm0000138'
GROUP BY p.nconst;

