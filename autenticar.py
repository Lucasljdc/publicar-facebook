import os
import subprocess
import sys

def main():
    # Caminho padrão do Chrome no Windows
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
    # Define o diretório do perfil local na pasta do próprio projeto
    profile_dir = os.path.abspath("chrome-profile")
    
    print("=======================================================")
    print(f"Abrindo o Google Chrome...")
    print(f"Pasta do perfil da sessão: {profile_dir}")
    print("-------------------------------------------------------")
    print("INSTRUÇÕES:")
    print("1. Faça login na sua conta do Facebook na janela do navegador.")
    print("2. Certifique-se de salvar/lembrar o dispositivo se o Facebook perguntar.")
    print("3. Após estar logado no Feed, FECHE a janela do navegador.")
    print("=======================================================")
    
    try:
        # Abre o Chrome de forma interativa apontando para a pasta local
        subprocess.run([chrome_path, f"--user-data-dir={profile_dir}", "https://www.facebook.com"])
        print("\nSessão de login salva com sucesso no diretório 'chrome-profile'!")
    except Exception as e:
        print(f"\nErro ao iniciar o Chrome: {e}")
        print("Certifique-se de que o Google Chrome está instalado no caminho padrão.")

if __name__ == "__main__":
    main()
