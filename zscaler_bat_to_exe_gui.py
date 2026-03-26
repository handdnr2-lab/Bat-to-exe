#!/usr/bin/env python3
"""Zscaler Client Connector BAT generator (tab + checkbox based)."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


INSTALLER_EXE = "ZSATrayManager.exe"


@dataclass
class BuildConfig:
    output_dir: str = ""
    bat_name: str = "install_zscaler.bat"


PARAMETER_TABS: list[tuple[str, list[str]]] = [
    (
        "기본/자주 사용",
        ["userDomain", "cloudName", "userName", "deviceToken", "policyToken"],
    ),
    (
        "보안/동작",
        ["enableFips", "strictEnforcement", "enableAntiTampering", "enableSSO", "mtAuthRequired"],
    ),
    (
        "설치/실행",
        ["mode", "unattendedmodeui", "hideAppUIOnLaunch", "launchTray", "installer-language"],
    ),
    (
        "네트워크/드라이버",
        ["useLWFDriver", "installLWFDriver", "LWFBootStart", "reinstallDriver", "enableCustomProxyDetection"],
    ),
    (
        "ZPA/고급",
        ["bcpConfigFilePath", "bcpMAPublicKeyHash", "importSEFailCloseConfig", "failCloseConfigThumbprint"],
    ),
    (
        "기타/유지보수",
        [
            "externalDeviceId",
            "externalRedirect",
            "configTimeout",
            "vdi",
            "uninstallPasswordCmdLine",
            "revertzcc",
            "revertPasswordCmdLine",
            "upgradePasswordCmdLine",
        ],
    ),
]

DEFAULT_ENABLED = {"cloudName", "userDomain"}
CLOUD_NAME_OPTIONS = ["", "zscaler", "zscalerone", "zscalertwo", "zscalerthree", "zscloud"]


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Zscaler BAT Generator")
        self.root.geometry("980x740")

        self.vars = {
            "output_dir": tk.StringVar(value=str(Path.cwd() / "build")),
            "bat_name": tk.StringVar(value="install_zscaler.bat"),
        }
        self.param_vars: dict[str, dict[str, tk.Variable]] = {}

        self._build_ui()
        self._refresh_preview()

    def _build_ui(self) -> None:
        base = ttk.Frame(self.root)
        base.pack(fill="both", expand=True)

        form = ttk.LabelFrame(base, text="기본 설정")
        form.pack(fill="x", padx=10, pady=10)

        self._add_path_row(form, "Output Folder", "output_dir", 0)
        self._add_entry_row(form, "BAT File Name", "bat_name", 1)

        tabs_frame = ttk.LabelFrame(base, text="파라미터 선택 (체크된 항목만 BAT에 포함)")
        tabs_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.notebook = ttk.Notebook(tabs_frame)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        for tab_name, params in PARAMETER_TABS:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tab_name)
            self._build_tab_rows(tab, params)

        actions = ttk.Frame(base)
        actions.pack(fill="x", padx=10, pady=8)
        ttk.Button(actions, text="Preset 저장", command=self.save_preset).pack(side="left")
        ttk.Button(actions, text="Preset 불러오기", command=self.load_preset).pack(side="left", padx=5)
        ttk.Button(actions, text="기본 체크 복원", command=self.reset_default_checks).pack(side="left", padx=5)
        ttk.Button(actions, text="BAT 생성", command=self.generate_bat).pack(side="right")

        preview_box = ttk.LabelFrame(base, text="BAT 내용 Preview")
        preview_box.pack(fill="both", expand=True, padx=10, pady=8)

        self.preview = tk.Text(preview_box, wrap="word", height=12)
        self.preview.pack(fill="both", expand=True, padx=8, pady=8)
        self.preview.configure(state="disabled")

    def _build_tab_rows(self, parent: ttk.Frame, params: list[str]) -> None:
        for row_idx, param in enumerate(params):
            enabled_var = tk.BooleanVar(value=param in DEFAULT_ENABLED)
            value_var = tk.StringVar()

            chk = ttk.Checkbutton(parent, text=f"--{param}", variable=enabled_var, command=self._refresh_preview)
            chk.grid(row=row_idx, column=0, sticky="w", padx=8, pady=4)

            if param == "cloudName":
                entry = ttk.Combobox(parent, textvariable=value_var, values=CLOUD_NAME_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._refresh_preview())
            else:
                entry = ttk.Entry(parent, textvariable=value_var, width=45)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<KeyRelease>", lambda _: self._refresh_preview())

            ttk.Label(parent, text="값(비우면 플래그만 추가)").grid(row=row_idx, column=2, sticky="w", padx=8, pady=4)

            parent.columnconfigure(1, weight=1)
            self.param_vars[param] = {"enabled": enabled_var, "value": value_var}

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

    def _collect_config(self) -> BuildConfig:
        return BuildConfig(**{k: v.get() for k, v in self.vars.items()})

    def _collect_selected_parameters(self) -> list[tuple[str, str]]:
        selected: list[tuple[str, str]] = []
        for param, fields in self.param_vars.items():
            if bool(fields["enabled"].get()):
                value = str(fields["value"].get()).strip()
                selected.append((param, value))
        return selected

    def _build_install_command(self, selected: list[tuple[str, str]]) -> str:
        parts = [INSTALLER_EXE]
        for param, value in selected:
            parts.append(f"--{param}")
            if value:
                parts.append(value)
        return " ".join(shlex.quote(x) for x in parts)

    def _bat_content(self, command: str) -> str:
        return f"""@echo off
{command}
"""

    def _refresh_preview(self) -> None:
        cmd = self._build_install_command(self._collect_selected_parameters())
        content = self._bat_content(cmd)

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

        bat_path = out_dir / cfg.bat_name
        bat_path.write_text(self._bat_content(self._build_install_command(self._collect_selected_parameters())), encoding="utf-8")
        messagebox.showinfo("완료", f"BAT 생성 완료:\n{bat_path}")

    def reset_default_checks(self) -> None:
        for param, fields in self.param_vars.items():
            fields["enabled"].set(param in DEFAULT_ENABLED)
            if param not in DEFAULT_ENABLED:
                fields["value"].set("")
        self._refresh_preview()

    def save_preset(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return

        payload = {
            "config": asdict(self._collect_config()),
            "params": {
                param: {
                    "enabled": bool(fields["enabled"].get()),
                    "value": str(fields["value"].get()),
                }
                for param, fields in self.param_vars.items()
            },
        }
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        messagebox.showinfo("저장", f"Preset 저장 완료:\n{path}")

    def load_preset(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        for key, val in payload.get("config", {}).items():
            if key in self.vars:
                self.vars[key].set(val)

        for param, saved in payload.get("params", {}).items():
            if param in self.param_vars:
                self.param_vars[param]["enabled"].set(bool(saved.get("enabled", False)))
                self.param_vars[param]["value"].set(str(saved.get("value", "")))

        self._refresh_preview()
        messagebox.showinfo("불러오기", f"Preset 불러오기 완료:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
