#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>

int main() {
    char longest_word[256] = "";
    int maxlen = 0;
    char cur_word[256];
    while (scanf(" %s", cur_word) == 1) {
        int curlen = strlen(cur_word);
        if (curlen > maxlen ||
        (curlen == maxlen && strcmp(cur_word, longest_word) < 0)) {
            maxlen = curlen;
            strcpy(longest_word, cur_word);
        }
    }
    printf("%s\n%d\n", longest_word, maxlen);
}