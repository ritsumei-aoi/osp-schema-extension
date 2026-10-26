# 修正の実験 試行 3: thm01-R-gemini38f-b01-C

- 手順: runs/fix/PROTOCOL.md (v0.2、§9 の 5 の委任: 書記が推奨で進め、Manager への文面の Enter も送る。新しい Manager の起動は著者)
- もとの run: runs/batch/thm01-R-gemini38f-b01-C (C、Gemini 3.8 Flash)、最終コミット b8029d0 (最初 = 最後)、静的な目安 F1、予測 insufficient
- 写し: <home>/notebook/git/thm01-R-fix/thm01-R-gemini38f-b01-C (branch fix/thm01-R-gemini38f-b01-C、origin なし)
- Manager: <home>/notebook/git/thm01-R-fix/managers/thm01-R-gemini38f-b01-C、HOME <home>/notebook/git/thm01-R-fix/agy-home/manager-thm01-R-gemini38f-b01-C、Gemini 3.1 Pro (Low)、herdr ペイン w2:p13
- 記録: experiment/manifests/fix-thm01-R-gemini38f-b01-C.txt
- 枠 (開始前): agy Gemini 週の残り 49%

## 書記の検算 (写しの上、judging/facts と facts2 の b01 final を確かめた)
- 報告 :12 は gb を「parity-1 parameters」とし、:66-68 は p(κ)=1 から「p(γ_gb(X,Y)) = p(X)+p(Y)+1、γ は奇の 2-cochain」とする (これは gb が偶のときに成り立つ)。コードは gb を可換な Symbol とする (verification/cn1_algebra.py:13)。κ の係数に動かすことによる符号はない (76-82)。
- §4 (:108-) は「General Analytical Proof」と称するが、Obstruction 1 で H_1^{(j)} = a_1^+a_1^- + b_j^+b_j^- (:126) を使う。報告の基底 (:56-59) にあるのは b_1 を含む H_1 だけで、j≥2 の H_1^{(j)} は基底にない。コードの確認 (verification/verify_minimal.py:98) は n=1 だけ。
- :100-102「all derivations are inner ... dim Z^1 = 4n」: docs/math に出典なし (derivation の出現 0)。計算したのは ker M の次元 4n だけ。
- verification/export_artifacts.py:148 の "triviality_conclusion" は固定の文字列で、artifacts_n{1,2,3}.json に書かれる。
- 結論 (:232) は「全ての n で gb = 0 のときに限り自明」。数 (報告 :196-208): rank M 28/168/516、制約の rank 4/8/12。
- 再実行 (scratchpad の複製): `python3 -m verification.export_artifacts` と `python3 -m verification.verify_minimal` はどちらも終了コード 0。artifacts_n{1,2,3}.json はバイトまで一致 (git status に変更なし)。verify_minimal (n=1) は 4 つの障害で delta_f comb = 0、gamma comb = ±2 gb。

## 段階 1 の事実: relay/M_facts1.txt (sha256 d2f0776c)。§9 の 5 により推奨の水準 (種類だけ、場所と値は渡さない) で書記が決めた。
1. gb のパリティと γ のパリティの記述が互いに合わず、コードの gb の扱いも報告の gb のパリティと合わない。
2. 結論は全ての n について述べるが、§4 の一般の n の証明は報告の定義した基底にないものを使い、コードの確認は n=1 だけ。
3. 「すべての微分は内部」は docs/math に出典がなく、計算もされていない。
4. JSON に記録された結論はコードで計算されていない。

## Manager の開始 (#2 の後)
- 「Ready」と要約を返した。走らせたコマンドは python3 -c による os.listdir / os.walk の 3 回 (reference/ と写しの一覧、読むだけ)。写しと Manager ディレクトリの status は空。

## 中継の記録
| # | UTC | ペイン | 文面 | sha256 先頭 8 | 照合 | Enter |
|---|---|---|---|---|---|---|
| 1 | 04:52:03 | w2:p13 | relay/M_launch.txt (起動。著者の指示「起動コマンドを入力してください」により書記が入力し Enter。最初の設定の画面は著者) | 9b051976 | 画面で確認 | 書記 (著者の指示) |
| 2 | 04:53:32 | w2:p13 | relay/M_start.txt | 527fac92 | 一致 (history.jsonl 04:53:32、末尾の改行を除く) | 書記 (P4) |
| 3 | 04:55:15 | w2:p13 | relay/M_facts1.txt | d2f0776c | 一致 (history.jsonl 04:55:15、末尾の改行を除く) | 書記 (P4) |
| 4 | 05:15:52 | w2:p13 | relay/M_facts2.txt | c6acd465 | 一致 (history.jsonl 05:15:52、末尾の改行を除く) | 書記 (P4) |

## 段階 1: Manager memo 01 (起草)
- memo の差分は 36 行の追加だけで、削除はない。写しは変わっていない。走らせたコマンドは一覧だけ (読むだけ)。memo の Active Manager Model は「Gemini 3.1 Pro」((Low) なし)。
- 事実 1〜4 はそれぞれ Part 2 の項目 1〜4 で扱われている。場所 (行) は Manager が自分で特定した。空欄はない。
- 事実にない記述:
  - 項目 1 の「gb が parity 1 で κ が parity 1 なら −gb·κ は偶になり、左辺 [b_j^s, a_1^σ] (奇) と合わない」は Manager の推論。docs/math/C_inhomogeneous_definition.md:36 の Parity Note (gb は parity 1) とは逆の向きの議論で、「コードの実装に合わせよ」とも書いている (gb を偶とする方向へのほのめかし)。正しい値・結論は含まない。
  - 項目 2 の「verify_minimal.py は H_2 への射影を手で書いている」は Manager が自分で見つけたこと。
  - 項目 5 (Manager が自分で見つけたこと): docs/issues/issue_open.md:42 の絶対パス (thm01-R-batch) を相対パスにせよ。そのパスはこの機械に実在する (もとの作業場所)。issue_open.md の該当箇所は Worker が b8029d0 で書いた応答の部分。
- §9 の 5 により、推奨 (起草を直さない前例) のとおりそのまま送る。
- Worker への文面: relay/W_stage1.txt (sha256 1b84e402)
- 起動前: もとの作業場所 (thm01-R-batch/thm01-R-gemini38f-b01-C) の全ファイルの sha256 を控えた。HEAD b8029d0。枠 49%。

## 段階 1: Worker (新しいセッション)
- 04:58:18〜05:12:38 UTC (860 秒)。agy 1.3.3、gemini-3.8-flash-medium。ツールの呼び出し 143 回、エラー 0、ツールの外の参照 0。トークン: 入力 476,826、出力 61,711、キャッシュの読み 12,290,530。
- もとの作業場所の 40 ファイルの sha256 は終わった後も同じ。
- コミット 4e5a43c (6 ファイル、+146 / −91): issue_open.md (リンク)、mathematical_proof.md、cn1_algebra.py (コメントだけ)、export_artifacts.py (結論を rank から決める)、test_brackets.py、verify_minimal.py (n=1,2 で実行。障害 1 は各 j、障害 2〜4 は n==1 のときだけ)。artifacts の JSON は変わっていない (結論の文字列が同じになるため)。
- 書記の再実行 (複製): export_artifacts と verify_minimal はどちらも終了コード 0。assert はすべて通り、JSON はバイトまで一致 (git status に変更なし)。

### 事実ごとの解消 (書記の確認)
1. パリティ: 一部。gb を偶 (p(gb)=0) と宣言し直し、γ が奇の 2-cochain であることとコード (可換な Symbol) は合った。しかし docs/math/C_inhomogeneous_definition.md:36 (gb は parity 1) と違うことの説明がない。κ は奇と書くが、奇の a_1^σ の向こうへ κ を動かすときの規則は書かれていない。コード (cn1_algebra.py:76-82) は符号をつけない。
2. 一般の n: 一部。障害 1 は正準な基底の一次結合 H_1^{(j)} = H_1 − Σ H_k で書き直し、n=1,2 で確かめた。障害 2〜4 は n=1 だけを書き、一般の n は「similarly」(:174) で済ませている。verify_minimal も障害 2〜4 は n==1 だけ。結論 (:253) は全ての n のまま。
3. 内部微分: 解消。主張を外し、計算した ker M の次元 (4/8/12) に置き換えた。
4. JSON の結論: 解消。rank から決めるようにした (出力は同じ)。
5. (Manager の項目) リンク: 解消。
- 判定 (書記の記録、最終は著者): 段階 1 では直っていない → 段階 2 へ。

## 段階 2 の事実: relay/M_facts2.txt (sha256 c6acd465)。§9 の 5 により推奨の水準 (場所を示し、正しい値・読み方の正否は渡さない) で書記が決めた。

## 段階 2: Manager memo 02 (起草)
- memo の差分は 26 行の追加だけで、削除はない。写しは変わっていない。走らせたのは git log / git show 4e5a43c (読むだけ)。
- 事実 1・2 は Part 2 の項目 1・2 で扱われている。空欄はない。事実にない数学や値は足していない。項目 1 は「(a) 障害 2〜4 を一般の j で書き、コードで n≥2 も確かめる、または (b) 証明の範囲を限定し、一般の n の根拠を明記する」の 2 通りから選ばせている。
- §9 の 5 により、そのまま送る。Worker への文面: relay/W_stage2.txt (sha256 7a254b01)
- Manager の終了 (P5): 05:18 UTC ごろ、書記が `/exit` と Enter を送った (段階 2 の起草で Manager の仕事は終わり)。会話 3c9332f2-e603-4135-878e-f854f620e7d6。

## 段階 2: Worker (段階 1 のセッションを resume)
- 05:17:44〜05:23:31 UTC (346 秒)。session は段階 1 と同じ。ツールの呼び出し 36 回、エラー 1 (replace_file_content の当てはめ失敗。Worker はやり直した)、ツールの外の参照 0。トークン: 入力 598,786、出力 96,598、キャッシュの読み 20,047,013。
- もとの作業場所の 40 ファイルの sha256 は終わった後も同じ。
- コミット 243aa60 (2 ファイル、+139 / −42 は 4e5a43c から): mathematical_proof.md、verify_minimal.py (n=2 の障害 2〜4 を j=1,2 で追加)。
- 書記の再実行 (複製): export_artifacts と verify_minimal (n=1,2) はどちらも終了コード 0。assert はすべて通り (12 件)、JSON はバイトまで一致。

### 事実ごとの解消 (書記の確認)
1. 一般の n: 一部。障害 2〜4 を n=1,2 で書き、コードで確かめた。j<n と j≥2 の一般の形は式を 1 行示すだけで、計算は n=2 だけ。「Scope of the Justification」の節は「障害 1 は全ての n、障害 2〜4 は n=1,2、rank は n=1,2,3」と範囲を書いた。しかし同じ節の最後は「rigorous and comprehensive proof that all 4n parameters must vanish」とし、§7 の Final Conclusion (:253 付近) も「For all n ≥ 1」のまま。全ての n の主張に対する根拠は n ≤ 3 のまま。
2. 規約: 解消。docs/math:36 (gb は parity 1) との違いを説明し (κ を明示する慣習では gb は偶)、κ は「strictly central」で奇の元の向こうへ動かしても符号をつけないと明記した。コード (cn1_algebra.py:76-84) と一致する。
- 結論とデータ: 「gb = 0 のときに限り自明」(変わらず)。計算 (κ に符号なし、K/スカラーを除く) は odd-gb の読み方の計算と同じで、数 (制約の rank 4n) とも一致する。ただし宣言は「gb は偶、κ は奇だが厳密に可換」で、README の 2 つの読み方の組 (odd-gb: gb 奇・κ 可換、even-gb: gb 偶・κ 超可換) のどちらとも宣言の上ではそろわない。これが認められる読み方に当たるかどうかは著者の判断。
- 書記の記録 (最終は著者): 事実 1 が一部のまま (全ての n の主張に一般の証明がない) → 直らなかった → **困難**。
- 往復: Manager の起草 2、Worker への送信 2。
