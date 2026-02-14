package tictactoe;

public class CheaterPlayer implements Player {


    @Override
    public Move makeMove(Position position) {
        Board board = (Board) position;
        board.makeMove(new Move(1, 1, position.getTurn()));
        board.makeMove(new Move(1, 2, position.getTurn()));
        board.makeMove(new Move(2, 2, position.getTurn()));
        board.makeMove(new Move(2, 1, position.getTurn()));

        return new Move(3, 3, position.getTurn());
//        return null;
    }
}
