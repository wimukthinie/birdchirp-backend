# BirdChirp Flask App

This Flask API allows you to predict bird species from audio files using machine learning models.

## Requirements

-   Python 3.9 (recommended)

## Setup

1.  Create a folder called `static` in the root directory of the app.
    
2.  Inside `static`, create a folder called `audio`. This is used to cache the audio files uploaded for prediction.
    
3.  Create a MySQL database called `birdchirp` in XAMPP PHPMyAdmin.
    
4.  Within the `birdchirp` database, create a table called `birdchirp_user` using the following query:
    
```    
    CREATE TABLE `birdchirp_user` (
      `id` int(11) NOT NULL,
      `name` varchar(255) NOT NULL,
      `email` varchar(255) NOT NULL,
      `password` varchar(255) NOT NULL,
      `created_date` date NOT NULL DEFAULT current_timestamp(),
      `token` varchar(255) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;`` 
```
    
5.  Install the required Python packages by running 

```
pip install -r requirements.txt
```

6.  Run the app using

```
flask run
```

## Usage

To use the app, navigate to `http://localhost:5000` in your web browser. You can upload an audio file and get a prediction for the bird species in the file. You can also register an account and log in to see your prediction history.



