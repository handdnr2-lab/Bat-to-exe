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
- `mode`는 드롭다운 선택 제공 (`unattended`, `win32(Default)`)
- `unattendedmodeui`는 드롭다운 선택 제공 (`none`, `minimal`, `minimalWithDialogs`)
- `hideAppUIOnLaunch` 드롭다운 선택 제공 (`1`, `0`)
- `launchTray` 드롭다운 선택 제공 (`1`, `0`)
- `strictEnforcement` 드롭다운 선택 제공 (`1`, `0`)
- `strictEnforcement` 체크박스는 `cloudName` + `policyToken` 체크 시에만 활성화
- `unattendedmodeui` 체크박스는 `mode=unattended`일 때만 활성화
- 기본 체크값: `cloudName`, `userDomain`만 체크
- `/install` 옵션 제거
- `ZCC Origin File`은 Browse로 선택하며, 경로 없이 파일명만 BAT에 포함
- `ZCC Origin File` 기본값: `Zscaler-windows-4.7.0.168-installer-x64.exe`

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

## 사용 방법

1. `Output Folder`, `BAT File Name` 입력
2. `ZCC Origin File`을 Browse로 선택 (파일명만 사용)
3. 탭별로 필요한 파라미터 체크 + 값 입력
4. Preview 확인
5. `BAT 생성` 또는 `BAT+Origin -> EXE 생성`

## EXE 생성(내장 빌더) 사용 방법

1. `Embed Origin File`에 포함할 원본 EXE 파일 지정
2. `Output EXE Name` 지정
3. `BAT+Origin -> EXE 생성` 클릭

앱은 내부적으로 임시 스테이징 폴더를 만들고, BAT/Origin 파일을 Base64로 포함한 C# 런처 코드를 생성한 뒤 `csc.exe`로 단일 EXE를 컴파일합니다.

생성 BAT는 최소 구성으로 `@echo off` + 설치 명령만 포함합니다.

## 주의

- 실제 적용 가능한 파라미터/값은 운영 정책 및 공식 문서를 반드시 기준으로 사용하세요.
- EXE 생성은 Windows 환경의 `csc.exe`(.NET Framework/SDK) 사용 가능 상태가 필요합니다.
