import csv
import openpyxl
from openpyxl.chart import LineChart, Reference
from dft import *
import os
# fdir=r'E:\\Sci\\2022.1_impinging_jet\\Research\\1-U-Pc-rou\\雾化锥角\\20230416\\实验编号81'
# MaxFreq=100#图像显示的最大频率
current_folder = os.path.abspath(os.path.dirname(__file__))
with open(current_folder+"\\inputpy.txt", 'r',encoding='utf-8') as file:
    lines = file.readlines()
fdir=lines[0].strip()+'\\'+lines[3].strip()
SummaryDir=lines[1].strip()
MaxFreq=lines[2].strip()

csv_filename=current_folder+"\\result.csv"
def convert_to_number(value):
    """尝试将字符串值转换为整数或浮点数"""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value  # 如果都不是，返回原始字符串
def read_columns_to_list(ws, start_row=7, columns=['B', 'C', 'D']):

    data_list = []

    for row in ws.iter_rows(min_row=start_row, min_col=2, max_col=4):
        # 提取指定列的值
        row_data = [row[0].value,row[1].value,row[2].value]
        # 转换为浮点数，并忽略空值
        row_data = [float(cell) if cell is not None else None for cell in row_data]
        data_list.append(row_data)

    return np.array(data_list)
def write_excel_mat(ws,data,FlagContinue=False,row_start=1,col_start=1):
    '''
    向ws工作表中写入data矩阵，矩阵左上角的单元格坐标为row_start,col_start
    '''
    if FlagContinue:
        row_start+=ws.max_row
    for ni,i in enumerate(data):
        for nj,j in enumerate(i):
            ws.cell(ni+row_start,nj+col_start,j)
wb = openpyxl.Workbook()
ws = wb.active
with open(csv_filename, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        new_row = [convert_to_number(cell) for cell in row]
        ws.append(new_row)
res=read_columns_to_list(ws)
AngleM=(res[:,0]+res[:,1])/2
write_excel_mat(ws,[['AngleM']],FlagContinue=False,row_start=3,col_start=5)
write_excel_mat(ws,[[np.mean(AngleM)]],FlagContinue=False,row_start=4,col_start=5)
write_excel_mat(ws,[[np.std(AngleM,ddof=1)]],FlagContinue=False,row_start=5,col_start=5)
write_excel_mat(ws,[[np.std(AngleM,ddof=1)/ws.cell(row=4,column=4).value]],FlagContinue=False,row_start=6,col_start=5)
for ni,i in enumerate(AngleM):
    ws.cell(ni+7,5,i)
res=np.column_stack((res,AngleM))
#频域特性
cache_dftans=(dft(res[:,0],40000),dft(res[:,1],40000),dft(res[:,2],40000),dft(res[:,3],40000))
resfft=np.column_stack((cache_dftans[0][0],cache_dftans[0][1],cache_dftans[1][1],cache_dftans[2][1],cache_dftans[3][1]))[:len(cache_dftans[0][0])//2,:]#只保留正频率
write_excel_mat(ws,[['f/Hz','左边界角幅值/°','右边界角幅值/°','雾化锥角幅值/°','锥角中心线幅值/°']],FlagContinue=False,row_start=3,col_start=6)
write_excel_mat(ws,[['最大值']+list(np.max(resfft[1:,:],axis=0))[1:]],FlagContinue=False,row_start=4,col_start=6)
write_excel_mat(ws,resfft,FlagContinue=False,row_start=5,col_start=6)

# 创建第一个折线图
chart1 = LineChart()
chart1.title = "时域信号"
chart1.y_axis.title = "角度/°"
chart1.x_axis.title = "帧数"

# 添加数据系列
data1 = Reference(ws, min_col=2, min_row=7, max_col=5, max_row=ws.max_row)
chart1.add_data(data1, titles_from_data=True)

# 设置图例名称
legend_names = ["左锥角", "右锥角", "雾化锥角"]
for i, name in enumerate(legend_names):
    chart1.series[i].name = name

# 设置横轴数据
cats1 = Reference(ws, min_col=1, min_row=7, max_row=ws.max_row)
chart1.set_categories(cats1)

# 设置图表位置和大小
ws.add_chart(chart1, "K3")
chart1.width = 28  # 宽度
chart1.height = 10  # 高度

# 创建第二个折线图
chart2 = LineChart()
chart2.title = "频域信号：DFT分解"
chart2.y_axis.title = "幅值/°"
chart2.x_axis.title = "频率"

# 添加数据系列
data2 = Reference(ws, min_col=7, min_row=5, max_col=10, max_row=MaxFreq)
chart2.add_data(data2, titles_from_data=True)

# 设置图例名称
for i, name in enumerate(legend_names):
    chart2.series[i].name = name

# 设置横轴数据
cats2 = Reference(ws, min_col=6, min_row=5, max_row=MaxFreq)
chart2.set_categories(cats2)

# 设置图表位置和大小
ws.add_chart(chart2, "K22")
chart2.width = 28  # 宽度
chart2.height = 10  # 高度

# 创建第三个折线图
chart3 = LineChart()
chart3.title = "频域信号：DFT分解"
chart3.y_axis.title = "幅值/°"
chart3.x_axis.title = "频率"

# 添加数据系列
data2 = Reference(ws, min_col=7, min_row=5, max_col=10, max_row=ws.max_row//2)
chart3.add_data(data2, titles_from_data=True)

# 设置图例名称
for i, name in enumerate(legend_names):
    chart3.series[i].name = name

# 设置横轴数据
cats2 = Reference(ws, min_col=6, min_row=5, max_row=ws.max_row//2)
chart3.set_categories(cats2)

# 设置图表位置和大小
ws.add_chart(chart3, "K42")
chart3.width = 28  # 宽度
chart3.height = 10  # 高度
import psutil
def close_all_excel():
    for process in psutil.process_iter(['pid', 'name']):
        if 'EXCEL.EXE' in process.info['name']:
            try:
                # 尝试终止Excel进程
                psutil.Process(process.info['pid']).terminate()
            except Exception as e:
                print(f"Error closing Excel process: {e}")

close_all_excel()
wb.save(fdir+'雾化锥角批处理结果.xlsx')
os.system(r'start excel "'+fdir+'雾化锥角批处理结果.xlsx'+r'"')
print('后处理文件完成')

#写入汇总表
def extract_and_convert_to_int(input_str):#抓取字符串最后的数字部分
    # Find the numeric part at the end of the string
    numeric_part = ''.join(filter(str.isdigit, input_str[::-1]))

    # Reverse the numeric part to get the correct order
    numeric_part = numeric_part[::-1]

    # Convert the numeric part to an integer
    result = int(numeric_part) if numeric_part else None

    return result

ExpNo=extract_and_convert_to_int(lines[3].strip())
wb_target=openpyxl.load_workbook(SummaryDir)
ws_target=wb_target.active
for i in range(1,15):#写入设置参数
    for j in range(1,ws_target.max_column+1):
        if ws.cell(row=1,column=i).value == ws_target.cell(row=1,column=j).value:
            ws_target.cell(ExpNo+2,j,ws.cell(row=2,column=i).value)
for i in range(1,ws_target.max_column+1):
    if ws_target.cell(row=1,column=i).value=='AngleL':
        ws_target.cell(ExpNo+2,i,ws.cell(row=4,column=2).value)
        ws_target.cell(ExpNo+2,i+1,ws.cell(row=5,column=2).value)
    if ws_target.cell(row=1,column=i).value=='AngleR':
        ws_target.cell(ExpNo+2,i,ws.cell(row=4,column=3).value)
        ws_target.cell(ExpNo+2,i+1,ws.cell(row=5,column=3).value)
    if ws_target.cell(row=1,column=i).value=='AtmAngle':
        ws_target.cell(ExpNo+2,i,ws.cell(row=4,column=4).value)
        ws_target.cell(ExpNo+2,i+1,ws.cell(row=5,column=4).value)
    if ws_target.cell(row=1,column=i).value=='AngleM':
        ws_target.cell(ExpNo+2,i,ws.cell(row=4,column=5).value)
        ws_target.cell(ExpNo+2,i+1,ws.cell(row=5,column=5).value)
wb_target.save(SummaryDir)
os.system(r'start excel "'+SummaryDir+r'"')
print('写入汇总表完成')
# wb.save('result.xlsx')