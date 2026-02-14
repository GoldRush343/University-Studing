import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.function.Predicate;

public class MyScanner {
    //final
    private final BufferedReader reader;
    private final char[] buffer;
    //private final StringBuilder left = new StringBuilder();

    //iterate
    private int bufSize = -1;
    private int bufPos = -1;
    private boolean isClosed = false;
    private String curElement;
    private boolean isElementFound = false;

    //final static
    private static Predicate<Character> predicate = Character::isWhitespace;
    //private static Predicate<Character> predicate;
    private static final int BUFFER_SIZE = 1024;

    //WsppPosition
    private int cntOfSkippedLines = 0;

    //Constructors
    public MyScanner(InputStream input) throws IOException {
        this.reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8));
        buffer = new char[BUFFER_SIZE];
        read();
    }

    public MyScanner(String input) throws IOException {
        //input += '\n';
        byte[] byreArr = input.getBytes(StandardCharsets.UTF_8);
        this.reader = new BufferedReader(new InputStreamReader(new ByteArrayInputStream(byreArr)));
        buffer = new char[BUFFER_SIZE];
        read();
    }

    private boolean read() {
        if (isClosed) {
            return false;
        }
        try {
            bufPos = 0;
            bufSize = reader.read(buffer);
            if (bufSize == -1) { //read ended
                close();
                return false;
            }
            return true;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

//    private void delete() {
//        if (!left.isEmpty()){
//            left.delete(0, left.length());
//            isElementFound = false;
//        }
//    }

    public boolean isEndOfLine(char c) {
        if (c == '\r') {
            if (hasNextChar()) {
                char next = buffer[bufPos];
                if (next == '\n') {
                    bufPos++;
                }
            }
            return true;
        }
        return c == '\n';
    }

    private static boolean isWhiteSpace_(char c) {
        return predicate.test(c);
    }

    private boolean isInt(String str) {
        try {
            Integer.parseInt(str);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    //methods to read
    private void skipWhitespace() {
        char curChar;
        while (hasNextChar()) { //skipping whitespaces
            curChar = nextChar();
            if (isEndOfLine(curChar)){
                cntOfSkippedLines++;
            }
            if (!isWhiteSpace_(curChar)) {//found not whitespace
                bufPos--;
                break;
            }
            //left.append(curChar);
        }
    }

    private String collectElem() {
        StringBuilder elem = new StringBuilder(); //there no whitespaces
        char curChar;
        while (hasNextChar()) { //collecting elem
            curChar = nextChar();
            if (isWhiteSpace_(curChar)) {
                bufPos--;
                break;
            }
            //left.append(curChar);
            elem.append(curChar);
        }
        return elem.toString();
    }

    private void findElement() {
        if (isElementFound) {
            return;
        }
        skipWhitespace();
        isElementFound = true;
        curElement = collectElem();
    }

    //public methods
    public static void changePredicate(Predicate<Character> newPredicate){
        predicate = newPredicate;
    }

    //hasNextChar nextChar
    public boolean hasNextChar() {
        return bufPos < bufSize || read();
    }

    public char nextChar() {
        if (!hasNextChar()) {
            throw new NoSuchElementException("Line not found");
        }
        return buffer[bufPos++];
    }

    //hasNextLine nextLine
    public boolean hasNextLine() {
        return hasNextChar();
    }

    public String nextLine() {
        StringBuilder line = new StringBuilder();
        char curChar;
        while (hasNextChar()) {
            curChar = nextChar();
            if (isEndOfLine(curChar)) {
                break;
            }
            line.append(curChar);
        }
        //delete();
        return line.toString();
    }

    //hasNext next nextWithCntLines
    public boolean hasNext() {
        findElement();
        return !curElement.isEmpty();
    }

    public String next() {
        if (!hasNext()) { // word not fount
            throw new NoSuchElementException("word not fount");
        }
        //delete();
        isElementFound = false;
        return curElement;
    }

    public static class Current {
        private final String current;
        private final int lineNumber;

        public Current(String current, int lineNumber) {
            this.current = current;
            this.lineNumber = lineNumber;
        }

        public String getCurrent() {
            return current;
        }

        public int getLineNumber() {
            return lineNumber;
        }
    }

    public Current nextWithCntLines(){
        if (!hasNext()) { // word not fount
            throw new NoSuchElementException("word not fount");
        }
        //delete();
        isElementFound = false;
        return new Current(curElement, cntOfSkippedLines);
    }

    //hasInt nextInt
    public boolean hasNextInt() {
        findElement();
        return isInt(curElement);
    }

    public int nextInt() {
        if (!hasNextInt()) {
            throw new NoSuchElementException("int not fount");
        }
        //delete();
        isElementFound = false;
        return Integer.parseInt(curElement);
    }

    public void close() throws IOException {
        if (!isClosed) {
            reader.close();
            isClosed = true;
        }
    }
}
