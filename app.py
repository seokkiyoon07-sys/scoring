import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="자동 채점 시스템",
    page_icon="📝",
    layout="wide"
)

# 타이틀
st.title("📝 자동 채점 시스템")
st.markdown("---")

# 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📁 파일 업로드")
    
    st.subheader("1. 학생 답안 파일")
    st.caption("형식: 수험번호 | 과목코드 | 1번 | 2번 | 3번 ...")
    student_file = st.file_uploader(
        "학생 답안 CSV 파일을 업로드하세요",
        type=['csv'],
        key='student'
    )
    
    st.subheader("2. 정답 및 배점 파일")
    st.caption("형식: 과목번호 | 문항 | 정답 | 배점")
    answer_file = st.file_uploader(
        "정답/배점 CSV 파일을 업로드하세요",
        type=['csv'],
        key='answer'
    )
    
    st.markdown("---")
    st.info("💡 두 파일을 모두 업로드하면 자동으로 채점이 시작됩니다.")
    
    st.markdown("---")
    st.subheader("⚙️ 설정")
    debug_mode = st.checkbox("🔧 디버깅 모드", value=False, help="파일 구조 및 채점 과정을 상세히 표시합니다")


def load_student_data(file):
    """학생 답안 파일 로드"""
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except:
        df = pd.read_csv(file, encoding='cp949')
    return df


def load_answer_data(file):
    """정답/배점 파일 로드"""
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except:
        df = pd.read_csv(file, encoding='cp949')
    return df


def grade_students(student_df, answer_df, debug_mode=False):
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
            st.warning(f"⚠️ 과목코드 '{subject}'의 정답이 없습니다. (수험번호: {student_id})")
            continue
        
        answers = answer_dict[subject]['answers']
        points = answer_dict[subject]['points']
        
        # 총 문항 수 (정답지 기준)
        total_questions = len(answers)
        
        # 배점을 숫자로 변환 (문자열로 읽힌 경우 대비)
        points_numeric = []
        for p in points:
            try:
                points_numeric.append(float(p))
            except:
                st.error(f"❌ 배점 변환 오류: {p}")
                points_numeric.append(0)
        
        max_score = sum(points_numeric)
        
        # 학생 답안 (3번째 열부터)
        student_answers = row[2:].tolist()
        
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
        
        results.append({
            '수험번호': student_id,
            '과목코드': subject,
            '총점': int(total_score),
            '만점': int(max_score),
            '정답수': f"{correct_count}/{total_questions}",
            '오답번호': ', '.join(map(str, wrong_questions)) if wrong_questions else '없음'
        })
    
    return pd.DataFrame(results)


# 메인 영역
if student_file and answer_file:
    try:
        # 데이터 로드
        with st.spinner("📂 파일을 불러오는 중..."):
            student_df = load_student_data(student_file)
            answer_df = load_answer_data(answer_file)
            
            # 파일이 변경되면 기존 결과 초기화
            current_files = (student_file.name, answer_file.name)
            if 'previous_files' not in st.session_state or st.session_state['previous_files'] != current_files:
                st.session_state['previous_files'] = current_files
                if 'result_df' in st.session_state:
                    del st.session_state['result_df']
        
        # 데이터 미리보기 (접기 가능)
        with st.expander("📂 업로드된 파일 미리보기", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 학생 답안 데이터")
                st.dataframe(student_df.head(), use_container_width=True)
                st.caption(f"총 {len(student_df)}명의 학생")
            
            with col2:
                st.subheader("✅ 정답 및 배점 데이터")
                st.dataframe(answer_df.head(), use_container_width=True)
                st.caption(f"총 {len(answer_df)}개 문항")
        
        st.markdown("---")
        
        # 채점 버튼
        if st.button("🎯 채점 시작", type="primary", use_container_width=True):
            with st.spinner("⚡ 채점 중..."):
                result_df = grade_students(student_df, answer_df, debug_mode)
                # session_state에 저장하여 페이지 새로고침 시에도 유지
                st.session_state['result_df'] = result_df
            
            st.success("✅ 채점이 완료되었습니다!")
        
        # session_state에서 결과 가져오기
        if 'result_df' in st.session_state:
            result_df = st.session_state['result_df']
            
            # 결과 표시
            st.subheader("📊 채점 결과")
            st.dataframe(result_df, use_container_width=True)
            
            # 과목 필터
            st.markdown("---")
            subjects = ['전체'] + sorted(result_df['과목코드'].unique().tolist())
            selected_subject = st.selectbox(
                "📚 통계를 볼 과목 선택",
                subjects,
                help="특정 과목만 선택하면 해당 과목의 통계만 표시됩니다"
            )
            
            # 선택한 과목에 따라 데이터 필터링
            if selected_subject == '전체':
                filtered_df = result_df.copy()
                subject_label = "전체"
            else:
                filtered_df = result_df[result_df['과목코드'] == selected_subject].copy()
                subject_label = f"{selected_subject}"
            
            # 통계 정보
            st.markdown("---")
            st.subheader(f"📈 기본 통계 ({subject_label})")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("인원", f"{len(filtered_df)}명")
            
            with col2:
                avg_score = filtered_df['총점'].mean()
                st.metric("평균 점수", f"{avg_score:.1f}점")
            
            with col3:
                std_score = filtered_df['총점'].std()
                st.metric("표준편차", f"{std_score:.2f}")
            
            with col4:
                max_score = filtered_df['총점'].max()
                max_student = filtered_df[filtered_df['총점'] == max_score]['수험번호'].values[0]
                st.metric("최고 점수", f"{max_score}점", delta=f"수험번호: {max_student}")
            
            with col5:
                min_score = filtered_df['총점'].min()
                min_student = filtered_df[filtered_df['총점'] == min_score]['수험번호'].values[0]
                st.metric("최저 점수", f"{min_score}점", delta=f"수험번호: {min_student}")
            
            # 점수 분포 (10점 단위)
            st.markdown("")
            st.subheader("📊 점수 분포 (10점 단위)")
            
            # 10점 단위로 구간 나누기
            bins = list(range(0, 101, 10))
            labels = [f"{i}-{i+9}점" for i in range(0, 100, 10)]
            
            # 구간별 인원 계산
            filtered_df['점수구간'] = pd.cut(filtered_df['총점'], bins=bins, labels=labels, include_lowest=True)
            score_dist = filtered_df['점수구간'].value_counts().sort_index()
            
            # 데이터프레임으로 변환
            dist_df = pd.DataFrame({
                '점수 구간': score_dist.index,
                '학생 수': score_dist.values
            })
            dist_df['비율'] = (dist_df['학생 수'] / len(filtered_df) * 100).round(1).astype(str) + '%'
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # 표로 표시
                st.dataframe(dist_df, use_container_width=True, hide_index=True)
            
            with col2:
                # 막대 그래프
                chart_data = dist_df.set_index('점수 구간')['학생 수']
                st.bar_chart(chart_data)
            
            # 점수구간 열 제거 (임시로 추가한 것)
            filtered_df = filtered_df.drop('점수구간', axis=1)
            
            # 오답 분석
            st.markdown("---")
            st.subheader("🔍 오답 분석")
            
            # 오답 번호를 파싱하여 각 문항별 오답 개수 계산
            wrong_question_counts = {}
            for idx, row in filtered_df.iterrows():
                wrong_nums = row['오답번호']
                if wrong_nums and wrong_nums != '없음':
                    for num_str in wrong_nums.split(','):
                        num = int(num_str.strip())
                        wrong_question_counts[num] = wrong_question_counts.get(num, 0) + 1
            
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
                    df_wrong['오답률'] = (df_wrong['오답 인원'] / len(filtered_df) * 100).round(1).astype(str) + '%'
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
                    all_wrong_df['오답률'] = (all_wrong_df['오답 인원'] / len(filtered_df) * 100).round(1).astype(str) + '%'
                    st.dataframe(all_wrong_df, use_container_width=True, hide_index=True)
                    
                    # 오답 분포 CSV 다운로드
                    wrong_csv = all_wrong_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 오답 분포 CSV 다운로드",
                        data=wrong_csv,
                        file_name=f"오답분포_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("모든 학생이 전 문항을 맞췄습니다! 🎉")
            
            # 과목별 통계 (과목코드가 여러 개인 경우)
            if len(result_df['과목코드'].unique()) > 1:
                st.markdown("---")
                st.subheader("📚 과목별 통계")
                
                subject_stats = result_df.groupby('과목코드').agg({
                    '수험번호': 'count',
                    '총점': ['mean', 'std', 'max', 'min']
                }).round(2)
                
                subject_stats.columns = ['응시 인원', '평균', '표준편차', '최고점', '최저점']
                st.dataframe(subject_stats, use_container_width=True)
            
            # 다운로드
            st.markdown("---")
            st.subheader("💾 결과 다운로드")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV 다운로드
                csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 채점 결과 CSV 다운로드",
                    data=csv,
                    file_name=f"채점결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # 통계 리포트 이미지 다운로드
                if st.button("📊 통계 리포트 이미지 생성", use_container_width=True):
                    with st.spinner("이미지 생성 중..."):
                        # 통계 리포트 이미지 생성
                        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                        fig.suptitle(f'채점 통계 리포트 ({subject_label})', fontsize=20, fontweight='bold', y=0.98)
                        
                        # 한글 폰트 설정 (맥의 경우 AppleGothic)
                        try:
                            plt.rcParams['font.family'] = 'AppleGothic'
                        except:
                            plt.rcParams['font.family'] = 'DejaVu Sans'
                        plt.rcParams['axes.unicode_minus'] = False
                        
                        # 1. 기본 통계 표
                        ax1 = axes[0, 0]
                        ax1.axis('off')
                        stats_data = [
                            ['인원', f"{len(filtered_df)}명"],
                            ['평균 점수', f"{filtered_df['총점'].mean():.1f}점"],
                            ['표준편차', f"{filtered_df['총점'].std():.2f}"],
                            ['최고 점수', f"{filtered_df['총점'].max()}점 (수험번호: {filtered_df[filtered_df['총점'] == filtered_df['총점'].max()]['수험번호'].values[0]})"],
                            ['최저 점수', f"{filtered_df['총점'].min()}점 (수험번호: {filtered_df[filtered_df['총점'] == filtered_df['총점'].min()]['수험번호'].values[0]})"]
                        ]
                        table1 = ax1.table(cellText=stats_data, cellLoc='left', loc='center',
                                          colWidths=[0.3, 0.7])
                        table1.auto_set_font_size(False)
                        table1.set_fontsize(12)
                        table1.scale(1, 3)
                        for i in range(len(stats_data)):
                            table1[(i, 0)].set_facecolor('#E8F4F8')
                            table1[(i, 0)].set_text_props(weight='bold')
                        ax1.set_title('📈 기본 통계', fontsize=16, fontweight='bold', pad=20)
                        
                        # 2. 점수 분포 (10점 단위)
                        ax2 = axes[0, 1]
                        bins = list(range(0, 101, 10))
                        labels = [f"{i}-{i+9}" for i in range(0, 100, 10)]
                        filtered_df_temp = filtered_df.copy()
                        filtered_df_temp['점수구간'] = pd.cut(filtered_df_temp['총점'], bins=bins, labels=labels, include_lowest=True)
                        score_dist = filtered_df_temp['점수구간'].value_counts().sort_index()
                        
                        bars = ax2.bar(score_dist.index, score_dist.values, color='skyblue', edgecolor='black', alpha=0.7)
                        ax2.set_xlabel('점수 구간', fontsize=12)
                        ax2.set_ylabel('학생 수', fontsize=12)
                        ax2.set_title('📊 점수 분포 (10점 단위)', fontsize=16, fontweight='bold', pad=20)
                        ax2.grid(axis='y', alpha=0.3)
                        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                        # 막대에 숫자 표시
                        for bar, count in zip(bars, score_dist.values):
                            if count > 0:
                                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                                        f'{int(count)}', ha='center', va='bottom', fontsize=10)
                        
                        # 3. 오답 TOP 10
                        if wrong_question_counts:
                            ax3 = axes[1, 0]
                            top_10 = sorted_wrong[:10]
                            questions = [f"{q}번" for q, _ in top_10]
                            counts = [c for _, c in top_10]
                            bars = ax3.barh(questions, counts, color='coral', edgecolor='black')
                            ax3.set_xlabel('오답 인원', fontsize=12)
                            ax3.set_title('🔍 오답이 많은 문항 TOP 10', fontsize=16, fontweight='bold', pad=20)
                            ax3.invert_yaxis()
                            ax3.grid(axis='x', alpha=0.3)
                            # 막대에 숫자 표시
                            for bar, count in zip(bars, counts):
                                ax3.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                                        f' {count}명', va='center', fontsize=10)
                        else:
                            ax3 = axes[1, 0]
                            ax3.text(0.5, 0.5, '오답 데이터 없음', ha='center', va='center', fontsize=14)
                            ax3.axis('off')
                        
                        # 4. 과목별 통계 (전체 선택 시에만 표시)
                        ax4 = axes[1, 1]
                        if selected_subject == '전체' and len(result_df['과목코드'].unique()) > 1:
                            subject_means = result_df.groupby('과목코드')['총점'].mean().sort_values(ascending=False)
                            subjects = list(subject_means.index)
                            means = list(subject_means.values)
                            bars = ax4.bar(subjects, means, color='lightgreen', edgecolor='black', alpha=0.7)
                            ax4.set_ylabel('평균 점수', fontsize=12)
                            ax4.set_title('📚 과목별 평균 점수', fontsize=16, fontweight='bold', pad=20)
                            ax4.grid(axis='y', alpha=0.3)
                            # 막대에 숫자 표시
                            for bar, mean in zip(bars, means):
                                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                                        f'{mean:.1f}', ha='center', va='bottom', fontsize=10)
                        else:
                            # 단일 과목 선택 시 점수 분포 히스토그램 추가
                            filtered_df_hist = filtered_df.copy()
                            ax4.hist(filtered_df_hist['총점'], bins=10, color='lightgreen', edgecolor='black', alpha=0.7)
                            ax4.set_xlabel('점수', fontsize=12)
                            ax4.set_ylabel('학생 수', fontsize=12)
                            ax4.set_title(f'📊 {subject_label} 점수 분포', fontsize=16, fontweight='bold', pad=20)
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
                            file_name=f"통계리포트_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        st.success("✅ 이미지가 생성되었습니다!")
            
    except Exception as e:
        st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        st.info("파일 형식을 확인해주세요.")
        
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



