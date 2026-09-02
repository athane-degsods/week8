import json
import os

import azure.functions as func
import pypyodbc

# ---- Fill in your Azure SQL connection details here ----
server = 'inclass-week8.database.windows.net'
database = 'in-class-assignment-db'
username = 'duy-admin'
password = 'Password1'
# ----------------------------------------------------------

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def get_db_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=" + server + ";"
        "DATABASE=" + database + ";"
        "UID=" + username + ";"
        "PWD=" + password + ";"
        "ENCRYPT=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )


@app.function_name(name="login")
@app.route(route="login", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def login(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.method == "GET":
            req_username = req.params.get("username")
            req_password = req.params.get("password")
        else:
            content_type = req.headers.get("Content-Type", "")
            body = req.get_body()

            if body:
                if "application/json" in content_type.lower():
                    data = json.loads(body)
                    req_username = data.get("username")
                    req_password = data.get("password")
                else:
                    data = body.decode("utf-8")
                    pairs = {}
                    for item in data.split("&"):
                        if "=" in item:
                            key, value = item.split("=", 1)
                            pairs[key] = value
                    req_username = pairs.get("username")
                    req_password = pairs.get("password")
            else:
                req_username = None
                req_password = None

        if not req_username or not req_password:
            return func.HttpResponse(
                json.dumps({"message": "Missing username or password"}),
                status_code=400,
                mimetype="application/json",
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (req_username, req_password),
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return func.HttpResponse(
                json.dumps({
                    "message": "Login Successful",
                    "username": req_username,
                }),
                mimetype="application/json",
            )

        return func.HttpResponse(
            json.dumps({"message": "Invalid username or password"}),
            status_code=401,
            mimetype="application/json",
        )

    except Exception as exc:
        return func.HttpResponse(
            json.dumps({"message": f"Database error: {str(exc)}"}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="home")
@app.route(route="", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def home(req: func.HttpRequest) -> func.HttpResponse:
    html_path = os.path.join(os.path.dirname(__file__), 'week8.html')
    with open(html_path, 'r', encoding='utf-8') as file:
        html = file.read()

    return func.HttpResponse(html, mimetype="text/html")
