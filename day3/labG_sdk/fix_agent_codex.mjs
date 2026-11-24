// 用 Codex SDK（TypeScript／JavaScript）寫的修 bug Agent
//
// 用法：
//   npm install @openai/codex-sdk        （Node 18 以上；只能在伺服器端執行）
//   node fix_agent_codex.mjs <專案資料夾>                # 修 bug，印出事件
//   node fix_agent_codex.mjs <專案資料夾> --resume <ID>  # 接續同一個 Thread，要求結構化摘要
//
// 需要已登入的 Codex（codex login）或環境變數 CODEX_API_KEY。
import { Codex } from "@openai/codex-sdk";
import path from "node:path";

const TASK = `執行 \`python3 -m unittest discover -s tests\`，找出失敗原因並修正 invoice/calc.py。
規則：只能修改 invoice/calc.py，不要改測試；改完再執行一次測試確認全部通過；最後用兩三句話說明每個 bug 的原因。`;

const SUMMARY_SCHEMA = {
  type: "object",
  properties: {
    tests_passed: { type: "boolean" },
    bugs: {
      type: "array",
      items: {
        type: "object",
        properties: { function: { type: "string" }, cause: { type: "string" }, fix: { type: "string" } },
        required: ["function", "cause", "fix"],
        additionalProperties: false,
      },
    },
  },
  required: ["tests_passed", "bugs"],
  additionalProperties: false,
};

const [project, flag, threadId] = process.argv.slice(2);
if (!project) { console.error("用法：node fix_agent_codex.mjs <專案資料夾> [--resume <ID>]"); process.exit(1); }

const codex = new Codex();
const threadOptions = {
  workingDirectory: path.resolve(project),
  skipGitRepoCheck: true,
  sandboxMode: "workspace-write",   // 只能寫專案資料夾
  approvalPolicy: "never",          // 沒有人可以按核准；越界的動作直接失敗
};

function show(ev) {
  switch (ev.type) {
    case "thread.started": console.log(`[thread] ${ev.thread_id}`); break;
    case "item.started":
      if (ev.item.type === "command_execution") console.log(`[tool]   ${ev.item.command}`);
      break;
    case "item.completed":
      if (ev.item.type === "command_execution") console.log(`[result] exit=${ev.item.exit_code}`);
      else if (ev.item.type === "file_change") console.log(`[edit]   ${ev.item.changes.map(c => c.path).join(", ")}`);
      else if (ev.item.type === "agent_message") console.log(`[text]   ${ev.item.text.slice(0, 200)}`);
      break;
    case "turn.completed": console.log(`[done]   usage=${JSON.stringify(ev.usage)}`); break;
    case "turn.failed": console.log(`[failed] ${ev.error.message}`); break;
  }
}

if (flag === "--resume") {
  const thread = codex.resumeThread(threadId, threadOptions);
  const turn = await thread.run("依照剛才的修正，輸出摘要。", { outputSchema: SUMMARY_SCHEMA });
  console.log(JSON.stringify(JSON.parse(turn.finalResponse), null, 2));
  console.log(`[done]   usage=${JSON.stringify(turn.usage)}`);
} else {
  const thread = codex.startThread(threadOptions);
  const { events } = await thread.runStreamed(TASK);
  for await (const ev of events) show(ev);
  console.log(`[thread] 之後可用 --resume ${thread.id} 接續`);
}
