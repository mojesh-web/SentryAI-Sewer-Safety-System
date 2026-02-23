# 🚨 SentryAI – AI-Based Sewer Safety Monitoring System

AI-powered real-time sewer safety monitoring system with PPE detection and risk classification.

---

## 🎯 Problem

Unsafe sewer entry continues to cause fatal accidents due to toxic gas exposure and lack of real-time monitoring. Despite regulations, there is no automated safety enforcement mechanism.

---

## 🧠 Solution

SentryAI detects human entry into restricted sewer zones and verifies helmet (PPE) usage using AI-based computer vision.

It:
- Detects person inside restricted zone
- Checks helmet presence
- Classifies risk as HIGH or LOW
- Logs timestamped evidence
- Captures event snapshots
- Displays results on a live dashboard

---

## ⚙️ Technology Stack

- Python
- YOLOv8 (Ultralytics)
- OpenCV
- Streamlit
- Pandas
- JSON-based logging

---

## 🚀 How To Run

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Add Input Videos
Place videos inside:
```
data/videos/
```

### 3️⃣ Add Helmet Model
Download and place:
```
models/helmet_best.pt
```

### 4️⃣ Run Detection
```bash
python src/detect_people.py
```

### 5️⃣ Launch Dashboard
```bash
streamlit run app.py
```

---

## 🌍 Impact

SentryAI enhances sanitation worker safety, reduces fatal incidents, ensures digital accountability, and provides a scalable smart-city safety solution.
---

## 🏗 System Architecture

```
Camera / Video Input
        ↓
YOLOv8 Person Detection
        ↓
Restricted Zone Monitoring
        ↓
Helmet (PPE) Detection
        ↓
Risk Classification Engine
        ↓
Event Logging (JSON + Snapshot)
        ↓
Streamlit Dashboard (Live Monitoring)
```

---

## 🔄 System Workflow

1. Video feed is processed frame-by-frame.
2. Person detection identifies human presence.
3. A polygon-based zone defines restricted sewer area.
4. When a person enters the zone:
   - Helmet detection model checks PPE compliance.
5. Entry is classified:
   - 🔴 HIGH Risk → No Helmet
   - 🟢 LOW Risk → Helmet Detected
6. Event is logged with timestamp + snapshot.
7. Dashboard displays metrics and visual evidence.

---

## 🖥 Dashboard Features

- Real-time risk count (HIGH vs LOW)
- Event log table
- Snapshot evidence display
- Auto-refresh monitoring view

---

## 📈 Future Improvements

- Gas detection integration (IoT sensors)
- SMS / Email alert system
- Real-time CCTV deployment
- Edge device optimization (Raspberry Pi / Jetson Nano)
- Municipal authority alert escalation

---

## 🎥 Demo

To see the system in action:

1. Run detection:
   ```bash
   python src/detect_people.py
   ```

2. Launch dashboard:
   ```bash
   streamlit run app.py
   ```

The dashboard will display detected entries and classify risk levels.
