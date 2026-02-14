package expression.generic;

import expression.exceptions.errors.ArithmeticalException;

import java.math.BigInteger;

public class BigIntegerOperation implements GenericOperation<BigInteger> {
    @Override
    public BigInteger add(BigInteger x, BigInteger y) {
        return x.add(y);
    }

    @Override
    public BigInteger subtract(BigInteger x, BigInteger y) {
        return x.subtract(y);
    }

    @Override
    public BigInteger multiply(BigInteger x, BigInteger y) {
        return x.multiply(y);
    }

    @Override
    public BigInteger divide(BigInteger x, BigInteger y) {
        if (y.equals(BigInteger.ZERO)) {
            throw new ArithmeticalException("Division by zero");
        }
        return x.divide(y);
    }

    @Override
    public BigInteger negate(BigInteger x) {
        return x.negate();
    }

    @Override
    public BigInteger parseNumber(String number) {
        return new BigInteger(number);
    }

    @Override
    public BigInteger valueOf(int value) {
        return BigInteger.valueOf(value);
    }
}
