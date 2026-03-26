# Zscaler BAT Generator (옵션 선택형)

명령어를 직접 입력하지 않고, GUI에서 옵션을 선택해 **Zscaler Client Connector 설치 BAT 파일**을 생성하는 도구입니다.

요청사항에 맞춰 **1차 목표는 BAT 파일 생성만** 지원합니다. (EXE 컴파일 기능 제외)

## 기준 문서

- Supported Parameters for Zscaler Client Connector on Windows  
  https://help.zscaler.com/zscaler-client-connector/supported-parameters-zscaler-client-connector-windows

## 주요 기능

- Output 폴더, BAT 파일명, 설치 실행 파일명 설정
- Zscaler 파라미터를 행 단위로 추가/삭제
  - 예: `--cloudName`, `--userDomain`, `--mode unattended`
- `/install` 플래그 포함 여부 선택
- BAT 내용 실시간 Preview
- Preset(JSON) 저장/불러오기

## 실행

```bash
python3 zscaler_bat_to_exe_gui.py
```

## 사용 순서

1. `Output Folder`와 `BAT File Name` 입력
2. 파라미터를 공식 문서 기준으로 추가/수정
3. 필요 시 `/install` 플래그 체크
4. `BAT 생성` 클릭

## 기본 파라미터 템플릿

앱 실행 시 아래 값이 기본으로 들어갑니다.

- `--cloudName`
- `--userDomain`
- `--mode unattended`
- `--hideAppUIOnLaunch 1`

> 실제 배포 시 파라미터 이름/값은 반드시 운영 중인 Zscaler 정책 및 공식 문서와 일치하도록 조정하세요.
