# Group 6 — Dublin Bike Sharing Web Application

A full-stack web application designed to help users explore Dublin's bike stations, check availability, view current weather, and plan their cycling journey with the help of a smart, interactive map and machine learning predictions.

---

## 📚 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Pages Overview](#pages-overview)
- [System Architecture](#system-architecture)
- [Setup Instructions](#setup-instructions)
- [Deployment](#deployment)
- [User Flow](#user-flow)
- [Contributors](#contributors)
- [Important Notes](#important-notes)
- [Future Improvements](#future-improvements)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## 📌 Introduction

This project was developed as part of our university group coursework. It aims to simulate a city bike-sharing platform where users can:

- View real-time bike availability
- View real-time weather condition and temperature 
- Show historic station-specific data and historic weather information
- Predict bike availability using machine learning
- Interact with the system through a user-friendly frontend

---

## ✨ Features

- 🗺️ Interactive Google Maps showing all station markers
- 🚲 Real-time bike availability display per station in Dublin (JCDecaux API)
- 🌤️ Weather data (OpenWeather API)
- 📈 Google visualisations tool for bike usage trends
- 🤖 ML-powered prediction of bike availability
- 🔐 Basic login/register feature (with Google Sheet as backend)
- 💬 Contact form with auto-email reply and data storage (with Google Sheet as backend)
- 💻 Responsive layout optimised for desktop and mobile

---

## 🧰 Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Flask (Python)
- **Data Storage:** CSV files, Google Sheets (via Apps Script)
- **ML Model:** Random Forest (joblib model)
- **External APIs:** Google Maps, OpenWeather API, JCDecaux API
- **Deployment:** AWS EC2, Google Apps Script

---

## 📄 Pages Overview

| Page         | Description                                     |
|--------------|-------------------------------------------------|
| `/`          | Homepage with project intro and testimonials    |
| `/about`     | Company's history and stations information      |                  
| `/rent`      | Simulated rent + fake payment validation        |
| `/use`       | Step-by-step usage guide and safety policies    |
| `/map`       | Interactive map + station markers + prediction  |
| `/faq`       | Frequently asked questions                      |
| `/contact`   | Contact form with email sending                 |
| `/login`     | Register/login form connected to Google Sheet   |

---

## 🏗️ System Architecture

> See `/docs/class_diagram.png` for full structure  

Main components:

- `map.js`, `initMap.js` – handles all map logic
- `contact.js`, `payment.js`, `account.js` – handles user interaction logic
- `getWeatherData.py`, `getBikeData.py`, `accountApiFunction.py, storeContactInfo.py` – helper scripts for backend
- `bike_availability_rf_model_with_new_features.joblib` – prediction model
- CSVs in `/data` – stations, weather, bike availability, etc.

---

## 🛠️ Setup Instructions

1. **Clone the repository:**

```
git clone https://github.com/Peja016/software-project.git
```

2. **Install dependencies:**

```
pip install -r requirements.txt
```

3. **Create .env:**

Create a .env file and put your API key in the file.

JCDecaux_API_KEY
WEATHER_API_KEY
GOOGLE_MAP_API
GOOGLE_APP_SCRIPT_URL
SECRET_KEY

4. **Run the Flask app locally:**

```
flask run
```

---

## 🌐 Deployment

This project is hosted on AWS EC2. To access the site:

http://<ec2-public-ip>:5000

Make sure ports are open and `flask run --host=0.0.0.0` is used on server.

---

## 🔄 User Flow Summary

1. User lands on homepage → sees intro/testimonials  
2. Navigates to map → clicks station → sees bike + weather info  
3. (Optional) Logs in via login page  
4. (Optional) Sends message via contact form  
5. System responds with real-time data, visual charts, or confirmation

---

## 👥 Contributors

- **Hsuan-Yu Tan** – Full Stack Developer, UI/UX Designer, Project Manager, Scrum Master and Tester
- **Kexun Liu** – UI/UX Designer, Machine Learning Engineer, Developer, Scrum Master and Tester 
- **Herman Dolhyi** – Report Writing, Scrum Master, Frontend Developer, Project Manager, Tester

---

## ⚠️ Important Notes

- The login/register feature is for demonstration only. Please **do not use your real passwords** during testing.
- User data is stored in Google Sheets without encryption or validation. This is **not secure for production use**.
- The payment process is a front-end simulation and does not involve actual transactions.
- API keys are restricted to testing usage. Rate limits may apply.

## 🚧 Future Improvements

- Implement full user authentication with password hashing and email verification
- Enable a user dashboard for logged-in users to view booking history and assigned bike unlock codes
- Send an automated email with the bike pickup code to subscribed users after completing a (simulated) rental process
- Replace Google Sheets with a proper database system (e.g. MySQL or NoSQL) to store user data, contact form submissions, and rental information more securely and efficiently

## 📝 Disclaimer

This project was developed for academic purposes only. Some features are mock implementations and not intended for production use.

## 📄 License

MIT License  
© 2025 Group 6 – University Coursework
