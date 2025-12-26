import asyncio
from typing import Dict, Any
from groq import Groq
from config import Config
import logging

logger = logging.getLogger(__name__)

class MedicalAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.temperature = Config.GROQ_TEMPERATURE

    async def analyze_patient_request(self, patient_text: str) -> Dict[str, Any]:
        try:
            system_prompt = """Ты - опытный врач общей практики. Твоя задача:
            1. Анализировать обращения пациентов
            2. Выявлять симптомы и проблемы со здоровьем
            3. Структурировать медицинскую информацию
            4. Предлагать пути решения

            Формат ответа:
            📋 ТИП ОБРАЩЕНИЯ: [Симптомы/Диагностика/Лечение/Профилактика/Другое]

            🎯 ОСНОВНАЯ ПРОБЛЕМА:
            - Краткое описание ключевой проблемы со здоровьем

            🩺 МЕДИЦИНСКИЕ ДЕТАЛИ (если указаны):
            - Симптомы
            - Длительность
            - Локализация боли

            🔍 ДОПОЛНИТЕЛЬНЫЕ ВОПРОСЫ:
            1. ...
            2. ...
            3. ...

            💡 РЕКОМЕНДАЦИИ ВРАЧУ:
            - Какие обследования назначить
            - Какие препараты рекомендовать
            - Что уточнить у пациента

            📞 ДАЛЬНЕЙШИЕ ШАГИ:
            - Конкретные действия для постановки диагноза

            Будь профессиональным, точным и полезным."""

            user_prompt = f"""Пациент обратился с жалобой/вопросом:

            "{patient_text}"

            Проанализируй это обращение по указанной структуре."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=800
            )

            analysis = response.choices[0].message.content.strip()
            request_type = self._detect_request_type(patient_text)
            keywords = self._extract_keywords(patient_text)

            return {
                "analysis": analysis,
                "request_type": request_type,
                "keywords": keywords,
                "original_text": patient_text[:500] + "..." if len(patient_text) > 500 else patient_text
            }

        except Exception as e:
            logger.error(f"Error in medical analysis: {e}")
            return {
                "analysis": "Не удалось проанализировать обращение.",
                "request_type": "Не определен",
                "keywords": [],
                "original_text": patient_text[:200] if patient_text else ""
            }

    def _detect_request_type(self, text: str) -> str:
        text_lower = text.lower()

        request_types = {
            "Симптомы": ["бол", "боль", "температур", "тошнит", "кашель", "насморк"],
            "Диагностика": ["обследован", "анализ", "рентген", "узи", "диагноз"],
            "Лечение": ["леч", "таблетк", "укол", "мазь", "препарат"],
            "Профилактика": ["профилактик", "прививк", "здоровь", "предупред"],
            "Жалоба": ["жалоб", "проблем", "недовол", "плох", "ужасн"]
        }

        for req_type, keywords in request_types.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return req_type

        return "Консультация"

    def _extract_keywords(self, text: str) -> list:
        text_lower = text.lower()
        keywords = []

        medical_terms = [
            "боль", "температур", "давлен", "сердц", "голова", "живот",
            "кашель", "насморк", "тошнот", "рвот", "аллерги", "инфекц",
            "препарат", "таблетк", "укол", "мазь", "анализ", "обследован"
        ]

        for term in medical_terms:
            if term in text_lower:
                keywords.append(term)

        return list(set(keywords))[:5]

medical_analyzer = MedicalAnalyzer()
