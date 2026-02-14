package game;

public interface Board {
    Result makeMove(Move move);

    int getN();

    int getM();

    Cell[][] getField();

    PositionProxy getPos();

    void clear();
}
