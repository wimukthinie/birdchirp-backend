from flask import Flask, request
from flask_mysqldb import MySQL
from flask_hashing import Hashing
import uuid
from flask_cors import cross_origin

from tensorflow.keras.models import load_model
import numpy as np
import os
import librosa

app = Flask(__name__)
model = load_model('birdchirp_voice_classification_model.hdf5')
target_audio = os.path.join(os.getcwd(), 'static/audio')

hashing = Hashing(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'birdchirp'

mysql = MySQL(app)

salt = "my-secret-salt"


@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    name = request.json['name']
    email = request.json['email']
    if does_user_exist(email):
        return {
                   "message": "User already exists"
               }, 400
    password = hashing.hash_value(request.json['password'], salt=salt)
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO birdchirp_user(name, email, password) VALUES(%s,%s,%s)''', (name, email, password))
    mysql.connection.commit()
    cursor.execute(''' SELECT * FROM birdchirp_user WHERE email = %s''', [email])
    user = cursor.fetchone()
    cursor.close()
    return {
        "id": user[0],
        "name": user[1],
        "email": user[2]
    }


def does_user_exist(email):
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM birdchirp_user WHERE email = %s''', [email])
    user = cursor.fetchone()
    cursor.close()
    return user is not None


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    email = request.json['email']
    password = hashing.hash_value(request.json['password'], salt=salt)
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM birdchirp_user WHERE email = %s''', [email])
    user = cursor.fetchone()
    print(user)
    print(user[3])
    cursor.close()
    if user is not None:
        if user[3] == password:
            token = uuid.uuid4()
            cursor = mysql.connection.cursor()
            cursor.execute(''' UPDATE birdchirp_user SET token = %s WHERE email = %s''', (token, email))
            mysql.connection.commit()
            cursor.close()
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "token": token
            }
        else:
            return {
                       "message": "Password is incorrect"
                   }, 401
    else:
        return {
                   "message": "User does not exist"
               }, 404


@app.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    email = request.json['email']
    token = request.json['token']
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM birdchirp_user WHERE email = %s''', [email])
    user = cursor.fetchone()
    cursor.close()
    if user is not None:
        if user[5] == token:
            cursor = mysql.connection.cursor()
            cursor.execute(''' UPDATE birdchirp_user SET token = %s WHERE email = %s''', (None, email))
            mysql.connection.commit()
            cursor.close()
            return {
                "message": "User logged out successfully"
            }
        else:
            return {
                       "message": "Token is incorrect"
                   }, 401
    else:
        return {
                   "message": "User does not exist"
               }, 404


@app.route('/me', methods=['GET'])
@cross_origin()
def me():
    token = request.json['token']
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM birdchirp_user WHERE token = %s ''', [token])
    user = cursor.fetchone()
    cursor.close()
    if user is not None:
        return {
                   "id": user[0],
                   "name": user[1],
                   "email": user[2],
               }, 200
    else:
        return {
                   "message": "User does not exist"
               }, 404


@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    if request.method == 'POST':
        # get audio and token from form data
        audio_file = request.files['audio']
        # token = request.form['token']
        # cursor = mysql.connection.cursor()
        # cursor.execute(''' SELECT * FROM birdchirp_user WHERE token = %s ''', [token])
        # user = cursor.fetchone()
        # cursor.close()
        return predictAnimal(audio_file)
        # if user is not None:
        #     return predictAnimal(audio_file)
        # else:
        #     return {
        #                "message": "User does not exist"
        #            }, 404
    else:
        return {
                   "message": "Invalid request"
               }, 400


# Allow files with extension wav
ALLOWED_EXT = set(['wav', 'mp3'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


# Function to load and prepare the audio in right shape
def read_audio(filename):
    # preprocess the audio file
    audio, sample_rate = librosa.load(filename, res_type='kaiser_fast')
    mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccs_scaled_features = np.mean(mfccs_features.T, axis=0)

    # Reshape MFCC feature to 2-D array
    mfccs_scaled_features = mfccs_scaled_features.reshape(1, -1)
    return mfccs_scaled_features


def predictAnimal(audio_file):
    if audio_file and allowed_file(audio_file.filename):
        classes_x = -1
        filename = audio_file.filename
        file_path = os.path.join('static/audio', filename)
        audio_file.save(file_path)
        audio = read_audio(file_path)
        class_prediction = model.predict(audio)
        classes_x = np.argmax(class_prediction, axis=1)[0]
        # 0 = Indian Peafowl
        # 1 = Greater Coucal
        # 2 = Indian Cuckoo
        # 3 = Asian Koel
        # 4 = Indian Cuckoo
        # 5 = Puff-throated Babbler

        if classes_x == 0:
            label = "Indian Peafowl"
        elif classes_x == 1:
            label = "Asian Koel"
        elif classes_x == 2:
            label = "Indian Cuckoo"
        elif classes_x == 3:
            label = "Greater Couca"
        elif classes_x == 4:
            label = "Puff-throated Babbler"
        else:
            label = "Unknown Class"
        return {
            "class": int(classes_x[0]),
            "prediction": prediction_class
        }
    else:
        return {
            "message": "Invalid request"
        }


if __name__ == '__main__':
    app.run()
