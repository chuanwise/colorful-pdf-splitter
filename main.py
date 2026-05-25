#  Copyright 2026 Chuanwise.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import os

import fitz
from PIL import Image, ImageChops


def is_page_colored(page, dpi=36, threshold=5):
    pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_gray = img.convert("L").convert("RGB")
    diff = ImageChops.difference(img, img_gray)

    extrema = diff.getextrema()
    if not extrema:
        return False

    for v_min, v_max in extrema:
        if v_max > threshold:
            return True
    return False

def format_page_ranges(pages):
    """将页码列表转换为类似 '1-5, 7, 9-20' 的字符串格式。"""
    if not pages:
        return "无"

    sorted_pages = sorted(list(pages))
    ranges = []
    start = sorted_pages[0]
    end = sorted_pages[0]

    for p in sorted_pages[1:]:
        if p == end + 1:
            end = p
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = p
            end = p

    ranges.append(f"{start}-{end}" if start != end else str(start))
    return ", ".join(ranges)

def get_page_splits(num_pages, color_pages, single_page=False):
    """
    分离计算逻辑，将提取出的具有彩色内容的页码分配为双面/单面打印页。
    color_pages 为包含彩色内容的页码的 set (0-based)
    """
    final_color_pages = set()
    final_bw_pages = set()

    if single_page:
        for i in range(num_pages):
            if i in color_pages:
                final_color_pages.add(i)
            else:
                final_bw_pages.add(i)
    else:
        for i in range(0, num_pages, 2):
            page1 = i
            page2 = i + 1 if i + 1 < num_pages else None

            p1_color = page1 in color_pages
            p2_color = page2 in color_pages if page2 is not None else False

            if p1_color or p2_color:
                final_color_pages.add(page1)
                if page2 is not None:
                    final_color_pages.add(page2)
            else:
                final_bw_pages.add(page1)
                if page2 is not None:
                    final_bw_pages.add(page2)

    return final_color_pages, final_bw_pages


def process_pdf(file_path, single_page=False, out_dir=None, dpi=36, threshold=5, auto_yes=False, auto_no=False, dry_run=False):
    dirname, basename = os.path.split(file_path)
    name, ext = os.path.splitext(basename)

    if ext.lower() != '.pdf':
        print(f"跳过非 PDF 文件: {file_path}")
        return

    out_dir_path = out_dir if out_dir else dirname
    color_pdf_path = os.path.join(out_dir_path, f"{name}-COLOR.pdf")
    bw_pdf_path = os.path.join(out_dir_path, f"{name}-BW.pdf")

    if not dry_run:
        if out_dir_path and not os.path.exists(out_dir_path):
            os.makedirs(out_dir_path, exist_ok=True)

        if os.path.exists(color_pdf_path) or os.path.exists(bw_pdf_path):
            if auto_no:
                print(f"警告：文件 '{color_pdf_path}' 或 '{bw_pdf_path}' 已存在。跳过处理: {file_path}")
                return
            elif not auto_yes:
                print(f"警告：文件 '{color_pdf_path}' 或 '{bw_pdf_path}' 已存在。")
                ans = input(f"是否覆盖这些文件？(y/n) [n]: ")
                if ans.strip().lower() != 'y':
                    print(f"跳过处理: {file_path}")
                    return

    try:
        with fitz.open(file_path) as doc:
            color_pages = set()
            num_pages = len(doc)

            for i in range(num_pages):
                page = doc[i]
                if is_page_colored(page, dpi=dpi, threshold=threshold):
                    color_pages.add(i)

            final_color_pages, final_bw_pages = get_page_splits(num_pages, color_pages, single_page)

        if not dry_run:
            if len(final_color_pages) > 0:
                with fitz.open(file_path) as color_doc:
                    color_doc.select(sorted(list(final_color_pages)))
                    color_doc.save(color_pdf_path)

            if len(final_bw_pages) > 0:
                with fitz.open(file_path) as bw_doc:
                    bw_doc.select(sorted(list(final_bw_pages)))
                    bw_doc.save(bw_pdf_path)

    except Exception as e:
        print(f"处理 PDF 失败: {file_path}，错误信息: {e}")
        return

    color_pages_1_based = [p + 1 for p in final_color_pages]
    bw_pages_1_based = [p + 1 for p in final_bw_pages]

    print(f"处理完成: {file_path}" + (" (Dry Run)" if dry_run else ""))
    print(f"  总页面数: {num_pages}")
    print(f"  彩色页面: {len(final_color_pages)} ({format_page_ranges(color_pages_1_based)})")
    print(f"  黑白页面: {len(final_bw_pages)} ({format_page_ranges(bw_pages_1_based)})")


def main():
    parser = argparse.ArgumentParser(description="Colorful PDF Splitter - 分割 PDF 的彩色和黑白页")
    parser.add_argument("pdfs", nargs='+', help="需要处理的 PDF 文件列表")
    parser.add_argument("--single-page", action="store_true", help="单页打印模式")
    parser.add_argument("--out", "-o", help="指定输出文件夹，默认为原 PDF 所在目录", default=None)
    parser.add_argument("--dpi", type=int, default=36, help="解析 PDF 使得页面进行渲染时的 DPI，默认为 36。越大越慢越准。")
    parser.add_argument("--threshold", type=int, default=5, help="非灰度判断的亮度阈值，默认为 5。超过该阈值的差异点视为彩色。")
    parser.add_argument("-y", "--yes", action="store_true", help="自动确认覆盖已存在的文件")
    parser.add_argument("-n", "--no", action="store_true", help="自动拒绝覆盖已存在的文件并跳过")
    parser.add_argument("--dry-run", action="store_true", help="演练运行，只统计彩色页信息，不实际生成文件")

    args = parser.parse_args()

    for pdf_file in args.pdfs:
        if not os.path.exists(pdf_file):
            print(f"文件不存在: {pdf_file}")
            continue
        process_pdf(
            pdf_file,
            single_page=args.single_page,
            out_dir=args.out,
            dpi=args.dpi,
            threshold=args.threshold,
            auto_yes=args.yes,
            auto_no=args.no,
            dry_run=args.dry_run
        )


if __name__ == "__main__":
    main()
