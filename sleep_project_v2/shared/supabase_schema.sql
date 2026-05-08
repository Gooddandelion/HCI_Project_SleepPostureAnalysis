-- =====================================================
--  shared/supabase_schema.sql
--  Supabase 대시보드 → SQL Editor 에서 실행하세요
--  테이블 2개: posture_log / condition_log
-- =====================================================


-- ── 1. 자세 분류 결과 테이블 ──────────────────────
CREATE TABLE IF NOT EXISTS posture_log (
    id            BIGSERIAL PRIMARY KEY,
    timestamp     BIGINT       NOT NULL,           -- Unix timestamp
    datetime      TIMESTAMPTZ  NOT NULL,           -- 촬영 시각
    posture       TEXT         NOT NULL,           -- Supine / Lateral_L / Lateral_R / Prone / Unknown
    angle         FLOAT,                           -- 분류 신뢰도 각도
    capture_type  TEXT         NOT NULL,           -- regular / motion
    image_path    TEXT,                            -- 이미지 파일 경로 (로컬 or Storage URL)
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

-- 인덱스: 날짜 기준 조회 빠르게
CREATE INDEX IF NOT EXISTS idx_posture_log_datetime
    ON posture_log (datetime DESC);

-- 인덱스: 자세 기준 필터링
CREATE INDEX IF NOT EXISTS idx_posture_log_posture
    ON posture_log (posture);


-- ── 2. 기상 후 컨디션 입력 테이블 ────────────────
CREATE TABLE IF NOT EXISTS condition_log (
    id              BIGSERIAL PRIMARY KEY,
    log_date        DATE         NOT NULL UNIQUE,  -- 기록 날짜 (하루 1개)
    refresh_level   INT          CHECK (refresh_level BETWEEN 1 AND 5),
                                                   -- 개운함 1(최악) ~ 5(최고)
    pain_neck       BOOLEAN      DEFAULT FALSE,    -- 목 통증
    pain_shoulder   BOOLEAN      DEFAULT FALSE,    -- 어깨 통증
    pain_back       BOOLEAN      DEFAULT FALSE,    -- 허리 통증
    memo            TEXT,                          -- 자유 메모
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- 인덱스: 날짜 기준 조회
CREATE INDEX IF NOT EXISTS idx_condition_log_date
    ON condition_log (log_date DESC);


-- ── 3. 샘플 데이터 (테스트용) ─────────────────────
-- 실제 사용 전 아래 INSERT로 연결 테스트 가능

INSERT INTO posture_log (timestamp, datetime, posture, angle, capture_type, image_path)
VALUES
(1746000000, '2025-05-07 23:00:00+09', 'Supine',    72.3, 'regular', '/sleep_frames/20250507/1746000000_regular_color.png'),
(1746003600, '2025-05-08 00:00:00+09', 'Lateral_L', 18.5, 'regular', '/sleep_frames/20250507/1746003600_regular_color.png'),
(1746007200, '2025-05-08 01:00:00+09', 'Lateral_R', 22.1, 'motion',  '/sleep_frames/20250507/1746007200_motion_color.png');

INSERT INTO condition_log (log_date, refresh_level, pain_neck, pain_shoulder, pain_back, memo)
VALUES ('2025-05-08', 3, TRUE, FALSE, FALSE, '어깨가 약간 뻐근했음');
