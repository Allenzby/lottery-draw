# -*- coding: utf-8 -*-
"""幸运摇号软件 - 从配置文件指定的范围内随机抽取指定数量的数字（不重复）"""

import json
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk

DEFAULT_CONFIG = {
    "title": "幸运摇号",
    "min": 1,
    "max": 100,
    "default_count": 5,
    "animation_ms": 1500,
    "interval_ms": 60,
}


def base_dir():
    """程序所在目录（打包成 exe 后为 exe 所在文件夹）"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(base_dir(), "config.json")

# 窗口图标（PNG 的 base64 数据，由 make_icon.py 生成）
ICON_PNG_B64 = "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"


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if not os.path.exists(CONFIG_PATH):
        save_config(cfg)
        return cfg
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            cfg.update(data)
    except Exception as e:
        messagebox.showerror("配置错误", "config.json 读取失败：\n%s\n\n将使用默认配置。" % e)
    return cfg


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


class LotteryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_config()

        self.min_value, self.max_value = self._validate_range()
        self.pool_size = self.max_value - self.min_value + 1

        root.title(self.cfg.get("title", "幸运摇号"))
        root.configure(bg="#f4f6fb")
        root.resizable(False, False)

        # 设置窗口图标
        try:
            self._icon_img = tk.PhotoImage(data=ICON_PNG_B64, format="png")
            root.iconphoto(True, self._icon_img)
        except Exception:
            pass

        self.count_var = tk.StringVar(value=str(self.cfg.get("default_count", 5)))
        self.status_var = tk.StringVar(value="准备就绪")
        self.running = False
        self.after_id = None
        self.cells = []

        self._build_ui()
        self._center()
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- 配置校验 ----------
    def _validate_range(self):
        try:
            lo = int(self.cfg.get("min", 1))
            hi = int(self.cfg.get("max", 100))
        except (TypeError, ValueError):
            lo, hi = 1, 100
        if lo > hi:
            lo, hi = hi, lo
        self.cfg["min"], self.cfg["max"] = lo, hi
        if hi - lo + 1 <= 0:
            lo, hi = 1, 1
            self.cfg["min"], self.cfg["max"] = lo, hi
        return lo, hi

    # ---------- 界面 ----------
    def _build_ui(self):
        pad = {"padx": 24}
        title_font = ("Microsoft YaHei UI", 22, "bold")
        normal_font = ("Microsoft YaHei UI", 12)

        header = tk.Frame(self.root, bg="#2f54eb", height=78)
        header.pack(fill="x", **pad)
        header.pack_propagate(False)
        tk.Label(
            header, text=self.cfg.get("title", "幸运摇号"), font=title_font,
            bg="#2f54eb", fg="white"
        ).pack(side="left", padx=16)

        info = tk.Frame(self.root, bg="#f4f6fb")
        info.pack(fill="x", pady=(18, 0), **pad)
        tk.Label(
            info,
            text="抽取范围：%d ~ %d（共 %d 个数字）" % (self.min_value, self.max_value, self.pool_size),
            font=("Microsoft YaHei UI", 13, "bold"), bg="#f4f6fb", fg="#1f2937"
        ).pack(anchor="w")

        # 输入区
        form = tk.Frame(self.root, bg="#f4f6fb")
        form.pack(fill="x", pady=(14, 0), **pad)

        tk.Label(form, text="摇号数量：", font=normal_font, bg="#f4f6fb").pack(side="left")
        self.count_spin = ttk.Spinbox(
            form, from_=1, to=self.pool_size, textvariable=self.count_var,
            width=8, font=("Microsoft YaHei UI", 13), justify="center"
        )
        self.count_spin.pack(side="left")
        tk.Label(form, text="(最多 %d)" % self.pool_size, font=("Microsoft YaHei UI", 10),
                 bg="#f4f6fb", fg="#6b7280").pack(side="left", padx=(6, 0))

        self.start_btn = tk.Button(
            form, text="开始摇号", font=("Microsoft YaHei UI", 14, "bold"),
            bg="#2f54eb", fg="white", activebackground="#1d3fd0", activeforeground="white",
            disabledforeground="#dbe4ff", relief="flat", width=14, height=1,
            cursor="hand2", command=self.start
        )
        self.start_btn.pack(side="right")

        # 结果区
        self.result_frame = tk.Frame(self.root, bg="white", highlightbackground="#e5e7eb",
                                     highlightthickness=1)
        self.result_frame.pack(fill="both", expand=True, pady=(16, 0), padx=23)

        # 状态栏
        tk.Label(self.root, textvariable=self.status_var, font=("Microsoft YaHei UI", 10),
                 bg="#f4f6fb", fg="#6b7280").pack(anchor="w", padx=24, pady=(8, 14))

    def _center(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry("+%d+%d" % (x, y))

    # ---------- 结果展示 ----------
    def _clear_cells(self):
        for w in self.result_frame.winfo_children():
            w.destroy()
        self.cells = []

    def _make_cells(self, count):
        self._clear_cells()
        per_row = min(count, 5) if count >= 5 else count
        rows = (count + per_row - 1) // per_row
        for r in range(rows):
            self.result_frame.grid_rowconfigure(r, weight=1, uniform="r")
            for c in range(per_row):
                idx = r * per_row + c
                if idx >= count:
                    break
                self.result_frame.grid_columnconfigure(c, weight=1, uniform="c")
                cell = tk.Label(
                    self.result_frame, text="?", font=("Consolas", 30, "bold"),
                    bg="#eef2ff", fg="#2f54eb", width=5, height=1,
                    relief="solid", bd=1, highlightbackground="#c7d2fe"
                )
                cell.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
                self.cells.append(cell)
        return per_row, rows

    def _result_size(self, count):
        per_row = min(count, 5) if count >= 5 else count
        rows = (count + per_row - 1) // per_row
        cell_w = 110
        cell_h = 78
        width = max(560, per_row * (cell_w + 20) + 40)
        height = max(220, rows * (cell_h + 20) + 60)
        return width, height

    def _resize_window(self, want_w, want_h):
        self.root.update_idletasks()
        cur_w = self.root.winfo_width()
        cur_h = self.root.winfo_height()
        cur_fh = self.result_frame.winfo_height()
        new_w = max(cur_w, want_w + 46)
        new_h = max(cur_h, cur_h - cur_fh + want_h)
        if (new_w, new_h) != (cur_w, cur_h):
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry("%dx%d+%d+%d" % (new_w, new_h, x, y))
            self.root.update_idletasks()

    # ---------- 逻辑 ----------
    def start(self):
        if self.running:
            return
        try:
            count = int(str(self.count_var.get()).strip())
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的摇号数量（整数）。")
            return
        if count < 1 or count > self.pool_size:
            messagebox.showwarning("提示", "摇号数量必须在 1 ~ %d 之间。" % self.pool_size)
            return

        self.count_var.set(str(count))
        self.running = True
        self.start_btn.config(state="disabled", text="摇号中…")
        self.status_var.set("正在摇号，请稍候…")

        # 调整窗口/结果区大小以容纳结果
        w, h = self._result_size(count)
        self._resize_window(w, h)
        self._make_cells(count)

        # 最终结果：范围内不重复随机抽取
        self.final_numbers = random.sample(range(self.min_value, self.max_value + 1), count)

        # 动画参数
        try:
            animation_ms = int(self.cfg.get("animation_ms", 1500))
            interval = max(30, int(self.cfg.get("interval_ms", 60)))
        except (TypeError, ValueError):
            animation_ms, interval = 1500, 60

        self.tick = 0
        self.animate_until = animation_ms // interval

        def step():
            if not self.running:
                return
            self.tick += 1
            if self.tick > self.animate_until:
                # 动画结束，一次性揭晓全部结果
                for cell, num in zip(self.cells, self.final_numbers):
                    cell.config(text=str(num), bg="#dcfce7", fg="#15803d")
                self._finish()
                return
            # 滚动动画：所有格子随机跳数字
            for cell in self.cells:
                cell.config(text=str(random.randint(self.min_value, self.max_value)))
            self.after_id = self.root.after(interval, step)

        self.after_id = self.root.after(interval, step)

    def _finish(self):
        self.running = False
        self.after_id = None
        self.start_btn.config(state="normal", text="开始摇号")
        self.result = list(self.final_numbers)
        self.status_var.set("完成！共抽出 %d 个数字：%s" % (
            len(self.final_numbers),
            "、".join(str(n) for n in sorted(self.final_numbers))
        ))

    def _on_close(self):
        if self.after_id is not None:
            self.running = False
            self.root.after_cancel(self.after_id)
        save_config(self.cfg)
        self.root.destroy()


def main():
    root = tk.Tk()
    LotteryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
