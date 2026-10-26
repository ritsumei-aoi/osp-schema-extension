# 所要時間のまとめ (2026-10-07、書記)

元データ: `timing.csv` (バッチと 10 月の対話型の run、`timing.py`)、`timing_issues.csv` (条件 A の issue ごと)、`timing_may.csv` (5 月の run、記録からの抜き出し)。事実のみ。並列実行による遅れは考えない (著者、2026-10-07)。

## 定義

- **span**: 開始 (Worker への最初の人間の文面) から終了 (Worker・Worker のコミット・Manager のスナップショットの最後) まで。人間の待ち、休止、利用枠の待ちを全て含む。
- **active**: span から 30 分を超える空白 (夜の中断、枠の待ちなど) を除いたもの。
- **worker_busy**: 人間の文面から、次の人間の文面の前の Worker の最後の動作まで、の合計 (Worker が動いていた時間)。span − worker_busy は Manager・人間・書記の時間と休止。
- バッチ (自動): span = 実時間 (run.json の started〜finished)、worker_busy = 各ターンの秒数の合計 (差はほぼ 0)。

## 人間対応の run (条件 A / F−、10 月)

| run | 条件 | 期間 (JST) | span | active | Worker busy | 人間の入力 | 30 分超の空白 |
|---|---|---|---:|---:|---:|---:|---|
| luna-A | A1 | 10-03 01:24〜11:57 | 633 分 | 278 分 | 59 分 | 27 | 3 回 (191 分、131 分ほか) |
| luna-F | F− | 10-03 12:57〜19:13 | 376 分 | 319 分 | 50 分 | 25 | 1 回 (57 分) |
| sonnet46-A | A2 | 10-05 21:02〜10-06 08:57 | 715 分 | 311 分 | 134 分 | 24 | 3 回 (245 分ほか、夜) |
| sonnet46-F | F− | 10-06 09:17〜14:12 | 295 分 | 261 分 | 77 分 | 28 | 1 回 (34 分) |
| sonnet46-A1 | A1 | 10-06 21:19〜10-07 19:50 | 1351 分 | 280 分 | 120 分 | 28 | 5 回 (605 分 = Gemini の枠の待ち、332 分 = 夜ほか) |
| luna-A2 | A2 | 10-07 20:36〜23:19 | 163 分 | 163 分 | 56 分 | 24 | なし |

- 中断を除いた実働 (active) は 2.7〜5.3 時間。そのうち Worker が動いていた時間は 2〜4 割で、残りは Manager・人間 (書記) の時間。
- 人間の入力には、課題の開始の文面、Manager の起草文の送付、選択画面への定型文を含む。luna-A と luna-A2 の開始は、破棄したセッションを含む。
- issue ごと (`timing_issues.csv`): 長いのは人間の判断や事実の提示が入った issue (luna-A I05 251 分、sonnet46-A I03 164 分・I08 282 分 (夜を含む)、luna-A2 I05 約 28 分)。

## 自動実行 (バッチ、C / G−、10 月)

モデルと条件ごとの span の中央値 (除外の run を除く。単位は分):

| モデル | C | G− |
|---|---:|---:|
| Gemini 3.1 Pro | 5.5 (6 本) | 8.3 (5 本、最大 123) |
| Gemini 3.6 Flash | 8.2 (10) | 9.5 (5) |
| Gemini 3.7 Flash | 5.5 (10) | 10.3 (5) |
| Gemini 3.8 Flash | 9.2 (5) | 14.3 (5) |
| Haiku 4.5 | 4.3 (6) | 9.4 (5) |
| GPT-6 Luna | 1.7 (5) | 12.6 (5) |
| Opus 4.6 | 36.9 (5) | 27.8 (5) |
| Opus 4.7 / 4.8 / 5 | 10.4 / 29.1 / 20.4 | 24.4 / 26.8 / 30.2 |
| Opus 5.5 | 7.6 (5) | 15.9 (5) |
| Sonnet 4.6 | 18.0 (5) | 40.5 (5) |
| Sonnet 5.5 | 5.6 (5) | 13.8 (5) |

- 自動実行は 1 本あたり数分〜1 時間程度 (最長は gemini31p-b04-G の 123 分、1 ターン目が 120 分)。人間対応の run (active 2.7〜5.3 時間) との差は、Manager と人間の待ちが大きい。
- 10-02〜04 の対話型の C / G (luna、sonnet46 の各 3 本) も `timing.csv` にある。sonnet46 の C は出力上限での停止と再実行を挟むため span が 6 時間を超えるが、active は 23〜79 分。

## 5 月の run (`timing_may.csv`)

| run | 条件 | 最も良い全体の時間 | 出典 |
|---|---|---|---|
| thm01-01 / 02 / 03 (Gemini) | May-Iterative | Wall 51.5 時間 (3 本とも)、Agent Active 2h44m / 1h54m / 17m | gemini-cli の終了時の統計 (analysis/stats_group1.md) |
| thm01-04 (Sonnet 4.6)、05 (GPT-5.4) | May-Iterative | 11h46m、11h40m (Copilot の表示)、API 約 1h40m / 1h20m | stats_group2.md、保存された events.jsonl |
| thm01-X-01 / 02 / 03 (Gemini) | May-OneShot | Wall 3h33m / 1h36m / 54m、Active 12m / 5m / 1m | I_X0N_memo.md |
| thm01-X-04 (Sonnet 4.6) | May-OneShot | 4h37m (Copilot)、API 約 56 分 | I_X04_memo.md、events.jsonl |
| thm01-X-05 (GPT-5.4) | May-OneShot | 1h47m (セッションの記録)、API 約 21 分 | events.jsonl |
| thm01-X-06 (Opus 4.6、Antigravity) | May-OneShot | 記録なし | — |

- 5 月の Wall Time は人間の入力待ちを含む (Gemini の 3 本は複数日にまたがる)。5 月の Worker の自己申告の時間は、統計と食い違うものがある (X-01「約 3 分」に対し Wall 3h33m、Active 12m)。
- Gemini の 5 月の run は gemini-cli で動いている (inventory.csv の harness 欄は Copilot CLI と一括で書いているので注意)。

## 測れないもの

- 人間 (著者) が画面の前で使った時間そのもの (待ちと作業の区別はない)。
- Manager の応答時間の内訳 (agy の会話の記録から取れる可能性あり、未着手)。
