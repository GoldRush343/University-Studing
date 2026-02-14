package markup;

import java.util.List;

public class Strong extends AbstractMarkupElement {
    public Strong(List<MarkupElement> body) {
        super(body);
        openTexMark = "\\textbf{";
        closeTexMark = "}";
        markdownSymbol = "__";
    }
}
