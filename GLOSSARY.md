# Glossary of Japanese terms in the records

Many records (run logs, Human memos, scribe checks, the design log, judging notes) are written in Japanese. Texts sent to the models (issue files, prompts, Manager drafts) are in English. The terms below occur often.

## Roles and actions

| Japanese | English |
|---|---|
| 著者 | the author (the human supervisor and judge) |
| 書記 | the scribe (a Claude Code session that operated the relay and kept records, under the author's delegation) |
| 中継 | relay (typing a text into the Worker's or the Manager's terminal) |
| 起草 / 起草文 | draft (a text drafted by the Manager AI) |
| 承認 | approval (at an issue gate) |
| 修正依頼 / 訂正 (CORRECTION) | correction request |
| 事実の提示 / 事実を示す | presentation of facts (the human shows facts to the Manager instead of sending its draft) |
| 明確化 | clarification |
| 送らない / 差し戻し | withheld (a draft that was not sent) |
| 振り返り | final reflection (issue I09) |
| 介入 | intervention |
| 起動し直し / 再起動 | restart |
| 自動圧縮 | automatic context compaction |
| 許可 / 拒否 | permission granted / denied (tool permission dialog) |
| 作業場所 | workspace |
| 作業場所の外 | outside the workspace |
| 枠 | usage quota (values removed for publication) |

## Conditions and outcomes

| Japanese | English |
|---|---|
| 人間対応の run | gated run (A1, A2, F−) |
| 自動実行 | automated run (G−, C) |
| 手で起動した run | run started by hand |
| 合格 | pass |
| 不十分 | insufficient |
| 不合格 | fail |
| 除外 | excluded |
| 数える / 数えない | counted / not counted |
| 仕組み起因の停止 | mechanical stop |
| 判定 | verdict / judgment |
| 凍結した予測 | frozen (rule-based) prediction |
| 読み方 | reading (interpretation of the definitions) |
| K 依存 | $K$-dependence |
| 構造定数 | structure constants |
| 照合 | check against a reference (independent computation) |
| 修正の実験 | correction experiment |
| 段 (容易 / 中程度 / 困難) | ease tier (easy / moderate / hard) |
| 隔離の破れ | isolation breach |

## Manager claims (judging/manager_review)

| Code | Meaning |
|---|---|
| M1-false | the claim contradicts evidence the Manager opened in that conversation |
| M2-unverified | the Manager asserted correctness without opening the sources (unverified endorsement when false) |
| M3-added | the Manager added content not present in the materials it was given |
