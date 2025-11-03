# 🚀 자동 채점 시스템 배포 가이드

## 📋 목차
- [Streamlit Community Cloud 배포 (추천)](#streamlit-community-cloud-배포-추천)
- [Railway 배포](#railway-배포)
- [Render 배포](#render-배포)

---

## 🌟 Streamlit Community Cloud 배포 (추천)

### ✅ 장점
- 완전 무료
- 가장 쉬운 배포
- GitHub 연동 자동 배포
- Streamlit 공식 호스팅

### 📝 배포 단계

#### 1. GitHub에 코드 푸시

```bash
# 현재 디렉토리에서
git add .
git commit -m "Add scoring app"
git push origin main
```

#### 2. Streamlit Community Cloud 접속

1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭

#### 3. 앱 설정

- **Repository**: `your-username/scoring` 선택
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL**: 원하는 URL 입력 (예: `scoring-app`)

#### 4. Deploy 클릭!

몇 분 후 앱이 배포됩니다:
```
https://scoring-app.streamlit.app
```

### ⚙️ 환경 설정

앱 설정에서 Secrets 추가 가능 (API 키 등):
```toml
# .streamlit/secrets.toml
[passwords]
admin = "your-password"
```

---

## 🚂 Railway 배포

### 1. Railway 계정 생성
https://railway.app

### 2. 프로젝트 생성

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 생성
railway init

# 배포
railway up
```

### 3. 환경 변수 설정

Railway 대시보드에서:
- `PORT`: 자동 설정됨
- 커스텀 도메인 설정 가능

### 4. 배포 명령어

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

**비용**: 월 $5 크레딧 제공

---

## 🎨 Render 배포

### 1. Render 계정 생성
https://render.com

### 2. Web Service 생성

- "New Web Service" 클릭
- GitHub 레포지토리 연결
- 다음 설정 입력:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

**Environment Variables:**
```
PYTHON_VERSION=3.10
```

### 3. Deploy!

**비용**: 무료 티어 제공 (앱이 비활성 시 슬립 모드)

---

## 📊 플랫폼 비교

| 플랫폼 | 비용 | 난이도 | 속도 | 추천도 |
|--------|------|--------|------|--------|
| Streamlit Cloud | 무료 | ⭐ (가장 쉬움) | 빠름 | ⭐⭐⭐⭐⭐ |
| Railway | $5/월 | ⭐⭐ | 빠름 | ⭐⭐⭐⭐ |
| Render | 무료 (슬립) | ⭐⭐ | 중간 | ⭐⭐⭐ |
| Heroku | $5/월~ | ⭐⭐⭐ | 빠름 | ⭐⭐ |

---

## 🔧 문제 해결

### 한글 폰트가 깨져요
Streamlit Cloud에서는 기본 한글 폰트가 없을 수 있습니다.

**해결 방법:**
1. `packages.txt` 파일에 폰트 패키지 추가
2. 또는 웹 폰트 사용

### 메모리 부족 오류
- Streamlit Cloud는 1GB RAM 제한
- 대용량 데이터는 청크로 처리
- 캐싱 활용 (`@st.cache_data`)

### 앱이 느려요
```python
# 데이터 캐싱 추가
@st.cache_data
def load_student_data(file):
    # ...
```

---

## 📞 지원

- Streamlit 커뮤니티: https://discuss.streamlit.io
- 문서: https://docs.streamlit.io


