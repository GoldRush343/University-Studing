package expression;

import java.util.Objects;

public class Const implements SuperExpression {
    private final long value;

    public Const(int value) {
        this.value = value;
    }

    public Const(long value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return Long.toString(value);
    }

    @Override
    public int evaluate(int num) {
        return (int) this.value;
    }

    @Override
    public int evaluate(int num1, int num2, int num3) {
        return (int) this.value;
    }

    @Override
    public long evaluateL(long num1, long num2, long num3) {
        return this.value;
    }

    @Override
    public boolean equals(Object object) {
        if (object == null || object.getClass() != Const.class) {
            return false;
        }
        Const tmp = (Const) object;
        return Objects.equals(value, tmp.value);
    }

    @Override
    public int hashCode() {
        return Integer.hashCode((int) value);
    }
}
