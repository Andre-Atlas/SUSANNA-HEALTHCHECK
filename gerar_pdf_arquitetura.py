from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Projeto Susana (SUS-DF) - Visão Arquitetural', border=False, ln=1, align='C')
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def create_pdf(output_path):
    pdf = PDF()
    pdf.add_page()
    
    # Body
    pdf.set_font('helvetica', '', 12)
    
    content = """
    Visão Geral
    O Projeto Susana é uma assistente virtual administrativa construída para a Secretaria de Saúde do Distrito Federal (SES-DF). O objetivo primário é fornecer informações sobre os serviços do SUS (horários, marcações, documentação para a Farmácia de Alto Custo, locais de vacinação) sem infringir normativas médicas.
    
    Soberania de Dados e Privacidade (LGPD)
    Para garantir controle total sobre os dados sensíveis e compliance absoluto com a LGPD, a arquitetura foi desenhada de forma 100% "on-premise". Nenhuma API externa (como OpenAI ou Google Gemini) é utilizada. Tudo roda nos servidores locais da Secretaria.
    
    Arquitetura de Inteligência Artificial
    - Modelo Base (LLM): Llama 3.1 8B, executado localmente através da engine Ollama, oferecendo alto desempenho na geração de texto em português brasileiro.
    - Retrieval-Augmented Generation (RAG): O sistema consulta um banco vetorial local (ChromaDB) indexado através do modelo de embedding "all-MiniLM-L6-v2" via sentence-transformers, garantindo que as respostas sejam exclusivamente fundamentadas em documentos oficiais raspados do portal saude.df.gov.br.
    
    Segurança Clínica (ML Guardrails)
    A assistente é rigorosamente proibida de fazer triagem médica ou sugerir medicamentos. Para isso, foi desenvolvido um classificador híbrido:
    - Um modelo Machine Learning (Logistic Regression + TF-IDF, em scikit-learn) intercepta intenções clínicas com probabilidade > 65%.
    - Sistema Fallback de Regex "Fail-Closed" garante bloqueio se o modelo falhar.
    
    Práticas de Engenharia MLOps
    Os modelos e experimentos são rastreados através do ecossistema MLflow, com datasets controlados no DVC. A arquitetura de software Backend adota o padrão Hexagonal (Ports & Adapters) desenvolvido no FastAPI.
    """
    
    pdf.multi_cell(0, 8, content.strip())
    pdf.output(output_path)
    print(f"PDF gerado com sucesso em {output_path}")

if __name__ == '__main__':
    create_pdf('Projeto_Susana_Visao_Geral.pdf')
