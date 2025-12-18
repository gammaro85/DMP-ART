# utils/ai_module.py
"""
AI Review Assistant for DMP-ART
Main module orchestrating AI-powered DMP review functionality
"""

import json
import os
from typing import Optional, Dict, List, Any
from .ai_providers import get_provider, AIProvider
from .knowledge_manager import KnowledgeManager


class AIReviewAssistant:
    """Main AI assistant module for DMP review"""

    def __init__(self, config_path: str = "config/ai/ai_config.json"):
        """
        Initialize the AI Review Assistant

        Args:
            config_path: Path to AI configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.knowledge_manager = KnowledgeManager(
            self.config.get("knowledge_base_path", "config/ai/knowledge_base.json")
        )
        self.provider: Optional[AIProvider] = None

        if self.is_enabled():
            self._init_provider()

    def _load_config(self) -> dict:
        """Load AI configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading AI config: {e}")
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "enabled": False,
            "provider": "openai",
            "api_keys": {
                "openai": "",
                "anthropic": ""
            },
            "model_settings": {
                "openai": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                "anthropic": {
                    "model": "claude-sonnet-4-5-20250929",
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            },
            "review_settings": {
                "ready_comments_ratio": 0.75,
                "ai_suggestions_ratio": 0.25,
                "auto_learn_enabled": True,
                "min_confidence_threshold": 0.7
            },
            "knowledge_base_path": "config/ai/knowledge_base.json"
        }

    def _save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _init_provider(self):
        """Initialize the AI provider"""
        try:
            self.provider = get_provider(self.config)
        except Exception as e:
            print(f"Error initializing AI provider: {e}")
            self.provider = None

    def is_enabled(self) -> bool:
        """Check if AI module is enabled"""
        return self.config.get("enabled", False)

    def enable(self):
        """Enable the AI module"""
        self.config["enabled"] = True
        self._save_config()
        self._init_provider()

    def disable(self):
        """Disable the AI module"""
        self.config["enabled"] = False
        self._save_config()
        self.provider = None

    def update_settings(self, settings: dict):
        """
        Update AI settings

        Args:
            settings: Dictionary of settings to update
        """
        # Deep merge settings
        for key, value in settings.items():
            if isinstance(value, dict) and key in self.config:
                self.config[key].update(value)
            else:
                self.config[key] = value

        self._save_config()

        if self.is_enabled():
            self._init_provider()

    def get_config(self, hide_keys: bool = True) -> dict:
        """
        Get current configuration

        Args:
            hide_keys: If True, mask API keys

        Returns:
            Configuration dictionary
        """
        config_copy = self.config.copy()
        if hide_keys and "api_keys" in config_copy:
            config_copy["api_keys"] = {
                k: "***" if v else ""
                for k, v in config_copy["api_keys"].items()
            }
        return config_copy

    def test_connection(self) -> tuple:
        """
        Test connection to AI API

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.provider:
            return False, "AI provider nie jest zainicjalizowany. Sprawdź klucz API."
        return self.provider.test_connection()

    def list_available_models(self) -> dict:
        """
        Get list of available models from current AI provider

        Returns:
            Dictionary with success status and list of models
        """
        if not self.provider:
            # Initialize provider if not already done
            self._init_provider()

        if not self.provider:
            return {
                "success": False,
                "models": [],
                "error": "AI provider nie jest zainicjalizowany. Sprawdź klucz API."
            }

        return self.provider.list_models()

    def generate_review_suggestions(self, dmp_content: Dict[str, Any],
                                   available_comments: Dict[str, Any]) -> dict:
        """
        Generate review suggestions for entire DMP

        Args:
            dmp_content: Dictionary with DMP content {section_id: content}
            available_comments: Dictionary with available comments by category

        Returns:
            Dictionary with suggestions for each section
        """
        if not self.is_enabled():
            return {"error": "Moduł AI jest wyłączony"}

        if not self.provider:
            return {"error": "AI provider nie jest zainicjalizowany. Sprawdź konfigurację."}

        suggestions = {}
        ready_ratio = self.config.get("review_settings", {}).get("ready_comments_ratio", 0.75)

        for section_id, content in dmp_content.items():
            # Skip metadata keys
            if section_id.startswith("_"):
                continue

            # Get content text
            if isinstance(content, dict):
                paragraphs = content.get("paragraphs", [])
                if isinstance(paragraphs, list):
                    content_text = "\n".join(str(p) for p in paragraphs)
                else:
                    content_text = str(paragraphs)
            else:
                content_text = str(content)

            # Get knowledge base context
            knowledge_context = self.knowledge_manager.get_context_for_section(section_id)

            # Get available comments for this section
            section_comments = self._get_comments_for_section(section_id, available_comments)

            # Combine context
            full_context = f"{knowledge_context}\n\nDOSTĘPNE KOMENTARZE:\n{section_comments}"

            try:
                # Generate AI suggestions
                ai_result = self.provider.generate_feedback(
                    dmp_content=content_text,
                    section_id=section_id,
                    knowledge_context=full_context
                )

                # Apply 75/25 ratio
                suggestions[section_id] = self._apply_ratio(ai_result, ready_ratio)

            except Exception as e:
                suggestions[section_id] = {
                    "error": str(e),
                    "selected_comments": [],
                    "ai_suggestions": [],
                    "quality_score": 0,
                    "issues": [f"Błąd generowania sugestii: {str(e)}"]
                }

        return suggestions

    def generate_section_suggestion(self, section_id: str, content: str,
                                   available_comments: List[dict]) -> dict:
        """
        Generate suggestion for a single section

        Args:
            section_id: Section identifier
            content: Section content text
            available_comments: List of available comments for this section

        Returns:
            Dictionary with suggestions
        """
        if not self.is_enabled():
            return {"error": "Moduł AI jest wyłączony"}

        if not self.provider:
            return {"error": "AI provider nie jest zainicjalizowany"}

        # Get knowledge context
        knowledge_context = self.knowledge_manager.get_context_for_section(section_id)

        # Format available comments
        comments_context = "\n".join([
            f"- [{c.get('id', 'unknown')}] {c.get('text', '')}"
            for c in available_comments
        ])

        full_context = f"{knowledge_context}\n\nDOSTĘPNE KOMENTARZE:\n{comments_context}"

        try:
            result = self.provider.generate_feedback(
                dmp_content=content,
                section_id=section_id,
                knowledge_context=full_context
            )

            ready_ratio = self.config.get("review_settings", {}).get("ready_comments_ratio", 0.75)
            return self._apply_ratio(result, ready_ratio)

        except Exception as e:
            return {
                "error": str(e),
                "selected_comments": [],
                "ai_suggestions": [],
                "quality_score": 0,
                "issues": [f"Błąd: {str(e)}"]
            }

    def _get_comments_for_section(self, section_id: str, available_comments: dict) -> str:
        """
        Format available comments for a section

        Args:
            section_id: Section identifier
            available_comments: All available comments by category

        Returns:
            Formatted string of comments
        """
        comments_list = []

        for category, sections in available_comments.items():
            if isinstance(sections, dict) and section_id in sections:
                section_comments = sections[section_id]
                if isinstance(section_comments, list):
                    for i, comment in enumerate(section_comments):
                        comment_id = f"{category}_{section_id}_{i:03d}"
                        comment_text = comment if isinstance(comment, str) else str(comment)
                        comments_list.append(f"- [{comment_id}] {comment_text}")

        return "\n".join(comments_list) if comments_list else "Brak gotowych komentarzy dla tej sekcji."

    def _apply_ratio(self, ai_result: dict, ready_ratio: float) -> dict:
        """
        Apply the 75/25 ratio to suggestions

        Args:
            ai_result: Raw AI result
            ready_ratio: Ratio for ready comments (e.g., 0.75)

        Returns:
            Adjusted result dictionary
        """
        selected = ai_result.get("selected_comments", [])
        suggestions = ai_result.get("ai_suggestions", [])

        total_items = len(selected) + len(suggestions)
        if total_items == 0:
            return ai_result

        # Calculate limits
        max_ready = max(1, int(total_items * ready_ratio))
        max_ai = max(1, total_items - max_ready)

        return {
            "selected_comments": selected[:max_ready],
            "ai_suggestions": suggestions[:max_ai],
            "quality_score": ai_result.get("quality_score", 50),
            "issues": ai_result.get("issues", [])
        }

    def learn_from_saved_feedback(self, section_id: str, dmp_content: str,
                                  feedback_text: str, used_comments: List[str]):
        """
        Learn from user's saved feedback

        Args:
            section_id: Section that was reviewed
            dmp_content: Original DMP content
            feedback_text: User's feedback text
            used_comments: List of comment IDs used
            
        Returns:
            None
        """
        if not self.config.get("review_settings", {}).get("auto_learn_enabled", True):
            return

        self.knowledge_manager.learn_from_feedback(
            section_id=section_id,
            dmp_content=dmp_content,
            feedback_text=feedback_text,
            selected_comments=used_comments
        )

    def get_knowledge_base(self) -> dict:
        """
        Get the knowledge base for UI display

        Returns:
            Complete knowledge base dictionary
        """
        return self.knowledge_manager.get_all_entries()

    def update_knowledge_entry(self, section_id: str, issue_id: str, updates: dict) -> bool:
        """
        Update a knowledge base entry

        Args:
            section_id: Section identifier
            issue_id: Issue ID to update
            updates: Dictionary of fields to update

        Returns:
            Success status
        """
        return self.knowledge_manager.update_entry(section_id, issue_id, updates)

    def delete_knowledge_entry(self, section_id: str, issue_id: str) -> bool:
        """
        Delete a knowledge base entry

        Args:
            section_id: Section identifier
            issue_id: Issue ID to delete

        Returns:
            Success status
        """
        return self.knowledge_manager.delete_entry(section_id, issue_id)

    def add_knowledge_entry(self, section_id: str, pattern: str,
                           keywords: List[str], suggested_comments: List[str],
                           ai_template: str = "") -> str:
        """
        Add a new knowledge base entry

        Args:
            section_id: Section identifier
            pattern: Issue pattern description
            keywords: Keywords to detect the pattern
            suggested_comments: Suggested comment IDs
            ai_template: AI suggestion template

        Returns:
            ID of the created entry
        """
        return self.knowledge_manager.add_issue_pattern(
            section_id=section_id,
            pattern=pattern,
            keywords=keywords,
            suggested_comments=suggested_comments,
            ai_suggestion_template=ai_template
        )

    def get_statistics(self) -> dict:
        """
        Get usage statistics

        Returns:
            Statistics dictionary
        """
        knowledge = self.knowledge_manager.get_all_entries()
        most_used = self.knowledge_manager.get_most_used_patterns(10)

        total_issues = 0
        total_practices = 0
        for section_data in knowledge.get("sections", {}).values():
            total_issues += len(section_data.get("common_issues", []))
            total_practices += len(section_data.get("good_practices", []))

        return {
            "enabled": self.is_enabled(),
            "provider": self.config.get("provider", "unknown"),
            "total_issues": total_issues,
            "total_practices": total_practices,
            "most_used_patterns": most_used,
            "last_updated": knowledge.get("_metadata", {}).get("last_updated", "unknown")
        }
