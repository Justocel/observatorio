-- sql/seeds/01_fuentes.sql
-- Catálogo inicial de fuentes a scrapear.
-- Las fuentes pueden repetirse, pero no pueden tener el mismo nombre.
-- De cada fuente se extrae un solo dolar
-- La frecuencia de actualizacion es distinta para cada fuente, 
-- y se mide en minutos. El sistema se encarga de respetar esa frecuencia.
INSERT INTO fuentes (nombre, categoria, descripcion, unidad, url_origen, frecuencia_min) VALUES
    ('dolar_oficial', 'dolar', 'Dólar oficial BNA',     'ARS', 'https://api.bluelytics.com.ar/v2/latest', 60),
    ('dolar_blue',    'dolar', 'Dólar blue (informal)', 'ARS', 'https://api.bluelytics.com.ar/v2/latest', 15);
