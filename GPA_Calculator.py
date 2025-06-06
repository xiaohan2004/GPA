import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import sys
import pandas as pd  # 用于导出 Excel
import webbrowser


# 获取资源的绝对路径
def resource_path(relative_path):
    """获取资源的绝对路径。"""
    try:
        # PyInstaller 创建的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 正常运行的路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 保存输入框内容到文件
def save_input_to_file():
    try:
        with open("input_data.json", "w", encoding="utf-8") as file:
            file.write(json_input.get("1.0", "end-1c"))
    except Exception as e:
        messagebox.showerror("错误", f"保存文件时出错: {e}")


# 从文件中读取内容到输入框
def load_input_from_file():
    try:
        if os.path.exists("input_data.json"):
            with open("input_data.json", "r", encoding="utf-8") as file:
                json_input.delete("1.0", "end")
                json_input.insert("1.0", file.read())
    except Exception as e:
        messagebox.showerror("错误", f"读取文件时出错: {e}")


# 根据成绩计算绩点的函数
def calculate_gpa(score):
    if score >= 95:
        return 4.5
    elif score >= 90:
        return 4.0
    elif score >= 85:
        return 3.5
    elif score >= 80:
        return 3.0
    elif score >= 75:
        return 2.5
    elif score >= 70:
        return 2.0
    elif score >= 65:
        return 1.5
    elif score >= 60:
        return 1.0
    else:
        return 0.0


# 计算加权平均分和加权学分绩的函数
def calculate_weighted_scores():
    try:
        # 获取表格中的数据
        total_score = 0
        total_credits = 0
        total_gpa = 0
        for child in treeview.get_children():
            score = float(treeview.item(child)["values"][2])  # 成绩
            credit = float(treeview.item(child)["values"][3])  # 学分
            gpa = float(treeview.item(child)["values"][4])  # 绩点
            total_score += score * credit
            total_credits += credit
            total_gpa += gpa * credit

        # 计算加权平均分和加权绩点
        if total_credits != 0:
            weighted_average = total_score / total_credits
            weighted_gpa = total_gpa / total_credits
        else:
            weighted_average = weighted_gpa = 0

        # 显示计算结果
        messagebox.showinfo(
            "计算结果",
            f"加权平均分: {weighted_average:.2f}\n加权学分绩: {weighted_gpa:.2f}",
        )

    except Exception as e:
        messagebox.showerror("错误", f"计算出错: {e}")


def get_score(entry):
    """获取成绩，处理异常情况并返回分数"""
    try:
        return float(entry.get("cj", 0))
    except Exception:
        if entry.get("cj") == "优秀":
            return 95.0
        elif entry.get("cj") == "良好":
            return 85.0
        else:
            return None  # 返回 None 表示成绩无法处理


# 加载输入框中的JSON数据并显示到表格
def load_json():
    try:
        # 获取输入框内容并解析为JSON
        data = json.loads(json_input.get("1.0", "end-1c"))

        # 清空表格
        for item in treeview.get_children():
            treeview.delete(item)

        # 重修课程列表
        repair_courses = []
        # 渲染数据到表格
        for entry in data.get("items", []):  # 获取 "items" 列表
            if entry.get("ksxz") == "重修":  # 如果是重修课程则先存储到列表中
                score = get_score(entry)
                if score is None:
                    continue  # 如果分数无法处理，跳过该条记录
                repair_courses.append(
                    {
                        "kch": entry.get("kch", ""),
                        "kcmc": entry.get("kcmc", ""),
                        "cj": score,
                        "xf": entry.get("xf", ""),
                    }
                )
            else:
                score = get_score(entry)
                if score is None:
                    continue  # 如果分数无法处理，跳过该条记录
                gpa = calculate_gpa(score)  # 计算绩点
                treeview.insert(
                    "",
                    "end",
                    values=(
                        entry.get("kch", ""),
                        entry.get("kcmc", ""),
                        score,
                        entry.get("xf", ""),
                        gpa,
                    ),
                )

        # 处理重修课程：遍历重修课程列表，如果表格中已经有该课程的成绩，则只保留最高分；否则插入新的记录
        if repair_var.get():  # 如果勾选了“计算重修”
            for course in repair_courses:
                found = False
                for item in treeview.get_children():
                    if str(treeview.item(item)["values"][0]) == str(course["kch"]):
                        found = True
                        if course["cj"] > float(treeview.item(item)["values"][2]):
                            # 更新原有成绩
                            treeview.item(
                                item,
                                values=(
                                    course["kch"],
                                    course["kcmc"],
                                    course["cj"],
                                    course["xf"],
                                    calculate_gpa(course["cj"]),
                                ),
                            )
                        break
                if not found:
                    gpa = calculate_gpa(course["cj"])  # 计算绩点
                    treeview.insert(
                        "",
                        "end",
                        values=(
                            course["kch"],
                            course["kcmc"],
                            course["cj"],
                            course["xf"],
                            gpa,
                        ),
                    )

    except json.JSONDecodeError:
        messagebox.showerror("错误", "输入的不是有效的 JSON 格式！")


# 清空输入框
def clear_input():
    json_input.delete("1.0", "end")


# 表格排序功能
def sort_table(col_index, reverse=False):
    # 获取表格中的所有数据
    data = [(treeview.item(item)["values"], item) for item in treeview.get_children()]
    # print(data)

    # 按成绩列（col_index=2）排序
    data.sort(key=lambda x: float(x[0][col_index]), reverse=reverse)
    # print(data)

    # 删除表格中的所有数据
    obj = treeview.get_children()
    for o in obj:
        treeview.delete(o)

    # 添加排序后的数据
    for values, item in data:
        treeview.insert("", "end", values=values)


# 切换排序顺序
def toggle_sort_order():
    global reverse_sort  # 需要在全局范围内修改排序顺序
    reverse_sort = not reverse_sort  # 反转排序顺序
    sort_table(2, reverse=reverse_sort)  # 按成绩列排序

    # 根据排序方向更新按钮文本
    if reverse_sort:
        toggle_sort_button.config(text="成绩降序")  # 降序时按钮显示“成绩降序”
    else:
        toggle_sort_button.config(text="成绩升序")  # 升序时按钮显示“成绩升序”


# 新增课程对话框
def add_new_row():
    # 创建 Toplevel 对话框
    add_window = tk.Toplevel(root)
    add_window.title("新增课程")
    add_window.geometry("300x250")

    # 输入框标签和控件
    tk.Label(add_window, text="课程代码:").grid(row=0, column=0, padx=10, pady=5)
    course_code_entry = tk.Entry(add_window)
    course_code_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_window, text="课程名称:").grid(row=1, column=0, padx=10, pady=5)
    course_name_entry = tk.Entry(add_window)
    course_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_window, text="成绩:").grid(row=2, column=0, padx=10, pady=5)
    score_entry = tk.Entry(add_window)
    score_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(add_window, text="学分:").grid(row=3, column=0, padx=10, pady=5)
    credit_entry = tk.Entry(add_window)
    credit_entry.grid(row=3, column=1, padx=10, pady=5)

    # 提交按钮
    def submit():
        try:
            score = float(score_entry.get())
            credit = float(credit_entry.get())
            course_code = course_code_entry.get()
            course_name = course_name_entry.get()

            # 计算绩点
            gpa = calculate_gpa(score)

            # 将新数据插入表格
            treeview.insert(
                "", "end", values=(course_code, course_name, score, credit, gpa)
            )

            # 关闭对话框
            add_window.destroy()

        except ValueError:
            messagebox.showerror("输入错误", "成绩和学分必须是有效数字！")

    submit_button = tk.Button(add_window, text="提交", command=submit)
    submit_button.grid(row=4, column=0, columnspan=2, pady=20)

    # 运行对话框
    add_window.transient(root)
    add_window.grab_set()
    add_window.mainloop()


# 删除选中行
def delete_selected_row():
    selected_item = treeview.selection()  # 获取选中的行
    if not selected_item:
        messagebox.showwarning("警告", "请先选择要删除的行！")
        return
    for item in selected_item:
        treeview.delete(item)  # 删除选中的行


# 导出为 Excel
def export_to_excel():
    # 弹出选择文件保存对话框
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
    )
    if not file_path:
        return  # 用户取消保存

    # 弹出选择对话框
    choice = messagebox.askquestion(
        "选择导出内容",
        "是否导出表格中的数据？\n（选择“否”将导出 JSON 输入框中的数据）",
    )

    if choice == "yes":  # 如果选择了“是”，导出表格中的数据
        # 获取表格中的数据
        data = []
        for child in treeview.get_children():
            values = treeview.item(child)["values"]
            data.append(values)

        if not data:
            messagebox.showwarning("警告", "表格中没有数据！")
            return

        # 将数据转换为 DataFrame
        df = pd.DataFrame(
            data, columns=["课程代码", "课程名称", "成绩", "学分", "绩点"]
        )

    else:  # 如果选择了“否”，导出 JSON 输入框中的数据
        try:
            # 解析 JSON 数据
            data = json.loads(json_input.get("1.0", "end-1c"))
            items = data.get("items", [])

            # 检查 items 是否为空
            if not items:
                messagebox.showwarning("警告", "JSON 输入框中没有有效数据！")
                return

            # 提取需要的字段
            extracted_data = []
            for item in items:
                extracted = {
                    "学年": item.get("xnmmc"),
                    "学期": item.get("xqmmc"),
                    "课程代码": item.get("kch"),
                    "课程名称": item.get("kcmc"),
                    "课程性质": item.get("kcxzmc"),
                    "学分": item.get("xf"),
                    "成绩备注": item.get("cjbz"),
                    "绩点": item.get("jd"),
                    "成绩性质": item.get("ksxz"),
                    # "是否学位课程": item.get("sfkj"),  # 解析有误，并且无意义，不导出
                    "开课学院": item.get("kkbmmc"),
                    "课程标记": item.get("kcbj"),
                    "课程类别": item.get("kclbmc"),
                    "课程归属": item.get("kcgsmc"),
                    "教学班": item.get("jxbmc"),
                    "任课教师": item.get("jsxm"),
                    # "考核方式": item.get("khfsmc"),  # 无意义，有些老师乱填，不导出
                    # "学号": item.get("xh"),  # 无意义，不导出
                    # "姓名": item.get("xm"),  # 无意义，不导出
                    # "学生标记": item.get("sfzx"),  # 解析有误，并且无意义，不导出
                    "成绩": item.get("cj"),
                    "是否成绩作废": item.get("cjsfzf"),
                    "学分绩点": item.get("xfjd"),
                }
                extracted_data.append(extracted)

            # 将提取的数据转换为 DataFrame
            df = pd.DataFrame(extracted_data)

        except Exception as e:
            messagebox.showerror("错误", f"解析 JSON 数据失败: {e}")

    # 导出为 Excel
    try:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("成功", f"数据已导出到 {file_path}")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败: {e}")


# 设置窗口
root = tk.Tk()
root.title("成绩计算器")
root.geometry("900x600")

# 创建选项卡
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# 主页选项卡
home_tab = ttk.Frame(notebook)
notebook.add(home_tab, text="主页")

# 输入框
json_input_label = tk.Label(home_tab, text="输入JSON数据:")
json_input_label.pack(pady=5)
json_input = tk.Text(home_tab, height=10, width=80)
json_input.pack(pady=5)

# 按钮框架
button_frame = tk.Frame(home_tab)
button_frame.pack(pady=10)

# 加载按钮
load_button = tk.Button(button_frame, text="加载", command=load_json)
load_button.grid(row=0, column=0, padx=10)

# 新增一个单选按钮“计算重修”
repair_var = tk.BooleanVar()  # 用于存储单选按钮的值
repair_check = tk.Checkbutton(button_frame, text="计算重修", variable=repair_var)
repair_check.grid(row=0, column=1, padx=10)

# 清空按钮
clear_button = tk.Button(button_frame, text="清空", command=clear_input)
clear_button.grid(row=0, column=2, padx=10)

# 计算按钮
calculate_button = tk.Button(
    button_frame, text="计算", command=calculate_weighted_scores
)
calculate_button.grid(row=0, column=3, padx=10)

# 切换排序按钮
toggle_sort_button = tk.Button(button_frame, text="成绩升序", command=toggle_sort_order)
toggle_sort_button.grid(row=0, column=4, padx=10)

# 新增按钮
add_row_button = tk.Button(button_frame, text="新增课程", command=add_new_row)
add_row_button.grid(row=0, column=5, padx=10)

# 删除按钮
delete_button = tk.Button(button_frame, text="删除行", command=delete_selected_row)
delete_button.grid(row=0, column=6, padx=10)

# 导出按钮
export_button = tk.Button(button_frame, text="导出为 Excel", command=export_to_excel)
export_button.grid(row=0, column=7, padx=10)

# 表格
columns = ("课程代码", "课程名称", "成绩", "学分", "绩点")
treeview_frame = tk.Frame(home_tab)
treeview_frame.pack(pady=10)

# 创建 Treeview 表格并绑定到框架中
treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=15)
treeview.grid(row=0, column=0)

# 设置表格列标题
for col in columns:
    treeview.heading(col, text=col)

# 设置表格列宽度
treeview.column("课程代码", width=100)
treeview.column("课程名称", width=200)
treeview.column("成绩", width=100)
treeview.column("学分", width=100)
treeview.column("绩点", width=100)

# 滑块：垂直滚动条
scrollbar = tk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

# 将 Treeview 与滚动条关联
treeview.configure(yscrollcommand=scrollbar.set)


# 使表格内容可编辑
def on_edit(event):
    item = treeview.selection()[0]
    column = treeview.identify_column(event.x)
    col_index = int(column.replace("#", "")) - 1

    # 获取当前列的值
    current_value = treeview.item(item)["values"][col_index]

    # 弹出输入框让用户修改
    new_value = simpledialog.askstring(
        "修改", f"修改 {columns[col_index]}:", initialvalue=current_value
    )

    if new_value is not None:
        # 更新表格中的值
        treeview.item(
            item,
            values=(
                treeview.item(item)["values"][0],
                treeview.item(item)["values"][1],
                (treeview.item(item)["values"][2] if col_index != 2 else new_value),
                (treeview.item(item)["values"][3] if col_index != 3 else new_value),
                (
                    treeview.item(item)["values"][4]
                    if col_index not in [4, 2]
                    else calculate_gpa(float(new_value))
                ),
            ),
        )


treeview.bind("<Double-1>", on_edit)

# 全局变量来控制排序方向
reverse_sort = False  # 初始为升序

# 操作说明选项卡
instructions_tab = ttk.Frame(notebook)
notebook.add(instructions_tab, text="操作说明")

# 美化操作说明页面
instructions_frame = tk.Frame(instructions_tab)
instructions_frame.pack(pady=20, padx=20, fill="both", expand=True)

instructions_text = """
1. 在主页的输入框中粘贴 JSON 数据。
注：
JSON 数据通过教务处的“信息查询->学生成绩查询->F12打开开发者工具->点击查询按钮”，然后
在开发者工具的网络选项中点击刚刚发送的查询请求，点击“预览”或“响应”，复制其中的 JSON 数据即可。
2. 点击“加载”按钮，将数据加载到表格中。并且可以选择“计算重修”来计算重修课程的最高分。
3. 点击“计算”按钮，计算加权平均分和加权学分绩。
4. 双击表格中的单元格可以编辑数据。
5. 点击“新增课程”按钮可以手动添加课程。
6. 点击“删除行”按钮可以删除选中的行。
7. 点击“导出为 Excel”按钮可以将表格数据导出为 Excel 文件。
8. 看不懂 JSON 数据怎么获取吗？对于操作还有什么疑问吗？点击下方的链接查看详细说明。
注：
计算功能计算的是当前表格中的数据，勾选了“计算重修”之后要重新点击“加载”按钮再计算才会生效。
勾选“计算重修”后，如果表格中已有重修课程的成绩，则只保留最高分；若无则插入重修课程的成绩。
"""

# 创建一个标签显示操作说明文本
instructions_label = tk.Label(
    instructions_frame, text=instructions_text, justify="left", font=("Arial", 12)
)
instructions_label.pack(pady=10)

# 创建一个超链接标签
link = tk.Label(instructions_frame, text="点击查看详细说明", fg="blue", cursor="hand2")
link.pack(pady=10)


# 绑定点击事件，跳转到指定链接
def open_link(event):
    webbrowser.open(
        "https://dandansad.com/index.php/2025/01/24/%e6%88%90%e7%bb%a9%e8%ae%a1%e7%ae%97%e5%99%a8%e4%bd%bf%e7%94%a8%e8%af%b4%e6%98%8e/"
    )  # 替换为你想跳转的网址


link.bind("<Button-1>", open_link)

# 关于选项卡
about_tab = ttk.Frame(notebook)
notebook.add(about_tab, text="关于")

# 美化关于页面
about_frame = tk.Frame(about_tab)
about_frame.pack(pady=20, padx=20, fill="both", expand=True)

about_text = """
成绩计算器

版本: 2.0

作者: XiaoHan

描述: 
这是一个用于计算加权平均分和加权学分绩的工具。用教务
处获得的json格式数据形成表格，可以编辑表格信息进行计
算，同时还可以新增或删除课程用于预测分数。此外还可以
选择是否计算重修课程以及导出数据为Excel文件。

联系方式(微信): dan2deyousang
"""
about_label = tk.Label(about_frame, text=about_text, justify="left", font=("Arial", 12))
about_label.pack(pady=10)

# 打赏选项卡
donate_tab = ttk.Frame(notebook)
notebook.add(donate_tab, text="打赏")


# 加载打赏图片
try:
    donate_image_path = resource_path("donate_image.png")  # 获取图片路径
    donate_image = tk.PhotoImage(file=donate_image_path)
    image_label = tk.Label(donate_tab, image=donate_image)
    image_label.pack(pady=10)
    donate_label = tk.Label(donate_tab, image=donate_image)
    donate_label.pack(pady=20)
except Exception as e:
    print(f"加载打赏图片失败: {e}")


# 在窗口关闭时保存输入框内容
def on_closing():
    save_input_to_file()
    root.destroy()


# 绑定窗口关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# 在窗口启动时加载输入框内容
load_input_from_file()

# 运行应用
root.mainloop()
