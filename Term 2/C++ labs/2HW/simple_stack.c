#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    int n;
    scanf("%d\n", &n);
    stack stack1 = constructor();
    char str[30];
    for (int i = 0; i < n; i++) {
        scanf("%s", str);
        if (strcmp(str, "push") == 0) {
            int el;
            scanf("%d", &el);
            push(&stack1, el);
            printf("ok\n");
        } else if (strcmp(str, "pop") == 0) {
            printf("%d\n", pop(&stack1));
        } else if (strcmp(str, "back") == 0) {
            printf("%d\n", back(&stack1));
        } else if (strcmp(str, "size") == 0) {
            printf("%d\n", stack1.size);
        } else if (strcmp(str, "clear") == 0) {
            clear(&stack1);
            printf("ok\n");
        } else {
            printf("bye\n");
            free(stack1.arr);
            return 0;
        }
    }
    return 0;
}