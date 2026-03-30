class AIService:
    """
    AI Service (Rule-Based v1)

    Responsible for:
    - analyzing task text
    - generating structured task
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

    def analyze_task(self, text: str) -> dict:
        """
        Main AI entrypoint
        """

        priority = self.suggest_priority(text)

        return {
            "title": text[:50],
            "description": text,
            "priority": priority,
        }

    def suggest_priority(self, title: str) -> str:
        """
        Predict priority from title.
        """

        text = title.lower()

        for word in self.HIGH_KEYWORDS:
            if word in text:
                return "high"

        for word in self.MEDIUM_KEYWORDS:
            if word in text:
                return "medium"

        return "low"


    @staticmethod
    def classify_task(title: str) -> str:
        text = title.lower()

        # 🔥 1. testing له أعلى أولوية
        if "test" in text or "testing" in text:
            return "testing"

        # 🔥 2. auth
        if (
            "auth" in text
            or "login" in text
            or "register" in text
            or "jwt" in text
            or "token" in text
            or "password" in text
        ):
            return "auth"

        # 🔥 3. frontend
        if (
            "frontend" in text
            or "ui" in text
            or "dashboard" in text
            or "react" in text
            or "page" in text
        ):
            return "frontend"

        # 🔥 4. api
        if (
            "api" in text
            or "endpoint" in text
            or "route" in text
            or "backend" in text
        ):
            return "api"

        # 🔥 5. default
        return "general" 

    @staticmethod
    def get_template(task_type: str) -> list[str]:

        # 🔥 auth tasks
        if task_type == "auth":
            return [
                "Design user model",
                "Implement register",
                "Implement login",
                "Add JWT authentication",
                "Add password hashing",
            ]

        # 🔥 frontend tasks
        if task_type == "frontend":
            return [
                "Design UI/UX",
                "Create components",
                "Setup routing",
                "Connect API",
                "Handle state",
                "Test UI",
            ]

        # 🔥 api tasks
        if task_type == "api":
            return [
                "Design endpoints",
                "Implement routes",
                "Add validation",
                "Handle errors",
                "Test endpoints",
            ]

        # 🔥 testing tasks
        if task_type == "testing":
            return [
                "Write unit tests",
                "Test edge cases",
                "Test error handling",
                "Run test suite",
            ]

        # 🔥 default
        return [
            "Break down task",
            "Implement solution",
            "Test functionality",
        ] 
    
    @staticmethod
    def enhance_steps(title: str, steps: list[str]) -> list[str]:
        text = title.lower()

        enhanced = steps.copy()  # علشان منغيرش الأصل

        # 🔥 security enhancement
        if "secure" in text or "security" in text:
            enhanced.append("Add security checks")
            enhanced.append("Protect against common attacks")

        # 🔥 api enhancement
        if "api" in text:
            enhanced.append("Add input validation")
            enhanced.append("Handle API errors properly")

        # 🔥 performance enhancement
        if "performance" in text or "optimize" in text:
            enhanced.append("Optimize performance")
            enhanced.append("Reduce response time")

        return enhanced
    
    @staticmethod
    def generate_subtasks(title: str) -> list[str]:
        
        # 1️⃣ تحديد النوع
        task_type = AIService.classify_task(title)

        # 2️⃣ جلب template
        steps = AIService.get_template(task_type)

        # 3️⃣ تحسين الخطوات
        enhanced_steps = AIService.enhance_steps(title, steps)

        return enhanced_steps