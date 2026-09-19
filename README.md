# Projeto Prático 1: Avaliação de Desempenho de Árvores Balanceadas em Bancos de Dados Chave-Valor (In-Memory Key-Value Store)

**Instituição:** Universidade Tecnológica Federal do Paraná (UTFPR) – Câmpus Medianeira  
**Curso:** Ciência da Computação  
**Disciplina:** Árvores e Grafos – Período Letivo 2026.2  
**Equipe:** Erik Mazzuco, Letícia Moro, Leonardo Herrero  
**Data Limite de Entrega no Moodle:** 22/09/2026  

---

## 🎯 Visão Geral

Este projeto implementa e avalia o desempenho de **seis árvores binárias de busca balanceadas** aplicadas como mecanismo de indexação e armazenamento para um **banco de dados chave-valor em memória** (Key-Value Store):

1. **Splay Tree** (Sleator & Tarjan, 1985) – Árvore autoajustável com operações top-down *splay*.
2. **Weight-Balanced Tree BB[α]** (Nievergelt & Reingold, 1973) – Balanço delimitado por peso de subárvores ($\alpha = 0.29$).
3. **AA Tree** (Andersson, 1993) – Variante simplificada de Rubro-Negra com níveis, *skew* e *split*.
4. **Scapegoat Tree** (Galperin & Rivest, 1993) – Árvore balanceada com zero metadados por nó e reconstrução $O(k)$ ($\alpha = 0.70$).
5. **Zip Tree** (Tarjan, Levy & Tsz-Kin Wong, 2019/2021) – Árvore aleatorizada isomórfica a Skip Lists com *unzip* e *zip*.
6. **WAVL Tree** (Haeupler, Sen & Tarjan, 2015) – Weak AVL baseada em diferenças de postos em $\{1, 2\}$, limitando rebalanceamentos a no máximo 2 rotações por inserção e remoção.

---

## 📁 Estrutura do Repositório

```text
AeG/
├── trees/
│   ├── __init__.py           # Exporta todas as 6 classes de árvores
│   ├── base.py               # Interface abstrata KeyValueStore e BaseNode
│   ├── splay_tree.py         # Implementação da Splay Tree
│   ├── bb_alpha_tree.py      # Implementação da Weight-Balanced Tree BB[α]
│   ├── aa_tree.py            # Implementação da AA Tree
│   ├── scapegoat_tree.py     # Implementação da Scapegoat Tree
│   ├── zip_tree.py           # Implementação da Zip Tree
│   └── wavl_tree.py          # Implementação da WAVL Tree
├── workloads/
│   ├── __init__.py
│   └── generator.py          # Gerador dos 6 workloads de teste (50k ops cada)
├── tests/
│   ├── __init__.py
│   └── test_trees.py         # Testes unitários de CRUD, estresse e invariantes matemáticas
├── plots/                    # Gráficos em alta resolução (300 DPI)
│   ├── throughput_comparison.png
│   ├── execution_time_comparison.png
│   ├── tree_height_comparison.png
│   ├── rebalance_overhead.png
│   ├── comparisons_per_op.png
│   └── zipfian_locality.png
├── results/                  # Dados brutos das medições
│   ├── benchmark_results.json
│   └── benchmark_results.csv
├── benchmark.py              # Suite de benchmark automatizada
├── generate_plots.py         # Script para geração dos gráficos comparativos
├── generate_report_pdf.py    # Compilador do relatório acadêmico completo em PDF
├── RELATORIO_PROJETO_1.pdf   # Relatório final formatado pronto para entrega
└── README.md                 # Este documento
```

---

## 🔬 Workloads Avaliados (Conforme Especificação UTFPR)

1. **Inserção Sequencial:** Inserção estritamente crescente ($0, 1, 2, \dots, N-1$) sem *get* ou *delete*.
2. **Inserção Aleatória:** Embaralhamento completo do conjunto de chaves, inserindo todas em ordem aleatória (caso médio).
3. **Carga Mista (OLTP):** 50% *put*, 40% *get*, 10% *delete*, com chaves escolhidas uniformemente.
4. **Leitura Intensiva:** Pré-povoamento de 10% do volume, seguido de 90% *get*, 5% *put*, 5% *delete*.
5. **Escrita Intensiva:** 70% *put*, 10% *get*, 20% *delete* (ingestão de alto volume).
6. **Zipfiano (Hotset):** Distribuição de popularidade assimétrica com expoente $s = 0.99$, simulando a regra 80/20 e hotspots reais de cache.

---

## 🚀 Como Executar

### 1. Instalar as Dependências
```powershell
python -m pip install -r requirements.txt
```

### 2. Executar os Testes Unitários e Validação de Invariantes
```powershell
python -m unittest discover -s tests -v
```

### 3. Executar o Benchmark Completo (50.000 Operações)
```powershell
python benchmark.py 50000
```

O benchmark compara o estado final de cada árvore com um `dict` de referência e
interrompe a execução se detectar divergência de chaves ou valores.

### 4. Gerar os Gráficos Comparativos
```powershell
python generate_plots.py
```

### 5. Compilar o Relatório Oficial em PDF
```powershell
python generate_report_pdf.py
```

O arquivo gerado estará disponível diretamente em `RELATORIO_PROJETO_1.pdf`.
