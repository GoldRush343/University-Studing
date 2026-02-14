package expression;

public class ArithmeticalShift extends BinaryOperation{
    public ArithmeticalShift(SuperExpression first, SuperExpression second) {
        super(first, second);
    }

    @Override
    protected String operation() {
        return ">>>";
    }

    @Override
    protected int solve(int one, int two) {
        return one >>> two;
    }

    @Override
    protected long solveL(long one, long two) {
        return one >>> two;
    }
}
