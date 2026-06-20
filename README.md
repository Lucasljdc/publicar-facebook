# Publicador de Veículos para o Facebook Marketplace

Este projeto automatiza o processo de preenchimento e upload de anúncios de veículos no Facebook Marketplace utilizando Python e a biblioteca Playwright. Ele se conecta à sua sessão ativa do Google Chrome para que você não precise digitar suas credenciais de login ou passar por etapas de CAPTCHA/Verificação de Duas Etapas.

---

## Requisitos Prévios

1. **Google Chrome** instalado no sistema.
2. **Python 3.10+** instalado (já detectado e configurado).
3. **Instância do Chrome com Porta de Depuração Ativada (`9222`)**:
   Para que o script controle o seu navegador, você precisa abrir o Chrome no modo de depuração. 

### Como abrir o Chrome na porta 9222 (Windows):

1. **Feche completamente** todas as janelas abertas do Google Chrome.
2. Abra o Menu Iniciar, digite `Executar` (ou pressione `Win + R`).
3. Digite o seguinte comando e dê Enter:
   ```cmd
   chrome.exe --remote-debugging-port=9222
   ```
   *Nota: Se o comando `chrome.exe` não for encontrado, você pode usar o caminho completo:*
   ```cmd
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```
4. Navegue até o [Facebook](https://www.facebook.com) no Chrome que acabou de abrir e verifique se você está logado na sua conta normal.

---

## Como Utilizar

Você pode usar esta automação diretamente conversando em linguagem natural no chat do **Antigravity**. 

Basta digitar uma mensagem como:
> "Publique o veículo: Ford Fiesta 2015, cor prata, 80.000km, mecânico, flex, preço 32.000, descrição: excelente estado de conservação, único dono. Fotos na pasta C:\fotos\fiesta"

O Antigravity fará o seguinte:
1. Extrairá todos os dados do veículo e o caminho da pasta de fotos.
2. Gerará um arquivo JSON de dados temporário.
3. Executará o script de automação no terminal.
4. O script abrirá uma nova aba no seu Chrome ativo, fará o upload das fotos e preencherá todas as informações.
5. Ele irá parar antes de clicar em "Publicar", permitindo que você revise o anúncio no navegador.
6. Após revisar e publicar manualmente no Facebook, você pode pressionar `ENTER` no console para encerrar o script (a aba do anúncio se fechará e as suas outras abas continuarão intactas).

---

## Configurações Padrão (`config.json`)

Você pode abrir o arquivo `config.json` e definir valores padrão que serão aplicados se você não os especificar na sua mensagem:
* `condicao`: Condição padrão do veículo (ex: `"Excelente"`, `"Muito bom"`, `"Bom"`, `"Razoável"`)
* `transmissao`: Câmbio padrão (ex: `"Manual"`, `"Automático"`)
* `combustivel`: Combustível padrão (ex: `"Flex/Gasolina"`, `"Gasolina"`, `"Diesel"`, `"Álcool"`, `"Híbrido"`, `"Elétrico"`)
* `localizacao_padrao`: Sua cidade/localização (ex: `"São Paulo, São Paulo"`)
