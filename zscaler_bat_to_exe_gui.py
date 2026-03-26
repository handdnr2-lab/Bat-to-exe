#!/usr/bin/env python3
"""Zscaler Client Connector BAT generator (option-select GUI)."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class BuildConfig:
    output_dir: str = ""
    bat_name: str = "install_zscaler.bat"
    installer_name: str = "ZSATrayManager.exe"
    run_install_flag: bool = True


DEFAULT_PARAMETERS: list[tuple[str, str]] = [
    ("--cloudName", ""),
    ("--userDomain", ""),
    ("--mode", "unattended"),
    ("--hideAppUIOnLaunch", "1"),
]


class ParameterRow(ttk.Frame):
    def __init__(self, parent: ttk.Widget, on_change) -> None:
        super().__init__(parent)
        self.on_change = on_change

        self.key_var = tk.StringVar()
        self.value_var = tk.StringVar()

        self.key_entry = ttk.Entry(self, textvariable=self.key_var, width=24)
        self.key_entry.grid(row=0, column=0, padx=4, pady=2)

        self.value_entry = ttk.Entry(self, textvariable=self.value_var, width=42)
        self.value_entry.grid(row=0, column=1, padx=4, pady=2, sticky="ew")

        self.remove_btn = ttk.Button(self, text="삭제", width=8)
        self.remove_btn.grid(row=0, column=2, padx=4, pady=2)

        self.columnconfigure(1, weight=1)

        self.key_entry.bind("<KeyRelease>", lambda _: self.on_change())
        self.value_entry.bind("<KeyRelease>", lambda _: self.on_change())

    def set_values(self, key: str, value: str) -> None:
        self.key_var.set(key)
        self.value_var.set(value)

    def get_values(self) -> tuple[str, str]:
        return self.key_var.get().strip(), self.value_var.get().strip()


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Zscaler BAT Generator")
        self.root.geometry("900x670")

        self.vars = {
            "output_dir": tk.StringVar(value=str(Path.cwd() / "build")),
            "bat_name": tk.StringVar(value="install_zscaler.bat"),
            "installer_name": tk.StringVar(value="ZSATrayManager.exe"),
            "run_install_flag": tk.BooleanVar(value=True),
        }

        self.param_rows: list[ParameterRow] = []
        self._build_ui()

        for key, value in DEFAULT_PARAMETERS:
            self.add_row(key, value)
        self._refresh_preview()

    def _build_ui(self) -> None:
        base = ttk.Frame(self.root)
        base.pack(fill="both", expand=True)

        form = ttk.LabelFrame(base, text="기본 설정")
        form.pack(fill="x", padx=10, pady=10)

        self._add_path_row(form, "Output Folder", "output_dir", 0)
        self._add_entry_row(form, "BAT File Name", "bat_name", 1)
        self._add_entry_row(form, "Installer EXE Name", "installer_name", 2)
        ttk.Checkbutton(
            form,
            text="명령 끝에 /install 추가",
            variable=self.vars["run_install_flag"],
            command=self._refresh_preview,
        ).grid(row=3, column=1, sticky="w", padx=8, pady=6)

        param_box = ttk.LabelFrame(base, text="Zscaler 파라미터 (공식 문서값으로 편집)")
        param_box.pack(fill="both", expand=True, padx=10, pady=8)

        controls = ttk.Frame(param_box)
        controls.pack(fill="x", padx=8, pady=6)
        ttk.Button(controls, text="파라미터 추가", command=lambda: self.add_row("", "")).pack(side="left")
        ttk.Button(controls, text="기본값 리셋", command=self.reset_rows).pack(side="left", padx=6)

        self.rows_container = ttk.Frame(param_box)
        self.rows_container.pack(fill="both", expand=True, padx=8, pady=6)

        actions = ttk.Frame(base)
        actions.pack(fill="x", padx=10, pady=8)
        ttk.Button(actions, text="Preset 저장", command=self.save_preset).pack(side="left")
        ttk.Button(actions, text="Preset 불러오기", command=self.load_preset).pack(side="left", padx=5)
        ttk.Button(actions, text="BAT 생성", command=self.generate_bat).pack(side="right")

        preview_box = ttk.LabelFrame(base, text="BAT 내용 Preview")
        preview_box.pack(fill="both", expand=True, padx=10, pady=8)

        self.preview = tk.Text(preview_box, wrap="word", height=12)
        self.preview.pack(fill="both", expand=True, padx=8, pady=8)
        self.preview.configure(state="disabled")

    def _add_entry_row(self, parent: ttk.Widget, label: str, key: str, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=5)
        entry = ttk.Entry(parent, textvariable=self.vars[key], width=70)
        entry.grid(row=row, column=1, sticky="ew", padx=8, pady=5)
        entry.bind("<KeyRelease>", lambda _: self._refresh_preview())
        parent.columnconfigure(1, weight=1)

    def _add_path_row(self, parent: ttk.Widget, label: str, key: str, row: int) -> None:
        self._add_entry_row(parent, label, key, row)

        def browse() -> None:
            chosen = filedialog.askdirectory()
            if chosen:
                self.vars[key].set(chosen)
                self._refresh_preview()

        ttk.Button(parent, text="Browse", command=browse).grid(row=row, column=2, padx=5, pady=5)

    def add_row(self, key: str, value: str) -> None:
        row = ParameterRow(self.rows_container, self._refresh_preview)
        row.set_values(key, value)
        row.remove_btn.configure(command=lambda r=row: self.remove_row(r))
        row.pack(fill="x", pady=2)
        self.param_rows.append(row)
        self._refresh_preview()

    def remove_row(self, row: ParameterRow) -> None:
        if row in self.param_rows:
            self.param_rows.remove(row)
            row.destroy()
            self._refresh_preview()

    def reset_rows(self) -> None:
        for row in list(self.param_rows):
            self.remove_row(row)
        for key, value in DEFAULT_PARAMETERS:
            self.add_row(key, value)

    def _collect_config(self) -> BuildConfig:
        data = {k: v.get() for k, v in self.vars.items()}
        return BuildConfig(**data)

    def _collect_parameters(self) -> list[tuple[str, str]]:
        params = []
        for row in self.param_rows:
            key, value = row.get_values()
            if key:
                params.append((key, value))
        return params

    def _build_install_command(self, cfg: BuildConfig, params: list[tuple[str, str]]) -> str:
        parts = [cfg.installer_name]
        for key, value in params:
            parts.append(key)
            if value:
                parts.append(value)
        if cfg.run_install_flag:
            parts.append("/install")
        return " ".join(shlex.quote(x) for x in parts)

    def _bat_content(self, cfg: BuildConfig, command: str) -> str:
        return f"""@echo off
setlocal

echo Zscaler Client Connector install 시작...
{command}

if %errorlevel% neq 0 (
    echo 설치 실패: %errorlevel%
    exit /b %errorlevel%
)

echo 설치 완료
exit /b 0
"""

    def _refresh_preview(self) -> None:
        cfg = self._collect_config()
        cmd = self._build_install_command(cfg, self._collect_parameters())
        content = self._bat_content(cfg, cmd)

        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")

    def generate_bat(self) -> None:
        cfg = self._collect_config()
        if not cfg.output_dir.strip():
            messagebox.showerror("오류", "Output Folder를 입력해 주세요.")
            return

        out_dir = Path(cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = self._build_install_command(cfg, self._collect_parameters())
        content = self._bat_content(cfg, cmd)
        bat_path = out_dir / cfg.bat_name
        bat_path.write_text(content, encoding="utf-8")

        messagebox.showinfo("완료", f"BAT 생성 완료:\n{bat_path}")

    def save_preset(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return

        payload = {
            "config": asdict(self._collect_config()),
            "params": self._collect_parameters(),
        }
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        messagebox.showinfo("저장", f"Preset 저장 완료:\n{path}")

    def load_preset(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        for k, v in payload.get("config", {}).items():
            if k in self.vars:
                self.vars[k].set(v)

        for row in list(self.param_rows):
            self.remove_row(row)

        for key, value in payload.get("params", []):
            self.add_row(key, value)

        self._refresh_preview()
        messagebox.showinfo("불러오기", f"Preset 불러오기 완료:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
