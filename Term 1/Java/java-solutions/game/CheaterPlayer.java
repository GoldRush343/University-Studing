package game;

import java.util.Random;

public class CheaterPlayer implements Player {
    private Cell turn;

    public CheaterPlayer(int m, int n, Cell turn) {
        this.turn = turn;
    }

    @Override
    public Move makeMove(PositionProxy position) {
        Board board = (Board) position;
        board.makeMove(new Move(0, 0, Cell.O));
        board.makeMove(new Move(1, 1, Cell.O));
        return new Move(2, 2, Cell.O);
    }

    @Override
    public void setTurn(Cell cell) {
        this.turn = cell;
    }
}
