package game;

import java.util.Arrays;
import java.util.Map;

public class MNKBoard implements Board {
    protected int m; // rows
    protected int n; // cols
    protected final int k;
    protected Cell[][] field;
    protected int stayedCells;
    protected final String delimiter = " ";

    protected final static Map<Cell, String> CELL_STRING_MAP = Map.of(
            Cell.X, "X",
            Cell.O, "O",
            Cell.E, ".",
            Cell.N, " "
    );

    public MNKBoard(int m, int n, int k) {
        this.m = m;
        this.n = n;
        this.k = k;
        fill();
    }

    public boolean isValid(Move move) {
        return isInField(move.getRow(), move.getCol())
                && field[move.getRow()][move.getCol()] == Cell.E;
    }

    public PositionProxy getPos() {
        return new PositionProxy(this);
    }

    protected boolean isInField(int row, int col) {
        return 0 <= row && row < m
                && 0 <= col && col < n;
    }

    private boolean checkLine(Move move, int dr, int dc) {
        int row = move.getRow();
        int col = move.getCol();
        Cell turn = move.getCell();
        int cnt = 0;
        int maxCnt = 0;
        for (int i = -k + 1; i <= k - 1; i++) {
            if (isInField(row + i * dr, col + i * dc) && field[row + i * dr][col + i * dc] == turn) {
                cnt++;
                maxCnt = Math.max(cnt, maxCnt);
            } else {
                cnt = 0;
            }
        }
        return maxCnt >= k;
    }

    private boolean isWin(Move move) {
        return checkLine(move, 1, 0) || checkLine(move, 0, 1)
                || checkLine(move, 1, 1) || checkLine(move, -1, 1);
    }

    private boolean isDraw() {
        return stayedCells == 0;
    }

    @Override
    public Result makeMove(Move move) {
        if (!isValid(move)) {
            return Result.LOSE;
        }
        field[move.getRow()][move.getCol()] = move.getCell();
        stayedCells--;
        if (isWin(move)) {
            return Result.WIN;
        }
        if (isDraw()) {
            return Result.DRAW;
        }
        return Result.UNKNOWN;
    }

    @Override
    public int getN() {
        return n;
    }

    @Override
    public int getM() {
        return m;
    }

    @Override
    public Cell[][] getField() {
        return field;
    }

    protected int getWidth(int num) {
        return Integer.toString(num).length();
    }

    protected static String setWidth(String input, int length) {
        if (input.length() >= length) {
            return input;
        }
        int total = length - input.length();
        int left = total / 2;
        int right = total - left;
        return " ".repeat(left) + input + " ".repeat(right);
    }

    private void fill() {
        field = new Cell[m][n];
        for (Cell[] row : field) {
            Arrays.fill(row, Cell.E);
        }
        stayedCells = n * m;
    }

    @Override
    public String toString() {
        int maxWidth = getWidth(n) + 1;
        StringBuilder sb = new StringBuilder();

        sb.append(" ".repeat(maxWidth));
        for (int i = 0; i < n; i++) {
            sb.append(setWidth(Integer.toString(i + 1), maxWidth + 1));
        }
        sb.append('\n');

        for (int row = 0; row < m; row++) {
            sb.append(setWidth(Integer.toString(row + 1), maxWidth));
            sb.append(delimiter);
            for (int cell = 0; cell < n; cell++) {
                String cellValue = CELL_STRING_MAP.get(field[row][cell]);
                sb.append(setWidth(cellValue, maxWidth));
                sb.append(delimiter);
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    @Override
    public void clear(){
        fill();
    }
}
