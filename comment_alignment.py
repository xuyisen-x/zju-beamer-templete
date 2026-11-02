import argparse
import unicodedata
import sys
import platform
import subprocess
import shutil
import os

def copy_to_clipboard(text: str):
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(["pbcopy"], input=text, text=True, check=True)

        elif os_name == "Windows":  # Windows
            subprocess.run(["powershell", "-Command", "$input | Set-Clipboard"], 
                           input=text, text=True, check=True)

        elif os_name == "Linux":
            if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
                print("--- 错误: 未检测到图形界面环境，无法使用剪贴板 ---", file=sys.stderr)
                return
            if shutil.which("wl-copy"):
                subprocess.run(["wl-copy"], input=text, text=True, check=True)
            elif shutil.which("xclip"):
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            elif shutil.which("xsel"):
                subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
            else:
                print("--- 错误: 未检测到 wl-copy/xclip/xsel，无法自动复制 ---", file=sys.stderr)
                return
        else:
            print(f"--- 错误: 不支持的操作系统 {os_name} ---", file=sys.stderr)
            return

        print("--- 结果已成功复制到剪贴板 ---", file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"--- 复制失败: 命令返回非 0 ({e}) ---", file=sys.stderr)
    except Exception as e:
        print(f"--- 复制失败: {e} ---", file=sys.stderr)

def get_visual_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in 'WFA' else 1 for c in text)

def generate_comment_box(title: str, total_width: int) -> str:
    # 装饰性固定宽度（% ++  和  ++ %）
    decoration_fixed_width = 8
    title_width = get_visual_width(title)
    
    padding_total = total_width - decoration_fixed_width - title_width
    
    if padding_total < 0:
        # 如果标题太长，动态调整宽度以适应标题
        total_width = title_width + decoration_fixed_width + 4
        padding_total = 4
        print(f"--- 警告：指定宽度太小，已自动调整为 {total_width} ---", file=sys.stderr)

    left_padding = padding_total // 2
    right_padding = padding_total - left_padding
    
    # 构造注释行
    inner_bar_width = total_width - 4
    line_border = f"% {'=' * inner_bar_width} %"
    line_plus   = f"% {'+' * inner_bar_width} %"
    line_empty  = f"% ++{' ' * (total_width - decoration_fixed_width)}++ %"
    line_title  = f"% ++{' ' * left_padding}{title}{' ' * right_padding}++ %"

    # 返回完整注释块
    result = [line_border, line_plus, line_empty, line_title, line_empty, line_plus, line_border]
    return "\n".join(result)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="用于生成特定风格的LaTeX注释块，支持中英文标题对齐。"
    )
    
    # 必须参数：标题文字
    parser.add_argument("title", help="注释块中间显示的标题文字")
    
    # 可选参数：注释块宽度
    parser.add_argument(
        "-w", "--width", 
        type=int, 
        default=64, 
        help="注释块字符宽度（默认：64）"
    )
    # 可选参数：打印输出或复制到剪贴板
    parser.add_argument("-p", "--print", action="store_true", help="在控制台展示生成的注释块")
    parser.add_argument("-n", "--no-copy", action="store_true", help="禁止自动复制到剪贴板")

    # 解析参数
    args = parser.parse_args()
    should_print = args.print
    should_copy = not args.no_copy

    # 生成注释块
    comment_block = generate_comment_box(args.title, args.width)
    # 打印到控制台
    if should_print: print(comment_block)
    # 复制到剪贴板
    if should_copy: copy_to_clipboard(comment_block)

if __name__ == "__main__":
    main()