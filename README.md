# PDF AI Chatbot

PDF 문서를 업로드하고 내용에 대해 질문할 수 있는 로컬 AI 챗봇입니다. Ollama와 LangChain을 사용하여 완전히 로컬에서 동작합니다.

## 기능
- PDF 파일 업로드 및 텍스트 추출
- 문서 내용 기반 질의응답
- 로컬 LLM 모델 사용 (외부 API 불필요)
- 실시간 채팅 인터페이스

## 배포 방법

### 🚀 빠른 시작 (Docker Hub) ⭐

가장 간단한 방법입니다. Docker만 있으면 바로 실행할 수 있습니다.

```bash
# 한 번에 실행
docker run -p 8501:8501 -p 11434:11434 hhaminlee/pdf-chatbot:latest

# 백그라운드 실행 (권장)
docker run -d -p 8501:8501 -p 11434:11434 --name pdf-chatbot hhaminlee/pdf-chatbot:latest
```

**브라우저에서 접속:** `http://localhost:8501`

---

### 🐳 Docker로 빌드해서 사용

소스코드를 수정하거나 개발하려는 경우 사용합니다.

#### 요구사항
- Docker & Docker Compose
- 최소 8GB RAM
- 15GB 이상 디스크 공간

#### 실행 방법

1. **저장소 클론**
```bash
git clone <repository-url>
cd scouterlab
```

2. **Docker로 실행**
```bash
docker-compose up --build
```

3. **브라우저 접속**
```
http://localhost:8501
```

#### Docker 명령어
```bash
# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down

# 완전 제거 (볼륨 포함)
docker-compose down -v
```

---

### 🛠️ 로컬 개발 환경

#### 요구사항

**1. Ollama 설치**
```bash
# macOS
brew install ollama

# 또는 공식 사이트에서 다운로드
# https://ollama.ai
```

**2. 필요한 모델 다운로드**
```bash
# Ollama 서비스 시작
ollama serve

# 새 터미널에서 모델 다운로드
ollama pull qwen3:8b
ollama pull llama3.2
ollama pull mistral
ollama pull embeddinggemma
```

#### 설치 및 실행

**1. 저장소 클론**
```bash
git clone <repository-url>
cd scouterlab
```

**2. Python 의존성 설치**
```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

**3. 실행**
```bash
# Ollama 서버 시작 (별도 터미널)
ollama serve

# 애플리케이션 실행
uv run streamlit run app.py
```

**4. 브라우저 접속**
```
http://localhost:8501
```

---

## 사용법

1. **모델 선택**: 사이드바에서 사용할 Ollama 모델 선택
2. **PDF 업로드**: 분석하고 싶은 PDF 파일 업로드
3. **설정 조정**: 텍스트 청크 크기와 오버랩 조정 (선택사항)
4. **질문하기**: 오른쪽 채팅창에서 PDF 내용에 대해 질문

## Docker Hub에 배포하기 (개발자용)

자세한 Docker Hub 배포 가이드는 [DOCKER_HUB_DEPLOY.md](DOCKER_HUB_DEPLOY.md)를 참고하세요.

**간단 요약:**
```bash
# 이미지 빌드 및 태그
docker build -t hhaminlee/pdf-chatbot:latest .

# Docker Hub에 푸시
docker push hhaminlee/pdf-chatbot:latest
```

## 기술 스택

- **Streamlit**: 웹 인터페이스
- **Ollama**: 로컬 LLM 실행
- **LangChain**: RAG 파이프라인
- **FAISS**: 벡터 데이터베이스
- **PyPDF**: PDF 텍스트 추출
- **Docker**: 컨테이너화 배포

## 지원 모델

- qwen3:8b (기본)
- llama3.2
- mistral
- embeddinggemma (임베딩 전용)

## 배포 방식 비교

| 방식 | 장점 | 단점 | 추천 대상 |
|------|------|------|-----------|
| Docker Hub | ⚡ 빠른 실행, 간편함 | 커스터마이징 어려움 | 일반 사용자 |
| 로컬 빌드 | 🔧 커스터마이징 가능 | 빌드 시간, 복잡함 | 개발자 |
| 로컬 설치 | 🎯 완전한 제어 | 수동 설정 필요 | 개발/연구용 |

## 문제해결

### Docker 관련
```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs pdf-chatbot

# 컨테이너 재시작
docker restart pdf-chatbot
```

### 로컬 설치 관련
```bash
# Ollama 연결 확인
curl http://localhost:11434/api/version

# 모델 목록 확인
ollama list

# 포트 사용 확인
lsof -i :11434
lsof -i :8501
```

## 시스템 요구사항

| 구분 | 최소 | 권장 |
|------|------|------|
| RAM | 8GB | 16GB+ |
| 디스크 | 15GB | 25GB+ |
| CPU | 4코어 | 8코어+ |

## 라이센스

MIT License

---

## 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 지원

문제가 있거나 질문이 있으시면 [Issues](https://github.com/hhaminlee/scouterlab/issues)에 등록해주세요.