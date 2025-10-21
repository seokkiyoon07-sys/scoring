# 변경 이력 (Changelog)

## [1.0.0] - 2025-10-15

### 추가 (Added)
- 초기 프로젝트 생성
- Streamlit 기반 웹 GUI 구현
- CSV 파일 업로드 기능 (학생 답안, 정답/배점)
- 과목코드별 자동 채점 로직
- 점수, 정답수, 오답번호 계산
- 통계 기능 (평균, 최고점, 최저점)
- 결과 CSV 다운로드
- UTF-8, CP949 인코딩 자동 감지
- 디버깅 모드 (파일 구조 및 채점 과정 표시)
- 샘플 데이터 파일 (sample_students.csv, sample_answers.csv)
- 개발 가이드 문서 (DEVELOPMENT_GUIDE.md)

### 수정 (Changed)
- pandas 버전 2.1.1 → 2.2.0+ (Python 3.13 호환)
- streamlit 버전 1.28.0 → 1.28.0+ (최신 안정 버전)

### 수정됨 (Fixed)
- 만점 계산 로직 개선 (정답지 기준으로 계산)
- 배점 타입 변환 오류 처리
- 문항 순서 정렬 (문항 번호 기준)
- Streamlit 첫 실행 시 이메일 입력 요청 제거 (config.toml 추가)

### 알려진 이슈 (Known Issues)
- `use_container_width` deprecation 경고 (기능에는 영향 없음)

---

## 향후 계획

### [1.1.0] (예정)
- [ ] 디버깅 모드 토글 기능
- [ ] 에러 메시지 개선
- [ ] 과목별 통계 추가

### [1.2.0] (예정)
- [ ] 엑셀 파일 직접 지원 (.xlsx)
- [ ] 문항별 정답률 분석
- [ ] 성적 분포 그래프

### [2.0.0] (장기)
- [ ] 사용자 계정 관리
- [ ] 채점 기록 저장
- [ ] REST API 제공

---

## 버전 관리 규칙

이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다:

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환되는 기능 추가
- **PATCH**: 하위 호환되는 버그 수정

### 변경 유형

- **Added**: 새로운 기능
- **Changed**: 기존 기능의 변경
- **Deprecated**: 곧 제거될 기능
- **Removed**: 제거된 기능
- **Fixed**: 버그 수정
- **Security**: 보안 취약점 수정


