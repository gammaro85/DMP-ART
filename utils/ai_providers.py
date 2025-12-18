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

    @abstractmethod
    def list_models(self) -> dict:
        """
        List available models from the provider

        Returns:
            dict with keys: success (bool), models (list of dicts with id, name, description)
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

        except openai.AuthenticationError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Błąd autoryzacji: nieprawidłowy klucz API OpenAI"]
            }
        except openai.RateLimitError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Przekroczono limit zapytań API OpenAI"]
            }
        except openai.APIError as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Błąd API OpenAI: {str(e)}"]
            }
        except Exception as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Nieoczekiwany błąd OpenAI: {str(e)}"]
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

    def list_models(self) -> dict:
        """List available OpenAI models"""
        try:
            import openai
        except ImportError:
            return {
                "success": False,
                "models": [],
                "error": "Biblioteka openai nie jest zainstalowana"
            }

        try:
            client = openai.OpenAI(api_key=self.api_key)
            models_response = client.models.list()

            # Filter only chat models (gpt-* models)
            chat_models = []
            model_descriptions = {
                "gpt-4o": "GPT-4o (najnowszy - REKOMENDOWANY)",
                "gpt-4o-mini": "GPT-4o Mini (szybki i tani)",
                "gpt-4-turbo": "GPT-4 Turbo",
                "gpt-4-turbo-preview": "GPT-4 Turbo Preview",
                "gpt-4": "GPT-4",
                "gpt-3.5-turbo": "GPT-3.5 Turbo (przestarzały, tani)",
                "gpt-3.5-turbo-16k": "GPT-3.5 Turbo 16K"
            }

            for model in models_response.data:
                model_id = model.id
                # Filter for chat completion models
                if model_id.startswith("gpt-") and not model_id.endswith(":latest"):
                    # Use known descriptions or generate from ID
                    description = model_descriptions.get(model_id, model_id.upper())
                    chat_models.append({
                        "id": model_id,
                        "name": description,
                        "recommended": model_id == "gpt-4o"
                    })

            # Sort: recommended first, then by name
            chat_models.sort(key=lambda x: (not x["recommended"], x["id"]))

            return {
                "success": True,
                "models": chat_models
            }

        except openai.AuthenticationError:
            return {
                "success": False,
                "models": [],
                "error": "Błąd autoryzacji: nieprawidłowy klucz API"
            }
        except Exception as e:
            return {
                "success": False,
                "models": [],
                "error": f"Błąd podczas pobierania modeli: {str(e)}"
            }


class AnthropicProvider(AIProvider):
    """Adapter for Anthropic Claude API"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929",
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

        except anthropic.AuthenticationError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Błąd autoryzacji: nieprawidłowy klucz API Anthropic"]
            }
        except anthropic.RateLimitError:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": ["Przekroczono limit zapytań API Anthropic"]
            }
        except anthropic.APIError as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Błąd API Anthropic: {str(e)}"]
            }
        except Exception as e:
            return {
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Nieoczekiwany błąd Anthropic: {str(e)}"]
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

    def list_models(self) -> dict:
        """List available Anthropic Claude models (static list)"""
        # Anthropic API doesn't have a models.list() endpoint
        # We maintain a static list of available models based on official docs
        # Source: https://platform.claude.com/docs/en/about-claude/models
        models = [
            # Claude 4.5 - Latest models (December 2025)
            {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5 (wrzesień 2025 - REKOMENDOWANY)",
                "recommended": True,
                "description": "Najnowszy model - najlepsza równowaga inteligencji, szybkości i ceny"
            },
            {
                "id": "claude-haiku-4-5-20251001",
                "name": "Claude Haiku 4.5 (październik 2025)",
                "recommended": False,
                "description": "Najszybszy model z wysoką inteligencją"
            },
            {
                "id": "claude-opus-4-5-20251101",
                "name": "Claude Opus 4.5 (listopad 2025)",
                "recommended": False,
                "description": "Premium - maksymalna inteligencja"
            },
            # Legacy models - still available
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku (październik 2024 - Legacy)",
                "recommended": False,
                "description": "Starszy szybki model"
            },
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4 (maj 2025 - Legacy)",
                "recommended": False,
                "description": "Poprzednia wersja Sonnet"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku (marzec 2024 - Legacy)",
                "recommended": False,
                "description": "Stary tani model"
            }
        ]

        return {
            "success": True,
            "models": models
        }


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
            model=model_settings.get("model", "claude-sonnet-4-5-20250929"),
            temperature=model_settings.get("temperature", 0.3),
            max_tokens=model_settings.get("max_tokens", 2000)
        )
    else:
        raise ValueError(f"Nieznany provider: {provider_name}")
