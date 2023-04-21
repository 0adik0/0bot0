from flask import Flask, jsonify, request, make_response, send_file
import os
import uuid
import traceback


app = Flask(__name__)

@app.route("/api/create_document", methods=["POST"])
def create_document():
    data = request.json
    document_type = data.get("document_type")
    app_name = data.get("app_name")
    developer_name = data.get("developer_name")
    email = data.get("email")
    try:
        data = request.json
        # остальная часть кода
    except Exception as e:
        print(f"Ошибка: {e}")
        print(traceback.format_exc())  # вывод полного стека ошибки
        return make_response(jsonify({"error": "Server error"}), 500)
    
    if document_type == "privacy_policy":
        content = create_privacy_policy(app_name)
    elif document_type == "terms_of_use":
        content = create_terms_of_use(app_name)
    else:
        return make_response(jsonify({"error": "Invalid document type"}), 400)
    
    unique_id = uuid.uuid4().hex[:10]
    file_name = f"{unique_id}_{document_type}.txt"

    with open(file_name, "w") as f:
        f.write(content)

    response = make_response(jsonify({"url": f"/documents/{file_name}"}))
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/documents/<path:file_name>")
def serve_document(file_name):
    return send_file(file_name)

def create_privacy_policy(app_name: str):
    # ваш код для создания политики конфиденциальности
    content = f"Здесь будет политика конфиденциальности для приложения {app_name}"
    return content

def create_terms_of_use(app_name: str):
    # ваш код для создания условий использования
    content = f"Здесь будут условия использования для приложения {app_name}"
    return content

if __name__ == "__main__":
    app.run(debug=True)
