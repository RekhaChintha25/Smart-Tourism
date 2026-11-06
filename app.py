import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import psycopg2
from psycopg2.extras import RealDictCursor

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)

app.secret_key = "smart_tourism_secret_key"


# ==========================================
# MYSQL DATABASE CONNECTION
# ==========================================

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not configured")

    connection = psycopg2.connect(database_url)

    return connection


# ==========================================
# TOURIST PLACES DATA
# ==========================================

tourist_places = [

    {
        "id": 1,
        "name": "Araku Valley",
        "location": "Andhra Pradesh",
        "category": "Nature",
        "description": "Beautiful hills, waterfalls and coffee plantations.",
        "image": "araku.jpg",
        "about": "Araku Valley is a beautiful hill destination known for its green valleys, coffee plantations, waterfalls and scenic mountain views.",
        "best_time": "October to March",
        "attractions": [
            "Borra Caves",
            "Katiki Waterfalls",
            "Coffee Plantations",
            "Padmapuram Gardens"
        ],
        "travel_info": "Araku Valley can be reached by road from Visakhapatnam. Train travel through the scenic hills is also a popular option."
    },

    {
        "id": 2,
        "name": "Hampi",
        "location": "Karnataka",
        "category": "Historical",
        "description": "Explore ancient temples and beautiful historical monuments.",
        "image": "hampi.jpg",
        "about": "Hampi is a historical destination famous for ancient temples, stone monuments and the remains of the Vijayanagara Empire.",
        "best_time": "October to February",
        "attractions": [
            "Virupaksha Temple",
            "Stone Chariot",
            "Vijaya Vittala Temple",
            "Hampi Bazaar"
        ],
        "travel_info": "Hampi can be reached by road and rail through nearby towns such as Hospet."
    },

    {
        "id": 3,
        "name": "Munnar",
        "location": "Kerala",
        "category": "Nature",
        "description": "Enjoy green tea plantations and beautiful mountain views.",
        "image": "munnar.jpg",
        "about": "Munnar is a popular hill station known for tea plantations, misty mountains, green landscapes and pleasant weather.",
        "best_time": "September to March",
        "attractions": [
            "Eravikulam National Park",
            "Mattupetty Dam",
            "Tea Museum",
            "Echo Point"
        ],
        "travel_info": "Munnar can be reached by road from Kochi and other nearby towns. The nearest major railway station is Aluva."
    },

    {
        "id": 4,
        "name": "Jaipur",
        "location": "Rajasthan",
        "category": "Historical",
        "description": "Discover royal palaces, forts and colorful markets.",
        "image": "jaipur.jpg",
        "about": "Jaipur is known for its royal architecture, historic forts, colorful markets and traditional Rajasthani culture.",
        "best_time": "October to March",
        "attractions": [
            "Hawa Mahal",
            "Amber Fort",
            "City Palace",
            "Jantar Mantar"
        ],
        "travel_info": "Jaipur is accessible by air, rail and road. Jaipur International Airport connects the city with several destinations."
    },

    {
        "id": 5,
        "name": "Taj Mahal",
        "location": "Agra, Uttar Pradesh",
        "category": "Historical",
        "description": "Explore the beautiful marble monument and its amazing architecture.",
        "image": "tajmahal.jpg",
        "about": "The Taj Mahal is a famous white marble monument in Agra, known for its beautiful architecture and historical significance.",
        "best_time": "October to March",
        "attractions": [
            "Taj Mahal",
            "Agra Fort",
            "Mehtab Bagh",
            "Fatehpur Sikri"
        ],
        "travel_info": "Agra can be reached by train, road and air through nearby airports. The Taj Mahal is located in Agra city."
    },

    {
        "id": 6,
        "name": "Ajanta Caves",
        "location": "Maharashtra",
        "category": "Historical",
        "description": "Discover ancient Buddhist caves and beautiful paintings.",
        "image": "ajanta.jpg",
        "about": "Ajanta Caves are ancient Buddhist rock-cut caves famous for their sculptures, paintings and historical heritage.",
        "best_time": "October to March",
        "attractions": [
            "Ajanta Cave 1",
            "Ajanta Cave 2",
            "Ancient Buddhist Paintings",
            "Rock-cut Sculptures"
        ],
        "travel_info": "Ajanta Caves can be reached by road from nearby cities. Aurangabad is a common starting point for visitors."
    },

    {
        "id": 7,
        "name": "Varanasi",
        "location": "Uttar Pradesh",
        "category": "Spiritual",
        "description": "Experience the sacred ghats and beautiful Ganga river views.",
        "image": "varanasi.jpg",
        "about": "Varanasi is a historic spiritual city known for its sacred riverfront, temples, traditional culture and Ganga Aarti.",
        "best_time": "October to March",
        "attractions": [
            "Dashashwamedh Ghat",
            "Kashi Vishwanath Temple",
            "Assi Ghat",
            "Sarnath"
        ],
        "travel_info": "Varanasi can be reached by air, rail and road. The city has an airport and major railway connections."
    }

]


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# TOURIST PLACES PAGE
# ==========================================

@app.route("/places")
def places():

    return render_template(
        "places.html",
        tourist_places=tourist_places
    )


# ==========================================
# TOURIST PLACE DETAILS
# ==========================================

@app.route("/place/<int:place_id>")
def place_details(place_id):

    selected_place = None

    for place in tourist_places:

        if place["id"] == place_id:

            selected_place = place

            break

    if selected_place is None:

        return "Tourist place not found", 404

    return render_template(
        "place_details.html",
        place=selected_place
    )
def get_db_connection

# ==========================================
# REGISTER PAGE
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not username or not email or not password:

            flash("Please fill all required fields.")

            return redirect(url_for("register"))

        if len(password) < 8:

            flash("Password must contain at least 8 characters.")

            return redirect(url_for("register"))

        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect(url_for("register"))

        connection = None

        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash("Email already registered.")

                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            cursor.execute(

                """
                INSERT INTO users
                (username, email, password)
                VALUES (%s, %s, %s)
                """,

                (
                    username,
                    email,
                    hashed_password
                )

            )

            connection.commit()

            flash("Registration successful. Please login.")

            return redirect(url_for("login"))

        except psycopg2.Error as error:

            print("Database Error:", error)

            flash("Database error. Please try again.")

            return redirect(url_for("register"))

        finally:

            if cursor is not None:

                cursor.close()

            if connection is not None:

                connection.close()

    return render_template("register.html")


# ==========================================
# LOGIN PAGE
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")

        if not email or not password:

            flash("Please enter email and password.")

            return redirect(url_for("login"))

        connection = None

        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(cursor_factory=RealDictCursor)

            cursor.execute(

                """
                SELECT id, username, email, password
                FROM users
                WHERE email = %s
                """,

                (email,)

            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"],
                password
            ):

                session.clear()

                session["user_id"] = user["id"]

                session["username"] = user["username"]

                flash("Login successful.")

                return redirect(url_for("home"))

            else:

                flash("Invalid email or password.")

                return redirect(url_for("login"))

        except psycopg2.Error as error:

            print("Database Error:", error)

            flash("Database error. Please try again.")

            return redirect(url_for("login"))

        finally:

            if cursor is not None:

                cursor.close()

            if connection is not None:

                connection.close()

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have logged out.")

    return redirect(url_for("home"))


# ==========================================
# ADD FAVORITE
# ==========================================

@app.route("/add_favorite/<int:place_id>", methods=["POST"])
def add_favorite(place_id):

    if "user_id" not in session:

        flash("Please login to add favorites.")

        return redirect(url_for("login"))

    place_exists = any(
        place["id"] == place_id
        for place in tourist_places
    )

    if not place_exists:

        flash("Tourist place not found.")

        return redirect(url_for("places"))

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(

            """
            SELECT id
            FROM favorites
            WHERE user_id = %s AND place_id = %s
            """,

            (
                session["user_id"],
                place_id
            )

        )

        existing_favorite = cursor.fetchone()

        if existing_favorite:

            flash("This place is already in your favorites.")

            return redirect(url_for("places"))

        cursor.execute(

            """
            INSERT INTO favorites
            (user_id, place_id)
            VALUES (%s, %s)
            """,

            (
                session["user_id"],
                place_id
            )

        )

        connection.commit()

        flash("Place added to favorites successfully.")

        return redirect(url_for("places"))

    except psycopg2.Error as error:

        print("Database Error:", error)

        flash("Unable to add favorite. Please try again.")

        return redirect(url_for("places"))

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# MY FAVORITES PAGE
# ==========================================

@app.route("/favorites")
def favorites():

    if "user_id" not in session:

        flash("Please login to view your favorites.")

        return redirect(url_for("login"))

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(

            """
            SELECT place_id
            FROM favorites
            WHERE user_id = %s
            """,

            (session["user_id"],)

        )

        favorite_rows = cursor.fetchall()

        favorite_ids = [
            row[0]
            for row in favorite_rows
        ]

        favorite_places = [

            place

            for place in tourist_places

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

    app.run(debug=True)