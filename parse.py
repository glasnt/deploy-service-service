# Originally pulled from https://github.com/glasnt/app-json-migrate/blob/main/ajm/parse.py

def warning_text(value):
    #TODO Implement
    print("WARNING: ", value)

def _parse_options(options):
    _settings = {}

    # Parse all stringy options
    for config in ["memory", "cpu", "concurrency", "max-instances", "port"]:
        if config in options.keys():
            _settings[config] = f"--{config}={options[config]}"

    if (
        "allow-unauthenticated" in options.keys()
        and options["allow-unauthenticated"] is False
    ):
        _settings["authentication"] = "--no-allow-unauthenticated"

    if "http2" in options.keys() and options["http2"] is True:
        _settings["http2"] = "--use-http2"

    return _settings


def _parse_hooks(hooks):
    _settings = {}

    for hook in ["prebuild", "postbuild", "precreate", "postcreate"]:
        if hook in hooks.keys() and hooks[hook] is not None:
            command = "; ".join(hooks[hook]["commands"])
            _settings[hook] = command

    return _settings


def _parse_env(env):
    """
    { "TITLE": { "description": "title for your site" }}

      - id: update service
        args:
          - update
          - $_SERVICE_NAME
          - --set-env-vars=TITLE=${_TITLE}

    substitutions:
        _TITLE: "" # title for your site
    """

    _service_envs = []
    _service_secrets = []
    _extra_substitutions = []

    for key in env:
        # Shortcut generated values
        if "generator" in env[key].keys() and env[key]["generator"] == "secret":
            _service_secrets.append(f"{key}={key}:latest")

        else:
            substitution = f"    _{key}: "
            if "value" in env[key].keys():
                substitution += '"' + env[key]["value"] + '"'
            elif "generator" in env[key].keys() and env[key]["generator"] == "secret":
                substitution += '""  # GENERATOR'
                warning_text(f"Value {key} needs secret TODO")
            else:
                substitution += '""'
                warning_text(f"Value {key} needs default TODO")

            if "description" in env[key].keys():
                substitution += f"  # {env[key]['description']}"

            _service_envs.append(f"{key}=${{_{key}}}")
            _extra_substitutions.append(substitution)

    _set_envvars, _set_secrets = "", ""
    if len(_service_envs) > 0:
        _set_envvars = "--set-env-vars=" + ",".join(_service_envs)
    if len(_service_secrets) > 0:
        _set_secrets = "--set-secrets=" + ",".join(_service_secrets)

    return _extra_substitutions, _set_envvars, _set_secrets


def _fix_service_name(service_name):
    # Based on tryFixServiceName https://github.com/GoogleCloudPlatform/cloud-run-button/blob/master/cmd/cloudshell_open/cloudrun.go#L121
    service_name = service_name[:63].lower().replace("_", "-").replace("/", "-").replace("\\", "-")

    if service_name[0] == "-":
        service_name = f"srv{service_name}"
    if service_name[-1] == "-":
        service_name = service_name[:-1]

    return service_name


def parse_appjson(data):
    settings = {}

    # Parse name
    if "name" in data.keys():
        settings["service_name"] = data["name"]
    else:
        settings["service_name"] = data["_service_name"]

    settings["service_name"] = _fix_service_name(settings["service_name"])
    settings["region"] = "us-central1"

    # Parse env
    if "env" in data.keys():
        (
            extra_substitutions,
            settings["service_envs"],
            settings["service_secrets"],
        ) = _parse_env(data["env"])
        settings["extra_substitutions"] = "\n".join(extra_substitutions)

    # Parse options
    options = {}
    if "options" in data.keys():
        options = _parse_options(data["options"])

    settings["options"] = "  ".join(options.values())

    # Parse hooks
    if "hooks" in data.keys():
        settings.update(_parse_hooks(data["hooks"]))

    return settings
