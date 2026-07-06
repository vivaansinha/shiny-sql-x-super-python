import pymysql
from pymysql.cursors import DictCursor

from flask import Flask, render_template, render_template_string, redirect, url_for, request, flash, abort


app = Flask(__name__)

# For LOCAL learning only.
# Change this to a long random value later.
app.secret_key = "my-local-flask-secret-key"


def get_connection():
    return pymysql.connect(
        host="localhost",
        user='vivaan',
        password='happybirthday',
        database='world',
        cursorclass=DictCursor,
        autocommit=False
    )


@app.route("/myapp")
def index():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    name,
                    rating,
                    price,
                    downloadable_in,
                    device_supported
                FROM video_game
                ORDER BY id DESC
            """)

            games = cursor.fetchall()

        return render_template("index.html", games=games)

    finally:
        connection.close()


@app.route("/add", methods=["POST"])
def add_game():
    name = request.form["name"].strip()
    rating = request.form["rating"]
    price = request.form["price"]
    downloadable_in = request.form["downloadable_in"].strip()
    device_supported = request.form["device_supported"].strip()

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO video_game
                (name, rating, price, downloadable_in, device_supported)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                rating,
                price,
                downloadable_in,
                device_supported
            ))

        connection.commit()
        flash("Game added successfully.")

    except pymysql.MySQLError as error:
        connection.rollback()
        flash(f"Could not add the game: {error}")

    finally:
        connection.close()

    return redirect(url_for("index"))


@app.route("/myapp/games/<int:game_id>/edit")
def edit_game_page(game_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    name,
                    rating,
                    price,
                    downloadable_in,
                    device_supported
                FROM video_game
                WHERE id = %s
            """, (game_id,))

            game = cursor.fetchone()

        if game is None:
            abort(404)

        return render_template("edit_game.html", game=game)

    finally:
        connection.close()


@app.route("/games/<int:game_id>/update", methods=["POST"])
def update_game(game_id):
    name = request.form["name"].strip()
    rating = request.form["rating"]
    price = request.form["price"]
    downloadable_in = request.form["downloadable_in"].strip()
    device_supported = request.form["device_supported"].strip()

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE video_game
                SET
                    name = %s,
                    rating = %s,
                    price = %s,
                    downloadable_in = %s,
                    device_supported = %s
                WHERE id = %s
            """, (
                name,
                rating,
                price,
                downloadable_in,
                device_supported,
                game_id
            ))

            if cursor.rowcount == 0:
                abort(404)

        connection.commit()
        flash("Game updated successfully.")

    except pymysql.MySQLError as error:
        connection.rollback()
        flash(f"Could not update the game: {error}")

    finally:
        connection.close()

    return redirect(url_for("index"))


@app.route("/games/<int:game_id>/delete", methods=["POST"])
def delete_game(game_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM video_game
                WHERE id = %s
            """, (game_id,))

            if cursor.rowcount == 0:
                abort(404)

        connection.commit()
        flash("Game deleted successfully.")

    except pymysql.MySQLError as error:
        connection.rollback()
        flash(f"Could not delete the game: {error}")

    finally:
        connection.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)