Smart Login Assistant

Face-Aware Application Prediction System (Local, Privacy-Preserving)

Overview

Smart Login Assistant is a local-first intelligent desktop system that identifies who is sitting in front of a PC using facial recognition, logs post-login application usage, and learns behavioral patterns to predict the next application a user is likely to open.

The system runs entirely on-device, combining computer vision, OS-level telemetry, and lightweight machine learning models to provide personalized app suggestions without sending biometric data to the cloud.

Key Features

Real-time facial recognition via webcam to identify the active user

Session-based identity confirmation to reduce false positives

Application usage logging using native Windows foreground process APIs

Behavioral learning models:

Time-of-day frequency modeling

Markov transition modeling for next-app prediction

Privacy-preserving design (no screenshots, keystrokes, or cloud uploads)

Single-command execution for daily use


Tech Stack

Language: Python 3.12

Computer Vision: OpenCV, DeepFace

ML / DL: TensorFlow / Keras

OS Telemetry: psutil, pywin32

Data Storage: SQLite

Platform: Windows

Privacy & Security

This project is designed with privacy-by-design principles:

All facial embeddings and behavioral data are stored locally

No images, video, keystrokes, or screen content are retained

No cloud services or external APIs are required

Intended for personal use with informed consent

Installation
git clone https://github.com/yourusername/smart-login-assistant.git
cd smart-login-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Usage
Run the full system (recommended)
.\.venv\Scripts\python.exe -m scripts.run_all


This will:

Start face recognition and session logging

Log application usage

Train behavioral models

Suggest the most likely next application

Run components individually
# Face recognition + logging
.\.venv\Scripts\python.exe -m scripts.run_monitor

# Train models
.\.venv\Scripts\python.exe -m scripts.train_model
.\.venv\Scripts\python.exe -m scripts.train_markov

# Suggest next app
.\.venv\Scripts\python.exe -m scripts.suggest_and_launch
.\.venv\Scripts\python.exe -m scripts.suggest_markov

Learning Models

Time-Bucket Model: Learns the most common first app per user per weekday/hour

Markov Model: Learns transitions between applications (e.g., Chrome → VS Code)

Models retrain automatically as more sessions are logged

Limitations

Requires multiple sessions to learn meaningful patterns

Webcam lighting and positioning affect recognition accuracy

Currently supports Windows only

Designed for single-machine, personal use

Future Improvements

Background system tray application

Confidence-based auto-launching

Multi-user profile support

Cloud analytics (optional, anonymized)

Mobile or cross-device extensions
