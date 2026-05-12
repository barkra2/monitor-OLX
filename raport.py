import plotly.express as px
import reportlab, pandas as pd

def generuj_xlsx(nazwa_tabeli:str, csv):
    df = pd.DataFrame(csv)

    df.to_excel(f"data/{nazwa_tabeli}.xlsx", index=False)

    return "Udalo sie"
    # with pd.ExcelWriter(f"data/{nazwa_tabeli}.xlsx", engine="openpyxl") as writer:
    #     df.to_excel(writer, sheet_name="Produkty", index=False)

    #     stats = df.groupby("category")["cena"].agg([])