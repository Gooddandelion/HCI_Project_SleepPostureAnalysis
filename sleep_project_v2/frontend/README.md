# Frontend 개발 가이드

## 역할
- Supabase에서 데이터를 직접 읽어서 대시보드 UI를 구성합니다
- Backend(Kinect 촬영/분류)와 완전히 독립적으로 개발 가능합니다

---

## Supabase에서 읽어야 할 데이터

### posture_log 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| datetime | timestamptz | 촬영 시각 |
| posture | text | Supine / Lateral_L / Lateral_R / Prone |
| angle | float | 분류 신뢰도 |
| capture_type | text | regular / motion |
| image_path | text | 이미지 경로 |

### condition_log 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| log_date | date | 날짜 |
| refresh_level | int | 개운함 1~5 |
| pain_neck | bool | 목 통증 |
| pain_shoulder | bool | 어깨 통증 |
| pain_back | bool | 허리 통증 |
| memo | text | 자유 메모 |

---

## UI가 제공해야 할 화면 4개

### 1. 수면 시작 화면
- 트래킹 시작 버튼 1개
- 촬영 간격 설정 (선택)

### 2. 수면 결과 대시보드 (메인)
- 자세 분포 파이차트 (Supabase posture_log 조회)
- Sleep Posture Score
- 타임랩스 영상 플레이어

### 3. 인사이트 카드
- 자세별 비율 설명
- 통증 상관관계 (condition_log와 조합)

### 4. 기상 후 컨디션 입력
- 개운함 슬라이더 (1~5)
- 통증 부위 체크박스 (목 / 어깨 / 허리)
- 저장 버튼 → Supabase condition_log에 upsert

---

## 기술 스택 선택지

| 스택 | 장점 | 단점 |
|------|------|------|
| **Streamlit** (Python) | Backend와 같은 Python, 빠른 개발 | 디자인 자유도 낮음 |
| **React + Supabase JS** | 디자인 자유도 높음 | JS 환경 별도 필요 |
| **Flutter** | 모바일 앱으로도 빌드 가능 | 학습 곡선 있음 |

> 데모 기간(3~4주)을 고려하면 **Streamlit 추천**

---

## Streamlit 빠른 시작

```bash
pip install streamlit supabase python-dotenv
streamlit run app.py
```

Supabase 데이터 읽기 예시:
```python
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
data = supabase.table("posture_log").select("*").order("datetime", desc=True).limit(100).execute()
df = pd.DataFrame(data.data)
```
