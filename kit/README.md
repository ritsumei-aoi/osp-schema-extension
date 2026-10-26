# R1-3 追加実験キット (thm01-R 系列)

設計は `../r1-3_experiment_design.md` (v0.3) を参照。この README は実行手順をまとめたもの。

## 構成

```text
experiment/
├── kit/                      配布物の唯一の出所 (ワークスペースはここからのみ組み立てる)
│   ├── math_core/            数学定義 3 ファイル (thm01-X-base と同一 blob、全条件共通)
│   ├── workflow_docs/        B(0,n) 定義、B(0,n) v5.0 スキーマ、docs/math/README.md (A, G−, F− のみ)
│   ├── handover/             Tier A の handover 一式 (thm01-base 由来。submit_correction.sh だけは main の修正版)
│   ├── handover_G/           G− 用の README.md と workflow.md (承認で止まらない版)
│   ├── issues_A/             I01–I09 (A 用)
│   ├── issues_G/             I01–I08 (G− 用。承認ゲートの節を外したもの)
│   ├── templates/            reflection と metrics のテンプレート、template_issue_open.md
│   ├── repo_files/           requirements.txt、pytest.ini、.gitignore
│   └── c_condition/          C 条件のワークスペース一式 (thm01-X-base と完全に同一)
├── prompts/                  条件ごとのプロンプト (実行前に確定し、コミットしておく)
│   ├── A_start/I01–I09.txt   A 用の issue ごとの開始プロンプト (I09 は reflection)
│   ├── session_start.md, final_reflection.md   旧 Tier A の汎用プロンプト (参考)
│   ├── G_prompt.txt          G− 用 (1 回だけ投入)
│   ├── F_opening.txt, F_messages/step1–8.md, F_final_reflection.txt   F− 用
│   ├── C_prompt.txt          C 用 (thm01-X-04〜06 の初期プロンプトと同一)
│   └── C_final_reflection.txt  C 用の reflection 依頼
├── scripts/
│   ├── build_workspace.sh    ワークスペースを組み立て、sha256 manifest を記録する
│   ├── deliver_issue.sh      A では次の issue を配置し、F− では次の step をクリップボードへコピーする (記録も残す)
│   ├── check_nonK_coboundary.py  K 成分を除いた γ が δf の像に入るかを、Worker のデータから検算する
│   └── manager.sh            Manager AI のディレクトリの作成 (init)、run ごとの memo の作成 (run)、issue ごとの開始プロンプトのコピー (start)
├── manager_kit/              MANAGER_BRIEF.md と、Manager AI の開始プロンプトのひな形
│   └── check_artifacts.py    4 層 JSON の有無と、Layer 1 の代数 (反対称性・super Jacobi) を独立に検査する
└── manifests/                run ごとの配布ファイルの sha256 (ワークスペースの外に置く)
```

## 既存の Tier A 資料から変えた点

新しい run の条件をそろえるため、次の点を変えた。論文にも明記する。

1. **数学定義**: 4 条件とも改訂版にした。旧 Tier A は旧版の `Cn1_definition.md` (8365814) を使っていた。この版には I01 で決めるはずの PBW 順序や JSON ラベルの規約が含まれていたので、新しい run では使わない。
2. **I02**: 旧 Tier A で途中から出した修正指示 C02-1 (統一スキーマ規則) を、最初から I02 の要件に含めた。G− は途中で修正を受けられないので、全条件で同じ情報を最初から渡す必要がある。
3. **I07**: 写像 $f$ の定義を、改訂版の定義 (奇線形写像 $f:\mathfrak g\to\mathfrak g$) に合わせた。旧 I07 には誤った定義 ($f:\mathfrak g\to\mathbb R$) が書かれていて、C07-1 で修正していた。
4. **I02A (欠陥スクリプト実験) は行わない。** `submit_correction.sh` は main の修正版を配る。
5. **ゴミファイルを除いた。** 旧 `thm01-base` には `src/__pycache__/C_generators.*.pyc` などが含まれていた。新しいキットからは除いた。

## run の一覧

| run | 条件 | モデル | 順 |
|---|---|---|---|
| thm01-R-luna-C | C | GPT-6 Luna | 1 (済) |
| thm01-R-luna-G | G− | GPT-6 Luna | 2 |
| thm01-R-luna-r2-C | C | GPT-6 Luna | 3 |
| thm01-R-luna-r2-G | G− | GPT-6 Luna | 4 |
| thm01-R-luna-r3-C | C | GPT-6 Luna | 5 |
| thm01-R-luna-r3-G | G− | GPT-6 Luna | 6 |
| thm01-R-luna-A | A | GPT-6 Luna | 7 |
| thm01-R-luna-F | F− | GPT-6 Luna | 8 |
| thm01-R-sonnet46-G | G− | Claude Sonnet 4.6 | 9 |
| thm01-R-sonnet46-A | A | Claude Sonnet 4.6 | 10 |
| thm01-R-sonnet46-F | F− | Claude Sonnet 4.6 | 11 |
| thm01-R-flash38-C | C | Gemini 3.8 Flash | 12 |
| thm01-R-flash38-G | G− | Gemini 3.8 Flash | 13 |
| thm01-R-flash38-A | A | Gemini 3.8 Flash | 14 |
| thm01-R-flash38-F | F− | Gemini 3.8 Flash | 15 |

Sonnet 4.6 の C は既存の `thm01-X-04` を使う (文書は同一)。

繰り返しの run は、`<tag>` に回数を付けて組み立てる。たとえば `scripts/build_workspace.sh C luna-r2 "GPT-6 Luna" <home>/notebook/git/thm01-R/thm01-R-luna-r2-C --with-remote` とすると、ブランチは `study/thm01-R-luna-r2-C` になる。毎回、新しいワークスペースで新しいセッションを始める。

## 共通の手順

1. 実行前に、キットとプロンプトをこのリポジトリにコミットする。manifest にはキットのコミット ID が記録される。
2. ワークスペースを組み立てる。
   ```bash
   scripts/build_workspace.sh <A|G|F|C> <tag> "<Model Name>" <新しいディレクトリ> [--with-remote]
   ```
   - 他の run のディレクトリとは別の場所に作る。
   - Worker の作業ディレクトリは、そのワークスペースだけにする。
3. Worker の設定を確認する。
   - 過去のセッション履歴を参照できないこと。
   - モデル名と版。
4. 実行中は `run_log` (下記) に記録する。
5. 終了後に、次を行う。
   - `python3 scripts/check_artifacts.py <ワークスペース> --json <run>_check.json` を実行する。
   - 人間による判定を行う (正しさ、範囲の区別、再実行による再現性)。
6. 公開リポジトリへの push。

## 条件ごとの手順

### C (One-shot)
- `--with-remote` を付けて組み立てる。
- `prompts/C_prompt.txt` を 1 回だけ投入する。以後は介入しない。
  - この文面は、thm01-X-04〜06 で実際に使った初期プロンプトと同一。`mathematical_proof.md` の作成を求める節を含む。
  - thm01-X-01〜03 では、この節がない旧版を使っていた。
- Worker から質問や承認の求め (外部 Web の利用など) があった場合は、次の定型文だけを返す。「No external access is approved. Proceed using only the provided documents.」返した回数を記録する。
- 主たる判定は、この最初の提出物に対して行う。既存の X-04 も、最初の提出物 (Worker Action 01) で判定し直して比べる。
- Worker が完了を報告したら、判定を待たずに `prompts/C_final_reflection.txt` を投入する。
  - 判定の結果や人間とのやり取りを、reflection に影響させないため。
  - 判定は、最初の提出物のコミットに対して行う。
  - reflection のコミットで提出物が変わっていないことを、git の差分で確認する。
- 既存の X 系列では、判定のあとに個別の追及 (rebuttal) を行った。新しい run で追及を行う場合は、主たる判定とは別の段階として記録する。

### G− (No gate)
- `--with-remote` を付けて組み立てる。
- `prompts/G_prompt.txt` を 1 回だけ投入する。以後は介入しない。
- 途中で質問されても回答しない。次の定型文だけを返し、その回数を記録する。
  > Proceed as instructed: make the decision yourself, record it in the Response section, and continue.
- 最終成果物を判定する。却下になっても修正の機会は与えない。

### A (Full)
- `--with-remote` を付けて組み立てる。`close_issue.sh` が push するため。
- 各 issue のセッションは、`prompts/A_start/I0N.txt` で始める。
  - この開始プロンプトは、issue ごとに事前に固定してある。group2 (thm01-04、05) で使った issue ごとのプロンプトをもとに、run に固有の内容を除いて作った。
  - group2 の文面から除いたもの: I06 の「starting with gb=0」、I07・I08 の group2 固有のファイル名、I07 の METARULE。
  - 「CRITICAL RULE FOR ITERATIVE DIALOGUE」の段落は、全 issue に残す。
  - `prompts/session_start.md` は使わない (参考として残す)。
- issue が終わったら、次の issue を配置する: `scripts/deliver_issue.sh A <ワークスペース> <N>`
  - I01 はビルドの時点で置かれている。したがって N=2 から使う。
  - 前の issue が `close_issue.sh` で閉じられていない場合、スクリプトは配置を拒否する。
  - 配置した記録は `manifests/<run>.deliveries.txt` に残る。
- 承認と修正の指示は、Manager AI が起草し、人間が確認してから投入する。
  - 修正は `docs/issues/issue_correction.md` で行う。
  - Manager AI の承認文は、Worker が挙げた論点や承認依頼の各項目に 1 つずつ応答する形にする。人間は、応答していない項目がないかを確認する。
  - 人間は Manager AI の起草文を直さない。直す必要があると考えたときは、事実だけを Manager AI に示し (違反かどうかなどの結論は示さない)、起草し直させる。そのやりとりは Human memo に記録する。
    - 理由: 旧 thm01-05 (GPT-5.4) では、共通の承認文で済ませたため、Worker が提起したパリティの論点が素通りした。
- gb のパリティの読み違いが分かったら、どの段階でも、その時点で修正指示を出す。介入の種類は「記法の明確化」として記録する。
- Manager AI とのやりとりは、下の「Manager AI の手順」に従う。
- 最後に I09 (`prompts/final_reflection.md`) を行う。

### F− (No files)
- `--with-remote` は付けない。Git は作られない。
- `prompts/F_opening.txt` を投入し、続けて `F_messages/step1.md` から `step8.md` を順に 1 通ずつ投入する。
  - `scripts/deliver_issue.sh F <ワークスペース> <N>` を使うと、step N をクリップボードにコピーし、その記録も残す。最後は N=final とする。
- 承認と修正は、Manager AI が起草し、人間が確認してからチャットで伝える。
  - 内容は A の承認・修正と同じ水準にする。
  - Manager AI の承認文を各項目に 1 つずつ応答させること、gb のパリティの読み違いをその時点で訂正することは、A と同じ。
- 最後に `F_final_reflection.txt` を投入する。
- 終了後、人間が次を行う。
  - チャットログを書き出す。
  - ワークスペースを公開ブランチ `study/thm01-R-<tag>-F` に保存する。

## Manager AI の手順 (A と F−)

- Manager AI: Gemini 3.1 Pro (preview) を Antigravity CLI で使う。
- Manager AI のディレクトリは、評価リポジトリとも Worker のワークスペース群とも別の場所に置く。例: `<home>/notebook/git/thm01-R-manager/`。
  - 評価リポジトリには、設計書、run_log、判定が置かれている。それらを Manager AI に読ませないため。
  - Worker のワークスペース群の下にも置かない。他の run を見せないため。
- 初回だけ実行する: `scripts/manager.sh init <home>/notebook/git/thm01-R-manager`
  - 作られるもの: `MANAGER_BRIEF.md`、`reference/` (A と F− の Worker が受け取るものと同じ文書・issue・プロンプト)、`memos/`
  - 設計や判定に関わる情報は入れない。gb のパリティについての情報も入れない。
- run ごとに実行する: `scripts/manager.sh run <home>/notebook/git/thm01-R-manager <Worker ワークスペース> <A|F>`
  - `memos/<run>/manager_memo.md` を作る。
- issue ごとの進め方:
  1. `scripts/manager.sh start <home>/notebook/git/thm01-R-manager <Worker ワークスペース> <N>` を実行する。開始プロンプトがクリップボードにコピーされる。
  2. Manager ディレクトリで、Antigravity CLI の**新しいセッション**を開き、貼り付ける。
  3. Worker が止まるたびに、Manager AI にレビューを依頼する。依頼文は `scripts/manager.sh review <Manager ディレクトリ> <Worker ワークスペース> <N>` で表示される英語の定型文を使う (`manager_kit/review_request.txt`)。
     - A の場合: Manager AI がワークスペースを読む。
     - F− の場合: Worker の返答を人間が貼り付ける。
  4. Manager AI の出力は 2 部に分かれている。人間はそれを読み、必要なら修正してから Worker に送る。
     - 送り方: 承認はチャットで送る。A の修正は `docs/issues/issue_correction.md` として置く。
     - Human memo に、実際に送った文面、修正の有無、修正した場合の理由を書く。
  5. issue が閉じたら、`scripts/manager.sh close <Manager ディレクトリ> <Worker ワークスペース> <N>` で表示される定型文を送る (`manager_kit/issue_closed.txt`)。Worker のコミットは git から自動で埋まる。Manager AI が carry-over を memo に書いたら、セッションを終える。
  - 定型の指示は英語で送る。人間からの個別の指摘や質問は日本語でよい。送った内容は Human memo に残す。
  - `TYPE:` の行は Worker に送らない。
- **Human memo に書いてよいもの** (2026-10-03 から):
  - Manager AI に送った文面
  - Worker に送った文面
  - 人間の判断のうち、Manager AI に見せてよいもの

  書記の検算、ほかの run の情報、評価の方針、Worker が尋ねていない論点についての方針は、Human memo に書かない。これらは評価リポジトリの `runs/<run>/run_log.md` に書く。Manager AI はセッションを始めるたびに memo を読むので、memo に書くと Manager AI に伝わってしまうため。
- 毎回確認すること:
  - Manager AI の作業のあとで、Worker のワークスペースの `git status` を見る。Manager AI がファイルを変えていないことを確かめる。
  - Manager AI の Worker 向けの文面が、Worker の各項目に 1 つずつ応答しているかを確かめる。
- gb のパリティ:
  - Worker が自分から指摘しない限り、Manager AI には伝えない。
  - 人間が読み違いに気づいた場合は、Manager AI に「記法の明確化として修正文を起草せよ」と指示する。そのことを Human memo に記録する。
- run の終了後: `memos/<run>/manager_memo.md` を、評価リポジトリの `runs/<run>/manager_memo.md` にコピーする。
- F− の場合:
  - 依頼文には `manager.sh review` を使う (memo の条件が F のときは `manager_kit/review_request_F.txt`)。表示された文面の印の位置に、Worker の最新の返答を人間が貼り付けて送る。
  - step の終了は `manager.sh close` で知らせる (`issue_closed_F.txt`。コミットはない)。
  - Manager のセッションは、step ごとに新しく開く (A の issue ごとと同じ)。

## F− の記録 (Git をワークスペースに置かない)

- `scripts/shadow.sh init <ワークスペース>` で、ワークスペースの外 (`<home>/notebook/git/thm01-R-shadow/<run>.git`) に影のリポジトリを作る。
- 各 step のあとに、`scripts/shadow.sh snap <ワークスペース> "<メッセージ>"` でスナップショットを取る。Worker からは見えない。
- Worker の開始文は `scripts/deliver_issue.sh F <ワークスペース> open` で表示する。

## run_log (run ごとに記録する)

`../runs/<run>/run_log.md` に、次の項目を記録する。

- 開始・終了時刻、モデル名と版、ツール (CLI 名と版)、Manager AI の版
- 人間からの各メッセージ: 時刻、種類 (承認 / 修正 / 違反通知 / 定型応答)、起草者 (Manager)、要約
- 手順違反: 承認待ちを無視したもの、委任境界を越えたもの
- 誤りの検出: 何が、いつ、誰によって、どの手段で見つかったか
- トークン数と実時間 (取得できる範囲で)

## Copilot CLI の選択画面への対応 (2026-10-03 から、全条件・全 run 共通)

- Worker が選択画面 (選択肢で答えを求める画面) を出したら、選択肢は選ばずに「Other」を選び、定型文だけを送る。
  - A と F−: `prompts/fixed_reply_plain_text.txt` を送る (文章で質問し直すよう求める)。Manager AI は通さない。Worker が文章で質問し直したら、通常どおり Manager AI にレビューを依頼する。
  - G− と C: それぞれの条件の定型文を送る。
- 同じ画面が 2 回続けて出たら、Copilot CLI の性質として記録し、「Other」で Manager AI の起草文を送る方式に切り替える。
- 介入の種類は「定型応答 (形式)」とし、run_log に回数を記録する。
- 開始の文面は変えない (実行済みの run と条件をそろえるため)。
