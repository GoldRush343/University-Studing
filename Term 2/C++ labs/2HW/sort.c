#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct{
    int capacity;
    int size;
    char **arr;
} dynamic_arr;

dynamic_arr constructor() {
    int capacity = 5;
    char **arr = malloc(capacity * sizeof(char*));
    dynamic_arr tmp = {capacity, 0, arr};
    return tmp;
}

void resize(dynamic_arr *pdynamic_arr) {
    pdynamic_arr->capacity *= 2;
    pdynamic_arr->arr = realloc(pdynamic_arr->arr, pdynamic_arr->capacity * sizeof(char*));
}

void push(dynamic_arr *pdynamic_arr, char* el) {
    pdynamic_arr->size++;
    if (pdynamic_arr->size == pdynamic_arr->capacity) {
        resize(pdynamic_arr);
    }
    pdynamic_arr->arr[pdynamic_arr->size-1] = strdup(el);
}

void freeDA(dynamic_arr *pdynamic) {
    for (int i = 0; i < pdynamic->size; i++) {
        free(pdynamic->arr[i]);
    }
    free(pdynamic->arr);
}

void print(dynamic_arr *p) {
    for (int i = 0; i < p->size; i++) {
        printf("%s\n", p->arr[i]);
    }
}
 
int comp(const void* a, const void* b) {
    const char **s1 = (const char**)a;
    const char **s2 = (const char**)b;
    return strcmp(*s1, *s2);
}

int main() {
    int ch;
    dynamic_arr arr = constructor();

    int word_cap = 5;
    char *word = malloc(word_cap * sizeof(char));
    int i = 0;

    while((ch = getchar()) != EOF) {
        if (ch != ' ' && ch != '\n') {
            if (i + 1 == word_cap) {
                word_cap *= 2;
                char *new_word = realloc(word, word_cap * sizeof(char));
                word = new_word;
            }
            word[i++] = ch;
        } else if (i > 0) {
            word[i] = '\0';
            push(&arr, word);
            free(word);
            word_cap = 5;
            word = malloc(word_cap * sizeof(char));
            i = 0;
        }
    }
    if (i > 0) {
        word[i] = '\0';
        push(&arr, word);
    }
    free(word);
    qsort(arr.arr, arr.size, sizeof(char*), comp);
    print(&arr);
    freeDA(&arr);
    return 0;
}