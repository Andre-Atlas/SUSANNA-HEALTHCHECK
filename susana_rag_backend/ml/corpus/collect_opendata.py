import requests
from bs4 import BeautifulSoup
from pathlib import Path

def get_mock_data():
    """Textos ESCRITOS À MÃO para testes. Não são dados oficiais."""
    return {
        "result": {
            "results": [
                {
                    "title": "Doenças Infecciosas e Transmissão (HIV/ISTs)",
                    "notes": "Informações validadas sobre transmissão de doenças. O HIV NÃO é transmitido por interações sociais cotidianas como abraços, beijos, suor, lágrimas ou compartilhamento de talheres. A transmissão ocorre por relações sexuais desprotegidas, compartilhamento de seringas ou de mãe para filho. Prevenção e testagem estão disponíveis nas UBS.",
                    "name": "hiv-transmissao-df"
                },
                {
                    "title": "Soros e Acidentes com Animais Peçonhentos/Silvestres",
                    "notes": "Em caso de acidentes com animais peçonhentos (cobras, escorpiões, aranhas) ou mordeduras de animais silvestres (risco de raiva), o paciente deve procurar imediatamente o HRAN (Hospital Regional da Asa Norte) ou HRT (Hospital Regional de Taguatinga), que são os polos de referência para aplicação de soro antiofídico, antiescorpiônico e antirrábico.",
                    "name": "soros-animais-peconhentos"
                },
                {
                    "title": "Procedimentos, Consultas e Exames (SISREG)",
                    "notes": "Procedimentos complexos, exames de sangue, radiografias e tomografias devem ser agendados através do sistema SISREG pelas Unidades Básicas de Saúde (UBS). O paciente recebe um comprovante com data e local do exame.",
                    "name": "procedimentos-exames-df"
                },
                {
                    "title": "Campanha e Estoque de Vacinas",
                    "notes": "As vacinas disponíveis nas UBS do DF neste mês incluem: BCG, Hepatite B, Poliomielite, Pentavalente, Rotavírus, Febre Amarela, Tríplice Viral e COVID-19. O estoque é reabastecido semanalmente pelo Ministério da Saúde.",
                    "name": "vacinas-disponiveis"
                },
                {
                    "title": "Unidades Básicas de Saúde do DF",
                    "notes": "Lista de UBS em funcionamento. A UBS 1 da Asa Sul fica na SGAS 612. A UBS 2 de Ceilândia fica na QNN 15. Atendimento de segunda a sexta, das 7h às 19h.",
                    "name": "ubs-df-lista"
                },
                {
                    "title": "Estoque de Medicamentos - Farmácia de Alto Custo",
                    "notes": "A Farmácia de Alto Custo (CEAF) possui disponibilidade de medicamentos especializados, insulina e imunossupressores. A retirada exige receita médica original e documento de identidade.",
                    "name": "estoque-farmacia-alto-custo"
                },
                {
                    "title": "Dados Epidemiológicos - Doenças e Dengue",
                    "notes": "Informações sobre sintomas e focos. Sintomas comuns da dengue incluem febre alta, dores musculares e manchas vermelhas. O fumacê está sendo aplicado semanalmente nas regiões com maior incidência.",
                    "name": "casos-dengue-df"
                }
            ]
        }
    }

def main() -> int:
    """
    Coleta descrições de datasets de saúde do portal CKAN dados.df.gov.br.

    Sem a flag --mock, falha (exit 1) se a API estiver indisponível: dados inventados
    NUNCA devem entrar em data/corpus/, porque tudo ali é exibido como "Fonte Oficial".
    Com --mock, grava os exemplos em data/mock/ (pasta não indexada), só para testes.
    """
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mock", action="store_true", help="gera dados de EXEMPLO em data/mock/ (não indexado)")
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    if args.mock:
        data = get_mock_data()
        output_file = data_dir / "mock" / "dados_abertos_EXEMPLO.txt"
    else:
        base_url = "https://dados.df.gov.br/api/3/action/package_search"
        try:
            response = requests.get(base_url, params={"q": "saude", "rows": 100}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"ERRO: API CKAN indisponível ({e}). Nada foi gravado no corpus.")
            print("Use --mock para gerar dados de exemplo fora do corpus.")
            return 1
        output_file = data_dir / "corpus" / "dados_abertos.txt"

    packages = data.get("result", {}).get("results", [])
    if not packages:
        print("ERRO: a API não retornou datasets. Nada foi gravado.")
        return 1

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for pkg in packages:
            title = pkg.get("title", "")
            notes = BeautifulSoup(pkg.get("notes", "") or "", "html.parser").get_text(separator="\n").strip()
            if not notes:
                continue
            f.write(f"[DADOS_ABERTOS] {title}\n{notes}\nFonte: https://dados.df.gov.br/dataset/{pkg.get('name', '')}\n\n")

    print(f"{len(packages)} datasets gravados em {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
