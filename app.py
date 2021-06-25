from flask import Flask, render_template, request
import logging

app = Flask(__name__, static_url_path='static')
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        print(
            f"\n===============\nNEW INQUIRY!\n\nNAME: {name}\nEMAIL: {email}\nSUBJECT: {subject}\nINQUIRY:\n{message}\n===============\n")
        return render_template("trouble.html", name=name)
    else:
        return render_template("trouble.html")
