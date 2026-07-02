# ImageProcess 架构说明书

## 1. 项目定位

`ImageProcess` 是一个用于冲击射流实验图像处理的 Tkinter 桌面程序。程序围绕实验图像序列提供多个处理功能：

- 液膜尺寸测量
- 破碎长度测量
- 火焰锥角测量与批处理
- 平均图生成与图像预处理
- 雾化锥角预览与 C++ 加速批处理

诱导长度功能已经删除，当前程序不再包含 `CalcInductionLength` 功能页和相关后端。

项目当前处在“兼容式重构”阶段：旧的 Tkinter 页面仍保留，新的 `core`、`algorithms`、`services` 分层已经引入，并逐步承接原来散落在 UI 和 DB 类中的职责。

## 2. 运行方式

### 2.1 Python 环境

推荐 Python 3.11 或更新版本。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` 当前包含：

```text
numpy
opencv-python
pillow
scipy
openpyxl
matplotlib
psutil
```

### 2.2 启动程序

在项目根目录运行：

```powershell
python main.py
```

程序入口是根目录下的 `main.py`。启动后会创建 Tkinter 主窗口、加载 `settings.json`，并显示主控制区和功能页 Notebook。

### 2.3 验证命令

轻量验证：

```powershell
python -B -m compileall .
python -B -m unittest discover -s tests
```

`compileall` 用于检查 Python 语法；`unittest` 用于运行当前基础回归测试。

## 3. 顶层目录结构

```text
ImageProcess/
  main.py
  database.py
  FrameChoosePic.py
  settings.json
  requirements.txt
  README.md
  docs/
    ARCHITECTURE.md
  core/
  algorithms/
  services/
  lib/
  MeasureSheet/
  MeasureBreakupLength/
  MeasureFlameAngle/
  CalcFlameAngle/
  CalcAverageFigure/
  PlayAtmAngle/
  PlayAtmAngleCPP/
  tests/
```

各目录职责如下。

| 路径 | 职责 |
| --- | --- |
| `main.py` | Tkinter 主程序入口，创建主窗口和主界面 |
| `database.py` | 当前全局状态树，负责连接各功能页后端 DB |
| `FrameChoosePic.py` | 功能页 Notebook 容器，负责切换图像和调用当前页面 |
| `core/` | 新的基础设施层：图像 IO、Excel IO、路径、配置、C++ runner、基础模型 |
| `algorithms/` | 新的算法入口层：把旧算法集中暴露成更清晰的计算入口 |
| `services/` | 新的业务流程层：组织 UI 参数、算法调用、外部程序调用 |
| `lib/` | 旧公共库：Tkinter widget、绘图、旧算法辅助函数、Excel helper 等 |
| `MeasureSheet/` | 液膜尺寸测量功能 |
| `MeasureBreakupLength/` | 破碎长度测量功能 |
| `MeasureFlameAngle/` | 火焰锥角单张/轻量批处理功能 |
| `CalcFlameAngle/` | 火焰锥角批处理功能 |
| `CalcAverageFigure/` | 平均图生成、彩色转灰度、Davis 文件预处理 |
| `PlayAtmAngle/` | 雾化锥角单张预览和批处理 UI |
| `PlayAtmAngleCPP/` | 雾化锥角 C++ 加速程序、CMake 工程、兼容输入输出文件 |
| `tests/` | 基础回归测试 |

## 4. 当前分层架构

当前目标架构分为四层：

```text
UI 层
  Tkinter 页面、控件、用户输入、图像显示

Service 层
  组织一次完整处理流程
  例如：构造参数、调用算法、调用 C++、保存结果

Algorithm 层
  纯计算入口
  不应该依赖 Tkinter 控件或全局 UI 状态

Core 层
  通用基础能力
  例如：图像读写、Excel 写入、路径规则、配置文件、C++ runner
```

### 4.1 UI 层

UI 层主要仍由旧目录承载：

- `main.py`
- `FrameChoosePic.py`
- `MeasureSheet/ClassMeasureSheet.py`
- `MeasureBreakupLength/ClassMeasureBreakupLength.py`
- `MeasureFlameAngle/ClassMeasureFlameAngle.py`
- `CalcFlameAngle/ClassCalcFlameAngle.py`
- `CalcAverageFigure/ClassCalcAverageFigure.py`
- `PlayAtmAngle/ClassPlayAtmAngle.py`

UI 层职责：

- 创建 Tkinter 控件
- 绑定按钮、输入框、键盘、鼠标事件
- 从 `tk.Variable` 或 `DB_*` 对象读取参数
- 调用 service
- 刷新图像、曲线、表格

UI 层不应继续承担的职责：

- 不应直接拼接复杂输出路径
- 不应直接实现算法公式
- 不应直接管理 C++ 输入输出细节
- 不应直接处理 Excel 表结构

当前已经迁移的部分：

- 平均图页面调用 `AverageImageService`
- 火焰锥角批处理调用 `FlameAngleService`
- 雾化锥角批处理调用 `AtomizationAngleService`
- 液膜尺寸和破碎长度计算通过 service/algorithm 层完成

### 4.2 Service 层

Service 层位于 `services/`。

```text
services/
  __init__.py
  atomization_angle_service.py
  average_image_service.py
  breakup_length_service.py
  flame_angle_service.py
  sheet_measurement_service.py
```

Service 层职责：

- 接收 UI 层整理出的参数
- 调用 `algorithms/` 中的算法入口
- 调用 `core/` 中的 IO 或 runner
- 对外暴露稳定的“功能级接口”

当前 service：

| Service | 文件 | 职责 |
| --- | --- | --- |
| `AtomizationAngleService` | `services/atomization_angle_service.py` | 调用 C++ runner 执行雾化锥角批处理 |
| `AverageImageService` | `services/average_image_service.py` | 平均图、彩色转灰度、Davis 文件名预处理 |
| `FlameAngleService` | `services/flame_angle_service.py` | 火焰锥角批处理与轻量批处理 |
| `BreakupLengthService` | `services/breakup_length_service.py` | 破碎长度计算 |
| `SheetMeasurementService` | `services/sheet_measurement_service.py` | 液膜宽度/长度计算 |

### 4.3 Algorithm 层

Algorithm 层位于 `algorithms/`。

```text
algorithms/
  __init__.py
  atomization.py
  average.py
  breakup.py
  flame.py
  sheet.py
```

当前大部分复杂算法仍保留在旧位置，`algorithms/` 先作为 facade 层暴露稳定入口。这样可以降低一次性搬迁风险，并为后续逐步移动算法代码做准备。

| 文件 | 当前内容 |
| --- | --- |
| `algorithms/average.py` | 转发平均图相关算法 |
| `algorithms/atomization.py` | 转发雾化锥角 Python 算法 |
| `algorithms/flame.py` | 转发火焰锥角算法 |
| `algorithms/breakup.py` | 破碎长度纯计算 |
| `algorithms/sheet.py` | 液膜尺寸纯计算 |

后续建议：

- 把 `lib/lib_Angle.py` 中的火焰算法逐步迁入 `algorithms/flame.py`
- 把 `lib/lib_AtmAngle.py` 中的雾化锥角 Python 算法逐步迁入 `algorithms/atomization.py`
- 保持算法函数只接收普通数据结构，不访问 Tkinter、DB 或文件系统

### 4.4 Core 层

Core 层位于 `core/`。

```text
core/
  __init__.py
  atomization_angle_runner.py
  config.py
  excel_io.py
  image_io.py
  models.py
  paths.py
```

| 文件 | 职责 |
| --- | --- |
| `atomization_angle_runner.py` | 定义雾化锥角 C++ 批处理参数和 runner |
| `config.py` | `settings.json` 读写封装 |
| `excel_io.py` | 通用 Excel 矩阵写入 |
| `image_io.py` | 支持中文路径的 OpenCV 图像读写 |
| `models.py` | 通用数据模型，例如 `FrameRange` |
| `paths.py` | 路径生成规则，例如实验文件夹和图像路径 |

## 5. 程序启动流程

启动链路：

```text
main.py
  -> 创建 tk.Tk()
  -> Base(root)
    -> ScrollableFrame
    -> Main(...)
      -> DB()
      -> 创建主控制面板
      -> 创建 FrameChoosePic
      -> db.load()
  -> root.mainloop()
```

关键对象：

- `Base`：主窗口壳层
- `Main`：主参数面板和功能 Notebook 的父容器
- `DB`：全局后端状态树
- `FrameChoosePic`：图像序列切换和各功能页容器

窗口关闭时：

```text
close_window()
  -> App.Main.db.save()
  -> root.quit()
  -> root.destroy()
```

## 6. 全局状态与配置

当前配置文件是根目录下的 `settings.json`。它保存了主界面和各功能页的大部分参数，例如：

- 数据目录
- 实验编号
- 当前帧号
- 像素尺寸
- 裁剪参数
- 火焰阈值
- 雾化锥角参数
- 并行进程数

当前状态树：

```text
DB
  Main: DB_main
    FrameChoosePic: DB_FrameChoosePic
      MeasureSheet: DB_MeasureSheet
      MeasureBreakupLength: DB_MeasureBreakupLength
      MeasureFlameAngle: DB_MeasureFlameAngle
      CalcAverageFigure: DB_CalcAverageFigure
      CalcFlameAngle: DB_CalcFlameAngle
      PlayAtmAngle: DB_PlayAtmAngle
```

`CalcInductionLength` 已从状态树中删除。

### 6.1 `BaseSubDB`

`lib/BaseClass.py` 中的 `BaseSubDB` 是当前 DB 子类的共同基类。

主要字段：

- `root`：指向根 DB
- `SubClassName`：子 DB 名称列表
- `SaveVarName`：需要保存到 `settings.json` 的变量名列表

主要方法：

- `update(name, value, FlagFresh=True)`
  - 更新后端变量
  - 可选同步前端 `tk.Variable`
  - 如果存在 `update_<name>()`，自动调用钩子
- `load(dict)`
  - 从配置字典加载变量
  - 递归加载子 DB
- `save()`
  - 收集当前 DB 和子 DB 的保存变量

### 6.2 `create_var`

`BaseFrame.create_var()` 用于把前端变量和后端变量绑定。

它会：

- 在 UI 对象上创建 `tk.StringVar`、`tk.IntVar`、`tk.DoubleVar` 或 `tk.BooleanVar`
- 在后端 DB 对象上创建同名普通属性
- 在后端 DB 对象上创建 `<name>_front`，指向前端变量
- 如果 `FlagSave=True`，把变量名加入 `SaveVarName`

这是当前程序 UI/DB 同步的核心机制。

## 7. 图像选择与功能页切换

`FrameChoosePic.py` 负责公共图像选择逻辑和 Notebook 功能页。

当前功能页顺序：

1. `MeasureSheet`
2. `MeasureBreakupLength`
3. `MeasureFlameAngle`
4. `CalcAverageFigure`
5. `CalcFlameAngle`
6. `PlayAtmAngle`

默认选中：

```python
self.NotebookProcess.select(5)
```

即默认进入 `PlayAtmAngle`。

主要公共参数：

- `Decimate`：帧号抽样间隔
- `FigNameStart`：当前文件夹最小图像编号
- `FigNameEnd`：当前文件夹最大图像编号
- `FigName`：当前帧号
- `ImpactX`、`ImpactY`：撞击点坐标
- `PixSize`：像素尺寸，单位 `um/pix`

图像路径生成：

```text
直接选单张图:
  Main.DirDirect

正常实验文件夹:
  Main.generate_fdir() + "/" + FigName + ".tif"
```

## 8. 功能模块说明

### 8.1 液膜尺寸测量：`MeasureSheet`

路径：

```text
MeasureSheet/
  ClassMeasureSheet.py
  DB_MeasureSheet.py
```

用途：

- 手动标记液膜的左、右、上、下边界
- 计算液膜宽度和长度
- 单位同时输出像素和毫米

核心参数：

- `LineLeftPosition`
- `LineRightPosition`
- `LineUpPosition`
- `LineDownPosition`
- `SheetWidthPix`
- `SheetWidth`
- `SheetLengthPix`
- `SheetLength`

当前计算链路：

```text
ClassMeasureSheet 鼠标/键盘事件
  -> DB_MeasureSheet.update_Sheet_Mouse / update_Sheet_Key
  -> DB_MeasureSheet.update_SheetData
  -> SheetMeasurementService.calculate
  -> algorithms.sheet.calculate_sheet_measurement
```

公式：

```text
width_px = right_px - left_px
length_px = down_px - up_px
width_mm = width_px * pixel_size_um / 1000
length_mm = length_px * pixel_size_um / 1000
```

### 8.2 破碎长度测量：`MeasureBreakupLength`

路径：

```text
MeasureBreakupLength/
  ClassMeasureBreakupLength.py
  DB_MeasureBreakupLength.py
```

用途：

- 手动标记破碎位置
- 根据撞击点 Y 坐标计算破碎长度

核心参数：

- `BreakupPosition`
- `BreakupLengthPix`
- `BreakupLength`

当前计算链路：

```text
ClassMeasureBreakupLength 鼠标/键盘事件
  -> DB_MeasureBreakupLength.update_SheetData
  -> BreakupLengthService.calculate
  -> algorithms.breakup.calculate_breakup_length
```

公式：

```text
length_px = breakup_position_px - impact_y_px
length_mm = length_px * pixel_size_um / 1000
```

### 8.3 火焰锥角测量：`MeasureFlameAngle`

路径：

```text
MeasureFlameAngle/
  ClassMeasureFlameAngle.py
  DB_MeasureFlameAngle.py
  MeasureFlameAngle.py
```

用途：

- 单张火焰图像预览
- 显示伪彩图
- 显示理论线、火焰锥角线、火焰长度线
- 计算火焰中心线角、左右边界角、火焰锥角和火焰长度
- 支持轻量批处理

主要参数：

- `Gain`
- `Threshold`
- `AngleO`
- `AngleF`
- `AngleCalc`
- `AngleL`
- `AngleR`
- `AngleM`
- `Angle`
- `YStart`
- `YEnd`
- `YLength`
- `FigStart`
- `FigEnd`

单张刷新链路：

```text
ClassMeasureFlameAngle.FreshSelf
  -> 读取当前图像
  -> Figure.change_figure
  -> DB_MeasureFlameAngle.Fresh
  -> lib.lib_Angle.calc_theta
  -> lib.lib_Angle.calc_Rparameter_flamedirection
  -> 更新 Angle/Y 参数
```

轻量批处理链路：

```text
ClassMeasureFlameAngle.CommandButtonCalcFlameAngle
  -> FlameAngleService.calculate_lightweight_batch
  -> MeasureFlameAngle.MeasureFlameAngle.calc_flame_angle
  -> 写入 Excel
```

注意：

- 当前火焰算法主体仍在 `lib/lib_Angle.py` 和 `MeasureFlameAngle/MeasureFlameAngle.py`
- `algorithms/flame.py` 已提供 facade，后续可以继续迁移算法代码

### 8.4 火焰锥角批处理：`CalcFlameAngle`

路径：

```text
CalcFlameAngle/
  ClassCalcFlameAngle.py
  DB_CalcFlameAngle.py
  CalcFlameAngle.py
```

用途：

- 批量计算火焰锥角
- 可选保存标记后的伪彩图
- 输出 Excel 结果

当前链路：

```text
ClassCalcFlameAngle.CommandButtonR4
  -> 收集 settings
  -> FlameAngleService.calculate_batch
  -> CalcFlameAngle.CalcFlameAngle.calc_flame_angle
  -> 写入 Excel
```

批处理输出字段包括：

- 帧号
- 中心线角
- 左边界角
- 右边界角
- 火焰锥角
- 火焰中心/起始/结束/长度
- 火焰区域平均强度
- 火焰区域最大强度

### 8.5 平均图与图像预处理：`CalcAverageFigure`

路径：

```text
CalcAverageFigure/
  ClassCalcAverageFigure.py
  DB_CalcAverageFigure.py
  CalcAverageFigure.py
```

用途：

- 彩色图转灰度图
- 计算指定帧范围的平均图
- Davis 导出文件去前缀和灰度放大处理

当前链路：

```text
ClassCalcAverageFigure.CommandButtonProcess
  -> AverageImageService.convert_color_to_gray

ClassCalcAverageFigure.CommandButtonCalcAverage
  -> AverageImageService.calculate_average

ClassCalcAverageFigure.CommandButtonRemovePrefix
  -> AverageImageService.remove_davis_prefix
```

底层算法仍在：

```text
CalcAverageFigure/CalcAverageFigure.py
```

### 8.6 雾化锥角：`PlayAtmAngle`

路径：

```text
PlayAtmAngle/
  ClassPlayAtmAngle.py
  DB_PlayAtmAngle.py
  PlayAtmAngle.py
  Gray.py
```

用途：

- 单张图像预览
- 颜色反转、二值化
- 绘制计算区域
- 绘制雾化锥角线
- 展示左右两侧角度灰度分布曲线
- 调用 C++ 加速程序进行批量计算

主要参数：

- `FlagReverseColor`
- `FlagBinary`
- `ThresBinary`
- `XLeft`
- `XRight`
- `Y`
- `Rmax`
- `ThetaLeft`
- `ThetaRight`
- `window_length`
- `polyorder`
- `NumAvgL`
- `RStartL`
- `NumAvgR`
- `RStartR`
- `ThresRatioL`
- `ThresRatioR`
- `AngleL`
- `AngleR`
- `Angle`
- `FigStart`
- `FigEnd`
- `FlagSaveImg`

单张预览链路：

```text
ClassPlayAtmAngle.FreshSelf
  -> core.image_io.read_image
  -> Figure.change_figure
  -> DB_PlayAtmAngle.Fresh
  -> PlayAtmAngle.PlayAtmAngle.mul_calculate_grayavg_byangle
  -> scipy.signal.savgol_filter
  -> 更新 AngleL / AngleR / Angle
  -> 更新曲线图
```

批处理链路：

```text
ClassPlayAtmAngle.CommandButtonCalcAtmAngle
  -> 构造 AtomizationAngleBatchConfig
  -> AtomizationAngleService.run_batch
  -> AtomizationAngleCppRunner.run_batch
  -> 写 PlayAtmAngleCPP/inputcpp.txt
  -> 执行 PlayAtmAngleCPP/main.exe
  -> C++ 写 result.csv
  -> C++ 兼容调用 process_cpp_result.py
```

当前 C++ 程序仍保持兼容旧流程。Python 侧已经不再直接拼接 `inputcpp.txt` 和 `os.system`，而是通过 `AtomizationAngleCppRunner` 统一处理。

## 9. C++ 加速程序说明

路径：

```text
PlayAtmAngleCPP/
  main.cpp
  calculate_single_image.cpp
  libcv.cpp
  lib_file.cpp
  lib_algorithm.cpp
  Interpolate2D.cpp
  SG_Filter_1st.cpp
  CMakeLists.txt
  main.exe
  inputcpp.txt
  inputpy.txt
  result.csv
  process_cpp_result.py
```

### 9.1 输入文件：`inputcpp.txt`

C++ 程序读取 `inputcpp.txt`，字段顺序由 `core.atomization_angle_runner.AtomizationAngleBatchConfig.to_legacy_lines()` 保持兼容。

字段顺序：

1. 数据目录
2. 起始帧
3. 结束帧
4. Decimate
5. 线程/进程数
6. 左起点 X
7. 右起点 X
8. 起点 Y
9. 最大半径 Rmax
10. 左角度下限
11. 右角度上限
12. 左侧平均点数
13. 左侧起始半径
14. 右侧平均点数
15. 右侧起始半径
16. 左阈值比例
17. 右阈值比例
18. 滤波窗口长度
19. 滤波阶数
20. 是否保存标记图
21. 模式

### 9.2 Python runner

核心类：

```python
AtomizationAngleBatchConfig
AtomizationAngleCppRunner
```

路径：

```text
core/atomization_angle_runner.py
```

职责：

- 校验批处理参数
- 原子写入 `inputcpp.txt`
- 检查 C++ 目录和 `main.exe` 是否存在
- 用 `subprocess.run(..., check=True)` 启动 C++ 程序
- 出错时向上抛出异常，便于 UI 显示失败信息

### 9.3 后处理

当前 C++ 程序在批处理结束后仍调用：

```text
PlayAtmAngleCPP/process_cpp_result.py
```

该脚本负责：

- 读取 `result.csv`
- 写入 Excel
- 计算角度中心线和频域结果
- 更新汇总表
- 打开 Excel

后续建议把这部分也迁入 Python service，令 C++ 只负责高速计算，不负责启动 Python 或 Excel。

## 10. 图像 IO

统一图像 IO 位于：

```text
core/image_io.py
```

主要函数：

```python
read_image(path, flags=cv.IMREAD_UNCHANGED)
write_tiff(path, image)
```

设计原因：

- OpenCV 的普通 `cv.imread()` 对中文路径支持不稳定
- 当前项目大量图像路径包含中文
- 统一使用 `np.fromfile + cv.imdecode`
- 写入统一使用 `cv.imencode + tofile`

当前已接入：

- `PlayAtmAngle/ClassPlayAtmAngle.py` 的 `FreshSelf()`

后续建议继续替换：

- `MeasureSheet/ClassMeasureSheet.py`
- `MeasureBreakupLength/ClassMeasureBreakupLength.py`
- `MeasureFlameAngle/ClassMeasureFlameAngle.py`
- `CalcAverageFigure/CalcAverageFigure.py`
- `CalcFlameAngle/CalcFlameAngle.py`

## 11. Excel IO

统一 Excel 写入位于：

```text
core/excel_io.py
```

主要函数：

```python
write_matrix(ws, data, append=False, row_start=1, col_start=1)
```

旧接口：

```text
lib/excel_io.py
```

仍然保留 `write_excel_mat()`，但内部已经转发到 `core.excel_io.write_matrix()`，用于保持旧调用兼容。

## 12. 路径规则

统一路径 helper 位于：

```text
core/paths.py
```

当前函数：

```python
experiment_dir(data_dir, exp_no)
image_path(folder, frame_no)
result_workbook_path(folder, prefix, class_name)
folder_name(path)
```

后续建议：

- 把所有 `DirData + '/实验编号' + str(ExpNo)` 替换为 `experiment_dir`
- 把所有 `folder + '/' + str(frame) + '.tif'` 替换为 `image_path`
- 统一结果 Excel 文件命名规则

## 13. 测试结构

测试目录：

```text
tests/
  test_core.py
```

当前测试覆盖：

- 雾化锥角 C++ legacy 输入格式
- 液膜尺寸计算
- 破碎长度计算
- 路径生成
- Excel 矩阵写入
- 缺失图像文件错误处理

运行：

```powershell
python -B -m unittest discover -s tests
```

当前测试数量：6。

## 14. 当前架构中的兼容层

为了避免一次性破坏旧程序，当前保留了一些兼容层。

### 14.1 旧算法位置仍保留

例如：

- `lib/lib_Angle.py`
- `lib/lib_AtmAngle.py`
- `CalcAverageFigure/CalcAverageFigure.py`
- `CalcFlameAngle/CalcFlameAngle.py`
- `MeasureFlameAngle/MeasureFlameAngle.py`
- `PlayAtmAngle/PlayAtmAngle.py`

`algorithms/` 目前主要做 facade，并没有完全搬移所有算法实现。

### 14.2 旧 UI/DB 结构仍保留

当前 Tkinter 页面和 DB 结构仍沿用旧方式：

```text
Class*.py
DB_*.py
```

这是为了保证 UI 不被大规模重写。后续可以继续把 UI 中的重复控件、图像显示、裁剪、保存按钮抽成 `ui/` 层。

### 14.3 C++ 后处理仍兼容旧脚本

`PlayAtmAngleCPP/process_cpp_result.py` 仍由 C++ 程序调用。后续建议改成：

```text
C++ only:
  input -> result.csv

Python service:
  result.csv -> Excel / charts / summary workbook
```

这样错误处理、日志和输出路径会更容易维护。

## 15. 数据流示意

### 15.1 手动测量类功能

```text
用户点击/按键
  -> Class*.py 事件处理
  -> DB_*.py 更新参数
  -> Service.calculate(...)
  -> algorithms.* 纯计算
  -> DB_*.py 更新结果变量
  -> Figure 刷新显示
```

适用：

- 液膜尺寸
- 破碎长度

### 15.2 Python 批处理类功能

```text
用户点击批处理按钮
  -> Class*.py 收集参数
  -> Service.calculate_batch(...)
  -> 旧算法模块 / algorithms facade
  -> 返回结果矩阵
  -> UI 或旧代码写 Excel
```

适用：

- 平均图
- 火焰锥角

### 15.3 C++ 加速雾化锥角

```text
用户点击雾化锥角批处理
  -> ClassPlayAtmAngle 构造 AtomizationAngleBatchConfig
  -> AtomizationAngleService
  -> AtomizationAngleCppRunner
  -> 写 inputcpp.txt
  -> 执行 main.exe
  -> C++ 多线程计算
  -> 写 result.csv
  -> 兼容后处理 process_cpp_result.py
```

## 16. 主要技术债

当前已经完成第一轮分层，但仍有一些技术债需要后续继续处理。

### 16.1 UI 代码重复

重复点：

- 图像读取
- 图像裁剪
- 中心线显示
- 保存图片
- Entry 绑定
- 按钮文字切换
- 鼠标/键盘事件

建议：

```text
ui/
  image_view.py
  forms.py
  tool_page.py
```

### 16.2 配置文件缺少 schema

`settings.json` 目前是扁平大字典，缺少：

- 版本号
- 默认值
- 字段迁移
- 类型校验

建议后续加入：

```python
SettingsSchema
SettingsMigration
```

### 16.3 硬编码路径仍存在

部分旧代码仍写死了实验输出路径，例如 `E:\...`、`D:\...`。这些路径应该迁移到：

- UI 可选路径
- `settings.json`
- `core.paths`
- service 参数

### 16.4 C++ 和 Python 算法一致性需要测试

雾化锥角有 Python 和 C++ 两套计算逻辑。建议建立小样例数据，测试：

- 单张图 Python/C++ 结果一致
- 批处理输出帧号顺序一致
- 滤波参数一致
- 8 bit / 16 bit 图像处理一致

### 16.5 结果输出职责仍分散

现在 Excel 输出仍散落在多个 UI 文件和处理脚本中。建议建立：

```text
services/export_service.py
```

或按功能拆分：

```text
services/atomization_exporter.py
services/flame_exporter.py
```

## 17. 后续推荐路线

建议后续按以下顺序继续：

1. 将所有图像读写替换为 `core.image_io`
2. 将所有 Excel 写入替换为 `core.excel_io`
3. 将路径拼接替换为 `core.paths`
4. 将 `process_cpp_result.py` 的后处理迁移到 `AtomizationAngleService`
5. 增加 `ui/` 层，抽象通用图像显示和表单控件
6. 为每个功能准备 1 到 3 张小型测试图像，建立算法回归测试
7. 清理旧脚本、旧注释、未使用 import 和历史 `__pycache__`

## 18. 当前提交状态

当前重构分支：

```text
codex/refactor-architecture
```

重要提交：

```text
7753de8 Initial import
4700f25 Refactor atomization angle C++ runner
8b1916e Add shared image IO helper
9c2cef8 Add generated file ignore rules
fbef5b0 Remove induction length feature
006b222 Introduce services and algorithm facades
2674670 Add project docs and smoke tests
```

本文档描述的是 `2674670` 之后的当前架构状态。
