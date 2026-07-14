# ImageProcess v2 架构说明

这份文档说明 `ImageProcessv2` 的整体架构。它面向没有接触过专业 GUI 程序框架的维护者，重点解释每个目录为什么存在、代码之间如何调用、以后应该在哪里改功能。

## 1. 总体目标

`ImageProcessv2` 是一个独立的科研图像处理程序包。它不再依赖旧工程根目录下的 `main.py`、`database.py`、`FrameChoosePic.py`、旧 GUI 页面，也不依赖根目录下的 `core/`、`services/`、`algorithms/`、`lib/`。

也就是说，后续可以把整个 `ImageProcessv2/` 文件夹复制到其他位置，只要 Python 依赖和 C++ runtime 所需 DLL 都在，就可以运行。

启动方式：

```powershell
python -m ImageProcessv2.main
```

或：

```powershell
python ImageProcessv2\main.py
```

## 2. 核心设计思想

旧 GUI 的主要问题是：界面控件、全局变量、算法调用、文件路径、Excel 输出混在一起。典型代码类似：

```python
self.back.update('FigStart', self.back.root.Main.FrameChoosePic.FigNameStart)
```

这种写法的问题是：

- 需要记住很深的对象层级。
- 页面之间互相知道太多内部结构。
- 参数在哪里创建、在哪里修改、在哪里保存不清楚。
- 以后改一个控件，可能影响很多功能。

v2 的改法是把程序拆成几层：

```text
UI 层
  只负责窗口、按钮、输入框、图像预览、鼠标点击

Application 层
  负责应用状态、页面动作、把 GUI 参数转换成一次处理任务

Domain 层
  负责纯数据模型，例如实验路径、帧范围、火焰参数、雾化参数

Service 层
  负责完整业务流程，例如“计算火焰锥角并导出 Excel”

Algorithm 层
  负责实际计算公式和图像算法入口

Core 层
  负责通用基础能力，例如图像读写、配置读写、Excel 写入、C++ runner

Lib 层
  负责算法内部需要的数学 helper

C++ Runtime
  负责雾化锥角高速批处理
```

一个简单原则是：上层可以调用下层，下层不要反过来知道上层。

例如：

```text
按钮点击
  -> UI 页面
  -> ImageProcessActions
  -> Service
  -> Algorithm / Core / C++ Runtime
  -> 输出文件
```

算法层不应该知道 Tkinter 控件，也不应该知道哪个按钮触发了它。

## 3. 目录结构

当前主要目录如下：

```text
ImageProcessv2/
  main.py
  README.md
  requirements.txt
  docs/
    ARCHITECTURE_CN.md
  domain/
    context.py
    settings.py
  application/
    app_state.py
    actions.py
    frame_catalog.py
  ui/
    app_window.py
    experiment_panel.py
    widgets.py
    preview/
      image_preview_pane.py
    pages/
      processing_pages.py
  services/
  algorithms/
  core/
  lib/
  PlayAtmAngleCPP/
  sample_data/
```

## 4. 各层职责

### 4.1 main.py

`main.py` 是程序入口，只做三件事：

- 创建 Tkinter 主窗口。
- 创建 `AppState`。
- 创建 `AppWindow`。

它不应该放具体功能逻辑。比如“计算雾化锥角”“保存平均图”都不应该写在这里。

### 4.2 domain/

`domain/` 保存纯数据模型。

代表文件：

- `context.py`
- `settings.py`

这里的数据模型不依赖 Tkinter，也不依赖算法。它们只是描述“程序当前有哪些参数”。

例如：

- `ExperimentContext`：实验目录、实验编号、帧范围、撞击点、像素尺寸。
- `FrameSelection`：起始帧、结束帧、当前帧、抽帧间隔。
- `FlameSettings`：火焰锥角参数。
- `AtomizationSettings`：雾化锥角参数。

这种做法的好处是：参数有明确位置，不再散落在各个页面控件或旧 `DB` 对象中。

### 4.3 application/

`application/` 是 GUI 和业务功能之间的中间层。

代表文件：

- `app_state.py`
- `actions.py`
- `frame_catalog.py`

`AppState` 负责保存整个程序状态：

```text
AppState
  settings
    experiment
    flame
    atomization
```

`ImageProcessActions` 负责把一个按钮动作转换成具体业务调用。

例如点击“C++ 批处理雾化锥角”后，调用链大致是：

```text
AtomizationPage._run_batch()
  -> ImageProcessActions.run_atomization_batch()
  -> build_atomization_config()
  -> AtomizationAngleService.run_batch()
  -> AtomizationAngleCppRunner.run_batch()
  -> PlayAtmAngleCPP/main.exe
```

这样 UI 页面不需要知道 C++ 输入文件怎么写，也不需要知道 Excel 后处理怎么做。

### 4.4 ui/

`ui/` 是 Tkinter 界面层。

代表文件：

- `app_window.py`
- `experiment_panel.py`
- `widgets.py`
- `preview/image_preview_pane.py`
- `pages/processing_pages.py`

UI 层只做这些事：

- 创建窗口和控件。
- 把输入框的值写回 `AppState`。
- 响应按钮点击。
- 显示状态信息。
- 预览图像和记录鼠标点击坐标。

当前 GUI 采用“左侧功能页 + 右侧共享预览窗格”的布局：

- `ProcessingPages` 只负责左侧功能页：液膜测量、平均图、火焰锥角、雾化锥角。
- `ImagePreviewPane` 只负责右侧图像显示、鼠标取点、刷新节流和坐标换算。
- 切换页面时，当前页面会把自己的预览渲染函数和鼠标点击处理函数注册到 `ImagePreviewPane`。
- 修改当前帧、实验编号、火焰参数、雾化参数或测量参数后，预览会自动延迟刷新。
- 取点模式使用单选，因为一次鼠标点击只能表示一个动作。
- 显示内容使用多选图层，例如裁剪框、撞击点、火焰角、动量角、雾化计算区域和锥角线可以按需要叠加显示。

这种布局适合科研调参：参数输入和图像反馈在同一屏幕中，不需要切到独立预览页。

UI 层不应该直接实现算法公式，不应该直接处理 Excel 表，也不应该直接拼 C++ 输入输出细节。

### 4.5 services/

`services/` 是功能流程层。

它负责组织一次完整处理流程，例如：

- 平均图计算。
- 火焰锥角批处理。
- 火焰锥角结果导出。
- 雾化锥角 C++ 批处理。
- 雾化锥角结果后处理。
- 液膜和破碎长度计算。

Service 的特点是：它知道一次任务需要哪些算法和 IO，但不关心 GUI 控件。

### 4.6 algorithms/

`algorithms/` 是算法入口层。

这里放图像计算逻辑，例如：

- 平均图。
- 彩色转灰度。
- 火焰锥角批处理。
- 雾化锥角 Python 版计算入口。
- 液膜尺寸和破碎长度的纯计算。

这一层应该尽量保持“输入普通参数，输出普通结果”。不要在算法里访问 Tkinter，也不要依赖页面对象。

### 4.7 core/

`core/` 是基础设施层。

例如：

- `image_io.py`：支持中文路径的图像读写。
- `excel_io.py`：Excel 矩阵写入。
- `config.py`：`settings_v2.json` 读写。
- `parallel.py`：帧范围切分。
- `atomization_angle_runner.py`：调用 C++ 程序。

这类代码不是某个功能专属，而是多个功能都会用。

### 4.8 lib/

`lib/` 是算法内部数学 helper。

这里的代码更接近公式和数值方法，例如：

- 双线性插值。
- 火焰角计算 helper。
- 雾化角计算 helper。
- DFT helper。

这层代码通常不需要知道“实验编号”“Excel 文件”“按钮”等概念。

### 4.9 PlayAtmAngleCPP/

`PlayAtmAngleCPP/` 是雾化锥角 C++ runtime。

它包含：

- `main.exe`
- C++ 源码
- OpenCV / MinGW 所需 DLL

v2 运行雾化 C++ 批处理时，会在这个目录写入输入文件并执行 `main.exe`。

## 5. 数据流示例

### 5.1 刷新帧范围

```text
用户点击“刷新帧范围”
  -> ExperimentPanel._refresh_frame_info()
  -> AppState.refresh_frame_selection()
  -> FrameCatalog.scan_tif_numbers()
  -> 更新 ExperimentContext.frames
  -> UI 显示帧范围
```

这里 `FrameCatalog` 只负责扫描文件夹中按数字命名的 `.tif` 文件。

### 5.2 计算平均图

```text
用户点击“计算并保存平均图”
  -> AveragePage._save_average()
  -> ImageProcessActions.save_average_image()
  -> AverageImageService.calculate_average()
  -> algorithms.average.calculate_average_image()
  -> core.image_io.write_tiff()
```

页面只触发动作，不直接读图、不直接算平均值。

### 5.3 雾化锥角 C++ 批处理

```text
用户填写雾化参数
  -> AtomizationPage.apply_to_state()
  -> AtomizationSettings

用户点击“C++ 批处理雾化锥角”
  -> ImageProcessActions.run_atomization_batch()
  -> build_atomization_config()
  -> AtomizationAngleService.run_batch()
  -> AtomizationAngleCppRunner 创建本次 runs/... 任务目录
  -> 在任务目录写 inputcpp.txt
  -> 在任务目录执行 main.exe
  -> 在任务目录生成 result.csv
  -> AtomizationResultExportService 导出 Excel
```

## 6. settings_v2.json 的作用

`settings_v2.json` 是本机运行状态，不是固定配置模板。

它保存：

- 实验路径。
- 实验编号。
- 帧范围。
- 撞击点。
- 火焰参数。
- 雾化参数。

这个文件已被 `.gitignore` 忽略，因为不同电脑、不同实验日期的路径和参数都可能不同。

## 7. 为什么这种结构更可维护

### 7.1 参数位置明确

旧写法中，一个变量可能在 UI 控件、DB 对象、父对象、子页面之间来回传。

v2 中：

- 实验公共参数在 `ExperimentContext`。
- 火焰参数在 `FlameSettings`。
- 雾化参数在 `AtomizationSettings`。

需要找参数时，先看 `domain/settings.py`。

### 7.2 页面不再互相穿透

旧写法常见：

```python
self.back.root.Main.FrameChoosePic.xxx
```

这等于一个页面知道了整个窗口树的内部结构。

v2 中，页面只拿到：

- `AppState`
- `ImageProcessActions`

页面不需要知道其他页面怎么组织。

### 7.3 算法可以单独测试

算法函数不依赖 GUI 后，可以直接在测试里调用。

这对于科研程序很重要，因为后续你可能要确认：

- 某个公式有没有改错。
- 某个图像处理流程结果是否稳定。
- C++ 和 Python 结果是否一致。

### 7.4 独立搬迁更容易

v2 内部导入都使用：

```python
from ImageProcessv2.xxx import ...
```

而不是：

```python
from core.xxx import ...
from services.xxx import ...
```

这保证了 `ImageProcessv2/` 搬到其他目录后，不会再去找旧工程根目录下的模块。

## 8. 以后修改功能时应该改哪里

### 修改界面文字或布局

看：

- `ui/experiment_panel.py`
- `ui/pages/processing_pages.py`
- `ui/preview/image_preview_pane.py`

### 增加一个新参数

一般需要改：

1. `domain/settings.py`：把参数加入对应 dataclass。
2. `ui/pages/processing_pages.py`：把参数加入表单字段。
3. `application/actions.py`：如果这个参数要参与任务配置，在这里传给 service。

### 修改平均图、火焰、雾化的处理流程

看：

- `application/actions.py`
- `services/`

### 修改具体算法公式

看：

- `algorithms/`
- `lib/`

### 修改 C++ 调用方式

看：

- `core/atomization_angle_runner.py`
- `services/atomization_angle_service.py`
- `PlayAtmAngleCPP/`

## 9. C++ 通信文件隔离

雾化 C++ 程序本身仍然按照旧规则读取 `inputcpp.txt`，并输出 `result.csv`。v2 没有强行重写 C++ 通信格式，而是在 Python runner 层做隔离：

- 每次批处理都会在 `ImageProcessv2/PlayAtmAngleCPP/runs/` 下创建一个独立任务目录。
- `main.exe` 和所需 DLL 会以硬链接方式放入任务目录；如果硬链接失败，则自动复制。
- 本次任务的 `inputcpp.txt` 写入任务目录。
- C++ 生成的 `result.csv` 也只存在于任务目录。
- Excel 后处理直接读取本次任务目录下的 `result.csv`。

这样做的好处是：

- 不再覆盖 `PlayAtmAngleCPP/` 根目录下的固定通信文件。
- 多次处理实验时，每次任务都有独立输入和输出。
- 出错后可以回看对应任务目录，确认当时写入 C++ 的参数和结果。
- 不需要重新编译 C++，保持当前高速程序稳定。
