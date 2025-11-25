#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики подключения к GigaChat API
"""

import os
import sys
from dotenv import load_dotenv
from gigachat_client import GigaChatClient

# Загружаем переменные окружения
load_dotenv()

def main():
    print("🔧 Диагностика подключения к GigaChat API")
    print("=" * 50)

    # Проверяем переменные окружения
    print("📋 Проверка переменных окружения:")
    api_url = os.getenv("GIGACHAT_API_URL")
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    auth_key = os.getenv("GIGACHAT_AUTH_KEY")

    print(f"   GIGACHAT_API_URL: {api_url}")
    print(f"   GIGACHAT_CLIENT_ID: {'✅ Установлен' if client_id else '❌ Не установлен'}")
    print(f"   GIGACHAT_CLIENT_SECRET: {'✅ Установлен' if client_secret else '❌ Не установлен'}")
    print(f"   GIGACHAT_AUTH_KEY: {'✅ Установлен' if auth_key else '❌ Не установлен'}")

    if not (client_id and client_secret) and not auth_key:
        print("\n❌ Ошибка: Не установлены API ключи!")
        print("📖 Инструкция:")
        print("1. Зарегистрируйтесь в https://developers.sber.ru/")
        print("2. Создайте проект в разделе GigaChat API")
        print("3. Получите Client ID и Client Secret")
        print("4. Вставьте их в файл .env")
        return

    # Создаем клиент и тестируем подключение
    print("\n🔌 Тестирование подключения...")
    client = GigaChatClient()

    try:
        success = client.test_connection()
        if success:
            print("\n🎉 Подключение успешно! API ключи работают правильно.")
        else:
            print("\n❌ Подключение не удалось.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        print("\n🔍 Возможные причины:")
        print("1. Неверные API ключи")
        print("2. Ключи деактивированы в личном кабинете")
        print("3. Превышен лимит запросов")
        print("4. Аккаунт не активирован для использования API")
        print("\n💡 Рекомендации:")
        print("1. Проверьте правильность ключей в личном кабинете Sber AI")
        print("2. Убедитесь, что проект активен")
        print("3. Проверьте баланс токенов")
        print("4. Свяжитесь с поддержкой Sber AI")

if __name__ == "__main__":
    main()
