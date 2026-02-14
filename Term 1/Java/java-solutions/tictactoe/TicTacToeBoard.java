package tictactoe;

import java.util.Arrays;
import java.util.Map;

public class TicTacToeBoard implements Board, Position {
    private final Cell[][] field;
    private Cell turn;

    private final static Map<Cell, String> CELL_STRING_MAP = Map.of(
            Cell.X, "X",
            Cell.O, "O",
            Cell.E, " "
    ) ;

    public TicTacToeBoard() {
        field = new Cell[3][3];
        for (Cell[] row : field) {
            Arrays.fill(row, Cell.E);
        }
        turn = Cell.X;
    }


    @Override
    public Position getPosition() {
        return this;
    }

    private boolean checkRow(){
        for (int i = 0; i < 3; i++){
            if (field[0][i] == turn && field[1][i] == turn && field[2][i] == turn) {
                return true;
            }
        }
        return false;
    }
    private boolean checkCol(){
        for (int i = 0; i < 3; i++){
            if (field[i][0] == turn && field[i][1] == turn && field[i][2] == turn) {
                return true;
            }
        }
        return false;
    }
    private boolean checkDiagonal(){
        return (field[0][0] == turn && field[1][1] == turn && field[2][2] == turn) ||
                (field[2][0] == turn && field[1][1] == turn && field[0][2] == turn);
    }

    private boolean isDraw(){
        int stayedCells = 0;
        for (int row = 0; row < 3; row++) {
            for (int cell = 0; cell < 3; cell++) {
                if (field[row][cell] == Cell.E) {
                    stayedCells++;
                }
            }
        }
        return stayedCells == 0;
    }


    @Override
    public Result makeMove(Move move) {
        if (!isValid(move)) {
            return Result.LOSE;//need to change this
        }
        field[move.getRow()][move.getCol()] = move.getCell();
        if ( checkCol() || checkRow() || checkDiagonal()){
            return Result.WIN;
        }
        if (isDraw()) {
            return Result.DRAW;
        }
        turn = turn == Cell.X ? Cell.O : Cell.X;
        return Result.UNKNOWN;
    }

    @Override
    public Cell getTurn() {
        return turn;
    }

    public boolean isValid(Move move) {
        return 0 <= move.getCol() && move.getCol() < 3
                && 0 <= move.getRow() && move.getRow() < 3
                && field[move.getRow()][move.getCol()] == Cell.E
                && move.getCell() == turn;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("  123\n +---\n");
        for (int row = 0; row < 3; row++) {
            sb.append(row + 1);
            sb.append("|");
            for (int cell = 0; cell < 3; cell++) {
                sb.append(CELL_STRING_MAP.get(field[row][cell]));
            }
            sb.append("\n");
        }
        return sb.toString();
    }
}
