import os
import json
import re
import streamlit as st

from dotenv import load_dotenv
from google import genai

from database import (
    create_table,
    save_chat,
    get_chat_history,
    clear_chat_history
)


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="centered"
)


# ==========================================
# 2. DATABASE INITIALIZATION
# ==========================================

create_table()


# ==========================================
# 3. LOAD API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Gemini API key not found. "
        "Please check your .env file."
    )
    st.stop()


# ==========================================
# 4. INITIALIZE GEMINI
# ==========================================

MODEL_NAME = "gemini-3.5-flash-lite"

# Keep the Gemini client alive during the session
if (
    "client" not in st.session_state
    or "chat" not in st.session_state
):
    st.session_state.client = genai.Client(
        api_key=api_key
    )

    st.session_state.chat = (
        st.session_state.client.chats.create(
            model=MODEL_NAME
        )
    )

# Reuse the same client throughout the app
client = st.session_state.client


# ==========================================
# 5. INITIALIZE SESSION STATE
# ==========================================

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = {}


# ==========================================
# 6. SIDEBAR
# ==========================================

st.sidebar.title("📚 StudyMate AI")

feature = st.sidebar.radio(
    "Choose a feature:",
    [
        "Chat with AI",
        "Explain a Topic",
        "Summarize Text",
        "Generate Quiz",
        "Chat History"
    ]
)


# ==========================================
# FEATURE 1: CHAT WITH AI
# ==========================================

if feature == "Chat with AI":

    st.title("💬 Chat with StudyMate")
    st.caption("Ask questions and learn something new!")

    # Display current conversation
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask your study question..."
    )

    if question:

        # Save and display user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        prompt = f"""
        You are StudyMate AI, a helpful study assistant.

        Explain concepts in simple language.
        Use examples wherever possible.
        Keep answers beginner-friendly.

        Student's question: {question}
        """

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = (
                        st.session_state.chat.send_message(
                            prompt
                        )
                    )

                    answer = response.text

                    st.markdown(answer)

                    # Save question and answer permanently
                    save_chat(question, answer)

                    # Save answer in current session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(
                        f"Something went wrong: {e}"
                    )


# ==========================================
# FEATURE 2: EXPLAIN A TOPIC
# ==========================================

elif feature == "Explain a Topic":

    st.title("📖 Explain a Topic")

    topic = st.text_input(
        "Enter the topic you want explained"
    )

    if st.button("Explain"):

        if topic.strip():

            prompt = f"""
            Explain the topic '{topic}' to a beginner.

            Follow this structure:

            1. Simple definition
            2. How it works
            3. Real-world example
            4. Key points to remember

            Use simple language.
            """

            with st.spinner("Preparing explanation..."):

                try:

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt
                    )

                    st.markdown(response.text)

                except Exception as e:
                    st.error(
                        f"Something went wrong: {e}"
                    )

        else:
            st.warning("Please enter a topic.")


# ==========================================
# FEATURE 3: SUMMARIZE TEXT
# ==========================================

elif feature == "Summarize Text":

    st.title("📝 Summarize Your Notes")

    text = st.text_area(
        "Paste your study material here",
        height=250
    )

    if st.button("Summarize"):

        if text.strip():

            prompt = f"""
            Summarize the following text into
            beginner-friendly study notes.

            Include:

            1. Main idea
            2. Important points
            3. Key terms
            4. Short conclusion

            Keep the summary clear and concise.

            Text:
            {text}
            """

            with st.spinner("Summarizing your notes..."):

                try:

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt
                    )

                    st.markdown(response.text)

                except Exception as e:
                    st.error(
                        f"Something went wrong: {e}"
                    )

        else:
            st.warning("Please paste some text.")


# ==========================================
# FEATURE 4: GENERATE QUIZ
# ==========================================

elif feature == "Generate Quiz":

    st.title("🧠 Generate a Quiz")

    st.write(
        "Choose a topic and test your knowledge!"
    )

    topic = st.text_input(
        "Enter a quiz topic",
        key="quiz_topic"
    )

    num_questions = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    # Generate quiz
    if st.button("Generate Quiz"):

        if topic.strip():

            prompt = f"""
            Create exactly {int(num_questions)}
            multiple-choice questions about:

            Topic: {topic}

            The questions should be beginner-friendly.

            Return ONLY a valid JSON array.
            Do not include markdown or code fences.

            Format:

            [
                {{
                    "question": "Question text?",
                    "options": [
                        "First option",
                        "Second option",
                        "Third option",
                        "Fourth option"
                    ],
                    "answer": 0,
                    "explanation": "Explain the correct answer."
                }}
            ]

            Rules:
            - Each question must have four options.
            - The answer must be an integer from 0 to 3.
            - The answer represents the correct option's index.
            - Include a short explanation.
            """

            with st.spinner("Generating your quiz..."):

                try:

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt
                    )

                    result = response.text.strip()

                    # Remove code fences if Gemini adds them
                    result = re.sub(
                        r"^```(?:json)?\s*",
                        "",
                        result,
                        flags=re.IGNORECASE
                    )

                    result = re.sub(
                        r"\s*```$",
                        "",
                        result
                    )

                    quiz = json.loads(result)

                    # Validate quiz
                    if not isinstance(quiz, list) or not quiz:
                        raise ValueError(
                            "Invalid quiz format."
                        )

                    for q in quiz:

                        if not all(
                            key in q
                            for key in [
                                "question",
                                "options",
                                "answer",
                                "explanation"
                            ]
                        ):
                            raise ValueError(
                                "A question is missing information."
                            )

                        if (
                            not isinstance(q["options"], list)
                            or len(q["options"]) != 4
                        ):
                            raise ValueError(
                                "Each question must have four options."
                            )

                        if (
                            not isinstance(q["answer"], int)
                            or isinstance(q["answer"], bool)
                            or q["answer"] not in range(4)
                        ):
                            raise ValueError(
                                "Invalid correct-answer index."
                            )

                    # Store quiz in session state
                    st.session_state.quiz = quiz
                    st.session_state.quiz_submitted = {}

                    # Clear old selections
                    for i in range(20):
                        st.session_state.pop(
                            f"question_{i}",
                            None
                        )

                    st.rerun()

                except Exception as e:
                    st.error(
                        f"Could not generate quiz: {e}"
                    )

        else:
            st.warning("Please enter a quiz topic.")

    # Display quiz
    if st.session_state.quiz:

        st.divider()
        st.subheader("Your Quiz")

        for i, q in enumerate(st.session_state.quiz):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(q["question"])

            selected = st.radio(
                "Select your answer:",
                q["options"],
                index=None,
                key=f"question_{i}",
                disabled=(
                    i in st.session_state.quiz_submitted
                )
            )

            # Submit answer
            if i not in st.session_state.quiz_submitted:

                if st.button(
                    "Submit Answer",
                    key=f"submit_{i}"
                ):

                    if selected is None:

                        st.warning(
                            "Please select an option first."
                        )

                    else:

                        selected_index = (
                            q["options"].index(selected)
                        )

                        st.session_state.quiz_submitted[i] = (
                            selected_index
                        )

                        st.rerun()

            # Reveal answer only after submission
            if i in st.session_state.quiz_submitted:

                selected_index = (
                    st.session_state.quiz_submitted[i]
                )

                if selected_index == q["answer"]:
                    st.success("✅ Correct answer!")

                else:
                    st.error("❌ Incorrect answer.")

                st.write(
                    "**Correct answer:**",
                    q["options"][q["answer"]]
                )

                st.info(
                    f"**Explanation:** {q['explanation']}"
                )

            st.divider()

        # Display score after all answers are submitted
        if len(st.session_state.quiz_submitted) == len(
            st.session_state.quiz
        ):

            score = sum(
                1
                for i, q in enumerate(st.session_state.quiz)
                if (
                    st.session_state.quiz_submitted[i]
                    == q["answer"]
                )
            )

            total = len(st.session_state.quiz)

            st.subheader("🎉 Quiz Completed!")

            st.metric(
                "Your Score",
                f"{score} / {total}"
            )

            st.progress(score / total)

            if st.button("Try Another Quiz"):

                st.session_state.quiz = None
                st.session_state.quiz_submitted = {}

                for i in range(20):
                    st.session_state.pop(
                        f"question_{i}",
                        None
                    )

                st.rerun()


# ==========================================
# FEATURE 5: CHAT HISTORY
# ==========================================

elif feature == "Chat History":

    st.title("🕘 Chat History")

    st.write(
        "Here you can revisit your previous conversations."
    )

    try:

        history = get_chat_history()

        if history:

            st.caption(
                f"You have {len(history)} saved conversations."
            )

            # Display newest conversations first
            for item in history:

                chat_id, user_message, ai_response, created_at = item

                with st.expander(
                    f"💬 {user_message[:70]} "
                    f"— {created_at}"
                ):

                    st.markdown("**Your question:**")
                    st.write(user_message)

                    st.markdown("**StudyMate AI:**")
                    st.markdown(ai_response)

            st.divider()

            if st.button(
                "🗑️ Clear Chat History",
                type="secondary"
            ):

                st.session_state.confirm_clear = True

            if st.session_state.get(
                "confirm_clear",
                False
            ):

                st.warning(
                    "Are you sure you want to delete "
                    "all saved chat history?"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button("Yes, delete"):

                        clear_chat_history()

                        st.session_state.confirm_clear = False

                        st.success(
                            "Chat history deleted."
                        )

                        st.rerun()

                with col2:

                    if st.button("Cancel"):

                        st.session_state.confirm_clear = False

                        st.rerun()

        else:

            st.info(
                "No chat history yet. "
                "Start chatting with StudyMate AI!"
            )

    except Exception as e:

        st.error(
            f"Could not load chat history: {e}"
        )