#include <iostream>
#include <string>
#include <vector>
#include <windows.h>

void removeFolder(const std::string& folderPath) {
    try {
        // Initialize SHFILEOPSTRUCT
        SHFILEOPSTRUCTA fileOp;  // Use SHFILEOPSTRUCTA for ANSI version
        ZeroMemory(&fileOp, sizeof(fileOp));
        fileOp.wFunc = FO_DELETE;

        // Ensure double null-termination
        std::string folderPathWithDoubleNull = folderPath + '\0';

        // Allocate a buffer for double null-termination
        std::vector<char> buffer(folderPathWithDoubleNull.begin(), folderPathWithDoubleNull.end());

        // Use directly as LPCSTR
        fileOp.pFrom = buffer.data();

        // Remove the folder and its contents
        if (SHFileOperationA(&fileOp) != 0) {
            throw std::runtime_error("Error removing folder: " + std::to_string(GetLastError()));
        }

        std::cout << "Folder removed successfully: " << folderPath << std::endl;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }
}

int main() {
    // Folder path, including Chinese characters
    std::string folderPath = "E:\\实验数据\\雾化锥角\\20230416\\实验编号81\\处理结果";

    // Remove the folder and its contents
    removeFolder(folderPath);

    return 0;
}
