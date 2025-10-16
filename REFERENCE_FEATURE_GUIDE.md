# Reference Questions Feature Guide

## Overview

The Reference Questions feature allows you to provide unstructured text containing multiple-choice questions as a style/difficulty reference. When generating new questions, the AI will match the characteristics of your reference questions.

## How to Use

### Adding Reference Questions

1. **Open the Reference Dialog**
   - In the "Generate Questions" tab, look for the "📎 Add Reference(s)" button next to the Quantity selector
   - Click the button to open the reference dialog

2. **Paste Your Reference Text**
   - Paste unstructured text containing one or more MCQ questions
   - The text can include:
     - Questions with or without correct answers
     - Various formatting styles
     - Multiple questions in any format

3. **AI Analysis Phase**
   - Click "Confirm" to start analysis
   - Claude Haiku 4.5 will analyze the text and:
     - Extract all MCQ questions found
     - Identify correct answers (if provided)
     - Generate reasoning for correct answers
     - Analyze style, difficulty, and formatting patterns

4. **Handle Incomplete Questions**
   - If any questions are missing correct answers:
     - A dialog will appear asking you to select the correct answer (A/B/C/D)
     - Fill in all missing answers
     - Click "Save Reference with Answers"
   - If all questions have answers, the reference is saved immediately

5. **Success Notification**
   - A toast notification appears: "✅ X MCQ question(s) detected as reference"
   - A reference card appears between the controls and Generate button

### Using References

Once a reference is active:

- **Reference Card Display**
  - Shows the count of reference questions
  - Displays a preview of up to 3 questions
  - Click "📋 View Reference Details" to see:
    - All reference questions with correct answers
    - Style analysis notes
    - Difficulty assessment

- **Generation Behavior**
  - When you click "🚀 Generate Questions", the AI will:
    - Match the style of your reference questions
    - Match the difficulty level
    - Match the length and structure
    - Match the organization patterns
    - Use reference reasoning as examples

### Clearing References

1. **Clear Button**
   - Click the "🗑️ Clear" button on the reference card
   - A confirmation dialog appears

2. **Confirm Clearance**
   - Click "Clear" to remove the reference
   - A toast notification confirms: "Reference cleared"

### Error Handling

The feature will show an error if:
- **No MCQs Detected**: The text doesn't contain any recognizable multiple-choice questions
- **Extraction Failed**: The AI couldn't parse the text properly
- **Invalid Input**: Empty or malformed text was provided

## Technical Details

### What Gets Extracted

For each reference question:
- Question text
- All answer options (A, B, C, D)
- Correct answer
- Generated reasoning explaining why the correct answer is right
- Topic identification
- Difficulty assessment

### Style Analysis

The AI analyzes:
- Question length and complexity
- Answer option formatting
- Scenario-based vs. direct questions
- Use of legal terminology
- Overall difficulty level

### Prompt Integration

When references are active, the generation prompt includes:
- All reference questions with their structure
- Style and difficulty notes
- Instruction to match reference characteristics
- Reference reasoning traces as examples

## Use Cases

1. **Match Existing Exam Style**
   - Paste questions from a previous exam
   - Generate new questions with the same style

2. **Maintain Consistency**
   - Set a reference at the start of a session
   - All generated questions will be consistent

3. **Target Specific Difficulty**
   - Provide questions at your desired difficulty level
   - New questions will match that level

4. **Custom Format Requirements**
   - If you need specific formatting or structure
   - The AI will replicate it in new questions

## Files Modified

- `app.py`: Main application with reference UI and workflow
- `prompts.py`: Centralized prompt management with reference support
- `test_reference_sample.txt`: Sample reference questions for testing

## Session State

References persist during your Streamlit session but are not saved to disk. If you refresh the page, you'll need to re-add your references.
