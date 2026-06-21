# albirex

アルビレックス新潟およびアルビレックス新潟レディースの、2026/27シーズン向けオフ動向を整理するためのリポジトリです。

## 現在の主なファイル

- `albirex_niigata_men_2026_27_offseason_print_mobile.xlsx`
  - アルビレックス新潟 男子トップチームの選手一覧・契約更新・移籍・レンタル情報を整理したExcelファイルです。
- `albirex_niigata_ladies_2026_27_offseason_print_mobile.xlsx`
  - アルビレックス新潟レディースの選手一覧・契約更新・退団・復帰情報を整理したExcelファイルです。

## 更新仕様

重複入力を減らし、公式サイトの情報を逐次更新してスマホ用一覧へまとめるための推奨仕様は、以下を参照してください。

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
