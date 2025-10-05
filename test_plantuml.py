#!/usr/bin/env python3
"""
Тестовый скрипт для проверки PlantUML диаграмм
"""

import streamlit as st
import json
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plantuml_generator import generateBPMNDiagram, generateUseCaseDiagram, render_plantuml
from plantuml_renderer import check_requirements, download_plantuml_jar

# Настройка страницы
st.set_page_config(page_title="Test PlantUML", layout="wide")

st.title("Test PlantUML Diagrams")

# Тестовые данные для BPMN диаграммы
test_bpmn_data = {
    "bpmn_plantuml": """@startuml
!theme plain
title BPMN Process Diagram

start
:Пользователь заходит на сайт;
if (Авторизован?) then (Нет)
  :Показать форму входа;
  :Ввести логин/пароль;
  if (Данные верны?) then (Да)
    :Показать меню;
  else (Нет)
    :Показать ошибку;
    repeat
      :Ввести логин/пароль;
      if (Данные верны?) then (Да)
        :Показать меню;
        break;
      else (Нет)
        :Показать ошибку;
      endif
    repeat while (Данные неверны) is (Нет) not (Да)
  endif
else (Да)
  :Показать меню;
endif
:Выбрать блюда;
:Добавить в корзину;
if (Хочет оформить заказ?) then (Да)
  :Перейти к оформлению;
  :Ввести данные доставки;
  :Выбрать способ оплаты;
  :Подтвердить заказ;
  :Заказ отправлен;
  stop;
else (Нет)
  :Выбрать блюда;
endif
@enduml"""
}

# Тестовые данные для Use-Case диаграммы
test_usecase_data = {
    "usecase_plantuml": """@startuml
!theme plain
title Use Case Diagram
left to right direction

actor "Пользователь" as user
actor "Система" as system

usecase "Просмотреть меню" as uc1
usecase "Добавить в корзину" as uc2
usecase "Оформить заказ" as uc3
usecase "Оплатить заказ" as uc4

user --> uc1
user --> uc2
user --> uc3
user --> uc4

uc1 --> system
uc2 --> system
uc3 --> system
uc4 --> system
@enduml"""
}

def test_plantuml_diagrams():
    st.header("Тестирование PlantUML диаграмм")
    
    # Тест BPMN диаграммы
    st.subheader("BPMN Диаграмма процесса заказа еды")
    
    with st.expander("🔍 Исходные данные PlantUML"):
        st.code(test_bpmn_data["bpmn_plantuml"], language="text")
    
    # Рендерим диаграмму
    render_plantuml(test_bpmn_data["bpmn_plantuml"], 600)
    
    st.markdown("---")
    
    # Тест Use-Case диаграммы
    st.subheader("Use-Case Диаграмма")
    
    with st.expander("🔍 Исходные данные PlantUML"):
        st.code(test_usecase_data["usecase_plantuml"], language="text")
    
    # Рендерим диаграмму
    render_plantuml(test_usecase_data["usecase_plantuml"], 400)

def test_custom_input():
    st.header("Тест с пользовательскими данными")
    
    # Ввод BPMN кода
    st.subheader("BPMN диаграмма")
    custom_bpmn = st.text_area(
        "Введите BPMN код в формате PlantUML:",
        value="@startuml\n!theme plain\ntitle BPMN Process Diagram\n\nstart\n:Действие 1;\nif (Условие?) then (Да)\n  :Действие 2;\nelse (Нет)\n  :Действие 3;\nendif\nstop\n@enduml",
        height=150
    )
    
    if st.button("Сгенерировать BPMN PlantUML"):
        if custom_bpmn.strip():
            with st.expander("🔍 Введенный код PlantUML"):
                st.code(custom_bpmn, language="text")
            
            render_plantuml(custom_bpmn, 400)
        else:
            st.warning("Пожалуйста, введите BPMN код")
    
    st.markdown("---")
    
    # Ввод Use-Case кода
    st.subheader("Use-Case диаграмма")
    custom_usecase = st.text_area(
        "Введите Use-Case код в формате PlantUML:",
        value="@startuml\nactor \"Пользователь\" as user\nusecase \"Действие\" as uc1\nuser --> uc1\n@enduml",
        height=150
    )
    
    if st.button("Сгенерировать Use-Case PlantUML"):
        if custom_usecase.strip():
            with st.expander("🔍 Введенный код PlantUML"):
                st.code(custom_usecase, language="text")
            
            render_plantuml(custom_usecase, 400)
        else:
            st.warning("Пожалуйста, введите Use-Case код")

def test_local_rendering():
    st.header("Локальный рендеринг PlantUML")
    
    # Проверка требований
    st.subheader("Проверка требований")
    requirements = check_requirements()
    
    if requirements["can_render_locally"]:
        st.success("✅ Все требования для локального рендеринга выполнены!")
        st.write(f"**Java найдена:** {requirements['java_path']}")
        st.write(f"**PlantUML JAR найден:** {requirements['plantuml_path']}")
    else:
        st.error("❌ Требования для локального рендеринга не выполнены:")
        st.write(f"**Ошибка:** {requirements['error']}")
        
        if not requirements["java_available"]:
            st.warning("Установите Java Runtime Environment (JRE)")
        if not requirements["plantuml_available"]:
            st.info("Скачайте plantuml.jar:")
            if st.button("Скачать plantuml.jar"):
                download_plantuml_jar()
    
    st.markdown("---")
    
    # Тест локального рендеринга
    st.subheader("Тест локального рендеринга")
    
    test_code = """@startuml
!theme plain
title Test BPMN Diagram

start
:Test action;
if (Test condition?) then (Yes)
  :Action 1;
else (No)
  :Action 2;
endif
stop
@enduml"""
    
    with st.expander("🔍 Тестовый код PlantUML"):
        st.code(test_code, language="text")
    
    if st.button("🔄 Проверить локальный рендеринг"):
        render_plantuml(test_code, 400)

# Основной интерфейс
tab1, tab2, tab3 = st.tabs(["📊 Тестовые диаграммы", "✏️ Пользовательский ввод", "🔧 Локальный рендеринг"])

with tab1:
    test_plantuml_diagrams()

with tab2:
    test_custom_input()

with tab3:
    test_local_rendering()

st.markdown("---")
st.markdown("*Тестирование PlantUML генератора*")
