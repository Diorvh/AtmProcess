def split_list(file_names, x):
    total_files = len(file_names)
    avg_files_per_chunk = total_files // x
    remaining_files = total_files % x

    chunks = []
    start_index = 0

    for i in range(x):
        chunk_size = avg_files_per_chunk + (1 if i < remaining_files else 0)
        chunks.append(file_names[start_index:start_index + chunk_size])
        start_index += chunk_size

    return chunks
if __name__ == '__main__':
    # 示例文件名列表
    file_names = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt", "file6.txt", "file7.txt", "file8.txt"]

    # 将文件名列表分成 3 份
    x = 3
    result = split_list(file_names, x)

    # 打印结果
    for i, chunk in enumerate(result):
        print(f"Chunk {i+1}: {chunk}")
