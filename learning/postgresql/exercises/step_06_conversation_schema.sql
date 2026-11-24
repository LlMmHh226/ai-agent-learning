CREATE TABLE IF NOT EXISTS public.lesson_conversations (
    conversation_id text PRIMARY KEY CHECK (conversation_id ~ '^lesson-[a-z0-9-]+$'),
    messages jsonb NOT NULL CHECK (jsonb_typeof(messages) = 'array'),
    facts jsonb NOT NULL CHECK (jsonb_typeof(facts) = 'object'),
    revision uuid NOT NULL
);
