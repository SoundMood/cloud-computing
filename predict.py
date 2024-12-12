import io
import os
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from mtcnn import MTCNN
import cv2
import numpy as np
import spotipy

from google.cloud import storage

def get_top_tracks_from_playlist(sp, playlist_id):
    """
    Mendapatkan lagu populer dari playlist berdasarkan popularitas.
    """
    try:

        playlist_tracks = sp.playlist_tracks(playlist_id, limit=25)        
        sorted_tracks = sorted(playlist_tracks['items'], key=lambda x: x['track']['popularity'], reverse=True)
        top_tracks = [track['track']['uri'] for track in sorted_tracks]

        return top_tracks
    
    except Exception as e:
        raise e


def get_playlist_for_mood(sp, mood_keywords):
    """
    Mencari playlist berdasarkan keyword mood dan mengambil 5 lagu terpopuler.
    """

    try:
        # Mencari playlist berdasarkan keyword mood
        playlist_results = sp.search(q=mood_keywords, type="playlist", limit=10)
        
        playlist_id = None
        for playlist in playlist_results['playlists']['items']:
            if playlist:
                playlist_id = playlist['id']
    
        
        return get_top_tracks_from_playlist(sp, playlist_id)

    except Exception as e:
        raise e

    
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
        # print("No face detected!")
        return None

# NEXT: Imple ML part and done

storage_client = storage.Client()


def predict(image_name: str, access_token: str):
    try:
        # Access Google Cloud Storage to read image
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(image_name)
        content = blob.download_as_bytes()

        image = Image.open(io.BytesIO(content))
        image = image.convert("RGB")  # Ensure image is in RGB format
        image_np = np.array(image)  # Convert PIL Image to NumPy array

        # Deteksi dan crop wajah
        cropped_face = detect_and_crop_face(image_np)

        if cropped_face is None:
            return {"error": "No face detected!"}
        
        image_resized = cv2.resize(cropped_face, (100, 100))  # Resize ke ukuran input model
        image_resized = np.expand_dims(image_resized, axis=0)  # Tambahkan dimensi batch
        image_resized = image_resized / 255.0  # Normalisasi gambar
        predictions = model.predict(image_resized, verbose=0)  # Prediksi
        predicted_class = np.argmax(predictions)  # Ambil kelas dengan probabilitas tertinggi

        mood = class_names[predicted_class]
        sp = spotipy.Spotify(auth=access_token)

        return {"mood": mood, "song_ids": get_playlist_for_mood(sp, mood)}

    except Exception as e:
        return {"error": e}
