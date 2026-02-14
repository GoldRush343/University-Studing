package expression.generic;

public class GenericParser <T>{
    private final GenericOperation<T> operation;

    public GenericOperation(GenericOperation<T> op){
        this.operation = op;
    }
}
