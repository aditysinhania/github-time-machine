import asyncio
import json
import logging
import re
from typing import Dict, List, Optional

from core.config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Prompt Templates
# ─────────────────────────────────────────────────────────────

SUMMARY_PROMPT = """You are a senior software engineer analyzing a GitHub repository.

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

Respond ONLY with valid JSON in exactly this format:

{{
  "purpose":"...",
  "risks":["..."],
  "strengths":["..."],
  "recommendations":["..."],
  "summary":"..."
}}
"""

CHAT_SYSTEM_PROMPT = """You are an expert software engineering assistant.

You have analyzed the following GitHub repository.

Repository Context:
{context}

Rules:

- Answer using only the repository context.
- If something is unknown, say so.
- Keep answers concise.
- Use markdown where appropriate.
"""


# ─────────────────────────────────────────────────────────────
# Base Provider
# ─────────────────────────────────────────────────────────────

class AIProvider:

    async def complete(self, prompt: str) -> str:
        raise NotImplementedError

    async def chat(
        self,
        system: str,
        messages: List[Dict]
    ) -> str:
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────
# Gemini Provider
# ─────────────────────────────────────────────────────────────

class GeminiProvider(AIProvider):

    def __init__(self):

        import google.generativeai as genai

        genai.configure(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = genai.GenerativeModel(
            "gemini-2.0-flash"
        )

    async def complete(
        self,
        prompt: str
    ) -> str:

        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )

        return response.text.strip()

    async def chat(
        self,
        system: str,
        messages: List[Dict]
    ) -> str:

        history = []

        for message in messages[:-1]:

            history.append(
                {
                    "role": (
                        "user"
                        if message["role"] == "user"
                        else "model"
                    ),
                    "parts": [
                        message["content"]
                    ],
                }
            )

        chat = self.model.start_chat(
            history=history
        )

        if history:
            prompt = messages[-1]["content"]
        else:
            prompt = (
                f"{system}\n\n"
                f"{messages[-1]['content']}"
            )

        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message(prompt)
        )

        return response.text.strip()


# ─────────────────────────────────────────────────────────────
# OpenAI Provider
# ─────────────────────────────────────────────────────────────

class OpenAIProvider(AIProvider):

    def __init__(self):

        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    async def complete(
        self,
        prompt: str
    ) -> str:

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )

    async def chat(
        self,
        system: str,
        messages: List[Dict],
    ) -> str:

        openai_messages = [
            {
                "role": "system",
                "content": system,
            }
        ]

        openai_messages.extend(messages)

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.5,
            max_tokens=512,
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )


# ─────────────────────────────────────────────────────────────
# Groq Provider
# ─────────────────────────────────────────────────────────────

class GroqProvider(AIProvider):

    def __init__(self):

        from groq import AsyncGroq

        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

    async def complete(
        self,
        prompt: str,
    ) -> str:

        response = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )

    async def chat(
        self,
        system: str,
        messages: List[Dict],
    ) -> str:

        groq_messages = [
            {
                "role": "system",
                "content": system,
            }
        ]

        groq_messages.extend(messages)

        response = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=groq_messages,
            temperature=0.5,
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )


# ─────────────────────────────────────────────────────────────
# Provider Factory
# ─────────────────────────────────────────────────────────────

def _get_provider() -> AIProvider:

    provider = settings.AI_PROVIDER.lower()

    if provider == "gemini":

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing."
            )

        return GeminiProvider()

    elif provider == "openai":

        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is missing."
            )

        return OpenAIProvider()

    elif provider == "groq":

        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is missing."
            )

        return GroqProvider()

    raise RuntimeError(
        f"Unsupported AI provider: {provider}"
    )


# ─────────────────────────────────────────────────────────────
# AI Service
# ─────────────────────────────────────────────────────────────

class AIService:
    """
    Unified AI service supporting Gemini, OpenAI and Groq.
    """

    def __init__(self):

        try:
            self._provider: Optional[AIProvider] = _get_provider()

        except Exception as e:

            logger.warning(
                f"AI provider unavailable: {e}"
            )

            self._provider = None

    def _build_context(
        self,
        repo_data: Dict,
    ) -> str:

        return (
            f"Repository: {repo_data.get('full_name', 'Unknown')}\n"
            f"Language: {repo_data.get('primary_language', 'Unknown')}\n"
            f"Total commits: {repo_data.get('total_commits', 0)}\n"
            f"Contributors: {repo_data.get('total_contributors', 0)}\n"
            f"Repository age: {repo_data.get('age_days', 0)} days\n"
            f"Health score: {repo_data.get('health_score', 0)}/100\n"
            f"Bus factor: {repo_data.get('bus_factor_score', 0)}/100\n"
            f"Top contributor: "
            f"{repo_data.get('top_contributor', 'N/A')} "
            f"({repo_data.get('top_pct', 0)}%)\n"
            f"High risk files: "
            f"{', '.join(repo_data.get('high_risk_files', []))}\n"
            f"Modules: "
            f"{', '.join(repo_data.get('modules', []))}"
        )

    # ───────────────────────────────────────────────

    async def generate_summary(
        self,
        repo_data: Dict,
    ) -> Dict:

        if not self._provider:
            return self._fallback_summary(repo_data)

        prompt = SUMMARY_PROMPT.format(
            full_name=repo_data.get(
                "full_name",
                "unknown/unknown",
            ),
            language=repo_data.get(
                "primary_language",
                "Unknown",
            ),
            total_commits=repo_data.get(
                "total_commits",
                0,
            ),
            total_contributors=repo_data.get(
                "total_contributors",
                0,
            ),
            age_days=repo_data.get(
                "age_days",
                0,
            ),
            health_score=repo_data.get(
                "health_score",
                0,
            ),
            bus_factor_score=repo_data.get(
                "bus_factor_score",
                0,
            ),
            top_contributor=repo_data.get(
                "top_contributor",
                "N/A",
            ),
            top_pct=repo_data.get(
                "top_pct",
                0,
            ),
            high_risk_files=", ".join(
                repo_data.get(
                    "high_risk_files",
                    [],
                )
            ),
            modules=", ".join(
                repo_data.get(
                    "modules",
                    [],
                )
            ),
        )

        try:

            raw = await self._provider.complete(prompt)

            raw = re.sub(
                r"```json|```",
                "",
                raw,
            ).strip()

            return json.loads(raw)

        except Exception as e:

            logger.exception(
                "AI summary failed"
            )

            return self._fallback_summary(
                repo_data
            )

    # ───────────────────────────────────────────────

    async def chat(
        self,
        repo_data: Dict,
        messages: List[Dict],
    ) -> str:

        if not self._provider:

            return (
                "AI provider is not configured.\n\n"
                "Please configure one of:\n"
                "- Gemini\n"
                "- OpenAI\n"
                "- Groq"
            )

        system = CHAT_SYSTEM_PROMPT.format(
            context=self._build_context(
                repo_data
            )
        )

        try:

            return await self._provider.chat(
                system,
                messages,
            )

        except Exception as e:

            logger.exception(
                "AI chat failed"
            )

            return (
                f"{type(e).__name__}: {e}"
            )

    # ───────────────────────────────────────────────

    @staticmethod
    def _fallback_summary(
        repo_data: Dict,
    ) -> Dict:

        return {

            "purpose":
                f"A software repository named "
                f"{repo_data.get('full_name', 'Unknown')}.",

            "risks": [
                "AI provider unavailable."
            ],

            "strengths": [
                f"{repo_data.get('total_commits', 0)} commits analysed.",
                f"{repo_data.get('total_contributors', 0)} contributors detected.",
            ],

            "recommendations": [
                "Configure Gemini, OpenAI or Groq.",
                "Review repository health metrics.",
                "Reduce high-risk files if possible.",
            ],

            "summary":
                f"{repo_data.get('full_name', 'Repository')} "
                f"contains "
                f"{repo_data.get('total_commits', 0)} commits "
                f"from "
                f"{repo_data.get('total_contributors', 0)} contributors "
                f"with a repository health score of "
                f"{repo_data.get('health_score', 0)}/100."
        }
