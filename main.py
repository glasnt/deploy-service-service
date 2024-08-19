from flask import Flask, render_template, request
from repo import parse_repo
from parse import parse_appjson
import requests

app = Flask(__name__)

## HTMX
@app.get("/public")
def public():
    """IAM Code to make a service public."""
    if "public" in request.args:
        return """
            <span id="public-flag">--allow-unauthenticated</span>
            <span id="public-iam"></span>
            """
    else:
        return """
            <span id="public-iam"><b>Optional</b>: </span>"
            """


@app.post("/input")
def update_input():
    """Multi-glob. (Warning: gnarly.)

    Using the multi-swap extension, we can update multiple "(value)N" fields.
    Presumes at most 10 numbered fields, in the form "[field]N".
    """

    response = ""
    for value in [
        "project",
        "projectnum",
        "region",
        "service",
        "repo",
        "branch",
        "serviceaccount",
        "pool",
        "provider",
    ]:
        if value in request.form:
            data = request.form[value]
            for i in range(10):
                response += f"<span id='{value}{i}'>{data}</span>"
    return response


## MAIN
def get_context(referer):

    context = parse_repo(referer)
    #breakpoint()


    context["prefill_message"] = True
    context["debug"] = context
    return context


@app.get("/")
def home():
    # Optionally insert information from header
    context = {}
    """
    if (
        "referer" in request.headers
        and "https://github.com" in request.headers["referer"]
    ):
        context = get_context(request.headers["referer"])
    """
    #context = get_context("https://github.com/glasnt/deploy-service-service/tree/latest/tests/options")

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
