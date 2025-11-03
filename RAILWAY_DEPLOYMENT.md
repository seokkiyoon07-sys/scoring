# Railway 배포 가이드

## 🚂 Railway란?

Railway는 간단하게 웹 애플리케이션을 배포할 수 있는 플랫폼입니다. GitHub 연동으로 자동 배포가 가능합니다.

---

## 📋 사전 요구사항

1. ✅ GitHub 계정
2. ✅ Railway 계정 (https://railway.app)
3. ✅ 이 프로젝트가 GitHub에 푸시되어 있어야 함

---

## 🚀 배포 단계

### 1단계: Railway 프로젝트 생성

1. Railway 웹사이트 접속: https://railway.app
2. "Start a New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. GitHub 계정 연동 (처음이라면)
5. 이 저장소 선택: `seokkiyoon07-sys/scoring`

### 2단계: 자동 배포 확인

Railway가 자동으로:
- ✅ `requirements.txt` 감지
- ✅ Python 환경 설정
- ✅ 패키지 설치
- ✅ Streamlit 앱 실행

### 3단계: 환경 변수 설정 (선택사항)

현재 프로젝트는 환경 변수가 필요하지 않지만, 나중에 필요하면:

1. Railway 대시보드에서 프로젝트 선택
2. "Variables" 탭 클릭
3. 환경 변수 추가

### 4단계: 도메인 설정

1. Railway 대시보드에서 "Settings" 탭
2. "Domains" 섹션
3. "Generate Domain" 클릭
4. 자동 생성된 도메인 확인 (예: `your-app.railway.app`)

---

## 📁 필요한 파일들

### ✅ 이미 있는 파일
- `requirements.txt` - Python 패키지 목록
- `app.py` - Streamlit 앱 메인 파일
- `.streamlit/config.toml` - Streamlit 설정

### ✅ 새로 생성된 파일
- `railway.toml` - Railway 배포 설정

---

## ⚙️ Railway 설정 파일 (`railway.toml`)

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 설정 설명
- `builder`: NIXPACKS 사용 (Railway 기본 빌더)
- `startCommand`: Streamlit 실행 명령어
- `--server.port $PORT`: Railway가 제공하는 포트 사용
- `--server.address 0.0.0.0`: 외부 접속 허용
- `healthcheckPath`: 헬스체크 경로
- `restartPolicyType`: 실패 시 재시작 정책

---

## 🔄 자동 배포

GitHub에 푸시하면 자동으로 Railway에 배포됩니다:

```bash
git add .
git commit -m "Update app"
git push origin main
```

Railway가 자동으로:
1. 변경사항 감지
2. 새로운 버전 빌드
3. 자동 배포
4. 이전 버전 교체

---

## 📊 배포 모니터링

### Railway 대시보드에서 확인 가능:
- 📈 CPU 사용량
- 💾 메모리 사용량
- 📡 네트워크 트래픽
- 📝 애플리케이션 로그

### 로그 확인
1. Railway 대시보드
2. "Deployments" 탭
3. 최신 배포 선택
4. "View Logs" 클릭

---

## 💰 요금

### Free Tier (무료)
- ✅ 월 $5 크레딧
- ✅ 1개 프로젝트
- ✅ 512MB 메모리
- ✅ 1GB 저장공간
- ✅ 커스텀 도메인 지원

### 예상 사용량
이 Streamlit 앱은:
- 메모리: ~200-300MB
- 트래픽: 적당 (파일 업로드/다운로드)
- **무료 플랜으로 충분합니다**

---

## 🐛 문제 해결

### 문제 1: 앱이 시작되지 않음
**해결**:
1. Railway 로그 확인
2. `requirements.txt` 패키지 버전 확인
3. Python 버전 확인

### 문제 2: 한글 폰트가 깨짐
**해결**:
현재 코드는 폰트가 없으면 자동으로 대체 폰트 사용:
```python
def setup_korean_font_for_pdf():
    try:
        # macOS 폰트 시도
        ...
    except:
        return 'Helvetica'  # 실패 시 기본 폰트
```

### 문제 3: 파일 업로드 크기 제한
**해결**:
`.streamlit/config.toml`에 이미 설정되어 있음:
```toml
[server]
maxUploadSize = 200
```

### 문제 4: 메모리 부족
**해결**:
1. Railway 대시보드에서 메모리 사용량 확인
2. 필요시 유료 플랜으로 업그레이드
3. 또는 코드 최적화 (대용량 DataFrame 처리)

---

## 🔒 보안 고려사항

### 현재 구현
- ✅ 파일 업로드만 지원 (데이터베이스 없음)
- ✅ 세션별로 데이터 분리
- ✅ 업로드된 파일은 메모리에만 저장

### 추가 권장사항
1. **HTTPS 자동 적용** (Railway 기본 제공)
2. **파일 크기 제한** (이미 설정됨: 200MB)
3. **악성 파일 검사** (필요시 추가)

---

## 📱 접속 방법

배포 후 다음 URL로 접속:
```
https://[your-app-name].railway.app
```

예시:
```
https://scoring-production.railway.app
```

---

## 🔄 업데이트 프로세스

### 코드 수정 후 배포

```bash
# 1. 코드 수정
vim app.py

# 2. 테스트
streamlit run app.py

# 3. Git에 커밋
git add .
git commit -m "Update: 기능 개선"

# 4. GitHub에 푸시 (자동 배포)
git push origin main
```

Railway가 자동으로:
- ✅ 변경사항 감지
- ✅ 새 버전 빌드
- ✅ 무중단 배포 (zero-downtime)
- ✅ 롤백 가능 (이전 버전으로)

---

## 📚 추가 자료

- [Railway 공식 문서](https://docs.railway.app)
- [Streamlit 배포 가이드](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [Railway Streamlit Template](https://github.com/railwayapp-templates/streamlit)

---

## ✅ 배포 체크리스트

배포 전 확인:
- [ ] `requirements.txt` 최신화
- [ ] `.streamlit/config.toml` 확인
- [ ] `railway.toml` 생성
- [ ] GitHub에 최신 코드 푸시
- [ ] Railway 프로젝트 생성
- [ ] GitHub 저장소 연결
- [ ] 자동 배포 확인
- [ ] 생성된 도메인 접속 테스트
- [ ] 파일 업로드/다운로드 기능 테스트
- [ ] 한글 표시 확인

배포 후 확인:
- [ ] 앱이 정상 작동하는지 확인
- [ ] 모든 기능 테스트
- [ ] 로그에 에러 없는지 확인
- [ ] 메모리/CPU 사용량 모니터링

---

**작성일**: 2025-11-03
**버전**: 1.0
**작성자**: Claude Code
