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
