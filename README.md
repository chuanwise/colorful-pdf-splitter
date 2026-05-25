# Colorful PDF Splitter - 彩色 PDF 分割器

彩色文件打印往往按页计费，价格高昂。尤其是到了毕业季，自行打印大论文，价格更是令人肉疼。Colorful PDF Splitter 是分割 PDF
文件的工具，能够将彩色页和黑白页分开，从而帮助用户节省打印成本。

## 背景

不难发现，PDF 文件中，彩色页的数量远远少于黑白页。为了节省打印成本，我们可以将 PDF 文件分割成两部分：一部分包含所有彩色页，另一部分包含所有黑白页。
这样，我们就可以分别打印彩色页和黑白页，随后再自行拼合，从而大幅降低打印费用。

然而，手动分割 PDF 文件既麻烦又容易出错。以双面打印为例，不仅需要考虑需要彩打的页面，还需要考虑它们的反面——因为双面打印时，彩色页的反面可能是黑白页，或者反之亦然。
手动操作不仅耗时，还容易遗漏或错误地分割页面。

经过简单调研，暂未发现解决类似问题的工具。因此，Colorful PDF Splitter 应运而生。它的输入是一个 PDF，输出为两个 PDF
文件：一个包含所有彩色页，另一个包含所有黑白页。用户只需简单操作，即可轻松完成分割。

## 快速开始

脚本 `main.py` 有 N 个位置参数，每个为一个 PDF 文件。

对于输入的每一个 PDF 文件 `foo.py`，系统将输出两个 PDF：`foo-COLOR.pdf` 和 `foo-BW.pdf`，分别包含需要彩打的页和需要黑白打印的页。
默认输出到该文档所在的相同目录下。若希望输出到指定目录，可以使用 `--out` 或 `-o` 参数。
若输出目录不存在会被自动创建。若这些文件已经存在，则程序将提出警告，并要求输入 `y` 来覆盖它们，或输入 `n` 来跳过该文件的处理。若
PDF 读取失败，则程序将输出错误信息，并跳过该文件的处理。

下面以从 [File Format 网站下载的示例 PDF](https://docs.fileformat.com/pdf/download-pdf/) 为例，来展示两种模式的使用方法。

### 双页打印模式（默认）

预期您输入的每一个 PDF 都将被双页打印。在此情况下，每一个带有彩色内容的页及其背面都将输出指彩色 PDF
中。程序将智能地考虑文档总页数为奇数或偶数的情况。

```bash
python main.py docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

### 单页打印模式

使用 `--single-page` 指定使用单页打印模式，否则默认为双页打印模式。在此情况下，每一个彩色内容的页将输出到彩色 PDF
中，而不考虑其背面内容（除非也是彩色）。

```bash
python main.py --single-page docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

## 进阶

### 自动确认覆盖 (-y)

如果是批量跑脚本不想频繁按回车，或者你正将此脚本集成进其他全自动的工作流中，您可以加入 `-y` (或 `--yes`)
标志。所有原本需要人工确认才能覆盖前次同名拆分结果的情况都会默认强行覆盖：

```bash
python main.py -y docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

### 指定输出文件夹 - `--out`

使用 `--out` 或 `-o` 指定拆分后的 PDF 文件存放位置。如果文件夹不存在将被自动创建。

```bash
python main.py --out output/ docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

由于程序是通过将 PDF 页面渲染为图像，并比较原图与灰度图的差异来判断是否包含彩色内容，在某些极端情况下（如有微小的高压缩噪声色块），你可能会需要调整检测的精度参数。

### DPI - `--dpi`

指定渲染页面以进行色彩检测时使用的内部 DPI，默认为 `36`。
可以将其调高以获得更精确的细节判定（例如检测极小的彩色文字），但会显著增加处理时间和系统内存的占用：

```bash
python main.py --dpi 72 docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

> **注意**：该 DPI 仅用来判断页面是否是彩色，**不会**影响最终导出的 PDF 的清晰度（输出的 PDF 是无损的逻辑切分，可以保留完美的矢量效果和原图画质）。

### 色彩阈值 - `--threshold`

原图相较于灰度图在 RGB 颜色通道上的容差容忍值，默认为 `5` (范围 0-255)。

- 调大可以避免将非常接近灰色的轻微偏色（压缩噪点）误认为“彩色页面”。
- 调小使判断更加严苛，稍有一点偏色的色差也会被分割为彩色页。

```bash
python main.py --threshold 10 docs/examples/SamplePDF-500kb-Text-Images-Links-9Pages.pdf
```

## 贡献代码

欢迎任何形式的贡献！无论是修复 bug、添加新功能，还是改进文档，都非常感谢。请随时提交 Pull Requests 或在 Issues 中提出建议。

贡献代码之前，请确保测试通过。例如，你可以使用以下命令运行测试：

```bash
python main.py .\docs\examples\SamplePDF-500kb-Text-Images-Links-9Pages.pdf --out .\docs\examples\double-pages\
python main.py .\docs\examples\SamplePDF-500kb-Text-Images-Links-9Pages.pdf --out .\docs\examples\single-page --single-page
```

## 许可证

```text
Copyright 2026 Chuanwise.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```