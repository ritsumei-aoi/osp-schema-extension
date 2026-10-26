# 配布ファイルの書き換え (2026-10-08、書記、`kit_edits.py` → `kit_edits.csv`)

事実のみ。各 run の最終コミットの写しを、配布時の manifest (R の run) または init/setup コミット (5 月の run) と機械的に比べた。分類: reference (docs/math/*、handover/* の規則・スクリプト。notation.md と handover_memo_latest.md は作業ファイルとして除く)、template (振り返り・指標・issue のテンプレート)、config (pytest.ini、.gitignore、requirements.txt)、working (issue ファイルなど、編集が求められるもの)。

## reference の書き換え (153 run 中 6 run)

| run | 条件 | 書き換えたファイル (行の増減) |
|---|---|---|
| thm01-05 (GPT-5.4) | May-Iterative | docs/math/README.md (+9/−26) |
| thm01-R-luna-A2 | A2 | docs/math/C_inhomogeneous_definition.md (+10/−2)、docs/math/Cn1_definition.md (+2/−1)、handover/scripts/submit_correction.sh (+1/−1) |
| thm01-R-luna-b02-G | G− | docs/math/C_inhomogeneous_definition.md (+6/−1) |
| thm01-R-luna-b06-G | G− | 同 (+9/−0) |
| thm01-R-luna-b08-G | G− | 同 (+5/−1) |
| thm01-R-luna-b10-G | G− | 同 (+10/−2) |

- 定義文書の書き換えは **Luna (GPT-6 Luna) に集中**: バッチの G− 5 本中 4 本と luna-A2。いずれも C_inhomogeneous_definition.md の Parity Note (gb のパリティ) の箇所で、b02 は「Parity consistency correction ... this schema uses even gb parameters」と文書の記述を誤りとして書き換え、b06 は「Consistency caveat」を追記。Luna の C (定義を読むだけの条件) の 5 本、luna-A、luna-F、luna-G (対話型)、luna-r2/r3-G では reference の書き換えはない。
- 他のモデル (Gemini 4 系統、Haiku、Opus 各版、Sonnet 4.6 / 5.5) は reference を書き換えていない (5 月の thm01-05 の README を除く)。

## template・config

- template を書き換えた (テンプレートを写さずにその場で埋めた、または消した) run: C 5 本 (gemini31p-b01 は 2 つとも削除、gemini31p-b09、gemini36f-b09、opus46-b09、sonnet55-b09) と 5 月の OneShot 3 本 (X-02、X-04、X-06)。
- config の変更: G− 16 本。pytest.ini に 1〜2 行追加 15 本 (Gemini Flash 系 12、luna-b04-G、対話型の luna-G と luna-r3-G)、opus48-b02-G は .gitignore に 3 行追加。

## 関連

- luna-A2 の書き換えはいずれも最後の承認の後または修正の作業中で、Manager に見る機会はほぼなかった (runs/thm01-R-luna-A2/run_log.md)。
