# app.py
# Flask entry point — loads .env first, then wires all firewall layers.

import os
from dotenv import load_dotenv

# ── IMPORTANT: Load .env BEFORE importing modules that read env vars ──────
load_dotenv()

from flask import Flask, request, jsonify, render_template
from firewall import layer1_keyword_check, layer2_pattern_check
from ai_moderation import layer3_ai_moderation
from scorer import compute_risk_score
from llm import generate_response
from logger import log_request, read_stats

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main firewall endpoint.
    POST JSON: { "prompt": "..." }
    Returns:   { "status", "score", "response", "breakdown" }
    """
    data = request.get_json(silent=True)
    if not data or not data.get("prompt", "").strip():
        return jsonify({"error": "No prompt provided"}), 400

    prompt = data["prompt"].strip()

    # ── Layer 1: Keyword detection ────────────────────────────────────────
    kw_result = layer1_keyword_check(prompt)

    # ── Layer 2: Pattern matching ─────────────────────────────────────────
    pat_result = layer2_pattern_check(prompt)

    # ── Layer 3: AI semantic moderation (Gemini) ──────────────────────────
    # Optimisation: if both Layer 1 & 2 already flag → skip expensive API call
    if kw_result["flagged"] and pat_result["flagged"]:
        ai_result = {
            "label":      "MALICIOUS",
            "confidence": 0.97,
            "reason":     "Blocked by keyword + pattern layers (AI call skipped for speed)",
        }
    else:
        ai_result = layer3_ai_moderation(prompt)   # ← Real Gemini API call

    # ── Compute final risk score ──────────────────────────────────────────
    risk   = compute_risk_score(kw_result, pat_result, ai_result)
    status = risk["status"]
    score  = risk["score"]

    # ── Generate LLM response (SAFE prompts only) ─────────────────────────
    if status == "SAFE":
        llm_response = generate_response(prompt)   # ← Real Gemini API call
    elif status == "SUSPICIOUS":
        llm_response = (
            "⚠️  This prompt was flagged as SUSPICIOUS by the AI firewall.\n"
            "No LLM response was generated. Please rephrase your question."
        )
    else:
        llm_response = (
            "🚫  Request BLOCKED by the AI Cybersecurity Gateway.\n"
            "This prompt was identified as MALICIOUS.\n"
            "No LLM response will be generated. This attempt has been logged."
        )

    # ── Log to logs.txt ───────────────────────────────────────────────────
    log_request(
        prompt=prompt,
        status=status,
        score=score,
        ai_reason=ai_result.get("reason", ""),
    )

    return jsonify({
        "status":    status,
        "score":     score,
        "response":  llm_response,
        "breakdown": risk["breakdown"],
    })


@app.route("/stats", methods=["GET"])
def stats():
    """Return dashboard counts from logs.txt."""
    return jsonify(read_stats())


if __name__ == "__main__":
    print("\n🛡  AI Cybersecurity Gateway")
    print(f"   Gemini API key loaded: {'✅  Yes' if os.getenv('GEMINI_API_KEY') else '❌  Missing — check .env'}")
    print("   Visit: http://127.0.0.1:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
