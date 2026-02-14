package expression.generic;

public class CheckedIntOperation implements GenericOperation<Integer> {
    @Override
    public Integer add(Integer x, Integer y) {
        return Math.addExact(x, y);
    }

    @Override
    public Integer subtract(Integer x, Integer y) {
        return Math.subtractExact(x, y);
    }

    @Override
    public Integer multiply(Integer x, Integer y) {
        return Math.multiplyExact(x, y);
    }

    @Override
    public Integer divide(Integer x, Integer y) {
        if (y == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return Math.divideExact(x, y); // divideExact нужен для Integer.MIN_VALUE / -1
    }

    @Override
    public Integer negate(Integer x) {
        return Math.negateExact(x);
    }

    @Override
    public Integer parseNumber(String number) {
        return Integer.parseInt(number);
    }

    @Override
    public Integer valueOf(int value) {
        return value;
    }
}