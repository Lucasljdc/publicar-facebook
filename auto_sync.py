import subprocess
import time
import os
from datetime import datetime

# Intervalo entre verificações (em segundos). Padrão: 5 minutos (300 segundos).
INTERVALO_SEGUNDOS = 300

def sincronizar():
    try:
        # Executa 'git status --porcelain' para verificar se há mudanças nos arquivos monitorados
        resultado = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        alteracoes = resultado.stdout.strip()
        
        if alteracoes:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{agora}] Alterações detectadas! Iniciando sincronização...")
            
            # Adiciona todas as alterações
            subprocess.run(["git", "add", "."], check=True)
            
            # Cria o commit com a data/hora atual
            subprocess.run(["git", "commit", "-m", f"Auto sync: {agora}"], check=True)
            
            # Faz o push para o repositório remoto
            subprocess.run(["git", "push"], check=True)
            
            print(f"[{agora}] Sincronizado com sucesso no GitHub!\n")
        else:
            # Sem mudanças pendentes
            pass
            
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando do Git: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    print("==============================================================")
    print("SERVIÇO DE SINCRONIZAÇÃO AUTOMÁTICA DO GITHUB INICIADO")
    print(f"O script verificará alterações a cada {INTERVALO_SEGUNDOS} segundos.")
    print("Pressione Ctrl+C para encerrar o serviço.")
    print("==============================================================\n")
    
    try:
        while True:
            sincronizar()
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\nServiço encerrado pelo usuário.")
