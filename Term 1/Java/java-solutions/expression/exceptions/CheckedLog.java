package expression.exceptions;

import expression.BinaryOperation;
import expression.SuperExpression;
import expression.exceptions.errors.IllegalNumber;

public class CheckedLog extends BinaryOperation {
    protected CheckedLog(SuperExpression first, SuperExpression second) {
        super(first, second);
    }

    @Override
    protected String operation() {
        return "//";
    }

    @Override
    protected int solve(int one, int two) {
        if (two <= 0 || two == 1) {
            throw new IllegalNumber("Base must be greater than 1!");
        }
        if (one <= 0) {
            throw new IllegalNumber("Argument must be positive!");
        }
        int result = 0;
        while(one >= two){
            one /= two;
            result++;
        }
        return result;
    }
    @Override
    protected long solveL(long one, long two) {
        if (two <= 0 || two == 1) {
            throw new IllegalNumber("Base must be greater than 1!");
        }
        if (one <= 0) {
            throw new IllegalNumber("Argument must be positive!");
        }
        int result = 0;
        while(one >= two){
            one /= two;
            result++;
        }
        return result;
    }
}
