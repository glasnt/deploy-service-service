from flask import Flask, render_template, request

app = Flask(__name__)


@app.post("/clicked")
def clicked():
    return "<b>Clickced!</b>"


@app.get("/public")
def public():
    """IAM Code to make a service public. """
    if "public" in request.args:
        return "public"
    else:
        return ""

@app.post("/input")
def update_input():
    """ Multi-glob. (Warning: gnarly.)
    Using the multi-swap extension, we can update multiple "(value)N" fields.
    Presumes at most 10 numbered fields, in the form "[field]N".
    """
    for value in ["project", "region"]:
        if value in request.form:
            data = request.form[value]
            response = ""
            for i in range(10):
                response += f"<span id='{value}{i}'>{data}</span>"
            return response

@app.get("/")
def home():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
