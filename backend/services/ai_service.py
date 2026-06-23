import logging
from typing import List, Dict, Optional

from core.config import settings

logger = logging.getLogger(__name__)


# ── Prompt templates ──────────────────────────────────────────────────────────
SUMMARY_PROMPT = """You are a senior software engineer analyzing a GitHub repository.
Given the following repository data, provide a structured analysis.

Repository: {full_name}
Language: {language}
Total Commits: {total_commits}
Contributors: {total_contributors}
Age: {age_days} days
Health Score: {health_score}/100
Bus Factor Score: {bus_factor_score}/100
Top Contributor: {top_contributor} owns {top_pct}% of commits
High-risk files: {high_risk_files}
Most active modules: {modules}

Respond ONLY with valid JSON in this exact shape:
{{
  "purpose": "one sentence describing what this project does",
  "risks": ["risk 1", "risk 2", "risk 3"],
  "strengths": ["strength 1", "strength 2"],
  "recommendations": ["action 1", "action 2", "action 3"],
  "summary": "3-4 sentence executive summary of the repository health and state"
}}"""

CHAT_SYSTEM_PROMPT = """You are an expert repository analyst for GitHub Time Machine.
You have deeply analyzed the following repository and answer developer questions about it.

Repository context:
{context}

Rules:
- Be concise and specific (2-5 sentences max per answer)
- Always ground your answer in the repository data provided
- If something is unknown, say so honestly
- Use markdown formatting (bold, bullet points) where helpful
- Focus on actionable insights"""


# ── Provider base ─────────────────────────────────────────────────────────────
class AIProvider:
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError

    async def chat(self, system: str, messages: List[Dict]) -> str:
        raise NotImplementedError


# ── Gemini adapter ────────────────────────────────────────────────────────────
class GeminiProvider(AIProvider):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel("gemini-2.0-flash")

    async def complete(self, prompt: str) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self._model.generate_content(prompt)
        )
        return response.text.strip()

    async def chat(self, system: str, messages: List[Dict]) -> str:
        import asyncio
        # Gemini uses a different conversation format
        history = []
        for m in messages[:-1]:  # all but last
            history.append({
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]],
            })

        chat_session = self._model.start_chat(history=history)
        last_msg = f"{system}\n\n{messages[-1]['content']}" if not history else messages[-1]["content"]

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: chat_session.send_message(last_msg)
        )
        return response.text.strip()


# ── OpenAI adapter ────────────────────────────────────────────────────────────
class OpenAIProvider(AIProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def complete(self, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    async def chat(self, system: str, messages: List[Dict]) -> str:
        openai_msgs = [{"role": "system", "content": system}]
        for m in messages:
            openai_msgs.append({"role": m["role"], "content": m["content"]})

        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_msgs,
            max_tokens=512,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()


# ── Factory ───────────────────────────────────────────────────────────────────
def _get_provider() -> AIProvider:
    if settings.AI_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        return GeminiProvider()
    else:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in .env")
        return OpenAIProvider()


# ── High-level AI service ─────────────────────────────────────────────────────
class AIService:
    """
    Unified AI service. Instantiate once per request or inject as a dependency.
    Falls back gracefully if no API key is configured.
    """

    def __init__(self):
        try:
            self._provider: Optional[AIProvider] = _get_provider()
        except Exception as e:
            logger.warning(f"AI provider unavailable: {e}")
            self._provider = None

    def _build_context(self, repo_data: Dict) -> str:
        return (
            f"Name: {repo_data.get('full_name')}\n"
            f"Language: {repo_data.get('primary_language', 'Unknown')}\n"
            f"Total commits: {repo_data.get('total_commits', 0)}\n"
            f"Contributors: {repo_data.get('total_contributors', 0)}\n"
            f"Age: {repo_data.get('age_days', 0)} days\n"
            f"Health score: {repo_data.get('health_score', 0)}/100\n"
            f"Bus factor score: {repo_data.get('bus_factor_score', 0)}/100\n"
            f"Top contributor: {repo_data.get('top_contributor', 'N/A')} "
            f"({repo_data.get('top_pct', 0)}% of commits)\n"
            f"High-risk files: {', '.join(repo_data.get('high_risk_files', []))}\n"
            f"Modules: {', '.join(repo_data.get('modules', []))}"
        )

    async def generate_summary(self, repo_data: Dict) -> Dict:
        """
        Returns a structured dict:
        {purpose, risks, strengths, recommendations, summary}
        """
        if not self._provider:
            return self._fallback_summary(repo_data)

        prompt = SUMMARY_PROMPT.format(
            full_name=repo_data.get("full_name", "unknown/unknown"),
            language=repo_data.get("primary_language", "Unknown"),
            total_commits=repo_data.get("total_commits", 0),
            total_contributors=repo_data.get("total_contributors", 0),
            age_days=repo_data.get("age_days", 0),
            health_score=repo_data.get("health_score", 0),
            bus_factor_score=repo_data.get("bus_factor_score", 0),
            top_contributor=repo_data.get("top_contributor", "N/A"),
            top_pct=repo_data.get("top_pct", 0),
            high_risk_files=", ".join(repo_data.get("high_risk_files", [])),
            modules=", ".join(repo_data.get("modules", [])),
        )

        try:
            raw = await self._provider.complete(prompt)
            import json, re
            # Strip markdown code fences if present
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"AI summary failed")
            raise

    async def chat(self, repo_data: Dict, messages: List[Dict]) -> str:
        """Multi-turn chat grounded in repository context."""
        if not self._provider:
            return "AI is not configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."

        context = self._build_context(repo_data)
        system = CHAT_SYSTEM_PROMPT.format(context=context)

        try:
            return await self._provider.chat(system, messages)
        except Exception as e:
            logger.error(f"AI chat failed: {e}")
            return f"({type(e).__name__}:{str(e)})"

    @staticmethod
    def _fallback_summary(repo_data: Dict) -> Dict:
        return {
            "purpose": f"A software project hosted at {repo_data.get('full_name', 'unknown')}.",
            "risks": ["AI analysis unavailable — configure GEMINI_API_KEY or OPENAI_API_KEY."],
            "strengths": [f"{repo_data.get('total_commits', 0)} commits in the history."],
            "recommendations": ["Add an AI API key to unlock deep insights."],
            "summary": (
                f"{repo_data.get('full_name', 'This repository')} has "
                f"{repo_data.get('total_commits', 0)} commits from "
                f"{repo_data.get('total_contributors', 0)} contributors "
                f"with a health score of {repo_data.get('health_score', 0)}/100."
            ),
        }
