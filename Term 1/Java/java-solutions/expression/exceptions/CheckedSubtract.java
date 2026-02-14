package expression.exceptions;

import expression.BinaryOperation;
import expression.SuperExpression;
import expression.TripleExpression;
import expression.Variable;
import expression.exceptions.errors.ConstantOverflow;

public class CheckedSubtract extends BinaryOperation implements TripleExpression {
    public CheckedSubtract(SuperExpression vx, SuperExpression vy) {
        super(vx, vy);
    }

    @Override
    protected String operation() {
        return "-";
    }

    @Override
    protected int solve(int one, int two) throws ConstantOverflow {
        if (two < 0 && one > Integer.MAX_VALUE + two){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " can't fit in int!");
        }
        if (two > 0 && one < Integer.MIN_VALUE + two){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " is too low to fit in int!");
        }
        return one - two;
    }

    @Override
    protected long solveL(long one, long two) throws ConstantOverflow {
        if (two < 0 && one > Long.MAX_VALUE + two){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " can't fit in int!");
        }
        if (two > 0 && one < Long.MIN_VALUE + two){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " is too low to fit in int!");
        }
        return one - two;
    }
}
