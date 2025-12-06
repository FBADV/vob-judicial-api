import pandas as pd
import os

def generate_mapping():
    columns = [
        "Órgão", "Consulta Pública", "Consulta com Login", 
        "Consulta com A1", "API Oficial", "Tipo de Extração", "Observações"
    ]
    
    data = []
    
    # 1. TJs (27)
    tjs = [
        "TJAC", "TJAL", "TJAP", "TJAM", "TJBA", "TJCE", "TJDF", "TJES", "TJGO", 
        "TJMA", "TJMT", "TJMS", "TJMG", "TJPA", "TJPB", "TJPR", "TJPE", "TJPI", 
        "TJRJ", "TJRN", "TJRS", "TJRO", "TJRR", "TJSC", "TJSP", "TJSE", "TJTO"
    ]
    for tj in tjs:
        # Default assumptions for TJs
        row = [tj, "Sim", "Sim", "Sim", "DataJud", "Crawler", ""]
        data.append(row)

    # 2. TRFs (6)
    trfs = ["TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6"]
    for trf in trfs:
        row = [trf, "Sim", "Sim", "Sim", "DataJud", "Crawler", ""]
        data.append(row)

    # 3. Superiores
    superiores = ["STJ", "STF", "TST", "TSE", "STM"] # Added TST/TSE/STM for completeness if relevant, but user said STJ+STF
    # User strictly said: STJ + STF + TCU
    user_superiores = ["STJ", "STF"]
    for sup in user_superiores:
         data.append([sup, "Sim", "Sim", "Sim", "Sim", "Crawler/API", ""])

    # 4. TCU
    data.append(["TCU", "Sim", "Sim", "Sim", "Sim", "Crawler", ""])

    # 5. TCEs (27 States + DF - usually TCE-UF)
    ufs = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
        "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
        "SP", "SE", "TO"
    ]
    for uf in ufs:
        name = f"TCE-{uf}"
        data.append([name, "Sim", "Sim", "Sim", "Não", "Crawler", ""])

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # Save
    output_path = os.path.join(os.getcwd(), "judicial-api", "process_mapping.xlsx")
    # Ensure dir exists (it should)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_excel(output_path, index=False)
    print(f"Arquivo gerado em: {output_path}")

if __name__ == "__main__":
    generate_mapping()
