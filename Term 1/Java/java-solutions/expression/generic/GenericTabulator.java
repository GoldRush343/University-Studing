package expression.generic;

import expression.TripleExpression;
import expression.exceptions.ExpressionParser;
import expression.exceptions.errors.ArithmeticalException;

import java.util.Map;

public class GenericTabulator implements Tabulator {
    private final Map<String, GenericOperation<?>> modes = Map.of(
            "i", new CheckedIntOperation(),
            "d", new DoubleOperation(),
            "bi", new BigIntegerOperation()
    );

    @Override
    public Object[][][] tabulate(String mode, String expression, int x1, int x2, int y1, int y2, int z1, int z2) throws Exception {
        GenericOperation<?> operation = modes.get(mode);
        if (operation == null) {
            throw new IllegalArgumentException("Unsupported mode: " + mode);
        }
        return makeTable(operation, expression, x1, x2, y1, y2, z1, z2);
    }

    private <T> Object[][][] makeTable(GenericOperation<T> op, String expression, int x1, int x2, int y1, int y2, int z1, int z2) throws Exception {
        int xSize = x2 - x1 + 1;
        int ySize = y2 - y1 + 1;
        int zSize = z2 - z1 + 1;

        Object[][][] result = new Object[xSize][ySize][zSize];

        // ВАЖНО: ExpressionParser должен быть дженериком и принимать операцию
        // Либо ваш парсер должен возвращать структуру, которая использует переданную операцию.
        // Пример использования:
        ExpressionParser<T> parser = new ExpressionParser<>(op);
        GenericTripleExpression<T> expr = parser.parse(expression);

        for (int i = 0; i < xSize; i++) {
            for (int j = 0; j < ySize; j++) {
                for (int k = 0; k < zSize; k++) {
                    T x = op.valueOf(x1 + i);
                    T y = op.valueOf(y1 + j);
                    T z = op.valueOf(z1 + k);

                    try {
                        result[i][j][k] = expr.evaluate(x, y, z);
                    } catch (ArithmeticalException e) {
                        result[i][j][k] = null;
                    }
                }
            }
        }
        return result;
    }
}
