package markup;

import java.util.List;

public abstract class AbstractMarkupElement implements MarkupElement {
    protected List<MarkupElement> body;
    protected String markdownSymbol = "";
    protected String openTexMark = "";
    protected String closeTexMark = "";

    public AbstractMarkupElement(List<MarkupElement> body){
        this.body = body;
    }

    @Override
    public void toMarkdown(StringBuilder stringBuilder){
        stringBuilder.append(markdownSymbol);
        for (MarkupElement peace: body){
            peace.toMarkdown(stringBuilder);
        }
        stringBuilder.append(markdownSymbol);
    }

    @Override
    public void toTex(StringBuilder stringBuilder) {
        stringBuilder.append(openTexMark);
        for (MarkupElement peace: body){
            peace.toTex(stringBuilder);
        }
        stringBuilder.append(closeTexMark);
    }
}
