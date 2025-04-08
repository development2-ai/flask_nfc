from flask import Flask, render_template, request, jsonify
import nfc
import ndef
import os, time, subprocess

app = Flask(__name__)

LOCK_FILE = "/tmp/nfc_lock.txt"

# Función para escribir en NFC
def write_nfc(message):
    clf = None  # Inicializar la variable
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
        validation = restart_usb()  # Reiniciar el USB del lector
        if(validation == False):
            return "Error: No se pudo reiniciar el lector NFC"
        else:
            return "Espere un momento para volver a intentar la escritura en NFC"

# Función para reiniciar el USB del lector
def restart_usb():
    print("🔌 Reiniciando USB del lector...")
    os.system("echo '1-1.4' | sudo tee /sys/bus/usb/drivers/usb/unbind")
    time.sleep(1)
    os.system("echo '1-1.4' | sudo tee /sys/bus/usb/drivers/usb/bind")

    # Esperar hasta que el lector vuelva a aparecer
    print("⏳ Esperando que el lector se reconecte...")
    for _ in range(10):
        output = subprocess.getoutput("lsusb -d 072f:2200")
        if "ACR122U" in output:
            print("✅ Lector reconectado correctamente.")
            return True
        time.sleep(1)
    print("❌ El lector no reapareció.")
    return False

# Ruta para la interfaz web
@app.route('/')
def index():
    try:
        open(LOCK_FILE, 'w').close()
        print(f"🔒 Archivo de bloqueo creado en {LOCK_FILE}")
        os.system("echo '1-1.4' | sudo tee /sys/bus/usb/drivers/usb/unbind")
        time.sleep(1) 
        os.system("echo '1-1.4' | sudo tee /sys/bus/usb/drivers/usb/bind")
    except Exception as e:
        print(f"❌ Error al crear archivo de bloqueo: {str(e)}")
        restart_usb()  # Reiniciar el USB del lector
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