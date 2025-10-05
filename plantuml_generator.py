#!/usr/bin/env python3
"""
Модуль для генерации PlantUML диаграмм из Mermaid-подобных структур данных
"""

import re
from typing import Dict, Any, List


def generateBPMNDiagram(processData: Dict[str, Any]) -> str:
    """
    Генерирует BPMN диаграмму в формате PlantUML из данных процесса
    
    Args:
        processData: Словарь с данными BPMN диаграммы (ожидает поле 'bpmn_mermaid')
        
    Returns:
        Строка с PlantUML кодом для BPMN диаграммы
    """
    if not processData or 'bpmn_mermaid' not in processData:
        return "@startuml\ntitle BPMN Diagram\n@enduml"
    
    mermaid_code = processData['bpmn_mermaid']
    
    # Парсим Mermaid код и конвертируем в PlantUML BPMN
    plantuml_lines = ["@startuml", "!theme plain", "title BPMN Process Diagram"]
    
    # Добавляем стили для BPMN элементов
    plantuml_lines.extend([
        "skinparam participant {",
        "  BackgroundColor LightGreen",
        "  BorderColor DarkGreen",
        "}",
        "skinparam activity {",
        "  BackgroundColor LightBlue",
        "  BorderColor DarkBlue",
        "}",
        "skinparam decision {",
        "  BackgroundColor LightYellow",
        "  BorderColor Orange",
        "}"
    ])
    
    lines = mermaid_code.strip().split('\n')
    
    # Пропускаем первую строку с типом диаграммы Mermaid
    if lines and lines[0].strip().startswith('flowchart'):
        lines = lines[1:]
    
    # Словарь для хранения узлов и их типов
    nodes = {}
    connections = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        
        # Парсим узлы и соединения
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) >= 2:
                # Извлекаем исходный узел
                source_part = parts[0].strip()
                source_match = re.match(r'^(\w+)', source_part)
                if source_match:
                    source_id = source_match.group(1)
                    
                    # Извлекаем текст узла
                    source_text_match = re.search(r'\[([^\]]+)\]', source_part)
                    if source_text_match:
                        nodes[source_id] = source_text_match.group(1)
                    else:
                        # Проверяем на условие
                        condition_match = re.search(r'\{([^\}]+)\}', source_part)
                        if condition_match:
                            nodes[source_id] = condition_match.group(1)
                
                # Извлекаем целевой узел
                target_part = parts[1].strip()
                
                # Извлекаем метку соединения
                label = ""
                label_match = re.search(r'\|([^|]+)\|', target_part)
                if label_match:
                    label = label_match.group(1)
                    target_part = re.sub(r'\|[^|]+\|', '', target_part).strip()
                
                target_match = re.match(r'^(\w+)', target_part)
                if target_match:
                    target_id = target_match.group(1)
                    
                    # Извлекаем текст целевого узла
                    target_text_match = re.search(r'\[([^\]]+)\]', target_part)
                    if target_text_match:
                        nodes[target_id] = target_text_match.group(1)
                    else:
                        condition_match = re.search(r'\{([^\}]+)\}', target_part)
                        if condition_match:
                            nodes[target_id] = condition_match.group(1)
                    
                    connections.append((source_id, target_id, label))
    
    # Генерируем PlantUML активити диаграмму
    plantuml_lines.append("|")
    
    # Определяем стартовый узел
    if nodes:
        start_node = list(nodes.keys())[0]
        plantuml_lines.append(f"(*) --> \"{nodes[start_node]}\"")
        
        # Генерируем соединения
        for source, target, label in connections:
            if source in nodes and target in nodes:
                # Определяем тип узла
                source_text = nodes[source]
                target_text = nodes[target]
                
                # Проверяем, является ли узел условием
                if '?' in source_text or 'как' in source_text.lower() or 'ли' in source_text.lower():
                    # Условный узел
                    if label:
                        plantuml_lines.append(f"if \"{source_text}\" then")
                        plantuml_lines.append(f"  -->[\"{label}\"] \"{target_text}\"")
                    else:
                        plantuml_lines.append(f"if \"{source_text}\" then")
                        plantuml_lines.append(f"  --> \"{target_text}\"")
                else:
                    # Обычное действие
                    if label:
                        plantuml_lines.append(f"-->[\"{label}\"] \"{target_text}\"")
                    else:
                        plantuml_lines.append(f"--> \"{target_text}\"")
    
    # Добавляем конечную точку
    plantuml_lines.append("--> (*)")
    
    plantuml_lines.append("@enduml")
    
    return '\n'.join(plantuml_lines)


def generateUseCaseDiagram(actorData: Dict[str, Any]) -> str:
    """
    Генерирует Use-Case диаграмму в формате PlantUML из данных акторов
    
    Args:
        actorData: Словарь с данными Use-Case диаграммы (ожидает поле 'usecase_mermaid')
        
    Returns:
        Строка с PlantUML кодом для Use-Case диаграммы
    """
    if not actorData or 'usecase_mermaid' not in actorData:
        return "@startuml\ntitle Use Case Diagram\n@enduml"
    
    mermaid_code = actorData['usecase_mermaid']
    
    # Парсим Mermaid код и конвертируем в PlantUML Use Case
    plantuml_lines = ["@startuml", "!theme plain", "title Use Case Diagram", "left to right direction"]
    
    # Добавляем стили
    plantuml_lines.extend([
        "skinparam actor {",
        "  BackgroundColor LightGreen",
        "  BorderColor DarkGreen",
        "}",
        "skinparam usecase {",
        "  BackgroundColor LightBlue",
        "  BorderColor DarkBlue",
        "}"
    ])
    
    lines = mermaid_code.strip().split('\n')
    
    # Пропускаем первую строку с типом диаграммы Mermaid
    if lines and lines[0].strip().startswith('flowchart'):
        lines = lines[1:]
    
    # Словарь для хранения акторов и use-case
    actors = {}
    usecases = {}
    connections = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        
        # Парсим связи между акторами и use-case
        if '-->' in line or '-.->' in line:
            # Определяем тип соединения
            if '-->' in line:
                parts = line.split('-->')
                connection_type = "-->"
            else:
                parts = line.split('-.->')
                connection_type = ".->"
            
            if len(parts) >= 2:
                # Извлекаем исходный элемент
                source_part = parts[0].strip()
                
                # Проверяем на актора (прямоугольник)
                if '[' in source_part and not '(' in source_part:
                    source_match = re.match(r'^(\w+)\[([^\]]+)\]', source_part)
                    if source_match:
                        source_id = source_match.group(1)
                        source_text = source_match.group(2)
                        actors[source_id] = source_text
                
                # Проверяем на use-case (овал)
                elif '((' in source_part:
                    source_match = re.match(r'^(\w+)\(\(([^)]+)\)\)', source_part)
                    if source_match:
                        source_id = source_match.group(1)
                        source_text = source_match.group(2)
                        usecases[source_id] = source_text
                
                # Извлекаем целевой элемент
                target_part = parts[1].strip()
                
                # Извлекаем метку соединения
                label = ""
                label_match = re.search(r'\|([^|]+)\|', target_part)
                if label_match:
                    label = label_match.group(1)
                    target_part = re.sub(r'\|[^|]+\|', '', target_part).strip()
                
                # Проверяем на актора
                if '[' in target_part and not '(' in target_part:
                    target_match = re.match(r'^(\w+)\[([^\]]+)\]', target_part)
                    if target_match:
                        target_id = target_match.group(1)
                        target_text = target_match.group(2)
                        actors[target_id] = target_text
                        connections.append((source_id, target_id, connection_type, label))
                
                # Проверяем на use-case
                elif '((' in target_part:
                    target_match = re.match(r'^(\w+)\(\(([^)]+)\)\)', target_part)
                    if target_match:
                        target_id = target_match.group(1)
                        target_text = target_match.group(2)
                        usecases[target_id] = target_text
                        connections.append((source_id, target_id, connection_type, label))
    
    # Генерируем акторов
    for actor_id, actor_text in actors.items():
        plantuml_lines.append(f'actor "{actor_text}" as {actor_id}')
    
    plantuml_lines.append("")
    
    # Генерируем use-case
    for uc_id, uc_text in usecases.items():
        plantuml_lines.append(f'usecase "{uc_text}" as {uc_id}')
    
    plantuml_lines.append("")
    
    # Генерируем связи
    for source, target, conn_type, label in connections:
        if label:
            if conn_type == ".->":
                plantuml_lines.append(f'{source} .{conn_type[1:]} "{label}" {target}')
            else:
                plantuml_lines.append(f'{source} {conn_type} "{label}" {target}')
        else:
            plantuml_lines.append(f'{source} {conn_type} {target}')
    
    plantuml_lines.append("@enduml")
    
    return '\n'.join(plantuml_lines)


# Импортируем новый рендерер и фиксатор синтаксиса
try:
    from plantuml_renderer import render_plantuml as render_plantuml_local
except ImportError:
    render_plantuml_local = None

try:
    from plantuml_syntax_fixer import auto_fix_plantuml
except ImportError:
    auto_fix_plantuml = None

def render_plantuml(plantuml_code: str, height: int = 500):
    """
    Рендерит PlantUML диаграмму с использованием локального или онлайн рендеринга
    Автоматически исправляет синтаксические ошибки перед рендерингом
    
    Args:
        plantuml_code: PlantUML код для рендеринга
        height: Высота контейнера для диаграммы
    """
    import streamlit as st
    
    if not plantuml_code:
        return
    
    # Автоматически исправляем синтаксис, если доступен фиксатор
    if auto_fix_plantuml is not None:
        try:
            fixed_code, fixes_applied = auto_fix_plantuml(plantuml_code)
            if fixes_applied:
                st.info(f"🔧 Применены автоматические исправления синтаксиса PlantUML:")
                for fix in fixes_applied:
                    st.text(f"  • {fix}")
                plantuml_code = fixed_code
        except Exception as e:
            st.warning(f"⚠️ Ошибка при автоматическом исправлении синтаксиса: {e}")
            st.info("Будет использован исходный код")
    
    # Пробуем локальный рендерер, если доступен
    if render_plantuml_local is not None:
        try:
            render_plantuml_local(plantuml_code, height)
            return
        except Exception as e:
            st.warning(f"⚠️ Локальный рендерер не сработал: {e}")
            st.info("Будет использован онлайн-рендерер как запасной вариант")
    
    # Запасной вариант: используем старый онлайн рендеринг
    import streamlit.components.v1 as components
    import urllib.parse
    import base64
    import hashlib
    
    # Кодируем PlantUML код для URL
    encoded_code = urllib.parse.quote(plantuml_code)
    
    # Используем несколько альтернативных серверов PlantUML
    servers = [
        f"https://www.plantuml.com/plantuml/png/{encoded_code}",
        f"https://plantuml-server.kkeisuke.com/plantuml/png/{encoded_code}",
        f"https://plantuml.aoaostudio.com/png/{encoded_code}"
    ]
    
    # Генерируем уникальный ID для диаграммы
    diagram_id = hashlib.md5(plantuml_code.encode()).hexdigest()[:8]
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                min-height: 100vh;
                background-color: #ffffff;
            }}
            .plantuml-container {{
                width: 100%;
                max-width: 100%;
                text-align: center;
            }}
            .plantuml-container img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            .error-message {{
                color: #d32f2f;
                background-color: #ffebee;
                padding: 16px;
                border-radius: 4px;
                border-left: 4px solid #d32f2f;
                font-family: monospace;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .code-display {{
                background-color: #f5f5f5;
                padding: 16px;
                border-radius: 4px;
                font-family: monospace;
                white-space: pre-wrap;
                text-align: left;
                margin: 10px 0;
            }}
            .loading {{
                color: #666;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="plantuml-container">
            <div class="code-display">
                <strong>PlantUML Code:</strong><br>
                {plantuml_code.replace('<', '<').replace('>', '>')}
            </div>
            <div id="loading-{diagram_id}" class="loading">
                Загрузка диаграммы...
            </div>
            <img id="diagram-{diagram_id}" style="display:none;" alt="PlantUML Diagram" onerror="this.style.display='none'; document.getElementById('error-{diagram_id}').style.display='block'; document.getElementById('loading-{diagram_id}').style.display='none';">
            <div id="error-{diagram_id}" class="error-message" style="display:none;">
                <strong>Ошибка загрузки диаграммы PlantUML</strong><br><br>
                Возможные причины:<br>
                • Проблемы с подключением к серверу PlantUML<br>
                • Некорректный синтаксис PlantUML кода<br>
                • Слишком большая диаграмма для онлайн-рендеринга<br><br>
                <strong>PlantUML код:</strong><br>
                {plantuml_code.replace('<', '<').replace('>', '>')}
            </div>
        </div>
        <script>
            // Пробуем разные серверы
            const servers = {servers};
            const diagramId = '{diagram_id}';
            let currentServer = 0;
            
            function loadDiagram() {{
                if (currentServer >= servers.length) {{
                    document.getElementById('loading-' + diagramId).style.display = 'none';
                    document.getElementById('error-' + diagramId).style.display = 'block';
                    return;
                }}
                
                const img = document.getElementById('diagram-' + diagramId);
                const loading = document.getElementById('loading-' + diagramId);
                
                img.onload = function() {{
                    loading.style.display = 'none';
                    img.style.display = 'block';
                }};
                
                img.onerror = function() {{
                    currentServer++;
                    loadDiagram();
                }};
                
                img.src = servers[currentServer];
            }}
            
            // Начинаем загрузку
            loadDiagram();
        </script>
    </body>
    </html>
    """
    
    try:
        components.html(html_code, height=height, scrolling=True)
    except Exception as e:
        st.error(f"❌ Ошибка отображения PlantUML диаграммы: {e}")
        st.code(plantuml_code, language="text")
