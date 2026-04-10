# 🩺 Celiac Disease AI Chatbot System

## Overview

An **agentic AI system for real-time celiac disease management**, designed to provide personalised, clinically grounded assistance.

Unlike traditional chatbots, this system integrates:

* **Multi-agent orchestration**
* **Retrieval-Augmented Generation (RAG) with clinical embeddings**
* **Persistent user memory**
* **Symptom tracking and proactive reminders**

The system runs **fully locally using Ollama (Llama 3.2)**, ensuring complete privacy of sensitive health data.

---

## Problem Statement

Celiac disease affects ~1% of the global population and requires:

* Strict gluten-free diet adherence
* Continuous symptom monitoring
* Personalised nutritional guidance

Existing solutions are:

* Generic and not domain-specific
* Unable to track user history
* Lacking proactive intervention

---

## Proposed Solution

A **multi-agent AI architecture** that provides:

* Personalised, context-aware responses
* Long-term user profiling
* Real-time symptom tracking
* Automated reminders and health insights

---

## System Architecture

### 🔁 Data Flow

```
React Frontend
      ↓
FastAPI Backend
      ↓
Orchestrator Agent (Intent Classification)
      ↓
Specialist Agents
      ↓
Shared Tool Layer
      ↓
Local LLM (Llama 3.2 via Ollama)
```

---

## 🤖 Multi-Agent System

The system uses **4 specialised agents**, each handling a distinct domain:

*  **Meal Planner Agent**
  Generates gluten-free meal recommendations

*  **Symptom Tracker Agent**
  Logs symptoms, severity (1–10), and maintains history

*  **Lifestyle Coach Agent**
  Provides wellness and lifestyle guidance

*  **Reminder Agent**
  Schedules and triggers proactive notifications

All agents are coordinated by an **Orchestrator Agent** that performs intent classification and routing.

---

##  Core Technologies

### 🔹 RAG Pipeline

* Documents chunked (1000 chars, 200 overlap)
* Embedded using **Bio_ClinicalBERT**
* Stored in **FAISS vector database**
* Top-k retrieval injected into prompts

➡️ Ensures **clinically grounded, hallucination-resistant responses**

---

### 🔹 Persistent Memory

* Extracts user-specific data (symptoms, triggers, preferences)
* Stores in **SQLite database**
* Injected into future conversations

➡️ Enables **long-term personalisation**

---

### 🔹 Local LLM Execution

* **Llama 3.2 (1B)** via Ollama
* Fully offline
* No external API calls

➡️ Ensures **100% privacy**

---

## ⚙️ Tech Stack

### Backend

* FastAPI
* LangChain
* FAISS
* SQLite
* APScheduler

### AI / ML

* Llama 3.2 (Ollama)
* Bio_ClinicalBERT

### Frontend

* React.js
* Node.js

---

##  Key Features

*  Multi-agent intelligent routing
*  Clinical RAG-based responses
*  Persistent user memory
*  Symptom tracking with severity logging
*  Proactive reminders (APScheduler)
*  PDF health report generation
*  Fully local, privacy-preserving system

---

##  System Capabilities

* 4 specialised agents
* RAG-based clinical retrieval
* Zero cloud dependency
* Real-time dashboard + chatbot interface

---

## 🛠️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd chatbot2
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r ../req.txt
```

Run backend:

```bash
uvicorn app:app --reload
```

---

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

### 4️⃣ Run Ollama (Required)

Ensure Ollama is installed and run:

```bash
ollama run llama3
```

---

## ▶️ Usage

* Open the React frontend
* Ask queries related to celiac disease
* System routes query → retrieves knowledge → generates response
* Tracks symptoms and updates memory in real-time

---

##  Future Enhancements

* Cloud deployment (optional mode)
* Advanced analytics dashboard
* Voice-based interaction
* Integration with wearable health devices

---

