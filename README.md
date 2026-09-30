# Clasificación ABC-XYZ de inventario

Análisis que clasifica los productos de un comercio minorista según **cuánto aportan a los ingresos (ABC)** y **qué tan estable es su demanda (XYZ)**, para definir una política de inventario distinta para cada grupo.

**Stack:** Python · pandas · matplotlib · seaborn · Jupyter · GitHub Codespaces

## Problema de negocio
No todos los productos merecen la misma atención. Tratar igual un producto que genera gran parte de las ventas y uno que casi no se vende lleva a **roturas de stock en lo importante** y **capital inmovilizado en lo que no rota**. La matriz ABC-XYZ ayuda a Compras y Logística a priorizar.

## Datos
[Online Retail II – UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii): ~1 millón de transacciones de un comercio online del Reino Unido (dic. 2009 – dic. 2011). Licencia CC BY 4.0.

El notebook descarga los datos automáticamente la primera vez (no se guardan en el repositorio).

## Metodología
1. **Limpieza:** se eliminan las cancelaciones, las cantidades y precios no válidos, los duplicados y los códigos que no son productos (portes, ajustes, comisiones).
2. **ABC (valor):** A = SKUs que generan el primer 80 % de los ingresos, B = el siguiente 15 %, C = el 5 % restante.
3. **XYZ (variabilidad):** coeficiente de variación (CV) de la demanda semanal. X ≤ 0,5 (estable), Y 0,5–1 (variable), Z > 1 (errática).
4. **Matriz ABC-XYZ** y **política de inventario** recomendada para cada una de las 9 clases.

## Resultados
> Pendiente: se completa al ejecutar el notebook (curva de Pareto, matriz ABC-XYZ y resumen por clase en `reports/figures/`).

## Políticas por clase

| | X (estable) | Y (variable) | Z (errática) |
|---|---|---|---|
| **A** | Reposición automática, stock de seguridad bajo | Pronóstico con estacionalidad | Seguimiento cercano con Compras |
| **B** | Reposición periódica automática | Revisión periódica con pronóstico | Evaluar compra bajo pedido |
| **C** | Pedidos grandes y poco frecuentes | Revisión periódica simple | Candidato a descatalogar |

## Cómo ejecutarlo

**En GitHub Codespaces (recomendado):** pulsa **Code → Codespaces → Create codespace on main**. Las dependencias se instalan solas. Luego abre `notebooks/abc_xyz_analysis.ipynb` y ejecuta todas las celdas.

**En local:**
```bash
pip install -r requirements.txt
jupyter notebook notebooks/abc_xyz_analysis.ipynb
```

## Estructura
```
├── .devcontainer/            # Configuración de Codespaces
├── notebooks/
│   └── abc_xyz_analysis.ipynb
├── src/
│   ├── download_data.py      # Descarga del dataset
│   └── abc_xyz.py            # Limpieza y clasificación ABC-XYZ
└── requirements.txt
```

---
**María Gabriela Figuera** · [LinkedIn](https://www.linkedin.com/in/mar%C3%ADa-gabriela-figuera-m-843830a5/)
