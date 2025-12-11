#!/bin/bash

# Скрипт для обновления pip во всех установленных версиях Python

echo "Поиск всех установленных версий Python..."

# Находим все python3 и python исполняемые файлы
PYTHON_PATHS=$(which -a python3 python 2>/dev/null | sort -u)

# Также ищем в стандартных местах установки
ADDITIONAL_PATHS=(
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "/usr/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/*/bin/python3"
    "/Users/$USER/opt/anaconda3/bin/python3"
)

for pattern in "${ADDITIONAL_PATHS[@]}"; do
    for path in $pattern; do
        if [ -f "$path" ] && [ -x "$path" ]; then
            PYTHON_PATHS="$PYTHON_PATHS $path"
        fi
    done
done

# Убираем дубликаты и сортируем
PYTHON_PATHS=$(echo "$PYTHON_PATHS" | tr ' ' '\n' | sort -u | tr '\n' ' ')

echo "Найдено версий Python:"
for py_path in $PYTHON_PATHS; do
    if [ -f "$py_path" ] && [ -x "$py_path" ]; then
        version=$($py_path --version 2>&1)
        echo "  - $py_path ($version)"
    fi
done

echo ""
read -p "Обновить pip во всех найденных версиях? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено."
    exit 0
fi

echo ""
echo "Обновление pip..."

SUCCESS=0
FAILED=0

for py_path in $PYTHON_PATHS; do
    if [ ! -f "$py_path" ] || [ ! -x "$py_path" ]; then
        continue
    fi
    
    version=$($py_path --version 2>&1)
    echo ""
    echo "Обновление pip для: $py_path ($version)"
    
    if $py_path -m pip install --upgrade pip --quiet 2>/dev/null; then
        new_version=$($py_path -m pip --version 2>&1 | head -1)
        echo "  ✅ Успешно: $new_version"
        ((SUCCESS++))
    else
        echo "  ❌ Ошибка при обновлении"
        ((FAILED++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Готово! Успешно: $SUCCESS, Ошибок: $FAILED"
