import java.io.IOException;
import java.util.Arrays;
import java.util.function.Predicate;

public class ReverseSum {
    private static boolean isWhiteSpace_(char c) {
        return Character.isWhitespace(c) || Character.getType(c) == Character.END_PUNCTUATION || Character.getType(c) == Character.START_PUNCTUATION;
    }

    public static void main(String[] args) {
        int size = 0;
        int maxRow = 0;
        DynamicArray matrix = new DynamicArray();
        Predicate<Character> predicate = ReverseSum::isWhiteSpace_;
        MyScanner.changePredicate(predicate);

        // записываем ввод в matrix
        //Scanner scanner1 = new Scanner(System.in);
        try {
            MyScanner scanner1 = new MyScanner(System.in);
            try {
                while (scanner1.hasNextLine()) {
                    int curCountOfRow = 0;
                    MyScanner scanner2 = new MyScanner(scanner1.nextLine());
                    DynamicArray row = new DynamicArray();
                    while (scanner2.hasNextInt()) {
                        row.add(scanner2.nextInt());
                        curCountOfRow++;
                    }
                    scanner2.close();
                    matrix.add(row);// добавляем row в matrix
                    maxRow = Math.max(maxRow, curCountOfRow);
                    size++;
                }
            } finally {
                scanner1.close();
            }
        } catch (IOException e){
            System.out.println("IO Error: " + e.getMessage());
        }

        int[] rowSums = new int[size];
        int[] columnSums = new int[maxRow];

        // заполняем rowSums columnSums
        Arrays.fill(rowSums, 0);
        Arrays.fill(columnSums, 0);
        for (int i = 0; i < size; i++) {
            DynamicArray tmp = (DynamicArray) matrix.get(i);
            for (int j = 0; j < tmp.size(); j++) {
                rowSums[i] += (int) tmp.get(j);
                columnSums[j] += (int) tmp.get(j);
            }
        }

        //output
        for (int i = 0; i < size; i++) {
            DynamicArray tmp = (DynamicArray) matrix.get(i);
            for (int j = 0; j < tmp.size(); j++) {
                int curNum = (int) tmp.get(j);
                int result = rowSums[i] + columnSums[j] - curNum;
                System.out.print(result + " ");
            }
            System.out.println();
        }
    }
}

