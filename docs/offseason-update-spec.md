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

女子データは公式サイト確認ベースで反映する。非公式情報や推測は入れない。個別記事URLが確認できる場合はNEWS一覧ではなく個別記事URLを出典URLに入れる。公式サイトで確認できない情報は空欄にし、公式発表が見つからない選手はスマホ表示シート上で未発表扱いにする。

スマホ表示シートの母集団は `players.csv` とする。`official_events.csv` は動向データであり、母集団ではない。`players.csv` に存在する選手は、`official_events.csv` に動向がなくてもスマホ表示シートに出力する。`official_events.csv` に動向がない場合は未発表として扱う。

背番号は `players.csv` を正本とする。スマホ表示シートA列には `players.csv` の背番号を出力する。`official_events.csv` には背番号を持たせない。背番号不明・未発表の場合は空欄を許容する。推測や非公式情報で背番号を補完しない。背番号不明時は `未確認` と入力せず、空欄にする。

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
- その他備考: `players.csv` のその他備考。ない場合は空欄
- 区分: 未発表
- ステータス: 未発表

同一選手に複数イベントがある場合は、発表日が新しいものを優先し、同日または日付不明ならCSV上で後ろの行を優先する。

## 色分け

スマホ表示シートでは、区分または動向に応じて行を色分けする。

- 契約更新: 薄い緑
- 加入、復帰、期限付き移籍加入、期限付き移籍延長: 薄い青
- 完全移籍、退団、契約満了、引退、レンタル中: 薄い橙
- 未発表: 薄い黄

## 区分マスタ

区分マスタとCSVの区分表記を一致させる。区分マスタは以下を必ず含める。

| 区分 | 分類 | 色 |
| --- | --- | --- |
| 契約更新 | 残留系 | 薄い緑 |
| 加入 | 加入系 | 薄い青 |
| 復帰 | 加入系 | 薄い青 |
| 期限付き移籍加入 | 加入系 | 薄い青 |
| 期限付き移籍延長 | 加入系 | 薄い青 |
| 完全移籍 | 退団系 | 薄い橙 |
| 退団 | 退団系 | 薄い橙 |
| 契約満了 | 退団系 | 薄い橙 |
| 引退 | 退団系 | 薄い橙 |
| レンタル中 | 退団系 | 薄い橙 |
| 未発表 | 未発表 | 薄い黄 |

## GitHub Actions仕様

Artifact名は `albirex-offseason-excel-and-pdf` とする。`Build Excel and PDF` ワークフローで以下を行う。

1. Pythonをセットアップする。
2. `openpyxl` をインストールする。
3. LibreOfficeをインストールする。
4. 日本語フォント `fonts-noto-cjk` をインストールする。
5. `scripts/build_workbook.py` を実行して `exports/*.xlsx` を生成する。
6. `scripts/export_pdf.sh` を実行して `exports/*.pdf` を生成する。
7. `exports/*.xlsx` と `exports/*.pdf` をArtifact `albirex-offseason-excel-and-pdf` としてアップロードする。

PDF変換では、PDF用一時Excelを作り、スマホ表示シート以外を削除してからLibreOffice headlessで変換する。管理用シートがPDFに混ざらないようにする。
