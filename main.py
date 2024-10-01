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

# Função para obter o valor da célula, verificando em PT ou EN
def get_column_value(df, col_name_pt, col_name_en, row_index, default_value="Sem resposta"):
    """
    Verifica se a coluna existe no DataFrame, primeiro em português (PT) e, se não encontrar, busca em inglês (EN).
    Retorna o valor da célula como string ou um valor padrão.
    """
    if col_name_pt in df.columns:
        value = df[col_name_pt].iloc[row_index]
    elif col_name_en in df.columns:
        value = df[col_name_en].iloc[row_index]
    else:
        return default_value

    # Garante que o valor é uma string, tratando NaN e outros tipos
    if pd.isna(value):
        return default_value
    return str(value)

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

    # Obtém o nome do revisor da primeira linha do dataframe (PT ou EN)
    reviewer_name = get_column_value(dataframe, 'Nomes dos revisores', 'Reviewer Names', 0)

    # Adiciona o nome do responsável e a data de geração ao PDF
    pdf.add_responsible(reviewer_name, generation_date)

    # Itera sem ordenar para manter a ordem original do CSV
    current_section = None
    for index, row in dataframe.iterrows():
        # Seção (PT ou EN)
        section = get_column_value(dataframe, 'Seção', 'Section', index)
        if section != current_section:
            current_section = section
            pdf.chapter_title(section)

        # Formatação da pergunta e resposta
        pdf.question_format(
            get_column_value(dataframe, 'Número da pergunta', 'Question Number', index),
            get_column_value(dataframe, 'Pergunta', 'Question', index),
            get_column_value(dataframe, 'Opção (s) de resposta', 'Response Option(s)', index, "Sem resposta")
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

    # Gera o nome do arquivo PDF com o primeiro valor da coluna 'Response Option(s)' (PT ou EN)
    first_section_value = get_column_value(df, 'Opção (s) de resposta', 'Response Option(s)', 0, "output")
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
