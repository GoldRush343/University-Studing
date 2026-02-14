package expression.parser;

import expression.exceptions.errors.WrongSymbol;

public class BaseParser {
    protected CharSource source;
    private char ch;
    public static final char END = (char) -1;


    public BaseParser(CharSource source) {
        this.source = source;
        take();
    }

    protected boolean test(char c) {
        return ch == c;
    }

    protected boolean test(String s) {
        if (!source.hasNext(s.length())) {
            return false;
        }
        for (int i = 0; i < s.length(); i++) {
            if (source.getChAt(i) != s.charAt(i)) {
                return false;
            }
        }
        return true;
    }

    protected char take() {
        char res = ch;
        ch = source.hasNext() ? source.next() : END;
        return res;
    }

    protected boolean take(char c) {
        if (test(c)) {
            take();
            return true;
        }
        return false;
    }
    protected boolean take(String s){
        if (test(s)){
            for(int i = 0; i < s.length(); i++){
                take();
            }
            return true;
        }
        return false;
    }

    protected char getCh() {
        return ch;
    }

    protected boolean checkEOF() {
        return ch == END;
    }

    protected void expect(char c) throws WrongSymbol {
        if (!take(c)) {
            throw new WrongSymbol("Expected: " + c + " , but found: " + ch);
        }
    }

    protected void expect(String s) throws WrongSymbol {
        for (char c : s.toCharArray()) {
            expect(c);
        }
    }

    protected boolean between(char start, char end) {
        return start <= ch && ch <= end;
    }
}
