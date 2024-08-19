from flask import Flask, render_template, request

app = Flask(__name__)

## HTMX

@app.get("/public")
def public():
    """IAM Code to make a service public. """
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
    """ Multi-glob. (Warning: gnarly.)

    Using the multi-swap extension, we can update multiple "(value)N" fields.
    Presumes at most 10 numbered fields, in the form "[field]N".
    """

    response = ""
    for value in ["project", "projectnum", "region", "service", "repo", "branch", "serviceaccount", "pool", "provider"]:
        if value in request.form:
            data = request.form[value]
            for i in range(10):
                response += f"<span id='{value}{i}'>{data}</span>"
    return response

## MAIN

@app.get("/")
def home():
    context = {}
    # Optionally insert information from header
    if 'referer' in request.headers: # and "https://github.com" in request.headers['referer']:
        print(f"Referer: {request.headers['referer']}")
        context['prefill_message'] = "Since you came from GitHub, we're prefilled some of these for you:"
        context['github_repo'] = "TEST"
        context['branch'] = "test"
        context['debug'] = "Request header: " + request.headers['referer']
    else:
        print("No referer headers")

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
