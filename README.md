# 🛌 수면 자세 분석 시스템
> HCI 팀플 Team 5 | Python 3.10.11 | Azure Kinect DK | Supabase

---

## 📁 프로젝트 구조

```
sleep_project/
│
├── config.py                        # 전체 공통 설정 (경로, 상수, 테이블명)
├── .env                             # Supabase 키 (Git 제외 ★)
├── .env.example                     # .env 템플릿
├── .gitignore
│
├── shared/
│   └── supabase_schema.sql          # DB 테이블 생성 SQL
│                                    # → Supabase SQL Editor에서 최초 1회 실행
│
├── backend/                         # Kinect 촬영 / 분류 담당 (팀원 A, B, C)
│   ├── notebooks/
│   │   ├── week2_00_supabase_test.ipynb      # Supabase 연결 테스트 ← 가장 먼저 실행
│   │   ├── week2_01_regular_capture.ipynb    # 정기 촬영
│   │   ├── week2_02_motion_capture.ipynb     # 움직임 감지 촬영
│   │   ├── week2_03_timelapse.ipynb          # 타임랩스 생성
│   │   └── week2_04_posture_classify.ipynb   # 자세 분류 + Supabase 저장
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py               # 촬영/분류/오버레이 함수
│   │   └── db.py                    # Supabase CRUD 함수
│   │
│   ├── sleep_frames/                # 촬영 이미지 (Git 제외)
│   │   └── YYYYMMDD/
│   │       ├── {ts}_regular_color.png
│   │       ├── {ts}_regular_depth.png
│   │       ├── {ts}_motion_color.png
│   │       └── {ts}_motion_depth.png
│   │
│   └── timelapse/                   # 타임랩스 mp4 (Git 제외)
│       └── YYYYMMDD_timelapse.mp4
│
└── frontend/                        # 대시보드 UI 담당 (팀원 D)
    ├── README.md                    # UI 개발 가이드
    └── app.py                       # (팀원 D가 생성)
```

---

## 🗄️ Supabase DB 구조

```
posture_log                          condition_log
──────────────────────────           ──────────────────────────
id            BIGSERIAL PK           id            BIGSERIAL PK
timestamp     BIGINT                 log_date      DATE UNIQUE
datetime      TIMESTAMPTZ            refresh_level INT (1~5)
posture       TEXT                   pain_neck     BOOLEAN
angle         FLOAT                  pain_shoulder BOOLEAN
capture_type  TEXT                   pain_back     BOOLEAN
image_path    TEXT                   memo          TEXT
created_at    TIMESTAMPTZ            created_at    TIMESTAMPTZ
```

---

## 🚀 처음 시작하는 순서

```
1. Supabase 프로젝트 생성 (https://supabase.com)
2. shared/supabase_schema.sql 실행 (SQL Editor)
3. .env.example → .env 복사 후 URL/KEY 입력
4. pip install supabase python-dotenv opencv-python numpy pandas matplotlib
5. backend/notebooks/week2_00_supabase_test.ipynb 실행 → 연결 확인
6. 나머지 노트북 순서대로 실행
```
---

## ⚠️ 팀원 공통 주의사항

1. **`.env` 파일은 절대 Git에 올리지 말 것** → Supabase 키 노출 위험
2. **자세 레이블은 `config.py` 상수 사용** → `POSTURE_SUPINE` 등
3. **DB 저장은 `utils/db.py` 함수만 사용** → 직접 SQL 작성 금지
4. **노트북 상단에 항상 경로 추가**
   ```python
   import sys; sys.path.append('../..')
   from config import *
   from utils import *
   ```
