"""
Prompts for Hallucinator - Legal Benchmark Generator & Evaluator
All LLM prompts used throughout the application
"""

def get_question_generation_prompt(topic, reference_data=None):
    """
    Get the prompt for generating a legal MCQ question

    Args:
        topic: The legal topic for the question
        reference_data: Optional dictionary containing reference question data

    Returns:
        String prompt for question generation
    """
    base_requirements = f"""Generate a legal multiple-choice question on the topic of {topic}.

Requirements:
- Create a moderately difficult to difficult question (no easy questions)
- Focus on federal law and broadly applicable legal principles relevant to public defenders
- Provide exactly 4 answer options labeled A, B, C, D
- Make the wrong answers adversarial - they should be plausible and require legal reasoning to rule out
- One answer must be clearly correct
- Include a detailed reasoning trace explaining why the correct answer is right and why the wrong answers are incorrect

Output format (valid JSON only):
{{
    "question": "The question text here",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "C",
    "reasoning": "Detailed explanation of why C is correct and why A, B, D are incorrect"
}}

Respond only with valid JSON, no additional text."""

    if reference_data:
        # Build reference context
        reference_context = "\n\nREFERENCE QUESTIONS TO MATCH:\n"
        reference_context += "Generate questions matching the style, difficulty, length, and structure of these reference questions:\n\n"

        for idx, ref_q in enumerate(reference_data.get('questions', []), 1):
            reference_context += f"Reference Question {idx}:\n"
            reference_context += f"Question: {ref_q.get('question', 'N/A')}\n"
            reference_context += f"Options: {', '.join(ref_q.get('options', []))}\n"
            reference_context += f"Correct Answer: {ref_q.get('correct_answer', 'N/A')}\n"
            if ref_q.get('reasoning'):
                reference_context += f"Reasoning: {ref_q.get('reasoning')}\n"
            reference_context += "\n"

        # Add style notes if available
        if reference_data.get('style_notes'):
            reference_context += f"\nStyle Characteristics:\n{reference_data.get('style_notes')}\n"

        if reference_data.get('difficulty_notes'):
            reference_context += f"\nDifficulty Level: {reference_data.get('difficulty_notes')}\n"

        return reference_context + "\n" + base_requirements

    return base_requirements


EVALUATION_PROMPT_TEMPLATE = """Answer this multiple choice question.

CRITICAL INSTRUCTION: You MUST respond with EXACTLY ONE LETTER: A, B, C, or D. Nothing else.

Question: {question}

{options}

Example CORRECT response: C
Example INCORRECT response: The answer is C because...

Your answer (single letter only):"""


REFERENCE_EXTRACTION_PROMPT = """You are an expert at analyzing and extracting multiple-choice questions from unstructured text.

Analyze the following text and extract ALL multiple-choice questions (MCQs) you find. For each question:
1. Extract the question text
2. Extract all answer options (typically A, B, C, D)
3. Identify the correct answer (if provided)
4. If the correct answer is NOT explicitly stated, mark it as "unknown"
5. Generate a detailed reasoning trace explaining why the correct answer is right (if known) or analyze which answer is most likely correct based on legal principles

Also provide:
- Total count of MCQs found
- Style analysis (question length, complexity, formatting patterns)
- Difficulty assessment (easy, moderate, difficult)
- Topic identification for each question

IMPORTANT: If NO multiple-choice questions are found in the text, return an error in the JSON.

Output format (valid JSON only):
{{
    "count": 3,
    "questions": [
        {{
            "question": "Question text here",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct_answer": "C",
            "reasoning": "Detailed explanation...",
            "topic": "Criminal Procedure",
            "has_answer": true
        }}
    ],
    "style_notes": "Questions are detailed, scenario-based, approximately 2-3 sentences long...",
    "difficulty_notes": "Moderate to difficult, requires application of legal principles...",
    "error": null
}}

If no MCQs found:
{{
    "count": 0,
    "questions": [],
    "error": "No multiple-choice questions detected in the provided text."
}}

Text to analyze:
{reference_text}

Respond only with valid JSON, no additional text."""


def get_evaluation_prompt(question, options):
    """
    Get the prompt for evaluating a question

    Args:
        question: The question text
        options: List of option strings

    Returns:
        String prompt for evaluation
    """
    options_text = "\n".join(options)
    return EVALUATION_PROMPT_TEMPLATE.format(question=question, options=options_text)


def get_reference_extraction_prompt(reference_text):
    """
    Get the prompt for extracting reference questions

    Args:
        reference_text: The unstructured text containing MCQs

    Returns:
        String prompt for reference extraction
    """
    return REFERENCE_EXTRACTION_PROMPT.format(reference_text=reference_text)
