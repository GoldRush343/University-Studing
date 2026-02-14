package markup;

import java.util.List;

public class UnorderedList extends ListOfTexElements{
    public UnorderedList (List<ListItem> list){
        super(list);
        openToTex = "\\begin{itemize}";
        closeToTex = "\\end{itemize}";
    }
}
