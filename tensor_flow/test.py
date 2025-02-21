import cv2

# Load pre-trained YOLO model and config files
net = cv2.dnn.readNet("C:\Users\EliasLa\Desktop\maturitni_projekt\tensor_flow\yolov3.cfg", "tensor_flow\yolov3.weights")


# Use the camera as input
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    # Perform forward pass
    detections = net.forward()

    # Display the frame (implement bounding boxes here)
    cv2.imshow("Live Object Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
