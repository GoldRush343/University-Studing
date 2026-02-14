package tictactoe;

public class Main {
    public static void main(String[] args) {
        Board board = new TicTacToeBoard();
        Player player1 = new RandomPlayer();
        Player player2 = new HumanPlayer();
        Game game = new Game(board, player1, player2, true);
        int result = game.play();
        System.out.println(board);
        if (result == 1) {
            System.out.println("First win");
        } else if (result == 2) {
            System.out.println("Second win");
        } else {
            System.out.println("Draw");
        }
    }
}
