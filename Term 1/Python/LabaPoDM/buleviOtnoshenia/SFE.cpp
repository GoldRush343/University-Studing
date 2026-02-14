#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<vector<int>> preds(n + 1);
    vector<vector<int>> tables(n + 1);
    vector<int> leaves;

    // Чтение входных данных
    for (int i = 1; i <= n; ++i) {
        int m;
        cin >> m;
        if (m == 0) {
            leaves.push_back(i);
        } else {
            preds[i].resize(m);
            for (int j = 0; j < m; ++j) {
                cin >> preds[i][j];
            }
            int sz = 1 << m;
            tables[i].resize(sz);
            for (int j = 0; j < sz; ++j) {
                cin >> tables[i][j];
            }
        }
    }

    // Вычисление глубины
    vector<int> depth(n + 1, 0);
    for (int i = 1; i <= n; ++i) {
        if (preds[i].empty()) {
            depth[i] = 0;
        } else {
            int maxd = 0;
            for (int p : preds[i]) {
                maxd = max(maxd, depth[p]);
            }
            depth[i] = maxd + 1;
        }
    }

    cout << depth[n] << '\n';

    // Обработка всех возможных масок
    int k = leaves.size();
    int max_mask = 1 << k;
    vector<char> s(max_mask);
    vector<int> bit_pos(k);
    for (int j = 0; j < k; ++j) {
        bit_pos[j] = k - 1 - j;
    }

    vector<int> value(n + 1);
    for (int mask = 0; mask < max_mask; ++mask) {
        for (int j = 0; j < k; ++j) {
            value[leaves[j]] = (mask >> bit_pos[j]) & 1;
        }
        for (int i = 1; i <= n; ++i) {
            if (preds[i].empty()) continue;
            int j = 0;
            for (int p : preds[i]) {
                j = (j << 1) | value[p];
            }
            value[i] = tables[i][j];
        }
        s[mask] = '0' + value[n];
    }

    cout.write(s.data(), max_mask);
    cout << '\n';

    return 0;
}
