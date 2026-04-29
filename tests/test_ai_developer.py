"""
Unit tests for the SDLC Multi-Agent Backend Builder
"""

import pytest
from ai_developer import (
    analyze_requirement,
    to_snake_case,
    pluralize_word,
    extract_requested_capabilities,
)


class TestRequirementAnalysis:
    """Test requirement analysis and classification"""

    def test_analyze_requirement_todo(self):
        """Test todo app requirement detection"""
        result = analyze_requirement("Build a todo list application")
        assert result == "todo_app"

    def test_analyze_requirement_weather(self):
        """Test weather API requirement detection"""
        result = analyze_requirement("Create a weather forecast API")
        assert result == "weather_api"

    def test_analyze_requirement_user_management(self):
        """Test user management requirement detection"""
        result = analyze_requirement("Build a login and authentication system")
        assert result == "user_management"

    def test_analyze_requirement_blog(self):
        """Test blog API requirement detection"""
        result = analyze_requirement("Create a blog platform with posts and comments")
        assert result == "blog_api"

    def test_analyze_requirement_custom(self):
        """Test custom API fallback for unknown requirement"""
        result = analyze_requirement("Build a custom inventory tracking system")
        assert result == "custom_api"


class TestUtilityFunctions:
    """Test utility functions"""

    def test_to_snake_case_simple(self):
        """Test snake_case conversion for simple names"""
        assert to_snake_case("StudentRecord") == "student_record"
        assert to_snake_case("Student") == "student"

    def test_to_snake_case_with_hyphens(self):
        """Test snake_case conversion with hyphens"""
        assert to_snake_case("inventory-item") == "inventory_item"

    def test_pluralize_word_simple(self):
        """Test simple pluralization"""
        assert pluralize_word("book") == "books"
        assert pluralize_word("student") == "students"

    def test_pluralize_word_ending_in_y(self):
        """Test pluralization for words ending in y"""
        assert pluralize_word("city") == "cities"
        assert pluralize_word("category") == "categories"

    def test_pluralize_word_special_cases(self):
        """Test pluralization for special cases"""
        assert pluralize_word("box") == "boxes"
        assert pluralize_word("bus") == "buses"


class TestCapabilityExtraction:
    """Test capability extraction from requirements"""

    def test_extract_authentication_capability(self):
        """Test authentication capability detection"""
        caps = extract_requested_capabilities("Build a system with JWT authentication and login")
        assert caps["authentication"] is True

    def test_extract_crud_capability(self):
        """Test CRUD capability detection"""
        caps = extract_requested_capabilities("Create CRUD operations for user management")
        assert caps["crud"] is True

    def test_extract_validation_capability(self):
        """Test validation capability detection"""
        caps = extract_requested_capabilities("Build with input validation and schema checks")
        assert caps["validation"] is True

    def test_extract_external_api_capability(self):
        """Test external API capability detection"""
        caps = extract_requested_capabilities("Integrate with third-party weather forecasting service")
        assert caps["external_api"] is True

    def test_extract_production_capability(self):
        """Test production readiness capability detection"""
        caps = extract_requested_capabilities("Build a production-ready, scalable API")
        assert caps["production"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
