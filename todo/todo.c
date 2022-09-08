#define MAXLINES 50
#define MAXLEN 255

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>
#include <unistd.h>

char *options[] = { "new", "delete", "edit", "exit" };

int height, width, key, padding;
int selected_option, selected_todo = 0;

char **todo;
int todo_length = 0;

char *filename;

void init() {
    initscr();
    keypad(stdscr, 1);
    noecho();
    curs_set(0);

    start_color();
    use_default_colors();
    init_pair(1, COLOR_BLACK, COLOR_WHITE);
}

void deinit() {
    keypad(stdscr, 0);
    echo();
    curs_set(1);
    endwin();
}

void loadTodo() {
    FILE *file = fopen(filename, "r");

    if (file == NULL)
        return;

    while (!feof(file) && !ferror(file))
        if (fgets(todo[todo_length], MAXLEN, file) != NULL)
            todo_length++;

    for (int index = 0; index < todo_length; index++)
        todo[index][strlen(todo[index]) - 1] = '\0';

    fclose(file);
}

void saveTodo() {
    FILE *file = fopen(filename, "w");

    if (file == NULL)
        return;

    for (int index = 0; index < todo_length; index++)
        fprintf(file, "%s\n", todo[index]);

    fclose(file);
}

void editTodo() {
    echo();
    curs_set(1);
    mvgetnstr(selected_todo, width / 2, todo[selected_todo], MAXLEN);
    noecho();
    curs_set(0);

    saveTodo();
}

void update() {
    clear();

    padding = 0;

    for (int index = 0; index < sizeof(options) / 8; index++) {
        if (index == selected_option)
            attron(COLOR_PAIR(1));

        mvprintw(height - 2, (width >= 54 ? 7 : 1) * (index + 1) + padding, options[index]);
        attroff(COLOR_PAIR(1));

        padding += strlen(options[index]);
    }

    for (int index = 0; index < todo_length; index++) {
        if (index == selected_todo)
            attron(COLOR_PAIR(1));

        mvprintw(index, 1, "%d. %s", index + 1, todo[index]);
        attroff(COLOR_PAIR(1));
    }

    refresh();
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <filename>", argv[0]);
        return 1;
    }

    filename = argv[1];

    todo = malloc(MAXLINES * sizeof(char *));

    for (int index = 0; index < MAXLINES; index++)
        todo[index] = malloc(MAXLEN * sizeof(char));

    loadTodo();

    init();

    getmaxyx(stdscr, height, width);
    update();

    while (true) {
        key = getch();

        switch (key) {
            case KEY_RIGHT:
            case 'd':
            case 'D':
                if (selected_option < sizeof(options) / 8 - 1)
                    selected_option++;
                break;

            case KEY_LEFT:
            case 'a':
            case 'A':
                if (selected_option > 0)
                    selected_option--;
                break;

            case KEY_DOWN:
            case 's':
            case 'S':
                if (selected_todo < todo_length - 1)
                    selected_todo++;
                break;

            case KEY_UP:
            case 'w':
            case 'W':
                if (selected_todo > 0)
                    selected_todo--;
                break;

            case 10:
                switch (selected_option) {
                    case 0:
                        selected_todo = todo_length++;

                        update();
                        editTodo();

                        break;

                    case 1:
                        for (int index = selected_todo; index < todo_length - 1; index++)
                            todo[index] = todo[index + 1];

                        todo = realloc(todo, --todo_length * sizeof(char *));
                        selected_todo = 0;

                        saveTodo();

                        break;

                    case 2:
                        editTodo();
                        break;

                    case 3:
                        deinit();
                        return 0;
                }

                break;
        }

        getmaxyx(stdscr, height, width);
        update();
        usleep(100000);
    }

    deinit();

    return 0;
}