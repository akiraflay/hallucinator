"""
Test script to verify OpenRouter API connection
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_connection():
    """Test basic OpenRouter API connection"""

    print("=" * 60)
    print("OpenRouter API Connection Test")
    print("=" * 60)

    # Check if API key exists
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
        print("   Make sure you have a .env file with OPENROUTER_API_KEY=your_key")
        return False

    # Display masked API key
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    print(f"✓ API Key found: {masked_key}")
    print(f"  Key length: {len(api_key)} characters")
    print(f"  Key starts with: {api_key[:10]}...")
    print()

    # Initialize OpenRouter client
    print("Initializing OpenRouter client...")
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Hallucinator - Legal Benchmark Generator",
            }
        )
        print("✓ Client initialized successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR initializing client: {str(e)}")
        return False

    # Test API call with a simple model
    print("Testing API call with anthropic/claude-sonnet-4.5...")
    print("Sending test message: 'Say hello in one word'")
    print()

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "user", "content": "Say hello in one word"}
            ],
            max_tokens=10,
            temperature=0
        )

        print("✅ SUCCESS! API call completed")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Model used: {response.model}")
        print(f"   Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR during API call: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print()

        # Check for common error patterns
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str or "credentials" in error_str:
            print("💡 This appears to be an authentication error. Possible causes:")
            print("   1. Invalid or expired API key")
            print("   2. API key doesn't have proper permissions")
            print("   3. Check your API key at: https://openrouter.ai/keys")
        elif "404" in error_str:
            print("💡 Model not found. The model ID might be incorrect.")
        elif "429" in error_str:
            print("💡 Rate limit exceeded. Wait a moment and try again.")
        elif "500" in error_str or "503" in error_str:
            print("💡 Server error. OpenRouter might be experiencing issues.")

        return False

def test_multiple_models():
    """Test connection with multiple models"""

    print("\n" + "=" * 60)
    print("Testing Multiple Models")
    print("=" * 60)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ API key not found")
        return

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Hallucinator - Legal Benchmark Generator",
        }
    )

    # Test models from your app
    test_models = [
        "anthropic/claude-sonnet-4.5",
        "anthropic/claude-haiku-4.5",
        "openai/gpt-4o-mini"
    ]

    results = []

    for model in test_models:
        print(f"\nTesting {model}...", end=" ")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Reply with just 'OK'"}],
                max_tokens=5,
                temperature=0
            )
            print(f"✅ Works! Response: {response.choices[0].message.content}")
            results.append((model, "✅ Success"))
        except Exception as e:
            error_msg = str(e)[:100]  # First 100 chars
            print(f"❌ Failed: {error_msg}")
            results.append((model, f"❌ {error_msg}"))

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for model, status in results:
        print(f"{status} - {model}")

if __name__ == "__main__":
    # Run basic test
    success = test_openrouter_connection()

    if success:
        # If basic test passes, try multiple models
        test_multiple_models()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
