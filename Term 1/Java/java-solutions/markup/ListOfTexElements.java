package markup;

import java.util.List;

public class ListOfTexElements implements TexElement{
    private List<ListItem> list;
    String openToTex = "";
    String closeToTex = "";

    public ListOfTexElements( List<ListItem> list){
        this.list = list;
    }

    public void toTex(StringBuilder stringBuilder){
        stringBuilder.append(openToTex);
        for (ListItem peace: list){
            peace.toTex(stringBuilder);
        }
        stringBuilder.append(closeToTex);
    }
}
