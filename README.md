# MaRiTs
Основные команды на создание 
git config --global user.name "Your Name"
git config --global user.email "your_email@whatever.com"

Создать репу 
git init

Добавить файл к индексации 
git add hello.html

Закоммитить проиндексированное 
git commit -m "Init commit"

Посмотреть незакоммиченные изменения 
git status

Проиндексировать, а потом закоммитить все файлы 
(add + commit) bash git commit -a -m "Init commit" 
История 
git log

git log --all --pretty=format:"%h %cd %s (%an)" --since="7 days ago" --author=Lex

git log --pretty=format:"%h %ad | %s%d [%an]" --date=short
В деталях: - --pretty="..." — определяет формат вывода. - %h — укороченный хеш коммита. - %ad — дата коммита.
- | — просто визуальный разделитель. - %s — комментарий. - %d — дополнения коммита («головы» веток или теги). -
%an — имя автора. - --date=short — сохраняет формат даты коротким и симпатичным. 
Конфиг пример (чтобы много не печатать) 
git config --global format.pretty '%h %ad | %s%d [%an]' 
git config --global log.date short

Работа с прошлым 
Снятие индексацию с изменений (откатиться) 
git restore --staged

Посмотреть (переключиться) коммит по хэшу 
git checkout <hash>

C:\Users\student\AppData\Local\miniconda3\Library\usr\bin;C:\Users\student\AppData\Local\miniconda3\Library\bin;C
\Users\student\AppData\Local\miniconda3\Scripts; 
git credential-cache exit 
git checkout develop git pull origin develop # Обновляемся git checkout -b feature/my-task # Создаем ветку 
ПАТОМ 
1. Переходим в develop 
git checkout develop 
2. Подтягиваем свежие изменения от коллег (на всякийслучай) 
git pull origin develop 
3. Вливаем свою фичу 
git merge feature/my-task 
4. Удаляем временную ветку 
git branch -d feature/my-task 
5. Отправляем в облако 
git push origin develop 
https://github.com/LexTheBright/MaRiTs.git 
git@github.com:LexTheBright/MaRiTs.git 
ghp_LSwipSrkNvferEK0yJCcqX1ldzWwcB45jxJ