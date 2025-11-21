import streamlit as st
import tempfile
import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="PDF AI Chatbot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 PDF AI Chatbot")
st.markdown("PDF 문서를 업로드하고 내용에 대해 질문해보세요!")

# 사이드바에 설정 옵션들
with st.sidebar:
    # 사용법 먼저 표시
    with st.expander("ℹ️ 사용법"):
        st.markdown("""
        1. 사이드바에서 **모델**과 **분석 모드**를 선택하세요
        2. **PDF 파일**을 업로드하세요
        3. 파일 처리가 완료되면 오른쪽 채팅창에서 **질문**하세요
        4. AI가 PDF 내용을 기반으로 답변해드립니다
        
        **🔧 분석 모드 가이드:**
        - ⚡ **빠른 분석**: 속도 우선, 일반적인 질문에 적합
        - 🔍 **정밀한 분석**: 정확도 우선, 세부적인 내용 분석 시 사용
        - 🎯 **균형잡힌 분석**: 속도와 정확도의 균형 (권장)
        
        **지원 파일:** PDF | **기술 스택:** Ollama, LangChain, FAISS
        """)
    
    st.header("⚙️ 설정")
    
    # Ollama 모델 선택
    model_name = st.selectbox(
        "사용할 모델을 선택하세요:",
        ["qwen3:8b", "llama3.2", "mistral"]
    )
    
    # 분석 정밀도 설정
    analysis_mode = st.selectbox(
        "분석 모드를 선택하세요:",
        ["⚡ 빠른 분석 (권장)", "🔍 정밀한 분석", "🎯 균형잡힌 분석"]
    )
    
    # 분석 모드에 따른 파라미터 매핑
    if analysis_mode == "⚡ 빠른 분석 (권장)":
        chunk_size, chunk_overlap = 1500, 75  # 큰 청크, 적은 오버랩
    elif analysis_mode == "🔍 정밀한 분석":
        chunk_size, chunk_overlap = 800, 150   # 작은 청크, 많은 오버랩
    else:  # 균형잡힌 분석
        chunk_size, chunk_overlap = 1000, 100  # 기본값
    
    st.markdown("---")
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "PDF 파일을 업로드하세요",
        type="pdf",
        accept_multiple_files=False
    )

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

def extract_text_from_pdf(pdf_file):
    """PDF에서 텍스트 추출"""
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file.flush()
            
            reader = PdfReader(tmp_file.name)
            for page in reader.pages:
                text += page.extract_text()
        
        # 임시 파일 삭제
        os.unlink(tmp_file.name)
        
    except Exception as e:
        st.error(f"PDF 처리 중 오류가 발생했습니다: {str(e)}")
        return ""
    
    return text

def create_vectorstore(text, model_name, chunk_size, chunk_overlap):
    """텍스트를 청크로 나누고 벡터 스토어 생성"""
    if not text.strip():
        st.error("추출된 텍스트가 없습니다.")
        return None
    
    try:
        # Document 객체 생성
        document = Document(page_content=text, metadata={"source": "uploaded_pdf"})
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents([document])
        
        if not chunks:
            st.error("텍스트 청크 생성에 실패했습니다.")
            return None
        
        # Ollama 임베딩 생성 (재시도 로직 포함)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = OllamaEmbeddings(
                    model="embeddinggemma",
                    base_url="http://localhost:11434"
                )
                
                # FAISS 벡터 스토어 생성
                vectorstore = FAISS.from_documents(chunks, embeddings)
                return vectorstore
                
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    raise retry_error
                st.warning(f"임베딩 생성 재시도 중... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(2)
        
        return None
        
    except Exception as e:
        st.error(f"벡터 스토어 생성 중 오류: {str(e)}")
        st.error("Ollama 서버가 실행 중인지 확인해주세요.")
        return None

def format_docs(docs):
    """문서들을 하나의 문자열로 포맷팅"""
    return "\n\n".join(doc.page_content for doc in docs)

def get_conversation_chain(vectorstore, model_name):
    """대화 체인 생성"""
    try:
        llm = ChatOllama(
            model=model_name, 
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        
        # 프롬프트 템플릿 생성
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            다음 문서를 기반으로 질문에 답변해주세요:

            문서:
            {context}

            질문: {question}
            
            답변은 반드시 한국어로 해주시고, 문서에 있는 정보만을 사용해서 답변해주세요.
            만약 문서에 관련 정보가 없다면 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변해주세요.
            
            답변:
            """
        )
        
        # LCEL 체인 생성 (StuffDocumentsChain 대체)
        rag_chain = (
            {"context": vectorstore.as_retriever() | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return rag_chain
        
    except Exception as e:
        st.error(f"대화 체인 생성 중 오류: {str(e)}")
        return None

# 📄 문서 처리 영역 (상단)
st.header("📄 문서 처리")

if uploaded_file is not None:
    # 파일이 변경되었거나 처음 업로드된 경우에만 처리
    if st.session_state.processed_file != uploaded_file.name:
        with st.spinner("PDF 처리 중..."):
            # PDF 텍스트 추출
            text = extract_text_from_pdf(uploaded_file)
            
            if text:
                st.success("PDF 텍스트 추출 완료!")
                st.info(f"추출된 텍스트 길이: {len(text)} 문자")
                
                # 텍스트 미리보기
                with st.expander("추출된 텍스트 미리보기"):
                    st.text(text[:500] + "..." if len(text) > 500 else text)
                
                # 벡터 스토어 생성
                with st.spinner("벡터 임베딩 생성 중..."):
                    vectorstore = create_vectorstore(text, model_name, chunk_size, chunk_overlap)
                    
                    if vectorstore:
                        st.session_state.vectorstore = vectorstore
                        st.session_state.processed_file = uploaded_file.name
                        st.success("벡터 스토어 생성 완료! 이제 아래 채팅창에서 질문할 수 있습니다.")
                    else:
                        st.error("벡터 스토어 생성에 실패했습니다.")
            else:
                st.error("PDF에서 텍스트를 추출할 수 없습니다.")
    else:
        # 이미 처리된 파일인 경우
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"📁 **{uploaded_file.name}** 파일이 준비되었습니다!")
        with col2:
            if st.button("🔄 다른 파일 업로드"):
                st.session_state.vectorstore = None
                st.session_state.processed_file = None
                st.session_state.messages = []
                st.rerun()
else:
    st.info("👆 사이드바에서 PDF 파일을 업로드해주세요.")

st.divider()  # 구분선 추가

# 💬 AI 채팅 영역 (하단)
st.header("💬 AI 챗봇")

# 채팅 컨테이너 생성
chat_container = st.container()

# 사용자 입력
if prompt := st.chat_input("PDF 내용에 대해 질문해보세요..."):
    if st.session_state.vectorstore is None:
        st.error("먼저 PDF 파일을 업로드해주세요.")
    else:
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI 응답 생성
        with st.spinner("답변 생성 중..."):
            try:
                conversation = get_conversation_chain(st.session_state.vectorstore, model_name)
                
                if conversation:
                    answer = conversation.invoke(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = "대화 체인 생성에 실패했습니다."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except Exception as e:
                error_msg = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # 페이지 새로고침
        st.rerun()
    
# 채팅 기록을 역순으로 표시 (최신 메시지가 위로)
with chat_container:
    for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

