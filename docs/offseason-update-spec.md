# オフシーズン更新仕様

## 基本方針

- Excelファイルを正本にしない。
- PDFファイルを正本にしない。
- 正本は `data/men/` と `data/ladies/` のCSVとする。
- Excel/PDFはGitHub Actionsで生成する。
- AndroidスマホだけでCSV編集、Actions実行、Artifact取得まで運用する。
- Codex上ではExcel/PDFを生成しない。
- 既存xlsxは参考扱いであり、今後は正本として扱わない。

## CSV仕様

### players.csv

対象は `data/men/players.csv` と `data/ladies/players.csv`。ヘッダーは必ず以下にする。

```csv
背番号,ポジション,選手名,その他備考
```

### official_events.csv

対象は `data/men/official_events.csv` と `data/ladies/official_events.csv`。ヘッダーは必ず以下にする。

```csv
選手名,動向,発表日,区分,移籍先元,ステータス,出典URL,その他備考
```

女子データは公式サイト確認ベースで反映する。非公式情報や推測は入れない。公式サイトで確認できない情報は空欄にし、公式発表が見つからない選手はスマホ表示シート上で未発表扱いにする。

## スマホ表示シート仕様

スマホ表示シートの列は以下にする。

- A列: 背番号
- B列: ポジション
- C列: 選手名
- D列: 動向
- E列: 発表日
- F列: その他備考
- G列: 区分
- H列: 移籍先/元
- I列: ステータス
- J列: 出典URL

印刷対象は `A:F` とする。印刷対象列は「背番号、ポジション、選手名、動向、発表日、その他備考」。`G:J` は管理用であり印刷対象外とする。

公式発表がない選手は以下の表示にする。

- 動向: 未発表
- 発表日: 空欄
- その他備考: 空欄
- 区分: 未発表
- ステータス: 未発表

同一選手に複数イベントがある場合は、発表日が新しいものを優先し、同日または日付不明ならCSV上で後ろの行を優先する。

## 色分け

スマホ表示シートでは、区分または動向に応じて行を色分けする。

- 契約更新: 薄い緑
- 加入、復帰、期限付き移籍加入、期限付き移籍延長: 薄い青
- 退団、契約満了、引退: 薄い橙
- 未発表: 薄い黄

## GitHub Actions仕様

`Build Excel and PDF` ワークフローで以下を行う。

1. Pythonをセットアップする。
2. `openpyxl` をインストールする。
3. LibreOfficeをインストールする。
4. 日本語フォント `fonts-noto-cjk` をインストールする。
5. `scripts/build_workbook.py` を実行して `exports/*.xlsx` を生成する。
6. `scripts/export_pdf.sh` を実行して `exports/*.pdf` を生成する。
7. `exports/*.xlsx` と `exports/*.pdf` をArtifact `albirex-offseason-excel-and-pdf` としてアップロードする。

PDF変換では、PDF用一時Excelを作り、スマホ表示シート以外を削除してからLibreOffice headlessで変換する。管理用シートがPDFに混ざらないようにする。
