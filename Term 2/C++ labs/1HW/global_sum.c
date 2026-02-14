#include <stdio.h>

int main() {
    long long ans = 0;
    int cur;
    while( scanf(" %d", &cur) == 1 ) {
        ans += cur;
    }
    printf("%lld\n", ans);
    return 0;
}