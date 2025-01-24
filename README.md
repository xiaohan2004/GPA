# 成绩计算器

## 项目简介
成绩计算器是一个用于计算加权平均分和加权学分绩的工具。它可以通过教务处获取的 JSON 格式数据生成表格，支持编辑表格信息、新增未来课程以预测分数。此外，程序还提供了操作说明、关于信息和打赏功能。

## 使用方法

1. 直接运行GPA_Calculator.py文件
2. 运行exe可执行文件
3. 使用
   ```bash
   pyinstaller --onefile --windowed --icon=favicon.ico --add-data "donate_image.png;." --clean .\GPA_Calculator.py
   ```
   打包源代码运行

## 文件结构

GPA/  
├── gpa_calculator.py       # 主程序文件  
├── favicon.ico             # 程序图标  
├── donate_image.jpg        # 打赏页面图片  
├── README.md               # 项目说明文件  
└── .gitignore  