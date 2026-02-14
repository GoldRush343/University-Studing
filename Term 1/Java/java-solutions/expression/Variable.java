package expression;

import java.util.InputMismatchException;
import java.util.Objects;

public class Variable implements SuperExpression {
    private final String var;

    public Variable(String var) {
        this.var = var;
    }

    public String getVariable() {
        return var;
    }

    @Override
    public int evaluate(int num) {
        return num;
    }

    @Override
    public int evaluate(int x, int y, int z) {
        return switch (var) {
            case "x" -> x;
            case "y" -> y;
            case "z" -> z;
            default -> throw new InputMismatchException("Variable should be x, y, z. Yours: " + var);
        };
    }

    @Override
    public long evaluateL(long num1, long num2, long num3) {
        return switch (var) {
            case "x" -> num1;
            case "y" -> num2;
            case "z" -> num3;
            default -> throw new InputMismatchException("Variable should be x, y, z. Yours: " + var);
        };
    }

    @Override
    public String toString() {
        return var;
    }

    @Override
    public boolean equals(Object object) {
        if (object == null || object.getClass() != Variable.class) {
            return false;
        }
        Variable tmp = (Variable) object;
        return Objects.equals(var, tmp.var);
    }

    @Override
    public int hashCode() {
        return Objects.hash(var);
    }
}
