# ===============================
# AIService (Rule-Based v1)
# ===============================

class AIService:
    """
    AI Service (Version 1 - Rule Based)

    الهدف:
    - اقتراح priority بناءً على title
    """

    HIGH_KEYWORDS = [
        "urgent",
        "asap",
        "immediately",
        "now",
        "fix",
        "bug",
        "error",
        "production",
    ]

    MEDIUM_KEYWORDS = [
        "today",
        "soon",
        "important",
        "review",
        "prepare",
    ]

    @staticmethod
    def suggest_priority(title: str) -> str:
        """
        Predict priority from title.

        Returns:
        - "high"
        - "medium"
        - "low"
        """

        text = title.lower()

        # HIGH
        for word in AIService.HIGH_KEYWORDS:
            if word in text:
                return "high"

        # MEDIUM
        for word in AIService.MEDIUM_KEYWORDS:
            if word in text:
                return "medium"

        # DEFAULT
        return "low"