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

from psycopg2 import Error

from psycopg2.extras import RealDictCursor

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart_tourism_secret_key"
)


# ==========================================
# POSTGRESQL DATABASE CONNECTION
# ==========================================

def get_db_connection():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not configured.")

    return psycopg2.connect(
        database_url,
        sslmode="require"
    )


def init_db():
    """Create the required tables if they do not already exist."""
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                place_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, place_id)
            )
        """)

        connection.commit()
        print("PostgreSQL tables are ready.")

    except Error as error:
        if connection is not None:
            connection.rollback()
        print("Database initialization error:", error)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


try:
    init_db()
except Exception as startup_error:
    print("Database startup check failed:", startup_error)


# ==========================================
# TOURIST PLACES DATA
# ==========================================

tourist_places = [

    {
        "id": 1,

        "name": "Araku Valley",

        "location": "Andhra Pradesh",

        "category": "Nature",

        "description": (
            "Beautiful hills, waterfalls "
            "and coffee plantations."
        ),

        "image": "araku.jpg",

        "about": (
            "Araku Valley is a beautiful "
            "hill destination known for its "
            "green valleys, coffee plantations, "
            "waterfalls and scenic mountain views."
        ),

        "best_time": "October to March",

        "attractions": [

            "Borra Caves",

            "Katiki Waterfalls",

            "Coffee Plantations",

            "Padmapuram Gardens"

        ],

        "travel_info": (
            "Araku Valley can be reached "
            "by road from Visakhapatnam. "
            "Train travel through the scenic "
            "hills is also a popular option."
        )

    },

    {
        "id": 2,

        "name": "Hampi",

        "location": "Karnataka",

        "category": "Historical",

        "description": (
            "Explore ancient temples and "
            "beautiful historical monuments."
        ),

        "image": "hampi.jpg",

        "about": (
            "Hampi is a historical destination "
            "famous for ancient temples, stone "
            "monuments and the remains of "
            "the Vijayanagara Empire."
        ),

        "best_time": "October to February",

        "attractions": [

            "Virupaksha Temple",

            "Stone Chariot",

            "Vijaya Vittala Temple",

            "Hampi Bazaar"

        ],

        "travel_info": (
            "Hampi can be reached by road "
            "and rail through nearby towns "
            "such as Hospet."
        )

    },

    {
        "id": 3,

        "name": "Munnar",

        "location": "Kerala",

        "category": "Nature",

        "description": (
            "Enjoy green tea plantations "
            "and beautiful mountain views."
        ),

        "image": "munnar.jpg",

        "about": (
            "Munnar is a popular hill station "
            "known for tea plantations, misty "
            "mountains, green landscapes "
            "and pleasant weather."
        ),

        "best_time": "September to March",

        "attractions": [

            "Eravikulam National Park",

            "Mattupetty Dam",

            "Tea Museum",

            "Echo Point"

        ],

        "travel_info": (
            "Munnar can be reached by road "
            "from Kochi and other nearby towns. "
            "The nearest major railway station "
            "is Aluva."
        )

    }

]


# ==========================================
# HELPER FUNCTION
# FIND TOURIST PLACE
# ==========================================

def get_place_by_id(place_id):

    for place in tourist_places:

        if place["id"] == place_id:

            return place

    return None


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
@app.route("/home")

def home():

    return render_template(

        "index.html",

        tourist_places=tourist_places

    )


# ==========================================
# REGISTER PAGE
# ==========================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)

def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # VALIDATION

        if not username or not email or not password:

            flash(
                "Please fill all required fields."
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters."
            )

            return redirect(
                url_for("register")
            )

        connection = None

        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            # CHECK EXISTING EMAIL

            cursor.execute(

                """
                SELECT id
                FROM users
                WHERE email = %s
                """,

                (email,)

            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "Email already registered."
                )

                return redirect(
                    url_for("register")
                )

            # HASH PASSWORD

            hashed_password = generate_password_hash(
                password
            )

            # INSERT USER

            cursor.execute(

                """
                INSERT INTO users
                (
                    username,
                    email,
                    password
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,

                (
                    username,
                    email,
                    hashed_password
                )

            )

            connection.commit()

            flash(
                "Registration successful. Please login."
            )

            return redirect(
                url_for("login")
            )

        except Error as error:

            if connection is not None:

                connection.rollback()

            print(
                "Database Error:",
                error
            )

            flash(
                "Unable to register. Please try again."
            )

            return redirect(
                url_for("register")
            )

        finally:

            if cursor is not None:

                cursor.close()

            if connection is not None:

                connection.close()

    return render_template(
        "register.html"
    )


# ==========================================
# LOGIN PAGE
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)

def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter email and password."
            )

            return redirect(
                url_for("login")
            )

        connection = None

        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                cursor_factory=RealDictCursor
            )

            # GET USER

            cursor.execute(

                """
                SELECT
                    id,
                    username,
                    email,
                    password
                FROM users
                WHERE email = %s
                """,

                (email,)

            )

            user = cursor.fetchone()

            # CHECK PASSWORD

            if user and check_password_hash(

                user["password"],

                password

            ):

                session.clear()

                session["user_id"] = user["id"]

                session["username"] = user["username"]

                flash(
                    "Login successful."
                )

                return redirect(
                    url_for("home")
                )

            else:

                flash(
                    "Invalid email or password."
                )

                return redirect(
                    url_for("login")
                )

        except Error as error:

            print(
                "Database Error:",
                error
            )

            flash(
                "Database error. Please try again."
            )

            return redirect(
                url_for("login")
            )

        finally:

            if cursor is not None:

                cursor.close()

            if connection is not None:

                connection.close()

    return render_template(
        "login.html"
    )


# ==========================================
# TOURIST PLACES PAGE
# ==========================================

@app.route("/places")

def places():

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    category = request.args.get(
        "category",
        ""
    ).strip()

    filtered_places = tourist_places

    # SEARCH FILTER

    if search:

        filtered_places = [

            place

            for place in filtered_places

            if search in place["name"].lower()

            or search in place["location"].lower()

            or search in place["category"].lower()

        ]

    # CATEGORY FILTER

    if category:

        filtered_places = [

            place

            for place in filtered_places

            if place["category"] == category

        ]

    return render_template(

        "places.html",

        tourist_places=filtered_places,

        search=search,

        category=category

    )


# ==========================================
# PLACE DETAILS PAGE
# ==========================================

@app.route(
    "/place/<int:place_id>"
)

def place_details(place_id):

    place = get_place_by_id(
        place_id
    )

    if place is None:

        flash(
            "Tourist place not found."
        )

        return redirect(
            url_for("places")
        )

    return render_template(

        "place_details.html",

        place=place

    )


# ==========================================
# ADD FAVORITE
# ==========================================

@app.route(
    "/add_favorite/<int:place_id>",
    methods=["POST"]
)

def add_favorite(place_id):

    # LOGIN CHECK

    if "user_id" not in session:

        flash(
            "Please login first."
        )

        return redirect(
            url_for("login")
        )

    # PLACE CHECK

    place = get_place_by_id(
        place_id
    )

    if place is None:

        flash(
            "Tourist place not found."
        )

        return redirect(
            url_for("places")
        )

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        # CHECK EXISTING FAVORITE

        cursor.execute(

            """
            SELECT id
            FROM favorites
            WHERE user_id = %s
            AND place_id = %s
            """,

            (

                session["user_id"],

                place_id

            )

        )

        existing_favorite = cursor.fetchone()

        if existing_favorite:

            flash(
                "This place is already in favorites."
            )

            return redirect(
                url_for("favorites")
            )

        # INSERT FAVORITE

        cursor.execute(

            """
            INSERT INTO favorites
            (
                user_id,
                place_id
            )
            VALUES
            (
                %s,
                %s
            )
            """,

            (

                session["user_id"],

                place_id

            )

        )

        connection.commit()

        flash(
            "Place added to favorites."
        )

        return redirect(
            url_for("favorites")
        )

    except Error as error:

        if connection is not None:

            connection.rollback()

        print(
            "Database Error:",
            error
        )

        flash(
            "Unable to add favorite."
        )

        return redirect(
            url_for("places")
        )

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# FAVORITES PAGE
# ==========================================

@app.route("/favorites")

def favorites():

    # LOGIN CHECK

    if "user_id" not in session:

        flash(
            "Please login first."
        )

        return redirect(
            url_for("login")
        )

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        # GET FAVORITE PLACE IDS

        cursor.execute(

            """
            SELECT place_id
            FROM favorites
            WHERE user_id = %s
            """,

            (

                session["user_id"],

            )

        )

        favorite_rows = cursor.fetchall()

        favorite_ids = [

            row[0]

            for row in favorite_rows

        ]

        # GET FAVORITE PLACES

        favorite_places = [

            place

            for place in tourist_places

            if place["id"] in favorite_ids

        ]

        return render_template(

            "favorites.html",

            favorite_places=favorite_places

        )

    except Error as error:

        print(
            "Database Error:",
            error
        )

        flash(
            "Unable to load favorites."
        )

        return redirect(
            url_for("places")
        )

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# REMOVE FAVORITE
# ==========================================

@app.route(
    "/remove_favorite/<int:place_id>",
    methods=["POST"]
)

def remove_favorite(place_id):

    # LOGIN CHECK

    if "user_id" not in session:

        flash(
            "Please login first."
        )

        return redirect(
            url_for("login")
        )

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        # DELETE FAVORITE

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

            flash(
                "Favorite removed successfully."
            )

        else:

            flash(
                "Favorite not found."
            )

        return redirect(
            url_for("favorites")
        )

    except Error as error:

        if connection is not None:

            connection.rollback()

        print(
            "Database Error:",
            error
        )

        flash(
            "Unable to remove favorite."
        )

        return redirect(
            url_for("favorites")
        )

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")

def logout():

    session.clear()

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("login")
    )


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )