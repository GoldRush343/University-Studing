package game;

import java.io.PrintStream;
import java.util.ArrayList;

import java.util.*;

public class Tournament {
    private final HashMap<Integer, Player> players;
    private final Scanner in;
    private final PrintStream out;
    private final List<Integer> leavePlayers;
    private int championId;
    private int boardType;
    private ScanParams scanParams = new ScanParams("Can't create game with this m, n, k. Try again!");

    public Tournament(List<Player> players, Scanner in, PrintStream out) {
        this.in = in;
        this.out = out;
        this.leavePlayers = new ArrayList<>();
        this.players = new HashMap<>();
        for (int i = 0; i < players.size(); i++) {
            this.players.put(i + 1, players.get(i));
        }
    }

    public Tournament(List<Player> players) {
        this(players, new Scanner(System.in), System.out);
    }

    public void start() {
        List<Integer> playerIds = new ArrayList<>(players.keySet());
        Collections.shuffle(playerIds);
        championId = playWinners(playerIds);
        playerIds = new ArrayList<>(players.keySet());
        playerIds.remove(championId - 1);
        out.println("LOSERS!");
        playLosers(playerIds);
    }

    private void printVS(Integer playerId1, Integer playerId2) {
        out.println("Player №" + playerId1 + " vs " + "Player №" + playerId2);
    }

    private void playRound(List<Integer> currentPlayers, boolean isWinners) {
        int playerId1 = currentPlayers.removeLast();
        int playerId2 = currentPlayers.removeLast();
        Player player1 = players.get(playerId1);
        Player player2 = players.get(playerId2);
        Parameters params = scanParams.scanParameters();
        Board board;
        if (boardType == 1) {
            board = new MNKBoard(params.m(), params.n(), params.k());
        } else {
            board = new MNKBoardRhombus(params.m(), params.n(), params.k());
        }
        player1.setTurn(Cell.X);
        player2.setTurn(Cell.O);
        MNKGame game = new MNKGame(board, player1, player2, params.m(), params.n(), new Scanner(System.in), System.out);
        printVS(playerId1, playerId2);
        int result = game.play();
        printResult(result);
        while (result == 0) {
            out.println("Play until no winner!");
            board.clear();
            result = game.play();
            printResult(result);
        }
        if (result == 1) {
            currentPlayers.addFirst(playerId1);
            if (!isWinners){
                leavePlayers.add(playerId2);
            }
        } else if (result == 2) {
            currentPlayers.addFirst(playerId2);
            if (!isWinners){
                leavePlayers.add(playerId1);
            }
        }
    }

    private int playWinners(List<Integer> currentPlayers) {
        while (currentPlayers.size() > 1) {
            playRound(currentPlayers, true);
        }
        return currentPlayers.removeLast();
    }

    private void playLosers(List<Integer> currentPlayers) {
        while (currentPlayers.size() > 1) {
            playRound(currentPlayers, false);
        }
        if (!leavePlayers.isEmpty()){
            leavePlayers.add(currentPlayers.removeLast());
        }
    }

    public ArrayList<Integer> getPrizeWinners() {
        ArrayList<Integer> prizeWinners = new ArrayList<>();
        prizeWinners.add(championId);
        for (int i = 0; i < 2; i++) {
            try{
                int playerId = leavePlayers.get(leavePlayers.size() - i - 1);
                prizeWinners.add(playerId);
            } catch (RuntimeException e){
                return prizeWinners;
            }
        }
        return prizeWinners;
    }

    private static void printResult(int result) {
        if (result == 1) {
            System.out.println("First win");
        } else if (result == 2) {
            System.out.println("Second win");
        } else {
            System.out.println("Draw");
        }
    }

    public void setBoard(int boardType) {
        this.boardType = boardType;
    }
}