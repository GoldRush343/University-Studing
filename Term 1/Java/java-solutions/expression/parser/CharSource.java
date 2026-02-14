package expression.parser;

public interface CharSource {
    boolean hasNext();
    boolean hasNext(int length);
    char getChAt(int shift);
    char next();
    IllegalArgumentException error(String message);
}
