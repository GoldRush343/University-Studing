package expression.parser;

public class StringSource implements CharSource {
    private final String string;
    private int pos;

    public StringSource(String string) {
        this.string = string;
    }

    @Override
    public boolean hasNext() {
        return pos < string.length();
    }

    @Override
    public boolean hasNext(int length) {
        if (length < 0) {
            return false;
        }
        return pos + length <= string.length();
    }

    @Override
    public char getChAt(int shift) {
        return string.charAt(pos + shift - 1);
    }

    @Override
    public char next() {
        return string.charAt(pos++);
    }

    @Override
    public IllegalArgumentException error(String message) {
        return new IllegalArgumentException(pos + ":" + message);
    }
}
