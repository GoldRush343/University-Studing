package expression.exceptions;

import expression.*;
import expression.exceptions.errors.*;
import expression.parser.BaseParser;
import expression.parser.StringSource;

public class ExpressionParser extends BaseParser implements TripleParser {
    public ExpressionParser() {
        super(new StringSource(""));
    }

    @Override
    public TripleExpression parse(String expression) throws ParseException {
        ExpressionParserProxyWE parserProxy = new ExpressionParserProxyWE(new StringSource(expression));
        return parserProxy.parse();
    }
}
