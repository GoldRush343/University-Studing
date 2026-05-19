#include <iostream>

class Matrix{
public:
    Matrix(std::size_t rows, std::size_t cols) 
    : _rows(rows)
    , _cols(cols)
    , _data(new int[rows * cols]{}){}

    ~Matrix() {
        delete[] _data;
    }

    Matrix(const Matrix& other) 
    : _rows(){

    }

    std::size_t rows(){
        return _rows;
    }

private:
    std::size_t _rows;
    std::size_t _cols;
    int *_data;

};

int main() {
    Matrix m(10, 10);
    std::cout << "Hello";
}