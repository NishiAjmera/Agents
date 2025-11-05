
# Habit Tracker Agent

This is a simple conversational agent that acts as a friendly wellness coach. It helps users log daily habits and summarize their activity over time.

## Project Structure

- `backend/`: Contains the FastAPI server, agent logic, and tools.
- `frontend/`: Contains the React-based chat interface.

## Setup Instructions

### 1. Backend

**a. Navigate to the backend directory:**

```bash
cd backend
```

**b. Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**c. Install dependencies:**

```bash
pip install -r requirements.txt
```

**d. Set up your Google API Key:**

Create a `.env` file in the `backend` directory by copying the `.env.example` file:

```bash
cp .env.example .env
```

Open the `.env` file and replace `YOUR_GOOGLE_API_KEY` with your actual Google API Key.

**e. Run the FastAPI server:**

```bash
uvicorn main:app --reload
```

The backend server will be running at `http://localhost:8000`.

### 2. Frontend

**a. Navigate to the frontend directory:**

```bash
cd frontend
```

**b. Install dependencies:**

```bash
npm install
```

**c. Start the React app:**

```bash
npm start
```

The frontend will be running at `http://localhost:3000`.

## How to Use

1.  Open your browser and go to `http://localhost:3000`.
2.  You will see a chat interface.
3.  You can log habits by typing messages like:
    - "I ran 5 km today."
    - "I drank 8 glasses of water."
4.  You can ask for a summary of your habits:
    - "Can I get a summary of my habits?"
    - "Show me my weekly summary."

The agent will respond conversationally and log your habits.
