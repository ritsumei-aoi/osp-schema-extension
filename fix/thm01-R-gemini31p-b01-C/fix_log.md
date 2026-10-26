# 修正の実験 試行 1: thm01-R-gemini31p-b01-C

- 手順: runs/fix/PROTOCOL.md (v0.2、2026-10-11 夜に著者の了承)
- もとの run: runs/batch/thm01-R-gemini31p-b01-C (C、gemini-3.1-pro-low、agy 1.2.16)、最終コミット 4335d47、静的な目安 F2、予測 insufficient (R9)
- 写し: <home>/notebook/git/thm01-R-fix/thm01-R-gemini31p-b01-C (branch fix/thm01-R-gemini31p-b01-C、origin なし)
- Manager: <home>/notebook/git/thm01-R-fix/managers/thm01-R-gemini31p-b01-C、HOME <home>/notebook/git/thm01-R-fix/agy-home/manager-thm01-R-gemini31p-b01-C、Gemini 3.1 Pro (Low)、herdr ペイン w2:p13 (タブ fix-Manager)
- 記録: experiment/manifests/fix-thm01-R-gemini31p-b01-C.txt
- 枠 (開始前、10-11 夜): agy Gemini 週の残り 51%

## 段階 1 の事実 (書記の検算、写しの上で確認)
1. 課題の文面 (run.json turn 1) は「adjoint representation / up to scalar」の扱いの説明を求めるが、mathematical_proof.md に "scalar" は 0 回。gb のパリティ・κ の符号の約束も書かれていない (コード: gb は可換な Symbol (solve_triviality.py:28)、κ の係数は符号なし (85-91)、スカラーの項は 'scalar' / 'kappa_scalar' に入り使われない (59-61, 88-91))。
2. verification_artifacts.json: n=1 112×32、左零空間 84 → rank A 28。n=2 1356×176、1180 → 176 (未知数の数と同じ)。n=3 6516×528、5988 → 528 (同)。報告 (proof:29-31) に rank はない。参照 (spec) の rank A は 28 / 168 / 516 だが、正しい値なので**渡さない**。段階 1 では「検算されていない」ことだけを示す。段階 2 では n=2・3 で rank A が未知数の数に等しい (δf=0 となる 0 でない f がない) ことを、run 自身の数として示す。
3. 結論は全ての n について述べる (proof:34-35) が、根拠は n=1,2,3 だけで一般の n の議論はない。振り返り final_reflection.md:19 は "rigorously verify the condition generalized algebraically"。

- 著者の了承 (2026-10-11 22 時台 JST、番号 1): 段階 1 の文面 relay/M_facts1.txt をこのまま送る。

## 中継の記録
| # | UTC | ペイン | 文面 | sha256 先頭 8 | 照合 | Enter |
|---|---|---|---|---|---|---|
| 1 | 13:25 | w2:p13 | relay/M_launch.txt (入力のみ) | 423f8572 | 画面で確認 | 著者 |
| 2 | 13:33 | w2:p13 | relay/M_start.txt | dfba668b | 一致 (history.jsonl、末尾の改行を除く) | 著者 |
| 3 | 10-12 00:12 | w2:p13 | relay/M_facts1.txt (入力のみ、Enter は著者) | f3e35fc7 | 一致 (history.jsonl 00:13:06、末尾の改行を除く) | 著者 |
| 4 | 10-12 02:34 | w2:p13 | relay/M_facts2.txt (入力のみ、Enter は著者) | ef3f9f8c | 一致 (history.jsonl 02:34:52、末尾の改行を除く。画面では最後の語が枠に隠れていた) | 著者 |

## Manager の開始 (#2 の後)
- 「Ready」と 1 段落の要約を返した。読んだのは brief、memo、reference/ の 14 ファイルと写し。走らせたコマンドは python3 -c による os.listdir / os.walk の 3 回 (reference/ と写しのファイルの一覧)。どれも読むだけで、写しと Manager ディレクトリに変更はない (git status は空、写しの HEAD は 4335d47)。

## 段階 1: Manager memo 01 (起草)
- Part 1 と Part 2 を返し、memo に「Manager memo 01」(Stage: 1) を追記した。memo の差分は 26 行の追加だけで、削除はない。写しは変わっていない (HEAD 4335d47、status は空)。
- 事実 1〜3 はそれぞれ Part 2 の項目 1〜3 で扱われている。
- 事実にない記述 (書記が確かめた出どころ):
  - 項目 1 の「gb (parity 1)」は docs/math/C_inhomogeneous_definition.md:18 と :36 に書かれている。Worker が受け取った文書なので、外からの新しい数学ではない。
  - 項目 3 の「Either provide a rigorous theoretical proof ... or adjust the claims」は選択肢を示しているだけで、正しい値や結論は含まない。
- Manager が自分で見つけたこと (Part 1 だけにある): C_coboundary_definition.md:23-25 は「up to scalar」と書くが、solve_triviality.py:91 は kappa_scalar を捨てて完全一致を求めている。Part 2 では項目 1 の「up to scalar の扱いを説明せよ」として一般的に扱われ、行の番号は書かれていない。
- 空欄はない。
- Worker への文面: relay/W_stage1.txt (W_frame.txt + Part 2 から TYPE 行を除いたもの、sha256 5d538883)
- 枠 (起動前、10-12 00:2x UTC): 51%

## 段階 1: Worker (新しいセッション)
- 起動: 2026-10-12 00:31:01 UTC、終わり 00:34:30 (209 秒)。agy 1.3.3、gemini-3.1-pro-low。session 2971d66f-6e85-40b0-8425-3f468622c10c。ツールの呼び出し 46 回、エラー 0、ツールの外の参照 0。トークン: 入力 184,490、出力 12,582、キャッシュの読み 1,770,413。
- コミット 984808e (4 ファイル、+115 / −40): mathematical_proof.md、final_reflection.md、solve_triviality.py (+3、rank の出力)、verification_artifacts.json (+matrix_rank)。未追跡は __pycache__/ だけ。
- Worker は rank を一時的な python -c で計算し、JSON に手で書き入れた (ranks = {1: 28, 2: 176, 3: 528})。
- 書記の再実行 (scratchpad の複製、solve_triviality.py、137 秒): JSON は中身が一致 (鍵の順だけが違う)。rank 28 / 176 / 528、左零空間 84 / 1180 / 5988。

### 事実ごとの解消 (書記の確認)
1. 一部。up to scalar と規約は書かれた (proof §1.2)。しかし宣言はコードと合わない:
   - gb は parity 1 (奇の Grassmann 型) と宣言されたが、コードは可換な Symbol のまま (solve_triviality.py:28)。
   - κ u = (−1)^{p(u)} u κ と宣言されたが、κ の係数に符号はない (85-91、変更なし)。
   - up to scalar は「δf の 0 でない定数倍 c」と説明されたが、コードはスカラーの項 ('scalar' / 'kappa_scalar'、59-61・88-91) を式に使っていない (153-154 は ('kappa', Z) だけを読む)。
   → 宣言とコードの新しい食い違い。
2. 一部。rank は報告と JSON に書かれ、再実行でも出る。次元 (8/19/34、偶 4/11/22、奇 4/8/12) は docs/math/Cn1_definition.md:36-38 と一致する。しかし:
   - n=2・3 で rank = 未知数の数 (δf=0 となる 0 でない f がない) であることを §3.1 は「n≥2 では奇の微分はすべて内部」と読む。n=1 の 4 次元は「osp(2|2) で知られた外部の奇の微分」と読む。どちらも docs/math やコードからは導かれていない。
   - A が定義と合うかどうかの照合 (核の次元の妥当性) はされていない。
3. 解消。報告 §4 は n=1,2,3 に限り、一般の n は予想とした。振り返り :19 も直った。
- 新しい食い違い:
  - 上の 1 の宣言とコードの不一致
  - §3 の「right nullspace was computed directly」(コードは rank と左零空間だけを計算する、201・214)
  - osp(2|2) についての外からの記述
- 判定 (書記の記録、最終は著者): 段階 1 では直っていない → 段階 2 へ。

## 段階 2 の事実 (著者の了承: 番号 1、文面そのまま)
- relay/M_facts2.txt (sha256 ef3f9f8c)。上の 1・2 と新しい食い違いを場所つきで示す。参照の rank (28 / 168 / 516) は渡さない。示すのは run 自身の数 (rank = 未知数の数) と、核の次元が定義と合うか確かめられていないことだけ。

## 段階 2: Manager memo 02 (起草)
- memo の差分は 31 行の追加だけで、削除はない。写しは変わっていない (HEAD 984808e)。
- 事実 1〜4 はそれぞれ Part 2 の項目 1〜4 で扱われている。空欄はない。
- 事実にない記述: 項目 3 の「For an inner derivation f = ad_Z with odd Z ... check whether ... δ(ad_Z) = 0. If it does, ker(A) = 0 would contradict the existence of non-zero inner derivations」。
  - Part 1 の 3 (自分で見つけた問題) に、Manager 自身の推論として書かれている (「内部導分であれば ker(A) の次元は少なくとも dim(g_1) − dim(z_1)」)。
  - 内部導分 ad_Z の議論は docs/math と事実の文面のどちらにもない。brief の規則 4 (外からの新しい数学を足さない) に当たるかは著者の判断。
  - 参照の値そのもの (168 / 516) は書かれていない。
- Worker への文面 (案): relay/W_stage2.txt (W_frame + Part 2 から TYPE 行を除いたもの、sha256 7cda458b)

## 段階 2: Worker (段階 1 のセッションを resume)
- 起動 2026-10-12 02:44:36 UTC、終わり 02:49:24 (287 秒)。session 2971d66f (段階 1 と同じ)。ツールの呼び出し 29 回、エラー 0、ツールの外の参照 0。トークン: 入力 330,372、出力 29,822、キャッシュの読み 3,979,361。
- コミット 5999018: docs/issues/mathematical_proof.md だけを変えた (+33 / −26)。コードとデータは変えていない → 段階 1 の再実行の結果 (rank 28 / 176 / 528) がそのまま当てはまる。
- Worker のログに残っている一時的な検算 (コミットはされていない):
  - ad_Z (Z は奇の基底) を f として A に入れた。n=1 は 4 つとも A·vec = 0。n=2 は 8 つとも 0 にならず、0 でない式が 6〜10 本ある。
  - 直接の評価では a_p a_p のような基底にない項 (('a','p',0),('a','p',0)) が出た。

### 事実ごとの解消 (書記の確認)
1. 規約: 一部。報告は、コードのとおり gb を可換な Symbol とし、κ を符号のない形式的なラベルとして扱うと書き直した。宣言とコードは合った。しかし §1.2 の 1 は「gb·κ は奇のパリティ」と書いており、これは p(κ)=1 から p(gb)=0 を意味する。docs/math/C_inhomogeneous_definition.md:36 (gb は parity 1) とも、段階 1 の版の報告とも合わない。gb のパリティは明記されていない。
2. up to scalar とスカラーの項: 解消。'kappa_scalar' を除くことと、その理由 (随伴表現の値の部分だけで δf と比べる) を、コードのとおりに説明した。
3. rank と核: 未解消。
   - n=1 の核 4 次元は ad_Z (奇の Z) だと書いた (ログの A·vec = 0 と合う)。
   - n≥2 の核が 0 であることについては、「基底の並びと違う並びの項や、正規順序で出る g の外の中心の項のために、式が過剰に決まる」と説明した。しかし Worker 自身の検算では、n=2 で ad_Z が A の核に入らない。報告はこのことを書かず、A を直さないまま結論を保っている。
   - 核の次元が定義と合うかどうかは確かめられていない。むしろ合わないことを示すログがある。
4. 右の零空間の求め方: 解消。「直接計算した」を、rank 退化次数の定理による記述に直した。
- 結論: 「gb = 0 のときに限り自明」(変わらず)。この結論は odd-gb の読み方の結論と同じだが、根拠の A が n≥2 で内部導分を核に含まない (Worker 自身の検算)。そのため「データに一致」とは言えない。
- 新しい食い違い: 上の 1 (gb·κ のパリティの記述と docs の parity 1)。§3.1 の 2 の n≥2 の説明は、コードからもログからも裏付けられていない。
- 書記の記録 (最終は著者): 段階 2 でも直らなかった → **困難**。往復: Manager の起草 2、Worker への送信 2。
- 全体の差分 (4335d47..5999018): 4 ファイル +122 / −40 (docs 112/36、振り返り 1/1、src 3/0、data 6/3)、新しいファイル 0。
- 枠 (試行の後): agy Gemini 週の残り 50%。
