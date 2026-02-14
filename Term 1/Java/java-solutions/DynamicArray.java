class DynamicArray {
    private int size;
    private int capasity;
    private Object[] array;

    public DynamicArray() {
        capasity = 5;
        array = new Object[capasity];
        size = 0;
    }

    public void add(Object value) {
        if (this.size == this.capasity) {
            resize();
        }
        array[size] = value;
        size++;
    }

    public void resize() {
        this.capasity = (int) (this.capasity * 1.5);//1.5 working faster than 2
        Object[] newArray = new Object[capasity];
        System.arraycopy(this.array, 0, newArray, 0, size);
        this.array = newArray;
    }

    public Object get(int index) {
        return this.array[index];
    }

    public int size() {
        return this.size;
    }
}
