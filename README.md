# OMANI Therapist

A modern web-based therapy assistant leveraging Microsoft Azure OpenAI services, the GROQ API, and advanced Clause Opus text processing for enhanced conversational intelligence.

---

## 🚀 Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Getting Started](#getting-started)  
5. [Configuration](#configuration)  
   - [Microsoft Azure OpenAI](#microsoft-azure-openai)  
   - [GROQ API](#groq-api)  
   - [Clause Opus Functionality](#clause-opus-functionality)  
6. [Running the App](#running-the-app)  
7. [Project Structure](#project-structure)  


---

## 📖 Overview

OMANI Therapist is a full-stack mental-health chat interface combining:

- **Azure OpenAI** for large-language-model prompts and responses  
- **GROQ API** for structured content queries  
- **Clause Opus**: a bespoke text-segmentation engine that parses user input into semantic “clauses” for more accurate context handling.

---

## ✨ Features

- Interactive, real-time chat interface  
- Bilingual support (English / Arabic with RTL compatible UI)  
- Voice recording & transcription (via Whisper)  
- Clause Opus segmentation for richer context management  
- System health & emergency contact panel

---

## 📋 Prerequisites

- Node.js (>= 16.x) & npm  
- Python (>= 3.10)  
- Access to an Azure OpenAI resource  
- A GROQ-enabled content store (e.g., Sanity, custom service)

---

## ⚡ Getting Started

1. Clone this repo  
2. `cd Mental Health`  
3. Install back-end Python requirements:  
   ```powershell
   pip install -r backend/requirements.txt
