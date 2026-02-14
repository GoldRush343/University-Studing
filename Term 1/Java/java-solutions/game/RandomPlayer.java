package game;

import java.util.Random;

public class RandomPlayer implements Player {
    private Cell turn;
    private final Random random = new Random();

    public RandomPlayer(Cell turn) {
        this.turn = turn;
    }
    public RandomPlayer(){
        this.turn = Cell.X;
    }

    @Override
    public Move makeMove(PositionProxy position) {
        while (true) {
            Move move = new Move(
                    random.nextInt(position.getM()),
                    random.nextInt(position.getN()),
                    turn);
            if (position.isValid(move)) {
                return move;
            }
        }
    }

    @Override
    public void setTurn(Cell cell) {
        this.turn = cell;
    }
}

