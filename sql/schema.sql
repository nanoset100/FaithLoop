-- ============================================
-- FaithLoop - Database Schema
-- Supabase PostgreSQL + pgvector + Auth
-- 파일럿 100명용
-- ============================================

-- pgvector 확장 활성화 (Supabase Extensions에서 활성화 필요)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. profiles - 사용자 프로필 (Auth 연동)
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    role TEXT DEFAULT 'member',  -- 'member', 'admin'
    timezone TEXT DEFAULT 'Asia/Seoul',
    invite_code_used TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_select_own" ON profiles
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "profiles_insert_own" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "profiles_update_own" ON profiles
    FOR UPDATE USING (auth.uid() = user_id);


-- ============================================
-- 2. invite_codes - 초대코드 (파일럿용)
-- ============================================
CREATE TABLE IF NOT EXISTS invite_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    max_uses INTEGER,
    current_uses INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE invite_codes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "invite_codes_select_all" ON invite_codes
    FOR SELECT USING (true);
CREATE POLICY "invite_codes_update_admin" ON invite_codes
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.user_id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- 초대코드 사용량 증가 함수
CREATE OR REPLACE FUNCTION increment_invite_usage(code_param TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE invite_codes
    SET current_uses = current_uses + 1
    WHERE code = code_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 초기 데이터: 파일럿 초대코드
INSERT INTO invite_codes (code, description, max_uses)
VALUES ('FAITHLOOP2024', '파일럿 100명용 초대코드', 100)
ON CONFLICT (code) DO NOTHING;


-- ============================================
-- 3. checkins - 오늘의 기록 (일일 체크인)
-- ============================================
CREATE TABLE IF NOT EXISTS checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    mood TEXT CHECK (mood IN ('great', 'good', 'neutral', 'bad', 'terrible')),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    is_demo BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_checkins_user_id ON checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_checkins_created_at ON checkins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_checkins_mood ON checkins(mood);
CREATE INDEX IF NOT EXISTS idx_checkins_tags ON checkins USING GIN(tags);

ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "checkins_own" ON checkins
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 4. sermons - 설교 (관리자 등록)
-- ============================================
CREATE TABLE IF NOT EXISTS sermons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    sermon_date DATE NOT NULL,
    scripture TEXT,
    preacher TEXT,
    summary TEXT,
    application_question TEXT,
    status TEXT DEFAULT 'draft',  -- 'draft', 'published'
    published_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sermons_date ON sermons(sermon_date DESC);
CREATE INDEX IF NOT EXISTS idx_sermons_status ON sermons(status);

ALTER TABLE sermons ENABLE ROW LEVEL SECURITY;

-- 모든 로그인 사용자가 published 설교 조회 가능
CREATE POLICY "sermons_select_published" ON sermons
    FOR SELECT USING (status = 'published');

-- admin만 모든 설교 관리 가능
CREATE POLICY "sermons_admin_all" ON sermons
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.user_id = auth.uid()
            AND profiles.role = 'admin'
        )
    );


-- ============================================
-- 5. sermon_applications - 교인별 설교 적용
-- ============================================
CREATE TABLE IF NOT EXISTS sermon_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sermon_id UUID NOT NULL REFERENCES sermons(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    my_application TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sermon_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_sermon_applications_sermon ON sermon_applications(sermon_id);
CREATE INDEX IF NOT EXISTS idx_sermon_applications_user ON sermon_applications(user_id);

ALTER TABLE sermon_applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sermon_applications_own" ON sermon_applications
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 6. prayers - 기도노트
-- ============================================
CREATE TABLE IF NOT EXISTS prayers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT[],  -- {'가족', '건강', '사역', '직장', '감사', '중보', '회개', '기타'}
    status TEXT DEFAULT 'praying',  -- 'praying', 'answered', 'ongoing'
    answer_note TEXT,
    answered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prayers_user ON prayers(user_id);
CREATE INDEX IF NOT EXISTS idx_prayers_status ON prayers(status);
CREATE INDEX IF NOT EXISTS idx_prayers_created ON prayers(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prayers_tags ON prayers USING GIN(tags);

ALTER TABLE prayers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "prayers_own" ON prayers
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 7. artifacts - 멀티모달 첨부파일
-- ============================================
CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    checkin_id UUID REFERENCES checkins(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('image', 'audio', 'file')),
    storage_path TEXT NOT NULL,
    original_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_artifacts_checkin ON artifacts(checkin_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_user ON artifacts(user_id);

ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "artifacts_own" ON artifacts
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 8. extractions - AI 추출 데이터
-- ============================================
CREATE TABLE IF NOT EXISTS extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,  -- 'checkin', 'artifact', 'prayer'
    source_id UUID NOT NULL,
    extraction_type TEXT NOT NULL,  -- 'keywords', 'sentiment', 'summary'
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_extractions_source ON extractions(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_extractions_user ON extractions(user_id);

ALTER TABLE extractions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "extractions_own" ON extractions
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 9. memory_chunks - RAG용 텍스트 청크
-- ============================================
CREATE TABLE IF NOT EXISTS memory_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,  -- 'checkin', 'prayer', 'sermon_application'
    source_id UUID NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_chunks_user ON memory_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_chunks_source ON memory_chunks(source_type, source_id);

ALTER TABLE memory_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "memory_chunks_own" ON memory_chunks
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 10. memory_embeddings - 벡터 임베딩 (pgvector)
-- ============================================
CREATE TABLE IF NOT EXISTS memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_vector 
ON memory_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_user ON memory_embeddings(user_id);

ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "memory_embeddings_own" ON memory_embeddings
    FOR ALL USING (auth.uid() = user_id);


-- ============================================
-- 11. ai_logs - AI 호출 로그
-- ============================================
CREATE TABLE IF NOT EXISTS ai_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,  -- 'checkin_summary', 'weekly_report', 'rag_search'
    input_tokens INTEGER,
    output_tokens INTEGER,
    status TEXT DEFAULT 'success',  -- 'success', 'error'
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_logs_user ON ai_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_logs_created ON ai_logs(created_at DESC);

ALTER TABLE ai_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ai_logs_own" ON ai_logs
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "ai_logs_insert" ON ai_logs
    FOR INSERT WITH CHECK (true);


-- ============================================
-- 12. feedback - 피드백 수집 (파일럿)
-- ============================================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    category TEXT,  -- 'bug', 'feature', 'complaint', 'praise', 'other'
    content TEXT NOT NULL,
    screenshot_url TEXT,
    status TEXT DEFAULT 'new',  -- 'new', 'reviewed', 'in_progress', 'resolved'
    admin_note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback(created_at DESC);

ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "feedback_insert_all" ON feedback
    FOR INSERT WITH CHECK (true);
CREATE POLICY "feedback_select_own" ON feedback
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "feedback_admin_all" ON feedback
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.user_id = auth.uid()
            AND profiles.role = 'admin'
        )
    );


-- ============================================
-- RAG 검색 함수 (RPC)
-- ============================================
CREATE OR REPLACE FUNCTION search_memories(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    match_threshold FLOAT DEFAULT 0.7,
    user_id_filter UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    source_type TEXT,
    source_id UUID,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        me.id,
        me.source_type,
        me.source_id,
        me.content,
        1 - (me.embedding <=> query_embedding) AS similarity,
        me.created_at
    FROM memory_embeddings me
    WHERE 
        (user_id_filter IS NULL OR me.user_id = user_id_filter)
        AND 1 - (me.embedding <=> query_embedding) > match_threshold
    ORDER BY me.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ============================================
-- 트리거: updated_at 자동 갱신
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_checkins_updated_at
    BEFORE UPDATE ON checkins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sermons_updated_at
    BEFORE UPDATE ON sermons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sermon_applications_updated_at
    BEFORE UPDATE ON sermon_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prayers_updated_at
    BEFORE UPDATE ON prayers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at
    BEFORE UPDATE ON feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- 프로필 자동 생성 트리거 (Auth 연동)
-- ============================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, display_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- auth.users에 새 사용자 생성 시 자동으로 profiles 생성
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();


-- ============================================
-- 완료
-- ============================================
