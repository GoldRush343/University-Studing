public class SumLongOctal {
    public static void main(String[] args) {
        long answer = 0;
//        boolean isWordBegin = true;
        int start = 0;
        for (int argIndex = 0; argIndex < args.length; argIndex++) { // going for strs
            for (int i = 0; i < args[argIndex].length(); i++) { // char c in
                char c = args[argIndex].charAt(i);
                boolean isEndOfString = (i == args[argIndex].length() - 1);
                if (!Character.isWhitespace(c) && isEndOfString) {
                    answer += parseOctal(args[argIndex].substring(start, i + 1));
                } else if (Character.isWhitespace(c)) {
                    if (start < i) {
                        answer += parseOctal(args[argIndex].substring(start, i));
                    }
                    start = i + 1;
                }
            }
        }
        System.out.println(answer);
    }

    private static long parseOctal(String s) {
        if (s.endsWith("o") || s.endsWith("O")) {
            return Long.parseUnsignedLong(s.substring(0, s.length() - 1), 8);
        } else {
            return Long.parseLong(s);
        }
    }
//    private static long parseOctal2(String s) {
//        if ((s.endsWith("o") || s.endsWith("O")) && s.startsWith("-")) {
//            return -Long.parseUnsignedLong(s.substring(1, s.length() - 1), 8);
//        } else if (s.endsWith("o") || s.endsWith("O")) {
//            return Long.parseUnsignedLong(s.substring(0, s.length() - 1), 8);
//        } else if (s.startsWith("-")){
//            return -Long.parseUnsignedLong(s.substring(1));
//        } else {
//            return Long.parseUnsignedLong(s);
//        }
//    }
}