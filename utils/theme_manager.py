from typing import Dict

class ThemeManager:
    """Менеджер тем для бота."""
    
    LIGHT_THEME = {
        'main_emoji': '🌞',
        'secondary_emoji': '✨',
        'accent_emoji': '☀️',
        'divider': '└',
        'card_emoji': '🎴',
        'message_emoji': '📜',
        'settings_emoji': '⚙️',
    }
    
    DARK_THEME = {
        'main_emoji': '🌙',
        'secondary_emoji': '🌠',
        'accent_emoji': '✨',
        'divider': '└',
        'card_emoji': '🎴',
        'message_emoji': '📜',
        'settings_emoji': '⚙️',
    }
    
    @classmethod
    def get_theme(cls, theme_name: str) -> Dict[str, str]:
        """Получает настройки темы по имени."""
        return cls.DARK_THEME if theme_name == "dark" else cls.LIGHT_THEME
    
    @classmethod
    def apply_theme(cls, message: str, theme_name: str) -> str:
        """Применяет тему к сообщению."""
        theme = cls.get_theme(theme_name)
        return message.format(**theme) 