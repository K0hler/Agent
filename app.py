import streamlit as st
import json
from dotenv import load_dotenv
from gigachat_client import gigachat_client
from plantuml_generator import render_plantuml

load_dotenv()

st.set_page_config(
    page_title="Агент-помощник системного аналитика",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Агент-помощник системного аналитика")
st.markdown("---")

with st.sidebar:
    st.header("ℹ️ Информация")
    st.markdown("""
    **Агент-помощник системного аналитика** помогает создавать:
    - 📋 Название проекта
    - 🔄 BPMN диаграммы процессов
    - 🎯 Use-Case диаграммы
    - 📋 Функциональные и нефункциональные требования

    **Как использовать:**
    1. Введите описание системы в текстовое поле
    2. Нажмите "Сгенерировать анализ"
    3. Просмотрите результаты во вкладках
    """)
    st.markdown("---")
    st.markdown("### Настройки модели")
    model_name = st.selectbox("Выберите модель GigaChat", ["GigaChat", "GigaChat-Pro", "GigaChat-2-Max"], index=0)
    temperature = st.slider("Температура", 0.0, 1.0, 0.0, 0.1)

st.header("📝 Описание системы")
user_input = st.text_area(
    "Опишите систему, которую нужно проанализировать:",
    height=150,
    placeholder="Пример: Система для онлайн-заказа еды в ресторане. Пользователь может просматривать меню, добавлять блюда в корзину, оформлять заказ и оплачивать онлайн..."
)

if st.button("🚀 Сгенерировать анализ", type="primary", use_container_width=True):
    if not user_input.strip():
        st.error("❌ Пожалуйста, введите описание системы")
    else:
        with st.spinner("🔄 Генерирую анализ..."):
            try:
                with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]

                response = gigachat_client.chat_completion(
                    messages=messages,
                    model=model_name,
                    temperature=temperature
                )

                assistant_content = response["choices"][0]["message"]["content"]

                try:
                    analysis_result = json.loads(assistant_content)
                    st.session_state.analysis_result = analysis_result
                    st.session_state.raw_response = assistant_content
                    st.success("✅ Анализ успешно сгенерирован!")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Ошибка парсинга JSON ответа модели: {e}")
                    st.info("📄 Сырой ответ модели:")
                    st.code(assistant_content, language="json")
                    st.session_state.raw_response = assistant_content

            except Exception as e:
                st.error(f"❌ Ошибка при обращении к API: {str(e)}")
                if "GIGACHAT_CLIENT_ID" in str(e) or "GIGACHAT_CLIENT_SECRET" in str(e):
                    st.warning("⚠️ Проверьте настройки API в файле .env")

if hasattr(st.session_state, 'analysis_result'):
    st.markdown("---")
    st.header("📊 Результаты анализа")

    tab1, tab2, tab3, tab4 = st.tabs(["🏷️ Название", "🔄 BPMN", "🎯 Use-Case", "📋 Требования"])

    with tab1:
        st.subheader("Название проекта")
        st.info(st.session_state.analysis_result.get("title", "Не указано"))

    with tab2:
        st.subheader("BPMN диаграмма процесса")
        bpmn_code = st.session_state.analysis_result.get("bpmn_plantuml", "")
        if bpmn_code:
            with st.expander("🔍 Код PlantUML"):
                st.code(bpmn_code, language="text")
            
            st.caption("Тип диаграммы: PlantUML BPMN")
            
            # Рендерим PlantUML диаграмму
            render_plantuml(bpmn_code, 600)
        else:
            st.warning("⚠️ BPMN диаграмма не найдена в ответе модели")

    with tab3:
        st.subheader("Use-Case диаграмма")
        usecase_code = st.session_state.analysis_result.get("usecase_plantuml", "")
        if usecase_code:
            with st.expander("🔍 Код PlantUML"):
                st.code(usecase_code, language="text")
            
            st.caption("Тип диаграммы: PlantUML Use-Case")
            
            # Рендерим PlantUML диаграмму
            render_plantuml(usecase_code, 600)
        else:
            st.warning("⚠️ Use-Case диаграмма не найдена в ответе модели")

    with tab4:
        st.subheader("Функциональные и нефункциональные требования")
        requirements_md = st.session_state.analysis_result.get("requirements_md", "")
        if requirements_md:
            st.markdown(requirements_md)
        else:
            st.warning("⚠️ Требования не найдены в ответе модели")

    with st.expander("🔍 Сырой JSON ответ"):
        st.json(st.session_state.analysis_result)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Скачать Markdown отчет"):
            # Используем PlantUML код напрямую
            bpmn_code = st.session_state.analysis_result.get("bpmn_plantuml", "")
            usecase_code = st.session_state.analysis_result.get("usecase_plantuml", "")
            
            report = f"""# Анализ системы: {st.session_state.analysis_result.get('title', 'Неизвестно')}

## BPMN диаграмма процесса
```plantuml
{bpmn_code}
```

## Use-Case диаграмма
```plantuml
{usecase_code}
```

## Требования
{st.session_state.analysis_result.get('requirements_md', '')}
"""
            st.download_button(
                label="💾 Скачать файл",
                data=report,
                file_name=f"analysis_{st.session_state.analysis_result.get('title', 'report').replace(' ', '_')}.md",
                mime="text/markdown"
            )

    with col2:
        if st.button("🔄 Сгенерировать новый анализ"):
            if hasattr(st.session_state, 'analysis_result'):
                del st.session_state.analysis_result
            if hasattr(st.session_state, 'raw_response'):
                del st.session_state.raw_response
            st.rerun()

st.markdown("---")
st.markdown("*Создано с помощью GigaChat API и Streamlit*")
