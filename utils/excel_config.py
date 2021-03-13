import io
import xlwt


def set_excel_style(color='white', colour_index=0, height=180, bold=False, name=u'宋体',
                    horz=xlwt.Alignment.HORZ_CENTER, vert=xlwt.Alignment.VERT_CENTER):
    """定义 excel 文件内容样式"""
    style = xlwt.XFStyle()
    # 设置字体
    font_one = xlwt.Font()
    font_one.name = name
    font_one.bold = bold
    font_one.colour_index = colour_index
    font_one.height = height
    style.font = font_one

    # 设置文字位置
    alignment = xlwt.Alignment()
    alignment.horz = horz  # 水平方向设置：左对齐/居中/右对齐
    alignment.vert = vert  # 垂直方向设置
    style.alignment = alignment

    # 设置单元格背景颜色
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map[color]
    style.pattern = pattern

    # 设置单元格边框线条
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style.borders = borders

    return style


class XlsExporter(object):
    """
    数据导出到 excel, 依赖包 xlwt, 导出文件行数限制65535
    >>> xe = XlsExporter()
    >>> data = [
    ... [1, 'aa', '2020-01-01'],
    ... [2, 'bb', '2020-01-02'],
    ... ]
    >>> xe.add_sheet(data, sheetname='sheet', headers=('col1', 'col2', 'col3'))
    字典数据导出
    >>> from collections import OrderedDict
    >>> data_dict = [
    ... {'a': 1, 'b': '2020-01-01'},
    ... {'a': 2, 'b': '2020-01-02'},
    ... ]
    >>> header_map = OrderedDict([('a', 'col1'), ('b', 'col2')])
    >>> xe.add_sheet_by_dict(data=data_dict, header_map=header_map, sheetname='sheet2')

    >>> xe.to_file('./test.xls')    # 直接保存本地文件
    >>> bio = xe.to_bio()           # 保存到BytesIO对象
    """

    def __init__(self, header_style, value_style):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.header_style = header_style  # 表头设置
        self.value_style = value_style  # 内容设置

    def add_sheet(self, data, headers=None, sheet_name='sheet', cell_overwrite_ok=False):
        """ 源数据为列表/元组格式 """
        sheet = self.wb.add_sheet(sheetname=sheet_name, cell_overwrite_ok=cell_overwrite_ok)
        first_row = 0
        if headers:
            for c, header in enumerate(headers):
                sheet.write(0, c, header, self.header_style)
                sheet.col(c).width = 256 * 20  # 列的宽度
            first_row = 1

        for r, line in enumerate(data, first_row):
            for c, item in enumerate(line):
                sheet.write(r, c, item, self.value_style)

    def add_sheet_by_dict(self, data, header_mapping, sheet_name='sheet', cell_overwrite_ok=False):
        """ 源数据为字典格式 """
        fields, headers = zip(*header_mapping.items())
        data_list = list()
        for item in data:
            data_list.append([item.get(f, None) for f in fields])
        self.add_sheet(data_list, headers=headers, sheet_name=sheet_name, cell_overwrite_ok=cell_overwrite_ok)

    def to_bio(self):
        bio = io.BytesIO()
        self.wb.save(bio)
        bio.seek(0)
        return bio

    def to_file(self, file_path):
        self.wb.save(file_path)


def export_to_bio(header_style, value_style, data_dict, header_map, sheet_name='sheet'):
    """ 数据 excel 导出到 BytesIO """
    xe = XlsExporter(header_style, value_style)
    xe.add_sheet_by_dict(data_dict, header_map, sheet_name=sheet_name)
    return xe.to_bio()


def export_to_file(header_style, value_style, data_dict, header_map, file_path, sheet_name='sheet1'):
    """数据 excel 导出到文件"""
    xe = XlsExporter(header_style, value_style)
    xe.add_sheet_by_dict(data_dict, header_map, sheet_name=sheet_name)
    xe.to_file(file_path)
    return
