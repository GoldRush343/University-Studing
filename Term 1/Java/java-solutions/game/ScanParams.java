package game;

import java.io.PrintStream;
import java.util.Scanner;

public class ScanParams {
    private final Scanner in;
    private final PrintStream out;
    private final String inputError;

    public ScanParams(Scanner in, PrintStream out, String inputError){
        this.in = in;
        this.out = out;
        this.inputError = inputError;
    }
    public ScanParams(String inputError){
        this(new Scanner(System.in),System.out,inputError);
    }
    public ScanParams(){
        this(new Scanner(System.in),System.out,"Input Error!");
    }

    public int scanInt(int range) {
        int type = scanNum();
        while(!(0 < type && type <= range)){
            type = scanNum();
            System.out.println("Wrong input! Try again!");
        }
        return type;
    }

    public int scanNum() {
        while (!in.hasNextInt()) {
            in.nextLine();
            inputMistake();
        }
        return in.nextInt();
    }

    private void inputMistake(){
        out.println(inputError);
    }

    public Parameters scanParameters() {
        out.print("Введите m, n, k: ");
        Parameters params;
        params = new Parameters(scanNum(), scanNum(), scanNum());
        if (isInvalid(params.m(), params.n(), params.k())){
            do{
                inputMistake();
                params = new Parameters(scanNum(), scanNum(), scanNum());
            }while(isInvalid(params.m(), params.n(), params.k()));
        }
        return params;
    }

    private boolean isInvalid(int m, int n, int k) {
        if (m < 1 || n < 1 || k < 1) {
            return true;
        }
        if (m > 1000 || n > 1000) {
            return true;
        }
        if (k > m + n - 1) {
            return true;
        }
        return false;
    }
}
