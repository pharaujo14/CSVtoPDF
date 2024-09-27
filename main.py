import streamlit as st
import pandas as pd
from fpdf import FPDF

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

    def add_responsible(self, reviewer_name):
        # Formatação do nome do revisor ajustada
        self.set_font("Arial", "B", 12)
        self.cell(55, 10, "Responsável pela Revisão: ", 0, 0)
        self.set_font("Arial", "", 12)
        self.cell(0, 10, reviewer_name, 0, 1)
        self.ln(10)

def generate_pdf(dataframe, logo_path, output_filename):
    pdf = PDF(logo_path)
    pdf.add_page()

    # Adiciona o nome do responsável pela revisão
    reviewer_name = dataframe['Reviewer Names'].iloc[0]
    pdf.add_responsible(reviewer_name)

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
st.title("Conversor de CSV para PDF")
st.write("Faça upload do CSV para converter para PDF.")

# Upload do CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file:
    # Carrega o CSV em um DataFrame
    df = pd.read_csv(uploaded_file)

    # Gera o nome do arquivo PDF baseado no nome do arquivo CSV
    csv_filename = uploaded_file.name
    pdf_filename = csv_filename.rsplit('.', 1)[0] + ".pdf"

    # Gera o PDF usando o logo presente na raiz do projeto
    logo_path = "logo.png"  # Caminho para o logo fixo na raiz do projeto
    pdf_file = generate_pdf(df, logo_path, pdf_filename)

    # Exibe o botão para download do PDF com o nome correspondente
    with open(pdf_file, "rb") as pdf:
        st.download_button(
            label="Baixar PDF",
            data=pdf,
            file_name=pdf_filename,
            mime="application/pdf"
        )
