package expression.exceptions;

import expression.*;
import expression.exceptions.errors.MissSymbol;
import expression.parser.CharSource;

import java.util.List;
import java.util.Map;

public class ExpressionParserProxyWE extends expression.parser.ExpressionParserProxy {
    public ExpressionParserProxyWE(CharSource source) {
        super(source);
        setOperations(Map.of(
                1, List.of("-"),
                2, List.of("**", "//"),
                3, List.of("*", "/"),
                4, List.of("+", "-"),
                5, List.of(">>>", ">>", "<<")
        ));
    }

    @Override
    protected BinaryOperation getOperation(String operation, SuperExpression left, SuperExpression right) throws MissSymbol {
        return switch (operation) {
            case "+" -> new CheckedAdd(left, right);
            case "-" -> new CheckedSubtract(left, right);
            case "*" -> new CheckedMultiply(left, right);
            case "/" -> new CheckedDivide(left, right);
            case "**" -> new CheckedPow(left, right);
            case "//" -> new CheckedLog(left, right);
            default -> throw new MissSymbol("Unknown Binary operation: " + operation);
        };
    }

    @Override
    protected UnaryOperation getUnaryOperation(String operation, SuperExpression value) throws MissSymbol {
        return switch (operation) {
            case "-" -> new CheckedNegate(value);
            default -> throw new MissSymbol("Unknown Unary operation: " + operation);
        };
    }
}
