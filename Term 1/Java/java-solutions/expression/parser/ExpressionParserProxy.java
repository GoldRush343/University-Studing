package expression.parser;

import expression.*;
import expression.exceptions.errors.*;

import java.util.List;
import java.util.Map;

public class ExpressionParserProxy extends BaseParser {
    private static Map<Integer, List<String>> operations = Map.of(
            1, List.of("-"),
            2, List.of("*", "/"),
            3, List.of("+", "-"),
            4, List.of(">>>", ">>", "<<")
    );

    protected static void setOperations(Map<Integer, List<String>> operations1) {
        operations = operations1;
    }

    protected BinaryOperation getOperation(String operation, SuperExpression left, SuperExpression right) throws MissSymbol {
        return switch (operation) {
            case "+" -> new Add(left, right);
            case "-" -> new Subtract(left, right);
            case "*" -> new Multiply(left, right);
            case "/" -> new Divide(left, right);
            case ">>>" -> new ArithmeticalShift(left, right);
            case ">>" -> new ShiftR(left, right);
            case "<<" -> new ShiftL(left, right);
            default -> throw new MissSymbol("Unknown Binary operation: " + operation);
        };
    }

    protected UnaryOperation getUnaryOperation(String operation, SuperExpression value) throws MissSymbol {
        return switch (operation) {
            case "-" -> new UnateMinus(value);
            default -> throw new MissSymbol("Unknown Unary operation: " + operation);
        };
    }

    public ExpressionParserProxy(CharSource source) {
        super(source);
    }

    //SIMPLE THINGS:
    private void skipWS() {
        while (Character.isWhitespace(getCh())) {
            take();
        }
    }

    private SuperExpression parseNumber(String pref) throws ConstantOverflow {
        StringBuilder sb = new StringBuilder(pref);
        while (between('0', '9')) {
            sb.append(take());
        }
        try {
            return new Const(Integer.parseInt(sb.toString()));
        } catch (NumberFormatException e) {
            throw new ConstantOverflow("Invalid number!");
        }
    }

    //RECURSION PARSE
    public TripleExpression parse() throws ParseException {
        SuperExpression result = parsePriority(operations.size());
        skipWS();
        if (!checkEOF()) {
            throw new ExtraSymbol("Unexpected symbol in end!");
        }
        return result;
    }

    private SuperExpression parsePriority(int priority) throws ParseException {
        if (priority == 1) {
            return parsePriorityOne();
        }
        SuperExpression result = parsePriority(priority - 1);
        skipWS();
        while (true) {
            String op = takePriority(priority);
            if (op.equals("-1")) {
                break;
            }
            SuperExpression right = parsePriority(priority - 1);
            result = getOperation(op, result, right);
            skipWS();
        }
        return result;
    }

    private String takePriority(int priority) {
        List<String> opers = operations.get(priority);
        for (String oper : opers) {
            if (take(oper)) {
                return oper;
            }
        }
        return "-1";
    }

    private SuperExpression parsePriorityOne() throws ParseException {
        skipWS();
        if (take('-')) {
            if (between('0', '9')) {
                return parseNumber("-");
            } else {
                return getUnaryOperation("-", parsePriorityOne());
            }
        }
        return parseElement();
    }

    private SuperExpression parseElement() throws ParseException {
        skipWS();
        if (take('(')) {
            SuperExpression result = parsePriority(operations.size());
            skipWS();
            expect(')');
            return result;
        }
        if (between('0', '9')) {
            return parseNumber("");
        } else if (test('x') || test('y') || test('z')) {
            return new Variable(String.valueOf(take()));
        }
        throw new MissSymbol("Argument missing!");
    }
}
