from flask import Flask, render_template, request, jsonify
import nfc
import ndef
import os

app = Flask(__name__)

LOCK_FILE = "/home/development2/tmp/nfc_lock.txt"

# Función para escribir en NFC
def write_nfc(message):
    try:
        clf = nfc.ContactlessFrontend('usb')
        if clf:
            def on_connect(tag):
                tag.ndef.records = [ndef.TextRecord(message)]
                return True

            clf.connect(rdwr={'on-connect': on_connect})
            clf.close()
            return "Escritura en NFC exitosa"
        else:
            return "Error: No se detectó un lector NFC"
    except Exception as e:
        # Asegurar que se elimine el archivo de bloqueo en caso de error
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        return f"Error al escribir en NFC: {str(e)}"

# Ruta para la interfaz web
@app.route('/')
def index():
    try:
        open(LOCK_FILE, 'w').close()
        print(f"🔒 Archivo de bloqueo creado en {LOCK_FILE}")
    except Exception as e:
        print(f"❌ Error al crear archivo de bloqueo: {str(e)}")
    return render_template('index.html')

# API para escribir en NFC
@app.route('/write_nfc', methods=['POST'])
def write_nfc_endpoint():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Mensaje vacío"}), 400

    result = write_nfc(message)
    return jsonify({"message": result})

# 📌 Eliminar el archivo de bloqueo cuando se cierra la página
@app.route('/remove_lock', methods=['POST'])
def remove_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print(f"🔓 Archivo de bloqueo eliminado: {LOCK_FILE}")
            return jsonify({"message": "Archivo de bloqueo eliminado"}), 200
        else:
            return jsonify({"message": "Archivo de bloqueo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al eliminar archivo de bloqueo: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)