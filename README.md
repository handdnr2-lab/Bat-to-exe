# Zscaler BAT Generator (체크박스 + 탭 기반)

명령어를 직접 입력하지 않고, GUI에서 **미리 정의된 파라미터를 체크박스로 선택**해 Zscaler Client Connector 설치 BAT를 생성하는 도구입니다.
또한 외부 bat2exe 실행파일 없이, 이 스크립트 내부 로직으로 BAT + Origin 파일을 합친 EXE를 생성할 수 있습니다.

## 기준 문서

- Supported Parameters for Zscaler Client Connector on Windows  
  https://help.zscaler.com/zscaler-client-connector/supported-parameters-zscaler-client-connector-windows

## 핵심 변경점

- 파라미터 **추가/삭제 방식 제거**
- 파라미터를 카테고리별 **탭으로 분리**
- 각 파라미터별로
  - 사용 여부 체크박스
  - 값 입력칸 제공
  - 우측에 파라미터 설명 표시
- `cloudName`은 드롭다운 선택 제공 (`zscaler`, `zscalerone`, `zscalertwo`, `zscalerthree`, `zscloud`)
- `mode`, `unattendedmodeui`, `strictEnforcement`는 `기본/자주 사용` 탭으로 이동
- `mode`는 드롭다운 선택 제공 (`unattended`, `win32(Default)`)
- `unattendedmodeui`는 드롭다운 선택 제공 (`none`, `minimal`, `minimalWithDialogs`)
- 주요 0/1 파라미터는 드롭다운을 `비활성화/활성화`(+ 기본값 표시)로 제공하고, BAT에는 실제 `0/1` 값으로 저장
- `enableSSO`는 `0/1/2(기본값)` 옵션 제공
- `installer-language`는 `English(기본값)/French` 표기로 제공되며 BAT에는 `en/fr`로 저장
- `strictEnforcement` 체크박스는 `cloudName` + `policyToken` 체크 시에만 활성화
- `unattendedmodeui` 체크박스는 `mode=unattended`일 때만 활성화
- 기본 체크값: `cloudName`, `userDomain`만 체크
- `/install` 옵션 제거
- `ZCC Origin File`은 단일 선택 항목이며, 이 파일을 EXE에 임베드하고 BAT 명령에는 파일명만 자동 사용
- `ZCC Origin File` 미선택 시 BAT에서는 기본값 `Zscaler-windows-4.7.0.168-installer-x64.exe` 사용

## 탭 구성

- 기본/자주 사용
- 설치/실행
- 보안/동작
- 네트워크/드라이버
- ZPA/고급
- 기타/유지보수

## 실행

```bash
python3 zscaler_bat_to_exe_gui.py
```

앱 아이콘은 코드의 `HARDCODED_ICON_DATA_URI`(data:image/png;base64,...) 상수로 하드코딩되어 있습니다.
`BAT+Origin -> EXE 생성` 시에도 동일 아이콘을 `.ico`로 내부 변환해 `/win32icon`으로 적용합니다.

## PyInstaller로 GUI EXE 만들기

```bash
pyinstaller --clean --noconfirm --onedir --console --name zcc-bat-builder zscaler_bat_to_exe_gui.py
```

위 명령(onedir/console) 기준으로 실행 시 GUI가 정상 동작하는 것을 확인했습니다.  
실행 시 문제가 있으면 빌드 산출물 폴더에서 `zcc_gui_startup_error.log`를 확인하세요.

## 사용 방법

1. `BAT File Name`, `ZCC Origin File`, `Custom ZCC File Name`, `Output Folder` 순서로 입력
2. 탭별로 필요한 파라미터 체크 + 값 입력
3. 중간의 참조 URL 클릭 시 브라우저에서 공식 문서 확인
4. Preview 확인
5. `BAT 생성` 또는 `BAT+Origin -> EXE 생성`

## EXE 생성(내장 빌더) 사용 방법

1. `ZCC Origin File`에 원본 EXE 파일 지정
2. `Output EXE Name` 지정
3. `BAT+Origin -> EXE 생성` 클릭

앱은 내부적으로 임시 스테이징 폴더를 만들고, `csc.exe`로 리소스 포함 C# 런처를 컴파일해 단일 EXE를 생성합니다.
컴파일 결과가 0KB이면 성공으로 처리하지 않고 오류로 안내합니다.
Windows 보안 프로그램으로 인해 생성 직후 파일 잠금이 발생할 수 있어, EXE 크기 확인/임시 정리 단계는 자동 재시도합니다.
컴파일 로그는 `output_dir/zcc_exe_build.log`에 저장됩니다.

생성 BAT는 최소 구성으로 `@echo off` + 설치 명령만 포함합니다.
BAT 실행 시 `cd /d "%~dp0"`를 먼저 수행해, 같은 폴더에 풀린 Origin EXE를 기준으로 실행합니다.
생성된 런처 EXE 실행 시, EXE와 같은 폴더의 `<Output EXE Name>_files` 하위에 BAT/Origin 파일을 풀고 BAT를 실행합니다.

## 주의

- 실제 적용 가능한 파라미터/값은 운영 정책 및 공식 문서를 반드시 기준으로 사용하세요.
- EXE 생성은 Windows 환경의 `csc.exe`(.NET Framework/SDK) 사용 가능 상태가 필요합니다.
