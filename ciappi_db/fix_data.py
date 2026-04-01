import pandas as pd
import os

input_dir = "/Users/raulfranca/projetos/ciappi/ciappi_db/arq/csv"
output_dir = "/Users/raulfranca/projetos/ciappi/ciappi_db/arq/csv_fix"

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.endswith(".csv"):
        path = os.path.join(input_dir, file)
        print(f"Processando {file}...")

        df = pd.read_csv(path, dtype=str)

        for col in df.columns:
            try:
                df[col] = df[col].replace(r"^0000-00-00.*", "", regex=True)

                converted = pd.to_datetime(
                    df[col],
                    format="%m/%d/%y %H:%M:%S",
                    errors="coerce"
                )

                if converted.notna().any():
                    df[col] = converted.dt.strftime("%Y-%m-%d %H:%M:%S")
                    df[col] = df[col].where(converted.notna(), pd.NA)  # ← pd.NA em vez de ""
            except Exception:
                pass

        # Garante que strings vazias e "nan" viram NaN real
        df = df.replace("", pd.NA)
        df = df.replace("nan", pd.NA)

        out_path = os.path.join(output_dir, file)
        df.to_csv(out_path, index=False, na_rep="\\N")
        print(f"Salvo em: {out_path}")

print("✅ Conversão concluída")