#include <string>

class Buffer {
public:
    void append(const std::string& s) { data_ += s; }
    int size() const { return data_.size(); }
private:
    std::string data_;
};

int add(int a, int b) {
    return a + b;
}
