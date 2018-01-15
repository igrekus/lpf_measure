import pathlib2 as pt
import xlsxwriter

def export_to_excel(data):
    fname, xname, yname, xdata, ydata = data

    excel_path = ".\\excel\\"
    pt.Path(excel_path).mkdir(parents=True, exist_ok=True)

    wb = xlsxwriter.Workbook(excel_path + fname)
    ws = wb.add_worksheet("Sheet1")

    ws.write("A1", xname)
    ws.write("B1", yname)

    start_row = 0
    row = 0
    for x, y in zip(xdata, ydata):
        row += 1
        ws.write(start_row + row, 0, x)
        ws.write(start_row + row, 1, y)

    chart = wb.add_chart({"type": "scatter",
                          "subtype": "smooth"})
    chart.add_series({"name": "Sheet1!$B$1",
                      "categories": "=Sheet1!$A$2:$A$" + str(row + 1),
                      "values": "=Sheet1!$B$2:$B$" + str(row + 1)})
    chart.set_x_axis({"name": xname})
    chart.set_y_axis({"name": yname})
    ws.insert_chart("D3", chart)

    wb.close()


