from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import serial
import serial.tools.list_ports
import tensorflow as tf

app = Flask(__name__)

# Globální proměnné
ser = None
current_mode = "manual"  # Režim ovládání (manual/automatic/line_following)

# Načtení TensorFlow Lite modelu pro rozhodování na křižovatkách
interpreter = tf.lite.Interpreter(model_path="intersection_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def get_available_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return ports

def set_serial_port(port):
    global ser
    if ser is not None:
        ser.close()  # Zavřít předchozí sériový port, pokud existuje
    ser = serial.Serial(port, 9600)

def detect_line(frame):
    # Převod do odstínů šedi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplikování Gaussova rozostření
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Prahování pro zvýraznění čáry
    _, thresholded = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)

    # Detekce hran pomocí Cannyho algoritmu
    edges = cv2.Canny(thresholded, 50, 150)

    # Nalezení čáry pomocí Houghovy transformace
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    return lines

def draw_lines(frame, lines):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
    return frame

def get_line_center(lines, frame_width):
    if lines is not None:
        # Průměrná pozice všech detekovaných čar
        x_center = np.mean([(line[0][0] + line[0][2]) / 2 for line in lines])
        return int(x_center)
    return frame_width // 2  # Vrátit střed, pokud není detekována žádná čára

def predict_direction(frame):
    # Převod snímku na vstup modelu
    img = cv2.resize(frame, (128, 128))  # Změna velikosti
    img = img / 255.0  # Normalizace
    img = np.expand_dims(img, axis=0).astype(np.float32)  # Přidání dimenze

    # Předpověď
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    # Interpretace výstupu
    classes = ["left", "right", "forward"]
    predicted_class = classes[np.argmax(output)]
    return predicted_class

def webcam_feed():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not capture frame")
            break

        # Pokud je aktivní režim jízdy podle čáry
        if current_mode == "line_following":
            lines = detect_line(frame)
            frame = draw_lines(frame, lines)

            if detect_intersection(lines):  # Pokud je detekována křižovatka
                print("Křižovatka detekována")
                decision = predict_direction(frame)  # Rozhodni se pomocí AI

                if decision == "left":
                    ser.write(b'L')  # Odboč vlevo
                    print("Rozhodnutí: Odbočit vlevo")
                elif decision == "right":
                    ser.write(b'R')  # Odboč vpravo
                    print("Rozhodnutí: Odbočit vpravo")
                elif decision == "forward":
                    ser.write(b'F')  # Pokračuj rovně
                    print("Rozhodnutí: Pokračovat rovně")
            else:
                # Normální sledování čáry
                line_center = get_line_center(lines, frame.shape[1])
                pid_output = compute_pid(line_center, frame.shape[1])
                control_robot_pid(pid_output)

        # Převod snímku do formátu JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()

@app.route('/set_mode', methods=['POST'])
def set_mode():
    global current_mode
    mode = request.json.get("mode")
    
    if mode == "manual":
        current_mode = "manual"
        if ser is not None:
            ser.write(b'N')  # Příkaz pro přepnutí na manuální režim
        return jsonify({"status": "success", "mode": "manual"})
    
    elif mode == "automatic":
        current_mode = "automatic"
        if ser is not None:
            ser.write(b'M')  # Příkaz pro přepnutí na automatický režim
        return jsonify({"status": "success", "mode": "automatic"})
    
    elif mode == "line_following":
        current_mode = "line_following"
        return jsonify({"status": "success", "mode": "line_following"})
    
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