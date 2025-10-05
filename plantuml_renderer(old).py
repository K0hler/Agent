#!/usr/bin/env python3
"""
Локальный рендерер PlantUML диаграмм с использованием plantuml.jar
Требует наличия Java Runtime Environment (JRE)
"""

import os
import subprocess
import tempfile
import base64
import hashlib
from typing import Optional
import streamlit as st


class PlantUMLRenderer:
    """Класс для локального рендеринга PlantUML диаграмм"""
    
    def __init__(self, jar_path: Optional[str] = None):
        """
        Инициализация рендерера
        
        Args:
            jar_path: Путь к файлу plantuml.jar. Если None, ищется в стандартных местах
        """
        self.jar_path = jar_path or self._find_plantuml_jar()
        self.java_path = self._find_java()
        
        if not self.jar_path:
            raise RuntimeError("PlantUML JAR файл не найден. Укажите путь к plantuml.jar или поместите его в одну из стандартных директорий")
        
        if not self.java_path:
            raise RuntimeError("Java Runtime Environment (JRE) не найден. Пожалуйста, установите Java.")
    
    def _find_java(self) -> Optional[str]:
        """Поиск Java в системе"""
        possible_paths = [
            "java",
            "java.exe",
            os.path.join(os.environ.get("JAVA_HOME", ""), "bin", "java.exe"),
            os.path.join(os.environ.get("JAVA_HOME", ""), "bin", "java")
        ]
        
        for path in possible_paths:
            try:
                if subprocess.run([path, "-version"], capture_output=True, timeout=5).returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return None
    
    def _find_plantuml_jar(self) -> Optional[str]:
        """Поиск plantuml.jar в системе"""
        possible_locations = [
            "plantuml.jar",
            os.path.join("lib", "plantuml.jar"),
            os.path.join("deps", "plantuml.jar"),
            os.path.join(os.path.dirname(__file__), "plantuml.jar"),
            os.path.join(os.path.dirname(__file__), "lib", "plantuml.jar"),
            os.path.join(os.path.dirname(__file__), "deps", "plantuml.jar")
        ]
        
        for location in possible_locations:
            if os.path.exists(location):
                return os.path.abspath(location)
        
        return None
    
    def render_to_image(self, plantuml_code: str, output_format: str = "png") -> bytes:
        """
        Рендерит PlantUML код в изображение
        
        Args:
            plantuml_code: Код PlantUML для рендеринга
            output_format: Формат вывода (png, svg, etc.)
            
        Returns:
            Байты изображения
        """
        if not plantuml_code.strip():
            raise ValueError("PlantUML код не может быть пустым")
        
        # Создаем временный файл для PlantUML кода
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as temp_input:
            temp_input.write(plantuml_code)
            temp_input_path = temp_input.name
        
        # Создаем временный файл для вывода
        with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Формируем команду для запуска PlantUML
            cmd = [
                self.java_path,
                "-Djava.awt.headless=true",
                "-jar", self.jar_path,
                "-charset", "UTF-8",
                "-t" + output_format,
                temp_input_path,
                "-o", os.path.dirname(temp_output_path)
            ]
            
            # Запускаем процесс
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                error_msg = f"PlantUML rendering failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                raise RuntimeError(error_msg)
            
            # Читаем результат
            output_file = temp_output_path.replace(f'.{output_format}', f'.{output_format}')
            if not os.path.exists(output_file):
                raise RuntimeError("Output file was not created")
            
            with open(output_file, 'rb') as f:
                return f.read()
                
        finally:
            # Удаляем временные файлы
            try:
                os.unlink(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
                output_file = temp_output_path.replace(f'.{output_format}', f'.{output_format}')
                if os.path.exists(output_file):
                    os.unlink(output_file)
            except OSError:
                pass


# Глобальный экземпляр рендерера
_renderer = None


def get_renderer() -> PlantUMLRenderer:
    """Получение глобального экземпляра рендерера"""
    global _renderer
    if _renderer is None:
        try:
            _renderer = PlantUMLRenderer()
        except RuntimeError as e:
            st.warning(f"⚠️ {str(e)}")
            st.info("Будет использован онлайн-рендерер как запасной вариант")
            return None
    return _renderer


def render_plantuml(plantuml_code: str, height: int = 500, use_local: bool = True):
    """
    Рендерит PlantUML диаграмму с использованием локального или онлайн рендеринга
    
    Args:
        plantuml_code: PlantUML код для рендеринга
        height: Высота контейнера для диаграммы
        use_local: Использовать локальный рендерер, если доступен
    """
    import streamlit.components.v1 as components
    import urllib.parse
    
    if not plantuml_code:
        return
    
    # Генерируем уникальный ID для диаграммы
    diagram_id = hashlib.md5(plantuml_code.encode()).hexdigest()[:8]
    
    # Пробуем локальный рендерер
    if use_local:
        renderer = get_renderer()
        if renderer is not None:
            try:
                # Рендерим в PNG
                image_data = renderer.render_to_image(plantuml_code, "png")
                
                # Кодируем в base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Создаем HTML с локально сгенерированным изображением
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
                        .code-display {{
                            background-color: #f5f5f5;
                            padding: 16px;
                            border-radius: 4px;
                            font-family: monospace;
                            white-space: pre-wrap;
                            text-align: left;
                            margin: 10px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="plantuml-container">
                        <div class="code-display">
                            <strong>PlantUML Code:</strong><br>
                            {plantuml_code.replace('<', '<').replace('>', '>')}
                        </div>
                        <img src="data:image/png;base64,{base64_image}" alt="PlantUML Diagram">
                    </div>
                </body>
                </html>
                """
                
                components.html(html_code, height=height, scrolling=True)
                return
                
            except Exception as e:
                st.warning(f"⚠️ Локальный рендерер не сработал: {e}")
                st.info("Будет использован онлайн-рендерер как запасной вариант")
    
    # Запасной вариант: онлайн рендеринг
    encoded_code = urllib.parse.quote(plantuml_code)
    
    # Используем несколько альтернативных серверов PlantUML
    servers = [
        f"https://www.plantuml.com/plantuml/png/{encoded_code}",
        f"https://plantuml-server.kkeisuke.com/plantuml/png/{encoded_code}",
        f"https://plantuml.aoaostudio.com/png/{encoded_code}"
    ]
    
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


def check_requirements() -> dict:
    """
    Проверяет требования для локального рендеринга
    
    Returns:
        Словарь с информацией о требованиях
    """
    try:
        renderer = PlantUMLRenderer()
        return {
            "java_available": True,
            "java_path": renderer.java_path,
            "plantuml_available": True,
            "plantuml_path": renderer.jar_path,
            "can_render_locally": True
        }
    except RuntimeError as e:
        return {
            "java_available": False,
            "java_path": None,
            "plantuml_available": False,
            "plantuml_path": None,
            "can_render_locally": False,
            "error": str(e)
        }


def download_plantuml_jar(url: str = "https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml.jar") -> bool:
    """
    Скачивает plantuml.jar из указанного URL
    
    Args:
        url: URL для скачивания plantuml.jar
        
    Returns:
        True если скачивание успешно, иначе False
    """
    try:
        import requests
        
        # Получаем имя файла из URL
        filename = os.path.basename(url)
        
        # Скачиваем файл
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Сохраняем файл
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        st.success(f"✅ Файл {filename} успешно скачан")
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка скачивания plantuml.jar: {e}")
        return False
