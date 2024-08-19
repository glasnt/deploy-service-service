from flask import Flask, render_template, request
import requests

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

def get_context(referer):
    context = {}
    clean_referer = referer.split("?")[0].replace("https://github.com/", "")

    # Get information
    github_repo = "/".join(clean_referer.split("/")[0:2])
    service_name = clean_referer.split('/')[1].replace("_","-")

    # Guess information
    if "tree" in clean_referer or "blob" in clean_referer:
        branch = clean_referer.split("/")[3]
    else:
        try:
            response = requests.get(f"https://api.github.com/repos/{github_repo}")
            branch = response.json()['default_branch']
        except:
            branch = ""

    context['github_repo'] = github_repo
    context['service_name']= service_name
    context['branch'] = branch
    context['prefill_message'] = True
    return context

@app.get("/")
def home():
    # Optionally insert information from header
    context = {}
    if 'referer' in request.headers and "https://github.com" in request.headers['referer']:
        context = get_context(request.headers['referer'])

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
