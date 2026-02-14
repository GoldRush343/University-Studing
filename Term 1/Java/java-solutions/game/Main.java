package game;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
    private static int m;
    private static int n;
    private static int k;
    public static ScanParams scanParams = new ScanParams("Can't create game with this m, n, k. Try again!");

    private static void printResult(int result) {
        if (result == 1) {
            System.out.println("First win");
        } else if (result == 2) {
            System.out.println("Second win");
        } else {
            System.out.println("Draw");
        }
    }

    public static void main(String[] args) {
        int boardType = chooseBoard();
        List<Player> playerList;
        int type = chooseType();
        if (type == 1) {
            int cntOfPlayers = chooseCntOfPlayers();
            playerList = choosePlayers(cntOfPlayers);
            Tournament tournament = new Tournament(playerList);
            tournament.setBoard(boardType);
            tournament.start();
            System.out.println(tournament.getPrizeWinners());
        } else {
            playerList = choosePlayers(2);
            Player player1 = playerList.getFirst();
            Player player2 = playerList.getLast();
            Board board;
            Parameters params = scanParams.scanParameters();
            m = params.m();
            n = params.n();
            k = params.k();
            if (boardType == 1) {
                board = new MNKBoard(m, n, k);
            } else {
                board = new MNKBoardRhombus(m, n, k);
            }
            MNKGame game = new MNKGame(board, player1, player2, m, n, new Scanner(System.in), System.out);
            printResult(game.play());
        }
    }

    private static int chooseType() {
        System.out.println("Choose Type of Game\n1-Tournament\n2-single");
        return scanParams.scanInt(2);
    }

    private static int chooseBoard() {
        System.out.println("Choose Board\n1-square\n2-rhombus");
        return scanParams.scanInt(2);
    }

    private static List<Player> choosePlayers(int cntOfPlayers) {
        List<Player> players = new ArrayList<>();
        for (int i = 0; i < cntOfPlayers; i++) {
            System.out.println("Choose Player №" + (i + 1) + "\n1-HumanPlayer\n2-RandomPlayer");
            if (scanParams.scanInt(2) == 1) {
                players.add(new HumanPlayer());
            } else {
                players.add(new RandomPlayer());
            }
        }
        return players;
    }

    private static int chooseCntOfPlayers() {
        System.out.println("Choose count of players:");
        return scanParams.scanInt(16);
    }
}
