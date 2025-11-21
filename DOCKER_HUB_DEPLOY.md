# Docker Hub 배포 가이드

## Docker Hub에 이미지 업로드하기

### 1. 준비사항
- Docker Hub 계정 생성 (https://hub.docker.com)
- Docker Desktop 설치 및 실행

### 2. Docker Hub 로그인
```bash
docker login
```

### 3. 이미지 빌드 및 태그
```bash
# 이미지 빌드
docker build -t hhaminlee/pdf-chatbot:latest .

# 추가 태그 (버전 관리)
docker tag hhaminlee/pdf-chatbot:latest hhaminlee/pdf-chatbot:v1.0.0
```

### 4. Docker Hub에 푸시
```bash
# latest 태그 푸시
docker push hhaminlee/pdf-chatbot:latest

# 버전 태그 푸시
docker push hhaminlee/pdf-chatbot:v1.0.0
```

### 5. 자동 빌드 설정 (선택사항)

**GitHub Actions를 통한 자동 빌드**

`.github/workflows/docker.yml` 파일 생성:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
        
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          hhaminlee/pdf-chatbot:latest
          hhaminlee/pdf-chatbot:${{ github.sha }}
```

**GitHub Secrets 설정:**
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. 다음 시크릿 추가:
   - `DOCKERHUB_USERNAME`: Docker Hub 사용자명
   - `DOCKERHUB_TOKEN`: Docker Hub 액세스 토큰

### 6. 사용자를 위한 간단한 실행 명령

이미지가 Docker Hub에 올라간 후 사용자들은 다음과 같이 실행할 수 있습니다:

```bash
# 한 번에 실행 (권장)
docker run -p 8501:8501 -p 11434:11434 hhaminlee/pdf-chatbot:latest

# 백그라운드 실행
docker run -d -p 8501:8501 -p 11434:11434 --name pdf-chatbot hhaminlee/pdf-chatbot:latest

# 볼륨 마운트 (모델 데이터 유지)
docker run -p 8501:8501 -p 11434:11434 -v ollama_data:/root/.ollama hhaminlee/pdf-chatbot:latest
```

### 7. Docker Compose 업데이트

Docker Hub 이미지 사용 시 `docker-compose.yml` 업데이트:

```yaml
version: '3.8'

services:
  pdf-chatbot:
    image: hhaminlee/pdf-chatbot:latest  # 로컬 빌드 대신 이미지 사용
    container_name: pdf-ai-chatbot
    ports:
      - "8501:8501"
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped

volumes:
  ollama_data:
    driver: local
```

## 장점

### Docker Hub 사용 시:
- ✅ **빠른 배포**: 사용자가 빌드 시간 없이 바로 실행
- ✅ **일관성**: 모든 사용자가 동일한 이미지 사용
- ✅ **자동화**: CI/CD 파이프라인으로 자동 빌드/배포
- ✅ **버전 관리**: 태그를 통한 버전 관리

### 현재 방식 vs Docker Hub 비교:

| 구분 | 현재 (로컬 빌드) | Docker Hub |
|------|------------------|------------|
| 첫 실행 시간 | 20-30분 (빌드+다운로드) | 10-15분 (다운로드만) |
| 디스크 사용량 | 빌드 임시파일 포함 | 최소한 |
| 네트워크 사용량 | 소스코드 + 종속성 | 이미지만 |
| 사용 편의성 | docker-compose up --build | docker run |

## 권장사항

1. **개발자용**: 현재 방식 (소스코드 수정 필요)
2. **일반 사용자용**: Docker Hub 방식 (간편 실행)

두 방식 모두 README에 포함하여 사용자가 선택할 수 있도록 하는 것이 좋습니다.