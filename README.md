# Zscaler BAT Generator (체크박스 + 탭 기반)

명령어를 직접 입력하지 않고, GUI에서 **미리 정의된 파라미터를 체크박스로 선택**해 Zscaler Client Connector 설치 BAT를 생성하는 도구입니다.

## 기준 문서

- Supported Parameters for Zscaler Client Connector on Windows  
  https://help.zscaler.com/zscaler-client-connector/supported-parameters-zscaler-client-connector-windows

## 핵심 변경점

- 파라미터 **추가/삭제 방식 제거**
- 파라미터를 카테고리별 **탭으로 분리**
- 각 파라미터별로
  - 사용 여부 체크박스
  - 값 입력칸 제공 (비우면 플래그만 포함)
- 기본 체크값: `cloudName`, `userDomain`만 체크
- `/install` 옵션 제거
- `installer exe name` 입력 제거 (내부에서 `ZSATrayManager.exe` 사용)

## 탭 구성

- 기본/자주 사용
- 보안/동작
- 설치/실행
- 네트워크/드라이버
- ZPA/고급
- 기타/유지보수

## 실행

```bash
python3 zscaler_bat_to_exe_gui.py
```

## 사용 방법

1. `Output Folder`, `BAT File Name` 입력
2. 탭별로 필요한 파라미터 체크 + 값 입력
3. Preview 확인
4. `BAT 생성`

## 주의

- 실제 적용 가능한 파라미터/값은 운영 정책 및 공식 문서를 반드시 기준으로 사용하세요.
