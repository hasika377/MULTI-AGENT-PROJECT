# 🚀 Quick Start Guide - Complete Workflow

## 5-Minute Quick Start

### Step 1: Get Your Gemini API Key (1 min)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the key

### Step 2: Setup Project (2 min)

**For Windows:**
```bash
setup.bat
```

**For Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 3: Configure API Key (1 min)
Create `.env` file in project root:
```
GEMINI_API_KEY=your_actual_key_here
```

### Step 4: Run Everything (1 min)

**Terminal 1 - Start Backend:**
```bash
python main.py
```
You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run app.py
```
Browser opens automatically with Streamlit UI

**Terminal 3 (Optional) - Run Tests:**
```bash
python tester_agent.py
```

**Optional - Run Security Scans:**
```bash
security_scan.bat
```

Or run the tools directly:
```bash
bandit -r . -x ./venv,./__pycache__
pip-audit
```

---

## Complete Workflow

### 1️⃣ **Development Phase** (Backend)

**What happens:**
- FastAPI server starts
- Endpoints become available
- Ready for testing

**Check it works:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Gemini API Wrapper is running"
}
```

---

### 2️⃣ **Testing Phase** (Validation)

**Option A: Automated Tests**
```bash
python tester_agent.py
```

Output example:
```
============================================================
🧪 GEMINI API WRAPPER - AUTOMATED TESTING
============================================================

[TEST 1] Health Check Endpoint
✓ PASSED: Health check successful

[TEST 2] Get API Info Endpoint
✓ PASSED: API info retrieved
  Available endpoints: ['GET /health', 'POST /chat', ...]

[TEST 3] Send Valid Prompt to Chat Endpoint
✓ PASSED: Valid prompt processed
  Prompt: What is FastAPI?
  Response: FastAPI is a modern, free, open source...

...

📊 TEST SUMMARY
============================================================
✓ Passed: 6
✗ Failed: 0
📈 Success Rate: 100.0%
============================================================
```

**Option B: Manual Testing with Postman**
1. Open Postman
2. Click "Import"
3. Select `Gemini_API_Wrapper.postman_collection.json`
4. Click on "Send Chat Prompt"
5. Click "Send" button
6. View response

**Option C: Browser API Docs**
1. Open `http://localhost:8000/docs`
2. Find "POST /chat" endpoint
3. Click "Try it out"
4. Enter a prompt
5. Click "Execute"

---

### 3️⃣ **Deployment Phase** (User Interface)

**What happens:**
- Streamlit UI starts
- Browser opens automatically
- Non-developers can use the app

**How to use:**
1. Type a prompt in the text area
2. Click "Send"
3. AI responds in the chat
4. History saved automatically
5. Clear anytime with "Clear Chat" button

**Example prompts to try:**
- "What is Python?"
- "Explain machine learning in simple terms"
- "How does the internet work?"

---

## File Structure Explained

```
multi agent project/
├── main.py                                    # 🔵 Developer Agent
│   └── FastAPI backend with Gemini integration
│
├── tester_agent.py                            # 🟢 Tester Agent
│   └── Automated tests for all endpoints
│
├── app.py                                     # 🟡 Deployment Agent
│   └── Streamlit UI for non-developers
│
├── requirements.txt                           # Dependencies
│   └── FastAPI, Streamlit, requests, etc.
│
├── .env.example                               # Configuration template
│   └── Copy to .env and add your API key
│
├── Gemini_API_Wrapper.postman_collection.json # 🔴 Postman Tests
│   └── Import this into Postman for manual testing
│
├── README.md                                  # Detailed documentation
├── ARCHITECTURE.md                            # System design
├── QUICK_START.md                             # This file
│
└── setup.bat / setup.sh                       # Auto-setup scripts
    └── Run once to install everything
```

---

## Troubleshooting

### ❌ "GEMINI_API_KEY environment variable not set"
**Solution:**
1. Create `.env` file in project root (copy from `.env.example`)
2. Add your actual API key
3. Restart the server with `python main.py`

### ❌ "Connection refused" or "Cannot connect to API"
**Solution:**
1. Make sure `python main.py` is running in Terminal 1
2. Check that both terminals show no errors
3. Verify port 8000 is not blocked by firewall

### ❌ "Request timeout" in Streamlit
**Solution:**
1. Gemini API can be slow - wait longer
2. Try a shorter prompt
3. Check internet connection
4. Verify API key is valid

### ❌ "Tests are failing"
**Solution:**
1. Run `python main.py` first (backend must be running)
2. Check `.env` file has correct API key
3. Run tests again: `python tester_agent.py`

### Security Scan Commands
Use these after installing requirements:
```bash
bandit -r . -x ./venv,./__pycache__
pip-audit
```

Or run the helper script:
```bash
security_scan.bat
```

---

## Multi-Agent Workflow Summary

```
┌─────────────────────────────────┐
│ USER DESCRIBES API NEED          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ DEVELOPER AGENT                  │
│ (main.py - Creates FastAPI)      │
│ ✓ Generates endpoints            │
│ ✓ Handles Gemini integration     │
│ ✓ Validates requests             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ TESTER AGENT                     │
│ (tester_agent.py - Validates)    │
│ ✓ Tests all endpoints            │
│ ✓ Checks error handling          │
│ ✓ Validates response format      │
└────────────┬────────────────────┘
             │
        Tests Pass?
        │        │
       YES      NO ──→ [LOOP: Developer fixes issues]
        │
        ▼
┌─────────────────────────────────┐
│ POSTMAN TESTING                  │
│ (Manual verification)            │
│ ✓ User explores endpoints        │
│ ✓ Confirms features work         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ DEPLOYMENT AGENT                 │
│ (app.py - Streamlit UI)          │
│ ✓ User-friendly interface        │
│ ✓ Non-developers can use it      │
└─────────────────────────────────┘
```

---

## Running Everything at Once (Advanced)

**PowerShell (Windows):**
```powershell
Start-Process python -ArgumentList "main.py"
Start-Sleep -Seconds 2
Start-Process cmd -ArgumentList "/c streamlit run app.py"
```

**Bash (Mac/Linux):**
```bash
python main.py &
sleep 2
streamlit run app.py
```

---

## What Each Agent Does

| Agent | File | Purpose | Starts on | Success Indicator |
|-------|------|---------|-----------|-------------------|
| Developer | `main.py` | Backend API | `python main.py` | "Uvicorn running on..." |
| Tester | `tester_agent.py` | Validation | `python tester_agent.py` | "100% Success Rate" |
| Deployment | `app.py` | UI | `streamlit run app.py` | Browser opens automatically |

---

## Next: Advanced Customization

After getting everything running:

1. **Add more endpoints** - Edit `main.py` to add new routes
2. **Custom models** - Try different Gemini models
3. **Database** - Add SQLite to store conversations
4. **Authentication** - Add API key protection
5. **Deployment** - Use Streamlit Cloud or Docker

---

## Getting Help

- **Browser docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)
- **Error messages**: Check terminal output for detailed errors
- **API responses**: View response in Postman/Streamlit for details

---

🎉 **You're all set! Enjoy your Gemini API wrapper!**

