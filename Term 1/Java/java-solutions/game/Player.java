package game;

public interface Player {
    Move makeMove(PositionProxy position);
    void setTurn(Cell cell);
}
