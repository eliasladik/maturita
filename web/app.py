from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)

# Načtení předtrénovaného modelu pro detekci obličejů (Haar Cascade Classifier)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def webcam_feed():
    # Otevření kamery (0 pro první připojenou kameru)
    cap = cv2.VideoCapture(0)

    # Kontrola, zda se kamera otevřela správně
    if not cap.isOpened():
        print("Error: Could not open webcam")

    while True:
        # Načtení snímku z kamery
        ret, frame = cap.read()

        # Kontrola, zda byl snímek načten správně
        if not ret:
            print("Error: Could not capture frame")
            break

        # Převod snímku na stupně šedi pro lepší detekci
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detekce obličejů v obrazu
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        # Kreslení obdélníků kolem detekovaných obličejů
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Převod snímku na formát JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Odeslání snímku v byte formátu
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        
    cap.release()
    
@app.route('/set_mode', methods=['POST'])
def set_mode():
    global control_mode
    mode = request.json.get("mode")
    
    if mode == "manual":
        control_mode = "Manuální ovládání"
    else:
        control_mode = "Automatické ovládání"
    
    print(f"Aktuální režim: {control_mode}")
    return jsonify({"status": "success", "mode": control_mode})

# Route pro zobrazení index stránky
@app.route('/')
def index():
    return render_template('index.html')

# Definování route pro každý pohybový akci
@app.route('/forward')
def forward():
    # Kód pro pohyb dopředu
    return 'Moving forward'

@app.route('/back')
def back():
    # Kód pro pohyb dozadu
    return 'Moving back'

@app.route('/left')
def left():
    # Kód pro pohyb vlevo
    return 'Moving left'

@app.route('/right')
def right():
    # Kód pro pohyb vpravo
    return 'Moving right'

# Route pro zastavení pohybu
@app.route('/stop')
def stop():
    # Kód pro zastavení
    return 'Stopping'

# Route pro video feed
@app.route('/video_feed')
def video_feed():
    return Response(webcam_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
