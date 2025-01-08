import tkinter as tk
from tkinter import messagebox
from urllib import parse
import base64

# 迅雷地址处理函数
def process_thunder_url():
    thunder_url = entry.get().strip()  # 去除输入框首尾空格
    if not thunder_url.startswith("thunder://"):
        messagebox.showerror("错误", "输入的地址不是有效的迅雷链接。")
        return

    try:
        # base64 解码
        decode_part = thunder_url[10:]  # 提取 base64 编码部分
        decoded_url = base64.b64decode(decode_part).decode('utf-8')
        
        # 去掉字符串首尾的无效字符
        trimmed_url = decoded_url[2:-2] if len(decoded_url) > 4 else decoded_url
        
        # URL转码
        final_url = parse.unquote(trimmed_url)
        
        # 在标签中显示转码后的地址
        result_label.config(text=f"解码后的URL: {final_url}")
    
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        messagebox.showerror("错误", "解码过程中发生错误，请检查输入格式。")
    except Exception as e:
        messagebox.showerror("错误", f"处理过程中发生错误: {e}")

# 创建主窗口
root = tk.Tk()
root.title("迅雷地址解码器")

# 创建并放置标签和输入框
label = tk.Label(root, text="请输入迅雷地址:")
label.pack(pady=5)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# 创建并放置处理按钮
button = tk.Button(root, text="解码", command=process_thunder_url)
button.pack(pady=20)

# 创建并放置结果标签
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

# 运行主循环
root.mainloop()
