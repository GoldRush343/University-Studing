package tictactoe;

public class Game {
    private final Board board;
    private final Player player1;
    private final Player player2;
    private final boolean log;

    public Game(Board board, Player player1, Player player2, boolean log) {
        this.board = board;
        this.player1 = player1;
        this.player2 = player2;
        this.log = log;
    }

    public int play() {
        while (true) {
            int result1 = getResult(1, player1);
            if (result1 != -1) {
                return result1;
            }
            int result2 = getResult(2, player2);
            if (result2 != -1) {
                return result2;
            }
        }
    }

    private int getResult(int no, Player player) {
        Move move = player.makeMove(board.getPosition());
        if (log) {
            System.out.println("Player #" + no + " move: " + move);
            System.out.println(board);
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
