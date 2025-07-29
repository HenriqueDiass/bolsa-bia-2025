# check_paths.py
import os

print("--- INICIANDO DIAGNÓSTICO DE CAMINHOS ---")

# 1. Mostra onde o terminal está executando o script (Diretório de Trabalho Atual)
cwd = os.getcwd()
print(f"\n[1] Diretório de Trabalho Atual:\n    {cwd}\n")

# 2. Mostra o caminho absoluto da pasta do projeto (onde o script está)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"[2] Diretório onde o script está:\n    {script_dir}\n")

# 3. Constrói o caminho completo e exato que o programa está procurando
target_file_path = os.path.join(script_dir, 'shared', 'south_america.geojson')
print(f"[3] O programa está procurando pelo arquivo EXATAMENTE em:\n    {target_file_path}\n")

# 4. Verifica se o arquivo realmente existe nesse caminho
file_exists = os.path.exists(target_file_path)
print(f"[4] Esse arquivo foi encontrado? -> {file_exists}\n")

# 5. Lista TUDO que existe dentro da pasta 'shared' para vermos os nomes reais
shared_dir_path = os.path.join(script_dir, 'shared')
print(f"[5] Verificando o conteúdo da pasta '{shared_dir_path}'...")

if os.path.exists(shared_dir_path):
    files_in_shared = os.listdir(shared_dir_path)
    if files_in_shared:
        print("    Arquivos encontrados dentro da pasta 'shared':")
        for f in files_in_shared:
            print(f"    - '{f}'")
    else:
        print("    A pasta 'shared' está VAZIA.")
else:
    print("    ERRO: A pasta 'shared' nem sequer foi encontrada!")

print("\n--- FIM DO DIAGNÓSTICO ---")