#include <iostream>
#include <fstream>
#include <string>

int main() {
    // Open the .txt file
    std::fstream file("inputpy.txt", std::ios::in | std::ios::out | std::ios::ate);

    if (!file.is_open()) {
        std::cerr << "Error opening the file!" << std::endl;
        return 1;
    }

    // Move the file pointer to the beginning of the last line
    file.seekg(-1, std::ios::end);

    // Find the beginning of the last line
    while (file.tellg() > 0 && file.peek() != '\n') {
        file.seekg(-1, std::ios::cur);
    }

    // Save the position of the beginning of the last line
    std::streampos lastLineBegin = file.tellg();

    // Read the last line into a string
    std::string lastLine;
    getline(file, lastLine);

    // Move the file pointer back to the beginning of the last line
    file.seekp(lastLineBegin);

    // Output a new string to the last line
    std::string newString = "This is the new last line.";
    file << newString << std::endl;

    // Close the file
    file.close();

    std::cout << "File updated successfully." << std::endl;

    return 0;
}
