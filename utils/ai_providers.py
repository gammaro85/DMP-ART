# utils/ai_providers.py
"""
AI Provider Adapters for DMP-ART
Supports OpenAI (ChatGPT) and Anthropic (Claude) APIs
"""

from abc import ABC, abstractmethod
import json
from typing import Tuple, Optional


class AIProvider(ABC):
    """Base interface for AI providers"""

    @abstractmethod
    def generate_feedback(self, dmp_content: str, section_id: str,
                         knowledge_context: str) -> dict:
        """
        Generate feedback for a DMP section

        Args:
            dmp_content: Text content from the DMP section
            section_id: Section identifier (e.g., "1.1", "2.1")
            knowledge_context: Context from knowledge base

        Returns:
            dict with keys: selected_comments, ai_suggestions, quality_score, issues
        """
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to the API

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    def _get_system_prompt(self) -> str:
        """Get the system prompt for DMP review"""
        return """Jesteś doświadczonym data stewardem recenzującym Plan Zarządzania Danymi (DMP)
dla polskich wniosków grantowych NCN. Twoja rola to:

1. Ocena kompletności i jakości odpowiedzi badacza
2. Identyfikacja brakujących informacji
3. Sugestie poprawek zgodnie ze standardami Science Europe
4. Wybór odpowiednich gotowych komentarzy z bazy wiedzy
5. Dodanie własnych sugestii gdy gotowe komentarze nie wystarczą

WAŻNE: Preferuj gotowe komentarze (75% odpowiedzi). Dodawaj własne sugestie tylko gdy konieczne (25%).

Format odpowiedzi - ZAWSZE zwracaj poprawny JSON:
{
    "selected_comments": ["ID_komentarza_1", "ID_komentarza_2"],
    "ai_suggestions": ["Własna sugestia 1", "Własna sugestia 2"],
    "quality_score": 75,
    "issues": ["Zidentyfikowany problem 1", "Problem 2"]
}

Gdzie:
- selected_comments: lista ID wybranych gotowych komentarzy z dostarczonego kontekstu
- ai_suggestions: lista własnych sugestii (max 2-3, krótkie i konkretne)
- quality_score: ocena jakości sekcji 0-100 (0=brak treści, 100=perfekcyjne)
- issues: lista zidentyfikowanych problemów do naprawienia"""

    def _build_prompt(self, dmp_content: str, section_id: str,
                     knowledge_context: str) -> str:
        """Build the user prompt for analysis"""
        return f"""Analizuję sekcję {section_id} planu zarządzania danymi.

=== TREŚĆ SEKCJI OD BADACZA ===
{dmp_content if dmp_content.strip() else "(Sekcja pusta lub bez treści)"}

=== DOSTĘPNE GOTOWE KOMENTARZE (wybierz najbardziej pasujące) ===
{knowledge_context if knowledge_context.strip() else "(Brak gotowych komentarzy dla tej sekcji)"}

=== ZADANIE ===
1. Oceń jakość odpowiedzi badacza (quality_score 0-100)
2. Zidentyfikuj problemy (issues)
3. Wybierz pasujące gotowe komentarze (selected_comments) - preferuj te
4. Dodaj własne sugestie tylko gdy potrzebne (ai_suggestions)

Odpowiedz TYLKO poprawnym JSON bez dodatkowego tekstu."""

    def _parse_response(self, raw_response: str) -> dict:
        """Parse AI response to structured dict"""
        try:
            # Remove markdown code blocks if present
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)

            # Validate required keys
            if "selected_comments" not in result:
                result["selected_comments"] = []
            if "ai_suggestions" not in result:
                result["ai_suggestions"] = []
            if "quality_score" not in result:
                result["quality_score"] = 50
            if "issues" not in result:
                result["issues"] = []

            return result

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw response as a suggestion
            return {
                "selected_comments": [],
                "ai_suggestions": [raw_response[:500] if len(raw_response) > 500 else raw_response],
                "quality_score": 50,
                "issues": [f"Nie udało się sparsować odpowiedzi AI: {str(e)}"]
            }


class OpenAIProvider(AIProvider):
    """Adapter for OpenAI ChatGPT API"""

    def __init__(self, api_key: str, model: str = "gpt-4",
                 temperature: float = 0.3, max_tokens: int = 2000):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_feedback(self, dmp_content: str, section_id: str,
                         knowledge_context: str) -> dict:
        """Generate feedback using OpenAI API"""
        try:
            import openai
        except ImportError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Biblioteka openai nie jest zainstalowana. Uruchom: pip install openai"]
            }

        try:
            client = openai.OpenAI(api_key=self.api_key)

            prompt = self._build_prompt(dmp_content, section_id, knowledge_context)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return self._parse_response(response.choices[0].message.content)

        except Exception as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Błąd OpenAI API: {str(e)}"]
            }

    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to OpenAI API"""
        try:
            import openai
        except ImportError:
            return False, "Biblioteka openai nie jest zainstalowana. Uruchom: pip install openai"

        try:
            client = openai.OpenAI(api_key=self.api_key)
            # Simple test - list models
            client.models.list()
            return True, "Połączenie z OpenAI API udane ✓"
        except openai.AuthenticationError:
            return False, "Błąd autoryzacji: nieprawidłowy klucz API"
        except openai.RateLimitError:
            return False, "Przekroczono limit zapytań API"
        except Exception as e:
            return False, f"Błąd połączenia: {str(e)}"


class AnthropicProvider(AIProvider):
    """Adapter for Anthropic Claude API"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229",
                 temperature: float = 0.3, max_tokens: int = 2000):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_feedback(self, dmp_content: str, section_id: str,
                         knowledge_context: str) -> dict:
        """Generate feedback using Anthropic API"""
        try:
            import anthropic
        except ImportError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Biblioteka anthropic nie jest zainstalowana. Uruchom: pip install anthropic"]
            }

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            prompt = self._build_prompt(dmp_content, section_id, knowledge_context)

            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system=self._get_system_prompt()
            )

            return self._parse_response(message.content[0].text)

        except Exception as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Błąd Anthropic API: {str(e)}"]
            }

    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to Anthropic API"""
        try:
            import anthropic
        except ImportError:
            return False, "Biblioteka anthropic nie jest zainstalowana. Uruchom: pip install anthropic"

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            # Simple test with minimal tokens
            client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            return True, "Połączenie z Anthropic API udane ✓"
        except anthropic.AuthenticationError:
            return False, "Błąd autoryzacji: nieprawidłowy klucz API"
        except anthropic.RateLimitError:
            return False, "Przekroczono limit zapytań API"
        except Exception as e:
            return False, f"Błąd połączenia: {str(e)}"


def get_provider(config: dict) -> Optional[AIProvider]:
    """
    Factory function - returns appropriate provider based on configuration

    Args:
        config: Configuration dict with provider settings

    Returns:
        AIProvider instance or None if configuration is invalid
    """
    provider_name = config.get("provider", "openai")
    api_keys = config.get("api_keys", {})
    model_settings = config.get("model_settings", {}).get(provider_name, {})

    api_key = api_keys.get(provider_name, "")
    if not api_key:
        return None

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=api_key,
            model=model_settings.get("model", "gpt-4"),
            temperature=model_settings.get("temperature", 0.3),
            max_tokens=model_settings.get("max_tokens", 2000)
        )
    elif provider_name == "anthropic":
        return AnthropicProvider(
            api_key=api_key,
            model=model_settings.get("model", "claude-3-sonnet-20240229"),
            temperature=model_settings.get("temperature", 0.3),
            max_tokens=model_settings.get("max_tokens", 2000)
        )
    else:
        raise ValueError(f"Nieznany provider: {provider_name}")
