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

## Excel再構築スクリプト

仕様に沿ったシート構成へExcelファイルを再構築する場合は、依存パッケージを入れてから以下を実行します。

```bash
python3 -m pip install -r requirements.txt
python3 scripts/rebuild_workbooks.py
```

このスクリプトは、`スマホ表示` を5列の出力専用シートにし、`選手マスタ` と `オフ動向_入力` を正本シートとして再生成します。生成されたExcelは `exports/` 配下に出力されます。Excelはバイナリファイルのため、PRには含めずローカル生成物として扱います。
