# 修正の実験 (§9.30) の手順 — v0.2 (2026-10-11 夜、ipsj-revision-fix)

状態: **著者の了承 (2026-10-11 22 時台 JST): §9 の 1〜4 をすべて推奨どおり採用し、試行 1 から始める。** 設計書へ移す提案は `PROPOSALS.md` (設計書は ① の持ち物)。

実装: `scripts/fix_setup.sh` (写し・Manager ディレクトリ・HOME・manifest)、`scripts/fix_run.py` (Worker への 1 通)、`kit/FIX_MANAGER_BRIEF.md`、`W_frame.txt` (Worker への固定の枠)。試行ごとの記録は `<run>/fix_log.md` と `<run>/relay/`。

## 0. 決まっていること (設計書 §9.30、§9.39、§9.45、§9.46)
- 目的: 不十分な run の成果物が「人間が出す水準の事実だけの指示」でどれだけ直しやすいかを測る。正しさの判定 (§9.31) の代わりにはしない。
- 手順は条件によらず同じ: 最終コミットの写し → 書記が事実の文面 (段階 1 一般 / 段階 2 場所。正しい値は渡さない) → Manager (Gemini 3.1 Pro (Low) 固定) が CORRECTION を起草 → 同じモデル・もとの run と同じツールの**新しい Worker セッション**に 1 通。
- Manager の起草は直さない。Manager 自身はコードを直さない (意味 2 は採らない)。Manager が事実を指示に反映したかも記録する。
- 対象外: 提供が終わったモデルの run (5 月の Gemini 3 Flash / 3.1 Flash-lite / GPT-5.4)。代わりのモデルでは直さない。
- Gemini 3.1 Pro、3.6 / 3.7 Flash は提供終了の予告あり → これらに関わる試行を先に行う。Manager は全試行で 1 つのモデル (§9.39)。

## 1. 試行の対象 (8 本、案) — `candidates.tsv`
選び方: 不十分 (author の判定は未着手なので、judgments.csv の prior か predicted) の最終コミットを、静的な目安で F1 / F2 / F3 に分け、G と C、モデルの系統を混ぜる。静的な目安は 10-07 の試算 (セッション 5f641591) のスクリプトを今の材料で再計算した (73 本: F1 51 / F2 18 / F3 4。10-08 以降の新しい run は judgments.csv に未収録のため入っていない)。
- F1 = 計算のコードあり・再実行可・n を扱う・構造化 (lie_sc と def_gamma)・γ の 8 割以上が参照と一致
- F2 = コードはあるが上のどれかを欠く
- F3 = 計算のコードがない、または γ の一致が半分未満

| # | run | 条件 | 目安 | モデル (Worker の道具) | 不十分の主な中身 (facts / facts2 より) |
|---|---|---|---|---|---|
| 1 | thm01-R-gemini31p-b01-C | C | F2 | Gemini 3.1 Pro Low (agy) | 「up to scalar」の扱いの説明なし、rank A が参照 (168 / 516) と違う、一般の n の議論なし |
| 2 | thm01-R-gemini36f-b13-C | C | F2 | Gemini 3.6 Flash Medium (agy) | 根拠のない f(Z0)=0、未評価の項を残して結論、JSON の鍵の名前と中身が違う |
| 3 | thm01-R-gemini38f-b01-C | C | F1 | Gemini 3.8 Flash Medium (agy) | 宣言した gb のパリティとコードの扱いが食い違う |
| 4 | thm01-R-opus55-b09-C | C | F1 | Claude Opus 5.5 (Claude Code -p) | 検定が方向ごとだけ、報告の成果物のパスが実物と違う |
| 5 | thm01-R-opus55-b08-G | G | F1 | Claude Opus 5.5 (Claude Code -p) | 検定が方向ごと + 符号の型だけ、結論が K の読み方に依存、振り返りの自己申告の食い違い |
| 6 | thm01-R-sonnet46-b11-G | G | F2 | Claude Sonnet 4.6 (Claude Code -p) | γ 39/50、全体の行簡約が未コミットのスクリプトだけ |
| 7 | thm01-R-sonnet46-b04-G | G | F3 | Claude Sonnet 4.6 (Claude Code -p) | γ 16/50、制約の数え方の誤り (13 本の「独立」な式)、H^1 の値の自己矛盾 |
| 8 | thm01-R-haiku45-b06-G | G | F3 | Claude Haiku 4.5 (Claude Code -p) | γ 0/50、f=0 だけで非自明と結論 |

- 内訳: C 4 / G 4、F1 3 / F2 3 / F3 2、Gemini 3 / Claude 5。Luna は G / C の不十分に入らないので無し。
- 順: 1 → 2 (提供終了の予告) → 3 → 4〜8。
- 8 本ともバッチの run (`runs/batch/`) なので、Worker の道具は batch_run.py と同じ非対話の起動 (Claude Code 2.1.288 `-p` / agy) にそろう。人間対応の G / C (sonnet46-r3-C など) は今回は入れない (入れるなら Claude Code 2.1.288 の対話で herdr の中継)。
- 道具の版: Claude Code はもとと同じ 2.1.288 (`~/.local/share/claude/versions/` にあることを 10-11 夜に確認)。agy はもとの 1.2.16 / 1.2.17 が残っておらず今の版 (1.3.x) になる → 記録に版を書き、論文では注記する。対象のモデルは 10-11 夜の `agy models` ですべて利用可。
- 8 本のブランチと最終コミットが `thm01-R-batch-remote.git` にあることを 10-11 夜に確認。

## 2. 作業場所の写し
- もとの作業場所 `<home>/notebook/git/thm01-R-batch/<run>` は触らない。`<home>/notebook/git/thm01-R-batch-remote.git` の `study/thm01-R-<TAG>-<COND>` を、judgments.csv の最終コミット (sheet.csv の `commit`) で `<home>/notebook/git/thm01-R-fix/<run>/` に clone し、ブランチ `fix/<run>` を作る。origin は外す (push しない。Worker が push を試みても失敗するだけ)。
- 未追跡だったファイル (inventory.csv の uncommitted) は写さない (最終コミットだけが成果物)。
- 写しの作り方・基のコミット・sha は `experiment/manifests/fix-<run>.txt` に記録する。
- agy の Worker は run ごとの新しい HOME (`<home>/notebook/git/thm01-R-fix/agy-home/<run>`、batch と同じ settings.json の許可)、Claude Code の Worker は新しい設定ディレクトリ `<home>/notebook/git/thm01-R-claude-config/fix` (batch の写し、ログイン情報は写さない → 著者の /login が 1 回要る)。

## 3. Manager (Gemini 3.1 Pro (Low)、agy の対話、herdr の中継)
- Manager ディレクトリは試行ごとに新しく `<home>/notebook/git/thm01-R-fix/managers/<run>/` (git init は scribe 名義)。HOME は `manager_home.sh` と同じ作り方で `<home>/notebook/git/thm01-R-fix/agy-home/manager-<run>`、model を "Gemini 3.1 Pro (Low)" に直す。
- `reference/` は A の Manager と同じもの (Worker が受け取った文書。C の run なら C の配布物、G なら G の配布物)。
- MANAGER_BRIEF: 既存の brief は issue ごとの審査のための文書で、修正の実験には合わない。修正の実験用の短い brief (`kit/FIX_MANAGER_BRIEF.md`、案は別ファイル) を使う。要点: 役割は「人間が示した事実をもとに CORRECTION を起草する」だけ / 写しは読むだけ / 事実にない新しい数学や正しい値を足さない / 出力は Part 1 (日本語の確認) と Part 2 (英語の CORRECTION、1 つのコードブロック) / memo は append only。
- 中継: §9.46 と同じ (書記が send-text で入力、Enter は著者)。人間の memo には送った文面だけを書く。
- Manager の起草に空欄や判断の要る点があれば著者に示す (前例どおり、起草は直さない。事実を示して起草し直させるかは著者)。

## 4. 事実の文面 (書記が作る)
- 材料: judging/facts、facts2、sheet.csv、g_summary、gcheck (参照モデル)。書記の検算で確かめた事実だけを使う。
- **段階 1 (一般)**: 食い違いの種類だけ。例「γ の値を定義から確かめよ」「検定が個々の方向だけで、すべての組み合わせを調べていない」「報告の記述と、コミットされたファイルが合わない箇所がある」。
- **段階 2 (場所)**: 食い違うファイル・行・項目を示す。正しい値・正しい結論・参照の数 (rank の参照値など) は渡さない。
- 読み方 (gb のパリティ、κ の符号、K の扱い) は 10-03 の基準ではどれも認めるので、読み方そのものは誤りとして示さない。示すのは「宣言とコードの食い違い」「宣言がない」など事実だけ。
- 文面は `runs/fix/<run>/facts_stage1.md`、`facts_stage2.md` に保存し、送る前に著者の了承を得る (事実を示すかどうかは著者の判断の範囲)。

## 5. Worker への 1 通
- 新しいセッションに、固定の枠 + Manager の CORRECTION (TYPE 行を除く) を 1 通で送る。固定の枠の案 (英語):

```
A reviewer has examined the work in this repository and found problems.
The correction below lists them. Read it, fix the work in this repository accordingly,
and commit your changes with git when you are done. Do not push.

----- CORRECTION -----
<Manager の Part 2、TYPE 行を除く>
----- END CORRECTION -----
```

- 送り方 (案): もとの run が非対話 (batch) なので、Worker も batch_run.py と同じ非対話の起動で 1 回だけ動かす (`runs/fix/scripts/fix_run.py`。batch_run.py の run_turn_claude / run_turn_agy を読み込んで使う。固定返答・再開は**しない**)。起動は著者の「k」の後に書記が行う。
- 段階 1 で直らなければ、段階 2 の事実 → Manager の新しい起草 → **同じ Worker セッションを resume** して 1 通 (A の訂正の前例と同じく、往復として数える)。段階 2 の後は終わり。

## 6. 成功の判定 (判定の前に固める)
- 各試行で、示した事実ごとに「解消 / 一部 / 未解消 / 悪化」を書記が記録 (再実行、gcheck の照合、facts の項目の再確認)。
- **直った**: 示した事実がすべて解消し、新しい食い違いが入らず、結論が認められる読み方 (§9.31) のどれかとデータに一致する。
- 結果の段: 段階 1 で直った = 容易 / 段階 2 で直った = 中程度 / 直らなかった = 困難。
- 最終の判定は著者 (判定の材料として ③ に渡す)。静的な目安 (F1/F2/F3) と段の対応を見る。

## 7. 測る量 (run ごとに `runs/fix/<run>/fix_log.md` と `runs/fix/results.tsv`)
- 段 (容易 / 中程度 / 困難)、事実ごとの解消
- 往復の数 (Manager の起草の数、Worker への送信の数)
- 差分の量 (`git diff --stat <base>..<final>`、src / data / docs 別の行数、新しいファイル数)
- 時間 (Worker の各ターンの秒、Manager の作業時間) と資源 (Worker のトークン・定価換算、agy の枠の消費)
- Manager の起草が事実をすべて反映したか、事実にないこと (正しい値、新しい数学) を足したか
- 参考: 拒否・ツール外の参照 (batch と同じ集計)

## 8. 枠と日程
- agy Gemini の週の残り 51% (10-11 夜、10-14 18:40 JST に戻る)。Manager は 1 試行で 1〜2% の見込み (sonnet46-r3-A1 の 1 run 全体で約 2%)。Gemini Worker の 3 本も各 1〜3%。始める前と各試行の後に `agy_min_remaining.sh` で確かめ、残りが 20% を切ったら止めて著者に示す。
- データ収集は 10/18 まで (§9.8)。1 試行あたり 1〜2 時間 (中継を含む) の見込みで、10-12〜10-15 に 8 本。

## 9. 著者の決定 (2026-10-11 22 時台、すべて推奨どおり)
1. 8 本の選び方 (上の表)
2. Worker を非対話の起動で動かすこと (Enter の承認は Manager への入力と、Worker を起動する前の「k」)
3. 修正の実験用の短い MANAGER_BRIEF を使うこと
4. 成功の判定と段の定義 (§6)
5. (2026-10-12 04 時台 UTC、著者の言葉「Manager に提案するものは一貫性を持ってそちらの推奨する方針で進めていますので，以後の作業もそちらでそのまま進めてもらって構いません．(Enterを押しても良い)ただし，新しいManagerの起動についてはこちらで行います．」) 以後、書記は推奨の選択肢で進め、Manager への文面 (開始・事実) の Enter も送ってよい。Worker の起動も推奨どおりなら書記が行う。文面の全文、照合、選んだ選択肢は記録と会話に残す。推奨が前例から決まらないとき、手順にない事態のときは止めて著者に伺う。**新しい Manager の起動 (新しい HOME の最初の設定の画面を含む) は著者が行う** (P3 の「起動コマンドは書記が Enter まで」はこれで置き換わる)。
6. (2026-10-12 04:53 UTC、著者の言葉「今回のManagerの操作が全て終わったら，`/exit` をEnterと共に入力して次の起動をして構いません．その後の初回操作はこちらで行います．」) 試行の Manager の仕事が終わったら、書記が `/exit` と Enter で終了させ、次の試行の起動コマンドを入力して Enter まで送ってよい。新しい HOME の最初の設定の画面は著者が操作する。
