import java.io.IOException;
import java.util.function.Predicate;

public class Reverse {
    private static boolean isWhiteSpace_(char c) {
        return Character.isWhitespace(c) || Character.getType(c) == Character.END_PUNCTUATION || Character.getType(c) == Character.START_PUNCTUATION;
    }

    public static void main(String[] args) {
        int size = 0;
        DynamicArray matrix = new DynamicArray();
        Predicate<Character> predicate = Reverse::isWhiteSpace_;
        MyScanner.changePredicate(predicate);

        try{
            MyScanner scanner1 = new MyScanner(System.in);
            //Scanner scanner1 = new Scanner(System.in);
            try{
                while (scanner1.hasNextLine()) {
                    MyScanner scanner2 = new MyScanner(scanner1.nextLine());
                    //Scanner scanner2 = new Scanner(scanner1.nextLine());
                    DynamicArray row = new DynamicArray();
                    while (scanner2.hasNextInt()) {
                        int tmp = scanner2.nextInt();
                        row.add(tmp);
                    }
                    scanner2.close();
                    matrix.add(row);// добавляем row в matrix
                    size++;
                }
            }finally {
                scanner1.close();
            }
        } catch (IOException e){
            System.err.println("IO error" + e.getMessage());
        }

        for (int i = size - 1; i > -1; i--) {
            DynamicArray row = (DynamicArray) matrix.get(i);
            for (int j = row.size() - 1; j > -1; j--) {
                System.out.print(row.get(j));
                System.out.print(" ");
            }
            System.out.print("\n");
        }
    }
}