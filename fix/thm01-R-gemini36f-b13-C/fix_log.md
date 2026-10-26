# 修正の実験 試行 2: thm01-R-gemini36f-b13-C

- 手順: runs/fix/PROTOCOL.md (v0.2)
- もとの run: runs/batch/thm01-R-gemini36f-b13-C (C、Gemini 3.6 Flash)、最終コミット 920d772、静的な目安 F2、予測 insufficient
- 写し: <home>/notebook/git/thm01-R-fix/thm01-R-gemini36f-b13-C (branch fix/thm01-R-gemini36f-b13-C、origin なし)
- Manager: <home>/notebook/git/thm01-R-fix/managers/thm01-R-gemini36f-b13-C、HOME <home>/notebook/git/thm01-R-fix/agy-home/manager-thm01-R-gemini36f-b13-C、Gemini 3.1 Pro (Low)、herdr ペイン w2:p13 (タブ fix-Manager。試行 1 の Manager は著者が終了させた)
- 記録: experiment/manifests/fix-thm01-R-gemini36f-b13-C.txt
- 枠 (開始前): agy Gemini 週の残り 50%

## 書記の検算 (写しの上、judging/facts と facts2 の b13 final を確かめた)
- 再実行 (scratchpad の複製): Rank(M_f) 28 / 168 / 516、'Rank([M_f | M_gb])' 4 / 8 / 12、左零空間 84 / 1232 / 6444、gb の制約の rank 4 / 8 / 12、自明な gb の空間 0。もとの出力と一致。
- 報告 Theorem 1 (proof:14-18) は全ての n について述べる。§4 の解析的な証明は次のとおり:
  - :85 の「f(Z_0) = 0 (from Z_0-invariance of f)」は docs/math (f は任意の奇の写像、C_coboundary_definition.md:7-11) にもなく、報告でも導かれていない。コードでは f(Z_0) は自由 (solve_triviality.py:217-221)。
  - :101 は −f([F_1,F_2]_0) を評価しないまま残し、:110-111 で結論する。
  - :78 の文は完結していない。
- solve_triviality.py:303 の `M_f_mat.hstack(M_gb_mat)` は sympy の classmethod の呼び出しなので M_gb_mat だけを返す (書記の確認: 形 (3,1))。:307 は「Rank([M_f | M_gb])」と出力し、JSON の 'rank_aug' (4/8/12) は M_gb だけの rank。
- 規約: 報告は κ が奇であることだけを書き (:36)、gb のパリティは書かない。κ の符号はコードに現れない (γ は手で書かれている、126-208)。スカラーの項は「identity terms vanish」(:54) で除いている。
- 結論「gb = 0 のときに限り自明」。odd-gb の読み方の結論と同じ。

## 段階 1 の事実 (著者の了承: 番号 1、文面そのまま): relay/M_facts1.txt (sha256 0d1b3696)
1. Theorem 1 は全ての n について述べるが、§4 の証明は完結していない (根拠のない f についての仮定、評価されていない項)。計算は n=1,2,3 だけ。
2. コードが出力して JSON に記録する量のうち、名前と中身が違うものがある。
3. 規約 (gb のパリティ、κ の符号の規則) が書かれていない。

## 中継の記録
| # | UTC | ペイン | 文面 | sha256 先頭 8 | 照合 | Enter |
|---|---|---|---|---|---|---|
| 1 | 03:02:13 | w2:p13 | relay/M_launch.txt (起動。著者の許可により書記が Enter まで送った。最初の設定の画面は著者が操作した) | eddb3c5f | 画面で確認 | 書記 (P3) |
| 2 | 03:06:15 | w2:p13 | relay/M_start.txt (入力のみ) | e987b144 | 一致 (history.jsonl 03:06:18、末尾の改行を除く) | 著者 |
| 3 | 03:48:34 | w2:p13 | relay/M_facts1.txt (入力のみ、Enter は著者) | 0d1b3696 | 一致 (history.jsonl 03:48:53、末尾の改行を除く) | 著者 |
| 4 | 04:25:33 | w2:p13 | relay/M_facts2.txt (入力のみ、Enter は著者) | b434c33a | 一致 (history.jsonl 04:25:45、末尾の改行を除く) | 著者 |

## Manager の開始 (#2 の後)
- 「Ready」と要約を返した。走らせたコマンドは find (reference/ と写しの一覧) と git -C <写し> log --oneline で、どれも読むだけ。写しと Manager ディレクトリの status は空。

## 段階 1: Manager memo 01 (起草)
- memo の差分は 49 行の追加だけで、削除はない。写しは変わっていない。Manager が新しく走らせたのは `git -C <写し> log -p -n 2` (読むだけ)。
- memo の Active Manager Model の欄は「Gemini 3.1 Pro」で、(Low) が書かれていない。
- 事実 1〜3 はそれぞれ Part 2 の項目 1〜3 で扱われている。空欄はない。
- 起草は場所を具体的に書いている (行 85、101、304-308、332)。段階 1 の事実は種類だけだったが、Manager が自分で場所を特定した。
- 事実にない記述:
  - 項目 2 の「augmented matrix の rank は Rank(M_f) より小さくなり得ない。4/8/12 は dim(gb) か P_cokernel M_gb の rank に当たる」は Manager の推論。実際の原因 (hstack が M_gb だけを返す) は書かれていない。正しい値は含まない。
  - 項目 3 の「docs/math/C_inhomogeneous_definition.md noting parity 1」は docs/math (:36) から。
- Manager が自分で見つけたこと: 項目 4「proof:136, 143, 144 のリンクが外の存在しないパス (<home>/notebook/git/thm01-R-batch/...) を指す」。行は正しい。ただしそのパス (もとの作業場所) はこの機械に存在する。「non-existent」は事実と違う。
- Worker への文面: relay/W_stage1.txt (sha256 41fd17d1)
- 枠 (起動前): 50%

## 段階 1: Worker (新しいセッション)
- 起動 2026-10-12 03:59:59 UTC、終わり 04:06:55 (415 秒)。agy 1.3.3、gemini-3.6-flash-medium。ツールの呼び出し 72 回、エラー 0、ツールの外の参照 0。トークン: 入力 300,632、出力 26,099、キャッシュの読み 3,043,837。
- もとの作業場所 (thm01-R-batch/thm01-R-gemini36f-b13-C) の 12 ファイルの sha256 は起動の前後で同じで、HEAD も 920d772 のまま。
- コミット 46774ac (3 ファイル、+110 / −87): mathematical_proof.md、solve_triviality.py (`sp.Matrix.hstack(M_f_mat, M_gb_mat)` に直し、rank_gb_constraints を追加)、verification_results.json。
- 書記の再実行 (複製): Rank(M_f) 28 / 168 / 516、Rank([M_f|M_gb]) 32 / 176 / 528、gb の制約の rank 4 / 8 / 12、自明な gb 0。JSON はバイトまで一致。

### 事実ごとの解消 (書記の確認)
1. 証明と範囲: 解消。Theorem 1 は n=1,2,3 に限り、一般の n は Conjecture 1。f(Z_0)=0 の仮定を外した (内部導分を理由に、§4.1 の 1)。−f([F_1,F_2]_0) を評価した (§4.1 の 3)。§4.2 は「仕組み」の説明で、結論は計算に頼っている。
2. 名前と中身: 解消。rank_aug は augmented matrix の rank になった (32/176/528)。gb の制約の rank は rank_gb_constraints として別に記録。報告の表も一致。
3. 規約: 一部。§2.2 で κ は超可換 (X κ = (−1)^{p(X)} κ X)、gb は可換なスカラーとして扱う、と宣言した。しかし計算の γ は手で書かれ (solve_triviality.py:126-208、変更なし)、κ を奇の元の向こうへ動かすことによる符号はない。宣言した規則から γ の式をどう得たかは報告に示されていない。
4. (Manager の項目) リンク: 解消。相対パスに直した。
- 判定 (書記の記録、最終は著者): 段階 1 では直っていない (事実 3 が一部) → 段階 2 へ。
- 段階 2 の事実 (著者の了承: 番号 1、文面そのまま): relay/M_facts2.txt (sha256 b434c33a)。上の 3 を場所つきで示す。読み方 (κ の符号の扱い) の正否や、読み方ごとの結論は示さない。

## 段階 2: Manager memo 02 (起草)
- memo の差分は 30 行の追加だけで、削除はない。写しは変わっていない。Manager が新しく走らせたのは git log / git show 46774ac (読むだけ)。
- 示した事実は Part 2 の項目 1 で扱われている。空欄はない。事実にない数学や値は足していない。指示は「導出を示す / 符号が変わるなら式・コード・データを直す / 今の符号が正しいならその導出を示す」の 3 通りで、どれかを選ばせている。
- Worker への文面: relay/W_stage2.txt (sha256 e7340533)

## 段階 2: Worker (段階 1 のセッションを resume)
- 起動 04:3x UTC、477 秒。session は段階 1 と同じ。ツールの呼び出し 51 回、エラー 0、ツールの外の参照 0。トークン: 入力 552,022、出力 72,649、キャッシュの読み 9,038,168。
- もとの作業場所の 12 ファイルの sha256 は終わった後も同じ。
- コミット 1975054 (3 ファイル、+171 / −135 は 46774ac から): mathematical_proof.md、solve_triviality.py (γ の符号を 4 箇所変えた。κ を奇の a_1^σ の向こうへ動かすときの符号)、verification_results.json。
- 書記の再実行 (複製): Rank(M_f) 28 / 168 / 516、Rank([M_f|M_gb]) 28 / 168 / 516、gb の制約の rank 0、自明な gb 4/4、8/8、12/12。JSON はバイトまで一致。
- **結論が変わった**: 「gb = 0 のときに限り自明」から「すべての gb で自明」(Theorem 1、全ての n ≥ 1)。一般の n の証明は、振動子のずらし a_1^σ → a_1^σ + κY^σ による構成 (§3)。宣言: κ は超可換、gb は可換なスカラー、スカラー (単位元) の項は随伴表現で落とす (§2.3 Sector 3)、κ² = 0 (§2.2 の 3)。

### 事実ごとの解消 (書記の確認)
- 段階 2 の事実 (κ の規約とコードの γ): 解消。§2.3 で、宣言した規則から γ の各成分を導く手順を示した。コードの γ はその式どおりに直され、再実行の結果は報告の表と JSON に一致する。
- 段階 1 の事実 1・2 と項目 4: 解消のまま (Theorem 1 は再び全ての n について述べるが、今度は構成的な証明がついている)。
- 新しい食い違い: final_reflection.md:16-17 は、もとの結論のまま (「P_cokernel M_gb は full column rank 4n」「gb = 0 が唯一の自明な配置」「任意の n に一般化」)。報告とデータの新しい結論 (すべての gb で自明、制約の rank 0) と合わない。Worker は振り返りを直していない (段階 1・2 の CORRECTION はどちらも振り返りに触れていない)。
- 結論とデータ: 「すべての gb で自明」は even-gb の読み方 (gb は偶のスカラー、κ は超可換、K/スカラーを除く) の結論と同じで、宣言した規約・コード・データとも一致する。
- 書記の記録 (最終は著者): §6 の基準 (新しい食い違いが入らないこと) では、振り返りの食い違いが残るので「直らなかった」→ **困難**。ただし数学の成果物 (報告・コード・データ) は互いに一致し、結論は認められる読み方の 1 つと一致する。著者の判定で「中程度」とする余地がある (判断の材料として ③ に渡す)。
- 往復: Manager の起草 2、Worker への送信 2。全体の差分 (920d772..1975054): 下記の results.tsv。
