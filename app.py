
            if place["id"] in favorite_ids

        ]

        return render_template(
            "favorites.html",
            favorite_places=favorite_places
        )

    except psycopg2.Error as error:

        print("Database Error:", error)

        flash("Unable to load favorites.")

        return redirect(url_for("places"))

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# REMOVE FAVORITE
# ==========================================

@app.route("/remove_favorite/<int:place_id>", methods=["POST"])
def remove_favorite(place_id):

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(url_for("login"))

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(

            """
            DELETE FROM favorites
            WHERE user_id = %s
            AND place_id = %s
            """,

            (
                session["user_id"],
                place_id
            )

        )

        connection.commit()

        if cursor.rowcount > 0:

            flash("Favorite removed successfully.")

        else:

            flash("Favorite not found.")

        return redirect(url_for("favorites"))

    except psycopg2.Error as error:

        print("Database Error:", error)

        flash("Unable to remove favorite.")

        return redirect(url_for("favorites"))

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
