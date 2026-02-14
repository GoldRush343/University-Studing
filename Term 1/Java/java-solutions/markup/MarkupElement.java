package markup;

public interface MarkupElement {
    void toMarkdown(StringBuilder stringBuilder);
    void toTex(StringBuilder stringBuilder);
}
