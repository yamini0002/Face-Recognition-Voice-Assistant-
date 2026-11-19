import cv2
import os
import numpy as np
import time

def collect_and_train():
    # 1. Setup paths
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 2. Collect Samples
    # Try index 1 first (usually FaceTime HD Camera on Macs when iPhone is nearby)
    cap = cv2.VideoCapture(1)
    if not cap.isOpened() or cap.read()[1] is None:
        print("[INFO] Index 1 not available, trying default index 0...")
        cap = cv2.VideoCapture(0)
    print("\n--- PHASE 1: Face Capture ---")
    print("Look straight into the camera. We are capturing 100 samples of your face...")
    time.sleep(2)
    
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            # Save the cropped gray face into the dataset folder
            # We assign ID '1' to you (e.g., User.1.1.jpg, User.1.2.jpg)
            face_img = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{dataset_dir}/User.1.{count}.jpg", face_img)
            
            # Draw a box on the preview
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"Captured: {count}/100", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
        cv2.imshow("Registering Face", frame)
        
        # Break if 'q' is pressed or we have 100 images
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 100:
            break
            
    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Face capture completed.")

    # 3. Train Model
    print("\n--- PHASE 2: Training Model ---")
    
    # Create LBPH Face Recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    face_samples = []
    ids = []
    
    image_paths = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir) if f.endswith(".jpg")]
    
    for image_path in image_paths:
        # Load image as grayscale
        gray_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # Extract the user ID (which is '1' in our file names "User.1.count.jpg")
        try:
            user_id = int(os.path.basename(image_path).split(".")[1])
            face_samples.append(gray_img)
            ids.append(user_id)
        except Exception as e:
            print(f"Skipping file: {image_path} due to error {e}")
            
    if len(face_samples) > 0:
        recognizer.train(face_samples, np.array(ids))
        recognizer.save("trainer.yml")
        print("[SUCCESS] Face model trained successfully and saved as 'trainer.yml'!")
    else:
        print("[ERROR] No face samples found to train on.")

if __name__ == '__main__':
    collect_and_train()