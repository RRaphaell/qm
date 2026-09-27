import { html, render } from "lit";
import { appState } from "./shell";

// Chief of Staff Brief: the one page a person reads. Served by the Chief of Staff
// runtime (goals, decisions, opportunities, ideas; learns from every answer).
const BRIEF_URL: string =
  (import.meta.env.VITE_COS_BRIEF_URL as string | undefined) ||
  localStorage.getItem("qm.cos.briefUrl") ||
  "http://localhost:8790/";

export function renderBrief(): void {
  if (appState.currentView !== "brief" || !appState.mainEl) return;
  const host = document.createElement("div");
  host.className = "pane";
  host.style.cssText = "display:flex;flex-direction:column;height:100%;min-height:0";
  render(
    html`
      <div class="list-page-head" style="padding:10px 16px;border-bottom:1px solid var(--border, #e5e5e5)">
        <div>
          <h1 class="pane-title" style="margin:0">Brief</h1>
          <div class="list-page-sub">goals, decisions, opportunities, ideas · learns from your answers</div>
        </div>
      </div>
      <iframe
        title="Chief of Staff Brief"
        src=${BRIEF_URL}
        style="flex:1;width:100%;border:0;min-height:0;background:#fff"
      ></iframe>
    `,
    host,
  );
  appState.mainEl.replaceChildren(host);
}
