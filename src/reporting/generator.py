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

def criarFigura1(profile_df, posts_df) -> io.BytesIO:
    """Cria um gráfico de barras de engajamento e o retorna como um buffer de memória.""" 
    
    def plotarFigura(df_profiles_posts_int):
    
        def plotarBarraSeguidores():
            
            # Calcular Estatísticas
            top_10_followers = df_profiles_posts_int.groupby('username')['followersCount'].sum().sort_values(ascending=True).tail(10).reset_index()
            
            # Preparar cores e rótulos para o primeiro gráfico
            cores1 = ['#1f77b4'] * 10 # Cor padrão para as barras

            # Plota o gráfico de barras
            barras1 = ax1.barh(top_10_followers['username'], top_10_followers['followersCount'], color=cores1)
            ax1.bar_label(barras1, fmt='%d', padding=5)
            ax1.set_title(f'Por Seguidores')
            ax1.set_xlabel('Seguidores')

        def plotarBarraPercEngajamento():

            # Calcular Estatísticas
            top_10_followers = df_profiles_posts_int.groupby('username')[r'% ENGAJAMENTO'].max().sort_values(ascending=True).tail(10).reset_index()

            # Preparar cores e rótulos para o segundo gráfico
            cores2 = ['#1f77b4'] * len(top_10_followers) # Cor padrão para as barras

            # Plota o gráfico de barras
            barras2 = ax2.barh(top_10_followers['username'], top_10_followers[r'% ENGAJAMENTO'], color=cores2)
            ax2.bar_label(barras2, fmt='%.2f', padding=5)
            ax2.set_title(f'Por %-Engajamento')
            ax2.set_xlabel('%-Engajamento')
        
        def plotarBarraQtdEngajamento():

            # Calcular Estatísticas
            top_10_followers = df_profiles_posts_int.groupby('username')['TOTAL ENGAJAMENTO'].max().sort_values(ascending=True).tail(10).reset_index()
            
            # --- 5. Configuração do Segundo Gráfico (Inferior) ---
            # Preparar cores e rótulos para o segundo gráfico
            cores2 = ['#1f77b4'] * len(top_10_followers) # Cor padrão para as barras

            # Plota o gráfico de barras
            barras3 = ax3.barh(top_10_followers['username'], top_10_followers['TOTAL ENGAJAMENTO'], color=cores2)
            ax3.bar_label(barras3, fmt='%d', padding=5)
            ax3.set_title(f'Por Qtd de Engajamentos')
            ax3.set_xlabel('Qtd Engajamento')
        
        # --- 3. Criação da Figura e dos Gráficos (Subplots) ---
        # Cria a figura com 2 linhas e 1 coluna de gráficos
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle('Análise de Melhores Perfis', fontsize=16)
        
        plotarBarraSeguidores()
        plotarBarraPercEngajamento()
        plotarBarraQtdEngajamento()

        # --- 6. Finalização e Exibição/Salvamento da Figura ---
        plt.tight_layout(rect=[0, 0, 1, 0.96]) # Ajusta o layout para evitar sobreposição

        # Para salvar a figura em um arquivo
        plt.savefig(buffer, format='png', dpi=300)

        # Para exibir a figura diretamente (se estiver em um ambiente interativo como Jupyter)
        plt.show()
     
    def tratarDados():
    
        # Tratar Dados
        posts_df['data_hora'] = pd.to_datetime(posts_df['timestamp'])

        posts_df_gruped = posts_df.groupby(['ownerId', 'ownerUsername']).agg(
        commentsSum=('commentsCount', 'sum'),
        likesSum=('likesCount', 'sum'),
        minData=('data_hora', 'min'),
        maxData=('data_hora', 'max'),
        count=('ownerId', 'count')
        ).reset_index()

        df_profiles_posts_int = pd.merge(profile_df, posts_df_gruped, left_on='id', right_on='ownerId', how='left').drop(['ownerId'], axis=1)
        df_profiles_posts_int['TOTAL ENGAJAMENTO'] = (df_profiles_posts_int['commentsSum'] + df_profiles_posts_int['likesSum'])
        df_profiles_posts_int[r'% ENGAJAMENTO'] =  df_profiles_posts_int['TOTAL ENGAJAMENTO'] / df_profiles_posts_int['followersCount']
        df_profiles_posts_int['RECENCIA'] = 1 / ((df_profiles_posts_int['maxData'].max() - df_profiles_posts_int['maxData']).dt.days + 1)
        df_profiles_posts_int['FREQUENCIA'] = df_profiles_posts_int['count'] / ((df_profiles_posts_int['maxData'] - df_profiles_posts_int['minData']).dt.days + 1)
        
        return df_profiles_posts_int
    
    buffer = io.BytesIO() 
    df_profiles_posts_int = tratarDados()
    plotarFigura(df_profiles_posts_int)
    buffer.seek(0) 
    
    return buffer 

# --- Função Principal de Geração de Relatório ---
def generate_full_report(client_name, profile_df, posts_df, content_analysis, output_path, template_path):
    """Gera o relatório completo em .docx."""
    document = Document(template_path) 

    # Titulo
    document.add_heading(f"Análise de Concorrentes do Instagram para {client_name}", level=0) 
    
    # Seção 1: Painel de KPIs
    document.add_heading("Análise de Perfil dos Concorrentes", level=1)
    document.add_paragraph(f"Nesta seção será realizada uma análise comparativa entre os concorrentes do {client_name}. "
                           "Além de ser analisadas, métricas de performance, frequência e recência dos perfis, também serão analisados,"
                           "qualitativamente, seus respectivos conteúdos, bem como o tom de voz, tópicos frequentes e posicionamento de marca.")
  
    # Adiciona gráfico de engajamento 
    chart_buffer = criarFigura1(profile_df, posts_df)
    document.add_picture(chart_buffer, width=Inches(6.5)) 
    document.add_page_break()
    
    """ 
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
    
    """
    
    # Salva o documento
    document.save(output_path) 