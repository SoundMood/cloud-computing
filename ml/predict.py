import io
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from settings import BUCKET_NAME
from mtcnn import MTCNN
import cv2
import numpy as np
from google.cloud import storage

model = load_model("models/5kelas.keras")
detector = MTCNN()
class_names = ['angry', 'happy', 'neutral', 'sad', 'surprised']

def detect_and_crop_face(image):
    """
    Fungsi untuk mendeteksi wajah dan meng-crop wajah pertama yang terdeteksi.
    :param image: Input gambar (numpy array)
    :return: Gambar wajah yang ter-crop, atau None jika tidak ada wajah yang terdeteksi
    """
    faces = detector.detect_faces(image)  # Deteksi wajah dalam gambar
    if faces:
        x, y, w, h = faces[0]['box']  # Ambil koordinat wajah pertama
        cropped_face = image[y:y+h, x:x+w]  # Crop wajah dari gambar
        return cropped_face
    else:
        print("No face detected!")
        return None

# NEXT: Imple ML part and done

storage_client = storage.Client.from_service_account_json('acc-key.json')


def predict(image_name: str):
    try:
        # Access Google Cloud Storage to read image
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(image_name)
        content = blob.download_as_bytes()

        image = Image.open(io.BytesIO(content))
        image = image.convert("RGB")  # Ensure image is in RGB format
        image_np = np.array(image)  # Convert PIL Image to NumPy array

        # TODO: DO IT SOON!
        arr = ["CC plz imple the clustering now"]

        # Deteksi dan crop wajah
        cropped_face = detect_and_crop_face(image_np)

        if cropped_face is None:
            return {"error": "No face detected!"}
        
        image_resized = cv2.resize(cropped_face, (100, 100))  # Resize ke ukuran input model
        image_resized = np.expand_dims(image_resized, axis=0)  # Tambahkan dimensi batch
        image_resized = image_resized / 255.0  # Normalisasi gambar
        predictions = model.predict(image_resized, verbose=0)  # Prediksi
        predicted_class = np.argmax(predictions)  # Ambil kelas dengan probabilitas tertinggi
        return {"mood": class_names[predicted_class], "song_ids": arr}

    except Exception as e:
        return {"error": e}
        # raise HTTPException(status_code=400, detail={"message": f"Error: {e}"})
