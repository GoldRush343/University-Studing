package expression;


import java.util.InputMismatchException;
import java.util.Objects;

public abstract class BinaryOperation implements SuperExpression {
    private final SuperExpression first;
    private final SuperExpression second;

    protected abstract String operation();

    protected BinaryOperation(SuperExpression first, SuperExpression second) {
        this.first = first;
        this.second = second;
    }

    protected abstract int solve(int one, int two);

    protected abstract long solveL(long one, long two);

    public Expression getFirst() {
        return first;
    }

    public Expression getSecond() {
        return second;
    }

    @Override
    public int evaluate(int num) {
        return solve(first.evaluate(num), second.evaluate(num));
    }

    @Override
    public int evaluate(int num1, int num2, int num3) {
        return solve(first.evaluate(num1, num2, num3), second.evaluate(num1, num2, num3));
    }

    @Override
    public long evaluateL(long num1, long num2, long num3) {
        return solveL(first.evaluateL(num1, num2, num3), second.evaluateL(num1, num2, num3));
    }

    @Override
    public String toString() {
        return "(" + first.toString() + " " + operation() + " " + second.toString() + ")";
    }

    @Override
    public boolean equals(Object object) {
        if (object == null || object.getClass() != this.getClass()) {
            return false;
        }
        BinaryOperation tmp = (BinaryOperation) object;
        return operation().equals(tmp.operation()) && first.equals(tmp.first) && second.equals(tmp.second);
    }

    @Override
    public int hashCode() {
        return Objects.hash(first, second, operation());
    }
}
