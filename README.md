# DNA-RNA 核苷酸 A4 PDF 排版生成器

本專案提供一個自動化的 Python 工具，用於將個別的核苷酸圖片素材排版並編譯成標準、可直接列印的 A4 PDF 檔案。非常適合用於教具製作與生物學教學，讓學生可以親手剪裁並組裝出實體的 DNA 雙螺旋結構或單股 RNA 模型。

---

## 🚀 核心功能

*   **情境一 (整張單一核苷酸)**：生成整頁填滿 10 行 × 2 列的相同核苷酸 PDF。包含分開的 DNA 核苷酸組（`DNA-A/T/C/G`）與 RNA 核苷酸組（`RNA-A/U/C/G`）。
*   **情境二 (雙股配對序列)**：輸入自訂的 DNA 或 RNA 序列，生成左右相鄰配對的雙股結構：
    *   **左列 (編碼股)**：正常方向（上方為 5'，下方為 3'），並在左側邊距中印出全域序列的鹼基編號小字（1, 2, 3...）。
    *   **右列 (互補股)**：旋轉 180 度（上方為 3'，下方為 5'），以呈現化學上的反向平行結構。兩股的氫鍵連接線會在頁面中軸完美交會。
*   **情境三 (單股接續序列)**：輸入自訂的單股序列，以接續排版（左行排滿 10 顆後接右行排 10 顆，然後換頁）生成 PDF。兩行均為正常方向（5' 朝上、3' 朝下）。鹼基編號分別印在左邊行（左側邊距）與右邊行（右側邊距），完全避免文字重疊。
*   **自動化素材辨識**：系統會自動根據序列中的鹼基（例如含有胸腺嘧啶 `T` 則判定為 DNA；含有尿嘧啶 `U` 則判定為 RNA）去載入對應的前綴圖片（`DNA-{Base}.png` 或 `RNA-{Base}.png`）。
*   **列印排版最佳化**：PDF 均以高解析度 **300 DPI** 輸出。垂直邊距 `margin_y` 設定為 `150` 像素，並將頁碼下移至 `PAGE_HEIGHT - 80` 像素，**完全避免頁碼與底部的核甘酸外框線重疊**。
*   **生物學轉譯驗證**：隨附序列驗證工具，可將 DNA 編碼股序列翻譯成氨基酸，並與野生型前胰島素原蛋白（UniProt P01308）進行完整比對。

---

## 📂 檔案結構

*   [generate_dna_rna.py](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py)：核心排版與 PDF 生成程式。主要函式包括：
    *   [load_nucleotide_images](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py#L43)：載入並轉換 RGBA 核苷酸圖片。
    *   [create_a4_page](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py#L112)：繪製單張 A4 頁面，處理縮放、轉置、格線、頁碼與邊距序號。
    *   [generate_scenario_1](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py#L196)：情境一（整張單一核苷酸）控制器。
    *   [generate_scenario_2](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py#L261)：情境二（雙股配對）控制器。
    *   [generate_scenario_3](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/generate_dna_rna.py#L313)：情境三（單股接續）控制器。
*   [verify_insulin.py](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/verify_insulin.py)：胰島素 DNA 序列轉譯與對比驗證腳本。
*   [insulin_sequence.txt](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/insulin_sequence.txt)︰已經過修正、格式化的人類胰島素（`INS`）完整基因編碼股序列 (DNA)。
*   [insulin_mrna_sequence.txt](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/insulin_mrna_sequence.txt)：轉換為 RNA 鹼基（含有尿嘧啶 `U`）的人類胰島素 mRNA 序列。
*   `DNA-A.png`, `DNA-T.png`, `DNA-C.png`, `DNA-G.png`：高解析度 DNA 核苷酸圖片素材。
*   `RNA-A.png`, `RNA-U.png`, `RNA-C.png`, `RNA-G.png`：高解析度 RNA 核苷酸圖片素材。

---

## 📦 系統需求

*   **Python 版本**：3.8 或以上。
*   **外部套件**：`Pillow` (PIL) 圖片處理程式庫。
    *   *安裝指令*：`pip install Pillow`

---

## 🛠️ 執行與操作說明

在專案目錄下打開終端機（如 Powershell），即可執行以下指令：

### 1. 互動式選單模式
不帶參數直接執行，將開啟中文的引導式互動選單：
```powershell
python generate_dna_rna.py
```

### 2. 執行情境一 (生成所有核苷酸整頁 PDF)
```powershell
python generate_dna_rna.py --mode 1
```
執行後會生成單張 PDF（如 [sheet_DNA-A.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/sheet_DNA-A.pdf)、[sheet_RNA-U.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/sheet_RNA-U.pdf)）與合併的多頁 PDF（[sheet_DNA_all.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/sheet_DNA_all.pdf) 及 [sheet_RNA_all.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/sheet_RNA_all.pdf)）。

### 3. 執行情境二 (自訂序列雙股配對 PDF)
傳入序列參數，產生雙股配對的 PDF 檔案：
```powershell
python generate_dna_rna.py --mode 2 --seq "ATCGATCGATCG" --output "dna_sequence_paired.pdf"
```

### 4. 執行情境三 (自訂序列單股接續 PDF)
傳入序列參數，產生單股依次接續排版的 PDF 檔案：
```powershell
python generate_dna_rna.py --mode 3 --seq "ATCGATCGATCG" --output "single_strand_sequence.pdf"
```

---

## 🧬 案例研究：人類胰島素（INS）基因
[insulin_sequence.txt](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/insulin_sequence.txt) 檔案中存放了經過修正與分段標註的人類前胰島素原（Preproinsulin）完整編碼股 DNA sequence（長度為 333 bp）。

你可以執行以下腳本，驗證此序列是否能 100% 正確轉譯出野生型蛋白質：
```powershell
python verify_insulin.py
```
本腳本將讀取該序列，進行密碼子翻譯，並與 UniProt 官方的野生型 [P01308](https://www.uniprot.org/uniprotkb/P01308/entry) 參考序列進行比對，以確保胰島素各片段序列均無缺失。

### 生成胰島素相關 PDF：
1. **生成 DNA 雙股配對 PDF**（情境二）：
   * 直接執行程式並選擇選項 `2`。
   * 當提示輸入序列時，直接按 **Enter** 鍵即可自動讀取 `insulin_sequence.txt`。
   * 會生成高解析度雙股配對的 [dna_sequence_paired.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/dna_sequence_paired.pdf)。
2. **生成 mRNA 單股連續 PDF**（情境三）：
   * 直接執行程式並選擇選項 `3`。
   * 當提示輸入序列時，直接按 **Enter** 鍵即可自動讀取對應的 `insulin_mrna_sequence.txt`（即將胸腺嘧啶 `T` 轉換為尿嘧啶 `U` 的 mRNA 序列）。
   * 會生成高解析度單股 mRNA 排版的 [insulin_mrna_single_strand.pdf](file:///C:/Users/user/Documents/GitHub/DNA-RNA-model/insulin_mrna_single_strand.pdf)。
