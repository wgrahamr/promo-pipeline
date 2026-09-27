INSERT INTO categorias (nome) VALUES
    ('Eletrônicos'),
    ('Casa e Cozinha'),
    ('Moda'),
    ('Beleza e Saúde'),
    ('Games'),
    ('Mercado'),
    ('Esportes e Lazer'),
    ('Automotivos')
    ON CONFLICT (nome) DO NOTHING;