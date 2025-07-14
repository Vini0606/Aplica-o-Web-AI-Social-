from docx import Document
from datetime import datetime
import os
import json
from docx import Document
from docx.text.paragraph import Paragraph
from datetime import datetime
import os
from docx.oxml.shared import OxmlElement
from docx import Document
from docx.text.paragraph import Paragraph
from copy import deepcopy
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from datetime import date

def preencher_plano_marketing(
    brief_data,          
    caminho_saida,           
    nome_empresa,            
    responsavel,             
    objetivos,               
    persona,                 
    pilares_conteudo,
    posicionamento,
    calendario=[]                                                     
):

    doc = Document()

    titulo_principal = doc.add_heading("Plano de Marketing de Conteúdo para Instagram", level=1)
    titulo_principal.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in titulo_principal.runs:
        run.font.size = Pt(24)
        run.bold = True

    doc.add_paragraph(f"Empresa: {nome_empresa}")
    doc.add_paragraph(f"Data: {date.today().strftime("%A, %d de %B de %Y")}")
    doc.add_paragraph(f"Responsável: Equipe AI Social")

    
    # Conteúdo extra dinâmico ao final
    doc.add_heading("📌 Objetivos de Marketing", level=2)
    for objetivo in objetivos:
        doc.add_paragraph(f"• {objetivo}")

    doc.add_heading("🎯 Público-alvo", level=2)
    for chave, valor in persona.items():
        if type(valor) is not list:
            doc.add_paragraph(f"{chave}: {valor}")
        else:
            doc.add_paragraph(f"{chave}: {', '.join(valor)}")

    doc.add_heading("🎙️ Posicionamento e Tom de Voz", level=2)
    doc.add_paragraph(posicionamento['resumo_posicionamento']) # Adiciona o texto diretamente
    
    doc.add_heading("📚 Pilares de Conteúdo", level=2)
    for pilar in pilares_conteudo:
        doc.add_heading(f"{pilar['nome']}", level=3)
        doc.add_paragraph(f"{pilar['objetivo']} Exemplos de conteúdo:")
        for exemplo in pilar.get('exemplos', []):
            doc.add_paragraph(f"• {exemplo}")
    
    doc.add_heading("◼️ Formatos:", level=2)
    doc.add_paragraph(f"""• Reels (Prioridade Alta): Tutoriais e dicas, Bastidores, Desafios e trends, Reações, """  
                      """Conteúdo educacional, Moda e tendências, 'Antes e depois', Comentários e agradecimentos, Conteúdo informativo e de entretenimento. """)
    doc.add_paragraph(f"""• Carrossel (Prioridade Média): Tutoriais e dicas, Listas, Comparativos, """ 
                      """Storytelling, Depoimentos, Catálogos de produtos, Imagens contínuas, """ 
                      """Vídeos, Jogos e desafios, Conteúdo educativo, Posts de identificação, Anúncios. """)
    doc.add_paragraph(f"""• Imagem Estática (Prioridade Média): Fotos, Ilustrações, Infográficos, """
                      """Ícones e Símbolos, Imagens para redes sociais, e-books e materiais digitais. """)
    doc.add_paragraph(f"""• Stories (Prioridade Alta): Enquetes, Perguntas e Respostas, Desafios e trends, """ 
                      """Mostre os bastidores, Dicas e tutoriais, Guia de produtos, Promoções, """ 
                      """Lançamentos, Vídeos curtos, Carrosséis, Uso de adesivos e GIFs, Reposts de clientes """)
    doc.add_paragraph(f"""• Lives (Prioridade Baixa): Debates, Entrevistas, Tutoriais e "Como fazer", """
                      """Bastidores, Gameplays, Eventos ao vivo, Conteúdo interativo, """ 
                      """Conteúdo temático, Sessões de perguntas e respostas, Apresentações e palestras. """)


    doc.add_heading("🗓️ Calendário Editorial Sugerido", level=2)
    doc.add_paragraph(
        "A seguir, uma sugestão de calendário semanal para distribuir os pilares de conteúdo. "
        "Este cronograma pode ser adaptado conforme a performance e o feedback do público."
    )
    if calendario:
        
        # Definir os cabeçalhos da tabela
        headers = ["Dia", "Pilar de Conteúdo", "Horário Sugerido"]
        
        # Adicionar a tabela com uma linha de cabeçalho
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid' # Aplica um estilo de grade à tabela
        
        # Preencher o cabeçalho
        hdr_cells = table.rows[0].cells
        for i, header in enumerate(headers):
            hdr_cells[i].text = header
            # Deixar o cabeçalho em negrito
            hdr_cells[i].paragraphs[0].runs[0].font.bold = True

        # Preencher as linhas com os dados do calendário
        for item in calendario:
            row_cells = table.add_row().cells
            row_cells[0].text = item.get('dia', 'N/A')
            row_cells[1].text = item.get('pilar', 'N/A')
            row_cells[2].text = item.get('periodo', 'N/A')

        # Ajustar a largura das colunas (opcional, mas melhora a aparência)
        # As larguras são apenas exemplos, ajuste conforme necessário
        widths = (Inches(1.2), Inches(1.5), Inches(1.5))
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = width
    else:
        doc.add_paragraph("Nenhuma sugestão de calendário foi gerada.")
    
    doc.add_heading("📈 Estratégia de Engajamento e Crescimento", level=2)
    doc.add_paragraph(f"""• Interação Proativa: Dedicar 30 minutos por dia para responder a todos os """  
                      """comentários e DMs, e interagir em posts de perfis da nossa persona e de parceiros. """)
    doc.add_paragraph(f"""• Uso Estratégico de Hashtags: Pesquisar e utilizar uma mistura de hashtags de nicho, """ 
                      """de volume médio e de baixa concorrência (5-15 por post). """)
    doc.add_paragraph(f"""• Call to Actions (CTAs) Claras: Em cada post, incentivar uma ação: "Salve este post",""" 
                     """ "Comente sua opinião", "Compartilhe com um amigo", "Clique no link da bio". """)
    doc.add_paragraph(f"""• Colaborações: Realizar collabs (posts em conjunto) e lives com outras """ 
                      """marcas ou influenciadores que tenham um público semelhante. """)
    doc.add_paragraph(f"""• Conteúdo Gerado pelo Usuário (UGC): Incentivar clientes a postarem """ 
                      """fotos com nossos produtos e repostar em nossos stories e feed, sempre dando os devidos créditos. """)
    
    doc.add_heading("📚 Métricas e Análise de Desempenho (KPIs)", level=2)
    doc.add_paragraph(f"""• Alcance e Impressões: Quantas pessoas estão vendo nosso conteúdo. """)
    doc.add_paragraph(f"""• Taxa de Engajamento: (Curtidas + Comentários + Salvamentos) / Alcance. """ 
                      """Acompanhar a evolução dessa taxa é mais importante do que o número bruto de curtidas. """)
    doc.add_paragraph(f"""• Cliques no Link da Bio: Medir o tráfego gerado para o site ou WhatsApp. """)
    doc.add_paragraph(f"""• Crescimento de Seguidores: Acompanhar o crescimento líquido (novos seguidores - deixaram de seguir). """)
    doc.add_paragraph(f"""• Visualizações e Retenção nos Reels: Analisar quais vídeos prendem mais a atenção. """)
    doc.add_paragraph(f"""• Conversões: (Leads ou Vendas) - Acompanhar através de cupons de desconto exclusivos para o Instagram ou parâmetros UTM nos links. """)
    

    # Criar pasta se não existir
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    # Salvar documento
    doc.save(caminho_saida)
    print(f"✅ Relatório gerado com sucesso: {caminho_saida}")

# =====================
# 🎯 EXEMPLO DE USO
# =====================
if __name__ == "__main__":
    
    preencher_plano_marketing(
        caminho_saida=r"reports\Relatorio_Marketing_Preenchido.docx",
        nome_empresa="Loja Criativa",
        responsavel="João da Silva",
        objetivos=[
            "Aumentar as vendas online em 15% nos próximos 6 meses",
            "Aumentar os seguidores em 20% no próximo trimestre",
            "Melhorar a taxa de engajamento em 10% ao mês"
        ],
        persona={
            "Nome": "Sofia, a Empreendedora Criativa",
            "Idade": "25-35 anos",
            "Gênero": "Feminino",
            "Localização": "Capitais do Brasil",
            "Ocupação": "Artesã e dona de pequeno negócio",
            "Interesses": "DIY, dicas de negócio, Reels e stories interativos",
            "Dores": "Falta de tempo, organização financeira"
        },
        pilares_conteudo=[
            {
                "nome": "Educacional",
                "objetivo": "Ensinar e informar",
                "exemplos": ["Tutoriais", "Dicas rápidas"]
            },
            {
                "nome": "Inspiração",
                "objetivo": "Conectar emocionalmente",
                "exemplos": ["Frases", "Histórias de sucesso"]
            },
            {
                "nome": "Entretenimento",
                "objetivo": "Engajar e entreter",
                "exemplos": ["Memes", "Desafios", "Enquetes"]
            },
            {
                "nome": "Vendas",
                "objetivo": "Converter e vender",
                "exemplos": ["Depoimentos", "Ofertas", "Lançamentos"]
            }
        ],
        calendario=[
            {"dia": "Segunda", "pilar": "Inspiração", "formato": "Imagem ou Carrossel", "horario": "09:00"},
            {"dia": "Terça", "pilar": "Educacional", "formato": "Reels", "horario": "12:00"},
            {"dia": "Quarta", "pilar": "Entretenimento", "formato": "Stories interativos", "horario": "Ao longo do dia"},
            {"dia": "Quinta", "pilar": "Educacional", "formato": "Reels ou Carrossel", "horario": "18:00"},
            {"dia": "Sexta", "pilar": "Vendas", "formato": "Reels ou Carrossel", "horario": "11:00"},
            {"dia": "Sábado", "pilar": "Bastidores", "formato": "Stories ou Reels", "horario": "10:00"},
            {"dia": "Domingo", "pilar": "Leve / Planejamento", "formato": "Imagem", "horario": "20:00"}
        ]
    )
