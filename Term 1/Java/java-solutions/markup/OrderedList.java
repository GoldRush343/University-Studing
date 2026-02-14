package markup;

import java.util.List;

public class OrderedList extends ListOfTexElements{
    public OrderedList(List<ListItem> list){
        super(list);
        openToTex = "\\begin{enumerate}";
        closeToTex = "\\end{enumerate}";
    }
}
