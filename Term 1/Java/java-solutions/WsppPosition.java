import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class WsppPosition {
    private final LinkedHashMap<String, Stats> map = new LinkedHashMap<>();

    public static class Stats {
        int count = 0;
        IntList intros = new IntList();
        IntList cntLines = new IntList();

        public void add(int pos, int cntLine) {
            intros.add(pos);
            cntLines.add(cntLine);
            count++;
        }
    }

    private static boolean isWhiteSpace_(char c) {
        return !(Character.isLetter(c) || c == '\'' || Character.getType(c) == Character.DASH_PUNCTUATION
                || c == '$' || c == '_' || Character.isDigit(c));
    }

    public void addWord(String word, int pos, int cntLine) {
        Stats stat = map.get(word);
        if (stat == null) {
            stat = new Stats();
            map.put(word, stat);
        }
        stat.add(pos, cntLine + 1);
    }

    public static String print(int cnt, IntList intros, IntList cntLines) {
        StringBuilder res = new StringBuilder();
        for (int i = 0; i < intros.size(); i++) {
            int newIntro = cnt - (int) intros.get(i) + 1;
            res.append(cntLines.get(i)).append(":").append(newIntro).append(" ");
        }
        return res.substring(0, res.length() - 1);
    }

    public static void main(String[] args) {
        WsppPosition wsppPosition = new WsppPosition();
        Predicate<Character> predicate = WsppPosition::isWhiteSpace_;
        MyScanner.changePredicate(predicate);
        try {
            int cnt = 0;
            int cntLine = 1;
            MyScanner scanner = new MyScanner(new FileInputStream(args[0]));
            try {
//                StringBuilder word = new StringBuilder();
//                while (scanner.hasNextChar()) { // :NOTE: чтение по символам
//                    char cur = scanner.nextChar();
//                    if (isWordChar(cur)) {
//                        word.append(cur);
//                    } else if (!word.isEmpty()) {
//                        cnt++;
//                        wsppPosition.addWord(word.toString().toLowerCase(), cnt, cntLine);
//                        word.delete(0, word.length());
//                    }
//                    if (scanner.isEndOfLine(cur)) {
//                        cntLine++;
//                    }
//                }
                while (scanner.hasNext()) {
                    var objectList = scanner.nextWithCntLines();// another next with cntLine
                    String word = objectList.getCurrent();
                    cntLine = objectList.getLineNumber();
                    cnt++;
                    wsppPosition.addWord(word.toLowerCase(), cnt, cntLine);
                }
            } finally {
                scanner.close();
            }

            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(
                    new FileOutputStream(args[1]), StandardCharsets.UTF_8));
            try {
                LinkedHashMap<String, Stats> sortedMap = wsppPosition.map.entrySet().stream()
                        .sorted(Comparator.comparingInt(entry -> entry.getKey().length()))
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                Map.Entry::getValue,
                                (e1, e2) -> e1,
                                LinkedHashMap::new
                        ));
                for (var elem : sortedMap.sequencedEntrySet()) {
                    String word = elem.getKey();
                    Stats stat = elem.getValue();
                    writer.write(word + " " + stat.count + " " + print(cnt, stat.intros, stat.cntLines) + '\n');
                }
            } finally {
                writer.close();
            }
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + e.getMessage());
        } catch (IOException e) {
            // :NOTE: не понятная ошибка
            System.err.println("IO error: " + e.getMessage());
        }
    }
}
