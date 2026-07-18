from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY  # Updated naming convention
from src.database import query_historic_facts
from src.search import get_live_news_context

# Define the Pydantic schema for structured output validation
class QuestionSchema(BaseModel):
    question: str = Field(description="The multiple-choice question text.")
    option_a: str = Field(description="Option A text.")
    option_b: str = Field(description="Option B text.")
    option_c: str = Field(description="Option C text.")
    option_d: str = Field(description="Option D text.")
    correct_answer: str = Field(description="Strictly a single letter: A, B, C, or D.")
    explanation: str = Field(description="Detailed background reasoning quoting from the context details.")

class QuizSchema(BaseModel):
    quiz: list[QuestionSchema] = Field(description="A list containing exactly 3 unique multiple-choice questions.")


def compile_quiz_data(sport, difficulty):
    """
    1. Gathers context from ChromaDB (Historical).
    2. Gathers context from DuckDuckGo (Live news).
    3. Blends them inside a grounded prompt.
    4. Connects to Gemini and generates a strictly structured JSON quiz.
    """
    # Create query to run against ChromaDB
    db_query = f"{sport} history cup championships rules records"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=2)
    db_context = "\n".join(db_matches) if db_matches else "No offline historic data recorded."

    # Search the live web
    web_context = get_live_news_context(sport)

    # Combine historical and web contexts
    unified_context = f"=== HISTORICAL FACTS ===\n{db_context}\n\n=== LIVE INTERNET NEWS ===\n{web_context}"

    # Instantiate the modern Google GenAI client
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Constructing a structured system prompt
    system_instruction = (
        "You are an expert sports quiz creator. Your job is to write multiple-choice quizzes "
        "relying strictly on the provided Context. Avoid hallucinations. Do not use facts not "
        "found in the Context below. If facts are scarce, make do with what you have, "
        "but keep details completely accurate to the text context.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}"
    )

    user_prompt = (
        f"Generate exactly 3 unique multiple-choice questions for the sport: {sport}.\n"
        f"Difficulty target: {difficulty}."
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            response_mime_type="application/json",
            response_schema=QuizSchema,
        )
    )

    # response.text is guaranteed to be a valid JSON string matching QuizSchema
    return response.text, unified_context