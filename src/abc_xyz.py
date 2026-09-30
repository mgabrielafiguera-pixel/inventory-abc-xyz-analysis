"""Funciones para la clasificación ABC-XYZ de inventario."""
import numpy as np
import pandas as pd

# Códigos que no son productos (portes, ajustes, comisiones, etc.)
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "C2", "D", "S", "B", "CRUK", "PADS", "BANK CHARGES",
    "AMAZONFEE", "ADJUST", "ADJUST2", "TEST001", "TEST002", "GIFT",
}


def load_raw(xlsx_path) -> pd.DataFrame:
    """Lee las dos hojas del Excel (2009-2010 y 2010-2011) y las une."""
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype={"StockCode": str, "Invoice": str})
    df = pd.concat(sheets.values(), ignore_index=True)
    return df.rename(columns={"Customer ID": "CustomerID"})


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia transacciones: quita cancelaciones, cantidades/precios no válidos y códigos que no son productos."""
    out = df.copy()
    out["Invoice"] = out["Invoice"].astype(str)
    out["StockCode"] = out["StockCode"].astype(str).str.strip().str.upper()
    out["InvoiceDate"] = pd.to_datetime(out["InvoiceDate"])

    mask = (
        ~out["Invoice"].str.startswith("C")          # cancelaciones
        & (out["Quantity"] > 0)
        & (out["Price"] > 0)
        & ~out["StockCode"].isin(NON_PRODUCT_CODES)
        & out["StockCode"].str.match(r"^\d")         # los productos empiezan con dígito
    )
    out = out.loc[mask].drop_duplicates()
    out["Revenue"] = out["Quantity"] * out["Price"]
    return out


def abc_classification(df: pd.DataFrame, a_cut: float = 0.80, b_cut: float = 0.95) -> pd.DataFrame:
    """Clasifica cada SKU en A/B/C según su contribución acumulada a los ingresos."""
    sku = (
        df.groupby("StockCode")
        .agg(Description=("Description", "first"),
             Revenue=("Revenue", "sum"),
             Units=("Quantity", "sum"),
             Orders=("Invoice", "nunique"))
        .sort_values("Revenue", ascending=False)
    )
    sku["RevenueShare"] = sku["Revenue"] / sku["Revenue"].sum()
    sku["CumShare"] = sku["RevenueShare"].cumsum()
    # Se usa el acumulado ANTERIOR para que el SKU que cruza el umbral quede en la clase superior
    prev = sku["CumShare"] - sku["RevenueShare"]
    sku["ABC"] = np.select([prev < a_cut, prev < b_cut], ["A", "B"], default="C")
    return sku


def xyz_classification(df: pd.DataFrame, freq: str = "W", x_cut: float = 0.5, y_cut: float = 1.0) -> pd.DataFrame:
    """Clasifica cada SKU en X/Y/Z según el coeficiente de variación (CV) de su demanda por periodo.

    Los periodos sin ventas cuentan como demanda 0, para no subestimar la variabilidad.
    """
    period = df["InvoiceDate"].dt.to_period(freq)
    demand = df.groupby(["StockCode", period])["Quantity"].sum().unstack(fill_value=0)
    all_periods = pd.period_range(period.min(), period.max(), freq=freq)
    demand = demand.reindex(columns=all_periods, fill_value=0)

    stats = pd.DataFrame({
        "MeanDemand": demand.mean(axis=1),
        "StdDemand": demand.std(axis=1, ddof=0),
    })
    stats["CV"] = stats["StdDemand"] / stats["MeanDemand"]
    stats["XYZ"] = np.select([stats["CV"] <= x_cut, stats["CV"] <= y_cut], ["X", "Y"], default="Z")
    return stats


def abc_xyz(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Combina ABC y XYZ en una sola tabla por SKU."""
    abc = abc_classification(df)
    xyz = xyz_classification(df, **kwargs)
    out = abc.join(xyz, how="left")
    out["Class"] = out["ABC"] + out["XYZ"]
    return out


POLICIES = {
    "AX": "Reposición automática, stock de seguridad bajo, revisión continua",
    "AY": "Pronóstico con estacionalidad, stock de seguridad medio",
    "AZ": "Seguimiento cercano con Compras; stock de seguridad alto o bajo pedido",
    "BX": "Reposición automática periódica",
    "BY": "Revisión periódica con pronóstico",
    "BZ": "Revisión periódica, evaluar comprar bajo pedido",
    "CX": "Pedidos grandes y poco frecuentes (minimizar coste de gestión)",
    "CY": "Revisión periódica simple",
    "CZ": "Candidato a descatalogar o vender solo bajo pedido",
}
