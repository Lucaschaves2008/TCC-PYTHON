-- ============================================================
-- HOTEL SYSTEM — DADOS INICIAIS (SEED)
-- ============================================================
-- Popula o banco com dados de exemplo para desenvolvimento e testes.
-- Execute APÓS rodar schema.sql ou init_db.py.
--
-- Como usar:
--   mysql -u root -p hotel_system < database/seed.sql
-- ============================================================

USE hotel_system;

-- ============================================================
-- QUARTOS INICIAIS
-- ============================================================
INSERT INTO quartos (numero, tipo, status, capacidade, preco_diaria, descricao)
VALUES
    ('101', 'solteiro', 'disponivel', 1, 150.00, 'Quarto solteiro com banheiro privativo'),
    ('102', 'solteiro', 'disponivel', 1, 150.00, 'Quarto solteiro com vista para o jardim'),
    ('103', 'solteiro', 'disponivel', 1, 160.00, 'Quarto solteiro com varanda'),
    ('201', 'casal', 'disponivel', 2, 250.00, 'Quarto casal com vista interna'),
    ('202', 'casal', 'disponivel', 2, 280.00, 'Quarto casal com varanda e vista para a piscina'),
    ('203', 'casal', 'disponivel', 2, 260.00, 'Quarto casal com banheira'),
    ('301', 'luxo', 'disponivel', 2, 450.00, 'Quarto luxo com hidromassagem e sala de estar'),
    ('302', 'luxo', 'disponivel', 3, 500.00, 'Quarto luxo com varanda premium'),
    ('401', 'suite', 'disponivel', 4, 750.00, 'Suite com dois quartos, sala, cozinha e terraco'),
    ('402', 'suite', 'disponivel', 2, 900.00, 'Suite presidencial com vista panoramica')
;

-- ============================================================
-- CLIENTES DE TESTE
-- ============================================================
INSERT INTO clientes (nome, email, telefone, cpf)
VALUES
    ('Joao Silva Santos',    'joao.silva@email.com',     '(11) 99999-1111', '123.456.789-00'),
    ('Maria Oliveira Costa', 'maria.oliveira@email.com', '(21) 99999-2222', '987.654.321-00'),
    ('Carlos Pereira Lima',  'carlos.pereira@email.com', '(31) 99999-3333', '456.789.123-00')
;

-- ============================================================
-- RESERVAS DE EXEMPLO
-- ============================================================
INSERT INTO reservas (cliente_id, quarto_id, check_in, check_out, status, total, observacoes)
VALUES
    (1, 1, '2026-06-01 14:00:00', '2026-06-05 12:00:00', 'confirmada', 600.00, 'Cliente solicitou andar baixo'),
    (2, 4, '2026-06-10 14:00:00', '2026-06-15 12:00:00', 'pendente',   NULL,   NULL)
;
