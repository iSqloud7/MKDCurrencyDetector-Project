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

#### Start the Server
```bash
cd app/
python main.py
```

### 3. Mobile App Setup

#### Install Flutter Dependencies
```bash
cd CurrencyDetectorApp/flutter_app/
flutter pub get
```

#### Run the Application
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
