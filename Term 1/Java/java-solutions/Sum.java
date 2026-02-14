public class Sum {
    public static void main(String[] args) {
        int answer = 0;
        boolean isWordBegin = true;
        int start = 0;
        for (int argIndex = 0; argIndex < args.length; argIndex++) {
            for (int i = 0; i < args[argIndex].length(); i++) {
                boolean isEndOfString = (i == args[argIndex].length() - 1);
                char c = args[argIndex].charAt(i);
                if (!Character.isWhitespace(c) && isWordBegin){
                    start = i;
                    isWordBegin = false;
                    if (isEndOfString) {
                        answer += Integer.parseInt(args[argIndex].substring(start, i + 1));
                        isWordBegin = true;
                    }
                } else if (!Character.isWhitespace(c) && isEndOfString) {
                    answer += Integer.parseInt(args[argIndex].substring(start, i + 1));
                    isWordBegin = true;
                } else if (!isWordBegin && Character.isWhitespace(c)) {
                    answer += Integer.parseInt(args[argIndex].substring(start, i));
                    isWordBegin = true;
                }
            }
        }
        System.out.println(answer);
    }
}
