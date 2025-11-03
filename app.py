import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
from pathlib import Path
import os

# ==================== 상수 정의 ====================
# 탐구 과목 CSV 파일 구조 관련 상수
STUDENT_ID_COL_IDX = 0          # 수험번호 컬럼 인덱스
SUBJECT_CODE1_COL_IDX = 1       # 과목코드1 컬럼 인덱스 (탐구용)
SUBJECT_CODE2_COL_IDX = 2       # 과목코드2 컬럼 인덱스 (탐구용)
ANSWERS_START_COL_IDX = 3       # 답안 시작 컬럼 인덱스
QUESTIONS_PER_SUBJECT = 20      # 탐구 과목당 문항 수

# 한글 폰트 경로 (macOS)
KOREAN_FONT_PATHS = [
    '/System/Library/Fonts/AppleSDGothicNeo.ttc',
    '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
]

# ==================== 과목 코드 매핑 설정 ====================
SUBJECT_CODE_MAPPINGS = {
    "국어": {
        "1": "화법과 작문",
        "2": "언어와 매체"
    },
    "수학": {
        "1": "확률과 통계",
        "2": "미분과 적분",
        "3": "기하"
    },
    "영어": {
        "1": "영어"
    },
    "한국사": {
        "1": "한국사"
    },
    "탐구": {
        # 사회탐구
        "11": "생활과 윤리",
        "12": "윤리와 사상",
        "13": "한국지리",
        "14": "세계지리",
        "15": "동아시아사",
        "16": "세계사",
        "17": "경제",
        "18": "정치와 법",
        "19": "사회·문화",
        # 과학탐구
        "20": "물리학Ⅰ",
        "21": "화학Ⅰ",
        "22": "생명과학Ⅰ",
        "23": "지구과학Ⅰ",
        "24": "물리학Ⅱ",
        "25": "화학Ⅱ",
        "26": "생명과학Ⅱ",
        "27": "지구과학Ⅱ"
    }
}

# 과목별 안내 메시지
SUBJECT_INFO_MESSAGES = {
    "국어": """
    **국어 과목코드 매핑:**
    - 과목코드 1 → 화법과 작문
    - 과목코드 2 → 언어와 매체
    """,
    "수학": """
    **수학 과목코드 매핑:**
    - 과목코드 1 → 확률과 통계
    - 과목코드 2 → 미분과 적분
    - 과목코드 3 → 기하
    """,
    "영어": """
    **영어 과목코드 매핑:**
    - 과목코드 1 → 영어
    """,
    "한국사": """
    **한국사 과목코드 매핑:**
    - 과목코드 1 → 한국사
    """,
    "탐구": """
    **탐구 과목코드 매핑:**

    📘 **사회탐구:**
    - 11: 생활과 윤리
    - 12: 윤리와 사상
    - 13: 한국지리
    - 14: 세계지리
    - 15: 동아시아사
    - 16: 세계사
    - 17: 경제
    - 18: 정치와 법
    - 19: 사회·문화

    🔬 **과학탐구:**
    - 20: 물리학Ⅰ
    - 21: 화학Ⅰ
    - 22: 생명과학Ⅰ
    - 23: 지구과학Ⅰ
    - 24: 물리학Ⅱ
    - 25: 화학Ⅱ
    - 26: 생명과학Ⅱ
    - 27: 지구과학Ⅱ
    """
}

# reportlab 선택적 import (PDF 기능용)
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="자동 채점 시스템",
    page_icon="📝",
    layout="wide"
)

# 사이드바 크기 확대 (CSS)
st.markdown("""
    <style>
    /* 사이드바 너비 확대 */
    [data-testid="stSidebar"] {
        min-width: 450px;
        max-width: 450px;
    }
    
    /* 사이드바 내용 영역 */
    [data-testid="stSidebar"] > div:first-child {
        width: 450px;
    }
    
    /* 메인 컨텐츠 여백 조정 */
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀
st.title("📝 자동 채점 시스템")
st.markdown("---")

# 사이드바 - 파일 업로드
with st.sidebar:
    # SN 로고 및 브랜딩 (컴팩트하게)
    import base64

    # 상대 경로로 로고 파일 로드
    logo_path = Path(__file__).parent / "public" / "sn-logo.png"

    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-bottom: 10px; margin-top: -10px;'>
                <img src='data:image/png;base64,{logo_data}' width='35' style='margin-right: 8px;'/>
                <span style='color: #666; font-size: 10px; white-space: nowrap;'>Powered by <strong>SN독학기숙학원</strong></span>
            </div>
        """, unsafe_allow_html=True)
    else:
        # 로고 파일이 없는 경우 텍스트만 표시
        st.markdown("""
            <div style='margin-bottom: 10px; margin-top: -10px;'>
                <span style='color: #666; font-size: 10px; white-space: nowrap;'>Powered by <strong>SN독학기숙학원</strong></span>
            </div>
        """, unsafe_allow_html=True)
    
    st.header("📁 파일 업로드")
    
    # 과목 선택 (최상단)
    st.caption("📚 과목을 선택하세요")
    subject_type = st.selectbox(
        "과목 종류",
        ["국어", "수학", "영어", "한국사", "탐구"],
        key="subject_type",
        help="업로드할 정답 파일의 과목을 선택하세요"
    )
    
    st.markdown("---")
    
    st.subheader("1. 학생 답안 파일")
    
    # 선택된 과목 확인
    current_subject = st.session_state.get('subject_type', '국어')
    
    if current_subject == '탐구':
        # 탐구용 샘플 파일
        st.caption("형식: 수험번호 | 과목코드1 | 과목코드2 | 1번~20번 | 21번~40번")
        st.info("⚠️ 탐구는 한 행에 2개 과목의 답안(총 40문항)이 들어갑니다.")
        
        sample_tamgu_data = {
            '수험번호': ['202400112345678', '202400223456789', '202400334567890'],
            '과목코드1': [11, 13, 17],
            '과목코드2': [20, 21, 22]
        }
        # 1~20번 문항 추가 (첫 번째 과목)
        for i in range(1, QUESTIONS_PER_SUBJECT + 1):
            sample_tamgu_data[f'{i}번'] = [1, 2, 3]
        # 21~40번 문항 추가 (두 번째 과목)
        for i in range(QUESTIONS_PER_SUBJECT + 1, QUESTIONS_PER_SUBJECT * 2 + 1):
            sample_tamgu_data[f'{i}번'] = [2, 3, 4]
        
        sample_tamgu_df = pd.DataFrame(sample_tamgu_data)
        sample_tamgu_csv = sample_tamgu_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="💾 탐구 샘플 다운로드",
            data=sample_tamgu_csv,
            file_name="학생답안_탐구_샘플.csv",
            mime="text/csv",
            help="탐구용 샘플 파일 (2개 과목, 40문항)"
        )
    else:
        # 일반 과목 샘플 파일 (국어, 수학, 영어, 한국사)
        st.caption("형식: 수험번호 | 과목코드 | 1번 | 2번 | 3번 ...")
        
        sample_student_data = {
            '수험번호': ['202400112345678', '202400223456789', '202400334567890', '202400445678901', '202400556789012', '202400667890123'],
            '과목코드': ['MATH01', 'MATH01', 'MATH01', 'ENG01', 'ENG01', 'ENG01'],
            '1번': [1, 1, 1, 2, 2, 2],
            '2번': [3, 2, 3, 3, 3, 4],
            '3번': [2, 2, 2, 1, 1, 1],
            '4번': [4, 4, 4, 4, 4, 4],
            '5번': [1, 1, 2, 2, 2, 2],
            '6번': [2, 2, 2, 1, 1, 1],
            '7번': [3, 4, 3, 3, 3, 3],
            '8번': [4, 4, 3, 2, 2, 2],
            '9번': [1, 1, 1, 4, 4, 4],
            '10번': [2, 2, 2, 1, 1, 2]
        }
        sample_student_df = pd.DataFrame(sample_student_data)
        sample_student_csv = sample_student_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="💾 샘플 다운로드",
            data=sample_student_csv,
            file_name="학생답안_샘플.csv",
            mime="text/csv",
            help="샘플 파일을 다운로드하여 형식을 확인하세요"
        )
    
    student_file = st.file_uploader(
        "학생 답안 CSV 파일을 업로드하세요",
        type=['csv'],
        key='student'
    )
    
    st.subheader("2. 정답 및 배점 파일")
    
    # 과목별 과목코드 매핑 안내 (설정에서 가져오기)
    info_message = SUBJECT_INFO_MESSAGES.get(subject_type, "")
    if info_message:
        st.info(info_message)

    subject_code_mapping = SUBJECT_CODE_MAPPINGS.get(subject_type, {})
    st.session_state['subject_code_mapping'] = subject_code_mapping
    
    # 샘플 정답 파일 생성
    sample_answer_data = {
        '과목번호': ['MATH01', 'MATH01', 'MATH01', 'MATH01', 'MATH01', 
                    'MATH01', 'MATH01', 'MATH01', 'MATH01', 'MATH01',
                    'ENG01', 'ENG01', 'ENG01', 'ENG01', 'ENG01',
                    'ENG01', 'ENG01', 'ENG01', 'ENG01', 'ENG01'],
        '문항': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        '정답': [1, 3, 2, 4, 1, 2, 3, 4, 1, 2, 2, 3, 1, 4, 2, 1, 3, 2, 4, 1],
        '배점': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    }
    sample_answer_df = pd.DataFrame(sample_answer_data)
    sample_answer_csv = sample_answer_df.to_csv(index=False, encoding='utf-8-sig')
    
    st.caption("형식: 과목번호 | 문항 | 정답 | 배점")
    st.download_button(
        label="💾 샘플 다운로드",
        data=sample_answer_csv,
        file_name="정답배점_샘플.csv",
        mime="text/csv",
        help="샘플 파일을 다운로드하여 형식을 확인하세요"
    )
    
    answer_file = st.file_uploader(
        "정답/배점 CSV 파일을 업로드하세요",
        type=['csv'],
        key='answer'
    )
    
    st.subheader("3. 학생 정보 파일 (선택)")
    
    # 샘플 학생 정보 파일 생성
    sample_info_data = {
        '학번': ['2024001', '2024002', '2024003', '2024004', '2024005', '2024006'],
        '전화번호': ['12345678', '23456789', '34567890', '45678901', '56789012', '67890123'],
        '이름': ['김철수', '이영희', '박민수', '최지훈', '정수연', '강하늘']
    }
    # 참고: 수험번호는 학번+전화번호로 생성됩니다
    # 예) 2024001 + 12345678 = 202400112345678
    sample_info_df = pd.DataFrame(sample_info_data)
    sample_info_csv = sample_info_df.to_csv(index=False, encoding='utf-8-sig')
    
    st.caption("형식: 학번 | 전화번호 | 이름")
    st.caption("⚠️ 학번, 전화번호 2개중 한개는 필수 기입")
    st.download_button(
        label="💾 샘플 다운로드",
        data=sample_info_csv,
        file_name="학생정보_샘플.csv",
        mime="text/csv",
        help="학생 이름을 표시하려면 학생 정보 파일을 업로드하세요"
    )
    
    student_info_file = st.file_uploader(
        "학생 정보 CSV 파일을 업로드하세요 (선택사항)",
        type=['csv'],
        key='student_info',
        help="학번 또는 전화번호로 유연하게 매칭됩니다. 완전 매칭 → 학번 매칭 → 전화번호 매칭 순서로 시도합니다."
    )
    
    st.markdown("---")
    st.info("💡 학생 답안과 정답 파일을 업로드하면 자동으로 채점이 시작됩니다.\n\n학생 정보 파일을 추가하면 결과에 이름이 표시됩니다.")
    
    st.markdown("---")
    st.subheader("⚙️ 설정")
    debug_mode = st.checkbox("🔧 디버깅 모드", value=False, help="파일 구조 및 채점 과정을 상세히 표시합니다")


def setup_korean_font_for_pdf():
    """PDF 생성을 위한 한글 폰트 설정

    Returns:
        str: 사용 가능한 폰트 이름 ('Korean' 또는 'Helvetica')
    """
    try:
        # macOS 한글 폰트 (AppleSDGothicNeo)
        pdfmetrics.registerFont(TTFont('Korean', KOREAN_FONT_PATHS[0], subfontIndex=0))
        return 'Korean'
    except:
        try:
            # 대체 폰트 (AppleGothic)
            pdfmetrics.registerFont(TTFont('Korean', KOREAN_FONT_PATHS[1]))
            return 'Korean'
        except:
            # 폰트 로드 실패 시 기본 폰트 사용
            return 'Helvetica'


def setup_korean_font_for_matplotlib():
    """matplotlib 그래프를 위한 한글 폰트 설정

    matplotlib의 rcParams를 설정하여 한글이 제대로 표시되도록 합니다.
    """
    try:
        plt.rcParams['font.family'] = 'AppleGothic'
    except:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def load_student_data(file, is_tamgu=False):
    """학생 답안 파일 로드

    Args:
        file: CSV 파일 객체
        is_tamgu: 탐구 과목 여부 (기본값: False)

    Returns:
        pandas.DataFrame: 학생 답안 데이터

    Raises:
        UnicodeDecodeError: 인코딩 오류 시
        pd.errors.EmptyDataError: 빈 파일일 경우
        Exception: 기타 파일 읽기 오류
    """
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8로 읽기 실패 시 CP949(한글 Windows 인코딩) 시도
        try:
            df = pd.read_csv(file, encoding='cp949')
        except Exception as e:
            raise Exception(
                f"❌ 파일 인코딩 오류\n\n"
                f"원인: UTF-8과 CP949(한글 Windows) 인코딩 모두 실패했습니다.\n\n"
                f"해결방법:\n"
                f"1. CSV 파일을 Excel에서 다시 저장할 때 'UTF-8' 인코딩 선택\n"
                f"2. 메모장에서 '다른 이름으로 저장' → 인코딩을 'UTF-8'로 선택\n\n"
                f"상세 오류: {str(e)}"
            )
    except pd.errors.EmptyDataError:
        raise Exception(
            f"❌ 빈 파일 오류\n\n"
            f"학생 답안 파일이 비어있습니다.\n\n"
            f"해결방법:\n"
            f"1. 파일에 데이터가 있는지 확인하세요\n"
            f"2. 샘플 파일을 다운로드하여 형식을 확인하세요"
        )
    except Exception as e:
        raise Exception(
            f"❌ 파일 읽기 오류\n\n"
            f"학생 답안 파일을 읽는 중 오류가 발생했습니다.\n\n"
            f"해결방법:\n"
            f"1. CSV 파일 형식이 올바른지 확인하세요\n"
            f"2. 파일이 손상되지 않았는지 확인하세요\n"
            f"3. 다른 CSV 뷰어로 파일을 열어보세요\n\n"
            f"상세 오류: {str(e)}"
        )

    # 기본 컬럼 수 검증
    if is_tamgu:
        # 탐구: 최소 3개 컬럼 (수험번호, 과목코드1, 과목코드2) + 40개 문항
        min_required_cols = ANSWERS_START_COL_IDX + (QUESTIONS_PER_SUBJECT * 2)
        if len(df.columns) < min_required_cols:
            raise Exception(
                f"❌ 탐구 과목 파일 형식 오류\n\n"
                f"현재 컬럼 수: {len(df.columns)}개\n"
                f"필요한 최소 컬럼 수: {min_required_cols}개\n"
                f"(수험번호 + 과목코드1 + 과목코드2 + 40개 문항)\n\n"
                f"해결방법:\n"
                f"1. 탐구 샘플 파일을 다운로드하여 형식을 확인하세요\n"
                f"2. 모든 40개 문항 답안이 입력되었는지 확인하세요\n"
                f"3. 과목코드1, 과목코드2가 올바르게 입력되었는지 확인하세요"
            )
    else:
        # 일반 과목: 최소 3개 컬럼 (수험번호, 과목코드, 답안 최소 1개)
        min_required_cols = 3
        if len(df.columns) < min_required_cols:
            raise Exception(
                f"❌ 학생 답안 파일 형식 오류\n\n"
                f"현재 컬럼 수: {len(df.columns)}개\n"
                f"필요한 최소 컬럼 수: {min_required_cols}개\n"
                f"(수험번호 + 과목코드 + 답안 1개 이상)\n\n"
                f"해결방법:\n"
                f"1. 샘플 파일을 다운로드하여 형식을 확인하세요\n"
                f"2. 첫 번째 열: 수험번호, 두 번째 열: 과목코드, 세 번째 열부터: 답안\n"
                f"3. 헤더 행이 포함되어 있는지 확인하세요"
            )

    # 데이터 행 존재 확인
    if len(df) == 0:
        raise Exception(
            f"❌ 데이터 없음 오류\n\n"
            f"파일에 데이터 행이 없습니다. (헤더만 있음)\n\n"
            f"해결방법:\n"
            f"1. 학생 답안 데이터가 입력되었는지 확인하세요\n"
            f"2. 최소 1명 이상의 학생 데이터가 필요합니다"
        )

    # 탐구 과목인 경우 특수 처리
    if is_tamgu:
        # 탐구는 한 행에 2개 과목이 있음
        # 형식: 수험번호 | 과목코드1 | 과목코드2 | 1~20번(과목1) | 21~40번(과목2)
        new_rows = []

        # 컬럼 인덱스 범위 검증
        required_indices = [STUDENT_ID_COL_IDX, SUBJECT_CODE1_COL_IDX, SUBJECT_CODE2_COL_IDX]
        for idx in required_indices:
            if idx >= len(df.columns):
                raise Exception(
                    f"❌ 탐구 파일 구조 오류\n\n"
                    f"필요한 컬럼 인덱스 {idx}가 존재하지 않습니다.\n"
                    f"현재 컬럼 수: {len(df.columns)}개\n\n"
                    f"해결방법:\n"
                    f"1. 탐구 샘플 파일 형식을 확인하세요\n"
                    f"2. 수험번호, 과목코드1, 과목코드2가 모두 있어야 합니다"
                )

        for idx, row in df.iterrows():
            student_id = row[df.columns[STUDENT_ID_COL_IDX]]      # 수험번호
            subject_code1 = row[df.columns[SUBJECT_CODE1_COL_IDX]]  # 과목코드1
            subject_code2 = row[df.columns[SUBJECT_CODE2_COL_IDX]]  # 과목코드2

            # 첫 번째 과목 (1~20번 문항)
            row1_data = {'수험번호': student_id, '과목코드': subject_code1}
            missing_count_1 = 0
            for i in range(QUESTIONS_PER_SUBJECT):
                col_idx = ANSWERS_START_COL_IDX + i
                if col_idx < len(df.columns):
                    row1_data[f'{i+1}번'] = row[df.columns[col_idx]]
                else:
                    missing_count_1 += 1

            if missing_count_1 > 0:
                raise Exception(
                    f"❌ 탐구 과목1 답안 누락\n\n"
                    f"학생 {student_id}의 첫 번째 탐구 과목 답안이 {missing_count_1}개 누락되었습니다.\n"
                    f"필요: 20개 문항, 현재: {QUESTIONS_PER_SUBJECT - missing_count_1}개\n\n"
                    f"해결방법:\n"
                    f"1. 모든 학생의 1~20번 답안을 확인하세요\n"
                    f"2. 빈칸이 있다면 0 또는 공백으로 채우세요"
                )
            new_rows.append(row1_data)

            # 두 번째 과목 (21~40번 문항을 1~20번으로 변환)
            row2_data = {'수험번호': student_id, '과목코드': subject_code2}
            missing_count_2 = 0
            for i in range(QUESTIONS_PER_SUBJECT):
                col_idx = ANSWERS_START_COL_IDX + QUESTIONS_PER_SUBJECT + i
                if col_idx < len(df.columns):
                    row2_data[f'{i+1}번'] = row[df.columns[col_idx]]
                else:
                    missing_count_2 += 1

            if missing_count_2 > 0:
                raise Exception(
                    f"❌ 탐구 과목2 답안 누락\n\n"
                    f"학생 {student_id}의 두 번째 탐구 과목 답안이 {missing_count_2}개 누락되었습니다.\n"
                    f"필요: 20개 문항, 현재: {QUESTIONS_PER_SUBJECT - missing_count_2}개\n\n"
                    f"해결방법:\n"
                    f"1. 모든 학생의 21~40번 답안을 확인하세요\n"
                    f"2. 빈칸이 있다면 0 또는 공백으로 채우세요"
                )
            new_rows.append(row2_data)

        # 새로운 DataFrame 생성
        df = pd.DataFrame(new_rows)

    return df


def load_answer_data(file):
    """정답/배점 파일 로드

    Args:
        file: CSV 파일 객체

    Returns:
        pandas.DataFrame: 정답 및 배점 데이터

    Raises:
        UnicodeDecodeError: 인코딩 오류 시
        pd.errors.EmptyDataError: 빈 파일일 경우
        Exception: 기타 파일 읽기 오류
    """
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8로 읽기 실패 시 CP949(한글 Windows 인코딩) 시도
        try:
            df = pd.read_csv(file, encoding='cp949')
        except Exception as e:
            raise Exception(
                f"❌ 파일 인코딩 오류\n\n"
                f"원인: UTF-8과 CP949(한글 Windows) 인코딩 모두 실패했습니다.\n\n"
                f"해결방법:\n"
                f"1. CSV 파일을 Excel에서 다시 저장할 때 'UTF-8' 인코딩 선택\n"
                f"2. 메모장에서 '다른 이름으로 저장' → 인코딩을 'UTF-8'로 선택\n\n"
                f"상세 오류: {str(e)}"
            )
    except pd.errors.EmptyDataError:
        raise Exception(
            f"❌ 빈 파일 오류\n\n"
            f"정답/배점 파일이 비어있습니다.\n\n"
            f"해결방법:\n"
            f"1. 파일에 데이터가 있는지 확인하세요\n"
            f"2. 샘플 파일을 다운로드하여 형식을 확인하세요"
        )
    except Exception as e:
        raise Exception(
            f"❌ 파일 읽기 오류\n\n"
            f"정답/배점 파일을 읽는 중 오류가 발생했습니다.\n\n"
            f"해결방법:\n"
            f"1. CSV 파일 형식이 올바른지 확인하세요\n"
            f"2. 파일이 손상되지 않았는지 확인하세요\n"
            f"3. 다른 CSV 뷰어로 파일을 열어보세요\n\n"
            f"상세 오류: {str(e)}"
        )

    # 컬럼 수 검증 (최소 4개: 과목번호, 문항, 정답, 배점)
    if len(df.columns) < 4:
        raise Exception(
            f"❌ 정답/배점 파일 형식 오류\n\n"
            f"현재 컬럼 수: {len(df.columns)}개\n"
            f"필요한 컬럼 수: 4개 (과목번호, 문항, 정답, 배점)\n\n"
            f"해결방법:\n"
            f"1. 샘플 파일을 다운로드하여 형식을 확인하세요\n"
            f"2. 필수 컬럼: 과목번호 | 문항 | 정답 | 배점\n"
            f"3. 현재 컬럼: {', '.join(df.columns.tolist())}"
        )

    # 데이터 행 존재 확인
    if len(df) == 0:
        raise Exception(
            f"❌ 데이터 없음 오류\n\n"
            f"정답/배점 파일에 데이터 행이 없습니다. (헤더만 있음)\n\n"
            f"해결방법:\n"
            f"1. 정답 및 배점 데이터가 입력되었는지 확인하세요\n"
            f"2. 최소 1개 이상의 문항 정답이 필요합니다"
        )

    # 배점 컬럼 유효성 검사 (숫자로 변환 가능한지)
    points_col = df.columns[3]  # 네 번째 컬럼이 배점
    invalid_rows = []
    for idx, value in enumerate(df[points_col]):
        try:
            float(value)
        except (ValueError, TypeError):
            invalid_rows.append(idx + 2)  # +2는 헤더 포함 및 1-based 인덱싱

    if invalid_rows:
        raise Exception(
            f"❌ 배점 데이터 형식 오류\n\n"
            f"배점 컬럼에 숫자가 아닌 값이 있습니다.\n"
            f"문제가 있는 행: {', '.join(map(str, invalid_rows[:5]))}"
            f"{'...' if len(invalid_rows) > 5 else ''}\n\n"
            f"해결방법:\n"
            f"1. 배점 컬럼(4번째 컬럼)에 숫자만 입력하세요\n"
            f"2. 빈칸, 문자, 특수문자가 있는지 확인하세요\n"
            f"3. 소수점은 점(.)으로 표시하세요 (예: 2.5)"
        )

    return df


def load_student_info(file):
    """학생 정보 파일 로드

    Args:
        file: CSV 파일 객체

    Returns:
        dict: 3가지 방식으로 매칭 가능한 학생 정보 딕셔너리
            - by_full: 학번+전화번호로 매칭
            - by_student_id: 학번으로 매칭
            - by_phone: 전화번호로 매칭

    Raises:
        UnicodeDecodeError: 인코딩 오류 시
        pd.errors.EmptyDataError: 빈 파일일 경우
        Exception: 기타 파일 읽기 오류
    """
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8로 읽기 실패 시 CP949(한글 Windows 인코딩) 시도
        try:
            df = pd.read_csv(file, encoding='cp949')
        except Exception as e:
            raise Exception(
                f"❌ 파일 인코딩 오류\n\n"
                f"원인: UTF-8과 CP949(한글 Windows) 인코딩 모두 실패했습니다.\n\n"
                f"해결방법:\n"
                f"1. CSV 파일을 Excel에서 다시 저장할 때 'UTF-8' 인코딩 선택\n"
                f"2. 메모장에서 '다른 이름으로 저장' → 인코딩을 'UTF-8'로 선택\n\n"
                f"상세 오류: {str(e)}"
            )
    except pd.errors.EmptyDataError:
        raise Exception(
            f"❌ 빈 파일 오류\n\n"
            f"학생 정보 파일이 비어있습니다.\n\n"
            f"해결방법:\n"
            f"1. 파일에 데이터가 있는지 확인하세요\n"
            f"2. 샘플 파일을 다운로드하여 형식을 확인하세요"
        )
    except Exception as e:
        raise Exception(
            f"❌ 파일 읽기 오류\n\n"
            f"학생 정보 파일을 읽는 중 오류가 발생했습니다.\n\n"
            f"해결방법:\n"
            f"1. CSV 파일 형식이 올바른지 확인하세요\n"
            f"2. 파일이 손상되지 않았는지 확인하세요\n"
            f"3. 다른 CSV 뷰어로 파일을 열어보세요\n\n"
            f"상세 오류: {str(e)}"
        )

    # 컬럼 수 검증 (최소 3개: 학번, 전화번호, 이름)
    if len(df.columns) < 3:
        raise Exception(
            f"❌ 학생 정보 파일 형식 오류\n\n"
            f"현재 컬럼 수: {len(df.columns)}개\n"
            f"필요한 컬럼 수: 3개 (학번, 전화번호, 이름)\n\n"
            f"해결방법:\n"
            f"1. 샘플 파일을 다운로드하여 형식을 확인하세요\n"
            f"2. 필수 컬럼: 학번 | 전화번호 | 이름\n"
            f"3. 현재 컬럼: {', '.join(df.columns.tolist())}"
        )

    # 데이터 행 존재 확인
    if len(df) == 0:
        raise Exception(
            f"❌ 데이터 없음 오류\n\n"
            f"학생 정보 파일에 데이터 행이 없습니다. (헤더만 있음)\n\n"
            f"해결방법:\n"
            f"1. 학생 정보 데이터가 입력되었는지 확인하세요\n"
            f"2. 최소 1명 이상의 학생 정보가 필요합니다"
        )

    # 학번, 전화번호, 이름 저장 (3가지 방식으로 매칭 가능하도록)
    student_info_dict = {
        'by_full': {},      # 학번+전화번호 (완전 매칭)
        'by_student_id': {},  # 학번으로 매칭
        'by_phone': {}      # 전화번호로 매칭
    }

    # 컬럼 인덱스 범위 검증 및 데이터 처리
    skipped_rows = []
    valid_count = 0

    for idx, row in df.iterrows():
        try:
            # 학번과 이름이 모두 비어있으면 빈 행으로 간주하고 건너뛰기
            is_student_num_empty = pd.isna(row[df.columns[0]]) or str(row[df.columns[0]]).strip() == ''
            is_name_empty = pd.isna(row[df.columns[2]]) or str(row[df.columns[2]]).strip() == ''

            # 둘 다 비어있으면 건너뛰기 (완전히 빈 행)
            if is_student_num_empty and is_name_empty:
                skipped_rows.append(idx + 2)
                continue

            # 학번이나 이름 중 하나만 비어있으면 경고하고 건너뛰기
            if is_student_num_empty:
                skipped_rows.append(idx + 2)
                continue

            if is_name_empty:
                skipped_rows.append(idx + 2)
                continue

            student_num = str(row[df.columns[0]])  # 학번
            phone = str(row[df.columns[1]]) if not pd.isna(row[df.columns[1]]) else ''  # 전화번호 (선택)
            name = str(row[df.columns[2]])  # 이름

            full_id = student_num + phone  # 학번 + 전화번호

            info = {
                '학번': student_num,
                '전화번호': phone,
                '이름': name
            }

            # 3가지 방식으로 저장
            student_info_dict['by_full'][full_id] = info
            student_info_dict['by_student_id'][student_num] = info
            if phone:  # 전화번호가 있을 때만 저장
                student_info_dict['by_phone'][phone] = info

            valid_count += 1

        except IndexError:
            # 컬럼이 부족한 행은 건너뛰기
            skipped_rows.append(idx + 2)
            continue

    # 건너뛴 행이 있으면 경고 표시 (Streamlit import 필요)
    if skipped_rows and len(skipped_rows) > 0:
        import streamlit as st
        if len(skipped_rows) <= 5:
            st.warning(
                f"⚠️ 학생 정보 파일 일부 행 건너뛰기\n\n"
                f"건너뛴 행: {', '.join(map(str, skipped_rows))}\n"
                f"(학번 또는 이름이 비어있거나 컬럼이 부족함)\n\n"
                f"유효한 학생 정보: {valid_count}명"
            )
        else:
            st.warning(
                f"⚠️ 학생 정보 파일 일부 행 건너뛰기\n\n"
                f"건너뛴 행 수: {len(skipped_rows)}개\n"
                f"첫 5개 행: {', '.join(map(str, skipped_rows[:5]))}\n"
                f"(학번 또는 이름이 비어있거나 컬럼이 부족함)\n\n"
                f"유효한 학생 정보: {valid_count}명"
            )

    return student_info_dict


def generate_subject_pdf_report(subject, subject_df, subject_label):
    """과목별 PDF 리포트 생성"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                           rightMargin=30, leftMargin=30, 
                           topMargin=30, bottomMargin=30)
    
    # 스토리 (PDF 내용)
    story = []

    # 한글 폰트 설정
    font_name = setup_korean_font_for_pdf()

    # 스타일 정의
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName=font_name
    )
    
    # 제목
    title_text = f"{subject} 과목 채점 리포트"
    if font_name == 'Helvetica':
        title_text = f"{subject} Subject Report"  # 폰트 실패 시 영문으로
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 1. 기본 통계
    story.append(Paragraph("1. Basic Statistics" if font_name == 'Helvetica' else "1. 기본 통계", heading_style))
    
    stats_data = [
        ['Item' if font_name == 'Helvetica' else '항목', 'Value' if font_name == 'Helvetica' else '값'],
        ['Students' if font_name == 'Helvetica' else '인원', f"{len(subject_df)}"],
        ['Average' if font_name == 'Helvetica' else '평균 점수', f"{subject_df['총점'].mean():.1f}"],
        ['Std Dev' if font_name == 'Helvetica' else '표준편차', f"{subject_df['총점'].std():.2f}"],
        ['Max Score' if font_name == 'Helvetica' else '최고 점수', f"{subject_df['총점'].max()}"],
        ['Min Score' if font_name == 'Helvetica' else '최저 점수', f"{subject_df['총점'].min()}"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 2. 점수 분포
    story.append(Paragraph("2. Score Distribution" if font_name == 'Helvetica' else "2. 점수 분포 (10점 단위)", heading_style))
    
    # 점수 분포 계산
    bins = list(range(0, 101, 10))
    labels = [f"{i}-{i+9}" for i in range(0, 100, 10)]
    subject_df_temp = subject_df.copy()
    subject_df_temp['점수구간'] = pd.cut(subject_df_temp['총점'], bins=bins, labels=labels, include_lowest=True)
    score_dist = subject_df_temp['점수구간'].value_counts().sort_index()
    
    # 점수 분포 테이블
    dist_data = [['Score Range' if font_name == 'Helvetica' else '점수 구간', 'Students' if font_name == 'Helvetica' else '학생 수', 'Ratio' if font_name == 'Helvetica' else '비율']]
    for idx, count in score_dist.items():
        ratio = f"{(count / len(subject_df) * 100):.1f}%"
        dist_data.append([str(idx), str(count), ratio])
    
    dist_table = Table(dist_data, colWidths=[2*inch, 2*inch, 2*inch])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    story.append(dist_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 3. 오답 분석
    story.append(Paragraph("3. Wrong Answer Analysis" if font_name == 'Helvetica' else "3. 오답 분석", heading_style))
    
    # 오답 번호 파싱
    wrong_question_counts = {}
    for idx, row in subject_df.iterrows():
        wrong_nums = row['오답번호']
        if wrong_nums and wrong_nums != '없음':
            for num_str in str(wrong_nums).split(','):
                try:
                    num = int(num_str.strip())
                    wrong_question_counts[num] = wrong_question_counts.get(num, 0) + 1
                except:
                    pass
    
    if wrong_question_counts:
        sorted_wrong = sorted(wrong_question_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        
        wrong_data = [['Question No.' if font_name == 'Helvetica' else '문항 번호', 
                       'Wrong Count' if font_name == 'Helvetica' else '오답 인원', 
                       'Wrong Rate' if font_name == 'Helvetica' else '오답률']]
        for q_num, count in sorted_wrong:
            rate = f"{(count / len(subject_df) * 100):.1f}%"
            wrong_data.append([str(q_num), str(count), rate])
        
        wrong_table = Table(wrong_data, colWidths=[2*inch, 2*inch, 2*inch])
        wrong_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        story.append(wrong_table)
    else:
        no_wrong_text = "All students answered correctly!" if font_name == 'Helvetica' else "모든 학생이 전 문항을 맞췄습니다!"
        story.append(Paragraph(no_wrong_text, styles['Normal']))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer


def display_subject_statistics(subject_df, subject_code, result_df=None):
    """과목별 상세 통계를 표시하는 공통 함수

    Args:
        subject_df: 해당 과목의 채점 결과 DataFrame
        subject_code: 과목 코드 (str)
        result_df: 전체 결과 DataFrame (오답 CSV 다운로드용, optional)
    """
    # 과목별 기본 통계
    st.subheader(f"📊 {subject_code} 기본 통계")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("인원", f"{len(subject_df)}명")

    with col2:
        avg_score = subject_df['총점'].mean()
        st.metric("평균 점수", f"{avg_score:.1f}점")

    with col3:
        std_score = subject_df['총점'].std()
        st.metric("표준편차", f"{std_score:.2f}")

    with col4:
        max_score_s = subject_df['총점'].max()
        max_row_s = subject_df[subject_df['총점'] == max_score_s].iloc[0]
        if '이름' in subject_df.columns:
            max_label_s = f"{max_row_s['이름']} ({max_row_s['학번']})"
        else:
            max_label_s = f"수험번호: {max_row_s['수험번호']}"
        st.metric("최고 점수", f"{max_score_s}점", delta=max_label_s)

    with col5:
        min_score_s = subject_df['총점'].min()
        min_row_s = subject_df[subject_df['총점'] == min_score_s].iloc[0]
        if '이름' in subject_df.columns:
            min_label_s = f"{min_row_s['이름']} ({min_row_s['학번']})"
        else:
            min_label_s = f"수험번호: {min_row_s['수험번호']}"
        st.metric("최저 점수", f"{min_score_s}점", delta=min_label_s)

    # 점수 분포 (10점 단위)
    st.markdown("---")
    st.subheader("📊 점수 분포 (10점 단위)")

    # 10점 단위로 구간 나누기
    bins = list(range(0, 101, 10))
    labels = [f"{i}-{i+9}점" for i in range(0, 100, 10)]

    # 구간별 인원 계산
    subject_df_temp = subject_df.copy()
    subject_df_temp['점수구간'] = pd.cut(subject_df_temp['총점'], bins=bins, labels=labels, include_lowest=True)
    score_dist = subject_df_temp['점수구간'].value_counts().sort_index()

    # 데이터프레임으로 변환
    dist_df = pd.DataFrame({
        '점수 구간': score_dist.index,
        '학생 수': score_dist.values
    })
    dist_df['비율'] = (dist_df['학생 수'] / len(subject_df) * 100).round(1).astype(str) + '%'

    col1, col2 = st.columns([1, 2])

    with col1:
        # 표로 표시
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

    with col2:
        # 막대 그래프
        chart_data = dist_df.set_index('점수 구간')['학생 수']
        st.bar_chart(chart_data)

    # 오답 분석
    st.markdown("---")
    st.subheader("🔍 오답 분석")

    # 오답 번호를 파싱하여 각 문항별 오답 개수 계산
    wrong_question_counts = {}
    for idx, row in subject_df.iterrows():
        wrong_nums = row['오답번호']
        if wrong_nums and wrong_nums != '없음':
            for num_str in wrong_nums.split(','):
                try:
                    num = int(num_str.strip())
                    wrong_question_counts[num] = wrong_question_counts.get(num, 0) + 1
                except:
                    pass

    if wrong_question_counts:
        # 오답이 많은 순으로 정렬
        sorted_wrong = sorted(wrong_question_counts.items(), key=lambda x: x[1], reverse=True)

        # 상위 10개 문항 표시
        st.write("**오답이 많은 문항 TOP 10**")

        col1, col2 = st.columns([1, 3])

        with col1:
            # 표로 표시
            top_10 = sorted_wrong[:10]
            df_wrong = pd.DataFrame(top_10, columns=['문항 번호', '오답 인원'])
            df_wrong['오답률'] = (df_wrong['오답 인원'] / len(subject_df) * 100).round(1).astype(str) + '%'
            st.dataframe(df_wrong, use_container_width=True, hide_index=True)

        with col2:
            # 바 차트로 시각화
            chart_data = pd.DataFrame({
                '문항': [f"{q}번" for q, _ in sorted_wrong[:10]],
                '오답 인원': [count for _, count in sorted_wrong[:10]]
            })
            st.bar_chart(chart_data.set_index('문항'))

        # 전체 오답 분포
        with st.expander("📊 전체 문항별 오답 분포 보기"):
            all_wrong_df = pd.DataFrame(sorted_wrong, columns=['문항 번호', '오답 인원'])
            all_wrong_df['오답률'] = (all_wrong_df['오답 인원'] / len(subject_df) * 100).round(1).astype(str) + '%'
            st.dataframe(all_wrong_df, use_container_width=True, hide_index=True)

            # 오답 분포 CSV 다운로드
            wrong_csv = all_wrong_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=f"📥 {subject_code} 오답 분포 CSV 다운로드",
                data=wrong_csv,
                file_name=f"{subject_code}_오답분포_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("모든 학생이 전 문항을 맞췄습니다! 🎉")

    # 과목별 채점 결과 다운로드
    st.markdown("---")
    st.subheader("💾 이 과목 결과 다운로드")

    col1, col2 = st.columns(2)

    with col1:
        subject_csv = subject_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label=f"📥 CSV 다운로드",
            data=subject_csv,
            file_name=f"{subject_code}_채점결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        if REPORTLAB_AVAILABLE:
            # 고유한 키 생성을 위해 subject_code 사용
            button_key = f"pdf_{subject_code}_{id(subject_df)}"
            if st.button(f"📄 PDF 리포트 생성", key=button_key, use_container_width=True):
                with st.spinner("PDF 생성 중..."):
                    pdf_buffer = generate_subject_pdf_report(subject_code, subject_df, subject_code)
                    st.download_button(
                        label=f"📥 PDF 다운로드",
                        data=pdf_buffer,
                        file_name=f"{subject_code}_리포트_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"pdf_download_{subject_code}_{id(subject_df)}"
                    )
                st.success("✅ PDF가 생성되었습니다!")
        else:
            st.info("📄 PDF 기능을 사용하려면 reportlab을 설치하세요.\n\n`pip install reportlab`")


def grade_students(student_df, answer_df, student_info_dict=None, subject_code_mapping=None, debug_mode=False):
    """채점 수행"""
    results = []
    
    # 디버깅 모드일 때만 파일 구조 표시
    if debug_mode:
        with st.expander("🔍 파일 구조 확인 (디버깅)", expanded=True):
            st.write("**📋 학생 답안 파일 열 구조**")
            st.write(f"- 전체 열 이름: {list(student_df.columns)}")
            st.write(f"- 1번째 열 (columns[0]): **{student_df.columns[0]}** ← 수험번호")
            st.write(f"- 2번째 열 (columns[1]): **{student_df.columns[1]}** ← 과목코드")
            st.write(f"- 3번째 열부터 (columns[2:]): 답안")
            st.write("")
            st.write("**📋 정답 파일 열 구조**")
            st.write(f"- 전체 열 이름: {list(answer_df.columns)}")
            st.write(f"- 1번째 열 (columns[0]): **{answer_df.columns[0]}** ← 과목번호")
            st.write(f"- 2번째 열 (columns[1]): **{answer_df.columns[1]}** ← 문항 번호")
            st.write(f"- 3번째 열 (columns[2]): **{answer_df.columns[2]}** ← 정답")
            st.write(f"- 4번째 열 (columns[3]): **{answer_df.columns[3]}** ← 배점")
    
    # 첫 번째와 두 번째 열은 수험번호, 과목코드
    id_col = student_df.columns[0]
    subject_col = student_df.columns[1]
    
    # 정답 데이터를 과목별로 그룹화
    answer_dict = {}
    for subject in answer_df[answer_df.columns[0]].unique():
        subject_answers = answer_df[answer_df[answer_df.columns[0]] == subject]
        # 문항 번호 순으로 정렬
        subject_answers = subject_answers.sort_values(by=subject_answers.columns[1])
        answer_dict[subject] = {
            'answers': subject_answers[subject_answers.columns[2]].tolist(),
            'points': subject_answers[subject_answers.columns[3]].tolist()
        }
    
    # 디버깅: 정답 데이터 확인
    if debug_mode:
        with st.expander("🔍 정답 데이터 구조 (디버깅)", expanded=False):
            for subj, data in answer_dict.items():
                st.info(f"📚 **과목코드: {subj}**")
                st.write(f"- 문항 수: {len(data['answers'])}개")
                st.write(f"- 정답 (1~5번): {data['answers'][:5]}")
                st.write(f"- 배점 (1~5번): {data['points'][:5]}")
                try:
                    total = sum([float(p) for p in data['points']])
                    st.write(f"- ✅ **만점: {int(total)}점**")
                except:
                    st.error(f"- ❌ 배점 합계 계산 오류: {data['points']}")
                st.write("---")
    
    # 디버깅 모드일 때 학생별 채점 과정 표시
    if debug_mode:
        debug_expander = st.expander("🔍 학생별 채점 과정 (디버깅)", expanded=False)
    
    # 각 학생별로 채점
    for idx, row in student_df.iterrows():
        student_id = row[id_col]
        subject = row[subject_col]

        if subject not in answer_dict:
            available_subjects = ', '.join([str(s) for s in answer_dict.keys()])
            st.error(
                f"❌ 과목코드 매칭 오류\n\n"
                f"학생 답안의 과목코드 '{subject}'에 해당하는 정답이 없습니다.\n"
                f"수험번호: {student_id}\n\n"
                f"정답 파일에 있는 과목코드: {available_subjects}\n\n"
                f"해결방법:\n"
                f"1. 정답 파일에 과목코드 '{subject}'의 정답을 추가하세요\n"
                f"2. 학생 답안 파일의 과목코드가 올바른지 확인하세요\n"
                f"3. 과목코드가 정확히 일치하는지 확인하세요 (대소문자, 공백 주의)"
            )
            continue

        answers = answer_dict[subject]['answers']
        points = answer_dict[subject]['points']

        # 총 문항 수 (정답지 기준)
        total_questions = len(answers)

        # 배점을 숫자로 변환 (문자열로 읽힌 경우 대비)
        points_numeric = []
        for p_idx, p in enumerate(points):
            try:
                points_numeric.append(float(p))
            except (ValueError, TypeError):
                st.error(
                    f"❌ 배점 변환 오류\n\n"
                    f"과목코드: {subject}, 문항: {p_idx + 1}번\n"
                    f"잘못된 배점 값: '{p}'\n\n"
                    f"해결방법:\n"
                    f"1. 정답 파일의 배점 컬럼에 숫자만 입력하세요\n"
                    f"2. 해당 문항의 배점을 수정하세요"
                )
                points_numeric.append(0)

        max_score = sum(points_numeric)

        # 학생 답안 (3번째 열부터)
        student_answers = row[2:].tolist()

        # 학생 답안 수와 정답 문항 수 비교
        if len(student_answers) < total_questions:
            st.warning(
                f"⚠️ 답안 부족 경고\n\n"
                f"수험번호: {student_id}, 과목: {subject}\n"
                f"정답지 문항 수: {total_questions}개\n"
                f"학생 답안 수: {len(student_answers)}개\n\n"
                f"누락된 {total_questions - len(student_answers)}개 문항은 오답 처리됩니다."
            )
        
        # 디버깅: 학생 답안 확인
        if debug_mode:
            with debug_expander:
                st.success(f"👤 **학생 {student_id} - 과목코드: {subject}로 채점**")
                st.write(f"- 학생 답안 (1~5번): {student_answers[:5]}")
                st.write(f"- 정답 (1~5번): {answers[:5]}")
                st.write(f"- 이 학생은 **{subject} 과목의 정답**으로 채점합니다")
        
        total_score = 0
        correct_count = 0
        wrong_questions = []
        
        # 채점 (정답지 기준으로 반복)
        for i in range(total_questions):
            question_num = i + 1
            correct_ans = answers[i]
            point = points_numeric[i]
            
            # 학생 답안이 존재하는지 확인
            if i < len(student_answers):
                student_ans = student_answers[i]
                
                # 답안 비교 (문자열로 변환하여 비교)
                if pd.notna(student_ans) and pd.notna(correct_ans):
                    # 공백 제거
                    student_ans_str = str(student_ans).strip()
                    correct_ans_str = str(correct_ans).strip()
                    
                    # 숫자인 경우 정수/실수 비교, 문자인 경우 문자열 비교
                    try:
                        # 숫자로 변환 시도
                        if float(student_ans_str) == float(correct_ans_str):
                            total_score += point
                            correct_count += 1
                        else:
                            wrong_questions.append(question_num)
                    except:
                        # 문자열 비교
                        if student_ans_str == correct_ans_str:
                            total_score += point
                            correct_count += 1
                        else:
                            wrong_questions.append(question_num)
                else:
                    # 답을 적지 않은 경우 (빈칸)
                    wrong_questions.append(question_num)
            else:
                # 학생이 해당 문항을 아예 작성하지 않은 경우
                wrong_questions.append(question_num)
        
        # 디버깅: 점수 계산 확인
        if debug_mode:
            with debug_expander:
                st.write(f"✅ **채점 완료** - 총점: **{int(total_score)}점** / 만점: **{int(max_score)}점** / 정답수: **{correct_count}/{total_questions}개**")
                st.write("---")
        
        # 학생 정보 매칭 (3가지 방식 시도)
        result_dict = {'수험번호': student_id}
        
        if student_info_dict:
            matched_info = None
            student_id_str = str(student_id)
            
            # 1순위: 완전 매칭 (학번+전화번호)
            if student_id_str in student_info_dict['by_full']:
                matched_info = student_info_dict['by_full'][student_id_str]
            
            # 2순위: 학번으로 매칭 (수험번호가 학번으로 시작하는지)
            elif not matched_info:
                for student_num, info in student_info_dict['by_student_id'].items():
                    if student_id_str.startswith(student_num) or student_id_str == student_num:
                        matched_info = info
                        break
            
            # 3순위: 전화번호로 매칭 (수험번호가 전화번호로 끝나는지)
            if not matched_info:
                for phone, info in student_info_dict['by_phone'].items():
                    if student_id_str.endswith(phone) or student_id_str == phone:
                        matched_info = info
                        break
            
            # 매칭된 정보가 있으면 추가
            if matched_info:
                result_dict['학번'] = matched_info['학번']
                result_dict['전화번호'] = matched_info['전화번호']
                result_dict['이름'] = matched_info['이름']
        
        # 과목명 매핑
        subject_name = subject
        if subject_code_mapping and str(subject) in subject_code_mapping:
            subject_name = subject_code_mapping[str(subject)]
        
        result_dict.update({
            '과목코드': subject,
            '과목명': subject_name,
            '총점': int(total_score),
            '만점': int(max_score),
            '정답수': f"{correct_count}/{total_questions}",
            '오답번호': ', '.join(map(str, wrong_questions)) if wrong_questions else '없음'
        })
        
        results.append(result_dict)
    
    return pd.DataFrame(results)


# 메인 영역
if student_file and answer_file:
    try:
        # 탐구 과목 여부 확인
        is_tamgu = st.session_state.get('subject_type') == '탐구'
        
        # 데이터 로드
        with st.spinner("📂 파일을 불러오는 중..."):
            student_df = load_student_data(student_file, is_tamgu=is_tamgu)
            answer_df = load_answer_data(answer_file)
            
            # 학생 정보 파일 로드 (선택사항)
            student_info_dict = None
            if student_info_file:
                student_info_dict = load_student_info(student_info_file)
            
            # 파일이 변경되면 기존 결과 초기화
            info_file_name = student_info_file.name if student_info_file else None
            current_files = (student_file.name, answer_file.name, info_file_name)
            if 'previous_files' not in st.session_state or st.session_state['previous_files'] != current_files:
                st.session_state['previous_files'] = current_files
                if 'result_df' in st.session_state:
                    del st.session_state['result_df']
        
        # 데이터 미리보기 (접기 가능)
        with st.expander("📂 업로드된 파일 미리보기", expanded=False):
            if student_info_dict:
                col1, col2, col3 = st.columns(3)
            else:
                col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 학생 답안 데이터")
                st.dataframe(student_df.head(), use_container_width=True)
                st.caption(f"총 {len(student_df)}명의 학생")
            
            with col2:
                st.subheader("✅ 정답 및 배점 데이터")
                st.dataframe(answer_df.head(), use_container_width=True)
                st.caption(f"총 {len(answer_df)}개 문항")
            
            if student_info_dict:
                with col3:
                    st.subheader("📇 학생 정보 데이터")
                    # 딕셔너리를 데이터프레임으로 변환
                    info_display = []
                    for student_num, info in list(student_info_dict['by_student_id'].items())[:5]:
                        full_id = info['학번'] + info['전화번호']
                        info_display.append({
                            '수험번호': full_id,
                            '학번': info['학번'],
                            '전화번호': info['전화번호'],
                            '이름': info['이름']
                        })
                    st.dataframe(pd.DataFrame(info_display), use_container_width=True)
                    st.caption(f"총 {len(student_info_dict['by_student_id'])}명의 학생 정보")
        
        st.markdown("---")
        
        # 채점 버튼
        if st.button("🎯 채점 시작", type="primary", use_container_width=True):
            with st.spinner("⚡ 채점 중..."):
                # 과목코드 매핑 가져오기
                subject_code_mapping = st.session_state.get('subject_code_mapping', {})
                result_df = grade_students(student_df, answer_df, student_info_dict, subject_code_mapping, debug_mode)
                # session_state에 저장하여 페이지 새로고침 시에도 유지
                st.session_state['result_df'] = result_df
            
            if student_info_dict:
                st.success("✅ 채점이 완료되었습니다! (학생 이름 포함)")
            else:
                st.success("✅ 채점이 완료되었습니다!")
        
        # session_state에서 결과 가져오기
        if 'result_df' in st.session_state:
            result_df = st.session_state['result_df']
            
            # 결과 표시
            st.subheader("📊 채점 결과")
            
            # 화면 표시용 DataFrame (수험번호 제거)
            display_df = result_df.copy()
            if '이름' in display_df.columns and '학번' in display_df.columns:
                # 학생 정보가 있는 경우: 이름, 학번 순서로 표시 (수험번호 제거)
                display_columns = ['이름', '학번', '전화번호', '과목코드', '과목명', '총점', '만점', '정답수', '오답번호']
                display_df = display_df[display_columns]
            # 학생 정보가 없는 경우: 수험번호 그대로 표시
            
            st.dataframe(display_df, use_container_width=True)
            
            # 전체 기본 통계
            st.markdown("---")
            st.subheader("📈 전체 기본 통계")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("총 인원", f"{len(result_df)}명")
            
            with col2:
                avg_score = result_df['총점'].mean()
                st.metric("전체 평균", f"{avg_score:.1f}점")
            
            with col3:
                std_score = result_df['총점'].std()
                st.metric("표준편차", f"{std_score:.2f}")
            
            with col4:
                max_score = result_df['총점'].max()
                max_row = result_df[result_df['총점'] == max_score].iloc[0]
                if '이름' in result_df.columns:
                    max_label = f"{max_row['이름']} ({max_row['학번']})"
                else:
                    max_label = f"수험번호: {max_row['수험번호']}"
                st.metric("최고 점수", f"{max_score}점", delta=max_label)
            
            with col5:
                min_score = result_df['총점'].min()
                min_row = result_df[result_df['총점'] == min_score].iloc[0]
                if '이름' in result_df.columns:
                    min_label = f"{min_row['이름']} ({min_row['학번']})"
                else:
                    min_label = f"수험번호: {min_row['수험번호']}"
                st.metric("최저 점수", f"{min_score}점", delta=min_label)
            
            # 과목별 통계 요약
            st.markdown("---")
            st.subheader("📚 과목별 통계 요약")
            
            subject_stats = result_df.groupby('과목코드').agg({
                '수험번호': 'count',
                '총점': ['mean', 'std', 'max', 'min']
            }).round(2)
            
            subject_stats.columns = ['응시 인원', '평균', '표준편차', '최고점', '최저점']
            st.dataframe(subject_stats, use_container_width=True)
            
            # 과목별 상세 통계 (탭으로 구분)
            st.markdown("---")
            st.subheader("📖 과목별 상세 통계")
            
            subjects = sorted(result_df['과목코드'].unique().tolist())
            
            if len(subjects) > 1:
                tabs = st.tabs([f"📘 {subject}" for subject in subjects])

                for tab, subject in zip(tabs, subjects):
                    with tab:
                        # 해당 과목 데이터 필터링
                        subject_df = result_df[result_df['과목코드'] == subject].copy()

                        # 공통 함수 호출
                        display_subject_statistics(subject_df, subject, result_df)
            else:
                # 과목이 하나만 있는 경우 탭 없이 바로 표시
                subject = subjects[0]
                subject_df = result_df.copy()

                # 공통 함수 호출
                display_subject_statistics(subject_df, subject, result_df)

            # 전체 다운로드
            st.markdown("---")
            st.subheader("💾 전체 결과 다운로드")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV 다운로드
                csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 전체 채점 결과 CSV 다운로드",
                    data=csv,
                    file_name=f"전체_채점결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # 전체 통계 리포트 이미지 다운로드
                if st.button("📊 전체 통계 리포트 이미지 생성", use_container_width=True):
                    with st.spinner("이미지 생성 중..."):
                        # 통계 리포트 이미지 생성
                        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                        fig.suptitle('채점 통계 리포트 (전체)', fontsize=20, fontweight='bold', y=0.98)

                        # 한글 폰트 설정
                        setup_korean_font_for_matplotlib()

                        # 1. 기본 통계 표
                        ax1 = axes[0, 0]
                        ax1.axis('off')
                        stats_data = [
                            ['인원', f"{len(result_df)}명"],
                            ['평균 점수', f"{result_df['총점'].mean():.1f}점"],
                            ['표준편차', f"{result_df['총점'].std():.2f}"],
                            ['최고 점수', f"{result_df['총점'].max()}점 (수험번호: {result_df[result_df['총점'] == result_df['총점'].max()]['수험번호'].values[0]})"],
                            ['최저 점수', f"{result_df['총점'].min()}점 (수험번호: {result_df[result_df['총점'] == result_df['총점'].min()]['수험번호'].values[0]})"]
                        ]
                        table1 = ax1.table(cellText=stats_data, cellLoc='left', loc='center',
                                          colWidths=[0.3, 0.7])
                        table1.auto_set_font_size(False)
                        table1.set_fontsize(12)
                        table1.scale(1, 3)
                        for i in range(len(stats_data)):
                            table1[(i, 0)].set_facecolor('#E8F4F8')
                            table1[(i, 0)].set_text_props(weight='bold')
                        ax1.set_title('📈 전체 기본 통계', fontsize=16, fontweight='bold', pad=20)
                        
                        # 2. 과목별 평균 점수
                        ax2 = axes[0, 1]
                        if len(result_df['과목코드'].unique()) > 1:
                            subject_means = result_df.groupby('과목코드')['총점'].mean().sort_values(ascending=False)
                            subjects_list = list(subject_means.index)
                            means = list(subject_means.values)
                            bars = ax2.bar(subjects_list, means, color='lightgreen', edgecolor='black', alpha=0.7)
                            ax2.set_ylabel('평균 점수', fontsize=12)
                            ax2.set_title('📚 과목별 평균 점수', fontsize=16, fontweight='bold', pad=20)
                            ax2.grid(axis='y', alpha=0.3)
                            # 막대에 숫자 표시
                            for bar, mean in zip(bars, means):
                                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                                        f'{mean:.1f}', ha='center', va='bottom', fontsize=10)
                        else:
                            ax2.text(0.5, 0.5, '단일 과목', ha='center', va='center', fontsize=14)
                            ax2.axis('off')
                        
                        # 3. 과목별 응시 인원
                        ax3 = axes[1, 0]
                        subject_counts = result_df['과목코드'].value_counts().sort_index()
                        bars = ax3.barh(subject_counts.index, subject_counts.values, color='skyblue', edgecolor='black', alpha=0.7)
                        ax3.set_xlabel('응시 인원', fontsize=12)
                        ax3.set_title('📊 과목별 응시 인원', fontsize=16, fontweight='bold', pad=20)
                        ax3.invert_yaxis()
                        ax3.grid(axis='x', alpha=0.3)
                        # 막대에 숫자 표시
                        for bar, count in zip(bars, subject_counts.values):
                            ax3.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                                    f' {count}명', va='center', fontsize=10)
                        
                        # 4. 전체 점수 분포
                        ax4 = axes[1, 1]
                        ax4.hist(result_df['총점'], bins=10, color='coral', edgecolor='black', alpha=0.7)
                        ax4.set_xlabel('점수', fontsize=12)
                        ax4.set_ylabel('학생 수', fontsize=12)
                        ax4.set_title('📊 전체 점수 분포', fontsize=16, fontweight='bold', pad=20)
                        ax4.grid(axis='y', alpha=0.3)
                        
                        plt.tight_layout()
                        
                        # 이미지를 바이트로 저장
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                        buf.seek(0)
                        plt.close()
                        
                        # 다운로드 버튼 표시
                        st.download_button(
                            label="📥 통계 리포트 이미지 다운로드",
                            data=buf,
                            file_name=f"전체통계리포트_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        st.success("✅ 이미지가 생성되었습니다!")
            
    except Exception as e:
        error_msg = str(e)
        # 이미 상세한 에러 메시지인 경우 그대로 표시
        if "❌" in error_msg and "해결방법:" in error_msg:
            st.error(error_msg)
        else:
            # 일반 에러의 경우 간단한 안내 추가
            st.error(
                f"❌ 오류가 발생했습니다\n\n"
                f"{error_msg}\n\n"
                f"💡 도움말:\n"
                f"1. 샘플 파일을 다운로드하여 형식을 확인하세요\n"
                f"2. 파일 인코딩이 UTF-8인지 확인하세요\n"
                f"3. 필수 컬럼이 모두 있는지 확인하세요\n"
                f"4. 디버깅 모드를 활성화하면 더 자세한 정보를 볼 수 있습니다"
            )
        
else:
    # 안내 메시지
    st.info("👈 왼쪽 사이드바에서 파일을 업로드해주세요.")
    
    st.markdown("---")
    st.subheader("📌 사용 방법")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 1️⃣ 학생 답안 파일 형식
        
        | 수험번호 | 과목코드 | 1번 | 2번 | 3번 | ... |
        |---------|---------|-----|-----|-----|-----|
        | 2024001 | MATH01  | 1   | 3   | 2   | ... |
        | 2024002 | ENG01   | 4   | 1   | 3   | ... |
        
        - 첫 번째 열: 수험번호
        - 두 번째 열: 과목코드
        - 세 번째 열부터: 각 문항 답안
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ 정답/배점 파일 형식
        
        | 과목번호 | 문항 | 정답 | 배점 |
        |---------|------|------|------|
        | MATH01  | 1    | 1    | 5    |
        | MATH01  | 2    | 3    | 5    |
        | ENG01   | 1    | 4    | 10   |
        
        - 과목번호: 과목 코드
        - 문항: 문항 번호
        - 정답: 정답
        - 배점: 문항별 배점
        """)
    
    st.markdown("---")
    st.markdown("""
    ### ✨ 주요 기능
    - 📁 CSV 파일 드래그 앤 드롭 업로드
    - 🎯 과목코드별 자동 채점
    - 📊 점수 및 오답 번호 분석
    - 📈 통계 정보 제공
    - 💾 결과 CSV 다운로드
    """)



