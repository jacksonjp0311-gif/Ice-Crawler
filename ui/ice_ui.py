import os, json, subprocess, threading, queue, time
import tkinter as tk
from tkinter import ttk, messagebox

def run_orchestrator(repo_root: str, repo_url: str, max_files: int, max_kb: int):
    engine = os.path.join(repo_root, "engine")
    state  = os.path.join(repo_root, "state", "runs")
    os.makedirs(state, exist_ok=True)

    ts = time.strftime("run_%Y%m%d_%H%M%S")
    state_run = os.path.join(state, ts)
    os.makedirs(state_run, exist_ok=True)

    tempw = os.path.join(os.environ.get("TEMP","."), "icecrawl_ui_" + str(int(time.time()*1000)))
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"]="1"

    py = "python"
    orch = os.path.join(engine, "orchestrator.py")
    cmd = [py, orch, repo_url, state_run, str(max_files), str(max_kb), tempw]

    p = subprocess.run(cmd, cwd=repo_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout, state_run

def safe_read(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

class IceUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ICE-CRAWLER ❄ (v4.0 UI)")
        self.geometry("920x640")

        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.q = queue.Queue()

        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Repo URL").pack(anchor="w")
        self.url = ttk.Entry(top)
        self.url.pack(fill="x", pady=(2,10))
        self.url.insert(0, "https://github.com/git/git.git")

        row = ttk.Frame(top)
        row.pack(fill="x")

        ttk.Label(row, text="MaxFiles").grid(row=0, column=0, sticky="w")
        self.max_files = ttk.Entry(row, width=10)
        self.max_files.grid(row=0, column=1, padx=(6,16))
        self.max_files.insert(0, "50")

        ttk.Label(row, text="MaxFileKB").grid(row=0, column=2, sticky="w")
        self.max_kb = ttk.Entry(row, width=10)
        self.max_kb.grid(row=0, column=3, padx=(6,16))
        self.max_kb.insert(0, "120")

        self.btn = ttk.Button(row, text="❄ RUN ICE-CRAWLER", command=self.on_run)
        self.btn.grid(row=0, column=4, sticky="e")
        row.columnconfigure(4, weight=1)

        ttk.Separator(self).pack(fill="x", pady=8)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Output").pack(anchor="w")
        self.out = tk.Text(body, height=18, wrap="word")
        self.out.pack(fill="both", expand=True)

        ttk.Separator(body).pack(fill="x", pady=10)

        ttk.Label(body, text="AI Handoff Proof (copy/paste)").pack(anchor="w")
        self.proof = tk.Text(body, height=6, wrap="word")
        self.proof.pack(fill="x")

        self.after(150, self.pump)

    def log(self, s: str):
        self.out.insert("end", s + "\n")
        self.out.see("end")

    def set_proof(self, s: str):
        self.proof.delete("1.0","end")
        self.proof.insert("end", s)

    def on_run(self):
        repo_url = self.url.get().strip()
        if not repo_url:
            messagebox.showerror("ICE-CRAWLER", "Repo URL required")
            return

        try:
            max_files = int(self.max_files.get().strip())
        except Exception:
            max_files = 50

        try:
            max_kb = int(self.max_kb.get().strip())
        except Exception:
            max_kb = 120

        self.btn.config(state="disabled")
        self.log("🧊 UI RUN BEGIN")
        self.log(f"Target -> {repo_url}")

        def work():
            rc, out, state_run = run_orchestrator(self.repo_root, repo_url, max_files, max_kb)
            self.q.put((rc, out, state_run))

        threading.Thread(target=work, daemon=True).start()

    def pump(self):
        try:
            while True:
                rc, out, state_run = self.q.get_nowait()
                self.log(out.strip())
                self.log(f"✅ state_run -> {state_run}")

                ai_path = safe_read(os.path.join(state_run, "ai_handoff_path.txt"))
                root_seal = safe_read(os.path.join(state_run, "ai_handoff", "root_seal.txt"))

                proof = []
                proof.append("AI_HANDOFF_READY")
                proof.append(ai_path if ai_path else "(missing ai_handoff_path.txt)")
                proof.append("")
                proof.append("ROOT_SEAL:")
                proof.append(root_seal if root_seal else "(missing root_seal.txt)")
                self.set_proof("\n".join(proof))

                self.log("🧊 UI RUN COMPLETE")
                self.btn.config(state="normal")
        except queue.Empty:
            pass
        self.after(150, self.pump)

if __name__ == "__main__":
    try:
        import tkinter
    except Exception as e:
        raise SystemExit("tkinter missing on this Python install")

    app = IceUI()
    app.mainloop()
