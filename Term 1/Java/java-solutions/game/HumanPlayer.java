package game;

import java.io.PrintStream;
import java.util.Scanner;

public class HumanPlayer implements Player {
    private Cell turn;
    private final Scanner in;
    private final PrintStream out;

    public HumanPlayer(Cell turn, Scanner in, PrintStream out) {
        this.turn = turn;
        this.in = in;
        this.out = out;
    }

    public HumanPlayer(Cell turn) {
        this(turn, new Scanner(System.in), System.out);
    }

    public HumanPlayer() {
        this(Cell.X, new Scanner(System.in), System.out);
    }

    private void inputMistake(){
        out.println("Wrong move, try again!");
    }

    private int scanNum(){
        while(!in.hasNextInt()){
            in.nextLine();
            inputMistake();
        }
        return in.nextInt();
    }

    @Override
    public Move makeMove(PositionProxy position) {
        int x = scanNum();
        int y = scanNum();
        Move move = new Move(x-1, y-1, turn);
        while(!position.isValid(move)){
            inputMistake();
            x = scanNum();
            y = scanNum();
            move = new Move(x-1, y-1, turn);
        }
        return move;
    }

    @Override
    public void setTurn(Cell cell) {
        this.turn = cell;
    }
}
