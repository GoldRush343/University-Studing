package expression.exceptions;

import expression.BinaryOperation;
import expression.SuperExpression;
import expression.TripleExpression;
import expression.exceptions.errors.ConstantOverflow;
import expression.exceptions.errors.DivisionByZero;

public class CheckedDivide extends BinaryOperation implements TripleExpression {
    public CheckedDivide(SuperExpression vx, SuperExpression vy) {
        super(vx, vy);
    }

    @Override
    protected String operation() {
        return "/";
    }

    @Override
    protected int solve(int one, int two) throws DivisionByZero, ConstantOverflow {
        if (two == 0) {
            throw new DivisionByZero("You can't divide by zero! You lose!");
        }
        if (one == Integer.MIN_VALUE && two == -1){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " can't fit in int!");
        }
        return one / two;
    }

    @Override
    protected long solveL(long one, long two) throws DivisionByZero {
        if (two == 0) {
            throw new DivisionByZero("You can't divide by zero! You lose!");
        }
        if (one == Long.MIN_VALUE && two == -1){
            throw new ConstantOverflow("Overflow, because " + one + " - " + two + " can't fit in int!");
        }
        return one / two;
    }
}
