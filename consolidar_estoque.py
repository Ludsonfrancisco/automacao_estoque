import pandas as pd
from pathlib import Path
import os

def extrair_codigo_tecnico(df_params):
    """Busca o código do armazém na aba Parametros."""
    for _, row in df_params.iterrows():
        for col_idx, cell_value in enumerate(row):
            val_str = str(cell_value).lower()
            if 'armaz' in val_str:
                if col_idx + 1 < len(row):
                    valor = str(row.iloc[col_idx + 1]).strip()
                    if valor and valor.lower() != 'nan':
                        return valor.upper()
    return "NAO_IDENTIFICADO"

def consolidar_e_renomear():
    diretorio = Path('estoque_tecnico')
    arquivo_saida = Path('estoque_dmais.xlsx')
    
    if not diretorio.exists():
        print(f"Erro: A pasta '{diretorio}' não existe.")
        return

    lista_dataframes = []
    mapeamento_codigos = {} # {COD: [lista_de_arquivos_originais]}
    operacoes_renomear = [] # [(path_antigo, path_novo)]

    print(f"--- Iniciando Processamento ---\n")

    # Primeiro passo: Coletar dados e mapear novos nomes
    for arquivo in list(diretorio.glob('*.xlsx')):
        if arquivo.name == arquivo_saida.name: continue
        
        try:
            with pd.ExcelFile(arquivo, engine='openpyxl') as xls:
                if 'Parametros' not in xls.sheet_names or 'Dados' not in xls.sheet_names:
                    print(f"Aviso: Arquivo {arquivo.name} ignorado (abas ausentes).")
                    continue
                
                # Extração do Código
                df_params = pd.read_excel(xls, sheet_name='Parametros', header=None)
                cod = extrair_codigo_tecnico(df_params)
                
                # Registro para Log de Duplicatas
                if cod not in mapeamento_codigos:
                    mapeamento_codigos[cod] = []
                mapeamento_codigos[cod].append(arquivo.name)
                
                # Leitura dos Dados para o consolidado
                df_dados = pd.read_excel(xls, sheet_name='Dados', header=1)
                if not df_dados.empty:
                    df_dados['Cod.'] = cod
                    lista_dataframes.append(df_dados)
                
                # Prepara lista de renomeação
                if cod != "NAO_IDENTIFICADO":
                    novo_nome = diretorio / f"{cod}.xlsx"
                    operacoes_renomear.append((arquivo, novo_nome, cod))

        except Exception as e:
            print(f"Erro ao ler {arquivo.name}: {e}")

    # 1. EXIBIR LOG DE DUPLICATAS
    print("--- LOG DE VERIFICAÇÃO DE DUPLICATAS ---")
    duplicados = {k: v for k, v in mapeamento_codigos.items() if len(v) > 1 and k != "NAO_IDENTIFICADO"}
    if duplicados:
        print("ALERTA: Códigos de armazém duplicados encontrados!")
        for cod, arquivos in duplicados.items():
            print(f"  - Código [{cod}]: Presente nos arquivos {arquivos}")
    else:
        print("Nenhuma duplicata de código encontrada.")

    # 2. SALVAR ARQUIVO CONSOLIDADO
    if lista_dataframes:
        df_final = pd.concat(lista_dataframes, ignore_index=True)
        try:
            df_final.to_excel(arquivo_saida, index=False)
            print(f"\nArquivo consolidado '{arquivo_saida}' gerado com sucesso.")
        except Exception as e:
            print(f"\nErro ao salvar consolidado: {e}")
    
    # 3. RENOMEAR ARQUIVOS FISICAMENTE
    print("\n--- RENOMEANDO ARQUIVOS ---")
    for antigo, novo, cod in operacoes_renomear:
        if antigo == novo:
            print(f"  Mantido: {antigo.name} (já está com o nome correto)")
            continue
            
        try:
            # Se houver duplicata, não sobrescrevemos para evitar perda de dados
            if len(mapeamento_codigos[cod]) > 1:
                print(f"  IGNORADO: {antigo.name} possui código duplicado ({cod}). Não renomeado para evitar conflito.")
            else:
                if novo.exists():
                    os.remove(novo) # Remove se for um resquício de execução anterior
                antigo.rename(novo)
                print(f"  Sucesso: {antigo.name} -> {novo.name}")
        except Exception as e:
            print(f"  Erro ao renomear {antigo.name}: {e}")

if __name__ == "__main__":
    consolidar_e_renomear()
