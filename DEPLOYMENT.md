# 배포 가이드 (Deployment Guide)

## 🌐 배포 옵션 비교

| 방법 | 난이도 | 비용 | 서버 관리 | 추천도 |
|------|-------|------|----------|--------|
| **Streamlit Cloud** | ⭐ | 무료 | 불필요 | ⭐⭐⭐⭐⭐ |
| **Google Cloud Run** | ⭐⭐⭐ | 무료 티어 | 불필요 | ⭐⭐⭐⭐ |
| **Heroku** | ⭐⭐ | 월 $7~ | 불필요 | ⭐⭐⭐ |
| **AWS EC2** | ⭐⭐⭐⭐ | 월 $5~ | 필요 | ⭐⭐ |

---

## 방법 1: Streamlit Cloud (추천! 🎯)

### 장점
- ✅ 완전 무료 (공개 앱)
- ✅ 가장 쉬움 (5분 배포)
- ✅ 서버 관리 불필요
- ✅ HTTPS 자동
- ✅ GitHub 연동 자동 재배포

### 단계별 가이드

#### 1단계: GitHub에 코드 업로드

```bash
cd /Volumes/SeokkiMAC/Coding/Myproject/OCR/scoring

# Git 초기화 (아직 안 했다면)
git init

# .gitignore 확인 (이미 있음)
cat .gitignore

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: 자동 채점 시스템"

# GitHub에 새 repo 만들기 (웹에서)
# https://github.com/new
# Repository name: scoring-system
# Public 선택 (무료 배포를 위해)

# Remote 추가
git remote add origin https://github.com/YOUR_USERNAME/scoring-system.git

# 푸시
git branch -M main
git push -u origin main
```

#### 2단계: Streamlit Cloud 설정

1. **https://streamlit.io/cloud** 접속
2. **Sign in with GitHub** 클릭
3. **New app** 클릭
4. Repository 선택: `YOUR_USERNAME/scoring-system`
5. Main file path: `app.py`
6. **Deploy!** 클릭

#### 3단계: 완료!

- 배포 완료까지 2~3분 소요
- URL 예시: `https://your-app.streamlit.app`
- 이 URL을 누구나 접근 가능!

### 업데이트 방법

```bash
# 코드 수정 후
git add .
git commit -m "기능 개선"
git push

# Streamlit Cloud가 자동으로 재배포됨! (30초~1분)
```

### 제약사항

- RAM: 1GB
- CPU: 공유
- 동시 사용자: 제한 있음 (정확한 수치 미공개)
- Public repo 필요 (private는 월 $20)

### 비용

- **무료!** (제한 내에서)

---

## 방법 2: Google Cloud Run (서버리스 🚀)

### 장점
- ✅ 진짜 서버리스 (사용한 만큼만 과금)
- ✅ 무료 티어 넉넉함
- ✅ 자동 스케일링
- ✅ 더 많은 리소스

### 준비물
- Google Cloud 계정 (카드 등록 필요, 무료 티어 있음)
- Docker 설치

### 단계별 가이드

#### 1단계: Dockerfile 생성

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일 복사
COPY . .

# Streamlit 포트
EXPOSE 8501

# Streamlit 실행
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2단계: .dockerignore 생성

```
# .dockerignore
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist/
build/
.git/
.gitignore
README.md
DEVELOPMENT_GUIDE.md
CHANGELOG.md
.DS_Store
```

#### 3단계: GCP 설정 및 배포

```bash
# Google Cloud SDK 설치 (아직 안 했다면)
brew install --cask google-cloud-sdk

# GCP 로그인
gcloud auth login

# 프로젝트 생성
gcloud projects create scoring-system-PROJECT_ID
gcloud config set project scoring-system-PROJECT_ID

# Cloud Run API 활성화
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 배포
gcloud run deploy scoring-app \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated

# 배포 완료! URL 출력됨
```

#### 4단계: 업데이트

```bash
# 코드 수정 후
gcloud run deploy scoring-app --source . --region asia-northeast3
```

### 비용

**무료 티어 (매월):**
- 요청: 200만 건
- CPU 시간: 36만 초
- 메모리: 18만 GB초
- 트래픽: 1GB

일반적인 사용에서는 **거의 무료**로 운영 가능!

초과 시 과금:
- 요청당 $0.40 / 백만 건
- vCPU 초당 $0.00001042
- 메모리 GB 초당 $0.000001094

### 예상 비용 예시

- 월 100명 사용자, 각 10회 채점 = 1,000회
- 1회당 5초 소요
- **예상 비용: $0.00** (무료 티어 내)

---

## 방법 3: Heroku (간단하지만 유료 💰)

### 장점
- ✅ 쉬운 배포
- ✅ Git 푸시로 배포

### 단점
- ❌ 무료 티어 없음 (월 $7~)

### 단계별 가이드

#### 1단계: Heroku 설정 파일 생성

```bash
# Procfile 생성
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# setup.sh 생성
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
EOF
```

#### 2단계: Heroku 배포

```bash
# Heroku CLI 설치
brew tap heroku/brew && brew install heroku

# Heroku 로그인
heroku login

# 앱 생성
heroku create scoring-system-YOUR-NAME

# 배포
git push heroku main

# 앱 열기
heroku open
```

### 비용
- Eco: 월 $5
- Basic: 월 $7
- Standard: 월 $25~

---

## 방법 4: Docker + 자체 서버 (고급 🖥️)

### AWS EC2 예시

```bash
# 1. EC2 인스턴스 생성 (Ubuntu)
# 2. SSH 접속
ssh -i key.pem ubuntu@ec2-xxx.amazonaws.com

# 3. Docker 설치
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker

# 4. 코드 가져오기
git clone https://github.com/YOUR_USERNAME/scoring-system.git
cd scoring-system

# 5. Docker 이미지 빌드
sudo docker build -t scoring-app .

# 6. 컨테이너 실행
sudo docker run -d -p 80:8501 --name scoring scoring-app

# 7. 도메인 연결 (선택)
# Route 53이나 CloudFlare에서 도메인 → EC2 IP 연결
```

### 비용
- EC2 t2.micro (무료 티어 1년): 무료
- 이후: 월 $5~10

---

## 🎯 상황별 추천

### 1. 개인/소규모 팀 (무료로 써야 함)
→ **Streamlit Cloud** ⭐⭐⭐⭐⭐

### 2. 중규모 (50명 이상 동시 사용)
→ **Google Cloud Run** ⭐⭐⭐⭐

### 3. 회사 업무용 (안정성 중요)
→ **AWS EC2 + Docker** 또는 **Cloud Run** ⭐⭐⭐⭐

### 4. 학교 과제/시연용
→ **Streamlit Cloud** (5분 배포) ⭐⭐⭐⭐⭐

---

## 보안 고려사항

### 배포 시 추가해야 할 것

#### 1. 비밀번호 보호 (선택)

```python
# app.py 최상단에 추가
import streamlit as st

def check_password():
    """비밀번호 확인"""
    def password_entered():
        if st.session_state["password"] == "your_password_here":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "비밀번호", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "비밀번호", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 비밀번호가 틀렸습니다")
        return False
    else:
        return True

if not check_password():
    st.stop()

# 나머지 코드...
```

#### 2. 환경 변수 사용 (secrets)

**Streamlit Cloud:**
```toml
# .streamlit/secrets.toml (로컬)
password = "your_password"

# Streamlit Cloud 대시보드에서도 설정 가능
```

```python
# app.py에서 사용
import streamlit as st
password = st.secrets["password"]
```

**Google Cloud Run:**
```bash
gcloud run deploy scoring-app \
  --set-env-vars PASSWORD=your_password
```

#### 3. HTTPS 강제

- Streamlit Cloud: 자동 제공 ✅
- Cloud Run: 자동 제공 ✅
- EC2: Let's Encrypt + Nginx 필요

---

## 도메인 연결 (선택)

### Streamlit Cloud
```
1. Streamlit 대시보드에서 Custom Domain 설정
2. DNS에서 CNAME 레코드 추가
   scoring.yourdomain.com → your-app.streamlit.app
```

### Cloud Run
```bash
# 도메인 매핑
gcloud run domain-mappings create \
  --service scoring-app \
  --domain scoring.yourdomain.com \
  --region asia-northeast3
```

---

## 모니터링

### Streamlit Cloud
- 대시보드에서 로그 확인
- 기본 메트릭 제공

### Cloud Run
```bash
# 로그 확인
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# 메트릭 확인 (Cloud Console)
```

---

## 문제 해결

### 메모리 부족
```python
# 큰 파일 처리 시 청크로 읽기
df = pd.read_csv(file, chunksize=1000)
```

### 타임아웃
```python
# Streamlit Cloud: 기본 타임아웃 5분
# Cloud Run: 최대 60분 설정 가능
gcloud run deploy --timeout=3600
```

---

## 다음 단계

1. **디버깅 모드 끄기** (배포 전)
2. **보안 추가** (비밀번호 등)
3. **사용자 가이드** 페이지 추가
4. **에러 처리** 강화

---

**Last Updated**: 2025-10-15
**Recommended**: Streamlit Cloud (무료, 쉬움, 5분 배포)



