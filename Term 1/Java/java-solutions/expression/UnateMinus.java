package expression;

public class UnateMinus extends UnaryOperation{
    public UnateMinus(SuperExpression elem) {
        super(elem);
    }

    @Override
    protected int solve(int x) {
        return -x;
    }

    @Override
    protected long solveL(long x) {
        return -x;
    }

    @Override
    protected String operation() {
        return "-";
    }
}
