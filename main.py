import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
from login import login, is_authenticated
import re

# Verifica se o usuário está autenticado
if not is_authenticated():
    login()
    st.stop()

# Função para sanitizar o nome do arquivo, removendo caracteres inválidos
def sanitize_filename(filename):
    # Substitui caracteres inválidos para nomes de arquivos no Windows
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Função para gerar o PDF
class PDF(FPDF):
    def __init__(self, logo_path):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        # Adiciona o logo no header de todas as páginas
        self.image(self.logo_path, 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "", 0, 1, 'C')
        self.ln(20)

    def chapter_title(self, title):
        # Formatação do título da sessão
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"Sessão: {title}", 0, 1, 'C')
        self.ln(4)

    def question_format(self, number, question, response):
        # Formatação de pergunta e resposta com quebra de linha e espaçamento reduzido
        self.set_font("Arial", "B", 10)
        self.multi_cell(0, 6, f"{number} - {question}")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 6, response)
        self.ln(4)

    def add_responsible(self, reviewer_name, generation_date):
        # Adiciona a data de geração e o responsável pela revisão
        self.set_font("Arial", "B", 12)
        self.cell(55, 10, f"Data de Geração: ", 0, 0)
        self.set_font("Arial", "", 12)
        self.cell(0, 10, generation_date, 0, 1)
        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(55, 10, "Responsável pela Revisão: ", 0, 0)
        self.set_font("Arial", "", 12)
        self.cell(0, 10, reviewer_name, 0, 1)
        self.ln(10)

def generate_pdf(dataframe, logo_path, output_filename):
    pdf = PDF(logo_path)
    pdf.add_page()

    # Subtrai 3 horas da data e hora atuais
    generation_date = (datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y - %H:%M")

    # Obtém o nome do revisor da primeira linha do dataframe
    reviewer_name = dataframe['Reviewer Names'].iloc[0]

    # Adiciona o nome do responsável e a data de geração ao PDF
    pdf.add_responsible(reviewer_name, generation_date)

    # Itera sem ordenar para manter a ordem original do CSV
    current_section = None
    for index, row in dataframe.iterrows():
        section = row['Section']
        if section != current_section:
            current_section = section
            pdf.chapter_title(section)

        pdf.question_format(
            row['Question Number'],
            row['Question'],
            row['Response Option(s)'] if pd.notna(row['Response Option(s)']) else "Sem resposta"
        )

    # Salva o PDF gerado com o nome especificado
    pdf.output(output_filename)
    return output_filename

# Interface do Streamlit
# Configurações da página com o logo
st.set_page_config(page_title="Century Data", page_icon="Century_mini_logo-32x32.png")

# Adiciona o logo ao topo da página
st.image("logo_site.png", use_column_width=True)

st.title("Gerador de PDF do PIA em Preenchimento")
st.write("Faça upload do CSV para converter para PDF.")

# Upload do CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file:
    # Carrega o CSV em um DataFrame
    df = pd.read_csv(uploaded_file)

    # Gera o nome do arquivo PDF com o primeiro valor da coluna Section
    first_section_value = df['Response Option(s)'].iloc[0] if not df['Response Option(s)'].empty else "output"
    sanitized_filename = sanitize_filename(first_section_value)
    pdf_filename = f"{sanitized_filename}.pdf"

    # Gera o PDF usando o logo presente na raiz do projeto
    logo_path = "logo.png"  # Caminho para o logo fixo na raiz do projeto
    pdf_file = generate_pdf(df, logo_path, pdf_filename)

    # Exibe o botão para download do PDF com o nome correspondente
    download_button = st.download_button(
        label="Baixar PDF",
        data=open(pdf_file, "rb").read(),
        file_name=pdf_filename,
        mime="application/pdf"
    )

    # Mostra os balões após o clique no botão de download
    if download_button:
        st.balloons()