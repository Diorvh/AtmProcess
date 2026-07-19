# ImageProcess v3

`ImageProcessv3` 是独立的科研图像处理程序，不依赖旧 GUI、v2 文件或外部可执行程序。

## 运行

从 `ImageProcess` 目录运行：

```powershell
python -m ImageProcessv3.main
```

也可以直接运行：

```powershell
python ImageProcessv3\main.py
```

依赖安装：

```powershell
python -m pip install -r ImageProcessv3\requirements.txt
```

## 主要变化

- 雾化锥角单帧预览和批量处理共用同一套 NumPy 向量化算法。
- 批量处理使用 Python 多进程，不再需要 EXE、DLL、文本通信或中间 CSV。
- 雾化、火焰、平均图和彩色转灰度批处理会实时显示完成数量和百分比。
- 批量结果仍输出原有格式的 Excel，并继续更新实验汇总表。
- 写入 Excel 前会仅保存并关闭同一路径的已打开工作簿；写入后自动重新打开结果表和汇总表，不影响其他工作簿。
- `settings_v3.json` 位于 v3 目录内，移动整个文件夹后仍能独立保存和恢复配置。

## 目录

- `domain/`：实验上下文和参数数据模型。
- `application/`：应用状态和 GUI 操作入口。
- `ui/`：Tkinter 页面与共享图像预览。
- `services/`：批处理、测量和 Excel 导出流程。
- `algorithms/`：图像计算算法。
- `core/`：图像、Excel、配置和并行等基础工具。
- `lib/`：插值、滤波和频域计算等数值函数。
- `sample_data/`：用于测试的少量雾化图像。
- `docs/ARCHITECTURE_CN.md`：详细中文架构说明。
