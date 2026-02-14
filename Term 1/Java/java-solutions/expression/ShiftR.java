package expression;

public class ShiftR extends BinaryOperation{
    public ShiftR(SuperExpression first, SuperExpression second) {
        super(first, second);
    }

    @Override
    protected String operation() {
        return ">>";
    }

    @Override
    protected int solve(int one, int two) {
        return one >> two;
    }

    @Override
    protected long solveL(long one, long two) {
        return one >> two;
    }
}
