# ImageProcess v3 架构说明

## 1. 程序定位

`ImageProcessv3` 是面向科研图像数据处理的桌面程序，主要功能包括：

- 液膜宽度、长度和破碎长度测量；
- 平均图生成与彩色图转灰度图；
- 火焰锥角处理；
- 雾化锥角单帧调参与批量处理；
- 结果图、灰度曲线和 Excel 数据导出；
- 实验汇总表参数读取与结果写入。

程序以简洁、可读和可维护为优先目标。参数由科研人员负责设置，只保留能够防止程序进入明显错误状态的基础检查。

v3 是独立程序包，不引用 v2 或旧 GUI 文件。雾化锥角计算全部由 Python 完成，不需要额外的可执行程序和通信文件。

## 2. 运行方式

在 `ImageProcessv3` 的上一级目录运行：

```powershell
python -m ImageProcessv3.main
```

或者直接运行：

```powershell
python ImageProcessv3\main.py
```

入口文件是 `main.py`。它只负责创建 Tk 根窗口、加载状态、构建主界面以及在关闭时保存配置。

## 3. 分层结构

```text
ImageProcessv3/
├─ main.py
├─ settings_v3.json
├─ application/
│  ├─ app_state.py
│  ├─ actions.py
│  └─ frame_catalog.py
├─ domain/
│  ├─ context.py
│  └─ settings.py
├─ ui/
│  ├─ app_window.py
│  ├─ experiment_panel.py
│  ├─ widgets.py
│  ├─ pages/
│  └─ preview/
├─ services/
├─ algorithms/
├─ core/
├─ lib/
└─ sample_data/
```

调用方向保持单向：

```text
UI -> Application -> Services -> Algorithms/Core/Lib
                  -> Domain
```

下层模块不反向访问 GUI 控件，因此算法、导出和状态管理可以独立测试。

## 4. 各层职责

### 4.1 Domain

`domain/context.py` 定义实验上下文：数据根目录、实验编号、帧范围、当前帧、抽帧间隔、撞击点和像素尺寸。

`domain/settings.py` 定义各功能参数：

- `FlameSettings`：火焰锥角参数；
- `AtomizationSettings`：雾化锥角参数；
- `MeasurementSettings`：液膜测量状态；
- `PreviewSettings`：预览保存目录、文件名和图层状态；
- `AppSettings`：组合全部设置并负责 JSON 转换。

Domain 中只保存数据，不访问 Tkinter，不读取图像，也不写 Excel。

### 4.2 Application

`application/app_state.py` 持有当前 `AppSettings`，负责加载和保存 `settings_v3.json`，以及重新扫描帧范围。

`application/actions.py` 是 GUI 的统一操作入口。页面只调用诸如：

- `save_average_image()`；
- `export_breakup_records()`；
- `calculate_flame_batch()`；
- `run_atomization_batch()`。

Actions 负责组织参数和服务，不实现具体数学算法。

### 4.3 UI

`ui/app_window.py` 负责整体布局：

- 顶部为实验参数；
- 左侧为功能页；
- 右侧为共享图像预览。

`ui/pages/processing_pages.py` 中的每个页面只管理本功能的输入控件、按钮、状态文字和预览叠加逻辑。

`ui/preview/image_preview_pane.py` 统一负责图像显示、缩放、坐标与灰度值显示、鼠标取点、图层开关以及预览图保存。

普通 Entry 不会在输入过程中自动刷新。用户按回车后，数据写入状态并刷新当前页面。

液膜测量页只保留当前实验上下文的逐帧记录。实验编号、数据根目录或直接图像来源发生变化时，页面立即清空液膜尺寸与破碎长度两类记录，并将表格和统计文字恢复为空状态，避免不同工况的数据混合。

### 4.4 Services

Services 负责完整科研操作流程，例如：

- 调用算法批量计算；
- 统计平均值和标准差；
- 生成工作簿；
- 更新实验汇总表；
- 确定输出路径。

`measurement_export_service.py` 同时负责液膜尺寸和破碎长度结果表的导出与回读。回读时跳过前两行参数和列标题，只恢复逐帧数据区；页面根据结果表标题自动切换到相应测量模式，并重新计算平均值和标准差。

雾化锥角相关服务分为：

- `atomization_angle_service.py`：生成帧序列、调用多进程算法并记录计算时间；
- `atomization_result_export_service.py`：直接接收计算结果矩阵，生成 Excel、频域数据和图表，并更新汇总表；
- `atomization_preview_export_service.py`：导出单帧灰度曲线。

### 4.5 Algorithms

Algorithms 只处理数组和数值参数，不了解 GUI 控件和 Excel 格式。

`algorithms/atomization.py` 定义：

- `AtomizationParameters`：计算所需的纯数值参数；
- `calculate_atomization_batch()`：按帧列表拆分任务并并行计算；
- 单个工作进程内部的逐帧计算和可选标记图保存。

### 4.6 Core 与 Lib

`core/` 提供稳定的基础能力：图像读写、配置文件、Excel 矩阵写入、路径和任务拆分。

其中 `excel_workbook_coordinator.py` 是所有 Excel 写入操作的统一协调层。写入前，它只按完整路径查找目标工作簿；若该文件已经在 Excel 中打开，则先保存并关闭该工作簿。写入完成后自动打开目标文件。它不会退出 Excel，也不会保存、关闭或修改其他已打开的工作簿。

`lib/` 保存底层数值函数。雾化锥角的角度灰度积分位于 `lib_AtmAngle.py`，当前使用 NumPy 向量化实现。

## 5. 雾化锥角处理流程

### 5.1 单帧预览

```text
用户修改参数并按回车
  -> 当前页面把 Entry 写入 AtomizationSettings
  -> ImagePreviewPane 刷新当前图像
  -> 计算左右面积加权平均灰度曲线
  -> Savitzky-Golay 滤波
  -> 根据阈值比例提取左右边界角
  -> 更新锥角线、结果文字和四张灰度曲线
```

页面保留一份简单的完整结果缓存。当图像路径和全部计算参数都相同时直接复用结果；任一计算参数变化时重新计算。

顶部实验参数栏提供播放/暂停和帧率输入。播放沿 `FrameSelection` 的有效帧集合前进，遵守帧范围和抽帧间隔，到达最后一帧后自动暂停。定时器使用 Tk `after()`，不会从后台线程操作 GUI。

### 5.2 向量化计算

旧式算法逐角度、逐半径调用 Python 插值函数。v3 将一组角度和半径组成二维坐标矩阵，批量完成：

1. 采样坐标生成；
2. 有效区域掩码；
3. 双线性插值；
4. 面积加权求和。

普通单帧调参仍使用分块向量化计算。播放开始后建立临时 `AtomizationSamplingGeometry`，缓存采样坐标对应的像素索引、双线性插值权重和面积权重；后续帧只读取像素并求加权和，暂停后释放缓存。数学定义、角度分辨率和插值公式保持不变。

四张面积加权灰度曲线使用一个 Figure 中的四个 Axes。坐标轴、曲线和角度标记只创建一次，逐帧刷新时通过 `set_data()` 和 Matplotlib blit 更新，不再清空坐标轴或重复执行 `tight_layout()`。数据超出当前纵坐标范围时才进行一次完整重绘。

### 5.3 Python 批量处理

```text
用户点击“批量处理雾化锥角”
  -> ImageProcessActions.run_atomization_batch()
  -> AtomizationAngleService.run_batch()
  -> FrameSelection 统一生成 start/end/decimate 对应的实际帧列表
  -> 按进程数均匀拆分帧列表
  -> 每个工作进程为自己的图像分块建立一次采样几何缓存
  -> 各进程调用同一套面积加权和阈值提取公式
  -> 合并为 [Frame, AngleL, AngleR, AtmAngle] 矩阵
  -> AtomizationResultExportService.export()
  -> 保存结果工作簿并更新汇总表
```

单帧预览和批量处理共用 `AtomizationSamplingGeometry`、面积加权和阈值提取函数。多进程之间不共享 NumPy 缓存对象，每个进程只在开始处理自己的帧分块时建立一次缓存。

平均图、彩色转灰度、火焰锥角和雾化锥角均接收同一份实际帧列表；当前帧加减按钮以及液膜测量快捷键也在该列表中移动。因此抽帧间隔统一限定四个页面能够处理的图像集合。

Windows 启动多个 Python 进程存在数秒固定开销。1000 张左右时固定开销占比较高，10000 张时主要由实际计算决定。

### 5.4 批处理进度

雾化锥角、火焰锥角、平均图和彩色转灰度共用 `core/progress.py`：

1. 每个工作进程完成一帧后，将共享计数器加一；
2. 主进程每 100 ms 读取一次计数器；
3. UI 更新 `已完成/总数/百分比` 和确定型进度条；
4. 所有任务结束后统一显示 100%。

批处理期间仍保持原来的阻塞方式，用户不能同时操作其他控件。GUI 只执行必要的重绘，不引入后台线程、取消状态或额外任务生命周期管理。

## 6. 雾化结果工作簿

为了兼容已有科研数据，v3 保留原工作簿布局：

- 第 1 行：参数标题；
- 第 2 行：参数值和计算时间；
- 第 3 行：`Frame / AngleL / AngleR / AtmAngle / AngleM`；
- 第 4 行：平均值；
- 第 5 行：标准差；
- 第 6 行：相对标准差；
- 第 7 行起：逐帧结果；
- 右侧：频域数据和时域、频域图表。

结果可以写入实验目录，也可以写入雾化页面手动选择的导出目录。

汇总表仍按第一行标题寻找参数位置，不依赖固定 Excel 列字母。

所有结果工作簿和被更新的汇总表都使用同一套 Excel 写入协调流程。若目标文件被 WPS 或其他无法通过 Excel COM 控制的程序占用，程序会给出明确错误，不会另存为时间戳文件或写入意外位置。

## 7. 配置持久化

`settings_v3.json` 位于 `ImageProcessv3` 目录内。关闭窗口时保存：

- 实验路径和编号；
- 帧范围、当前帧和抽帧间隔；
- 各功能参数；
- 液膜测量状态；
- 当前页面；
- 预览图层勾选状态；
- 导出目录与预览文件名。

因此复制整个 `ImageProcessv3` 文件夹后，配置和程序代码仍保持在一起。

## 8. 修改功能时的位置

- 修改控件布局或中文文字：`ui/`；
- 修改按钮触发流程：`application/actions.py`；
- 修改批处理组织方式：对应 `services/`；
- 修改数学计算：`algorithms/` 或 `lib/`；
- 修改 Excel 格式和汇总表：对应导出 service；
- 新增持久参数：先修改 `domain/settings.py`，再绑定到页面。

不要让算法读取 Tkinter 变量，也不要让页面直接操作工作簿。保持这条边界，程序在功能继续增加后仍然容易理解和测试。
