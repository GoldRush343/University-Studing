#include <iostream>
#include <vector>

using namespace std;

vector<int> used;
vector<vector<int>> gr;
vector<int> pr;

bool dfs(int v) {
    used[v] = 1;
    for (int u : gr[v]) {
        if (used[u] == 0) {
            pr[u] = v;
            if (dfs(u)) {
                return true;
            }
        } else if (used[u] == 1) {
            pr[u] = v;
            return true;
        }
    }
    used[v] = 2;
    return false;
}

void print_cycle(int v) {
    vector<int> ans;
    int cur = v;
    int next = pr[v];
    ans.push_back(v);

    while (next != v) {
        ans.push_back(next);
        cur = next;
        next = pr[cur];
    }

    cout << ans.size() << '\n';
    for (int i = ans.size() - 1; i >= 0; i--) {
        cout << ans[i] + 1 << ' ';
    }
    cout << '\n';
}

int main() {
    int n, m;
    cin >> n >> m;
    gr.resize(n);
    used.resize(n, 0);
    pr.resize(n, -1);
    for (int i = 0; i < m; i++) {
        int v, u;
        cin >> v >> u;
        v--; u--;
        gr[v].push_back(u);
    }
    for (int i = 0; i < n; i++) {
        if (used[i] == 0) {
            if (dfs(i)) {
                print_cycle(i);
                return 0;
            }
        }
    }
    cout << "-1\n";
}