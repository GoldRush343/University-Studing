package expression;

import game.ScanParams;

public class Main {
    public static void main(String[] args) {
        ScanParams scanParams = new ScanParams("Wrong input, try again!");
        int x = scanParams.scanNum();
        Expression expression = new Add(
                new Subtract(
                        new Multiply(new Variable("x"), new Variable("x")),
                        new Multiply(new Const(2), new Variable("x"))
                ),
                new Const(1)
        );
        System.out.println(expression + " = " + expression.evaluate(x));
    }
}
