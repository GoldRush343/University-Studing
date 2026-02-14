package markup;

import java.util.List;

public class ListItem {
    String open = "\\item ";
    List<TexElement> list;
    public ListItem(List<TexElement> list) {
        this.list = list;
    }

    public void toTex(StringBuilder stringBuilder){
        stringBuilder.append(open);
        for (TexElement element: list){
            element.toTex(stringBuilder);
        }
    }
}
