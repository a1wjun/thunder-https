'''
v1.0 迅雷thunder链接转https链接
created by HelloWorld05
in 2024.08.01
'''

# 导入模块
from urllib import parse
import base64

# 迅雷地址
thunder_url = 'thunder://QUFodHRwczovL2Rvdy5kb3dsemkuY29tLzIwMjIwMzE3LzQzXzg3NDkzMzZjL+icmOibm+S+oO+8muiLsembhOaXoOW9ki5tcDRaWg=='

try:
    # base64 解码
    decoded_url = base64.b64decode(thunder_url[10:]).decode('utf-8')
    # 去除前两个字符和后两个字符
    trimmed_url = decoded_url[2:-2]
    # url转码
    final_url = parse.unquote(trimmed_url)
    # 输出转码后地址
    print(final_url)
except Exception as e:
    print(f"处理过程中发生错误: {e}")