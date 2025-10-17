# 🎭 Hallucinator

A Streamlit app for generating and evaluating legal multiple-choice questions using OpenRouter API.

## Features

- **Question Generation**: Generate high-quality legal MCQs with streaming text output
- **Model Evaluation**: Test multiple LLM models on your question bank
- **JSON Storage**: Simple file-based storage for questions and results

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key:
     ```
     OPENROUTER_API_KEY=your_actual_api_key_here
     ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## Usage

### Generate Questions
1. Select a legal topic (Criminal Procedure, Evidence, etc.)
2. Choose a model for generation
3. Set the quantity of questions
4. Click "Generate Questions"
5. Review each question and approve/skip/navigate

### Evaluate Models
1. Select models to evaluate (checkboxes)
2. Click "Run Evaluation"
3. Watch real-time results as each model is tested
4. View ranked results with accuracy metrics
5. Download results as JSON

## File Structure

```
hallucinator/
├── app.py                  # Main Streamlit app
├── .streamlit/
│   └── config.toml        # Dark theme configuration
├── questions.json         # Approved questions storage
├── eval_results.json      # Evaluation results storage
├── requirements.txt       # Python dependencies
├── .env                   # API key (create from .env.example)
└── .env.example          # API key template
```

## Supported Models

- Sonnet 4.5
- Opus 4.1
- Haiku 4.5
- GPT 4.5 Thinking
- GPT 4.5
- GPT 4.1
- GPT 4o Mini
- Gemini 2.5 Pro
- Gemini 2.5 Flash

## Technologies

- **Streamlit**: Web framework
- **OpenRouter**: Multi-model LLM API
- **OpenAI SDK**: API client library
- **Python-dotenv**: Environment variable management

## Notes

- Questions are stored locally in `questions.json`
- Evaluation results are stored in `eval_results.json`
- The app uses OpenRouter's API - ensure you have credits
- Model IDs in code may need verification against OpenRouter's actual model names
