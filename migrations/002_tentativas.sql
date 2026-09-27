ALTER TABLE mensagens_cruas ADD COLUMN tentativas INT NOT NULL DEFAULT 0;
ALTER TABLE mensagens_cruas ADD COLUMN ultimo_erro TEXT;
