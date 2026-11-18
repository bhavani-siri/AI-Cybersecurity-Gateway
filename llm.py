# llm.py
# Generates an LLM response using Google Gemini — called ONLY for SAFE prompts.

import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "\n\n❌  GEMINI_API_KEY is missing!\n"
        "    Open the .env file and set:  GEMINI_API_KEY=your_key_here\n"
    )

genai.configure(api_key=GEMINI_API_KEY)

RESPONSE_MODEL = "gemini-1.5-flash"

RESPONSE_SYSTEM = """You are a helpful, knowledgeable, and friendly AI assistant.
Your responses have been cleared by a multi-layer AI security firewall,
so this prompt has been verified as safe.
Be concise, accurate, and genuinely useful.
Never assist with harmful, illegal, or unethical requests."""


def generate_response(prompt: str) -> str:
    """
    Generate a response from Gemini for a SAFE, cleared prompt.
    Returns the response text string.
    """
    try:
        model = genai.GenerativeModel(
            model_name=RESPONSE_MODEL,
            system_instruction=RESPONSE_SYSTEM,
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        return response.text.strip()

    except Exception as e:
        error_msg = str(e)

        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            return "❌ Invalid Gemini API key. Please check your .env file."
        elif "quota" in error_msg.lower():
            return "⚠️ Gemini API quota exceeded. Please try again later."
        else:
            return f"⚠️ LLM error: {error_msg[:200]}"
