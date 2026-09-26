import json
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from database import (
    create_table,
    save_chat,
    get_chat_history,
    clear_chat_history,
)


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
)


# --------------------------------------------------
# 2. GOOGLE LOGIN
# --------------------------------------------------

if not st.user.is_logged_in:
    st.title("📚 StudyMate AI")
    st.write("Your personal AI-powered study assistant.")

    st.info("Sign in with Google to continue.")

    if st.button("🔐 Login with Google", type="primary"):
        st.login()

    st.stop()


# Get the logged-in user's unique Google ID
user_id = st.user["sub"]
user_name = st.user.get("name", "Student")


# --------------------------------------------------
# 3. DATABASE SETUP
# --------------------------------------------------

create_table()


# --------------------------------------------------
# 4. GEMINI API SETUP
# --------------------------------------------------

load_dotenv()

api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY"),
)

if not api_key:
    st.error("Gemini API key is missing. Check your app Secrets.")
    st.stop()


MODEL_NAME = "gemini-3.5-flash-lite"

# Keep the client and chat in the user's Streamlit session
if "client" not in st.session_state:
    st.session_state.client = genai.Client(
        api_key=api_key
    )

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(
        model=MODEL_NAME
    )

client = st.session_state.client
chat = st.session_state.chat


# --------------------------------------------------
# 5. HELPER FUNCTION
# --------------------------------------------------

def ask_gemini(prompt):
    """Send a prompt to Gemini and return its response."""

    response = chat.send_message(prompt)
    return response.text


def save_result(question, answer):
    """Save a conversation for the currently logged-in user."""

    save_chat(user_id, question, answer)


# --------------------------------------------------
# 6. SIDEBAR
# --------------------------------------------------

st.sidebar.title("📚 StudyMate AI")
st.sidebar.write(f"Welcome, {user_name}!")

page = st.sidebar.radio(
    "Choose a feature",
    [
        "💬 Chat with AI",
        "📖 Explain a Topic",
        "📝 Summarize Text",
        "🧠 Generate Quiz",
        "🕘 Chat History",
    ],
)

st.sidebar.divider()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.logout()


# --------------------------------------------------
# 7. CHAT WITH AI
# --------------------------------------------------

if page == "💬 Chat with AI":

    st.title("💬 Chat with AI")
    st.caption("Ask questions and learn something new.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display current session's conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask me anything...")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_gemini(prompt)

                st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

            save_result(prompt, answer)

        except Exception as e:
            st.error(f"Something went wrong: {e}")


# --------------------------------------------------
# 8. EXPLAIN A TOPIC
# --------------------------------------------------

elif page == "📖 Explain a Topic":

    st.title("📖 Explain a Topic")
    st.write("Learn difficult concepts in simple language.")

    topic = st.text_input(
        "Enter a topic",
        placeholder="Example: Machine Learning",
    )

    level = st.selectbox(
        "Explanation level",
        ["Beginner", "Intermediate", "Advanced"],
    )

    if st.button("Explain Topic", type="primary"):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:
            prompt = f"""
            Explain the following topic: {topic}

            Explanation level: {level}

            Use simple language, clear headings,
            examples, and important points.
            """

            try:
                with st.spinner("Preparing explanation..."):
                    answer = ask_gemini(prompt)

                st.subheader(f"Explanation: {topic}")
                st.markdown(answer)

                save_result(
                    f"Explain topic: {topic} ({level})",
                    answer,
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")


# --------------------------------------------------
# 9. SUMMARIZE TEXT
# --------------------------------------------------

elif page == "📝 Summarize Text":

    st.title("📝 Summarize Text")
    st.write("Turn long text into concise notes.")

    text_input = st.text_area(
        "Paste your text here",
        height=250,
        placeholder="Paste your notes or study material...",
    )

    summary_length = st.selectbox(
        "Summary length",
        ["Short", "Medium", "Detailed"],
    )

    if st.button("Summarize", type="primary"):

        if not text_input.strip():
            st.warning("Please enter some text.")

        else:
            prompt = f"""
            Summarize the following text.

            Summary length: {summary_length}

            Preserve the important information.
            Use clear headings and bullet points where useful.

            TEXT:
            {text_input}
            """

            try:
                with st.spinner("Summarizing..."):
                    answer = ask_gemini(prompt)

                st.subheader("Summary")
                st.markdown(answer)

                save_result(
                    f"Summarize text ({summary_length})",
                    answer,
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")


# --------------------------------------------------
# 10. GENERATE QUIZ
# --------------------------------------------------

elif page == "🧠 Generate Quiz":

    st.title("🧠 Generate Quiz")
    st.write("Test your understanding of a topic.")

    quiz_topic = st.text_input(
        "Enter a topic for the quiz",
        placeholder="Example: Python, DBMS, Machine Learning",
    )

    num_questions = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5,
    )

    if st.button("Generate Quiz", type="primary"):

        if not quiz_topic.strip():
            st.warning("Please enter a topic.")

        else:
            prompt = f"""
            Create exactly {num_questions} multiple-choice
            questions about: {quiz_topic}

            Return ONLY valid JSON in this format:
            {{
                "questions": [
                    {{
                        "question": "Question text",
                        "options": [
                            "Option A",
                            "Option B",
                            "Option C",
                            "Option D"
                        ],
                        "answer": "Option A",
                        "explanation": "Why this answer is correct"
                    }}
                ]
            }}

            The answer must exactly match one of the options.
            Do not include Markdown code fences.
            """

            try:
                with st.spinner("Creating your quiz..."):
                    response = ask_gemini(prompt)

                # Extract JSON if the model adds code fences
                cleaned_response = response.strip()

                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response.replace(
                        "```json", "", 1
                    ).replace("```", "").strip()

                quiz_data = json.loads(cleaned_response)

                questions = quiz_data.get("questions", [])

                if not questions:
                    st.error("No questions were generated.")

                else:
                    st.session_state.quiz_data = questions
                    st.session_state.quiz_topic = quiz_topic
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}

                    save_result(
                        f"Generate quiz: {quiz_topic}",
                        f"Generated {len(questions)} quiz questions.",
                    )

            except Exception as e:
                st.error(
                    "Could not generate the quiz. "
                    "Please try again."
                )
                st.caption(str(e))

    # Display the generated quiz
    if "quiz_data" in st.session_state:

        questions = st.session_state.quiz_data

        st.subheader(
            f"Quiz: {st.session_state.quiz_topic}"
        )

        with st.form("quiz_form"):

            selected_answers = {}

            for i, question in enumerate(questions):

                st.markdown(
                    f"**Q{i + 1}. {question['question']}**"
                )

                selected_answers[i] = st.radio(
                    "Choose your answer:",
                    question["options"],
                    key=f"quiz_question_{i}",
                    index=None,
                )

                st.divider()

            submitted = st.form_submit_button(
                "Submit Quiz",
                type="primary",
            )

        if submitted:

            st.session_state.quiz_answers = selected_answers
            st.session_state.quiz_submitted = True

        if st.session_state.get("quiz_submitted", False):

            score = 0

            for i, question in enumerate(questions):

                chosen = st.session_state.quiz_answers.get(i)
                correct = question["answer"]

                if chosen == correct:
                    score += 1
                    st.success(f"Q{i + 1}: Correct!")

                else:
                    st.error(
                        f"Q{i + 1}: Incorrect. "
                        f"Correct answer: {correct}"
                    )

                st.write(
                    f"**Explanation:** {question['explanation']}"
                )

            st.subheader(
                f"Your score: {score} / {len(questions)}"
            )

            if st.button("Try Another Quiz"):
                del st.session_state.quiz_data
                st.session_state.pop("quiz_answers", None)
                st.session_state.pop("quiz_submitted", None)
                st.rerun()


# --------------------------------------------------
# 11. CHAT HISTORY
# --------------------------------------------------

elif page == "🕘 Chat History":

    st.title("🕘 Your Chat History")

    st.write(
        "Only conversations associated with your "
        "Google account are shown here."
    )

    history = get_chat_history(user_id)

    if not history:
        st.info("You don't have any saved conversations yet.")

    else:
        st.write(f"Total saved conversations: {len(history)}")

        if st.button("🗑️ Clear My Chat History"):

            clear_chat_history(user_id)

            st.success("Your chat history has been cleared.")
            st.rerun()

        for row in history:

            chat_id, question, answer, created_at = row

            with st.expander(
                f"💬 {question[:80]} | {created_at}"
            ):
                st.markdown("**You asked:**")
                st.write(question)

                st.markdown("**StudyMate AI:**")
                st.markdown(answer)