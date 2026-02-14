package markup;

import java.util.List;

public class Emphasis extends AbstractMarkupElement {
    public Emphasis(List<MarkupElement> body){
        super(body);
        openTexMark = "\\emph{";
        closeTexMark = "}";
        markdownSymbol = "*";
    }
}
