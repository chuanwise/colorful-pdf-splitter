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

import unittest
from main import get_page_splits

class TestPDFSplitterLogic(unittest.TestCase):
    def test_case_1_from_user(self):
        # 1. MC; 2. OpenEnded 3. GameModes 4. Skins 5. Mobs 6. McPacks
        # 7. Dimensions 8. TheEnd 9. Tail
        # 1, 2, 3, 4, 5, 6 是彩色的，7, 8, 9 是黑白的 (1-based)
        num_pages = 9
        color_pages_1_based = [1, 2, 3, 4, 5, 6]

        # 转换为 0-based index 进行测试
        color_pages_0_based = [p - 1 for p in color_pages_1_based]

        color_out, bw_out = get_page_splits(num_pages, color_pages_0_based, single_page=False)

        # 结果转换回 1-based 用于断言
        color_out_1_based = [p + 1 for p in color_out]
        bw_out_1_based = [p + 1 for p in bw_out]

        self.assertEqual(color_out_1_based, [1, 2, 3, 4, 5, 6])
        self.assertEqual(bw_out_1_based, [7, 8, 9])

    def test_case_2_scattered(self):
        # 比如说我现在彩色的是 1, 5, 8, 9, 20, 23（1-based） (共设 24 页)
        num_pages = 24
        color_pages_1_based = [1, 5, 8, 9, 20, 23]

        color_pages_0_based = [p - 1 for p in color_pages_1_based]
        color_out, bw_out = get_page_splits(num_pages, color_pages_0_based, single_page=False)

        color_out_1_based = sorted([p + 1 for p in color_out])

        # 按照双页（1-2, 3-4, 5-6 等）补偿背面的逻辑
        # 1 -> 1, 2
        # 5 -> 5, 6 (注意不是 4,6。因为奇数是纸张正面，n=5是正面，背面是6)
        # 8 -> 7, 8
        # 9 -> 9, 10
        # 20 -> 19, 20
        # 23 -> 23, 24
        expected_color = [1, 2, 5, 6, 7, 8, 9, 10, 19, 20, 23, 24]

        self.assertEqual(color_out_1_based, expected_color)

if __name__ == '__main__':
    unittest.main()
