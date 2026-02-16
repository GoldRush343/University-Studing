#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>

typedef struct {
    int capacity;
    int size;
    int *arr;

} stack;

stack constructor() {
    int capacity = 5;
    int *arr = malloc(capacity * sizeof(int));
    stack tmp = {capacity, 0, arr};
    return tmp;
}

void resize(stack *pstack) {
    pstack->capacity *= 2;
    pstack->arr = realloc(pstack->arr, pstack->capacity * sizeof(int));
}

void push(stack *pstack, int el) {
    pstack->size++;
    if (pstack->size == pstack->capacity) {
        resize(pstack);
    }
    pstack->arr[pstack->size-1] = el;
}

int pop (stack *pstack) {
    int ans = pstack->arr[pstack->size-1];
    pstack->size--;
    return ans;
}

void clear (stack *pstack) {
    free(pstack->arr);
    pstack->capacity = 5;
    pstack->size = 0;
    pstack->arr = malloc(pstack->capacity * sizeof(int));
}

int back (stack *pstack) {
    return pstack->arr[pstack->size-1];
}

int main() {
    char ch;
    stack st = constructor();
    while((ch = getchar()) != '\n') {
        if (ch == ' ') continue;
        if (isdigit(ch)){
            push(&st, ch - '0');
        } else {
            int a = pop(&st);
            int b = pop(&st);
            //printf("%d %d\t", a, b);
            switch (ch){
            case '+':
                push(&st, b + a);
                break;
            case '-': 
                push(&st, b - a);
                break;
            case '*':
                push(&st, b * a);
                break;
            default:
                break;
            }
        }
    }
    printf("%d\n", pop(&st));
    free(st.arr);
    return 0;
}