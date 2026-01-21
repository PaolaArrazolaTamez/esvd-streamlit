# ESVD – Plataforma de análisis de valores económicos de servicios ecosistémicos

## Descripción general
Esta aplicación web permite el análisis, resumen y visualización de valores económicos de servicios ecosistémicos a partir de la **Ecosystem Services Valuation Database (ESVD)**.  
La plataforma está diseñada para facilitar la exploración de la información mediante **filtros jerárquicos en cascada** y para ofrecer resultados estadísticos y espaciales con criterios metodológicos transparentes.

La aplicación está desarrollada en **Python** utilizando **Streamlit**, y está pensada para apoyar análisis técnicos, estudios ambientales, evaluaciones económicas y procesos de toma de decisión.

---

## Fuente de datos
La aplicación utiliza como insumo principal un archivo CSV derivado de la **Ecosystem Services Valuation Database (ESVD)**, que compila estudios de valoración económica de servicios ecosistémicos a nivel global.

Los valores económicos se expresan en:
- **USD por hectárea por año (USD2022/ha/año)**

Columnas clave utilizadas:
- `study_id`: identificador único del estudio
- `esvd2_0_biome`: bioma
- `esvd2_0_ecozones`: ecozona
- `esvd2_0_ecosystems`: ecosistema
- `es_1`: servicio ecosistémico
- `int_per_hectare_per_year`: valor económico
- `latitude`, `longitude`: localización espacial del estudio
- `valuation_methods`: método de valoración económica
- `countries`: país del estudio

---

## Estructura de la aplicación
La aplicación se organiza en dos pestañas principales:

### 1. Tabla de resultados
Presenta un resumen estadístico de los valores económicos por **servicio ecosistémico**, condicionado por filtros en cascada:

**Bioma → Ecozona → Ecosistema**

Para cada servicio ecosistémico se reportan:
- Número de estudios únicos (`study_id`)
- Número total de observaciones
- Promedio simple
- Mediana
- Valor mínimo
- Valor máximo

Se incluye además una fila **TOTAL**, que resume el subconjunto filtrado.

### 2. Mapa de estudios
Muestra la localización espacial de los estudios mediante un mapa interactivo, donde:
- Cada punto representa un **estudio único**
- El tamaño del punto se relaciona con el valor económico
- El *tooltip* despliega:
  - País
  - Ecosistema
  - Método de valoración
  - Servicios ecosistémicos y valores asociados

---

## Metodología de filtrado
La aplicación utiliza un **sistema de filtros en cascada estrictos**:

1. **Bioma** (obligatorio)
2. **Ecozona** (opcional, dependiente del bioma)
3. **Ecosistema** (opcional, dependiente del bioma y la ecozona)

Cada nivel restringe las opciones disponibles en los filtros subsecuentes, garantizando coherencia ecológica y evitando combinaciones inválidas.

---

## Metodología de cálculo de promedios

### Unidad de análisis
- Los cálculos estadísticos se realizan sobre **todas las observaciones disponibles** para cada servicio ecosistémico dentro del subconjunto filtrado.

### Promedios y estadísticas
- **Promedio, mediana, mínimo y máximo** se calculan utilizando todas las filas (`observaciones`) del servicio ecosistémico.
- Esto implica que estudios con múltiples observaciones para un mismo servicio contribuyen con todas ellas al cálculo estadístico.

### Conteo de estudios
- El número de investigaciones se calcula como el **conteo de identificadores únicos de estudio (`study_id`)**, evitando duplicar estudios que reportan múltiples observaciones.

### Fila TOTAL
- La fila TOTAL no representa un promedio global único.
- El valor reportado en `promedio_simple` corresponde a la **suma de los promedios por servicio ecosistémico**, como una aproximación del valor promedio agregado del ecosistema bajo el enfoque de servicios ecosistémicos.

---

## Tecnologías utilizadas
- Python 3
- Streamlit
- Pandas
- NumPy
- PyDeck

---

## Uso de la aplicación
1. Seleccionar un **bioma**
2. (Opcional) Seleccionar una **ecozona**
3. (Opcional) Seleccionar un **ecosistema**
4. Explorar los resultados en la tabla y el mapa
5. Descargar las tablas generadas en formato CSV

---

## Alcances y consideraciones
- Los resultados dependen de la disponibilidad y distribución de estudios en la base ESVD.
- Los valores económicos deben interpretarse como **referencias comparables**, no como estimaciones puntuales para un sitio específico.
- La plataforma está orientada a análisis exploratorios, comparativos y de apoyo técnico.

---

## Autoría
Desarrollado como herramienta de análisis técnico para la exploración y síntesis de valores económicos de servicios ecosistémicos a partir de la ESVD.
Fuentes: Brander, L.M. de Groot, R, Guisado Goñi, V., van 't Hoff, V., Schägner, P., Solomonides, S., McVittie, A., Eppink, F., Sposato, M., Do, L., Ghermandi, A., and Sinclair, M. (2025). Ecosystem Services Valuation Database (ESVD). Foundation for Sustainable Development and Brander Environmental Economics.
