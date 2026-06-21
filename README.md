# Albirex Niigata Offseason CSV Source

このリポジトリは、アルビレックス新潟（男子）とアルビレックス新潟レディース（女子）のオフシーズン動向を、Androidスマホだけで更新・生成・取得できるようにするためのCSV正本リポジトリです。

## 最重要方針

- このリポジトリでは `.xlsx` と `.pdf` を正本データにしません。
- 正本データは `data/men/` と `data/ladies/` のCSVです。
- ExcelとPDFはGitHub Actionsで生成します。
- Codex上では `.xlsx` と `.pdf` を生成・編集しません。
- `exports/*.xlsx` と `exports/*.pdf` はGit管理対象外です。
- 生成物はGitHub ActionsのArtifact `albirex-offseason-excel-and-pdf` からダウンロードします。

## データ構成

- `data/men/players.csv`: 男子の選手マスタ。ヘッダーは `背番号,ポジション,選手名,その他備考` です。
- `data/men/official_events.csv`: 男子の公式発表ベースの動向。ヘッダーは `選手名,動向,発表日,区分,移籍先元,ステータス,出典URL,その他備考` です。
- `data/ladies/players.csv`: 女子の選手マスタ。公式サイト確認ベースで一旦反映します。
- `data/ladies/official_events.csv`: 女子の公式発表ベースの動向。非公式情報や推測は入れません。

女子データはアルビレックス新潟レディース公式サイト確認ベースで一旦反映しています。公式ニュースで確認できない選手動向は推測で補完せず、スマホ表示シート上で未発表扱いになるようにします。

スマホ表示シートの表示対象は `players.csv` の選手マスタ全員です。`official_events.csv` は動向データであり、表示対象選手の母集団ではありません。`official_events.csv` に動向がない選手も、`players.csv` に存在する限りスマホ表示シートに出力されます。その場合、動向は `未発表` と表示されます。

背番号は `data/*/players.csv` を正本とします。スマホ表示シートのA列には `players.csv` の背番号が反映されます。公式サイトで背番号が確認できない選手は、背番号を空欄のままにします。推測や非公式情報による背番号補完は行いません。背番号不明時は `未確認` と入力せず、空欄にします。

一部選手については、公式サイトで背番号を確認できなかったため、背番号欄を空欄にしています。

## GitHub Actions生成物

`Build Excel and PDF` ワークフローで以下を生成し、Artifact `albirex-offseason-excel-and-pdf` に含めます。

- 男子用Excel
- 女子用Excel
- 男子用PDF
- 女子用PDF

ワークフローではPython、`openpyxl`、LibreOffice、日本語フォント `fonts-noto-cjk` をセットアップし、GitHub Actions上でのみ `python scripts/build_workbook.py` と `scripts/export_pdf.sh` を実行します。

## スマホ表示シート

スマホ表示シートの印刷対象は `A:F` です。印刷対象列は以下です。

1. 背番号
2. ポジション
3. 選手名
4. 動向
5. 発表日
6. その他備考

`G:J` 列は管理用情報であり印刷対象外です。

- G列: 区分
- H列: 移籍先/元
- I列: ステータス
- J列: 出典URL

公式発表がない選手は、動向、区分、ステータスを `未発表` と表示します。以前のような `―` は使いません。 その他備考は `players.csv` のその他備考を表示し、備考がない場合は空欄にします。

同一選手に複数イベントがある場合は、発表日が新しいものを優先し、同日または日付不明ならCSV上で後ろの行を優先します。

## 区分と色分け

区分は区分マスタに存在する値を使います。

- 契約更新: 薄い緑
- 加入、復帰、期限付き移籍加入、期限付き移籍延長: 薄い青
- 完全移籍、退団、契約満了、引退、レンタル中: 薄い橙
- 未発表: 薄い黄

## CSV更新時のデータ品質チェック

- `players.csv` の選手名と `official_events.csv` の選手名は完全一致させる。
- 同じ選手に複数イベントを入れる場合、発表日が新しい行が優先される。
- 発表日が同じ、または空欄の場合はCSV上で後ろにある行が優先される。
- 区分は区分マスタに存在する値を使う。
- 区分が未定の場合は `未発表` を使う。
- 公式確認できない情報は入れない。

## Androidスマホでの運用手順

1. Codexにプロンプトを投げ、公式サイトを確認してCSVを更新する。
2. 更新された `data/men` または `data/ladies` のCSVを確認する。
3. CSVの変更をCommitし、pushする。
4. CSVのpushをトリガーに、GitHub Actionsの `Build Excel and PDF` が自動実行される。
5. または `Actions` タブから `Build Excel and PDF` を選び、`Run workflow` を押して手動実行する。
6. 実行完了後、該当Runを開く。
7. `Artifacts` の `albirex-offseason-excel-and-pdf` をダウンロードする。
8. ダウンロードしたzipをAndroidスマホ上で展開する。
9. 中のExcelファイルまたはPDFファイルをスマホで開く。

## Codexでの作業ルール

Codexが作成・修正するのは、CSV、Pythonスクリプト、shellスクリプト、GitHub Actions workflow、README、仕様書、`.gitignore` などのテキストファイルだけです。Codex上でExcel/PDF生成スクリプトを実行してはいけません。

## 日次公式サイト確認運用

CSV更新はGitHub Actionsでは実行しません。CSV更新はCodexへの日次プロンプトで行います。1日1回、利用者がCodexにプロンプトを投げ、Codexが公式サイトを確認してCSVを更新する運用です。

- CSVはこのリポジトリの正本データです。
- Codexは公式サイトだけを確認し、契約更新、加入、復帰、期限付き移籍加入、期限付き移籍延長、完全移籍、退団、契約満了、引退、レンタル中などの公式発表が確認できた場合だけCSVへ反映します。
- 非公式サイト、SNS、掲示板、まとめサイト、推測情報はCSVへ反映しません。
- 公式サイト取得不可または解析不可の場合は既存CSVを維持し、推測で追加・削除・上書きしません。
- 更新済みCSVをpushすると、GitHub Actionsの `Build Excel and PDF` がCSVを元に決まった書式でExcel/PDFを生成し、Artifactとして出力します。
- GitHub Actionsは公式サイトを確認せず、CSV更新も行いません。
- schedule付きの `Daily CSV Update` workflowは作成せず、GitHub Actionsによる日次自動CSV更新は行いません。
- `scripts/update_official_csv.py`、`scripts/official_sources.py`、`scripts/csv_utils.py` は将来の自動化検討用または補助スクリプトです。現時点の正式運用では未使用であり、GitHub Actionsから実行しません。

### Androidスマホから日次更新する

1. Codexにプロンプトを投げ、公式サイト確認とCSV更新を依頼する。
2. Codexが更新したCSVの内容を確認する。
3. CSVの変更をCommitし、pushする。
4. CSVのpushをトリガーに `Build Excel and PDF` が実行される。
5. 実行後、`Build Excel and PDF` のRunを開く。
6. `Artifacts` の `albirex-offseason-excel-and-pdf` をダウンロードする。
7. Artifactはzip形式なので、Androidスマホでzipを展開してからExcelまたはPDFを開く。
