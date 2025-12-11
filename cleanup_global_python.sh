#!/bin/bash

# Скрипт для очистки глобальных пакетов Python
# Оставляет только базовые: pip, setuptools, wheel

echo "Проверка установленных пакетов..."

# Получаем список всех установленных пакетов
PACKAGES=$(pip3 list --format=freeze | cut -d'=' -f1)

# Базовые пакеты, которые нужно оставить
KEEP_PACKAGES=("pip" "setuptools" "wheel")

# Список пакетов для удаления
TO_REMOVE=()

for package in $PACKAGES; do
    # Приводим к нижнему регистру для сравнения
    package_lower=$(echo "$package" | tr '[:upper:]' '[:lower:]')
    keep=false
    
    for keep_pkg in "${KEEP_PACKAGES[@]}"; do
        if [ "$package_lower" == "$keep_pkg" ]; then
            keep=true
            break
        fi
    done
    
    if [ "$keep" == false ]; then
        TO_REMOVE+=("$package")
    fi
done

if [ ${#TO_REMOVE[@]} -eq 0 ]; then
    echo "✅ Глобальные пакеты уже чистые!"
    exit 0
fi

echo "Найдено пакетов для удаления: ${#TO_REMOVE[@]}"
echo ""
echo "Список пакетов для удаления:"
for pkg in "${TO_REMOVE[@]}"; do
    echo "  - $pkg"
done

echo ""
read -p "Удалить эти пакеты? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено."
    exit 0
fi

echo "Удаление пакетов..."
for pkg in "${TO_REMOVE[@]}"; do
    pip3 uninstall -y "$pkg" 2>/dev/null || echo "⚠️  Не удалось удалить: $pkg"
done

echo ""
echo "✅ Очистка завершена!"
echo "Остались только базовые пакеты:"
pip3 list
