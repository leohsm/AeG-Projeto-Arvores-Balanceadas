import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically render header and 'Página X de Y' footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))

        # Skip header and footer on page 1 (cover page)
        if self._pageNumber > 1:
            # Running Header at top (y = 808)
            self.drawString(54, 808, "UTFPR – DACOM-MD | Árvores e Grafos – Projeto Prático 1: Árvores Balanceadas")
            self.setStrokeColor(colors.HexColor("#B0BEC5"))
            self.setLineWidth(0.6)
            self.line(54, 802, 541, 802)

            # Running Footer at bottom (y = 42)
            self.setStrokeColor(colors.HexColor("#B0BEC5"))
            self.setLineWidth(0.6)
            self.line(54, 42, 541, 42)
            self.drawString(54, 30, "Autores: Erik Mazzuco, Letícia Moro, Leonardo Herrero")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(541, 30, page_text)

        self.restoreState()


def build_pdf_report(json_path: str = "results/benchmark_results.json",
                     pdf_filename: str = "RELATORIO_PROJETO_1.pdf"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # A4: 595.27 x 841.89 pt. Printable width: 595.27 - 108 = 487.27 pt.
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        textColor=colors.HexColor("#1D3557"),
        alignment=1,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#457B9D"),
        alignment=1,
        spaceAfter=25
    )

    author_style = ParagraphStyle(
        'CoverAuthor',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2B2D42"),
        alignment=1,
        spaceAfter=4
    )

    inst_style = ParagraphStyle(
        'CoverInst',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor("#1D3557"),
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2A9D8F"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#222222"),
        alignment=4,  # Justified
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#222222"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#111111"),
        alignment=1
    )

    table_cell_left = ParagraphStyle(
        'TableCellLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#111111"),
        alignment=0
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceBefore=4,
        spaceAfter=8
    )

    story = []

    # =========================================================================
    # CAPA / CABEÇALHO INSTITUCIONAL
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("MINISTÉRIO DA EDUCAÇÃO", inst_style))
    story.append(Paragraph("UNIVERSIDADE TECNOLÓGICA FEDERAL DO PARANÁ – UTFPR", inst_style))
    story.append(Paragraph("CÂMPUS MEDIANEIRA", inst_style))
    story.append(Paragraph("DEPARTAMENTO ACADÊMICO DE COMPUTAÇÃO – DACOM-MD", inst_style))
    story.append(Paragraph("DISCIPLINA: ÁRVORES E GRAFOS", inst_style))
    story.append(Spacer(1, 35))

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1D3557"), spaceAfter=20, spaceBefore=5))
    story.append(Paragraph("PROJETO PRÁTICO 1: ÁRVORES BALANCEADAS", title_style))
    story.append(Paragraph("Avaliação Comparativa de Desempenho na Implementação de um Banco de Dados Chave-Valor em Memória (Key-Value Store)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#457B9D"), spaceAfter=25, spaceBefore=10))

    story.append(Spacer(1, 25))
    story.append(Paragraph("EQUIPE DE DESENVOLVIMENTO:", author_style))
    story.append(Paragraph("Erik Mazzuco", author_style))
    story.append(Paragraph("Letícia Moro", author_style))
    story.append(Paragraph("Leonardo Herrero", author_style))

    story.append(Spacer(1, 35))
    story.append(Paragraph("<b>Período Letivo:</b> 2026.2", inst_style))
    story.append(Paragraph("<b>Data Limite de Entrega:</b> 22 de Setembro de 2026", inst_style))
    story.append(Paragraph("Medianeira – PR", inst_style))

    story.append(PageBreak())

    # =========================================================================
    # 1. INTRODUÇÃO E CONTEXTUALIZAÇÃO
    # =========================================================================
    story.append(Paragraph("1. Introdução e Contextualização", h1_style))
    story.append(Paragraph(
        "Os bancos de dados chave-valor (<i>key-value stores</i>) constituem uma das categorias mais céleres e difundidas "
        "do ecossistema NoSQL. Operando predominantemente em memória volátil (RAM), tais sistemas abdicam de esquemas estáticos "
        "e junções relacionais complexas em prol de tempos de resposta na ordem de microssegundos para operações primárias de escrita "
        "(<code>put</code>), consulta (<code>get</code>) e exclusão (<code>delete</code>). Essa arquitetura alimenta serviços críticos "
        "globais, tais como barramentos de cache (Redis, Memcached), sessões distribuídas, filas de mensagens, buffers de telemetria "
        "e catálogos de e-commerce com alta concorrência.",
        body_style
    ))
    story.append(Paragraph(
        "Apesar da ampla utilização de tabelas de dispersão (<i>hash tables</i>) para acesso pontual O(1), as árvores binárias de busca "
        "balanceadas são componentes fundamentais quando os requisitos incluem ordenação intrínseca de registros, buscas por faixa "
        "(<i>range queries</i>), garantia estrita contra degradação de pior caso e resiliência a padrões de acesso adversários. "
        "O presente trabalho tem como meta central avaliar, quantificar e analisar comparativamente a performance de seis distintas "
        "variantes de árvores balanceadas na sustentação de um banco chave-valor sob seis cargas de trabalho (<i>workloads</i>) representativas de sistemas reais.",
        body_style
    ))

    # =========================================================================
    # 2. FUNDAMENTAÇÃO TEÓRICA DAS 6 ÁRVORES
    # =========================================================================
    story.append(Paragraph("2. Fundamentação Teórica das Estruturas Avaliadas", h1_style))
    story.append(Paragraph(
        "Foram selecionadas seis árvores com formulações algorítmicas substancialmente heterogêneas, abarcando autoajuste, balanço por peso, "
        "simplificação de níveis, balanço por postos relaxados, aleatorização e reconstrução por amortização:",
        body_style
    ))

    # Splay
    story.append(Paragraph("a. Splay Tree (Sleator & Tarjan, 1985)", h2_style))
    story.append(Paragraph(
        "A Splay Tree é uma árvore autoajustável pioneira proposta por Daniel Sleator e Robert Tarjan. Caracteriza-se por não armazenar "
        "nenhuma informação explícita de balanço (altura, cor ou fator) em seus nós. A cada busca, inserção ou remoção, o elemento visado "
        "é promovido até a raiz por uma cascata de rotações duplas e simples denominadas <i>splay</i> (casos Zig, Zig-Zig e Zig-Zag). "
        "Possui complexidade amortizada estrita de O(log n) por operação e satisfaz teoremas de otimalidade estática e localidade "
        "(<i>working set</i>). Contudo, em cargas de inserção estritamente sequenciais desprovidas de leituras, a árvore forma temporariamente "
        "uma espinha linear que atinge profundidade N antes de ser colapsada pelos acessos subsequentes.",
        body_style
    ))

    # BB[alpha]
    story.append(Paragraph("b. Weight-Balanced Tree (BB[α] - Nievergelt & Reingold, 1973)", h2_style))
    story.append(Paragraph(
        "A árvore de balanço limitado por peso BB[α] (<i>Bounded Balance</i>) assegura o equilíbrio estrutural monitorando a proporção de "
        "nós existentes nas subárvores. O peso estendido de um nó é formalizado como w(T) = tamanho(T) + 1. A invariante estrutural requer "
        "que para todo nó T, as frações w(T.esq)/w(T) e w(T.dir)/w(T) permaneçam no intervalo [α, 1 - α]. Adotou-se o parâmetro comprovadamente "
        "estável α = 0.29 (com limiar γ = (1 - 2α)/(1 - α) ≈ 0.5915, conforme Blum & Mehlhorn), permitindo selecionar deterministicamente "
        "entre rotações simples ou duplas para restabelecer a cota de altura estritamente logarítmica O(log n).",
        body_style
    ))

    # AA Tree
    story.append(Paragraph("c. AA Tree (Arne Andersson, 1993)", h2_style))
    story.append(Paragraph(
        "A AA Tree foi desenvolvida por Arne Andersson como uma variante didática e elegante da Árvore Rubro-Negra. Em substituição "
        "às cores, cada nó armazena um número inteiro representando seu nível. O algoritmo elimina completamente as arestas horizontais "
        "para a esquerda e proíbe dois links horizontais consecutivos à direita. Como consequência dessa forte restrição canônica, "
        "o rebalanceamento reduz-se a duas operações primitivas ortogonais: <b>Skew</b> (rotação à direita para eliminar arestas esquerdas "
        "do mesmo nível) e <b>Split</b> (rotação à esquerda com elevação de nível para fracionar sequências horizontais duplas à direita).",
        body_style
    ))

    # Scapegoat
    story.append(Paragraph("d. Scapegoat Tree (Galperin & Rivest, 1993)", h2_style))
    story.append(Paragraph(
        "A Scapegoat Tree é uma estrutura autobalanceável que dispensa completamente metadados de controle por nó, armazenando apenas "
        "os ponteiros dos filhos e a tupla chave-valor. O estado global consiste apenas no número atual de elementos (n) e no tamanho "
        "máximo histórico desde a última reconstrução global (max_size). Se a profundidade de inserção ultrapassar o teto logarítmico "
        "floor(log_{1/α}(n)) (adotou-se α = 0.70), o algoritmo percorre os ancestrais para encontrar o nó bode expiatório (<i>scapegoat</i>), "
        "reconstruindo toda a subárvore em tempo O(k) como uma árvore perfeitamente simétrica. Garante buscas rápidas e inserção amortizada O(log n).",
        body_style
    ))

    # Zip Tree
    story.append(Paragraph("e. Zip Tree (Tarjan, Levy & Tsz-Kin Wong, 2019/2021)", h2_style))
    story.append(Paragraph(
        "A Zip Tree é uma estrutura de busca aleatorizada recente concebida por Robert Tarjan et al., estabelecendo uma equivalência "
        "direta com Skip Lists sob a interface de árvores binárias. Cada nó recebe um posto (<i>rank</i>) aleatório derivado de uma "
        "distribuição geométrica com p = 0.5. As inserções são realizadas particionando caminhos de busca por posto (<b>Unzip</b>) e as "
        "remoções mesclam as subárvores preservando a ordem de prioridade (<b>Zip</b>). Dispensa rotações complexas com ponteiros triplos "
        "e atinge altura esperada O(log n) com expressiva concisão de código.",
        body_style
    ))

    # WAVL
    story.append(Paragraph("f. WAVL Tree - Weak AVL (Haeupler, Sen & Tarjan, 2015)", h2_style))
    story.append(Paragraph(
        "A Weak AVL Tree sintetiza a disciplina de altura rigorosa da árvore AVL clássica com a flexibilidade de manutenção das árvores "
        "rubro-negras. Baseia-se em postos inteiros onde as diferenças de posto entre pais e filhos pertencem estritamente ao conjunto {1, 2}. "
        "Essa flexibilização garante altura estritamente delimitada por ≈ 1.44 log_2(n). O marco teórico fundamental da WAVL consiste no "
        "fato de que tanto a inserção quanto a remoção exigem <b>no máximo 2 rotações estruturais</b> para recuperar o balanço completo, "
        "superando o pior caso da AVL original que pode desencadear O(log n) rotações durante a remoção.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # 3. METODOLOGIA E WORKLOADS
    # =========================================================================
    story.append(Paragraph("3. Metodologia do Benchmark e Descrição dos Workloads", h1_style))
    story.append(Paragraph(
        "Para confrontar a robustez algorítmica de cada estrutura em regime empírico rigoroso, foram modelados e executados "
        "seis perfis de acesso simulando casos reais de utilização de bancos chave-valor. O volume de teste compreendeu "
        "<b>50.000 operações</b> por workload, com 3 repetições sob medição com cronômetro de resolução em nanossegundos "
        "(<code>time.perf_counter_ns</code>) e sementes controladas para garantir total reprodutibilidade:",
        body_style
    ))

    story.append(Paragraph("<b>1. Inserção Sequencial:</b> Inserção estrita de chaves crescentes (0, 1, ..., N-1) sem consultas ou exclusões intermediárias. Constitui o pior cenário clássico para árvores binárias, expondo a capacidade de conter a degeneração linear.", bullet_style))
    story.append(Paragraph("<b>2. Inserção Aleatória:</b> Permutação uniforme das 50.000 chaves inseridas uma única vez. Representa o caso médio de povoamento inicial homogêneo.", bullet_style))
    story.append(Paragraph("<b>3. Carga Mista (OLTP):</b> 50% put, 40% get e 10% delete com chaves selecionadas uniformemente entre as ativas. Modela o comportamento genérico de sistemas transacionais.", bullet_style))
    story.append(Paragraph("<b>4. Leitura Intensiva:</b> Povoamento prévio de 10% do volume total seguido de 90% get, 5% put e 5% delete. Modela serviços de catálogo, servidores de cache DNS/sessão e visualização de dados.", bullet_style))
    story.append(Paragraph("<b>5. Escrita Intensiva:</b> 70% put, 10% get e 20% delete. Simula ingestão contínua em alto volume, como logs de auditoria e fluxos de telemetria de sensores.", bullet_style))
    story.append(Paragraph("<b>6. Zipfiano (Hotset):</b> Simulação de extrema desigualdade de acessos governada pela distribuição de Zipf: P(k) ∝ 1/k^s, com s = 0.99. Reflete a regra 80-20 presente em sistemas corporativos, onde uma fatia diminuta de chaves populares concentra a maioria esmagadora das requisições.", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # 4. RESULTADOS EXPERIMENTAIS
    # =========================================================================
    story.append(Paragraph("4. Resultados Experimentais Consolidados", h1_style))
    story.append(Paragraph(
        "A Tabela 1 apresenta a consolidação empírica de todas as medições realizadas, correlacionando tempo total de processamento, "
        "vazão operacional, altura final da estrutura, volume total de rotações e modificações de ponteiros, além da média de comparações de chaves por operação:",
        body_style
    ))

    headers = [
        Paragraph("<b>Workload</b>", table_header_style),
        Paragraph("<b>Árvore</b>", table_header_style),
        Paragraph("<b>Tempo (ms)</b>", table_header_style),
        Paragraph("<b>Vazão (ops/s)</b>", table_header_style),
        Paragraph("<b>Altura</b>", table_header_style),
        Paragraph("<b>Rot / Mod</b>", table_header_style),
        Paragraph("<b>Comp/op</b>", table_header_style)
    ]

    table_rows = [headers]
    for item in data:
        w = item["workload"].replace(" (OLTP)", "").replace(" (Hotset)", "")
        t = item["tree"].replace("Tree", "").replace(" (0.29)", "").replace(" (0.70)", "").strip()
        time_str = f"{item['time_ms']:.1f}"
        tp_str = f"{item['throughput_ops_sec']:,.0f}"
        h_str = f"{item['height']}"
        rot_mod = f"{item['rotations']:,} / {item['structural_mods']:,}" if item['rotations'] > 0 or item['structural_mods'] > 0 else "0 / 0"
        comp_str = f"{item['comparisons'] / max(1, item['ops_count']):.2f}"

        row = [
            Paragraph(w, table_cell_left),
            Paragraph(t, table_cell_left),
            Paragraph(time_str, table_cell_style),
            Paragraph(tp_str, table_cell_style),
            Paragraph(h_str, table_cell_style),
            Paragraph(rot_mod, table_cell_style),
            Paragraph(comp_str, table_cell_style)
        ]
        table_rows.append(row)

    res_table = Table(table_rows, colWidths=[78, 75, 48, 62, 34, 130, 48], repeatRows=1)
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1D3557")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ]))

    story.append(res_table)
    story.append(Paragraph("Tabela 1: Métricas quantitativas de desempenho sob carga de 50.000 operações por workload.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # 5. ANÁLISE GRÁFICA COMPARATIVA
    # =========================================================================
    story.append(Paragraph("5. Análise Comparativa dos Resultados Gráficos", h1_style))

    # Figure 1: Throughput
    fig1_path = "plots/throughput_comparison.png"
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=6.6 * inch, height=3.5 * inch))
        story.append(Paragraph("Figura 1: Comparativo de Vazão Operacional (Throughput) das seis estruturas ao longo dos seis perfis de carga.", caption_style))

    story.append(Paragraph(
        "<b>Análise da Vazão e Eficiência Operacional (Figura 1):</b> A <b>WAVL Tree</b> consolidou-se como a estrutura de maior regularidade e throughput "
        "nos cenários práticos de consulta e processamento transacional: registrou <b>904.321 ops/s</b> na Leitura Intensiva e <b>535.571 ops/s</b> na Carga Mista (OLTP). "
        "A <b>Splay Tree</b> alcançou um pico extraordinário na Inserção Sequencial (1,45 milhão de ops/s), justificado pela simplicidade mecânica "
        "de anexar o antigo nó raiz à esquerda sem efetuar rotações. Já a <b>Scapegoat Tree</b> destacou-se com grande agilidade na Inserção Aleatória "
        "(368.290 ops/s) e no cenário Zipfiano (1,06 milhão de ops/s), beneficiada pela ausência de sobrecarga em leituras e baixa frequência de reconstruções.",
        body_style
    ))

    # Figure 2: Execution Time (Log Scale)
    fig2_path = "plots/execution_time_comparison.png"
    if os.path.exists(fig2_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig2_path, width=6.6 * inch, height=3.0 * inch))
        story.append(Paragraph("Figura 2: Tempo total de processamento em milissegundos sob escala logarítmica (menor tempo indica maior eficiência).", caption_style))

    story.append(PageBreak())

    # Figure 3: Tree Height
    fig3_path = "plots/tree_height_comparison.png"
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=6.6 * inch, height=3.2 * inch))
        story.append(Paragraph("Figura 3: Altura final observada comparada com o limite inferior ótimo teórico ceil(log2(N+1)) = 16.", caption_style))

    story.append(Paragraph(
        "<b>Disciplina Estrutural de Altura (Figura 3):</b> O controle rigoroso de profundidade é o que impede uma árvore de degenerar em busca linear. "
        "Para 50.000 nós, onde o piso ótimo teórico absoluto é ceil(log_2(50001)) = 16 níveis, a <b>WAVL Tree</b> atingiu um patamar de perfeição matemática, "
        "com alturas entre <b>15 e 19</b> níveis em todos os testes. A <b>BB[α]</b> e a <b>AA Tree</b> demonstraram consistência idêntica, oscilando entre "
        "15 e 21 níveis. A <b>Zip Tree</b> exibiu alturas entre 37 e 50 níveis, um comportamento intrínseco às árvores probabilísticas que operam com posto geométrico. "
        "A <b>Splay Tree</b> confirma sua característica teórica clássica: após inserções sequenciais puras gerou a espinha de 50.000 nós, mas recompôs "
        "rapidamente o balanceamento para a faixa de 28 a 33 níveis assim que as operações de leitura e splaying foram executadas.",
        body_style
    ))

    # Figure 4: Rebalancing Overhead
    fig4_path = "plots/rebalance_overhead.png"
    if os.path.exists(fig4_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig4_path, width=6.6 * inch, height=2.6 * inch))
        story.append(Paragraph("Figura 4: Volume de rotações e modificações estruturais executadas para sustentar as cargas Aleatória e Mista.", caption_style))

    # Figure 6: Zipfian Locality
    fig6_path = "plots/zipfian_locality.png"
    if os.path.exists(fig6_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig6_path, width=5.2 * inch, height=2.7 * inch))
        story.append(Paragraph("Figura 5: Profundidade média de busca para chaves quentes (top 10 do ranking Zipf) versus chaves frias (posições > 500).", caption_style))

    story.append(Paragraph(
        "<b>Efeito de Localidade e Cargas Zipfianas (Figura 5):</b> O experimento sob a distribuição de Zipf evidenciou a superioridade dinâmica "
        "da <b>Splay Tree</b> em ambientes de cache com concentração de acessos (regra 80/20). Devido à auto-reorganização, as dez chaves mais populares "
        "foram mantidas em profundidade média de apenas <b>6.4 níveis</b>, em contraste com a profundidade de 20.5 para itens frios. "
        "Nas árvores rigidamente balanceadas (WAVL, BB[α] e AA), as chaves quentes permaneceram distribuídas indistintamente entre as profundidades "
        "11 e 12, exigindo o mesmo número de comparações de um item raramente acessado.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # 6. DISCUSSÃO CRÍTICA E CONCLUSÕES
    # =========================================================================
    story.append(Paragraph("6. Discussão Crítica e Recomendações de Engenharia", h1_style))
    story.append(Paragraph(
        "Com base nos dados empíricos e nas propriedades analíticas evidenciadas neste benchmark, são delineadas as seguintes diretrizes "
        "para a seleção de estruturas de dados na arquitetura de bancos de dados chave-valor em memória:",
        body_style
    ))

    story.append(Paragraph(
        "<b>1. WAVL Tree como Estrutura Primária para Bancos Chave-Valor em Memória:</b> A Weak AVL Tree destacou-se como a campeã "
        "geral de desempenho. Ao limitar estritamente as rotações a no máximo 2 tanto na inserção quanto na exclusão, ela elimina a "
        "sobrecarga de rebalanceamentos profundos sem degradar a altura (mantida sempre entre 15 e 19). É a opção ideal para bases NoSQL "
        "com alta demanda transacional e concorrência mista.",
        bullet_style
    ))

    story.append(Paragraph(
        "<b>2. Splay Tree como Motor de Cache com Acessos Assimétricos:</b> Em sistemas onde certos registros são intensamente requisitados "
        "(hotspots, sessões ativas e feeds em alta), a Splay Tree minimiza as comparações de chaves para os itens do conjunto de trabalho, "
        "oferecendo latências excelentes. Contudo, seu uso em cargas puras de ingestão sequencial demanda mecanismos adicionais de proteção contra espinhas.",
        bullet_style
    ))

    story.append(Paragraph(
        "<b>3. Scapegoat Tree para Aplicações com Severo Limite de Memória (RAM-Constrained):</b> Por exigir exatamente zero bytes "
        "de controle em cada nó, a Scapegoat Tree proporciona o menor consumo de memória do benchmark. O fato de dispensar manutenção em buscas "
        "proporcionou mais de 1 milhão de operações/segundo no cenário Zipfiano, consolidando-a como a melhor escolha para dispositivos embarcados e IoT.",
        bullet_style
    ))

    story.append(Paragraph(
        "<b>4. AA Tree pela Razão Custo-Benefício entre Simplicidade e Robustez:</b> A AA Tree atingiu um patamar invejável de equilíbrio "
        "(alturas 17-21, vazão até 600k ops/s) utilizando uma base de código extremamente enxuta composta apenas por <code>skew</code> e <code>split</code>. "
        "Substitui com folga a Árvore Rubro-Negra tradicional em projetos acadêmicos e industriais onde manutenibilidade e facilidade de depuração são prioritárias.",
        bullet_style
    ))

    story.append(Paragraph(
        "<b>5. Zip Tree e a Eficiência do Balanceamento Aleatorizado:</b> As Zip Trees provaram que o princípio estatístico das Skip Lists "
        "pode ser aplicado com sucesso a árvores binárias sem envolver rotações rígidas de ponteiros pai. Com operações simples de descompactação e compactação, "
        "demonstrou vazão competitiva de até 680k ops/s em cargas Zipfianas.",
        bullet_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # 7. REFERÊNCIAS BIBLIOGRÁFICAS
    # =========================================================================
    story.append(Paragraph("7. Referências Bibliográficas", h1_style))
    story.append(Paragraph("[1] ANDERSSON, Arne. <i>Balanced search trees made simple</i>. In: Workshop on Algorithms and Data Structures (WADS). Springer, 1993. p. 60–71.", bullet_style))
    story.append(Paragraph("[2] SLEATOR, Daniel D.; TARJAN, Robert E. <i>Self-adjusting binary search trees</i>. Journal of the ACM (JACM), v. 32, n. 3, p. 652–686, 1985.", bullet_style))
    story.append(Paragraph("[3] NIEVERGELT, Jürg; REINGOLD, Edward M. <i>Binary search trees of bounded balance</i>. SIAM Journal on Computing, v. 2, n. 1, p. 33–43, 1973.", bullet_style))
    story.append(Paragraph("[4] GALPERIN, Igal; RIVEST, Ronald L. <i>Scapegoat trees</i>. In: Proceedings of the 4th Annual ACM-SIAM Symposium on Discrete Algorithms (SODA). 1993. p. 165–174.", bullet_style))
    story.append(Paragraph("[5] TARJAN, Robert E.; LEVY, Caleb; TSZ-KIN WONG, Stephen. <i>Zip Trees</i>. ACM Transactions on Algorithms (TALG), v. 17, n. 4, p. 1–24, 2021.", bullet_style))
    story.append(Paragraph("[6] HAEUPLER, Bernhard; SEN, Siddhartha; TARJAN, Robert E. <i>Rank-balanced trees</i>. ACM Transactions on Algorithms (TALG), v. 11, n. 4, p. 1–26, 2015.", bullet_style))
    story.append(Paragraph("[7] BLUM, Norbert; MEHLHORN, Kurt. <i>On the average number of rebalancing steps in weight-balanced trees</i>. Theoretical Computer Science, v. 11, n. 3, p. 303–320, 1980.", bullet_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatório PDF construído com sucesso em: {pdf_filename}")


if __name__ == "__main__":
    build_pdf_report()
