import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum
from random import randrange, choice
from collections import deque

# ============================
#   MODELO
# ============================

class ProcState(Enum):
    READY = "Listo"
    RUNNING = "Ejecutando"
    BLOCKED = "Bloqueado"
    TERMINATED = "Terminado"

class MemoryPartition:
    def __init__(self, size: int):
        self.size = size
        self.owner_pid = None
        self.occupied = 0
    def is_free(self):
        return self.owner_pid is None

class Memory:
    def __init__(self, partitions_sizes):
        self.partitions = [MemoryPartition(s) for s in partitions_sizes]
    def total_size(self): return sum(p.size for p in self.partitions)
    def used_size(self):  return sum(p.occupied for p in self.partitions)
    def free_size(self):  return self.total_size() - self.used_size()
    def first_fit(self, req_size: int):
        for i, p in enumerate(self.partitions):
            if p.is_free() and p.size >= req_size:
                return i
        return None
    def allocate(self, idx: int, pid: int, req_size: int):
        p = self.partitions[idx]
        p.owner_pid = pid
        p.occupied  = min(req_size, p.size)
    def free(self, idx: int):
        p = self.partitions[idx]
        p.owner_pid = None
        p.occupied  = 0

class Process:
    _next_pid = 100
    def __init__(self, mem_req_range=(1, 12), cpu_time_range=(20, 60)):
        self.pid = Process._next_pid; Process._next_pid += 1
        self.mem_required = randrange(mem_req_range[0], mem_req_range[1] + 1)
        self.mem_index = -1
        self.state = ProcState.BLOCKED
        self.cpu_remaining = randrange(cpu_time_range[0], cpu_time_range[1] + 1)
        self.io_remaining  = 0
        self.color = choice(["#6aa84f","#3c78d8","#e69138","#a64d79",
                             "#76a5af","#674ea7","#cc0000","#3d85c6"])

class Simulator:
    """Round Robin + memoria con particiones fijas (first-fit)."""
    def __init__(self, partitions_sizes=None, quantum=5,
                 cpu_time_range=(20, 60), prob_block=20, io_time_range=(3,8)):
        if partitions_sizes is None:
            partitions_sizes = [2,2,4,6,6,8,8,12,16]
        self.mem = Memory(partitions_sizes)
        self.all_procs: list[Process] = []
        self.wait_mem = deque()
        self.ready    = deque()
        self.blocked  = []
        self.running: Process | None = None

        self.quantum = max(1, int(quantum))
        self.quantum_left = self.quantum
        self.cpu_time_range = cpu_time_range
        self.prob_block = prob_block
        self.io_time_range = io_time_range

    def add_process(self):
        p = Process(cpu_time_range=self.cpu_time_range)
        self.all_procs.append(p)
        idx = self.mem.first_fit(p.mem_required)
        if idx is not None:
            self.mem.allocate(idx, p.pid, p.mem_required)
            p.mem_index = idx
            p.state = ProcState.READY
            self.ready.append(p)
        else:
            p.state = ProcState.BLOCKED
            self.wait_mem.append(p)

    def _try_admit_from_waiting(self):
        changed = True
        while changed and self.wait_mem:
            changed = False
            p = self.wait_mem[0]
            idx = self.mem.first_fit(p.mem_required)
            if idx is not None:
                self.mem.allocate(idx, p.pid, p.mem_required)
                p.mem_index = idx
                p.state = ProcState.READY
                self.ready.append(p)
                self.wait_mem.popleft()
                changed = True

    def _dispatch_if_needed(self):
        if self.running is None and self.ready:
            self.running = self.ready.popleft()
            self.running.state = ProcState.RUNNING
            self.quantum_left = self.quantum

    def _preempt(self):
        runnable = len(self.ready) + (1 if self.running else 0)
        if self.running and self.quantum_left <= 0 and runnable > 1:
            self.running.state = ProcState.READY
            self.ready.append(self.running)
            self.running = None

    def _finish_process(self, p: Process):
        p.state = ProcState.TERMINATED
        if p.mem_index >= 0:
            self.mem.free(p.mem_index)
            p.mem_index = -1
        self._try_admit_from_waiting()

    def _tick_running(self):
        if not self.running: return
        p = self.running
        p.cpu_remaining -= 1
        self.quantum_left -= 1
        if p.cpu_remaining <= 0:
            self._finish_process(p)
            self.running = None
            return
        if randrange(100) < self.prob_block:
            p.state = ProcState.BLOCKED
            p.io_remaining = randrange(self.io_time_range[0], self.io_time_range[1] + 1)
            self.blocked.append(p)
            self.running = None
            return
        self._preempt()

    def _tick_blocked(self):
        for p in list(self.blocked):
            if p.state != ProcState.BLOCKED:
                self.blocked.remove(p); continue
            if p.io_remaining > 0:
                p.io_remaining -= 1
            if p.io_remaining <= 0:
                p.state = ProcState.READY
                self.ready.append(p)
                self.blocked.remove(p)

    def step(self):
        self._try_admit_from_waiting()
        self._dispatch_if_needed()
        self._tick_running()
        self._tick_blocked()
        self._dispatch_if_needed()

# ============================
#   GUI
# ============================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Procesos y Memoria")
        self.geometry("1000x680")
        self.minsize(720, 480)

        # Modelo
        self.sim = Simulator(quantum=5, cpu_time_range=(20, 60))
        for _ in range(5):
            self.sim.add_process()

        # Layout base
        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")
        self.rowconfigure(0, weight=1)

        # Panel memoria
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Panel derecho
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        # Barra
        controls = ttk.Frame(right)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls.grid_columnconfigure(3, weight=1)
        self.auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text="Auto", variable=self.auto_var, command=self._toggle_loop)\
            .grid(row=0, column=0, padx=6, pady=2, sticky="w")
        ttk.Button(controls, text="Tick", command=self._tick_once)\
            .grid(row=0, column=1, padx=6, pady=2, sticky="w")
        ttk.Button(controls, text="Agregar proceso", command=self._add_proc)\
            .grid(row=0, column=2, padx=6, pady=2, sticky="w")
        ttk.Button(controls, text="Ajustes…", command=self._open_settings)\
            .grid(row=0, column=4, padx=6, pady=2, sticky="e")

        # Resumen y tabla
        self.summary = ttk.Label(right, text="", anchor="w", justify="left")
        self.summary.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.tree = ttk.Treeview(
            right, columns=("pid", "estado", "mem", "part", "cpu", "io"),
            show="headings", height=18
        )
        for col, text, w in [
            ("pid", "PID", 60), ("estado", "Estado", 110), ("mem", "Mem", 60),
            ("part", "Part", 60), ("cpu", "CPU restante", 100), ("io", "I/O restante", 100)
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.grid(row=2, column=0, sticky="nsew")

        # Ordenable con flechas y orden persistente
        self._setup_sorting()

        # Velocidad del loop
        self.ms_var = tk.IntVar(value=300)

        self._render_all()
        self.after(self.ms_var.get(), self._loop)

    # --- básicos ---
    def _add_proc(self): self.sim.add_process(); self._render_all()
    def _tick_once(self): self.sim.step(); self._render_all()
    def _toggle_loop(self):
        if self.auto_var.get():
            self.after(self.ms_var.get(), self._loop)
    def _loop(self):
        if self.auto_var.get():
            self.sim.step(); self._render_all(); self.after(self.ms_var.get(), self._loop)

    # ---------- AJUSTES (ventana) ----------
    def _open_settings(self):
        win = tk.Toplevel(self); win.title("Ajustes de simulación")
        win.grab_set(); win.resizable(False, False)
        frm = ttk.Frame(win, padding=12); frm.pack(fill="both", expand=True)

        # Velocidad
        ttk.Label(frm, text="Velocidad (ms por tick):").grid(row=0, column=0, sticky="e", pady=2)
        ms_var_local = tk.IntVar(value=self.ms_var.get())
        ttk.Entry(frm, width=8, textvariable=ms_var_local).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(frm, text="Cada tick avanza la simulación.\nMás ms = más lento; menos ms = más rápido.",
                  foreground="#555").grid(row=1, column=0, columnspan=2, sticky="w")

        # Quantum
        ttk.Label(frm, text="Quantum (Round Robin):").grid(row=2, column=0, sticky="e", pady=(10,2))
        quantum_var = tk.IntVar(value=self.sim.quantum)
        ttk.Entry(frm, width=8, textvariable=quantum_var).grid(row=2, column=1, sticky="w", padx=6)
        ttk.Label(frm, text="Ticks que un proceso puede usar CPU antes de ser desalojado\nsi hay otros listos.",
                  foreground="#555").grid(row=3, column=0, columnspan=2, sticky="w")

        # CPU inicial
        ttk.Label(frm, text="CPU inicial mín–máx (procesos nuevos):").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,2))
        cpu_min_var = tk.IntVar(value=self.sim.cpu_time_range[0])
        cpu_max_var = tk.IntVar(value=self.sim.cpu_time_range[1])
        ttk.Entry(frm, width=6, textvariable=cpu_min_var).grid(row=5, column=0, sticky="w")
        ttk.Entry(frm, width=6, textvariable=cpu_max_var).grid(row=5, column=1, sticky="w")
        ttk.Label(frm, text="Duración total de CPU de los procesos al crearse.",
                  foreground="#555").grid(row=6, column=0, columnspan=2, sticky="w")

        # Prob. bloqueo
        ttk.Label(frm, text="Prob. de bloqueo por tick (%):").grid(row=7, column=0, sticky="e", pady=(10,2))
        prob_block_var = tk.IntVar(value=self.sim.prob_block)
        ttk.Entry(frm, width=8, textvariable=prob_block_var).grid(row=7, column=1, sticky="w", padx=6)
        ttk.Label(frm, text="Probabilidad de que el proceso en CPU pase a Bloqueado (I/O).",
                  foreground="#555").grid(row=8, column=0, columnspan=2, sticky="w")

        # Rango I/O
        ttk.Label(frm, text="Rango de I/O mín–máx (ticks):").grid(row=9, column=0, columnspan=2, sticky="w", pady=(10,2))
        io_min_var = tk.IntVar(value=self.sim.io_time_range[0])
        io_max_var = tk.IntVar(value=self.sim.io_time_range[1])
        ttk.Entry(frm, width=6, textvariable=io_min_var).grid(row=10, column=0, sticky="w")
        ttk.Entry(frm, width=6, textvariable=io_max_var).grid(row=10, column=1, sticky="w")
        ttk.Label(frm, text="Cuántos ticks permanece bloqueado un proceso por I/O.",
                  foreground="#555").grid(row=11, column=0, columnspan=2, sticky="w")

        # Aplicar a existentes
        apply_existing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Aplicar nuevo rango de CPU a procesos existentes",
                        variable=apply_existing_var).grid(row=12, column=0, columnspan=2, sticky="w", pady=(10,0))
        ttk.Label(frm, text="Si está marcado, reasigna la CPU restante de los procesos activos al nuevo rango.",
                  foreground="#555").grid(row=13, column=0, columnspan=2, sticky="w")

        # Particiones (opcional)
        use_new_mem_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Reiniciar particiones de memoria", variable=use_new_mem_var)\
            .grid(row=14, column=0, columnspan=2, sticky="w", pady=(10,0))
        ttk.Label(frm, text="Si lo activás, ingresá una lista (ej: 4,4,8,16).\n"
                            "Se reinicia la memoria y los procesos vuelven a espera.",
                  foreground="#555").grid(row=15, column=0, columnspan=2, sticky="w")
        mem_parts_var = tk.StringVar(value="2,2,4,6,6,8,8,12,16")
        mem_entry = ttk.Entry(frm, width=30, textvariable=mem_parts_var, state="disabled")
        mem_entry.grid(row=16, column=0, columnspan=2, sticky="ew", pady=(2,0))
        def toggle_entry(*_):
            mem_entry.configure(state="normal" if use_new_mem_var.get() else "disabled")
        use_new_mem_var.trace_add("write", toggle_entry)

        # Botones
        btns = ttk.Frame(frm); btns.grid(row=17, column=0, columnspan=2, pady=(16,0), sticky="e")
        ttk.Button(btns, text="Cancelar", command=win.destroy).pack(side="right", padx=6)
        def apply_and_close():
            try:
                ms=int(ms_var_local.get()); q=int(quantum_var.get())
                cmin=int(cpu_min_var.get()); cmax=int(cpu_max_var.get())
                pbl=int(prob_block_var.get()); iomin=int(io_min_var.get()); iomax=int(io_max_var.get())
                assert ms>=10 and q>=1 and 1<=cmin<cmax and 0<=pbl<=100 and 1<=iomin<=iomax
                if use_new_mem_var.get():
                    new_parts=[int(x) for x in mem_parts_var.get().split(",") if x.strip()]
                    assert new_parts and all(s>0 for s in new_parts)
            except Exception:
                messagebox.showerror("Error","Valores inválidos."); return

            self.ms_var.set(ms)
            self.sim.quantum = q
            self.sim.cpu_time_range = (cmin, cmax)
            self.sim.prob_block = pbl
            self.sim.io_time_range = (iomin, iomax)

            if apply_existing_var.get():
                for p in self.sim.all_procs:
                    if p.state != ProcState.TERMINATED:
                        p.cpu_remaining = max(1, randrange(cmin, cmax + 1))

            if use_new_mem_var.get():
                self.sim.mem = Memory(new_parts)
                new_wait = [p for p in self.sim.all_procs if p.state != ProcState.TERMINATED]
                for p in new_wait:
                    p.state = ProcState.BLOCKED
                    p.mem_index = -1
                    p.io_remaining = 0
                self.sim.wait_mem = deque(new_wait)
                self.sim.ready = deque()
                self.sim.blocked = []
                self.sim.running = None

            self._render_all()
            win.destroy()
        ttk.Button(btns, text="Aplicar", command=apply_and_close).pack(side="right")

    # ---------- RENDER ----------
    def _render_all(self):
        self._render_memory()
        self._render_processes()
        self._render_summary()

    def _render_summary(self):
        total = self.sim.mem.total_size()
        used  = self.sim.mem.used_size()
        free  = total - used
        ready = sum(p.state == ProcState.READY for p in self.sim.all_procs)
        running = 1 if self.sim.running else 0
        blocked = sum(p.state == ProcState.BLOCKED for p in self.sim.all_procs)
        term    = sum(p.state == ProcState.TERMINATED for p in self.sim.all_procs)
        wait_mem= len(self.sim.wait_mem)
        cpu_rng = f"{self.sim.cpu_time_range[0]}–{self.sim.cpu_time_range[1]}"
        self.summary.config(text=(
            f"Memoria: usada {used}/{total} (libre {free}) | "
            f"Listo: {ready} Ejecutando: {running} Bloqueado: {blocked} "
            f"Terminado: {term} Espera Memoria: {wait_mem} | "
            f"CPU inicial: {cpu_rng} | Quantum: {self.sim.quantum} | ms/tick: {self.ms_var.get()}"
        ))

    def _render_memory(self):
        self.canvas.delete("all")
        W = self.canvas.winfo_width() or 450
        H = self.canvas.winfo_height() or 450
        blocks = self.sim.mem.partitions
        margin = 20; gap = 10
        total_h = H - 2*margin - gap*(len(blocks)-1)
        block_h = total_h / len(blocks) if blocks else 0
        x0, x1 = margin, W - margin
        pid2color = {p.pid: p.color for p in self.sim.all_procs}

        for i, blk in enumerate(blocks):
            y0 = margin + i*(block_h + gap); y1 = y0 + block_h
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="#aaa", width=2)
            if blk.is_free():
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="#2b2b2b", outline="")
                self.canvas.create_text(x0+8, (y0+y1)/2, anchor="w", fill="#ddd",
                                        text=f"Bloque {i} size={blk.size} (LIBRE)")
            else:
                frac = max(0.0, min(1.0, blk.occupied/blk.size if blk.size > 0 else 0))
                fill_w = x0 + frac*(x1 - x0)
                color = pid2color.get(blk.owner_pid, "#3da35a")
                self.canvas.create_rectangle(x0, y0, fill_w, y1, fill=color, outline="")
                self.canvas.create_rectangle(fill_w, y0, x1, y1, fill="#2b2b2b", outline="")
                self.canvas.create_text(x0+8, (y0+y1)/2, anchor="w", fill="#fff",
                                        text=f"Bloque {i} size={blk.size} used={blk.occupied} PID={blk.owner_pid}")

    def _render_processes(self):
        # limpiar la tabla
        for r in self.tree.get_children():
            self.tree.delete(r)

        rows = []
        for p in self.sim.all_procs:
            rows.append({
                "pid": p.pid,
                "estado": p.state.value,
                "mem": p.mem_required,
                "part": (p.mem_index if p.mem_index >= 0 else "-"),
                "cpu": p.cpu_remaining,
                "io": p.io_remaining,
            })

        # aplicar orden actual si hay
        if getattr(self, "_active_sort_col", None) is not None:
            col = self._active_sort_col
            reverse = self._active_sort_reverse

            def to_int(v):
                if isinstance(v, int): return v
                s = str(v).strip()
                if s in ("", "-"): return -10**12
                try: return int(s)
                except ValueError: return -10**12

            typ = self._col_types.get(col, "str")
            if typ == "int":
                rows.sort(key=lambda r: (to_int(r[col]), r["pid"]), reverse=reverse)
            else:
                rows.sort(key=lambda r: (str(r[col]).lower(), r["pid"]), reverse=reverse)

        for r in rows:
            self.tree.insert("", "end", values=(r["pid"], r["estado"], r["mem"], r["part"], r["cpu"], r["io"]))

    # ---------- ORDENAMIENTO PERSISTENTE ----------
    def _setup_sorting(self):
        self._col_types = {
            "pid": "int", "estado": "str", "mem": "int",
            "part": "int", "cpu": "int", "io": "int",
        }
        self._col_titles = {c: self.tree.heading(c, "text") for c in self._col_types}
        self._sort_reverse = {c: True for c in self._col_types}  # 1er click: DESC
        self._active_sort_col = None
        self._active_sort_reverse = None

        for col in self._col_types:
            self.tree.heading(
                col,
                text=self._col_titles[col],
                command=lambda c=col: self._sort_by(c, self._sort_reverse[c])
            )

    def _sort_by(self, col, reverse):
        # recordar elección para próximos renders
        self._active_sort_col = col
        self._active_sort_reverse = reverse

        # alternar para el próximo click
        self._sort_reverse[col] = not reverse

        # actualizar flechas en encabezados
        for c in self._col_types:
            base = self._col_titles[c]
            if c == col:
                base = f"{base} {'▼' if reverse else '▲'}"
            self.tree.heading(c, text=base,
                              command=lambda cc=c: self._sort_by(cc, self._sort_reverse[cc]))

        # re-render ordenado ya mismo
        self._render_processes()

if __name__ == "__main__":
    App().mainloop()
