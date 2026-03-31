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
                converted = pd.to_datetime(
                    df[col],
                    format="%m/%d/%y %H:%M:%S",
                    errors="coerce"
                )

                if converted.notna().any():
                    df[col] = converted.dt.strftime("%Y-%m-%d %H:%M:%S")
                    df[col] = df[col].where(converted.notna(), "")
            except Exception:
                pass

        out_path = os.path.join(output_dir, file)
        df.to_csv(out_path, index=False)
        print(f"Salvo em: {out_path}")

print("✅ Conversão concluída")