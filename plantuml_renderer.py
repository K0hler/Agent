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
import zlib
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
        ]
        
        # Добавляем пути из JAVA_HOME если установлено
        if "JAVA_HOME" in os.environ:
            java_home = os.environ["JAVA_HOME"]
            possible_paths.extend([
                os.path.join(java_home, "bin", "java.exe"),
                os.path.join(java_home, "bin", "java")
            ])
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "-version"], 
                    capture_output=True, 
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
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
        
        # Формируем команду для запуска PlantUML
        cmd = [
            self.java_path,
            "-Djava.awt.headless=true",
            "-jar", self.jar_path,
            "-charset", "UTF-8",
            f"-t{output_format}",
            "-pipe"
        ]
        
        try:
            # Запускаем процесс с передачей кода через stdin
            # ВАЖНО: передаем байты, а не строку
            result = subprocess.run(
                cmd,
                input=plantuml_code.encode('utf-8'),  # Кодируем строку в байты
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = f"PlantUML rendering failed:\nSTDERR: {result.stderr.decode('utf-8', errors='replace')}"
                raise RuntimeError(error_msg)
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("PlantUML rendering timeout (30 seconds)")
        except Exception as e:
            raise RuntimeError(f"PlantUML rendering error: {str(e)}")


def encode_plantuml_text(plantuml_code: str) -> str:
    """
    Кодирует PlantUML код для использования в текстовом формате URL
    Использует простое URL-кодирование для текстового формата
    """
    import urllib.parse
    
    # Убираем начальные/конечные пробелы
    plantuml_code = plantuml_code.strip()
    
    # Убеждаемся, что код начинается с @startuml и заканчивается @enduml
    if not plantuml_code.startswith('@start'):
        plantuml_code = '@startuml\n' + plantuml_code
    if not plantuml_code.endswith('@enduml'):
        plantuml_code = plantuml_code + '\n@enduml'
    
    # Возвращаем URL-кодированный текст
    return urllib.parse.quote(plantuml_code)


def encode_plantuml_compressed(plantuml_code: str) -> str:
    """
    Кодирует PlantUML код в сжатом формате для использования в URL
    Использует специальный формат кодирования PlantUML сервера
    """
    import string
    
    # Убираем начальные/конечные пробелы
    plantuml_code = plantuml_code.strip()
    
    # Убеждаемся, что код начинается с @startuml и заканчивается @enduml
    if not plantuml_code.startswith('@start'):
        plantuml_code = '@startuml\n' + plantuml_code
    if not plantuml_code.endswith('@enduml'):
        plantuml_code = plantuml_code + '\n@enduml'
    
    # Сжимаем с помощью zlib (deflate)
    compressed = zlib.compress(plantuml_code.encode('utf-8'), 9)[2:-4]
    
    # Специальная base64-подобная кодировка PlantUML
    # Используем алфавит PlantUML
    plantuml_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    
    # Кодируем в специальном формате PlantUML
    result = []
    for i in range(0, len(compressed), 3):
        if i+2 < len(compressed):
            b1, b2, b3 = compressed[i], compressed[i+1], compressed[i+2]
            result.append(plantuml_alphabet[b1 >> 2])
            result.append(plantuml_alphabet[((b1 & 0x3) << 4) | (b2 >> 4)])
            result.append(plantuml_alphabet[((b2 & 0xF) << 2) | (b3 >> 6)])
            result.append(plantuml_alphabet[b3 & 0x3F])
        elif i+1 < len(compressed):
            b1, b2 = compressed[i], compressed[i+1]
            result.append(plantuml_alphabet[b1 >> 2])
            result.append(plantuml_alphabet[((b1 & 0x3) << 4) | (b2 >> 4)])
            result.append(plantuml_alphabet[(b2 & 0xF) << 2])
        else:
            b1 = compressed[i]
            result.append(plantuml_alphabet[b1 >> 2])
            result.append(plantuml_alphabet[(b1 & 0x3) << 4])
    
    return ''.join(result)


# Глобальный экземпляр рендерера
_renderer = None


def get_renderer() -> Optional[PlantUMLRenderer]:
    """Получение глобального экземпляра рендерера"""
    global _renderer
    if _renderer is None:
        try:
            _renderer = PlantUMLRenderer()
        except RuntimeError as e:
            st.warning(f"⚠️ {str(e)}")
            st.info("Будет использован онлайн-рендерер")
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
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        .render-info {{
                            color: #4caf50;
                            font-size: 12px;
                            margin-top: 10px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="plantuml-container">
                        <img src="data:image/png;base64,{base64_image}" alt="PlantUML Diagram">
                        <div class="render-info">✓ Rendered locally</div>
                    </div>
                </body>
                </html>
                """
                
                components.html(html_code, height=height, scrolling=True)
                return
                
            except Exception as e:
                st.warning(f"⚠️ Локальный рендерер не сработал: {e}")
                st.info("Используется онлайн-рендерер")
    
    # Запасной вариант: онлайн рендеринг
    # Используем два подхода - текстовый формат и сжатый
    try:
        # Для основного сервера используем текстовый формат с префиксом ~1
        text_encoded = encode_plantuml_text(plantuml_code)
        # Для альтернативных серверов пробуем сжатый формат
        compressed_encoded = encode_plantuml_compressed(plantuml_code)
    except Exception as e:
        st.error(f"Ошибка кодирования PlantUML: {e}")
        st.code(plantuml_code, language="text")
        return
    
    # Используем несколько альтернативных серверов и форматов
    # ~1 префикс указывает на текстовый формат
    servers = [
        f"https://www.plantuml.com/plantuml/png/~1{text_encoded}",
        f"https://www.plantuml.com/plantuml/png/{compressed_encoded}",
        f"https://kroki.io/plantuml/png/{compressed_encoded}",
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
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .error-message {{
                color: #d32f2f;
                background-color: #ffebee;
                padding: 16px;
                border-radius: 4px;
                border-left: 4px solid #d32f2f;
                margin-top: 20px;
            }}
            .loading {{
                color: #666;
                font-style: italic;
                margin: 20px 0;
            }}
            .render-info {{
                color: #2196f3;
                font-size: 12px;
                margin-top: 10px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .spinner {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid #2196f3;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            .code-preview {{
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                text-align: left;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="plantuml-container">
            <div id="loading-{diagram_id}" class="loading">
                <div class="spinner"></div>
                Загрузка диаграммы...
            </div>
            <img id="diagram-{diagram_id}" style="display:none;" alt="PlantUML Diagram">
            <div id="render-info-{diagram_id}" class="render-info" style="display:none;">
                ✓ Rendered online
            </div>
            <div id="error-{diagram_id}" class="error-message" style="display:none;">
                <strong>Ошибка загрузки диаграммы PlantUML</strong><br><br>
                Возможные причины:<br>
                • Проблемы с подключением к серверу PlantUML<br>
                • Некорректный синтаксис PlantUML кода<br>
                • Слишком большая диаграмма для онлайн-рендеринга<br><br>
                <details>
                    <summary>Показать код диаграммы</summary>
                    <pre style="text-align: left; margin-top: 10px; background: #f5f5f5; padding: 10px; border-radius: 4px;">{plantuml_code.replace('<', '&lt;').replace('>', '&gt;')}</pre>
                </details>
            </div>
        </div>
        <script>
            const servers = {servers};
            const diagramId = '{diagram_id}';
            let currentServer = 0;
            let failedServers = [];
            
            function loadDiagram() {{
                if (currentServer >= servers.length) {{
                    console.error('All servers failed:', failedServers);
                    document.getElementById('loading-' + diagramId).style.display = 'none';
                    document.getElementById('error-' + diagramId).style.display = 'block';
                    return;
                }}
                
                const img = document.getElementById('diagram-' + diagramId);
                const loading = document.getElementById('loading-' + diagramId);
                const renderInfo = document.getElementById('render-info-' + diagramId);
                
                const currentUrl = servers[currentServer];
                console.log('Trying server ' + currentServer + ':', currentUrl);
                
                img.onload = function() {{
                    console.log('Successfully loaded from server ' + currentServer);
                    loading.style.display = 'none';
                    img.style.display = 'block';
                    renderInfo.style.display = 'block';
                }};
                
                img.onerror = function() {{
                    console.log('Failed to load from server ' + currentServer + ':', currentUrl);
                    failedServers.push(currentUrl);
                    currentServer++;
                    setTimeout(() => loadDiagram(), 500);
                }};
                
                img.src = currentUrl;
            }}
            
            // Начинаем загрузку с небольшой задержкой
            setTimeout(() => loadDiagram(), 100);
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
    info = {
        "java_available": False,
        "java_path": None,
        "plantuml_available": False,
        "plantuml_path": None,
        "can_render_locally": False
    }
    
    try:
        renderer = PlantUMLRenderer()
        info.update({
            "java_available": True,
            "java_path": renderer.java_path,
            "plantuml_available": True,
            "plantuml_path": renderer.jar_path,
            "can_render_locally": True
        })
    except RuntimeError as e:
        info["error"] = str(e)
    
    return info


def download_plantuml_jar(url: str = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar") -> bool:
    """
    Скачивает plantuml.jar из указанного URL
    
    Args:
        url: URL для скачивания plantuml.jar
        
    Returns:
        True если скачивание успешно, иначе False
    """
    try:
        import requests
        
        # Создаем директорию lib если её нет
        lib_dir = "lib"
        os.makedirs(lib_dir, exist_ok=True)
        
        # Путь для сохранения файла
        jar_path = os.path.join(lib_dir, "plantuml.jar")
        
        # Скачиваем файл с прогресс-баром
        with st.spinner(f"Скачивание plantuml.jar..."):
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(jar_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size
                            st.progress(progress)
        
        st.success(f"✅ Файл plantuml.jar успешно скачан в {jar_path}")
        return True
        
    except requests.RequestException as e:
        st.error(f"❌ Ошибка скачивания: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Неожиданная ошибка: {e}")
        return False


# Тестовая функция для проверки рендеринга
def test_render():
    """Тестирует рендеринг с простой диаграммой"""
    test_code = """
    @startuml
    Alice -> Bob: Hello
    Bob --> Alice: Hi there!
    @enduml
    """
    
    st.subheader("Тест рендеринга PlantUML")
    
    # Проверяем требования
    reqs = check_requirements()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Java:**", "✅" if reqs["java_available"] else "❌")
        if reqs["java_path"]:
            st.caption(f"Path: {reqs['java_path']}")
    
    with col2:
        st.write("**PlantUML JAR:**", "✅" if reqs["plantuml_available"] else "❌")
        if reqs["plantuml_path"]:
            st.caption(f"Path: {reqs['plantuml_path']}")
    
    # Рендерим тестовую диаграмму
    st.write("**Тестовая диаграмма:**")
    render_plantuml(test_code, height=300)