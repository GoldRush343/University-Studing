package expression.exceptions;

import expression.BinaryOperation;
import expression.Const;
import expression.SuperExpression;
import expression.exceptions.errors.CalculationException;
import expression.exceptions.errors.ConstantOverflow;

public class CheckedPow extends BinaryOperation {
    protected CheckedPow(SuperExpression first, SuperExpression second) {
        super(first, second);
    }

    @Override
    protected String operation() {
        return "**";
    }

    private int fastPow(int one, int two) {
        SuperExpression tmp = new CheckedLog(new Const(Integer.MAX_VALUE), new Const(one));
        if (two > tmp.evaluate(-1)) {
            throw new ConstantOverflow("Overflow, because " + one + " ** " + two + " can't fit in int!");
        } else if (two % 2 == 0) {
            int half = solve(one, two / 2);
            return half * half;
        } else {
            return one * solve(one, two - 1);
        }
    }

    @Override
    protected int solve(int one, int two) {
        if (one == 0 && two == 0) {
            throw new CalculationException("Undefined expression detected: 0 ** 0!");
        } else if (two < 0) {
            throw new CalculationException("Undefined expression detected: a ** b: b < 0!");
        }
        if (two == 0 || one == 1) {
            return 1;
        } else if (two == 1) {
            return one;
        } else if (one == 0) {
            return 0;
        } else if (one == -1) {
            return (two % 2 == 0) ? 1 : -1;
        }
        if (one > 0) {
            return fastPow(one, two);
        } else {
            return (two % 2 == 0) ? fastPow(-one, two) : -fastPow(-one, two);
        }
    }

    @Override
    protected long solveL(long one, long two) {
        throw new UnsupportedOperationException("This method not available for longs!");
    }
}
