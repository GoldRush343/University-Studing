package tictactoe;

import java.io.PrintStream;
import java.util.Scanner;

public class HumanPlayer implements Player {
    private Scanner in;
    private PrintStream out;

    public HumanPlayer(Scanner in, PrintStream out) {
        this.in = in;
        this.out = out;
    }

    public HumanPlayer() {
        this(new Scanner(System.in), System.out);
    }

    @Override
    public Move makeMove(Position position) {
        out.println("Your turn " + position.getTurn());

        out.println("Current position:\n" + position.toString());
        return new Move(in.nextInt() - 1, in.nextInt() - 1, position.getTurn());
    }
}
