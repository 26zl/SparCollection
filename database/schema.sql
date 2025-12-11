-- Spar Collection Database Schema
-- PostgreSQL Database Schema for Shopping List Management System

-- Create schema
CREATE SCHEMA IF NOT EXISTS spar;

-- Set search path
SET search_path TO spar;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS spar.users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    shop_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee' CHECK (role IN ('employee', 'manager', 'admin')),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX idx_users_username ON spar.users(username);
CREATE INDEX idx_users_shop_id ON spar.users(shop_id);

-- Products table (for pricing and product catalog)
CREATE TABLE IF NOT EXISTS spar.products (
    sku VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_products_active ON spar.products(active);
CREATE INDEX idx_products_category ON spar.products(category);

-- Shopping lists table
CREATE TABLE IF NOT EXISTS spar.lists (
    id VARCHAR(255) PRIMARY KEY,
    shop_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed')),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    completed_by VARCHAR(255),
    CONSTRAINT chk_completed CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status = 'active' AND completed_at IS NULL)
    )
);

CREATE INDEX idx_lists_shop_id ON spar.lists(shop_id);
CREATE INDEX idx_lists_status ON spar.lists(status);
CREATE INDEX idx_lists_created_at ON spar.lists(created_at DESC);

-- List items table
CREATE TABLE IF NOT EXISTS spar.list_items (
    id VARCHAR(255) PRIMARY KEY,
    list_id VARCHAR(255) NOT NULL,
    sku VARCHAR(255),
    name VARCHAR(500) NOT NULL,
    qty_requested INTEGER NOT NULL DEFAULT 1,
    qty_collected INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'collected', 'unavailable')),
    version INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT fk_list_items_list FOREIGN KEY (list_id) REFERENCES spar.lists(id) ON DELETE CASCADE,
    CONSTRAINT fk_list_items_product FOREIGN KEY (sku) REFERENCES spar.products(sku) ON DELETE SET NULL
);

CREATE INDEX idx_list_items_list_id ON spar.list_items(list_id);
CREATE INDEX idx_list_items_status ON spar.list_items(status);
CREATE INDEX idx_list_items_sku ON spar.list_items(sku);

-- Payment transactions table (for audit trail)
CREATE TABLE IF NOT EXISTS spar.payment_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    list_id VARCHAR(255) NOT NULL,
    shop_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    completed_by VARCHAR(255),
    processed_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT,
    CONSTRAINT fk_payment_list FOREIGN KEY (list_id) REFERENCES spar.lists(id) ON DELETE CASCADE
);

CREATE INDEX idx_payment_list_id ON spar.payment_transactions(list_id);
CREATE INDEX idx_payment_shop_id ON spar.payment_transactions(shop_id);
CREATE INDEX idx_payment_processed_at ON spar.payment_transactions(processed_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for products table
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON spar.products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON SCHEMA spar IS 'Spar Collection shopping list management system';
COMMENT ON TABLE spar.products IS 'Product catalog with pricing information';
COMMENT ON TABLE spar.lists IS 'Shopping lists created for collection';
COMMENT ON TABLE spar.list_items IS 'Items within shopping lists';
COMMENT ON TABLE spar.payment_transactions IS 'Payment transaction audit trail';
