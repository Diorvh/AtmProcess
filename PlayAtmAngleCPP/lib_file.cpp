#include <filesystem>
using namespace std;

void createFolder(const std::string& chineseFolderPath) {
    try {
        // Convert Chinese path to UTF-16 encoding
        std::wstring wideFolderPath;
        wideFolderPath.resize(MultiByteToWideChar(CP_UTF8, 0, chineseFolderPath.c_str(), -1, nullptr, 0));
        MultiByteToWideChar(CP_UTF8, 0, chineseFolderPath.c_str(), -1, &wideFolderPath[0], static_cast<int>(wideFolderPath.size()));

        // Check if the folder exists
        if (GetFileAttributesW(wideFolderPath.c_str()) == INVALID_FILE_ATTRIBUTES) {
            // If the folder doesn't exist, create it
            if (!CreateDirectoryW(wideFolderPath.c_str(), NULL)) {
                throw std::runtime_error("Error creating folder: " + std::to_string(GetLastError()));
            }
            std::wcout << L"Folder created successfully: " << wideFolderPath << std::endl;
        }
        else {
            std::wcout << L"Folder already exists: " << wideFolderPath << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error creating folder: " << e.what() << std::endl;
    }
}
std::string extractLastPathComponent(const std::string& path) {//读入一个文件路径字符串，只保留最后一个//后的内容
    // Find the last occurrence of '\\' in the path
    size_t lastBackslashPos = path.find_last_of("//");

    // Check if the character was found
    if (lastBackslashPos != std::string::npos) {
        // Extract the substring after the last '\\' character
        return path.substr(lastBackslashPos + 1);
    } else {
        // If '\\' is not found, return the entire string
        return path;
    }
}
std::string getFolderPath(const std::string& filePath) {
    // 使用C++17中引入的std::filesystem
    std::filesystem::path fullPath(filePath);

    // 获取文件所在文件夹的路径
    std::filesystem::path folderPath = fullPath.parent_path();

    // 将路径转换为字符串
    std::string folderPathString = folderPath.string();

    return folderPathString;
}
