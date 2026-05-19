#include <stdlib.h>
#include <stdio.h>

int main(int args, char** argv) {
    // for (int i = 0; i < args; i++) {
    //     printf("%s\n", argv[i]);
    // }
    // int i = 0;
    // while( argv[i] != NULL) {
    //     printf("hello");
    //     i++;
    // }
    // return 0;
    FILE *fin = fopen("input.txt", "r");
    if (fin == NULL) {
        perror("Ошибка компиляции!");
        return 1;
    }
    int res = fclose(fin);
    if (res != 0) {
        perror("Ошибка при закрытии!");
        return 1;
    }
    return 0;
}