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
import traceback
import base64
import webbrowser
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


DEFAULT_INSTALLER_EXE = "Zscaler-windows-4.7.0.168-installer-x64.exe"
HARDCODED_ICON_DATA_URI = "data:image/png;base64,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"


@dataclass
class BuildConfig:
    output_dir: str = ""
    bat_name: str = "install_zscaler.bat"
    origin_file_path: str = ""
    output_exe_name: str = "zcc-custom.exe"


PARAMETER_TABS: list[tuple[str, list[str]]] = [
    (
        "기본/자주 사용",
        ["userDomain", "cloudName", "userName", "deviceToken", "policyToken", "mode", "unattendedmodeui", "strictEnforcement"],
    ),
    (
        "설치/실행",
        ["hideAppUIOnLaunch", "launchTray", "installer-language", "installWebView2"],
    ),
    (
        "보안/동작",
        ["enableFips", "enableAntiTampering", "enableImprivataIntegration", "enableSSO", "mtAuthRequired"],
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
PARAM_OPTION_MAP: dict[str, list[tuple[str, str]]] = {
    "enableFips": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "hideAppUIOnLaunch": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "reinstallDriver": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "strictEnforcement": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "enableAntiTampering": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "enableImprivataIntegration": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "revertzcc": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "installWebView2": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "LWFBootStart": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "useLWFDriver": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "installLWFDriver": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "vdi": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "externalRedirect": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "mtAuthRequired": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "enableCustomProxyDetection": [("비활성화(기본값)", "0"), ("활성화", "1")],
    "launchTray": [("비활성화", "0"), ("활성화(기본값)", "1")],
    "enableSSO": [("0", "0"), ("1", "1"), ("2(기본값)", "2")],
    "installer-language": [("English(기본값)", "en"), ("French", "fr")],
}
REFERENCE_URL = "https://help.zscaler.com/zscaler-client-connector/customizing-zscaler-client-connector-install-options-exe"

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
        self._icon_image = None

        self.vars = {
            "output_dir": tk.StringVar(value=str(Path.cwd() / "build")),
            "bat_name": tk.StringVar(value="install_zscaler.bat"),
            "origin_file_path": tk.StringVar(),
            "output_exe_name": tk.StringVar(value="zcc-custom.exe"),
        }
        self.param_vars: dict[str, dict[str, tk.Variable]] = {}
        self.param_checkbuttons: dict[str, ttk.Checkbutton] = {}

        self._apply_hardcoded_icon()
        self._build_ui()
        self._refresh_preview()

    def _apply_hardcoded_icon(self) -> None:
        if "," not in HARDCODED_ICON_DATA_URI:
            return
        try:
            _, b64 = HARDCODED_ICON_DATA_URI.split(",", 1)
            base64.b64decode(b64)  # validate
            self._icon_image = tk.PhotoImage(data=b64)
            self.root.iconphoto(True, self._icon_image)
        except Exception:
            self._icon_image = None

    def _build_ui(self) -> None:
        base = ttk.Frame(self.root)
        base.pack(fill="both", expand=True)

        form = ttk.LabelFrame(base, text="기본 설정")
        form.pack(fill="x", padx=10, pady=10)

        self._add_entry_row(form, "BAT File Name", "bat_name", 0)
        self._add_origin_row(form, "ZCC Origin File", "origin_file_path", 1)
        self._add_entry_row(form, "Custom ZCC File Name", "output_exe_name", 2)
        self._add_path_row(form, "Output Folder", "output_dir", 3)

        tabs_frame = ttk.LabelFrame(base, text="파라미터 선택 (체크된 항목만 BAT에 포함)")
        tabs_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.notebook = ttk.Notebook(tabs_frame)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        for tab_name, params in PARAMETER_TABS:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tab_name)
            self._build_tab_rows(tab, params)

        link_frame = ttk.Frame(base)
        link_frame.pack(fill="x", padx=12, pady=(2, 6))
        ttk.Label(link_frame, text="참조 URL: ").pack(side="left")
        link = tk.Label(link_frame, text=REFERENCE_URL, fg="#1a73e8", cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda _e: webbrowser.open(REFERENCE_URL))

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
            elif param in PARAM_OPTION_MAP:
                options = [label for label, _value in PARAM_OPTION_MAP[param]]
                entry = ttk.Combobox(parent, textvariable=value_var, values=options, state="readonly", width=42)
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
                value = self._to_raw_value(param, value)
                selected.append((param, value))
        return selected

    @staticmethod
    def _to_raw_value(param: str, display_value: str) -> str:
        if param not in PARAM_OPTION_MAP:
            return display_value
        for label, raw in PARAM_OPTION_MAP[param]:
            if display_value == label or display_value == raw:
                return raw
        return display_value

    @staticmethod
    def _to_display_value(param: str, raw_value: str) -> str:
        if param not in PARAM_OPTION_MAP:
            return raw_value
        for label, raw in PARAM_OPTION_MAP[param]:
            if raw_value == raw or raw_value == label:
                return label
        return raw_value

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
cd /d "%~dp0"
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
                    "C# 컴파일러(csc.exe)를 찾을 수 없습니다.\n.NET Framework/SDK 설치를 확인해 주세요.",
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
            ]
            icon_ico = self._prepare_hardcoded_icon_ico(stage)
            if icon_ico:
                cmd.append(f"/win32icon:{icon_ico}")
            cmd.append(str(wrapper_source))
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            except OSError as exc:
                messagebox.showerror("실행 실패", f"csc 실행 중 오류:\n{exc}")
                return

            build_log = out_dir / "zcc_exe_build.log"
            build_log.write_text(
                f"CMD: {' '.join(cmd)}\n\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}\n",
                encoding="utf-8",
            )

            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "Unknown error").strip()
                messagebox.showerror("컴파일 실패", f"csc Exit code {proc.returncode}\n{detail}\n\n로그: {build_log}")
                return

            if not compiled_exe.exists():
                detail = (proc.stderr or proc.stdout or "No output").strip()
                messagebox.showerror("컴파일 실패", f"컴파일 출력 파일이 생성되지 않았습니다.\n{detail}")
                return

            size = 0
            for _ in range(30):
                try:
                    size = compiled_exe.stat().st_size
                    break
                except PermissionError:
                    time.sleep(0.5)

            if size == 0:
                detail = (proc.stderr or proc.stdout or "Compiler returned success but produced empty file").strip()
                messagebox.showerror(
                    "컴파일 실패",
                    f"출력 EXE 크기가 0KB 이거나 파일 잠금으로 읽을 수 없습니다.\n"
                    f"csc 출력:\n{detail}\n\n로그: {build_log}",
                )
                return

            final_exe = out_dir / cfg.output_exe_name
            tmp_final = out_dir / f"{cfg.output_exe_name}.tmp"
            copied = False
            for _ in range(30):
                try:
                    shutil.copyfile(compiled_exe, tmp_final)
                    copied = True
                    break
                except PermissionError:
                    time.sleep(0.5)

            if not copied:
                messagebox.showerror(
                    "컴파일 실패",
                    "컴파일 결과 EXE를 복사하지 못했습니다.\n"
                    "백신/보안프로그램이 파일을 점유 중일 수 있습니다.\n"
                    f"로그: {build_log}",
                )
                return

            if final_exe.exists():
                try:
                    final_exe.unlink()
                except OSError:
                    pass
            os.replace(tmp_final, final_exe)

        finally:
            for _ in range(10):
                try:
                    shutil.rmtree(stage, ignore_errors=False)
                    break
                except PermissionError:
                    time.sleep(0.3)
                except OSError:
                    break

        final_size = 0
        for _ in range(30):
            try:
                final_size = final_exe.stat().st_size
                break
            except PermissionError:
                time.sleep(0.3)
        size_mb = final_size / (1024 * 1024)
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
        return f'''using System;\nusing System.Diagnostics;\nusing System.IO;\nusing System.Reflection;\n\nclass Program\n{{\n    static int Main()\n    {{\n        try\n        {{\n            var baseDir = AppDomain.CurrentDomain.BaseDirectory;\n            var extractDir = Path.Combine(baseDir, "{app_name}_files");\n            Directory.CreateDirectory(extractDir);\n\n            var originPath = Path.Combine(extractDir, "{origin_name}");\n            var batPath = Path.Combine(extractDir, "{bat_name}");\n\n            ExtractResource("{origin_name}", originPath);\n            ExtractResource("{bat_name}", batPath);\n\n            var psi = new ProcessStartInfo("cmd.exe", "/c \\"" + batPath + "\\"")\n            {{\n                WorkingDirectory = extractDir,\n                UseShellExecute = false,\n                CreateNoWindow = true,\n            }};\n\n            using (var p = Process.Start(psi))\n            {{\n                p.WaitForExit();\n                return p.ExitCode;\n            }}\n        }}\n        catch\n        {{\n            return 1;\n        }}\n    }}\n\n    static void ExtractResource(string name, string outputPath)\n    {{\n        var asm = Assembly.GetExecutingAssembly();\n        using (var input = asm.GetManifestResourceStream(name))\n        {{\n            if (input == null)\n                throw new Exception("Resource not found: " + name);\n            using (var output = File.Create(outputPath))\n                input.CopyTo(output);\n        }}\n    }}\n}}\n'''

    def _prepare_hardcoded_icon_ico(self, stage: Path) -> Path | None:
        if "," not in HARDCODED_ICON_DATA_URI:
            return None
        try:
            _, b64 = HARDCODED_ICON_DATA_URI.split(",", 1)
            png_bytes = base64.b64decode(b64)
        except Exception:
            return None

        ico_path = stage / "hardcoded_icon.ico"
        try:
            # ICO 포맷(1개 이미지)로 직접 래핑. ICO 내부 이미지는 PNG 그대로 저장 가능.
            width = 0   # 0 means 256 in ICO
            height = 0  # 0 means 256 in ICO
            color_count = 0
            reserved = 0
            planes = 1
            bit_count = 32
            bytes_in_res = len(png_bytes)
            image_offset = 6 + 16  # ICONDIR + ICONDIRENTRY

            icon_dir = (
                (0).to_bytes(2, "little") +      # idReserved
                (1).to_bytes(2, "little") +      # idType
                (1).to_bytes(2, "little")        # idCount
            )
            icon_entry = (
                width.to_bytes(1, "little") +
                height.to_bytes(1, "little") +
                color_count.to_bytes(1, "little") +
                reserved.to_bytes(1, "little") +
                planes.to_bytes(2, "little") +
                bit_count.to_bytes(2, "little") +
                bytes_in_res.to_bytes(4, "little") +
                image_offset.to_bytes(4, "little")
            )

            ico_path.write_bytes(icon_dir + icon_entry + png_bytes)
            if ico_path.exists() and ico_path.stat().st_size > 0:
                return ico_path
        except Exception:
            return None
        return None

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
                    "value": self._to_raw_value(param, str(fields["value"].get())),
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
                raw = str(saved.get("value", ""))
                self.param_vars[param]["value"].set(self._to_display_value(param, raw))

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
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        log_path = Path.cwd() / "zcc_gui_startup_error.log"
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        try:
            messagebox.showerror("시작 실패", f"프로그램 시작 중 오류가 발생했습니다.\n로그: {log_path}")
        except Exception:
            pass
