package markup;

import java.util.List;

public class Paragraph implements TexElement{
    List<MarkupElement> body;
    String open = "\\par{}";
    public Paragraph(List<MarkupElement> body) {
        this.body = body;
    }

    public void toMarkdown(StringBuilder stringBuilder) {
        for (MarkupElement element: body){
            element.toMarkdown(stringBuilder);
        }
    }

    public void toTex(StringBuilder stringBuilder){
        stringBuilder.append(open);
        for (MarkupElement element: body){
            element.toTex(stringBuilder);
        }
    }
}
