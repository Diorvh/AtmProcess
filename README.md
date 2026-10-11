# AtmProcess

`AtmProcess` 是独立的科研图像处理程序，提供液膜尺寸与破碎长度测量、平均图、灰度转换、火焰锥角和雾化锥角处理。

当前定位为 Windows 科研桌面程序。论文配套发布前的已确认问题、复现要求与实施顺序见 [科研发布准备方案](docs/RESEARCH_RELEASE_PLAN_CN.md)。现有迁移检查不等同于算法的科学有效性验证。

## 运行

在本目录安装依赖并启动：

```powershell
python -m pip install -r requirements.txt
python main.py
```

也可以在上一级目录运行：

```powershell
python -m AtmProcess.main
```

## 功能说明

- 雾化锥角单帧预览和批量处理共用同一套 NumPy 向量化算法。
- 批量处理使用 Python 多进程，无需额外的计算程序或通信文件。
- 雾化、火焰、平均图和彩色转灰度批处理会实时显示完成数量和百分比。
- 批量结果仍输出原有格式的 Excel，并继续更新实验汇总表。
- 写入 Excel 前会仅保存并关闭同一路径的已打开工作簿；写入后自动重新打开结果表和汇总表，不影响其他工作簿。
- 播放支持暂停、帧率设置和四张灰度曲线同步刷新；帧范围及抽帧间隔统一控制处理的图像集合。
- `settings.json` 位于程序目录内，保存实验参数、路径和界面状态；移动整个 `AtmProcess` 文件夹后仍能恢复配置。

## 目录

- `domain/`：实验上下文和参数数据模型。
- `application/`：应用状态和 GUI 操作入口。
- `ui/`：Tkinter 页面与共享图像预览。
- `services/`：批处理、测量和 Excel 导出流程。
- `algorithms/`：图像计算算法。
- `core/`：图像、Excel、配置和并行等基础工具。
- `lib/`：插值、滤波和频域计算等数值函数。
- `sample_data/`：用于测试的少量雾化图像。
- `tests/`：独立导入、启动入口和多进程迁移检查。
- `docs/ARCHITECTURE_CN.md`：详细中文架构说明。

样例的文件清单和 SHA-256 校验值见 [样例说明](sample_data/README.md)。

## 配置与版本管理

`settings.json` 是本机运行配置，保留在磁盘上，但不提交到 Git。没有该文件时程序使用默认参数，关闭时自动保存。`settings.example.json` 提供不含本机路径的配置示例。

Git 跟踪程序代码、依赖清单、文档、测试和小型样例图像；忽略 Python 缓存、虚拟环境和本机配置。复制整个目录会携带本机配置，而仅克隆 Git 仓库不会携带已忽略的文件。

## 迁移检查

在本目录运行：

```powershell
python -B -m unittest discover -s tests -p test_independence.py
```

检查使用样例图像，不打开 GUI 或 Excel，也不修改实验数据。
