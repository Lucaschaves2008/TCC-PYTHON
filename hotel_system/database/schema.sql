-- ============================================================
-- HOTEL SYSTEM — SCHEMA DO BANCO DE DADOS
-- ============================================================
-- Este arquivo é a representação SQL do que o ORM cria automaticamente.
-- Use para referência, documentação, ou rodar diretamente no MySQL.
-- ============================================================

-- Cria o banco se não existir
CREATE DATABASE IF NOT EXISTS hotel_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hotel_system;

-- ============================================================
-- TABELA: clientes
-- Representa os hóspedes do hotel.
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id          INT           NOT NULL AUTO_INCREMENT,
    nome        VARCHAR(100)  NOT NULL,
    email       VARCHAR(150)  NOT NULL,
    telefone    VARCHAR(20)   NULL,
    cpf         VARCHAR(14)   NOT NULL,
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_clientes_email (email),
    UNIQUE KEY uq_clientes_cpf   (cpf)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- TABELA: quartos
-- Representa os quartos físicos do hotel.
-- ============================================================
CREATE TABLE IF NOT EXISTS quartos (
    id           INT            NOT NULL AUTO_INCREMENT,
    numero       VARCHAR(10)    NOT NULL,
    tipo         ENUM(
                    'solteiro',
                    'casal',
                    'luxo',
                    'suite'
                 )              NOT NULL,
    status       ENUM(
                    'disponivel',
                    'ocupado',
                    'manutencao'
                 )              NOT NULL DEFAULT 'disponivel',
    capacidade   INT            NOT NULL DEFAULT 1,
    preco_diaria DECIMAL(10,2)  NOT NULL,
    descricao    VARCHAR(300)   NULL,
    created_at   DATETIME       DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_quartos_numero (numero)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- TABELA: reservas
-- Conecta clientes e quartos em um período de tempo.
--
-- REGRAS:
-- • cliente_id deve existir em clientes (FK RESTRICT = impede deletar cliente com reservas)
-- • quarto_id  deve existir em quartos  (FK RESTRICT = impede deletar quarto com reservas)
-- ============================================================
CREATE TABLE IF NOT EXISTS reservas (
    id           INT            NOT NULL AUTO_INCREMENT,
    cliente_id   INT            NOT NULL,
    quarto_id    INT            NOT NULL,
    check_in     DATETIME       NOT NULL,
    check_out    DATETIME       NOT NULL,
    status       ENUM(
                    'pendente',
                    'confirmada',
                    'checkin',
                    'checkout',
                    'cancelada'
                 )              NOT NULL DEFAULT 'pendente',
    total        DECIMAL(10,2)  NULL,
    observacoes  VARCHAR(500)   NULL,
    created_at   DATETIME       DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Índices para acelerar buscas por cliente e quarto
    INDEX idx_reservas_cliente (cliente_id),
    INDEX idx_reservas_quarto  (quarto_id),
    INDEX idx_reservas_status  (status),

    -- Chaves estrangeiras com ON DELETE RESTRICT:
    -- impede remover um cliente ou quarto que ainda tem reservas
    CONSTRAINT fk_reservas_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_reservas_quarto
        FOREIGN KEY (quarto_id) REFERENCES quartos (id)
        ON DELETE RESTRICT ON UPDATE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
