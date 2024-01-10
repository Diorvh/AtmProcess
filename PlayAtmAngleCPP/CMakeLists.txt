cmake_minimum_required(VERSION 3.2.0)
project(opencvtest)

find_package(OpenCV REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)

message("===========${OpenCV_INCLUDE_DIRS}")
message("========${OpenCV_LIBS}")

target_include_directories(${PROJECT_NAME} PRIVATE ${OpenCV_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})