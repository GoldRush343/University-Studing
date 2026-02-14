package expression;

public class Add extends BinaryOperation {
    public Add(SuperExpression first, SuperExpression second) {
        super(first, second);
    }

    @Override
    protected String operation() {
        return "+";
    }

    @Override
    protected int solve(int one, int two) {
        return one + two;
    }

    @Override
    protected long solveL(long one, long two) {
        return one + two;
    }
}
