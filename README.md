# AI-Powered Sports Quiz Generator (RAG Agent)

An interactive, factually grounded web application that generates dynamic multiple-choice sports quizzes using **Retrieval-Augmented Generation (RAG)**. The agent intelligently balances offline historical knowledge from a local vector database with live tournament and news updates crawled directly from the web, eliminating LLM hallucinations.

Built with the modern **Google GenAI SDK**, **ChromaDB**, **Streamlit**, and **DuckDuckGo Search**.

---

## Key Features

*   **Hybrid RAG Architecture:** Fuses historical reference data (ChromaDB vector store) with real-time match details and tournament developments (DuckDuckGo Web Search).
*   **Structured Output Validation:** Leverages Pydantic schemas paired with Gemini's modern structured output config (`response_schema`) to guarantee parseable, reliable JSON payloads.
*   **Adaptive Theme UI:** An engaging, responsive quiz layout built on Streamlit that dynamically scales fonts and colors to match your dark/light browser preferences using CSS variables.
*   **Zero-Default State & Custom Spacing:** Eliminates the classic Streamlit radio button bug that forces pre-selection of option A. The app uses interactive row elements that wait for user input before executing immediate visual grading feedback (green for correct, red for incorrect).
*   **Animated Visual Triggers:** Features custom CSS animations to provide smooth slide-down effects for contextual explanations and fade-in transitions between quiz frames.

---

## Project Architecture

```text
sports-quiz-agent/
│
├── .env                  # Hidden file containing sensitive API keys
├── .gitignore            # Excludes environment files and databases from Git tracking
├── requirements.txt      # Third-party dependency checklist
├── README.md             # Detailed installation and project roadmap
│
├── data/
│   └── sports_facts.json # Local historic database (raw facts in JSON format)
│
├── chroma_db/            # Generated automatically by ChromaDB to store vector embeddings
│
├── src/
│   ├── __init__.py       # Package indicator for module imports
│   ├── config.py         # Manages environment variable extraction
│   ├── database.py       # ChromaDB operations (Embedding population & Keyword queries)
│   ├── search.py         # DuckDuckGo integration for real-time crawling
│   └── generator.py      # Prompt construction, RAG mixing, and Gemini client execution
│
└── app.py                # Frontend Streamlit GUI and interactive state layout

```

---

## Technical Prerequisites & Setup

This repository is optimized for **Python 3.9, 3.10, or 3.11**. (Avoid Python 3.12+ as specific C-dependencies of ChromaDB compile most reliably across these versions).

### 1. Clone the Project Workspace

```bash
git clone [https://github.com/YOUR_USERNAME/sports-quiz-agent.git](https://github.com/YOUR_USERNAME/sports-quiz-agent.git)
cd sports-quiz-agent

```

### 2. Configure Your Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Core Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

### 4. Establish Environment Secrets

Create a `.env` file in the root of the project workspace:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here

```

---

## Running the Application

1. **Populate and Boot the Platform:**
Execute the Streamlit server directly from your terminal workspace. The database script initializes automatically and parses `data/sports_facts.json` during the application initialization handshake.
```bash
streamlit run app.py

```


2. **Interact with the Dashboard:**
* Open the localhost portal displayed in your terminal window (usually `http://localhost:8501`).
* Navigate to the sidebar panel to choose a targeted sport variant and challenge parameter.
* Click **Generate Fresh Quiz** and engage with the dynamically generated animated interface!



---

## Architectural Workflow Overview

1. **User Action:** The client picks a parameter matrix (e.g., *Cricket, Hard*) and clicks "Generate Fresh Quiz".
2. **Local Fact Retrieval (`src/database.py`):** Performs a semantic vector search inside the local ChromaDB vector space matching your target topic.
3. **Live Web Crawling (`src/search.py`):** Queries live web search results to extract tournament metrics and news flashes from the open web using anonymous DuckDuckGo pipelines.
4. **Context Layer Generation (`src/generator.py`):** Both parameters merge inside the backend engine into a unified prompt block alongside system instructions.
5. **Schema Validation Execution:** Gemini processes the prompt matrix using `response_schema=QuizSchema` with the `gemini-2.5-flash-lite` model to deliver strict JSON parameters back to the application layer.
6. **Animated Display UI (`app.py`):** The application parses the payload, locking the questions down into animated, dynamic row triggers that provide real-time interactive evaluation.

```

```
