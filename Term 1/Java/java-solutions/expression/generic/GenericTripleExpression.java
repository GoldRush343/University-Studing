package expression.generic;

import expression.SuperExpression;

public interface GenericTripleExpression <T> extends SuperExpression {
    T evaluateGeneric(T x, T y, T z);
}
