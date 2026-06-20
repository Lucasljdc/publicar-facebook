import os
import json
import subprocess
import time
import sys

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

# List of vehicles to publish
vehicles = [
    {
        "ano": 2012,
        "marca": "Yamaha",
        "modelo": "XJ6 F",
        "preco": 34900,
        "quilometragem": 40000,
        "cor": "Preto",
        "transmissao": "Manual",
        "descricao": "🏍️ YAMAHA XJ6 F 2012 🏍️\n\nUma das motos de 4 cilindros mais amadas e desejadas do Brasil! Excelente ronco, ótima ciclística e excelente estado de conservação. Pronta para rodar!\n\n✨ Destaques do Veículo:\n• Ano: 2012\n• Quilometragem: 40.000 km rodados\n• Excelente estado de conservação\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Honda CB 600F Hornet, Kawasaki Z750, Suzuki Bandit 650, Yamaha MT-07, Honda CB 650F, Kawasaki ER-6n, Suzuki Gladius",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\yamaha Xj6",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Motocicleta"
    },
    {
        "ano": 1999,
        "marca": "Fiat",
        "modelo": "Palio 1.0",
        "preco": 35900,
        "quilometragem": 40000,
        "cor": "Prata",
        "transmissao": "Manual",
        "descricao": "🚗 FIAT PALIO 1.0 1999 🚗\n\nUma verdadeira raridade para colecionadores e entusiastas! Veículo impecável, com baixíssima quilometragem original e ar-condicionado gelando. Totalmente original, em estado de conservação raríssimo, parece que acabou de sair da fábrica da Fiat.\n\n✨ Destaques do Veículo:\n• Ano: 1999\n• Quilometragem: Apenas 40.000 km originais\n• Ar-condicionado gelando perfeitamente\n• Vidros elétricos\n• Todo original e impecável\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Volkswagen Gol, Chevrolet Corsa, Ford Fiesta, Renault Clio, Chevrolet Celta, Fiat Uno, Peugeot 206",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\palio sub melo",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2012,
        "marca": "Fiat",
        "modelo": "Palio 1.0",
        "preco": 29500,
        "quilometragem": 167000,
        "cor": "Preto",
        "transmissao": "Manual",
        "descricao": "🚗 FIAT PALIO 1.0 2012 🚗\n\nHatch prático, econômico e de manutenção barata! Excelente custo-benefício para o dia a dia, com ar-condicionado e vidros elétricos.\n\n✨ Destaques do Veículo:\n• Ano: 2012\n• Quilometragem: 167.000 km rodados\n• Ar-condicionado gelando\n• Vidros elétricos\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Volkswagen Gol, Chevrolet Celta, Ford Fiesta, Renault Clio, Chevrolet Onix, Hyundai HB20, Fiat Uno, Peugeot 207",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\palio preto 2012",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2010,
        "marca": "Fiat",
        "modelo": "Palio 1.0",
        "preco": 27200,
        "quilometragem": 199000,
        "cor": "Preto",
        "transmissao": "Manual",
        "descricao": "🚗 FIAT PALIO 1.0 COMPLETO 2010 🚗\n\nCarro completo, ideal para quem precisa de economia e conforto na rotina. Motor confiável e excelente custo-benefício.\n\n✨ Destaques do Veículo:\n• Ano: 2010\n• Quilometragem: 199.000 km rodados\n• Modelo Completo\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Volkswagen Gol, Chevrolet Celta, Ford Fiesta, Renault Clio, Chevrolet Corsa, Fiat Uno, Peugeot 207",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\palio preto 2010",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 1997,
        "marca": "Fiat",
        "modelo": "Palio 1.6 16V",
        "preco": 21800,
        "quilometragem": 199000,
        "cor": "Branco",
        "transmissao": "Manual",
        "descricao": "🚗 FIAT PALIO 1.6 16V ESPORTIVO 1997 🚗\n\nUma verdadeira raridade esportiva! Versão Hatch com motor 1.6 16V completa de época. Saíram pouquíssimas unidades com esta motorização especial. Perfeito para colecionadores, entusiastas e muito bom de andar!\n\n✨ Destaques do Veículo:\n• Ano: 1997\n• Quilometragem: 199.000 km rodados\n• Motor: 1.6 16V (esportivo e rápido)\n• Modelo Completo\n• Raridade de se encontrar (poucas unidades fabricadas)\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Volkswagen Gol GTI, Chevrolet Corsa GSI, Fiat Uno Turbo, Ford Escort, Peugeot 206, Chevrolet Astra, Fiat Tempra",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\palio branco castro",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2018,
        "marca": "Kia",
        "modelo": "Soul",
        "preco": 76800,
        "quilometragem": 99000,
        "cor": "Azul",
        "transmissao": "Automático",
        "descricao": "🚗 KIA SOUL AUTOMÁTICO 2018 🚗\n\nUm carro que une design exclusivo, muito conforto e tecnologia! Versão completa com bancos de couro, câmbio automático e excelente espaço interno. Muito bonito, chama a atenção por onde passa. E o melhor: preço abaixo da tabela Fipe!\n\n✨ Destaques do Veículo:\n• Ano: 2018\n• Quilometragem: 99.000 km rodados\n• Câmbio: Automático\n• Bancos de couro\n• Modelo Completo\n• Preço abaixo da tabela Fipe\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Hyundai Tucson, Ford EcoSport, Chevrolet Tracker, Nissan Kicks, Jeep Renegade, Honda HR-V, Suzuki Vitara, Peugeot 2008, Renault Duster",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\kia soul",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 1997,
        "marca": "Volkswagen",
        "modelo": "Kombi Motorhome",
        "preco": 58999,
        "quilometragem": 199000,
        "cor": "Verde",
        "transmissao": "Manual",
        "descricao": "🚐 VOLKSWAGEN KOMBI MOTORHOME 1997 🚐\n\nUma Kombi incrível montada como Motorhome! Pronta para viajar e curtir os seus finais de semana com total liberdade e conforto. Estrutura completa e muito bem cuidada.\n\n✨ Destaques do Veículo:\n• Ano: 1997\n• Quilometragem: 199.000 km rodados\n• Cama confortável\n• Pia funcional\n• Armários planejados\n• Geladeira e fogão inclusos\n• Toldo lateral para acampamento\n• Mala e estrutura interna completa\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Motorhome, Kombi Home, Camper, Renault Master, Mercedes Sprinter, Fiat Ducato, Chevrolet Caravan, Ford Transit",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\04\\kombi home",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Minivan"
    },
    {
        "ano": 2018,
        "marca": "Honda",
        "modelo": "WR-V 1.5",
        "preco": 76899,
        "quilometragem": 99000,
        "cor": "Prata",
        "transmissao": "Automático",
        "descricao": "🚗 HONDA WR-V 1.5 AUTOMÁTICO 2018 🚗\n\nExcelente utilitário compacto que combina robustez, espaço interno inteligente com o sistema ULTRAGear e a consagrada confiabilidade da mecânica Honda! Carro completo e muito bem cuidado, pronto para o uso diário ou viagens.\n\n✨ Destaques do Veículo:\n• Ano: 2018\n• Câmbio: Automático\n• Quilometragem: 99.000 km rodados\n• Excelente espaço interno e modularidade dos bancos\n• Mecânica confiável de baixo custo de manutenção\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Honda Fit, Honda HR-V, Chevrolet Tracker, Hyundai Creta, Nissan Kicks, Jeep Renegade, Ford EcoSport, Renault Duster",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\Wrv blum",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2000,
        "marca": "Ford",
        "modelo": "Fiesta 1.0",
        "preco": 21800,
        "quilometragem": 199000,
        "cor": "Azul",
        "transmissao": "Manual",
        "descricao": "🚗 FORD FIESTA 1.0 HATCH 2000 🚗\n\nUma verdadeira relíquia para entusiastas e quem busca economia extrema no dia a dia. Carro completo, com ar-condicionado gelando, e que passou por um processo de restauração minucioso. Está em estado impecável de conservação, parecendo recém-saído da linha de montagem!\n\n✨ Destaques do Veículo:\n• Ano: 2000\n• Quilometragem: 199.000 km rodados\n• Ar-condicionado gelando muito bem\n• Modelo completo\n• Restauração completa de alto nível\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Chevrolet Corsa, Fiat Uno, Volkswagen Gol, Chevrolet Celta, Renault Clio, Peugeot 206, Ford Ka",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\05\\fiesta azul antigo",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2017,
        "marca": "Suzuki",
        "modelo": "GSX-S 1000F",
        "preco": 47800,
        "quilometragem": 20000,
        "cor": "Azul",
        "transmissao": "Manual",
        "descricao": "🏍️ SUZUKI GSX-S 1000F 2017 🏍️\n\nSuper esportiva espetacular de alta cilindrada! Extremamente conservada, com apenas 20 mil km rodados e mais de 4 mil reais investidos em acessórios de qualidade. Moto que nunca sofreu quedas ou batidas, com procedência garantida.\n\n✨ Destaques do Veículo:\n• Ano: 2017\n• Quilometragem: Apenas 20.000 km rodados\n• Mais de R$ 4.000 em acessórios instalados\n• Histórico limpo (nunca caiu ou bateu)\n• Excelente procedência e cuidado\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Kawasaki Z1000, Honda CB 1000R, Yamaha MT-09, BMW S1000R, Ducati Monster, Triumph Speed Triple, Kawasaki Ninja 1000",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\06\\GSX 1000 willian cunhado loss",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Motocicleta"
    },
    {
        "ano": 2023,
        "marca": "Renault",
        "modelo": "Kwid Intense",
        "preco": 52300,
        "quilometragem": 44000,
        "cor": "Preto",
        "transmissao": "Manual",
        "descricao": "🚗 RENAULT KWID INTENSE 2023 🚗\n\nExcelente hatch compacto super econômico e moderno, ideal para uso diário na cidade! Veículo com apenas 44 mil km rodados, de uso particular (nunca foi utilizado para aplicativos/Uber) e com todo o histórico de manutenções em concessionária autorizada.\n\n✨ Destaques do Veículo:\n• Ano: 2023\n• Quilometragem: Apenas 44.000 km rodados\n• Uso estritamente particular (nunca foi Uber)\n• Revisões e manutenções carimbadas na concessionária Renault\n• Excelente economia de combustível\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Fiat Mobi, Chevrolet Onix, Hyundai HB20, Volkswagen Gol, Ford Ka, Fiat Uno, Renault Sandero",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\06\\Kwid loss",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Hatchback"
    },
    {
        "ano": 2014,
        "marca": "Mitsubishi",
        "modelo": "Lancer GT 2.0",
        "preco": 65900,
        "quilometragem": 135000,
        "cor": "Branco",
        "transmissao": "Automático",
        "descricao": "🚗 MITSUBISHI LANCER GT 2.0 AUTOMÁTICO 2014 🚗\n\nExcelente oportunidade de adquirir um sedan médio de visual esportivo e mecânica extremamente robusta! Equipado com motor 2.0, teto solar e câmbio automático. Carro muito bem conservado, ideal para quem busca estilo e confiabilidade.\n\n✨ Destaques do Veículo:\n• Ano: 2014\n• Câmbio: Automático\n• Quilometragem: 135.000 km rodados\n• Teto solar funcional\n• Excelente dirigibilidade e estabilidade\n\n💰 Condições Especiais:\n• Fazemos financiamento!\n• Parcelamos no cartão de crédito!\n• Aceitamos trocas!\n\n\nPesquisa: Honda Civic, Toyota Corolla, Chevrolet Cruze, Ford Focus Sedan, Volkswagen Jetta, Nissan Sentra, Hyundai Elantra, Kia Cerato",
        "fotos_dir": "H:\\Outros computadores\\Meu computador\\FLIGHT MOTORS\\CARROS\\2026\\06\\Lancer branco",
        "localizacao": "Canoas (cidade)",
        "tipo_veiculo": "Carro",
        "tipo_carroceria": "Sedã"
    }
]

def run_batch():
    temp_json = "veiculo_atual.json"
    python_exec = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exec):
        python_exec = "python"
        
    print(f"=== INICIANDO PUBLICAÇÃO EM LOTE DE {len(vehicles)} VEÍCULOS ===\n")
    
    for idx, vehicle in enumerate(vehicles, start=1):
        print(f"\n=======================================================")
        print(f"VEÍCULO {idx}/{len(vehicles)}: {vehicle['marca']} {vehicle['modelo']} ({vehicle['ano']})")
        print(f"=======================================================")
        
        # Write vehicle to JSON
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(vehicle, f, ensure_ascii=False, indent=2)
            
        print("Dados gravados em veiculo_atual.json. Iniciando publish.py...")
        
        # Execute publishing script
        start_time = time.time()
        try:
            # Using Popen to capture logs and display them in real time
            process = subprocess.Popen(
                [python_exec, "publish.py", temp_json, "--batch"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            
            # Read stdout line by line
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                # Print output line by line
                print(f"[{vehicle['modelo']}] {line.strip()}")
                
            process.wait()
            elapsed = time.time() - start_time
            
            if process.returncode == 0:
                print(f"Sucesso ao publicar {vehicle['marca']} {vehicle['modelo']}! Tempo: {elapsed:.1f}s")
            else:
                print(f"ERRO: publish.py retornou código {process.returncode} para {vehicle['marca']} {vehicle['modelo']}.")
                
        except Exception as e:
            print(f"Exceção ao executar o processo para {vehicle['marca']} {vehicle['modelo']}: {e}")
            
        print("Aguardando 10 segundos antes do próximo veículo...")
        time.sleep(10)
        
    print("\n=== TODOS OS ANÚNCIOS DO LOTE FORAM PROCESSADOS! ===")

if __name__ == "__main__":
    run_batch()
