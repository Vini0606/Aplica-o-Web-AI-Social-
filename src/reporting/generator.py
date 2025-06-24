# src/reporting/generator.py

import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# --- Funções Auxiliares de Estilização ---
def set_cell_shading(cell, hex_color: str):
    """Define a cor de fundo de uma célula da tabela.""" 
    try:
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), hex_color)
        cell._tc.get_or_add_tcPr().append(shading_elm) 
    except Exception as e:
        print(f"Não foi possível aplicar a cor de fundo à célula: {e}") 

def set_header_style(table):
    """Aplica cor de fundo cinza e negrito ao cabeçalho da tabela.""" 
    header_cells = table.rows[0].cells
    for cell in header_cells:
        set_cell_shading(cell, 'D9D9D9') # Cinza claro
        
        # Para aplicar negrito
        p = cell.paragraphs[0]
        run = p.runs[0] if p.runs else p.add_run()
        run.text = cell.text
        run.bold = True
        p.alignment = 1 # WD_ALIGN_PARAGRAPH.CENTER

# --- Funções de Geração de Gráficos ---
def create_engagement_chart(df: pd.DataFrame) -> io.BytesIO:
    """Cria um gráfico de barras de engajamento e o retorna como um buffer de memória.""" 
    buffer = io.BytesIO() 
    plt.figure(figsize=(10, 6)) 
    sns.set_style("whitegrid") 
    bar_plot = sns.barplot(x='Perfil', y='Taxa de Engajamento Média (%)', data=df, palette='viridis') 
    plt.title('Comparativo de Taxa de Engajamento Média', fontsize=16) 
    plt.ylabel('Taxa de Engajamento (%)', fontsize=12) 
    plt.xlabel('Perfil', fontsize=12) 
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout() 
    plt.savefig(buffer, format='png', dpi=300) 
    plt.close() 
    buffer.seek(0) 
    return buffer 

# --- Função Principal de Geração de Relatório ---
def generate_full_report(client_name, kpi_df, content_analysis, output_path, template_path):
    """Gera o relatório completo em .docx."""
    document = Document(template_path) 

    # Titulo
    document.add_heading(f"Análise de Concorrentes do Instagram para {client_name}", level=0) 
    
    # Seção 1: Painel de KPIs
    document.add_heading("Análise de Perfil dos Concorrentes", level=1)
    document.add_paragraph(f"Nesta seção será realizada uma análise comparativa entre os concorrentes do {client_name}. "
                           "Além de ser analisadas, métricas de performance, frequência e recência dos perfis, também serão analisados,"
                           "qualitativamente, seus respoectivos conteúdos, bem como o tom de voz, tópicos frequentes e posicionamento de marca.")
    
    # Adiciona gráfico de engajamento
    document.add_paragraph("\nVisualização da Taxa de Engajamento:", style='Intense Quote') 
    chart_buffer = create_engagement_chart(kpi_df) 
    document.add_picture(chart_buffer, width=Inches(6.5)) 
    document.add_page_break() 
    
    # Seção 2: Análise Individual de Concorrentes
    document.add_heading("Análise Detalhada por Perfil", level=1)

    for username, analysis in content_analysis.items():
        if not analysis: 
            continue

        document.add_heading(f"Análise de: {username}", level=2)

        # Resumo da Estratégia
        p_resumo = document.add_paragraph()
        p_resumo.add_run("Resumo da Estratégia:").bold = True
        if analysis.summary:
            document.add_paragraph(analysis.summary)

        # Tom de Voz
        p_tom = document.add_paragraph()
        p_tom.add_run("Tom de Voz:").bold = True
        if analysis.tone_of_voice:
            document.add_paragraph(analysis.tone_of_voice)

        # Pilares de Conteúdo
        p_pilares = document.add_paragraph()
        p_pilares.add_run("Principais Pilares de Conteúdo:").bold = True
        if analysis.content_pillars:
            for pillar in analysis.content_pillars:
                # Adiciona um marcador de lista manualmente para simplicidade
                document.add_paragraph(f"• {pillar}")
        
        document.add_paragraph("\n") # Adiciona um espaço antes do próximo concorrente
    
    # Salva o documento
    document.save(output_path) 