from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import string, random

# ------------------ Flask & DB Setup ------------------ #
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ Database Model ------------------ #
class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

# ------------------ Helper Functions ------------------ #
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if not URLMap.query.filter_by(short_code=code).first():
            return code

# ------------------ Routes ------------------ #
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        long_url = request.form.get("long_url")
        if long_url:
            # Check if URL already exists
            existing = URLMap.query.filter_by(long_url=long_url).first()
            if existing:
                short_code = existing.short_code
            else:
                short_code = generate_short_code()
                new_url = URLMap(long_url=long_url, short_code=short_code)
                db.session.add(new_url)
                db.session.commit()
            short_url = request.host_url + short_code
    return render_template("index.html", short_url=short_url)

@app.route("/<short_code>")
def redirect_short_url(short_code):
    url_entry = URLMap.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.long_url)
    else:
        return "URL not found", 404

# ------------------ Create DB & Run App ------------------ #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
