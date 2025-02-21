from flask import Flask, render_template, Response, request, jsonify
import cv2
import serial
import serial.tools.list_ports

app = Flask(__name__)

# Globální proměnná pro sériový port
ser = None

def get_available_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return ports

def set_serial_port(port):
    global ser
    if ser is not None:
        ser.close()  # Zavřít předchozí sériový port, pokud existuje
    ser = serial.Serial(port, 9600)

def webcam_feed():
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not capture frame")
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()

@app.route('/set_mode', methods=['POST'])
def set_mode():
    mode = request.json.get("mode")
    
    if mode == "manual":
        # Pošle příkaz pro přepnutí do manuálního režimu na Arduino
        if ser is not None:
            ser.write(b'N')
            print("manualni mod")  # Příkaz pro přepnutí na manuální režim ('N')
        return jsonify({"status": "success", "mode": "manual"})
    
    elif mode == "automatic":
        # Pošle příkaz pro přepnutí do automatického režimu na Arduino
        if ser is not None:
            ser.write(b'M')  # Příkaz pro přepnutí na automatický režim ('M')
        return jsonify({"status": "success", "mode": "automatic"})
    
    return jsonify({"status": "error", "message": "Invalid mode"})

@app.route('/')
def index():
    ports = get_available_ports()  # Získání dostupných portů
    return render_template('index.html', ports=ports)

@app.route('/set_port', methods=['POST'])
def set_port():
    port = request.form['port']
    try:
        set_serial_port(port)
        return f"Serial port set to {port}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/forward')
def forward():
    if ser is not None:
        ser.write(b'F')  # Odesílá příkaz 'F' pro dopředu
        return 'Moving forward'
    return 'Error: Serial port not set'

@app.route('/back')
def back():
    if ser is not None:
        ser.write(b'B')  # Odesílá příkaz 'B' pro dozadu
        return 'Moving back'
    return 'Error: Serial port not set'

@app.route('/left')
def left():
    if ser is not None:
        ser.write(b'L')  # Odesílá příkaz 'L' pro vlevo
        return 'Moving left'
    return 'Error: Serial port not set'

@app.route('/right')
def right():
    if ser is not None:
        ser.write(b'R')  # Odesílá příkaz 'R' pro vpravo
        return 'Moving right'
    return 'Error: Serial port not set'

@app.route('/stop')
def stop():
    if ser is not None:
        ser.write(b'S')  # Odesílá příkaz 'S' pro zastavení
        return 'Stopping'
    return 'Error: Serial port not set'

@app.route('/video_feed')
def video_feed():
    return Response(webcam_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    