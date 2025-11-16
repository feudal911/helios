-- ============================================================================
-- QUERIES ÚTEIS PARA O BANCO DE DADOS HELIOS - MYSQL
-- Sistema de Monitoramento e Manutenção Preditiva de Fazendas Solares
-- ============================================================================

-- Selecionar o banco de dados (IMPORTANTE: Execute isso primeiro!)
USE helios;

-- ============================================================================
-- 1. CONSULTAS BÁSICAS
-- ============================================================================

-- Listar todos os parques solares
SELECT id, nome, localizacao, capacidade_total_kw, status, data_instalacao
FROM parques
ORDER BY capacidade_total_kw DESC;

-- Listar todos os inversores com informações do parque
SELECT 
    i.id,
    i.codigo_serie,
    i.modelo,
    i.capacidade_kw,
    i.status,
    p.nome AS parque_nome,
    p.localizacao AS parque_localizacao
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
ORDER BY p.nome, i.codigo_serie;

-- Listar todas as placas solares com informações do inversor e parque
SELECT 
    pl.id,
    pl.codigo_serie,
    pl.modelo,
    pl.potencia_wp,
    pl.status,
    i.codigo_serie AS inversor_codigo,
    p.nome AS parque_nome
FROM placas_solares pl
INNER JOIN inversores i ON pl.inversor_id = i.id
INNER JOIN parques p ON i.parque_id = p.id
ORDER BY p.nome, i.codigo_serie, pl.codigo_serie;

-- ============================================================================
-- 2. CONSULTAS DE PERFORMANCE E GERAÇÃO
-- ============================================================================

-- Geração total por parque hoje
SELECT 
    p.nome AS parque,
    p.capacidade_total_kw,
    COALESCE(SUM(m.geracao_kw), 0) AS geracao_hoje_kw,
    ROUND((COALESCE(SUM(m.geracao_kw), 0) / p.capacidade_total_kw) * 100, 2) AS taxa_utilizacao_percent
FROM parques p
LEFT JOIN inversores i ON p.id = i.parque_id
LEFT JOIN medicoes_telemetria m ON i.id = m.inversor_id 
    AND m.data_medicao = CURDATE()
GROUP BY p.id, p.nome, p.capacidade_total_kw
ORDER BY geracao_hoje_kw DESC;

-- Geração total por parque nos últimos 7 dias
SELECT 
    p.nome AS parque,
    m.data_medicao,
    SUM(m.geracao_kw) AS geracao_diaria_kw
FROM parques p
INNER JOIN inversores i ON p.id = i.parque_id
INNER JOIN medicoes_telemetria m ON i.id = m.inversor_id
WHERE m.data_medicao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY p.id, p.nome, m.data_medicao
ORDER BY p.nome, m.data_medicao DESC;

-- Eficiência média por inversor hoje
SELECT 
    i.codigo_serie,
    i.capacidade_kw,
    p.nome AS parque,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media_percent,
    SUM(m.geracao_kw) AS geracao_total_kw,
    COUNT(m.id) AS num_medicoes
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
LEFT JOIN medicoes_telemetria m ON i.id = m.inversor_id 
    AND m.data_medicao = CURDATE()
WHERE i.status = 'operacional'
GROUP BY i.id, i.codigo_serie, i.capacidade_kw, p.nome
HAVING COUNT(m.id) > 0
ORDER BY eficiencia_media_percent DESC;

-- Top 10 inversores com maior geração hoje
SELECT 
    i.codigo_serie,
    i.modelo,
    i.capacidade_kw,
    p.nome AS parque,
    SUM(m.geracao_kw) AS geracao_total_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
INNER JOIN medicoes_telemetria m ON i.id = m.inversor_id
WHERE m.data_medicao = CURDATE()
GROUP BY i.id, i.codigo_serie, i.modelo, i.capacidade_kw, p.nome
ORDER BY geracao_total_kw DESC
LIMIT 10;

-- ============================================================================
-- 3. CONSULTAS DE ALERTAS
-- ============================================================================

-- Alertas ativos por severidade
SELECT 
    a.severidade,
    COUNT(*) AS quantidade,
    COUNT(DISTINCT a.inversor_id) AS inversores_afetados
FROM alertas a
WHERE a.resolvido = 0
GROUP BY a.severidade
ORDER BY 
    CASE a.severidade
        WHEN 'critica' THEN 1
        WHEN 'alta' THEN 2
        WHEN 'media' THEN 3
        WHEN 'baixa' THEN 4
    END;

-- Alertas ativos detalhados
SELECT 
    a.id,
    a.mensagem,
    a.severidade,
    a.criado_em,
    i.codigo_serie AS inversor,
    p.nome AS parque,
    r.nome AS regra
FROM alertas a
INNER JOIN inversores i ON a.inversor_id = i.id
INNER JOIN parques p ON i.parque_id = p.id
INNER JOIN regras r ON a.regra_id = r.id
WHERE a.resolvido = 0
ORDER BY 
    CASE a.severidade
        WHEN 'critica' THEN 1
        WHEN 'alta' THEN 2
        WHEN 'media' THEN 3
        WHEN 'baixa' THEN 4
    END,
    a.criado_em DESC;

-- Alertas por parque
SELECT 
    p.nome AS parque,
    COUNT(a.id) AS total_alertas,
    SUM(CASE WHEN a.resolvido = 0 THEN 1 ELSE 0 END) AS alertas_ativos,
    SUM(CASE WHEN a.severidade = 'critica' AND a.resolvido = 0 THEN 1 ELSE 0 END) AS criticos_ativos
FROM parques p
LEFT JOIN inversores i ON p.id = i.parque_id
LEFT JOIN alertas a ON i.id = a.inversor_id
GROUP BY p.id, p.nome
ORDER BY alertas_ativos DESC;

-- ============================================================================
-- 4. CONSULTAS DE EQUIPAMENTOS
-- ============================================================================

-- Inversores em manutenção ou inativos
SELECT 
    i.codigo_serie,
    i.modelo,
    i.status,
    i.localizacao_fisica,
    p.nome AS parque,
    COUNT(pl.id) AS num_placas
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
LEFT JOIN placas_solares pl ON i.id = pl.inversor_id
WHERE i.status IN ('manutencao', 'inativo')
GROUP BY i.id, i.codigo_serie, i.modelo, i.status, i.localizacao_fisica, p.nome
ORDER BY p.nome, i.codigo_serie;

-- Placas solares desligadas ou em manutenção
SELECT 
    pl.codigo_serie,
    pl.modelo,
    pl.potencia_wp,
    pl.status,
    i.codigo_serie AS inversor,
    p.nome AS parque
FROM placas_solares pl
INNER JOIN inversores i ON pl.inversor_id = i.id
INNER JOIN parques p ON i.parque_id = p.id
WHERE pl.status IN ('desligada', 'manutencao')
ORDER BY p.nome, i.codigo_serie, pl.codigo_serie;

-- Estatísticas de equipamentos por parque
SELECT 
    p.nome AS parque,
    COUNT(DISTINCT i.id) AS total_inversores,
    SUM(CASE WHEN i.status = 'operacional' THEN 1 ELSE 0 END) AS inversores_operacionais,
    COUNT(DISTINCT pl.id) AS total_placas,
    SUM(CASE WHEN pl.status = 'ligada' THEN 1 ELSE 0 END) AS placas_ligadas,
    ROUND(SUM(pl.potencia_wp) / 1000.0, 2) AS capacidade_total_placas_kw
FROM parques p
LEFT JOIN inversores i ON p.id = i.parque_id
LEFT JOIN placas_solares pl ON i.id = pl.inversor_id
GROUP BY p.id, p.nome
ORDER BY p.nome;

-- ============================================================================
-- 5. CONSULTAS DE TENDÊNCIAS E ANÁLISES
-- ============================================================================

-- Geração média por hora do dia (últimos 7 dias)
SELECT 
    HOUR(m.hora_medicao) AS hora,
    ROUND(AVG(m.geracao_kw), 2) AS geracao_media_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media,
    ROUND(AVG(m.temperatura), 1) AS temperatura_media
FROM medicoes_telemetria m
WHERE m.data_medicao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY HOUR(m.hora_medicao)
ORDER BY hora;

-- Comparação de geração: hoje vs ontem vs semana passada
SELECT 
    'Hoje' AS periodo,
    CURDATE() AS data_ref,
    SUM(m.geracao_kw) AS geracao_total_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media
FROM medicoes_telemetria m
WHERE m.data_medicao = CURDATE()
UNION ALL
SELECT 
    'Ontem' AS periodo,
    DATE_SUB(CURDATE(), INTERVAL 1 DAY) AS data_ref,
    SUM(m.geracao_kw) AS geracao_total_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media
FROM medicoes_telemetria m
WHERE m.data_medicao = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
UNION ALL
SELECT 
    'Semana Passada (mesmo dia)' AS periodo,
    DATE_SUB(CURDATE(), INTERVAL 7 DAY) AS data_ref,
    SUM(m.geracao_kw) AS geracao_total_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media
FROM medicoes_telemetria m
WHERE m.data_medicao = DATE_SUB(CURDATE(), INTERVAL 7 DAY);

-- Inversores com pior performance (eficiencia < 80%)
SELECT 
    i.codigo_serie,
    i.capacidade_kw,
    p.nome AS parque,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media,
    COUNT(m.id) AS num_medicoes,
    MIN(m.eficiencia) AS eficiencia_minima,
    MAX(m.eficiencia) AS eficiencia_maxima
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
INNER JOIN medicoes_telemetria m ON i.id = m.inversor_id
WHERE m.data_medicao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    AND m.eficiencia IS NOT NULL
GROUP BY i.id, i.codigo_serie, i.capacidade_kw, p.nome
HAVING AVG(m.eficiencia) < 80
ORDER BY eficiencia_media ASC;

-- ============================================================================
-- 6. CONSULTAS DE REGRAS
-- ============================================================================

-- Regras ativas e quantos alertas geraram
SELECT 
    r.nome,
    r.tipo,
    r.operador,
    r.valor_threshold,
    r.severidade,
    COUNT(a.id) AS total_alertas,
    SUM(CASE WHEN a.resolvido = 0 THEN 1 ELSE 0 END) AS alertas_ativos
FROM regras r
LEFT JOIN alertas a ON r.id = a.regra_id
WHERE r.ativo = 1
GROUP BY r.id, r.nome, r.tipo, r.operador, r.valor_threshold, r.severidade
ORDER BY alertas_ativos DESC, total_alertas DESC;

-- Regras que mais geram alertas
SELECT 
    r.nome AS regra,
    r.tipo,
    COUNT(a.id) AS total_alertas_gerados
FROM regras r
INNER JOIN alertas a ON r.id = a.regra_id
GROUP BY r.id, r.nome, r.tipo
ORDER BY total_alertas_gerados DESC
LIMIT 10;

-- ============================================================================
-- 7. CONSULTAS DE USUÁRIOS
-- ============================================================================

-- Listar todos os usuários
SELECT 
    id,
    username,
    email,
    nome,
    tipo,
    criado_em
FROM usuarios
ORDER BY tipo, nome;

-- Contagem de usuários por tipo
SELECT 
    tipo,
    COUNT(*) AS quantidade
FROM usuarios
GROUP BY tipo;

-- ============================================================================
-- 8. CONSULTAS DE MANUTENÇÃO PREDITIVA
-- ============================================================================

-- Inversores que precisam de atenção (baixa eficiência + alertas)
SELECT 
    i.codigo_serie,
    i.modelo,
    p.nome AS parque,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media_7dias,
    COUNT(DISTINCT a.id) AS alertas_nao_resolvidos
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
LEFT JOIN medicoes_telemetria m ON i.id = m.inversor_id 
    AND m.data_medicao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
LEFT JOIN alertas a ON i.id = a.inversor_id AND a.resolvido = 0
WHERE i.status = 'operacional'
GROUP BY i.id, i.codigo_serie, i.modelo, p.nome
HAVING eficiencia_media_7dias < 85 OR alertas_nao_resolvidos > 0
ORDER BY eficiencia_media_7dias ASC, alertas_nao_resolvidos DESC;

-- Histórico de temperatura por inversor (últimos 30 dias)
SELECT 
    i.codigo_serie,
    p.nome AS parque,
    m.data_medicao,
    ROUND(AVG(m.temperatura), 1) AS temperatura_media,
    ROUND(MAX(m.temperatura), 1) AS temperatura_maxima,
    COUNT(m.id) AS num_medicoes
FROM inversores i
INNER JOIN parques p ON i.parque_id = p.id
INNER JOIN medicoes_telemetria m ON i.id = m.inversor_id
WHERE m.data_medicao >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    AND m.temperatura IS NOT NULL
GROUP BY i.id, i.codigo_serie, p.nome, m.data_medicao
HAVING temperatura_maxima > 70
ORDER BY temperatura_maxima DESC, m.data_medicao DESC;

-- ============================================================================
-- 9. CONSULTAS DE CAPACIDADE E POTENCIAL
-- ============================================================================

-- Capacidade instalada vs capacidade utilizada
SELECT 
    p.nome AS parque,
    p.capacidade_total_kw AS capacidade_instalada_kw,
    ROUND(SUM(pl.potencia_wp) / 1000.0, 2) AS capacidade_placas_kw,
    ROUND(SUM(i.capacidade_kw), 2) AS capacidade_inversores_kw,
    ROUND(GREATEST(SUM(pl.potencia_wp) / 1000.0, SUM(i.capacidade_kw)), 2) AS capacidade_real_kw
FROM parques p
LEFT JOIN inversores i ON p.id = i.parque_id AND i.status = 'operacional'
LEFT JOIN placas_solares pl ON i.id = pl.inversor_id AND pl.status = 'ligada'
GROUP BY p.id, p.nome, p.capacidade_total_kw
ORDER BY capacidade_real_kw DESC;

-- Potencial de geração não aproveitado (placas desligadas)
SELECT 
    p.nome AS parque,
    COUNT(pl.id) AS placas_desligadas,
    ROUND(SUM(pl.potencia_wp) / 1000.0, 2) AS potencia_perdida_kw
FROM parques p
INNER JOIN inversores i ON p.id = i.parque_id
INNER JOIN placas_solares pl ON i.id = pl.inversor_id
WHERE pl.status = 'desligada'
GROUP BY p.id, p.nome
ORDER BY potencia_perdida_kw DESC;

-- ============================================================================
-- 10. CONSULTAS DE RELATÓRIOS
-- ============================================================================

-- Relatório completo de um parque específico
SELECT 
    p.nome AS parque,
    p.localizacao,
    p.capacidade_total_kw,
    p.status AS status_parque,
    COUNT(DISTINCT i.id) AS num_inversores,
    COUNT(DISTINCT pl.id) AS num_placas,
    SUM(m.geracao_kw) AS geracao_total_hoje_kw,
    ROUND(AVG(m.eficiencia), 2) AS eficiencia_media_hoje,
    COUNT(DISTINCT CASE WHEN a.resolvido = 0 THEN a.id END) AS alertas_ativos
FROM parques p
LEFT JOIN inversores i ON p.id = i.parque_id
LEFT JOIN placas_solares pl ON i.id = pl.inversor_id
LEFT JOIN medicoes_telemetria m ON i.id = m.inversor_id AND m.data_medicao = CURDATE()
LEFT JOIN alertas a ON i.id = a.inversor_id
WHERE p.id = 1  -- Substitua pelo ID do parque desejado
GROUP BY p.id, p.nome, p.localizacao, p.capacidade_total_kw, p.status;

-- Resumo executivo do sistema
SELECT 
    (SELECT COUNT(*) FROM parques) AS total_parques,
    (SELECT COUNT(*) FROM inversores) AS total_inversores,
    (SELECT COUNT(*) FROM placas_solares) AS total_placas,
    (SELECT COUNT(*) FROM alertas WHERE resolvido = 0) AS alertas_ativos,
    (SELECT SUM(geracao_kw) FROM medicoes_telemetria WHERE data_medicao = CURDATE()) AS geracao_hoje_kw,
    (SELECT ROUND(AVG(eficiencia), 2) FROM medicoes_telemetria WHERE data_medicao = CURDATE() AND eficiencia IS NOT NULL) AS eficiencia_media_hoje;

-- ============================================================================
-- FIM DAS QUERIES
-- ============================================================================

