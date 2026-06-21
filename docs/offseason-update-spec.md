# アルビレックス公式発表オフ動向 更新仕様書

## 基本方針

- Excelファイルを正本にしない。
- PDFファイルを正本にしない。
- 正本は `data/men/` と `data/ladies/` 配下のCSVとする。
- Excel/PDFはGitHub Actionsで生成する。
- AndroidスマホだけでCSV更新、GitHub Actions実行、Artifactダウンロードまで運用できる構成にする。
- Codex上ではExcel/PDFを生成しない。`scripts/build_workbook.py` と `scripts/export_pdf.sh` もCodex上では実行しない。
- 既存xlsxは参考扱いであり、今後は正本として扱わない。

## CSV

### players.csv

列は以下に統一する。

```csv
背番号,ポジション,選手名,その他備考
```

### official_events.csv

列は以下に統一する。

```csv
選手名,動向,発表日,区分,移籍先元,ステータス,出典URL,その他備考
```

女子データはアルビレックス新潟レディース公式サイト確認ベースで反映する。非公式情報や推測は入れない。公式サイトで確認できない情報は空欄にし、公式発表が見つからない選手はスマホ表示シート上で未発表扱いになるようにする。

## スマホ表示シート

印刷対象は `A:F` とする。印刷対象列は以下の6列とする。

1. 背番号
2. ポジション
3. 選手名
4. 動向
5. 発表日
6. その他備考

`G:J` 列は管理用情報とする。

- G列: 区分
- H列: 移籍先/元
- I列: ステータス
- J列: 出典URL

G列以降は印刷対象外とする。PDFもスマホ表示シートの印刷設定を使い、A:Fのみが出力対象になるようにする。

## 未発表選手

公式発表がない選手は以下のように表示する。

- 動向: 未発表
- 発表日: 空欄
- その他備考: 空欄
- 区分: 未発表
- ステータス: 未発表

## 複数イベントの優先順位

同一選手に複数イベントがある場合は、発表日が新しいものを優先する。発表日が空欄または同一の場合は、CSV上で後ろにある行を優先する。日付は `YYYY-MM-DD` 形式を基本とする。

## GitHub Actions

`Build Excel and PDF` ワークフローで以下を行う。

1. リポジトリをcheckoutする。
2. Pythonをセットアップする。
3. `openpyxl` をインストールする。
4. LibreOfficeと日本語フォントをインストールする。
5. `python scripts/build_workbook.py` を実行してExcelを生成する。
6. `scripts/export_pdf.sh` を実行してPDFを生成する。
7. `exports/*.xlsx` と `exports/*.pdf` をArtifact `albirex-offseason-excel-and-pdf` としてアップロードする。

PDF変換では、PDF用一時Excelを作り、スマホ表示シート以外を削除してからLibreOffice headlessで変換する。
