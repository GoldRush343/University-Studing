package game;

public class PositionProxy implements Position{
    private final int m; // rows
    private final int n; // cols
    private final Cell[][] field;

    public PositionProxy(Board board) {
        this.m = board.getN();
        this.n = board.getM();
        this.field = board.getField();
    }

    public int getM() {
        return m;
    }
    public int getN(){
        return n;
    }

    private boolean isInField(int row, int col) {
        return 0 <= row && row < m
                && 0 <= col && col < n;
    }

    @Override
    public boolean isValid(Move move) {
        return isInField(move.getRow(), move.getCol())
                && field[move.getRow()][move.getCol()] == Cell.E;
    }
}
