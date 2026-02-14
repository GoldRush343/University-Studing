package markup;

public class Text implements MarkupElement {
    private String text;
    public Text(String text) {
        this.text = text;
    }
    public Text(StringBuilder stringBuilder){
        this.text = stringBuilder.toString();
    }
    @Override
    public void toMarkdown(StringBuilder stringBuilder){
        stringBuilder.append(text);
    }
    @Override
    public void toTex(StringBuilder stringBuilder) {
        stringBuilder.append(text);
    }
}