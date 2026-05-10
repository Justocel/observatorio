-- sql/seeds/02_fuentes_bcra.sql
-- Fuentes adicionales del BCRA (Banco Central de la República Argentina).

INSERT INTO fuentes (nombre, categoria, descripcion, unidad, url_origen, frecuencia_min) VALUES
    ('dolar_mayorista',
     'dolar',
     'Tipo de cambio mayorista USD/ARS según BCRA (cotización oficial interbancaria, 1 vez por día hábil)',
     'ARS',
     'https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD',
     1440)
ON CONFLICT (nombre) DO NOTHING;
