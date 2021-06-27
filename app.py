from flask import Flask, render_template, request
import logging

app = Flask(__name__)
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/", methods=["GET", "POST"])
def trouble():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        print(
            f"\n===============\nNEW INQUIRY!\n\nNAME: {name}\nEMAIL: {email}\nSUBJECT: {subject}\nINQUIRY:\n{message}\n===============\n")
        return render_template("sent.html")
    else:
        return render_template("troubleshoot.html")


@app.route("/")
def indexpage():
    return render_template("index.html")


@app.route("/")
def commandpage():
    return render_template("command.html")


@app.route("/")
def faqpage():
    return render_template("faq.html")


@app.route("/")
def teampage():
    return render_template("team.html")
