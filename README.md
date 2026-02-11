# MKD Currency Detector

## Setup Instructions.

### 1. Clone the Repository.
```bash
git clone https://github.com/iSqloud7/MKD-Currency-Detector.git
```
### 2. Dataset Download (Roboflow → YOLOv8)
  This project uses a dataset hosted on Roboflow.
  The script in MKDCurrencyDetector-Project/CurrencyDetectorApp/yolov8_training/notebooks/download_from_roboflow.ipynb
  downloads version 9 of the dataset in YOLOv8 format and moves it into the project directory structure. After running the script, the dataset will be placed in: yolov8_training/datasets/raw_all_classes/
  Link to the dataset: https://app.roboflow.com/datasciencepro/mkd-currency-recognition_v1/9

### 3. Model Training

This project includes separate YOLOv8 training notebooks for different detection tasks.

🔹 train_binary.ipynb

Purpose: Binary detector (Coin vs Background)

Notebook location:

/yolov8_training/notebooks/train/train_binary.ipynb


Dataset location:

/datasets/binary/data.yaml


Output model:

models/binary_detector/weights/

🔹 train_banknote.ipynb

Purpose: Banknote detector

Notebook location:

/yolov8_training/notebooks/train/train_banknote.ipynb


Dataset location:

/yolov8_training/datasets/banknote/data.yaml


Output model:

models/banknote_detector/weights/

🔹 train_coin.ipynb

Purpose: Multi-class coin detector

Notebook location:

/yolov8_training/notebooks/train/train_coin.ipynb


Dataset location:

/yolov8_training/datasets/coin/data.yaml


Output model:

models/coin_detector/weights/

### 3. Backend Setup.

#### Navigate to the Backend Directory.
```bash
cd CurrencyDetectorApp/
```

#### Set Up Virtual Environment.
Create and activate a virtual environment (venv) in the `CurrencyDetectorApp/` folder.

#### Install Dependencies.
```bash
cd backend/
pip install -r requirements.txt
pip install -r requirements-torch.txt
```

#### Install ngrok.
You need to install ngrok and add your own authtokens (its highly reccomended because you get benefits),
also you can use it without authtokens it should work*

#### Start the Server.
```bash
cd app/
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
```
and dont close the venv
open new terminal and write ngrok http 8000 to start ngrok server (don't close this window too)


### 4. Mobile App Setup.

#### Install Flutter Dependencies.
```bash
cd CurrencyDetectorApp/flutter_app/
flutter pub get
```

### Network Configuration.

If you use free plan on ngrok everytime you start the server you get different url so
you will need to paste it in base url in flutter_app/lib/config/api_config.dart (without / at the end)
```bash
flutter run
```

### 5. Testing the Application.

1. Start the server in PyCharm
2. Run the mobile application in Android Studio
3. Verify the connection is established
4. Use your phone's camera to capture currency images

### 6. Future directions for development.

Based on the achieved results and the identified limitations, the following directions for future improvements are proposed:
### Improvement of coin detection:
  Expanding the dataset with more coin samples in different conditions (worn, at an angle, different lighting).
  Experimenting with larger models (YOLOv8m or YOLOv8l) specifically trained for small objects.
  Implementation of specialized preprocessing techniques for coins (edge ​​enhancement, circular detection).

### Multiple object detection:
  Optimization of the system for simultaneous detection of multiple currencies. 
  Implementation of an algorithm for summing the total value of the detected currencies.
  Addition of visual indicators (bounding boxes) to the display for clear identification of each currency.

### 7. Notes
  Capturing and processing currency images works significantly faster when using a GPU instead of a CPU.
  GPU acceleration is highly recommended for model training and real-time detection.
  Make sure CUDA is properly installed if using an NVIDIA GPU.
  
## Made By:
Marija Dimitrieska 211117

Ivan Pupinoski 223260

Gjorge Prodanov 216134

---

## Requirements:
- Python 3.x
- Flutter SDK
- PyCharm (recommended)
- Android Studio (recommended)
