package game;

import java.util.Arrays;

public class MNKBoardRhombus extends MNKBoard {
    private final int m_;
    private final int n_;

    private void fillDiagonal(int x, int y, int cnt) {
        for (int i = 0; i < cnt; i++) {
            if (field[x + i][y + i] != Cell.E) {
                field[x + i][y + i] = Cell.E;
                stayedCells++;
            }
        }
    }

    public MNKBoardRhombus(int m, int n, int k) {
        super(n + m - 1, n + m - 1, k);
        this.m_ = m;
        this.n_ = n;
        fill();
    }

    @Override
    public void clear(){
        fill();
    }

    private void fill() {
        stayedCells = 0;
        for (Cell[] row : field) {
            Arrays.fill(row, Cell.N);
        }
        int border = m_ >= 3 ? m_ / 2 + 1 : m_ / 2;
        if (m_ == 1) {
            fillDiagonal(0, 0, n_);
            return;
        }
        for (int i = 0; i < border; i++) {
            fillDiagonal(m_ - 1 - i, i, n_);
            fillDiagonal(m_ - 1 - i, i + 1, n_ - 1);
            fillDiagonal(i, m_ - 1 - i, n_);
            fillDiagonal(i + 1, m_ - 1 - i, n_ - 1);
        }
    }
}
