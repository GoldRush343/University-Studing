package expression.exceptions;

import expression.BinaryOperation;
import expression.SuperExpression;
import expression.TripleExpression;
import expression.exceptions.errors.ConstantOverflow;
import expression.exceptions.errors.DivisionByZero;

public class CheckedMultiply extends BinaryOperation implements TripleExpression {
    public CheckedMultiply(SuperExpression vx, SuperExpression vy) {
        super(vx, vy);
    }

    @Override
    protected String operation() {
        return "*";
    }

    @Override
    protected int solve(int one, int two) throws DivisionByZero {
        if (two > 0 && one > 0 && one > Integer.MAX_VALUE / two ||
                one < 0 && two < 0 && one < Integer.MAX_VALUE / two) {
            throw new ConstantOverflow("Overflow, because " + one + " * " + two + " can't fit in int!");
        }
        if (two < 0  && one > 0 && two < Integer.MIN_VALUE / one ||
                two > 0 && one < 0 && one < Integer.MIN_VALUE / two) {
            throw new ConstantOverflow("Overflow, because " + one + " * " + two + " is too low to fit in int!");
        }
        return one * two;
    }

    @Override
    protected long solveL(long one, long two) throws DivisionByZero {
        if (two > 0 && one > 0 && one > Long.MAX_VALUE / two ||
                one < 0 && two < 0 && one < Long.MAX_VALUE / two) {
            throw new ConstantOverflow("Overflow, because " + one + " * " + two + " can't fit in int!");
        }
        if (two < 0  && one > 0 && two < Long.MIN_VALUE / one ||
                two > 0 && one < 0 && one < Long.MIN_VALUE / two) {
            throw new ConstantOverflow("Overflow, because " + one + " * " + two + " is too low to fit in int!");
        }
        return one * two;
    }
}
