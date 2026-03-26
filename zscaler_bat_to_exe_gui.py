#!/usr/bin/env python3
"""Zscaler Client Connector BAT generator (tab + checkbox based)."""

from __future__ import annotations

import json
import os
import shutil
import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


DEFAULT_INSTALLER_EXE = "Zscaler-windows-4.7.0.168-installer-x64.exe"


@dataclass
class BuildConfig:
    output_dir: str = ""
    bat_name: str = "install_zscaler.bat"
    origin_file_path: str = ""
    output_exe_name: str = "zcc-custom.exe"


PARAMETER_TABS: list[tuple[str, list[str]]] = [
    (
        "기본/자주 사용",
        ["userDomain", "cloudName", "userName", "deviceToken", "policyToken"],
    ),
    (
        "설치/실행",
        ["mode", "unattendedmodeui", "hideAppUIOnLaunch", "launchTray", "installer-language", "installWebView2"],
    ),
    (
        "보안/동작",
        ["enableFips", "strictEnforcement", "enableAntiTampering", "enableImprivataIntegration", "enableSSO", "mtAuthRequired"],
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
MODE_OPTIONS = ["", "unattended", "win32(Default)"]
UNATTENDED_MODE_UI_OPTIONS = ["", "none", "minimal", "minimalWithDialogs"]
BOOLEAN_10_OPTIONS = ["", "1", "0"]

PARAMETER_DESCRIPTIONS: dict[str, str] = {
    "userDomain": "사용자 조직의 도메인 이름 (SAML NameID 기준 도메인)",
    "cloudName": "사용자가 연결될 Zscaler 클라우드 이름",
    "userName": "사용자 계정 이름 (도메인 제외)",
    "deviceToken": "Zscaler Client Connector Portal에서 발급된 디바이스 인증 토큰",
    "policyToken": "사용자 등록 전에 적용할 App Profile 정책을 지정하는 토큰",
    "enableFips": "FIPS 규격을 준수하는 보안 라이브러리 사용 여부",
    "externalDeviceId": "MDM과 Zscaler 간 디바이스를 매핑하기 위한 식별자",
    "hideAppUIOnLaunch": "사용자 등록 전 앱 UI를 숨길지 여부",
    "strictEnforcement": "사용자 등록 전 인터넷 접근을 차단하는 강제 정책 모드",
    "reinstallDriver": "기존 드라이버가 있어도 강제로 재설치 여부",
    "mode": "무인 설치(사용자 개입 없이 설치) 여부 설정",
    "unattendedmodeui": "무인 설치 시 사용자에게 표시되는 UI 수준",
    "uninstallPasswordCmdLine": "무인 제거 시 사용할 비밀번호",
    "enableAntiTampering": "사용자가 프로그램을 중지/변경/삭제하지 못하도록 보호",
    "enableImprivataIntegration": "Imprivata OneSign과의 연동 기능 활성화",
    "bcpConfigFilePath": "장애 상황 시 사용할 Business Continuity 설정 파일 경로",
    "bcpMAPublicKeyHash": "Business Continuity 설정 파일 검증용 공개키 값",
    "importSEFailCloseConfig": "strict enforcement 모드에서 사용할 fail-close 설정 파일",
    "failCloseConfigThumbprint": "fail-close 설정 파일 검증용 공개키 값",
    "revertzcc": "이전 버전으로 되돌리기(롤백) 수행 여부",
    "revertPasswordCmdLine": "롤백 수행 시 사용할 비밀번호",
    "installer-language": "설치 프로그램에서 사용할 언어",
    "installWebView2": "WebView2 프레임워크 설치 여부",
    "enableSSO": "Windows 계정 기반 SSO 인증 사용 여부",
    "LWFBootStart": "LWF 드라이버를 부팅 시 자동 시작하도록 설정",
    "useLWFDriver": "패킷 필터 기반 LWF 드라이버 사용 여부",
    "installLWFDriver": "NDIS 기반 LWF 드라이버 설치 여부",
    "vdi": "VDI(가상 데스크탑 환경)에서 설치 여부",
    "externalRedirect": "브라우저 기반 인증 방식 사용 여부",
    "configTimeout": "설정 파일 다운로드 대기 시간(초)",
    "mtAuthRequired": "머신 터널 시작 전에 사용자 인증을 요구할지 여부",
    "upgradePasswordCmdLine": "무인 업그레이드 시 사용할 비밀번호",
    "enableCustomProxyDetection": "초기 정책 다운로드 시 커스텀 방식으로 프록시 탐지",
    "launchTray": "설치 후 프로그램을 자동 실행할지 여부",
}


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Zscaler BAT Generator")
        self.root.geometry("980x740")

        self.vars = {
            "output_dir": tk.StringVar(value=str(Path.cwd() / "build")),
            "bat_name": tk.StringVar(value="install_zscaler.bat"),
            "origin_file_path": tk.StringVar(),
            "output_exe_name": tk.StringVar(value="zcc-custom.exe"),
        }
        self.param_vars: dict[str, dict[str, tk.Variable]] = {}
        self.param_checkbuttons: dict[str, ttk.Checkbutton] = {}

        self._build_ui()
        self._refresh_preview()

    def _build_ui(self) -> None:
        base = ttk.Frame(self.root)
        base.pack(fill="both", expand=True)

        form = ttk.LabelFrame(base, text="기본 설정")
        form.pack(fill="x", padx=10, pady=10)

        self._add_path_row(form, "Output Folder", "output_dir", 0)
        self._add_entry_row(form, "BAT File Name", "bat_name", 1)
        self._add_origin_row(form, "ZCC Origin File", "origin_file_path", 2)
        self._add_entry_row(form, "Output EXE Name", "output_exe_name", 3)

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
        ttk.Button(actions, text="BAT+Origin -> EXE 생성", command=self.generate_exe).pack(side="right", padx=5)
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

            on_toggle = lambda p=param: self._on_param_toggle(p)
            chk = ttk.Checkbutton(parent, text=f"--{param}", variable=enabled_var, command=on_toggle)
            chk.grid(row=row_idx, column=0, sticky="w", padx=8, pady=4)

            if param == "cloudName":
                entry = ttk.Combobox(parent, textvariable=value_var, values=CLOUD_NAME_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._refresh_preview())
            elif param == "mode":
                entry = ttk.Combobox(parent, textvariable=value_var, values=MODE_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._on_mode_changed())
            elif param == "unattendedmodeui":
                entry = ttk.Combobox(parent, textvariable=value_var, values=UNATTENDED_MODE_UI_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._refresh_preview())
            elif param in {"hideAppUIOnLaunch", "launchTray"}:
                entry = ttk.Combobox(parent, textvariable=value_var, values=BOOLEAN_10_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._refresh_preview())
            elif param == "strictEnforcement":
                entry = ttk.Combobox(parent, textvariable=value_var, values=BOOLEAN_10_OPTIONS, state="readonly", width=42)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<<ComboboxSelected>>", lambda _: self._refresh_preview())
            else:
                entry = ttk.Entry(parent, textvariable=value_var, width=45)
                entry.grid(row=row_idx, column=1, sticky="ew", padx=8, pady=4)
                entry.bind("<KeyRelease>", lambda _: self._refresh_preview())

            desc = PARAMETER_DESCRIPTIONS.get(param, "")
            ttk.Label(parent, text=desc, wraplength=360, justify="left").grid(row=row_idx, column=2, sticky="w", padx=8, pady=4)

            parent.columnconfigure(1, weight=1)
            self.param_vars[param] = {"enabled": enabled_var, "value": value_var}
            self.param_checkbuttons[param] = chk

        self._update_unattended_mode_ui_state()
        self._update_strict_enforcement_state()

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

    def _add_origin_row(self, parent: ttk.Widget, label: str, key: str, row: int) -> None:
        self._add_entry_row(parent, label, key, row)

        def browse() -> None:
            chosen = filedialog.askopenfilename(
                title="Origin EXE 선택",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            )
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

    def _build_install_command(self, cfg: BuildConfig, selected: list[tuple[str, str]]) -> str:
        origin_name = Path(cfg.origin_file_path).name if cfg.origin_file_path.strip() else DEFAULT_INSTALLER_EXE
        parts = [origin_name]
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
        cfg = self._collect_config()
        cmd = self._build_install_command(cfg, self._collect_selected_parameters())
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
        bat_path.write_text(self._bat_content(self._build_install_command(cfg, self._collect_selected_parameters())), encoding="utf-8")
        messagebox.showinfo("완료", f"BAT 생성 완료:\n{bat_path}")

    def generate_exe(self) -> None:
        cfg = self._collect_config()
        if not cfg.origin_file_path.strip():
            messagebox.showerror("오류", "ZCC Origin File을 지정해 주세요.")
            return
        if not Path(cfg.origin_file_path).exists():
            messagebox.showerror("오류", f"Origin 파일을 찾을 수 없습니다:\n{cfg.origin_file_path}")
            return

        out_dir = Path(cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        bat_path = out_dir / cfg.bat_name
        bat_path.write_text(self._bat_content(self._build_install_command(cfg, self._collect_selected_parameters())), encoding="utf-8")

        stage = Path(tempfile.mkdtemp(prefix="zcc_embed_"))
        try:
            staged_bat = stage / cfg.bat_name
            staged_origin = stage / Path(cfg.origin_file_path).name
            shutil.copy2(bat_path, staged_bat)
            shutil.copy2(cfg.origin_file_path, staged_origin)

            csc_path = self._find_csc()
            if not csc_path:
                messagebox.showerror(
                    "실행 실패",
                    "C# 컴파일러(csc.exe)를 찾을 수 없습니다.\nWindows .NET SDK 또는 .NET Framework Developer Pack을 설치해 주세요.",
                )
                return

            wrapper_source = stage / "ZccEmbeddedLauncher.cs"
            wrapper_source.write_text(
                self._build_wrapper_source(
                    bat_name=staged_bat.name,
                    origin_name=staged_origin.name,
                    output_name=cfg.output_exe_name,
                ),
                encoding="utf-8",
            )

            compiled_exe = stage / "compiled_launcher.exe"
            cmd = [
                str(csc_path),
                "/nologo",
                "/target:winexe",
                f"/out:{compiled_exe}",
                f"/resource:{staged_bat},{staged_bat.name}",
                f"/resource:{staged_origin},{staged_origin.name}",
                str(wrapper_source),
            ]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            except OSError as exc:
                messagebox.showerror("실행 실패", f"EXE 컴파일 중 오류:\n{exc}")
                return

            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "Unknown error").strip()
                messagebox.showerror("컴파일 실패", f"Exit code {proc.returncode}\n{detail}")
                return

            if not compiled_exe.exists():
                detail = (proc.stderr or proc.stdout or "No compiler output").strip()
                messagebox.showerror("컴파일 실패", f"컴파일 출력 파일이 생성되지 않았습니다.\n{detail}")
                return

            size = compiled_exe.stat().st_size
            if size == 0:
                detail = (proc.stderr or proc.stdout or "Compiler returned success but produced empty file").strip()
                messagebox.showerror(
                    "컴파일 실패",
                    f"출력 EXE 크기가 0KB 입니다.\n"
                    f"csc 출력:\n{detail}",
                )
                return

            final_exe = out_dir / cfg.output_exe_name
            if final_exe.exists():
                final_exe.unlink()
            copied = False
            for _ in range(10):
                try:
                    shutil.copy2(compiled_exe, final_exe)
                    copied = True
                    break
                except PermissionError:
                    time.sleep(0.4)

            if not copied:
                messagebox.showerror(
                    "컴파일 실패",
                    "생성된 EXE 파일 접근이 거부되었습니다.\n"
                    "백신/보안프로그램이 파일을 잠시 점유했을 수 있습니다.\n"
                    "잠시 후 다시 시도해 주세요.",
                )
                return

        finally:
            for _ in range(10):
                try:
                    shutil.rmtree(stage, ignore_errors=False)
                    break
                except PermissionError:
                    time.sleep(0.3)
                except OSError:
                    break

        size_mb = final_exe.stat().st_size / (1024 * 1024)
        messagebox.showinfo("완료", f"EXE 생성 완료:\n{final_exe}\n크기: {size_mb:.2f} MB")

    @staticmethod
    def _find_csc() -> Path | None:
        in_path = shutil.which("csc")
        if in_path:
            return Path(in_path)

        windir = os.environ.get("WINDIR", "C:\\Windows")
        candidates = [
            Path(windir) / "Microsoft.NET" / "Framework" / "v4.0.30319" / "csc.exe",
            Path(windir) / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe",
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    @staticmethod
    def _build_wrapper_source(bat_name: str, origin_name: str, output_name: str) -> str:
        app_name = Path(output_name).stem or "zcc-custom"
        return f'''using System;\nusing System.Diagnostics;\nusing System.IO;\nusing System.Reflection;\n\nclass Program\n{{\n    static int Main()\n    {{\n        try\n        {{\n            var tempDir = Path.Combine(Path.GetTempPath(), "{app_name}_" + Guid.NewGuid().ToString("N"));\n            Directory.CreateDirectory(tempDir);\n\n            var originPath = Path.Combine(tempDir, "{origin_name}");\n            var batPath = Path.Combine(tempDir, "{bat_name}");\n\n            ExtractResource("{origin_name}", originPath);\n            ExtractResource("{bat_name}", batPath);\n\n            var psi = new ProcessStartInfo("cmd.exe", "/c \\"" + batPath + "\\"")\n            {{\n                WorkingDirectory = tempDir,\n                UseShellExecute = false,\n                CreateNoWindow = true,\n            }};\n\n            using (var p = Process.Start(psi))\n            {{\n                p.WaitForExit();\n                return p.ExitCode;\n            }}\n        }}\n        catch\n        {{\n            return 1;\n        }}\n    }}\n\n    static void ExtractResource(string name, string outputPath)\n    {{\n        var asm = Assembly.GetExecutingAssembly();\n        using (var input = asm.GetManifestResourceStream(name))\n        {{\n            if (input == null)\n                throw new Exception("Resource not found: " + name);\n            using (var output = File.Create(outputPath))\n                input.CopyTo(output);\n        }}\n    }}\n}}\n'''

    def reset_default_checks(self) -> None:
        for param, fields in self.param_vars.items():
            fields["enabled"].set(param in DEFAULT_ENABLED)
            if param not in DEFAULT_ENABLED:
                fields["value"].set("")
        self._update_unattended_mode_ui_state()
        self._update_strict_enforcement_state()
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

        self._update_unattended_mode_ui_state()
        self._update_strict_enforcement_state()
        self._refresh_preview()
        messagebox.showinfo("불러오기", f"Preset 불러오기 완료:\n{path}")

    def _on_mode_changed(self) -> None:
        self._update_unattended_mode_ui_state()
        self._refresh_preview()

    def _on_param_toggle(self, param: str) -> None:
        if param in {"mode", "cloudName", "policyToken"}:
            self._update_unattended_mode_ui_state()
            self._update_strict_enforcement_state()
        self._refresh_preview()

    def _update_unattended_mode_ui_state(self) -> None:
        mode_fields = self.param_vars.get("mode")
        if not mode_fields:
            return

        mode_value = str(mode_fields["value"].get()).strip()
        allow_unattended_ui = mode_value == "unattended"

        ui_checkbox = self.param_checkbuttons.get("unattendedmodeui")
        ui_fields = self.param_vars.get("unattendedmodeui")
        if not ui_checkbox or not ui_fields:
            return

        if allow_unattended_ui:
            ui_checkbox.state(["!disabled"])
        else:
            ui_fields["enabled"].set(False)
            ui_fields["value"].set("")
            ui_checkbox.state(["disabled"])

    def _update_strict_enforcement_state(self) -> None:
        cloud_fields = self.param_vars.get("cloudName")
        policy_fields = self.param_vars.get("policyToken")
        strict_fields = self.param_vars.get("strictEnforcement")
        strict_checkbox = self.param_checkbuttons.get("strictEnforcement")
        if not cloud_fields or not policy_fields or not strict_fields or not strict_checkbox:
            return

        allow = bool(cloud_fields["enabled"].get()) and bool(policy_fields["enabled"].get())
        if allow:
            strict_checkbox.state(["!disabled"])
        else:
            strict_fields["enabled"].set(False)
            strict_fields["value"].set("")
            strict_checkbox.state(["disabled"])


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
