# Antigravity CLI (agy 1.2.16) を自動実行に使うための短いテスト (2026-10-04)

目的: Gemini Flash (3.6/3.7/3.8) の C / G− を自動で回す (案 1)。モデルは gemini-3.8-flash-low、作業場所は空のテスト用リポジトリ `<home>/notebook/git/thm01-R-agy-test/ws`。ログは `<home>/notebook/git/thm01-R-agy-test/t1–t6.jsonl`。

| 項目 | 結果 |
|---|---|
| 環境の切り離し | `HOME` を差し替えると、設定・記憶 (brain、knowledge、conversations) はすべてその下に作られる。著者が一度だけ `<home>/notebook/git/thm01-R-agy-home/base` にログインし、run ごとの HOME には認証ファイル `antigravity-oauth-token` だけを写す。Worker は「以前の会話の記憶はない」と答えた |
| git の名前 | HOME を差し替えても `GIT_CONFIG_GLOBAL=~/.gitconfig` でコミットできた |
| 許可 | `settings.json` の `permissions.allow` に `command(python3)` などを並べた許可リストが効く。リストにないコマンドは拒否される。`allowNonWorkspaceAccess: false` で作業場所の外のファイル読み取りも拒否された |
| 拒否されたとき | そのターンは応答なしで終わる (`denied_actions` に記録)。`--conversation` で続ければ再開できる |
| ログ | `--output-format stream-json`。init に model・tools・permission_mode、各ステップ (tool_name、引数、エラー)、result に conversation_id・usage (input/output/thinking トークン)・denied_actions |
| 会話の継続 | `--conversation <ID>` で同じ会話に続けて送れた |
| Web 検索 | `search_web` は許可なしで実行された (結果も返った)。`permissions.deny` と `disabledTools` (settings.json) では止まらなかった。`read_url_content` は許可リストにないので拒否された |
| 使わなかったもの | `--dangerously-skip-permissions` は Claude Code の安全判定で拒否されたため使っていない (許可リストで代替) |

未解決: `search_web` を止める方法。止められない場合は、stream-json から `search_web` の呼び出しを検出して run.json に記録する (条件の違いとして扱う)。

## 消費の目安 (著者の表示から、2026-10-04)

- gemini38f-b01-C 1 本 (直前の短いテスト 6 回を含む): 週の枠 70.69% → 69.52% (約 1.2%)、5 時間枠 100% → 92.37% (約 7.6%、この 5 時間はこの作業だけ)。テストのトークンは run の数 % なので、ほぼ run 1 本分。
- 見積もり: 5 時間枠で C 約 13 本、週の残り 69.5% で C 約 59 本。G は Claude の例では C の 1.5–3 倍だったので、G 1 本は 5 時間枠の 10–20% 程度と見て、最初の G で確かめる。
- 拒否で止まったターンへの固定返答は、Worker 自身の停止への返答と分けて数える (`denial_replies`、上限 5 → 10 に変更: glob を含む `git add data/C_*.json` なども拒否されるため、著者の決定 案 A)。
- 18:23 の表示: 週の枠 64.77%、5 時間枠 63.87%。前回 (b01-C 後) からの減少は週 4.75%、5 時間枠 28.5%。この間に 38f-b02-G と 37f-b01-C が完了、37f-b02-G が途中 (I07 まで)。C を 7.6% とすると G は 5 時間枠の約 14% (週の枠の約 2.3%) と見積もる。5 時間枠と週の枠の比は約 6:1。

# Copilot CLI (1.0.91、GPT-6 Luna) の短いテスト (2026-10-04)

`<home>/notebook/git/thm01-R-copilot-test/` (ログ c0–c4.jsonl)。
- `COPILOT_HOME` を run ごとに分けても、ログインは macOS のキーチェーンにあるので動く。指示ファイルは「No instruction sources found」、メモリは `-p` では既定で無効。
- 許可リスト: `--allow-tool 'shell(git:*)' ... write`。`shell(git)` だけでは `git add` / `git commit` が拒否されたので `:*` の形を使う。
- 拒否されてもターンは止まらず続く (Claude Code と同じ)。作業場所の外のファイル読み取り、`curl` (許可リスト外) は拒否された。
- `--excluded-tools web_fetch task ...` で Web とサブエージェント系のツールをモデルに見せない。`--disable-builtin-mcps` で GitHub の MCP を止める。
- `--resume <sessionId>` で同じ会話に続けられた。`--output-format json` に発言、ツールの引数と出力、送った文面がすべて残る。トークン数は `--usage-output-file` で turn ごとに保存する。
- Luna の reasoning effort は A / F− と同じ medium。
- Copilot の利用枠: 月 1500 クレジット。2026-10-04 19:0x の表示で 116.3/1500 (luna-A、luna-F、このテスト、luna-b01-C の合計)。usage ファイルの `totalNanoAiu` は luna-b01-C で 1.29e9 (= 1.29 AIU、会話の累計)、テストの 1 回の応答で 0.16e9。1 クレジット = 1 AIU かどうかは、次の run の前後の表示で確かめる。
- 19:0x の表示: 週の枠 62.41%、5 時間枠 49.68%。18:23 からの減少は週 2.36%、5 時間枠 14.2% (37f-b02-G の後半、36f-b01-C (短い)、36f-b02-G)。G 約 14% の見積もりと合う。
- 19:2x の表示: agy 5 時間枠 46.18% (38f-b03-C の途中)。Copilot 124.3 クレジット (116.4 から +7.9、luna-b02-G 以降の途中)。

## 問題: glob を含むコマンドの拒否で、コミットできずに止まる (2026-10-04 19:15)

- gemini38f-b03-C が stopped (固定返答 3 回を使い切り)。turn2 で `git add ... verification/*.py verification/*.json` が拒否され、agy の拒否文 ("Do not attempt to circumvent this denial by rephrasing the command ...") に従って、Worker はその後コミットを試みなかった。証明・振り返り・成果物は作業場所に未コミットで残っている。仕組みに起因する停止。
- 許可リストでは直せない: `command(git)`、`command(git add *)`、`command(git *)`、`command(git:*)`、正規表現の形 `command(git add .*)`、`command(git .*)`、`--sandbox` のいずれでも `git add *.txt` は拒否された (テスト用 HOME、gemini-3.8-flash-low)。glob を含むコマンドは規則に関係なく確認を求めるらしい。
- 38f-b02-G でも同じ拒否が 2 回あったが、そのときは Worker が別の形でコミットして完了した。

## 案 1 のテスト: `--dangerously-skip-permissions --sandbox` (著者の端末で実行、2026-10-04 19:5x)

スクリプトとログは `experiment/agy_tests/`。結果:

| 操作 | 結果 |
|---|---|
| `git add *.txt`、`git commit` (作業場所の中) | **失敗**。sandbox が `.git/index.lock` の作成と TMPDIR への書き込みを禁じる ("Operation not permitted") |
| 作業場所の外のファイルを view_file で読む | **読めた** (`allowNonWorkspaceAccess: false` は skip-permissions で無効になる) |
| 外のファイルを cat / python3 で読む、外の ls、外への書き込み | 防がれた (sandbox) |
| curl / python3 で外部ネットワーク | **通った** |

結論: 案 1 は使えない (コミットができず、ファイルを見るツールで外を読める)。
- 19:4x の表示: agy 5 時間枠 43.57% (gemini3 の連続実行の開始時)。
- 20:2x の表示: Copilot 185.2 クレジット (116.4 から +68.8)。Luna b02–b10 の AIU 合計 68.7 と一致 → **1 クレジット = 1 AIU**。Luna の G 約 10–15、C 約 1–3 クレジット。agy 5 時間枠 29.29% (43.57% から −14.3%、C 3 本 → C 1 本 約 4.8%)。
- 23:2x の表示: agy 週の枠 56.82% (5 時間枠は 22:14 ごろリセット済み)。
- 00:4x の表示: agy 5 時間枠 49.30% (23:23 からの 7 本で約 51%、3.1 Pro の C は小さい)。
- 05:2x の表示: agy 週 43.63%、5 時間枠 65.97% (04:30 からの 5 本で約 34%。Flash G 1 本と C 2 本を引くと、Pro の G と C で合わせて約 10%)。
- 09:2x の表示: agy 週 33.73%、5 時間枠 100% (リセット直後)。
- 11:2x の表示: agy 週 17.68%、5 時間枠 3.71% (残り)。36f-b11-G の実行中。次の 5 時間枠のリセットは 14:2x ごろ。
