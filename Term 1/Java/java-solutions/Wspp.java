import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.function.Predicate;

public class Wspp {
    private final LinkedHashMap<String, Stats> map = new LinkedHashMap<>();

    private  static boolean isWhiteSpace_(char c){
        return !(Character.isLetter(c) || c == '\'' || Character.getType(c) == Character.DASH_PUNCTUATION);
    }

    private static class Stats {
        int count = 0;
        IntList intros = new IntList();

        public void add(int pos) {
            intros.add(pos);
            count++;
        }
    }

    private void addWord(String word, int pos) {
        Stats stat = map.get(word);
        if (stat == null) {
            stat = new Stats();
            map.put(word, stat);
        }
        stat.add(pos);
    }

    public static void main(String[] args) {
        Wspp wspp = new Wspp();
        try {
            int cnt = 0;
            Predicate<Character> WSPP_PREDICATE = Wspp::isWhiteSpace_;
            MyScanner.changePredicate(WSPP_PREDICATE);
            MyScanner scanner = new MyScanner(new FileInputStream(args[0]));
            try {
                while (scanner.hasNext()) {
                    cnt++;
                    wspp.addWord(scanner.next().toLowerCase(), cnt);
                }
//                StringBuilder word = new StringBuilder();
//                while (scanner.hasNextChar()) {
//                    char cur = scanner.nextChar();
//                    if (isWordChar(cur)) {
//                        word.append(cur);
//                    } else if (!word.isEmpty()) {
//                        cnt++;
//                        wspp.addWord(word.toString().toLowerCase(), cnt);
//                        word.delete(0, word.length());
//                    }
//                }
            } finally {
                scanner.close();
            }

            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(
                    new FileOutputStream(args[1]), StandardCharsets.UTF_8));
            try {
                for (var elem : wspp.map.sequencedEntrySet()) {
                    String word = elem.getKey();
                    Stats stat = elem.getValue();
                    writer.write(word + " " + stat.count + " " + IntList.printIntList(stat.intros) + '\n');
                }
            } finally {
                writer.close();
            }
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + e.getMessage());
        } catch (IOException e) {
            System.err.println("IO error: " + e.getMessage());
        }
    }
}
