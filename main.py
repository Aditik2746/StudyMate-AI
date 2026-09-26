import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found in .env file")

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Create a chat session with conversation memory
chat = client.chats.create(model="gemini-3.5-flash-lite")


def chat_with_ai():
    """Chat with StudyMate AI."""

    question = input("\nAsk your question: ")

    response = chat.send_message(f"""
    You are StudyMate AI, a helpful study assistant.
    Explain concepts in simple language.
    Use examples wherever possible.
    Keep answers beginner-friendly.

    Student's question: {question}
    """)

    print("\nStudyMate AI:")
    print(response.text)


def explain_topic():
    """Explain a topic in simple language."""

    topic = input("\nEnter the topic you want explained: ")

    response = chat.send_message(f"""
    You are StudyMate AI, a beginner-friendly tutor.

    Explain the following topic:
    {topic}

    Follow this structure:
    1. Simple definition
    2. How it works
    3. A real-world example
    4. Key points to remember
    """)

    print("\nStudyMate AI - Explanation:")
    print(response.text)


def summarize_text():
    """Summarize text into study notes."""

    text = input("\nPaste the text you want to summarize:\n")

    response = chat.send_message(f"""
    You are StudyMate AI, a study assistant.

    Summarize the following text into clear study notes.

    Include:
    1. Main idea
    2. Important points
    3. Key terms
    4. A short conclusion

    Keep the summary concise and easy to understand.

    Text:
    {text}
    """)

    print("\nStudyMate AI - Summary:")
    print(response.text)

def generate_quiz():
    """Generate a multiple-choice quiz on a topic."""

    topic = input("\nEnter the topic for your quiz: ")

    num_questions = input(
        "How many questions do you want? (e.g., 5): "
    )

    response = chat.send_message(f"""
    You are StudyMate AI, a helpful study assistant.

    Create {num_questions} multiple-choice questions
    about the following topic:

    Topic: {topic}

    For each question:
    1. Provide four options: A, B, C, and D.
    2. Clearly mention the correct answer.
    3. Give a short explanation for the answer.

    Keep the questions beginner-friendly.
    """)

    print("\nStudyMate AI - Your Quiz:")
    print(response.text)


# Main program
print("\n===== Welcome to StudyMate AI =====")

while True:
    print("1. Chat with AI")
    print("2. Explain a Topic")
    print("3. Summarize Text")
    print("4. Generate Quiz")
    print("5. Exit")

    choice = input("\nEnter your choice (1-4): ")

    try:
        if choice == "1":
            chat_with_ai()

        elif choice == "2":
            explain_topic()

        elif choice == "3":
            summarize_text()

        elif choice == "4":
            generate_quiz()

        elif choice == "5":
            print("\nHappy learning! Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter 1 to 5.")

    except Exception as e:
        print("\nSomething went wrong:", e)