'''
v1.2 迅雷thunder链接转https链接
created by HelloWorld05
in 2025.03.30
'''

import tkinter as tk
from tkinter import ttk, messagebox
from urllib import parse
import base64
import webbrowser

def convert_thunder_link():
    thunder_url = entry.get().strip()
    if not thunder_url:
        messagebox.showerror("错误", "请输入迅雷地址")
        return
    if not thunder_url.startswith('thunder://'):
        messagebox.showerror("错误", "地址必须以thunder://开头")
        return
    
    try:
        encoded_str = thunder_url[10:]
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_url = decoded_bytes.decode('utf-8')
        trimmed_url = decoded_url[2:-2]
        final_url = parse.unquote(trimmed_url)
        
        result_entry.config(state='normal')
        result_entry.delete(0, tk.END)
        result_entry.insert(0, final_url)
        result_entry.config(state='readonly')
        global converted_url
        converted_url = final_url
    except Exception as e:
        messagebox.showerror("转换错误", f"处理过程中发生错误: {str(e)}")

def copy_to_clipboard():
    if converted_url:
        root.clipboard_clear()
        root.clipboard_append(converted_url)
        messagebox.showinfo("成功", "链接已复制到剪贴板")

def open_in_browser():
    if converted_url:
        try:
            webbrowser.open(converted_url)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开链接: {str(e)}")
    else:
        messagebox.showwarning("警告", "没有可用的链接")

# 创建主窗口
root = tk.Tk()
root.title("thunder-https v1.2")
root.geometry("600x300")

# 全局变量存储转换后的URL
converted_url = ""

# 创建界面组件
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill='both')

# 输入部分
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill='x', pady=5)

ttk.Label(input_frame, text="迅雷地址:").pack(side='left')
entry = ttk.Entry(input_frame, width=50)
entry.pack(side='left', padx=10, expand=True, fill='x')

# 转换按钮
convert_btn = ttk.Button(main_frame, text="转换链接", command=convert_thunder_link)
convert_btn.pack(pady=10)

# 结果部分
result_frame = ttk.Frame(main_frame)
result_frame.pack(fill='x', pady=5)

ttk.Label(result_frame, text="普通链接:").pack(side='left')
result_entry = ttk.Entry(result_frame, width=50, state='readonly')
result_entry.pack(side='left', padx=10, expand=True, fill='x')

# 操作按钮
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(pady=10)

copy_btn = ttk.Button(btn_frame, text="复制链接", command=copy_to_clipboard)
copy_btn.pack(side='left', padx=5)

open_btn = ttk.Button(btn_frame, text="打开链接", command=open_in_browser)
open_btn.pack(side='left', padx=5)

root.mainloop()
