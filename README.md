# albirex

アルビレックス新潟およびアルビレックス新潟レディースの、2026/27シーズン向けオフ動向を整理するためのリポジトリです。

## CSV正本化とGitHub ActionsによるExcel/PDF生成運用

このリポジトリでは、`.xlsx` と `.pdf` を正本データにしません。正本データは `data/men/` と `data/ladies/` 配下のCSVです。既存の `.xlsx` ファイルが残っている場合でも、それらは正本データではありません。今後の正本データは `data/` 配下のCSVであり、Excel/PDFはGitHub Actionsで生成します。

Codex上では `.xlsx` と `.pdf` を生成・編集しません。`exports/*.xlsx` と `exports/*.pdf` はGit管理対象外です。ExcelとPDFは、AndroidスマホのGitHub画面から `Build Excel and PDF` ワークフローを実行したときにだけ生成し、Artifactからダウンロードします。

## 正本CSV

- `data/men/players.csv`
- `data/men/official_events.csv`
- `data/ladies/players.csv`
- `data/ladies/official_events.csv`

女子データはアルビレックス新潟レディース公式サイト確認ベースで一旦反映したものです。非公式情報や推測は入れないでください。公式サイトで確認できない情報は空欄、またはスマホ表示シート上で未発表扱いになるようにしてください。

## 生成されるファイル

GitHub Actions上で以下を生成し、Artifact `albirex-offseason-excel-and-pdf` に含めます。

- `exports/albirex_niigata_men_2026_27_offseason_print_mobile.xlsx`
- `exports/albirex_niigata_ladies_2026_27_offseason_print_mobile.xlsx`
- `exports/albirex_niigata_men_2026_27_offseason_print_mobile.pdf`
- `exports/albirex_niigata_ladies_2026_27_offseason_print_mobile.pdf`

## スマホ表示シート

印刷対象は `A:F` です。印刷対象列は以下の6列です。

1. 背番号
2. ポジション
3. 選手名
4. 動向
5. 発表日
6. その他備考

`G:J` 列は管理用情報（区分、移籍先/元、ステータス、出典URL）であり、印刷対象外です。公式発表がない選手は、動向・区分・ステータスを `未発表` として表示します。

同一選手に複数イベントがある場合は、発表日が新しいものを優先します。同日または日付不明の場合は、CSV上で後ろにある行を優先します。日付は `YYYY-MM-DD` 形式を基本とし、公式サイトの表記が異なる場合はCSV上で可能な範囲で正規化してください。

## Androidスマホでの運用手順

1. GitHub上で `data/men` または `data/ladies` のCSVを編集する。
2. 変更をCommitする。
3. GitHub Actionsが自動実行される。
4. 手動実行する場合は、`Actions` タブから `Build Excel and PDF` を選び、`Run workflow` を押す。
5. 実行完了後、該当Runを開く。
6. `Artifacts` の `albirex-offseason-excel-and-pdf` をダウンロードする。
7. ダウンロードしたzipを展開する。
8. 中のExcelファイルまたはPDFファイルをスマホで開く。

## 更新仕様

詳細な運用仕様は以下を参照してください。

- [アルビレックス公式発表オフ動向 更新仕様書](docs/offseason-update-spec.md)


## CSV正本化とGitHub ActionsによるExcel生成運用

このリポジトリでは、`.xlsx` ファイルを正本データにしません。Excelファイルはバイナリ形式のため、Codex上で生成・編集せず、Gitにもコミットしません。既存の `.xlsx` ファイルは参考資料として扱い、直接編集・上書きしないでください。

正本データは以下のCSVです。

- `data/men/players.csv`
- `data/men/official_events.csv`
- `data/ladies/players.csv`
- `data/ladies/official_events.csv`

Excelファイルは、CSVを入力としてGitHub Actionsの `Build Excel` ワークフローで生成します。生成されたExcelはGitHub ActionsのArtifactとして配布され、`exports/*.xlsx` はGit管理対象外です。ユーザーはAndroidスマホだけでCSV編集、ワークフロー実行、Artifactダウンロードまで完結できます。

### 生成されるExcelファイル

GitHub Actions上で以下のExcelファイルが生成され、Artifact `albirex-offseason-excel` に含まれます。

- `exports/albirex_niigata_men_2026_27_offseason_print_mobile.xlsx`
- `exports/albirex_niigata_ladies_2026_27_offseason_print_mobile.xlsx`

### Androidスマホでの運用手順

1. GitHub上で `data/men` または `data/ladies` のCSVを編集する。
2. 変更をCommitする。
3. CSV変更時はGitHub Actionsが自動実行される。
4. 手動実行する場合は、GitHubの `Actions` タブから `Build Excel` を選び、`Run workflow` を押す。
5. 実行完了後、該当Runを開く。
6. `Artifacts` の `albirex-offseason-excel` をダウンロードする。
7. ダウンロードしたzipを展開し、中のExcelファイルをスマホで開く。

### 運用上の注意

- Codex上では `.xlsx` ファイルを生成・編集しないでください。
- `.xlsx` ファイルをGitにコミットしないでください。
- Excel生成はGitHub Actions上で行ってください。
- データ更新はCSVで行ってください。
- `スマホ表示` シートでは、`F:I` 列は管理用情報であり印刷対象外です。
- `スマホ表示` シートの印刷範囲は `A:E` です。
