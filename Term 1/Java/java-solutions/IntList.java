public class IntList {
    private int size;
    private int capasity;
    private int[] array;

    public IntList() {
        capasity = 5;
        array = new int[capasity];
        size = 0;
    }

    public IntList(int count) {
        capasity = (int) (count * 1.5);
        array = new int[capasity];
        size = count;
    }

    public void add(int value) {
        if (this.size == this.capasity) {
            resize();
        }
        array[size] = value;
        size++;
    }

    private void resize() {
        this.capasity = (int) (this.capasity * 1.7);//1.7 working faster than 2
        int[] newArray = new int[capasity];
        System.arraycopy(this.array, 0, newArray, 0, size);
        this.array = newArray;
    }

    public Object get(int index) {
        return this.array[index];
    }

    public int size() {
        return this.size;
    }

    public static String printIntList(IntList intList) {
        StringBuilder res = new StringBuilder();
        for (int i = 0; i < intList.size; i++) {
            res.append(intList.get(i)).append(" ");
        }
        return res.substring(0, res.length() - 1);
    }
}
