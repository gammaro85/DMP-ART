# utils/knowledge_manager.py
"""
Knowledge Base Manager for DMP-ART AI Module
Handles storage, retrieval, and auto-learning of feedback patterns
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, List, Tuple


class KnowledgeManager:
    """Manages the AI knowledge base for DMP review patterns"""

    def __init__(self, knowledge_path: str = "config/ai/knowledge_base.json"):
        self.knowledge_path = knowledge_path
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> dict:
        """Load knowledge base from JSON file"""
        if os.path.exists(self.knowledge_path):
            try:
                with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading knowledge base: {e}")
                return self._create_default_knowledge()
        return self._create_default_knowledge()

    def _create_default_knowledge(self) -> dict:
        """Create default knowledge base structure"""
        default = {
            "_metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_entries": 0
            },
            "sections": {},
            "global_patterns": {
                "empty_section": {
                    "pattern": "sekcja pusta lub zbyt krótka",
                    "min_chars_threshold": 50,
                    "suggested_comment": "Ta sekcja wymaga uzupełnienia."
                },
                "copy_paste_detected": {
                    "pattern": "skopiowany tekst z szablonu",
                    "indicators": ["[wpisz tutaj]", "[uzupełnij]", "Lorem ipsum"],
                    "suggested_comment": "Wykryto tekst szablonowy."
                }
            },
            "custom_rules": []
        }
        self._save_knowledge(default)
        return default

    def _save_knowledge(self, data: Optional[dict] = None):
        """Save knowledge base to file"""
        if data is None:
            data = self.knowledge

        # Update metadata
        data["_metadata"]["last_updated"] = datetime.now().isoformat()
        data["_metadata"]["total_entries"] = self._count_entries(data)

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.knowledge_path), exist_ok=True)

            with open(self.knowledge_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"Error saving knowledge base: {e}")
            raise

    def _count_entries(self, data: dict) -> int:
        """Count total entries in knowledge base"""
        count = 0
        for section_data in data.get("sections", {}).values():
            count += len(section_data.get("common_issues", []))
            count += len(section_data.get("good_practices", []))
        return count

    def get_context_for_section(self, section_id: str) -> str:
        """
        Get knowledge base context for a specific section

        Args:
            section_id: Section identifier (e.g., "1.1", "2.1")

        Returns:
            Formatted context string for AI prompt
        """
        section_data = self.knowledge.get("sections", {}).get(section_id, {})
        context_parts = []

        # Add section name if available
        section_name = section_data.get("section_name", f"Sekcja {section_id}")
        context_parts.append(f"=== {section_name} ===\n")

        # Add common issues
        issues = section_data.get("common_issues", [])
        if issues:
            context_parts.append("TYPOWE PROBLEMY:")
            for issue in issues:
                context_parts.append(f"  - [{issue['id']}] Wzorzec: {issue['pattern']}")
                if issue.get("keywords"):
                    context_parts.append(f"    Słowa kluczowe: {', '.join(issue['keywords'])}")
                if issue.get("suggested_comment_ids"):
                    context_parts.append(f"    Sugerowane komentarze: {', '.join(issue['suggested_comment_ids'])}")
                if issue.get("ai_suggestion_template"):
                    context_parts.append(f"    Szablon AI: {issue['ai_suggestion_template']}")

        # Add good practices
        practices = section_data.get("good_practices", [])
        if practices:
            context_parts.append("\nDOBRE PRAKTYKI:")
            for practice in practices:
                context_parts.append(f"  + {practice['pattern']}")
                if practice.get("feedback"):
                    context_parts.append(f"    Feedback: {practice['feedback']}")

        # Add global patterns
        global_patterns = self.knowledge.get("global_patterns", {})
        if global_patterns:
            context_parts.append("\nWZORCE GLOBALNE:")
            for pattern_name, pattern_data in global_patterns.items():
                context_parts.append(f"  * {pattern_name}: {pattern_data.get('pattern', '')}")

        return "\n".join(context_parts) if context_parts else "Brak kontekstu dla tej sekcji."

    def add_issue_pattern(self, section_id: str, pattern: str,
                         keywords: List[str], suggested_comments: List[str],
                         ai_suggestion_template: str = "") -> str:
        """
        Add a new issue pattern to the knowledge base

        Args:
            section_id: Section identifier
            pattern: Description of the issue pattern
            keywords: List of keywords to detect this pattern
            suggested_comments: List of suggested comment IDs
            ai_suggestion_template: Template for AI-generated suggestion

        Returns:
            ID of the created issue
        """
        if section_id not in self.knowledge["sections"]:
            self.knowledge["sections"][section_id] = {
                "section_name": f"Section {section_id}",
                "common_issues": [],
                "good_practices": []
            }

        # Generate unique ID
        existing_issues = self.knowledge["sections"][section_id]["common_issues"]
        issue_num = len(existing_issues) + 1
        issue_id = f"{section_id}_issue_{issue_num:03d}"

        # Create new issue entry
        new_issue = {
            "id": issue_id,
            "pattern": pattern,
            "keywords": keywords,
            "suggested_comment_ids": suggested_comments,
            "ai_suggestion_template": ai_suggestion_template,
            "usage_count": 0,
            "last_used": None,
            "source": "user_feedback",
            "created_at": datetime.now().isoformat()
        }

        self.knowledge["sections"][section_id]["common_issues"].append(new_issue)
        self._save_knowledge()

        return issue_id

    def add_good_practice(self, section_id: str, pattern: str,
                         keywords: List[str], feedback: str) -> bool:
        """
        Add a new good practice pattern

        Args:
            section_id: Section identifier
            pattern: Description of the good practice
            keywords: List of keywords to detect this pattern
            feedback: Positive feedback to give

        Returns:
            Success status
        """
        if section_id not in self.knowledge["sections"]:
            self.knowledge["sections"][section_id] = {
                "section_name": f"Section {section_id}",
                "common_issues": [],
                "good_practices": []
            }

        new_practice = {
            "pattern": pattern,
            "keywords": keywords,
            "feedback": feedback,
            "created_at": datetime.now().isoformat()
        }

        self.knowledge["sections"][section_id]["good_practices"].append(new_practice)
        self._save_knowledge()

        return True

    def increment_usage(self, issue_id: str) -> bool:
        """
        Increment usage counter for an issue pattern

        Args:
            issue_id: ID of the issue to increment

        Returns:
            Success status
        """
        for section_id, section_data in self.knowledge["sections"].items():
            for issue in section_data.get("common_issues", []):
                if issue["id"] == issue_id:
                    issue["usage_count"] = issue.get("usage_count", 0) + 1
                    issue["last_used"] = datetime.now().isoformat()
                    self._save_knowledge()
                    return True
        return False

    def learn_from_feedback(self, section_id: str, dmp_content: str,
                           feedback_text: str, selected_comments: List[str]):
        """
        Learn patterns from user feedback
        
        Args:
            section_id: Section that was reviewed
            dmp_content: Original DMP content
            feedback_text: User's feedback text
            selected_comments: List of comment IDs used
        """
        # Extract patterns from the feedback
        patterns = self._extract_patterns(dmp_content, feedback_text)

        patterns_added = 0
        for pattern, keywords in patterns:
            # Check if pattern already exists
            if not self._pattern_exists(section_id, pattern):
                self.add_issue_pattern(
                    section_id=section_id,
                    pattern=pattern,
                    keywords=keywords,
                    suggested_comments=selected_comments
                )
                patterns_added += 1
        
        # Perform periodic cleanup after adding patterns
        if patterns_added > 0:
            # Check if cleanup is needed based on section size
            size_info = self.get_knowledge_base_size()
            section_size = size_info["section_sizes"].get(section_id, 0)
            
            # If section has too many entries, enforce limits
            if section_size > 100:
                self.enforce_max_entries_per_section(max_entries=100)
            
            # Cleanup old unused patterns periodically
            if size_info["total_entries"] > 500:
                self.cleanup_low_usage_patterns(min_usage_threshold=0, max_age_days=90)

    def _extract_patterns(self, dmp_content: str, feedback_text: str) -> List[Tuple[str, List[str]]]:
        """
        Extract issue patterns from feedback (simplified heuristics)

        Args:
            dmp_content: Original DMP content
            feedback_text: User's feedback text

        Returns:
            List of (pattern_description, keywords) tuples
        """
        patterns = []
        feedback_lower = feedback_text.lower()
        content_lower = dmp_content.lower() if dmp_content else ""

        # Pattern 1: Empty or too short section
        if len(dmp_content.strip()) < 50:
            patterns.append(("sekcja zbyt krótka lub pusta", ["krótki", "brak", "uzupełnić", "puste"]))

        # Pattern 2: Missing information
        missing_indicators = ["brak", "nie podano", "nie wskazano", "nie określono", "uzupełnić"]
        if any(ind in feedback_lower for ind in missing_indicators):
            # Try to extract what is missing
            for indicator in missing_indicators:
                if indicator in feedback_lower:
                    patterns.append(("brakujące informacje", missing_indicators))
                    break

        # Pattern 3: Too generic description
        generic_indicators = ["niespecyficzne", "ogólnikowe", "zbyt ogólne", "konkretne", "szczegóły"]
        if any(ind in feedback_lower for ind in generic_indicators):
            patterns.append(("zbyt ogólnikowy opis", generic_indicators))

        # Pattern 4: Template text detected
        template_indicators = ["szablon", "template", "[wpisz", "[uzupełnij"]
        if any(ind in content_lower for ind in template_indicators):
            patterns.append(("tekst szablonowy", template_indicators))

        # Pattern 5: Format issues
        format_indicators = ["format", "plik", "csv", "json", "xml"]
        if any(ind in feedback_lower for ind in format_indicators):
            patterns.append(("problemy z formatem danych", format_indicators))

        # Pattern 6: Repository issues
        repo_indicators = ["repozytorium", "zenodo", "most wiedzy", "archiwum"]
        if any(ind in feedback_lower for ind in repo_indicators):
            patterns.append(("kwestie repozytorium", repo_indicators))

        return patterns

    def _pattern_exists(self, section_id: str, pattern: str) -> bool:
        """
        Check if a pattern already exists in the knowledge base

        Args:
            section_id: Section to check
            pattern: Pattern description

        Returns:
            True if pattern exists
        """
        section_data = self.knowledge.get("sections", {}).get(section_id, {})
        for issue in section_data.get("common_issues", []):
            # Simple similarity check - could be improved with fuzzy matching
            if self._similar_patterns(issue["pattern"], pattern):
                return True
        return False

    def _similar_patterns(self, pattern1: str, pattern2: str, threshold: float = 0.6) -> bool:
        """
        Check if two patterns are similar using Jaccard similarity

        Args:
            pattern1: First pattern
            pattern2: Second pattern
            threshold: Similarity threshold (0-1)

        Returns:
            True if patterns are similar
        """
        words1 = set(re.findall(r'\w+', pattern1.lower()))
        words2 = set(re.findall(r'\w+', pattern2.lower()))

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return (intersection / union) >= threshold if union > 0 else False

    def get_all_entries(self) -> dict:
        """
        Get all knowledge base entries for UI display

        Returns:
            Complete knowledge base dictionary
        """
        return self.knowledge

    def update_entry(self, section_id: str, issue_id: str, updates: dict) -> bool:
        """
        Update an existing knowledge base entry

        Args:
            section_id: Section identifier
            issue_id: Issue ID to update
            updates: Dictionary of fields to update

        Returns:
            Success status
        """
        section_data = self.knowledge.get("sections", {}).get(section_id, {})
        for issue in section_data.get("common_issues", []):
            if issue["id"] == issue_id:
                # Update allowed fields
                allowed_fields = ["pattern", "keywords", "suggested_comment_ids",
                                "ai_suggestion_template"]
                for field in allowed_fields:
                    if field in updates:
                        issue[field] = updates[field]
                issue["updated_at"] = datetime.now().isoformat()
                self._save_knowledge()
                return True
        return False

    def delete_entry(self, section_id: str, issue_id: str) -> bool:
        """
        Delete an entry from the knowledge base

        Args:
            section_id: Section identifier
            issue_id: Issue ID to delete

        Returns:
            Success status
        """
        section_data = self.knowledge.get("sections", {}).get(section_id, {})
        issues = section_data.get("common_issues", [])
        for i, issue in enumerate(issues):
            if issue["id"] == issue_id:
                del issues[i]
                self._save_knowledge()
                return True
        return False

    def get_most_used_patterns(self, limit: int = 10) -> List[dict]:
        """
        Get the most frequently used patterns

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of pattern dictionaries sorted by usage count
        """
        all_issues = []
        for section_id, section_data in self.knowledge.get("sections", {}).items():
            for issue in section_data.get("common_issues", []):
                issue_copy = issue.copy()
                issue_copy["section_id"] = section_id
                all_issues.append(issue_copy)

        # Sort by usage count descending
        all_issues.sort(key=lambda x: x.get("usage_count", 0), reverse=True)

        return all_issues[:limit]

    def export_knowledge(self, filepath: str) -> bool:
        """
        Export knowledge base to a file

        Args:
            filepath: Path to export file

        Returns:
            Success status
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False

    def import_knowledge(self, filepath: str, merge: bool = True) -> bool:
        """
        Import knowledge base from a file

        Args:
            filepath: Path to import file
            merge: If True, merge with existing; if False, replace

        Returns:
            Success status
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)

            if merge:
                # Merge sections
                for section_id, section_data in imported.get("sections", {}).items():
                    if section_id not in self.knowledge["sections"]:
                        self.knowledge["sections"][section_id] = section_data
                    else:
                        # Merge issues
                        existing_ids = {i["id"] for i in self.knowledge["sections"][section_id].get("common_issues", [])}
                        for issue in section_data.get("common_issues", []):
                            if issue["id"] not in existing_ids:
                                self.knowledge["sections"][section_id]["common_issues"].append(issue)
            else:
                self.knowledge = imported

            self._save_knowledge()
            return True

        except (IOError, json.JSONDecodeError):
            return False

    def get_knowledge_base_size(self) -> dict:
        """
        Get knowledge base size statistics
        
        Returns:
            Dictionary with size metrics
        """
        total_entries = 0
        total_sections = len(self.knowledge.get("sections", {}))
        section_sizes = {}
        
        for section_id, section_data in self.knowledge.get("sections", {}).items():
            section_entries = len(section_data.get("common_issues", []))
            total_entries += section_entries
            section_sizes[section_id] = section_entries
            
        try:
            file_size = os.path.getsize(self.knowledge_path)
        except OSError:
            file_size = 0
            
        return {
            "total_entries": total_entries,
            "total_sections": total_sections,
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2),
            "section_sizes": section_sizes
        }

    def cleanup_low_usage_patterns(self, min_usage_threshold: int = 0, 
                                   max_age_days: int = 90) -> int:
        """
        Remove low-usage patterns to prevent unbounded growth
        
        Args:
            min_usage_threshold: Minimum usage count to keep (default 0, keeps all)
            max_age_days: Remove unused patterns older than this (default 90 days)
            
        Returns:
            Number of patterns removed
        """
        from datetime import datetime, timedelta
        
        removed_count = 0
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for section_id, section_data in self.knowledge.get("sections", {}).items():
            issues = section_data.get("common_issues", [])
            initial_count = len(issues)
            
            # Filter out low-usage old patterns
            filtered_issues = []
            for issue in issues:
                usage_count = issue.get("usage_count", 0)
                created_at = issue.get("created_at", "")
                
                # Keep if used above threshold OR recently created
                try:
                    created_date = datetime.fromisoformat(created_at)
                    is_recent = created_date > cutoff_date
                except (ValueError, TypeError):
                    is_recent = True  # Keep if date parsing fails
                    
                if usage_count > min_usage_threshold or is_recent:
                    filtered_issues.append(issue)
                else:
                    removed_count += 1
                    
            section_data["common_issues"] = filtered_issues
            
        if removed_count > 0:
            self._save_knowledge()
            
        return removed_count

    def enforce_max_entries_per_section(self, max_entries: int = 100) -> int:
        """
        Enforce maximum entries per section, keeping most-used patterns
        
        Args:
            max_entries: Maximum entries per section (default 100)
            
        Returns:
            Number of patterns removed
        """
        removed_count = 0
        
        for section_id, section_data in self.knowledge.get("sections", {}).items():
            issues = section_data.get("common_issues", [])
            
            if len(issues) > max_entries:
                # Sort by usage count (descending) and recency
                issues.sort(key=lambda x: (
                    x.get("usage_count", 0),
                    x.get("last_used") or x.get("created_at", "")
                ), reverse=True)
                
                # Keep only top max_entries
                removed = len(issues) - max_entries
                section_data["common_issues"] = issues[:max_entries]
                removed_count += removed
                
        if removed_count > 0:
            self._save_knowledge()
            
        return removed_count
