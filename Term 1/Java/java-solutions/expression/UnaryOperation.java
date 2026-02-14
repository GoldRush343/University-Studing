package expression;

import java.util.Objects;

public abstract class UnaryOperation implements SuperExpression {
    private final SuperExpression elem;

    public UnaryOperation(SuperExpression elem) {
        this.elem = elem;
    }

    protected abstract int solve(int x);

    protected abstract long solveL(long x);

    protected abstract String operation();

    @Override
    public int evaluate(int x) {
        return solve(elem.evaluate(x));
    }

    @Override
    public long evaluateL(long x, long y, long z) {
        return solveL(elem.evaluateL(x, y, z));
    }

    @Override
    public int evaluate(int x, int y, int z) {
        return solve(elem.evaluate(x, y, z));
    }

    @Override
    public String toString() {
        return operation() + "(" + elem.toString() + ")";
    }

    @Override
    public boolean equals(Object object) {
        if (object == null || object.getClass() != this.getClass()) {
            return false;
        }
        UnaryOperation tmp = (UnaryOperation) object;
        return operation().equals(tmp.operation()) && elem.equals(tmp.elem);
    }

    @Override
    public int hashCode() {
        return Objects.hash(operation(), elem, getClass());
    }
}
