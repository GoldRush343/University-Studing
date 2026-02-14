package markup;

import java.util.List;

public class Strikeout extends AbstractMarkupElement {
    public Strikeout(List<MarkupElement> body){
        super(body);
        openTexMark = "\\textst{";
        closeTexMark = "}";
        markdownSymbol = "~";
    }
}
