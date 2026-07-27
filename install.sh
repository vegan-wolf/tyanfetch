#!/bin/bash

GREEN='\033[1;32m'
BLUE='\033[1;34m'
YElLOW='\033[1;33m'
RESET='\033[0m'

echo -e "${BLUE}!!! Установка tyanfetch !!!${RESET}\n"

PYTHON_SCRIPT="tyanfetch.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo -e "${YELLOW}Ошибка: файл $PYTHON_SCRIPT не найден в текущей папке!${RESET}"
  echo "Убедитесь, что запускаете install.sh из папки вашего репозитория."
fi

chmod +x "$PYTHON_SCRIPT"
mkdir -p "$HOME/.local/bin"
TARGET_LINK="$HOME/.local/bin/tyanfetch"

if [ -L "$TARGET_LINK" ] || [ -f "$TARGET_LINK" ]; then
    rm "$TARGET_LINK"
fi

REAL_PATH=$(realpath "$PYTHON_SCRIPT")
ln -s "$REAL_PATH" "$TARGET_LINK"

echo -e "${GREEN}Глобальная команда 'tyanfetch' успешно создана!${NC}"

CURRENT_SHELL=$(basename "$SHELL")
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "\n${YELLOW}Внимание: Папка ~/.local/bin не добавлена в вашу переменную PATH.${NC}"
    if [ "$CURRENT_SHELL" = "fish" ]; then
        echo -e "Выполните команду: ${BLUE}fish_add_path ~/.local/bin${NC}"
    else
        echo -e "Добавьте в свой конфиг строку: ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    fi
fi

echo -e "\n${GREEN}=== Установка завершена! Перезапустите терминал для применения изменений. ===${NC}"