#include <stdio.h>

int main() {
    int a, b;
    char op;
    scanf("%d%c%d", &a, &op, &b);
    double ans = 0;
    switch (op) {
        case '+':
            ans = (double)a + b;
            break;
        case '-':
            ans = (double)a - b;
            break;
        case '*':
            ans = (double)a * b;
            break;
        case '/':
            ans = (double)a / (double)b;
            break;
    }
    printf("%.12lf\n", ans);
    return 0;
}