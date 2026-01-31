# 🎓 MaheHub — Real-Time Event Management System

MaheHub is a real-time, full-stack event management platform designed for college campuses. It allows students to discover and register for events, organizers to submit event requests, and administrators to manage approvals with instant real-time updates using WebSockets.

## 🚀 Live Demo

Frontend (Netlify): https://mahehub.netlify.app  (currently issues in studentlogin page)

## ✨ Features

- Real-time synchronization using WebSockets without page refresh
- Role-based access for Students, Organizers, and Administrators
- Persistent and secure data storage with MongoDB Atlas
- Live notifications for students when events are approved by admins

## 🛠️ Tech Stack

Frontend:
- HTML5
- CSS3
- JavaScript (ES6)

Backend:
- Python 3.12
- websockets library

Database:
- MongoDB Atlas (NoSQL)

Hosting:
- Render (Backend)
- Netlify (Frontend)

## 📂 Project Structure

MaheHub/
├── server.py              # Python WebSocket server logic
├── requirements.txt       # Backend dependencies (pymongo, websockets, etc.)
├── index.html             # Login and entry point
├── admin.html             # Administrator dashboard
├── organizer.html         # Event submission portal
├── student.html           # Student event discovery and registration
└── style.css              # Global application styling

## 🌐 Deployment Details

Backend (Render):
- Deploy as a Web Service
- Start command: python server.py
- Bind server to 0.0.0.0

Frontend (Netlify):
- Deploy using Netlify Drop or Git integration
- Ensure main entry file is named index.html

Database (MongoDB Atlas):
- Set Network Access to 0.0.0.0/0 to allow Render dynamic IPs

## 🤝 Contributors

Tejas — tejasnj14@gmail.com  
Anup — anupvenu3011@gmail.com  
Abhay — abhay.sg2006@gmail.com  

## 📌 License

This project is developed for academic and learning purposes. Feel free to fork and modify.
