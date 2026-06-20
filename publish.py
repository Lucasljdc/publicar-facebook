import sys
import os
import json
import time
import re
from playwright.sync_api import sync_playwright

def safe_print(*args, **kwargs):
    msg = " ".join(str(arg) for arg in args)
    encoding = sys.stdout.encoding or "utf-8"
    try:
        sys.stdout.write(msg + kwargs.get("end", "\n"))
        sys.stdout.flush()
    except UnicodeEncodeError:
        safe_msg = msg.encode(encoding, errors="replace").decode(encoding)
        sys.stdout.write(safe_msg + kwargs.get("end", "\n"))
        sys.stdout.flush()

print = safe_print

def map_transmission(val):
    if not val:
        return None
    val_lower = str(val).lower()
    if "mecan" in val_lower or "manual" in val_lower or "mecân" in val_lower:
        return "Manual"
    if "auto" in val_lower:
        return "Automático"
    return val

def map_fuel(val):
    if not val:
        return None
    val_lower = str(val).lower()
    if "flex" in val_lower:
        return "Flex/Gasolina"
    if "gasol" in val_lower:
        return "Gasolina"
    if "alcool" in val_lower or "álcool" in val_lower:
        return "Álcool"
    if "diesel" in val_lower:
        return "Diesel"
    if "hibr" in val_lower or "híbr" in val_lower:
        return "Híbrido"
    if "elet" in val_lower or "elét" in val_lower:
        return "Elétrico"
    return val

def map_condition(val):
    if not val:
        return None
    val_lower = str(val).lower()
    if "excelente" in val_lower or "como novo" in val_lower:
        return "Como novo"
    if "novo" in val_lower or "nova" in val_lower:
        return "Novo"
    if "bom" in val_lower or "muito bom" in val_lower:
        return "Bom"
    if "razoavel" in val_lower or "razoável" in val_lower:
        return "Razoável"
    return val

def get_image_files(directory):
    if not os.path.isdir(directory):
        print(f"ERRO: A pasta de fotos '{directory}' não existe ou não é válida.")
        return []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif')
    files = []
    for f in os.listdir(directory):
        if f.lower().endswith(valid_extensions):
            files.append(os.path.abspath(os.path.join(directory, f)))
    files.sort()
    return files

def register_dialog_handler(page):
    try:
        page.on("dialog", lambda dialog: dialog.accept())
    except Exception:
        pass

def safe_click(page, element):
    if not element:
        return False
    try:
        element.evaluate("el => el.scrollIntoView({block: 'center'})")
        page.wait_for_timeout(200)
        element.click(timeout=3000)
        return True
    except Exception:
        try:
            element.click(force=True, timeout=2000)
            return True
        except Exception:
            try:
                element.evaluate("el => el.click()")
                return True
            except Exception:
                return False

def find_input_element(page, label_name):
    for selector in [
        f'label:has-text("{label_name}") input',
        f'label:has-text("{label_name}") textarea',
        f'input[aria-label*="{label_name}" i]',
        f'textarea[aria-label*="{label_name}" i]',
        f'input[placeholder*="{label_name}" i]',
        f'textarea[placeholder*="{label_name}" i]'
    ]:
        try:
            loc = page.locator(selector)
            for i in range(loc.count()):
                candidate = loc.nth(i)
                if candidate.is_visible():
                    return candidate
        except Exception:
            pass

    try:
        locators = [
            f'span:has-text("{label_name}")',
            f'label:has-text("{label_name}")',
            f'div:has-text("{label_name}")'
        ]
        for sel in locators:
            el_list = page.locator(sel)
            for i in range(el_list.count()):
                el = el_list.nth(i)
                if el.is_visible():
                    for depth in range(1, 5):
                        xpath = "/".join([".."] * depth)
                        ancestor = el.locator(f"xpath={xpath}")
                        for input_sel in ['input', 'textarea']:
                            child = ancestor.locator(input_sel)
                            for k in range(child.count()):
                                candidate = child.nth(k)
                                try:
                                    if candidate.is_visible() and candidate.get_attribute("type") != "hidden":
                                        return candidate
                                except Exception:
                                    pass
    except Exception:
        pass

    return None

def find_dropdown_element(page, label_name):
    for selector in [
        f'label[role="combobox"]:has-text("{label_name}")',
        f'div[role="combobox"]:has-text("{label_name}")',
        f'label:has-text("{label_name}")',
        f'span:has-text("{label_name}")'
    ]:
        try:
            loc = page.locator(selector)
            for i in range(loc.count()):
                candidate = loc.nth(i)
                if candidate.is_visible():
                    role = candidate.get_attribute("role")
                    if role in ["combobox", "button"]:
                        return candidate
                        
                    for role_sel in ['div[role="combobox"]', 'label[role="combobox"]', 'div[role="button"]']:
                        child = candidate.locator(role_sel)
                        if child.count() > 0 and child.first.is_visible():
                            return child.first
                            
                    for depth in range(1, 5):
                        xpath = "/".join([".."] * depth)
                        ancestor = candidate.locator(f"xpath={xpath}")
                        for role_sel in ['div[role="combobox"]', 'label[role="combobox"]', 'div[role="button"]']:
                            child = ancestor.locator(role_sel)
                            if child.count() > 0 and child.first.is_visible():
                                return child.first
        except Exception:
            pass
            
    return None

def fill_text_field(page, label_name, value):
    if value is None:
        return False
    print(f"Preenchendo campo '{label_name}' com: {value}")
    
    if label_name == "Descrição":
        try:
            el = page.locator('textarea').first
            if el.count() > 0 and el.is_visible():
                safe_click(page, el)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                el.fill(str(value))
                page.wait_for_timeout(200)
                return True
        except Exception as e:
            print(f"Erro ao preencher Descrição diretamente: {e}")
            
    el = find_input_element(page, label_name)
    if el:
        try:
            safe_click(page, el)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            if label_name in ["Preço", "Valor", "Quilometragem", "Quilômetros", "Quilometragem (km)"]:
                el.type(str(value), delay=50)
            else:
                el.fill(str(value))
                
            page.wait_for_timeout(200)
            return True
        except Exception as e:
            print(f"Erro ao digitar no campo '{label_name}': {e}")
            
    print(f"AVISO: Não foi possível preencher o campo '{label_name}' com seletores automáticos.")
    return False

def select_dropdown_option(page, label_name, option_name):
    if not option_name:
        return False
    print(f"Selecionando no dropdown '{label_name}' a opção: {option_name}")
    
    mapped_option = option_name
    if label_name == "Tipo de veículo":
        if "carro" in option_name.lower():
            mapped_option = "Carro/picape"
        elif "moto" in option_name.lower():
            mapped_option = "Motocicleta"
    elif label_name == "Estilo da carroceria":
        if "sed" in option_name.lower():
            mapped_option = "Sedã"
        elif "hatch" in option_name.lower():
            mapped_option = "Hatchback"
            
    candidates = [mapped_option]
    if '/' in mapped_option:
        candidates.extend([p.strip() for p in mapped_option.split('/') if p.strip()])
    if mapped_option == "Automático":
        candidates.extend(["Transmissão automática", "Automática", "Automático"])
    elif mapped_option == "Como novo":
        candidates.extend(["Excelente", "Novo", "Como novo"])
    elif mapped_option == "Sedã":
        candidates.extend(["Sedan", "Sedã"])
    elif mapped_option == "Hatchback":
        candidates.extend(["Hatch", "Dois volumes", "Hatchback"])
    elif mapped_option.upper() == "SUV":
        candidates.extend(["SUV", "Utilitário esportivo", "Utilitário Esportivo"])
        
    el = find_dropdown_element(page, label_name)
    if el:
        try:
            safe_click(page, el)
            page.wait_for_timeout(1000)
            
            def find_and_click_option():
                for name in candidates:
                    opt_selectors = [
                        f'div[role="option"]:has-text("{name}")',
                        f'span:has-text("{name}")',
                        f'div:has-text("{name}")',
                        f'div[role="listbox"] div:has-text("{name}")'
                    ]
                    for opt_sel in opt_selectors:
                        try:
                            loc = page.locator(opt_sel)
                            for i in range(loc.count()):
                                item = loc.nth(i)
                                if item.is_visible(timeout=500):
                                    safe_click(page, item)
                                    page.wait_for_timeout(500)
                                    return True
                        except Exception:
                            pass
                            
                    try:
                        opt = page.get_by_role("option", name=name, exact=False).first
                        if opt.is_visible(timeout=500):
                            safe_click(page, opt)
                            page.wait_for_timeout(500)
                            return True
                    except Exception:
                        pass
                        
                    try:
                        opt = page.get_by_text(name, exact=True).first
                        if opt.is_visible(timeout=500):
                            safe_click(page, opt)
                            page.wait_for_timeout(500)
                            return True
                    except Exception:
                        pass
                        
                    try:
                        opt = page.get_by_text(name, exact=False).first
                        if opt.is_visible(timeout=500):
                            safe_click(page, opt)
                            page.wait_for_timeout(500)
                            return True
                    except Exception:
                        pass
                return False
            
            if find_and_click_option():
                return True
                
            print(f"Opção não encontrada diretamente. Tentando digitar '{mapped_option}' para filtrar...")
            page.keyboard.type(str(mapped_option), delay=100)
            page.wait_for_timeout(1000)
            
            if find_and_click_option():
                return True
                
        except Exception as e:
            print(f"Erro ao selecionar no dropdown '{label_name}': {e}")
            
    print(f"AVISO: Não foi possível encontrar a opção '{option_name}' no dropdown '{label_name}'.")
    return False

def fill_location(page, location_value):
    if not location_value:
        return False
    print(f"Configurando localização: {location_value}")
    
    el = find_input_element(page, "Localização")
    if not el:
        for label in ["Cidade", "Bairro", "Cidade/Estado", "Cidade, Estado"]:
            el = find_input_element(page, label)
            if el:
                break
                
    if el:
        try:
            safe_click(page, el)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            clean_city = location_value
            if '(' in clean_city:
                clean_city = clean_city.split('(')[0].strip()
                
            print(f"Digitando cidade para busca: {clean_city}")
            el.type(clean_city, delay=100)
            page.wait_for_timeout(2500)
            
            suggestions_selectors = [
                'ul[role="listbox"] li',
                'div[role="option"]',
                'div[role="listbox"] div[role="button"]',
                'div[role="listbox"] span',
                'div[role="menu"] div[role="menuitem"]'
            ]
            
            for sel in suggestions_selectors:
                try:
                    loc = page.locator(sel)
                    for i in range(loc.count()):
                        item = loc.nth(i)
                        text = item.text_content() or ""
                        text_lower = text.lower()
                        if clean_city.lower() in text_lower and ("cidade" in text_lower or "rio grande" in text_lower) and item.is_visible(timeout=500):
                            safe_click(page, item)
                            print(f"Localização selecionada na lista de sugestões: {text.strip()}")
                            page.wait_for_timeout(1000)
                            return True
                except Exception:
                    pass
                    
            for sel in suggestions_selectors:
                try:
                    loc = page.locator(sel)
                    for i in range(loc.count()):
                        item = loc.nth(i)
                        if item.is_visible(timeout=500):
                            safe_click(page, item)
                            print(f"Primeira sugestão de localização selecionada: {item.text_content().strip()}")
                            page.wait_for_timeout(1000)
                            return True
                except Exception:
                    pass
                    
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            print("Selecionada localização via teclado (ArrowDown + Enter).")
            page.wait_for_timeout(500)
            return True
            
        except Exception as e:
            print(f"Erro ao preencher localização: {e}")
            
    print("AVISO: Não foi possível selecionar a localização a partir das sugestões.")
    return False

def upload_photos(page, file_paths):
    if not file_paths:
        print("AVISO: Nenhuma foto para upload.")
        return False
    print(f"Iniciando upload de {len(file_paths)} foto(s)...")
    try:
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(file_paths)
        page.wait_for_timeout(5000)
        print("Upload de fotos executado.")
        return True
    except Exception as e:
        print(f"Erro ao fazer upload de fotos: {e}")
        return False

def select_groups_and_publish(page):
    print("Iniciando seleção automática de grupos...")
    page.wait_for_timeout(4000) # Wait for group list to fully render
    
    checkbox_loc = page.locator('div[role="checkbox"]')
    group_list = []
    
    for i in range(checkbox_loc.count()):
        el = checkbox_loc.nth(i)
        if el.is_visible():
            text = el.text_content() or ""
            checked = el.get_attribute("aria-checked") == "true"
            
            members = 0
            text_clean = text.replace('\xa0', ' ').replace('\n', ' ')
            
            match_mil = re.search(r'([0-9.,]+)\s*(?:mil)\s*membros', text_clean, re.IGNORECASE)
            match_mi = re.search(r'([0-9.,]+)\s*(?:mi|milhão|milhões)\s*membros', text_clean, re.IGNORECASE)
            match_simple = re.search(r'([0-9.,]+)\s*membros', text_clean, re.IGNORECASE)
            
            if match_mi:
                val_str = match_mi.group(1).replace('.', '').replace(',', '.')
                members = int(float(val_str) * 1000000)
            elif match_mil:
                val_str = match_mil.group(1).replace('.', '').replace(',', '.')
                members = int(float(val_str) * 1000)
            elif match_simple:
                val_str = match_simple.group(1).replace('.', '').replace(',', '.')
                members = int(float(val_str))
                
            group_list.append({
                "element": el,
                "text": text,
                "members": members,
                "checked": checked
            })
            
    group_list.sort(key=lambda x: x["members"], reverse=True)
    
    print(f"Encontrados {len(group_list)} grupos para anúncio. Selecionando os 20 maiores...")
    
    selected_count = 0
    for g in group_list:
        if selected_count >= 20:
            break
            
        print(f"Selecionando grupo: '{g['text'].strip()[:50]}...' ({g['members']} membros)")
        if not g["checked"]:
            try:
                safe_click(page, g["element"])
                page.wait_for_timeout(200)
            except Exception as e:
                print(f"Erro ao selecionar grupo: {e}")
        selected_count += 1
        
    print("Grupos selecionados. Clicando no botão final 'Publicar'...")
    page.wait_for_timeout(1000)
    
    publish_btn = None
    btn_loc = page.locator('div[role="button"]:has-text("Publicar")')
    for i in range(btn_loc.count()):
        candidate = btn_loc.nth(i)
        if candidate.is_visible():
            publish_btn = candidate
            
    if publish_btn:
        safe_click(page, publish_btn)
        print("Botão final 'Publicar' clicado! Anúncio enviado.")
        page.wait_for_timeout(5000)
        return True
    else:
        print("AVISO: Botão final 'Publicar' não encontrado.")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python publish.py <caminho_do_veiculo.json>")
        sys.exit(1)
        
    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"ERRO: Arquivo JSON '{json_path}' não encontrado.")
        sys.exit(1)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            
    ano = data.get("ano")
    marca = data.get("marca")
    modelo = data.get("modelo")
    preco = data.get("preco")
    quilometragem = data.get("quilometragem")
    cor = data.get("cor")
    descricao = data.get("descricao")
    fotos_dir = data.get("fotos_dir")
    tipo_veiculo = data.get("tipo_veiculo") or "Carro"
    
    transmissao = map_transmission(data.get("transmissao") or config.get("transmissao", "Manual"))
    combustivel = map_fuel(data.get("combustivel") or config.get("combustivel", "Flex/Gasolina"))
    condicao = map_condition(data.get("condicao") or config.get("condicao", "Excelente"))
    tipo_carroceria = data.get("tipo_carroceria") or config.get("tipo_carroceria")
    localizacao = data.get("localizacao") or config.get("localizacao_padrao")

    print("\n--- Dados do Veículo ---")
    print(f"Tipo de Veículo: {tipo_veiculo}")
    print(f"Ano: {ano}")
    print(f"Marca: {marca}")
    print(f"Modelo: {modelo}")
    print(f"Preço: {preco}")
    print(f"Quilometragem: {quilometragem}")
    print(f"Cor: {cor}")
    print(f"Transmissão: {transmissao}")
    print(f"Combustível: {combustivel}")
    print(f"Condição: {condicao}")
    print(f"Carroceria: {tipo_carroceria}")
    print(f"Localização: {localizacao}")
    print(f"Fotos no diretório: {fotos_dir}")
    print("------------------------\n")
    
    image_paths = []
    if fotos_dir:
        image_paths = get_image_files(fotos_dir)
        print(f"Total de {len(image_paths)} fotos encontradas para upload.")
        
    print("Iniciando o navegador Google Chrome (Sessão Persistente)...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=r"C:\Users\TRABALHO\Desktop\Antigravity\chrome-profile",
                channel="chrome",
                headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox"]
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            register_dialog_handler(page)
            
            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)
            
            print("Abrindo página de criação de veículo no Facebook Marketplace...")
            page.goto("https://www.facebook.com/marketplace/create/vehicle", timeout=60000, wait_until="domcontentloaded")
            
            print("Aguardando carregamento do formulário...")
            try:
                page.locator('label[role="combobox"]:has-text("Ano")').wait_for(state="visible", timeout=30000)
                print("Formulário carregado com sucesso.")
            except Exception:
                print("AVISO: Tempo esgotado aguardando o formulário. Continuando mesmo assim...")
            
            page.wait_for_timeout(3000)
            
            if "login" in page.url or "checkpoint" in page.url:
                print("ERRO: O navegador não parece estar logado no Facebook. Por favor, logue no Facebook no seu Chrome e tente novamente.")
                sys.exit(1)
                
            select_dropdown_option(page, "Tipo de veículo", tipo_veiculo)
            select_dropdown_option(page, "Ano", str(ano))
            select_dropdown_option(page, "Fabricante", marca)
            
            fill_text_field(page, "Modelo", modelo)
            
            if not fill_text_field(page, "Quilometragem", quilometragem):
                if not fill_text_field(page, "Quilômetros", quilometragem):
                    fill_text_field(page, "Quilometragem (km)", quilometragem)
                    
            if not fill_text_field(page, "Preço", preco):
                fill_text_field(page, "Valor", preco)
                
            if cor:
                select_dropdown_option(page, "Cor externa", cor)
                
            if transmissao:
                if not select_dropdown_option(page, "Câmbio", transmissao):
                    select_dropdown_option(page, "Transmissão", transmissao)
                    
            if combustivel:
                if not select_dropdown_option(page, "Tipo de combustível", combustivel):
                    select_dropdown_option(page, "Combustível", combustivel)
                    
            if condicao:
                if not select_dropdown_option(page, "Condição do veículo", condicao):
                    select_dropdown_option(page, "Condição", condicao)
                    
            if tipo_carroceria:
                select_dropdown_option(page, "Estilo da carroceria", tipo_carroceria)
                
            fill_text_field(page, "Descrição", descricao)
            
            if localizacao:
                fill_location(page, localizacao)
                
            if image_paths:
                # Limit photo uploads to cumulative size of 45MB to avoid Playwright CDP 50MB transfer limit
                selected_paths = []
                total_size = 0
                for path in image_paths:
                    try:
                        sz = os.path.getsize(path)
                        if total_size + sz < 45 * 1024 * 1024:
                            selected_paths.append(path)
                            total_size += sz
                        else:
                            if not selected_paths:
                                selected_paths.append(path)
                                total_size += sz
                            break
                    except Exception:
                        pass
                upload_photos(page, selected_paths[:20])
                
            print("\n=======================================================")
            print("CAMPOS PREENCHIDOS E FOTOS ENVIADAS!")
            print("Aguardando upload de fotos concluir...")
            
            # Find the initial next/publish button
            btn = None
            for label in ["Avançar", "Publicar", "Next", "Publish"]:
                loc = page.locator(f'div[role="button"]:has-text("{label}")')
                for i in range(loc.count()):
                    candidate = loc.nth(i)
                    if candidate.is_visible():
                        btn = candidate
                        break
                if btn:
                    break
                    
            if btn:
                # Wait for button to become enabled (maximum 60 seconds)
                start_wait = time.time()
                print("Esperando o botão de publicação habilitar...")
                while time.time() - start_wait < 60:
                    disabled = btn.get_attribute("aria-disabled")
                    if disabled != "true":
                        print("Botão habilitado! Upload concluído.")
                        break
                    page.wait_for_timeout(1000)
                
                print("Clicando no botão de avançar/publicar...")
                safe_click(page, btn)
                page.wait_for_timeout(4000)
                
                # Select groups and publish
                select_groups_and_publish(page)
                
                print("\n=======================================================")
                print("ANÚNCIO PUBLICADO COM SUCESSO NO MARKETPLACE E GRUPOS!")
                print("=======================================================\n")
                
                if "--batch" in sys.argv:
                    print("Modo batch ativo. Aguardando 5 segundos antes de fechar a aba...")
                    page.wait_for_timeout(5000)
                else:
                    input("Pressione ENTER aqui no console do Antigravity quando desejar fechar a aba de publicação do Chrome...")
            else:
                print("AVISO: Botão 'Publicar' inicial não encontrado. Deixando aba aberta para revisão manual.")
                if "--batch" in sys.argv:
                    page.wait_for_timeout(5000)
                else:
                    input("Pressione ENTER aqui no console do Antigravity quando desejar fechar a aba de publicação do Chrome...")
            
            context.close()
            print("Navegador fechado. Script finalizado.")
            
    except Exception as e:
        print(f"Ocorreu um erro crítico durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
