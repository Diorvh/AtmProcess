[English README](README_EN.md)

# AtmProcess 使用说明

当前发布版本：**V1.0**。

AtmProcess 是用于互击式喷嘴雾化燃烧实验图像处理的 Windows 图像处理程序，支持液膜尺寸与破碎长度测量、平均图、彩色转灰度、火焰锥角和雾化锥角处理。界面可切换中文和英文。

程序附带编号29的20张雾化图像、提取参数和演示汇总表。第一次使用可以直接调参、计算和导出，不必先准备自己的实验数据。样例仅演示操作流程，不代表完整实验或论文全部结果的复现。

## 0. 对应论文

1. （破碎长度）费立涵，张玉园，尤冠文，汤成龙，黄佐华，张锋. 高环境压力下撞击射流雾化实验研究[C]//2023年中国工程热物理学会燃烧学学术年会. 2023-05.（墙报交流）
2. （火焰锥角）FEI L H, ZHANG F, TANG C L, XU T G, YANG A L, YANG B E, HUANG Z H. An experimental investigation on MMH/NTO impinging jets flame characteristics at high chamber pressure[J]. Proceedings of the Combustion Institute, 2024, 40(1-4): 105709. DOI: [10.1016/j.proci.2024.105709](https://doi.org/10.1016/j.proci.2024.105709).
3. （雾化锥角）FEI L H, LI Y, TANG C L, HUANG Z H, YANG A L. New observation of unsteady jets impingement caused by nozzle cavitation at varying ambient gas pressures[J]. Experimental Thermal and Fluid Science, 2026, 178: 111811. DOI: [10.1016/j.expthermflusci.2026.111811](https://doi.org/10.1016/j.expthermflusci.2026.111811).
4. （破碎长度、雾化锥角）费立涵，李源，汤成龙，黄佐华. 高环境气体密度下撞击式喷嘴雾化特性实验研究[J]. 推进技术（在投）.

## 1. 下载与准备

1. 下载仓库 ZIP 并**完整解压**到可写的本地文件夹，不要在压缩包内直接运行。文件夹可以保留 `AtmProcess-main` 等名称。
2. 安装64位 Python 3.10或更高正式版，包含 pip 和 Tcl/Tk。安装程序及说明见 [Python Windows 下载页](https://www.python.org/downloads/windows/)。确保 `py` 启动器或 `python` 命令可用。
3. 配置依赖时需要网络连接。结果表自动打开需要系统已关联 `.xlsx` 文件的应用；若需自动保存、关闭已打开的目标工作簿，需使用桌面版 Microsoft Excel。

依赖清单见 [requirements.txt](requirements.txt)。

## 2. 一键配置与启动

**首次使用：双击 `setup_env.bat`。** 脚本在当前程序目录创建 `.venv`，安装所需依赖。看到 `Setup complete` 后关闭该窗口。

**日常使用：双击 `start.bat`。** 启动脚本始终使用本目录的 `.venv`，不用手动激活环境或输入命令。正常退出程序后，启动窗口会关闭；出错时保留错误信息。

项目环境与其他 Python 项目的依赖隔离，不修改全局依赖。配置失败时可根据提示处理后重新运行 `setup_env.bat`。有关独立环境的机制见 [Python venv 说明](https://docs.python.org/3/library/venv.html)。

已经有可用 Python 环境的用户，也可以在程序目录手动运行：

```powershell
python -m pip install -r requirements.txt
python main.py
```

## 3. 先运行雾化锥角样例

### 单张调参

1. 首次打开时，程序进入“雾化锥角”页面，实验编号为29，帧范围为8000–8019。
2. 右侧显示当前图像，左侧显示提取参数、锥角结果及四张面积加权灰度曲线。
3. 修改参数后**按回车**，提交数值并重新计算。仅在输入框中打字不会触发延迟计算。
4. 用“当前帧”后的 `-`、`+` 切换图像；也可以设置播放帧率并点击播放。计算速度会限制实际播放速度。
5. 预览中的计算区域、锥角线等开关可以同时勾选。颜色反转、显示二值化只是显示选项，不改变计算参数。

### 批量处理与汇总

1. 默认帧范围覆盖全部20张样例，抽帧间隔为1。
2. 点击“批量处理雾化锥角”，等待进度完成。
3. 程序导出逐帧结果、统计量及频域数据，并把提取参数、角度平均值和标准差写入演示汇总表中**编号为29的记录**。

默认输出位置：

| 内容 | 程序目录下的路径 |
| --- | --- |
| 批量结果 | `sample_data/results/实验编号29_雾化锥角批处理结果.xlsx` |
| 演示汇总表 | `sample_data/results/atomization_summary.xlsx` |
| 预览图 | `sample_data/results/preview/` |

四张灰度曲线也可分别导出 Excel 数据，使用雾化页面中的结果目录。预览图使用右侧设置的保存目录和文件名。


## 4. 处理自己的数据

1. 选择“数据根目录”，例如该目录下包含 `实验编号29`、`实验编号30` 等子文件夹，图像名称使用可识别的帧编号。也可使用界面提供的直接图像来源选择。
2. 输入实验编号并按回车，确认图像来源、帧范围和当前帧。
3. 设置抽帧间隔。例如从202开始、间隔为2，处理集合为202、204、206……；切帧按钮和批量任务均遵守该集合。
4. 切换到需要的功能页，设置标定和处理参数，先检查单张图像效果，再执行批量操作。
5. 为自己的实验选择独立的结果目录和汇总表，不要继续把演示表当作真实实验的汇总表。

自己的汇总表可参考演示表布局：第一行保留程序识别的字段标题，工况行使用唯一实验编号。可在雾化页面点击读取参数按钮，从所选汇总表恢复当前实验的提取参数。

频域计算使用页面输入的图像帧率。应填写**参与处理的图像序列的采样频率**；若先做了抽帧，需要自行填写对应的有效频率，程序不会再自动除以抽帧间隔。

## 5. 其他功能

| 页面 | 基本用途 |
| --- | --- |
| 液膜测量 | 在液膜尺寸和破碎长度两种模式中选择一种，点击预览设置边界，实时显示结果，记录逐帧数据并导出 Excel；也可读取已导出的记录。 |
| 平均图 | 按所选帧集合生成平均图，或将彩色图批量转换为灰度图。 |
| 火焰锥角 | 查看单帧效果、调整参数并批量提取火焰锥角。 |
| 雾化锥角 | 单帧调参、灰度曲线检查、批量提取和汇总表读写。 |

液膜测量切换实验编号或图像来源时会清空当前记录表，请先导出需要保留的数据。平均图、灰度转换等操作可能生成或覆盖输出图像，首次处理自己的数据前应保留原图备份。

## 许可证与引用

程序代码及使用文档采用 [MIT License](LICENSE)，版权署名为 Lihan Fei（费立涵）。随仓库提供的样例图像、来源元数据和演示汇总表模板单独采用 [CC BY 4.0](sample_data/LICENSE)；具体范围和署名方式见 [样例说明](sample_data/README.md#scope-and-reuse)。

## 详细文档

- [中文详细文档：架构、计算与导出流程](docs/ARCHITECTURE_CN.md)
- [English documentation: architecture, computation and export](docs/ARCHITECTURE_EN.md)
