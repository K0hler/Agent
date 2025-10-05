#!/usr/bin/env python3
"""
Модуль для валидации и исправления синтаксиса PlantUML кода
"""

import re
from typing import List, Tuple


def fix_plantuml_syntax(plantuml_code: str) -> str:
    """
    Исправляет распространенные синтаксические ошибки в PlantUML коде
    
    Args:
        plantuml_code: Исходный PlantUML код
        
    Returns:
        Исправленный PlantUML код
    """
    if not plantuml_code:
        return plantuml_code
    
    lines = plantuml_code.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # 1. Исправляем "!thme" на "!theme"
        if '!thme' in line:
            line = line.replace('!thme', '!theme')
        
        # 2. Убираем двоеточие перед if, else, endif
        # Ищем паттерны типа ":if", ":else", ":endif"
        patterns_to_fix = [
            (r'^\s*:if\b', 'if'),
            (r'^\s*:else\b', 'else'),
            (r'^\s*:endif\b', 'endif'),
            (r'^\s*:start\b', 'start'),
            (r'^\s*:stop\b', 'stop'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            if re.match(pattern, line):
                line = re.sub(pattern, replacement, line)
                break
        
        # 3. Проверяем правильность структуры if-then-endif
        # Убедимся, что после if есть then
        if re.match(r'^\s*if\s*\(.*\)\s*$', line) and 'then' not in line:
            # Добавляем then в конец строки, если его нет
            line = line.rstrip() + ' then'
        
        # 4. Проверяем, что все if имеют соответствующие endif
        # Это делается на уровне всего кода, а не отдельной строки
        
        # 5. Убираем лишние пробелы в начале строки (нормализация отступов)
        line = line.rstrip()
        
        fixed_lines.append(line)
    
    # 6. Проверка баланса if/endif
    fixed_code = '\n'.join(fixed_lines)
    fixed_code = _validate_if_structure(fixed_code)
    
    return fixed_code


def _validate_if_structure(plantuml_code: str) -> str:
    """
    Проверяет и исправляет структуру if-then-endif
    
    Args:
        plantuml_code: PlantUML код
        
    Returns:
        Исправленный PlantUML код
    """
    lines = plantuml_code.split('\n')
    fixed_lines = []
    if_stack = []
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Проверяем на начало блока if
        if stripped_line.startswith('if '):
            if_stack.append(i)
        
        # Проверяем на конец блока if
        elif stripped_line.startswith('endif'):
            if if_stack:
                if_stack.pop()
        
        # Добавляем then, если if не имеет then
        elif stripped_line.startswith('if ') and ' then' not in stripped_line:
            lines[i] = line.rstrip() + ' then'
        
        fixed_lines.append(lines[i])
    
    # Если остались незакрытые if, добавляем endif
    for if_line_index in if_stack:
        # Находим соответствующий if и добавляем после него endif
        for i in range(if_line_index + 1, len(fixed_lines)):
            if fixed_lines[i].strip():
                # Вставляем endif перед следующей непустой строкой
                fixed_lines.insert(i, 'endif')
                break
        else:
            # Если нет следующих непустых строк, добавляем в конец
            fixed_lines.append('endif')
    
    return '\n'.join(fixed_lines)


def validate_plantuml_syntax(plantuml_code: str) -> Tuple[bool, List[str]]:
    """
    Проверяет синтаксис PlantUML кода и возвращает список ошибок
    
    Args:
        plantuml_code: PlantUML код для проверки
        
    Returns:
        Кортеж (is_valid, errors_list)
    """
    errors = []
    
    if not plantuml_code:
        errors.append("Пустой PlantUML код")
        return False, errors
    
    lines = plantuml_code.split('\n')
    
    # Проверка наличия @startuml и @enduml
    has_start = any('@startuml' in line for line in lines)
    has_end = any('@enduml' in line for line in lines)
    
    if not has_start:
        errors.append("Отсутствует @startuml")
    if not has_end:
        errors.append("Отсутствует @enduml")
    
    # Проверка баланса if/endif
    if_count = 0
    endif_count = 0
    
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('if '):
            if_count += 1
        elif stripped_line.startswith('endif'):
            endif_count += 1
    
    if if_count != endif_count:
        errors.append(f"Несоответствие количества if ({if_count}) и endif ({endif_count})")
    
    # Проверка на запрещенные слова в ID
    forbidden_ids = ['end', 'click', 'class', 'style', 'subgraph', 'graph', 'flowchart']
    for line in lines:
        for forbidden_id in forbidden_ids:
            if f' as {forbidden_id}' in line or f' {forbidden_id} ' in line:
                errors.append(f"Использование запрещенного ID: {forbidden_id}")
                break
    
    # Проверка на наличие двоеточий перед ключевыми словами
    problematic_patterns = [
        (r'^\s*:if\b', 'Двоеточие перед if'),
        (r'^\s*:else\b', 'Двоеточие перед else'),
        (r'^\s*:endif\b', 'Двоеточие перед endif'),
        (r'^\s*:start\b', 'Двоеточие перед start'),
        (r'^\s*:stop\b', 'Двоеточие перед stop'),
    ]
    
    for line in lines:
        for pattern, error_msg in problematic_patterns:
            if re.match(pattern, line):
                errors.append(error_msg)
                break
    
    # Проверка на "!thme" вместо "!theme"
    if '!thme' in plantuml_code:
        errors.append("Использование '!thme' вместо '!theme'")
    
    return len(errors) == 0, errors


def auto_fix_plantuml(plantuml_code: str) -> Tuple[str, List[str]]:
    """
    Автоматически исправляет PlantUML код и возвращает исправленную версию и список исправлений
    
    Args:
        plantuml_code: Исходный PlantUML код
        
    Returns:
        Кортеж (fixed_code, fixes_applied)
    """
    fixes_applied = []
    fixed_code = plantuml_code
    
    # Проверяем синтаксис
    is_valid, errors = validate_plantuml_syntax(fixed_code)
    
    if not is_valid:
        # Применяем исправления
        original_code = fixed_code
        
        # 1. Исправляем "!thme" на "!theme"
        if '!thme' in fixed_code:
            fixed_code = fixed_code.replace('!thme', '!theme')
            fixes_applied.append("Исправлено '!thme' на '!theme'")
        
        # 2. Убираем двоеточия перед ключевыми словами
        patterns_to_fix = [
            (r'^(\s*):if\b', r'\1if'),
            (r'^(\s*):else\b', r'\1else'),
            (r'^(\s*):endif\b', r'\1endif'),
            (r'^(\s*):start\b', r'\1start'),
            (r'^(\s*):stop\b', r'\1stop'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            fixed_lines = []
            for line in fixed_code.split('\n'):
                new_line = re.sub(pattern, replacement, line)
                if new_line != line:
                    fixes_applied.append(f"Убрано двоеточие перед ключевым словом в строке: {line.strip()}")
                fixed_lines.append(new_line)
            fixed_code = '\n'.join(fixed_lines)
        
        # 3. Добавляем then после if, если его нет
        if_lines = []
        lines = fixed_code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('if ') and ' then' not in line:
                if_lines.append(i)
                lines[i] = line.rstrip() + ' then'
                fixes_applied.append(f"Добавлено 'then' после if в строке: {line.strip()}")
        
        fixed_code = '\n'.join(lines)
        
        # 4. Проверяем и исправляем баланс if/endif
        fixed_code = _validate_if_structure(fixed_code)
        
        # Проверяем, что ошибки были исправлены
        is_valid_after_fix, remaining_errors = validate_plantuml_syntax(fixed_code)
        
        if remaining_errors:
            fixes_applied.append(f"Остающиеся ошибки после автоматического исправления: {', '.join(remaining_errors)}")
    
    return fixed_code, fixes_applied


if __name__ == "__main__":
    # Пример использования
    test_code = """@startuml
!thme plain
title Тестовая диаграмма

:start
:Действие 1;
:if (Условие?) then (Да)
  :Действие 2;
:else (Нет)
  :Действие 3;
:endif
:stop
@enduml"""
    
    print("Исходный код:")
    print(test_code)
    print("\n" + "="*50 + "\n")
    
    fixed_code, fixes = auto_fix_plantuml(test_code)
    
    print("Исправленный код:")
    print(fixed_code)
    print("\nПримененные исправления:")
    for fix in fixes:
        print(f"  - {fix}")
    
    print("\n" + "="*50 + "\n")
    
    # Проверка синтаксиса
    is_valid, errors = validate_plantuml_syntax(fixed_code)
    print(f"Синтаксис валиден: {is_valid}")
    if errors:
        print("Ошибки:")
        for error in errors:
            print(f"  - {error}")
