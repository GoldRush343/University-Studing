package expression.parser;

import expression.*;
import expression.exceptions.errors.ArithmeticalException;
import expression.exceptions.errors.ParseException;

public class ExpressionParser extends BaseParser implements TripleParser {
    public ExpressionParser() {
        super(new StringSource(""));
    }

    @Override
    public SuperExpression parse(String expression) {
        ExpressionParserProxy parserProxy = new ExpressionParserProxy(new StringSource(expression));
        try{
            return (SuperExpression) parserProxy.parse();
        } catch (ArithmeticalException e){
            System.err.println("Arithmetical error! You lose!");
        } catch (ParseException e) {
            System.err.println("Parse error! You lose!");
        }
        return null;
    }
}
