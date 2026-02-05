# MKD Currency Detector

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/iSqloud7/MKD-Currency-Detector.git
```

### 2. Backend Setup

#### Navigate to the Backend Directory
```bash
cd CurrencyDetectorApp/
```

#### Set Up Virtual Environment
Create and activate a virtual environment (venv) in the `CurrencyDetectorApp/` folder.

#### Install Dependencies
```bash
cd backend/
pip install -r requirements.txt
pip install -r requirements-torch.txt
```

#### Install ngrok
You need to install ngrok and add your own authtokens(its highly reccomended because you get benefits),
also you can use it without authtokens it should work*



#### Start the Server
```bash
cd app/
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
```
and dont close the venv
open new terminal and write ngrok http 8000 to start ngrok server(don't close this window too)

### 3. Mobile App Setup

#### Install Flutter Dependencies
```bash
cd CurrencyDetectorApp/flutter_app/
flutter pub get
```

#### Run the Application
If you use free plan on ngrok everytime you start the server you get different url so
you will need to paste it in base url in flutter_app/lib/config/api_config.dart (without / at the end)
```bash
flutter run
```

### 4. Network Configuration

- Ensure your mobile device and server are on the same IP address/network
- Configure IP addresses in `CurrencyDetectorApp/flutter_app/lib/config/api_config.dart`

### 5. Testing the Application

1. Start the server in PyCharm
2. Run the mobile application in Android Studio
3. Verify the connection is established
4. Use your phone's camera to capture currency images

## Made By
Marija Dimitrieska 211117
Ivan Pupinoski 223260
Gjorge Prodanov 216134

---

## Requirements
- Python 3.x
- Flutter SDK
- PyCharm (recommended)
- Android Studio (recommended)
