import json
import os
from datetime import datetime
from pathlib import Path

class FeedbackManager:
    def __init__(self, feedback_dir: str = "logs/feedback"):
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback.json"
        self._init_feedback_file()
    
    def _init_feedback_file(self):
        """Инициализация файла обратной связи."""
        if not self.feedback_file.exists():
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump({"bug_reports": [], "suggestions": []}, f, ensure_ascii=False, indent=2)
    
    async def add_feedback(self, user_id: int, feedback_type: str, message: str):
        """Добавление нового отзыва."""
        feedback = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if feedback_type == "bug":
                data["bug_reports"].append(feedback)
            else:
                data["suggestions"].append(feedback)
            
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении обратной связи: {e}")
            return False
    
    async def get_feedback_stats(self):
        """Получение статистики обратной связи."""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "total_bug_reports": len(data["bug_reports"]),
                "total_suggestions": len(data["suggestions"]),
                "last_bug_report": data["bug_reports"][-1] if data["bug_reports"] else None,
                "last_suggestion": data["suggestions"][-1] if data["suggestions"] else None
            }
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return None 