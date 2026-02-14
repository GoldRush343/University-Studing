import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.function.Predicate;

public class WordStat {
    private static boolean isWhiteSpace_(char c) {
        return !(Character.isLetter(c) || c == '\'' || Character.getType(c) == Character.DASH_PUNCTUATION);
    }

    private static int lowerOrUpperBound(String[] arr, String val, boolean isLower) {
        int l = -1, r = arr.length;
        while (r - l > 1) {
            int mid = (r + l) / 2;
            if (isLower ? arr[mid].compareTo(val) < 0 : arr[mid].compareTo(val) <= 0) {
                l = mid;
            } else {
                r = mid;
            }
        }
        return r;
    }

    public static void main(String[] args) {
        String[] input = new String[0];
        //DynamicArray dynamicArray = new DynamicArray();
        Predicate<Character> predicate = WordStat::isWhiteSpace_;
        MyScanner.changePredicate(predicate);

        try {
            MyScanner scanner = new MyScanner(new FileInputStream(args[0]));
            try {
                int size = 0;
                int count;
//                StringBuilder word = new StringBuilder();
//                while (scanner.hasNextChar()) {
//                    for (int i = 0; i <= count; i++) {
//                        if (i < count && isWordChar(buffer[i])) { // is in White list
//                            word.append(buffer[i]);
//                        } else if (i == count) {
//                            break;
//                        } else if (!word.isEmpty()) { // is word end
//                            if (size == input.length) {
//                                input = Arrays.copyOf(input, input.length * 2 + 1);
//                            }
//                            input[size++] = word.substring(0, word.length()).toLowerCase();
//                            word.delete(0, word.length());
//                        }
//                    }
//                }

                while (scanner.hasNext()){
                    String word = scanner.next();
                    if (size == input.length) {
                        input = Arrays.copyOf(input, input.length * 2 + 1);
                    }
                    input[size++] = word.toLowerCase();
                }
                input = Arrays.copyOf(input, size);

                boolean[] isPrintedI = new boolean[size];
                String[] sortedInput = new String[size];
                System.arraycopy(input, 0, sortedInput, 0, size);
                Arrays.sort(sortedInput);
                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream(args[1]), StandardCharsets.UTF_8));
                try {
                    for (int i = 0; i < size; i++) {
                        String cur = input[i];
                        int low = lowerOrUpperBound(sortedInput, cur, true);
                        int up = lowerOrUpperBound(sortedInput, cur, false);
                        if (!isPrintedI[low]) {
                            writer.write(cur + ' ');
                            writer.write((up - low) + "\n");
                            isPrintedI[low] = true;
                        }
                    }
                } finally {
                    writer.close();
                }
            } finally {
                scanner.close();
            }
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + e.getMessage());
        } catch (IOException e) {
            System.err.println("IO error: " + e.getMessage());
        }
    }
}