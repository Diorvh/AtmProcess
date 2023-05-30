def write_excel_mat(ws,data,FlagContinue=False,row_start=1,col_start=1):
    '''
    向ws工作表中写入data矩阵，矩阵左上角的单元格坐标为row_start,col_start
    '''
    if FlagContinue:
        row_start+=ws.max_row
    for ni,i in enumerate(data):
        for nj,j in enumerate(i):
            ws.cell(ni+row_start,nj+col_start,j)
def read_rows_from_excel(ws, start_row, end_row=None):
    if end_row is None:
        # Read a single row
        row_data = [cell.value for cell in ws[start_row]]
        return row_data

    # Read an interval of rows
    row_data = []
    for row_number in range(start_row, end_row + 1):
        row = [cell.value for cell in ws[row_number]]
        row_data.append(row)

    return row_data
def read_columns_from_excel(ws, start_column, end_column=None):

    if end_column is None:
        # Read a single column
        column_data = [cell.value for cell in ws[start_column]]
        return column_data

    # Read a range of columns
    column_data = []
    for column_number in range(start_column, end_column + 1):
        column = [cell.value for cell in ws[column_number]]
        column_data.append(column)

    return column_data