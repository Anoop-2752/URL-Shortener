from flask import Flask, render_template, request, redirect
import string, random

app = Flask(__name__)

# In-Memory Storage
url_mapping = {}  # ephemeral storage: short_code -> long_url

# ------------------ Helper Function ------------------ #
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if code not in url_mapping:
            return code

# ------------------ Routes ------------------ #
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        long_url = request.form.get("long_url")
        if long_url:
            # Check if URL already exists
            existing_code = None
            for code, url in url_mapping.items():
                if url == long_url:
                    existing_code = code
                    break
            if existing_code:
                short_code = existing_code
            else:
                short_code = generate_short_code()
                url_mapping[short_code] = long_url
            # Construct full short URL
            short_url = request.headers.get("x-forwarded-proto", "https") + "://" + request.headers.get("host") + "/" + short_code
    return render_template("index.html", short_url=short_url)

@app.route("/<short_code>")
def redirect_short_url(short_code):
    long_url = url_mapping.get(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found", 404
