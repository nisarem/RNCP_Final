from flask import Flask, jsonify, abort, request
import pymysql
from getpass import getpass
import json
from flask_swagger_ui import get_swaggerui_blueprint
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config.from_file("flask_config.json", load=json.load)
auth = BasicAuth(app)

password = getpass()

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/openapi.yaml',
)
app.register_blueprint(swaggerui_blueprint)

@app.route("/")
@auth.required
def welcome():
    return """
    <!DOCTYPE html><html lang="en">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Movie Recommender</title>
    <style>body {font-family: Roboto, sans-serif;background-color: #f4f4f4;margin: 0;padding: 0;display: flex;justify-content: center;align-items: center;height: 100vh;}
    .container {text-align: center;}h1 {color: #333;}p {color: #666;}</style></head>
    <body><div class="container"><h1>Welcome to Movie Recommender</h1><p>Explore our database of movies and discover your next cinematic adventure!</p></div></body></html>
    """

@app.route("/movies/<string:movie_id>")
@auth.required
def movie(movie_id):
    db_conn = pymysql.connect(host="localhost", user="root", password=password, database="recommender",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT m.*, r.averageRating AS `average rating`, r.numVotes AS `vote count`,
        GROUP_CONCAT(g.genre) AS genres FROM movies AS m
        JOIN genres AS g ON m.tconst = g.tconst
        JOIN ratings AS r ON m.tconst = r.tconst
        WHERE m.tconst = %s GROUP BY m.tconst, r.averageRating, r.numVotes;""", (movie_id, ))
        movie = cursor.fetchone()
    db_conn.close()

    if movie:
        movie = {k: v for k, v in movie.items() if v is not None}
        return jsonify(movie)
    else:
        abort(404)

MAX_PAGE_SIZE = 25

@app.route("/movies")
@auth.required
def all_movies():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    db_conn = pymysql.connect(host="localhost", user="root", password=password, database="recommender",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT m.*, GROUP_CONCAT(g.genre) AS genres
        FROM Movies AS m
        JOIN genres AS g ON m.tconst = g.tconst
        GROUP BY m.tconst
        ORDER BY m.tconst
        LIMIT %s
        OFFSET %s
        ;""", (page_size,(page-1)*page_size ))
        movies = cursor.fetchall()
    db_conn.close()

    if movies:
        movies = [{k: v for k, v in m.items() if v is not None} for m in movies]
        return movies
    else:
        abort(404)
        
@app.route("/people/<string:people_id>")
@auth.required
def people(people_id):
    db_conn = pymysql.connect(host="localhost", user="root", password=password, database="recommender",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT p.*, GROUP_CONCAT(m.primaryTitle) AS knownForTitles
        FROM people AS p JOIN knownFor AS kf ON p.nconst = kf.nconst
        JOIN movies AS m ON kf.knownForTitle = m.tconst
        WHERE p.nconst = %s GROUP BY p.nconst;""", (people_id, ))
        person = cursor.fetchone()
    db_conn.close()

    if person:
        person = {k: v for k, v in person.items() if v is not None}
        return jsonify(person)
    else:
        abort(404)
        
@app.route("/people")
@auth.required
def all_people():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    db_conn = pymysql.connect(host="localhost", user="root", password=password, database="recommender",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT p.*, GROUP_CONCAT(m.primaryTitle) AS knownForTitles
                          FROM people AS p
                          JOIN knownFor AS kf ON p.nconst = kf.nconst
                          JOIN movies AS m ON kf.knownForTitle = m.tconst
                          GROUP BY p.nconst
                          ORDER BY p.nconst
                          LIMIT %s
                          OFFSET %s;""", (page_size, (page - 1) * page_size))
        people = cursor.fetchall()
    db_conn.close()

    if people:
        people = [{k: v for k, v in person.items() if v is not None} for person in people]
        return jsonify(people)
    else:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
#(base) iremnisa.kilinc@Nisa-Getir Project % flask run --port 8080 --debug
