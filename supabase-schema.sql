-- Croustillant Database Schema for Supabase (PostgreSQL)

-- Grant permissions on public schema (if needed)
-- Note: In Supabase SQL Editor, you should be connected as postgres superuser
-- If you get permission errors, ensure you're using the SQL Editor (not API)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id BIGSERIAL PRIMARY KEY,
    titre TEXT NOT NULL UNIQUE,
    temps_preparation TEXT,
    temps_cuisson TEXT,
    rendement TEXT,
    ingredients JSONB NOT NULL,
    instructions JSONB NOT NULL,
    image_url TEXT,
    category TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on title for faster searches
CREATE INDEX IF NOT EXISTS idx_recipes_titre ON recipes(titre);

-- Create index on category
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category);

-- Create GIN index on ingredients for faster JSON queries
CREATE INDEX IF NOT EXISTS idx_recipes_ingredients ON recipes USING GIN (ingredients);

-- Create GIN index on tags array
CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes USING GIN (tags);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_recipes_updated_at
    BEFORE UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Optional, for multi-user support later
-- ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for now (public access)
-- For future: You can add authentication and create policies per user
-- CREATE POLICY "Allow all operations" ON recipes FOR ALL USING (true);

COMMENT ON TABLE recipes IS 'Stores cooking recipes with ingredients and instructions';
COMMENT ON COLUMN recipes.ingredients IS 'JSON array of ingredients with nom, quantité, and unité';
COMMENT ON COLUMN recipes.instructions IS 'JSON array of instruction steps';
COMMENT ON COLUMN recipes.tags IS 'Array of tags for categorization and search';
