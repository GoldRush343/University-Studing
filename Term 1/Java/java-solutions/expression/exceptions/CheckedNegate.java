package expression.exceptions;

import expression.SuperExpression;
import expression.TripleExpression;
import expression.UnaryOperation;
import expression.exceptions.errors.ConstantOverflow;

public class CheckedNegate extends UnaryOperation implements TripleExpression {
    public CheckedNegate(SuperExpression vy) {
        super(vy);
    }

    @Override
    protected int solve(int x) {
        if (x == Integer.MIN_VALUE) {
            throw new ConstantOverflow("Overflow, because -" + x + " is too low to fit in int!");
        }
        return -x;
    }

    @Override
    protected long solveL(long x) {
        if (x == Long.MIN_VALUE) {
            throw new ConstantOverflow("Overflow, because -" + x + " is too low to fit in int!");
        }
        return -x;
    }

    @Override
    protected String operation() {
        return "-";
    }
}
