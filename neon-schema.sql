-- Croustillant Database Schema for Neon DB (PostgreSQL)
-- Execute this in your Neon SQL Editor: https://console.neon.tech

-- Enable UUID extension (optional for future use)
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_recipes_titre ON recipes(titre);
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category);
CREATE INDEX IF NOT EXISTS idx_recipes_created_at ON recipes(created_at DESC);

-- Create GIN indexes for JSONB and array columns (better search performance)
CREATE INDEX IF NOT EXISTS idx_recipes_ingredients ON recipes USING GIN (ingredients);
CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes USING GIN (tags);

-- Full-text search index on instructions (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_recipes_instructions_fts
    ON recipes USING GIN (to_tsvector('french', instructions::text));

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
DROP TRIGGER IF EXISTS update_recipes_updated_at ON recipes;
CREATE TRIGGER update_recipes_updated_at
    BEFORE UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Add constraints for data validation
ALTER TABLE recipes ADD CONSTRAINT check_titre_not_empty
    CHECK (char_length(trim(titre)) > 0);

-- Comments for documentation
COMMENT ON TABLE recipes IS 'Stores cooking recipes with ingredients and instructions';
COMMENT ON COLUMN recipes.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN recipes.titre IS 'Recipe title, must be unique';
COMMENT ON COLUMN recipes.ingredients IS 'JSON array of ingredients with nom, quantité, and unité fields';
COMMENT ON COLUMN recipes.instructions IS 'JSON array of instruction steps';
COMMENT ON COLUMN recipes.tags IS 'Array of tags for categorization and search';
COMMENT ON COLUMN recipes.created_at IS 'Timestamp when recipe was created';
COMMENT ON COLUMN recipes.updated_at IS 'Timestamp when recipe was last updated';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Schema created successfully! You can now use your Croustillant application with Neon DB.';
END
$$;
