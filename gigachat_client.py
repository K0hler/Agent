import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from gigachat import GigaChat

# Загружаем переменные окружения из .env файла
load_dotenv()

class GigaChatClient:
    def __init__(self):
        # Получаем credentials из переменных окружения
        self.credentials = os.getenv("GIGACHAT_AUTH_KEY") or self._get_credentials_from_env()
        if not self.credentials:
            raise ValueError("GIGACHAT_AUTH_KEY или GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET должны быть установлены в .env файле")

        # Создаем экземпляр официального клиента GigaChat
        self.client = GigaChat(
            credentials=self.credentials,
            scope="GIGACHAT_API_PERS",
            model="GigaChat-Pro",
            verify_ssl_certs=False  # Отключаем верификацию SSL для работы с корпоративными сертификатами
        )

    def _get_credentials_from_env(self) -> str:
        """Генерирует credentials из client_id и client_secret"""
        import base64
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

        if not client_id or not client_secret:
            return None

        credentials = f"{client_id}:{client_secret}"
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    def chat_completion(self, messages: List[Dict[str, str]], model: str = "GigaChat-Pro", temperature: float = 0.0) -> Dict[str, Any]:
        """Отправляет запрос на генерацию ответа модели"""
        try:
            # Создаем payload для запроса
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            # Используем официальный клиент
            response = self.client.chat(payload)
            # Преобразуем ответ в формат, совместимый с предыдущей реализацией
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content if hasattr(response, 'choices') and response.choices else response.content
                    }
                }],
                "usage": {
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0
                }
            }
        except Exception as e:
            raise ValueError(f"Ошибка при запросе к GigaChat API: {str(e)}")

    def get_models(self) -> Dict[str, Any]:
        """Получает список доступных моделей"""
        try:
            models = self.client.get_models()
            return {
                "data": [{"id": model.id_} for model in models.data] if hasattr(models, 'data') else []
            }
        except Exception as e:
            raise ValueError(f"Ошибка при получении списка моделей: {str(e)}")

    def tokens_count(self, input_text: List[str], model: str = "GigaChat-Pro") -> Dict[str, Any]:
        """Подсчитывает количество токенов в тексте"""
        try:
            tokens = self.client.tokens_count(input_text, model=model)
            # Возвращаем общее количество токенов
            total_tokens = sum(tc.tokens for tc in tokens) if tokens else 0
            return {
                "tokens": total_tokens
            }
        except Exception as e:
            raise ValueError(f"Ошибка при подсчете токенов: {str(e)}")

    def test_connection(self) -> bool:
        """Тестирует подключение к API"""
        try:
            print("🔧 Тестирую подключение к GigaChat API...")
            print(f"🔑 Credentials: {'✅ Установлены' if self.credentials else '❌ Не установлены'}")

            # Пробуем получить список моделей
            models = self.get_models()
            print(f"✅ Список моделей получен: {len(models.get('data', []))} моделей")

            # Пробуем сделать тестовый запрос
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.chat_completion(test_messages)
            print(f"✅ Тестовый запрос выполнен успешно")

            return True

        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")
            return False

# Глобальный экземпляр клиента
gigachat_client = GigaChatClient()
