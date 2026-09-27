# 📚 StudyMate AI

An AI-powered study assistant built using **Python, Streamlit, and Google's Gemini API**. StudyMate AI helps students understand concepts, summarize study materials, generate quizzes, and review their learning history.

🌐 **Live Demo:** [Try StudyMate AI](https://studymate-ai-gignmogq5idvjbpcuhcuub.streamlit.app/)

## ✨ Features

* **💬 AI Chat:** Ask questions and get AI-generated answers.
* **📖 Topic Explanation:** Learn concepts with explanations tailored to different difficulty levels.
* **📝 Text Summarization:** Convert lengthy study materials into concise notes.
* **🧠 Quiz Generation:** Generate interactive multiple-choice quizzes and check your answers.
* **🔐 Google Authentication:** Sign in using a Google account.
* **🕘 Personal Chat History:** Store and view conversations associated with your account.

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Frontend:** Streamlit
* **AI Model:** Google Gemini
* **Database:** SQLite
* **Authentication:** Google OAuth / Streamlit authentication
* **Libraries:** `google-genai`, `python-dotenv`, `streamlit`

## 📂 Project Structure

```text
StudyMate-AI/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

> The `.env` file contains local secrets and should not be uploaded to GitHub.

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Aditik2746/StudyMate-AI.git
```

### 2. Navigate to the project

```bash
cd StudyMate-AI
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure your Gemini API key

Create a `.env` file in the project directory:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Never commit this file to GitHub.

For Google sign-in, configure the required Streamlit authentication secrets in your local Streamlit secrets file.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔒 Security

* API keys and OAuth credentials must be kept private.
* The `.env` file and local database should not be committed to GitHub.
* Chat history is associated with the authenticated user's ID.

## 🚀 Future Enhancements

* PDF upload and document-based question answering.
* Persistent cloud database storage.
* Personalized study recommendations.
* More quiz types and learning analytics.

## 👩‍💻 Author

**Aditi**

Built as a hands-on project while learning Generative AI and Python application development.
