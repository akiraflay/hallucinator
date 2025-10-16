# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hallucinator is a Streamlit-based web application for generating and evaluating legal multiple-choice questions using OpenRouter's multi-model API. The app features two main workflows: question generation with streaming output and model evaluation on a question bank.

## Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key (required before running)
# Create .env file with: OPENROUTER_API_KEY=your_actual_api_key_here
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run app.py

# Test OpenRouter API connection
python test_openrouter.py
```

## Architecture

### Core Components

**app.py** - Single-file Streamlit application with two main tabs:
- **Generate Questions Tab**: Generates legal MCQs using streaming API calls, displays each question for review, and saves approved questions to `questions.json`
- **Evaluate Tab**: Tests multiple models on the question bank and stores results in `eval_results.json`

### Data Flow

1. **Question Generation**:
   - User selects topic, model, and quantity → `generate_question_stream()` makes streaming API calls → Chunks displayed in real-time → User reviews → Approved questions saved with auto-incrementing IDs to `questions.json`

2. **Model Evaluation**:
   - User selects models → `evaluate_question()` called for each question-model pair → Results aggregated and saved to `eval_results.json` → Rankings displayed with accuracy percentages

### Session State Management

The app uses Streamlit session state for multi-step workflows:
- `generated_questions`: List of generated questions awaiting review
- `current_question_idx`: Index for pagination through generated questions
- `generation_complete`: Flag to track when all questions are reviewed

### API Integration

OpenRouter client is initialized with:
- Base URL: `https://openrouter.ai/api/v1`
- Custom headers: `HTTP-Referer` and `X-Title` for request attribution
- Uses OpenAI SDK for compatibility

**Model IDs**: Display names in `MODELS` dict map to OpenRouter API IDs (e.g., "Sonnet 4.5" → "anthropic/claude-sonnet-4.5"). Verify model availability at openrouter.ai/models if errors occur.

### Styling

Custom CSS uses gradient-based dark theme:
- Primary gradient: cyan (#00D9FF) to purple (#7B2FFF)
- Background layers: #0E1117 (base), #1E2130 (secondary), #252838 (cards)
- Styled components: buttons, question cards, option boxes, progress bars, status indicators, JSON streaming container

## Key Implementation Details

### Streaming Question Generation
`generate_question_stream()` uses `stream=True` and yields chunks for real-time display. Final chunk includes `{"parsed": question_data}` after JSON parsing, or `{"error": message}` on failure.

### JSON Storage
- `questions.json`: Stores approved questions with auto-incrementing IDs and timestamps
- `eval_results.json`: Stores evaluation results with question_id, model, selected answer, correctness, and timestamp

### Answer Extraction
`evaluate_question()` uses temperature=0 and max_tokens=10 for deterministic answers. Extracts first A/B/C/D character from response to handle verbose outputs.

## Legal Topics
The app supports 6 legal domains: Criminal Procedure, Evidence, Professional Ethics, Sentencing, Bail & Pretrial, Constitutional Criminal Law. Question prompts emphasize federal law and public defender relevance.

## Environment Variables
- `OPENROUTER_API_KEY`: Required - obtain from openrouter.ai/keys
