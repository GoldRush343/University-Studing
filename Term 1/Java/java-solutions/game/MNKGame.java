package game;

import java.io.PrintStream;
import java.util.List;
import java.util.Scanner;

public class MNKGame {
    private final Board board;
    private final Player player1;
    private final Player player2;
    private final int m;
    private final int n;
    private final Scanner in;
    private final PrintStream out;
    private final List<String> players = List.of("First", "Second");

    public MNKGame(Board board, Player player1, Player player2, int m, int n, Scanner in, PrintStream out) {
        this.board = board;
        this.player1 = player1; // X
        this.player2 = player2; // O
        this.m = m;
        this.n = n;
        this.in = in;
        this.out = out;
    }

    private int move(int no, Player player) {
        out.println(players.get(no - 1) + " Player move:");
        int result1 = getResult(no, player);
        out.println(board);
        return result1;
    }

    public int play() {
        out.println(board);
        player1.setTurn(Cell.X);
        player2.setTurn(Cell.O);
        while (true) {
            int mv1 = move(1, player1);
            if (mv1 != -1) {
                return mv1;
            }
            int mv2 = move(2, player2);
            if (mv2 != -1) {
                return mv2;
            }
        }
    }

    private int getResult(int no, Player player) {
        Move move;
        try {
            move = player.makeMove(board.getPos());
        } catch (RuntimeException e) {
            return 3 - no;
        }
        Result result = board.makeMove(move);
        if (result == Result.WIN) {
            return no;
        } else if (result == Result.LOSE) {
            return 3 - no;
        } else if (result == Result.DRAW) {
            return 0;
        }
        return -1;
    }
}
