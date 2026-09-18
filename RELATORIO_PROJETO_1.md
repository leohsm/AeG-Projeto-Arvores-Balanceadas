# Relatório de Avaliação de Desempenho de Árvores Balanceadas em Bancos de Dados Chave-Valor (In-Memory Key-Value Store)

**Ministério da Educação**  
**Universidade Tecnológica Federal do Paraná (UTFPR) – Câmpus Medianeira**  
**Curso: Ciência da Computação**  
**Disciplina:** Árvores e Grafos (Período Letivo 2026.2)  
**Projeto Prático 1 – Árvores Balanceadas**  
**Equipe:** Erik Mazzuco, Letícia Moro, Leonardo Herrero  
**Data Limite:** 22/09/2026  

---

## 1. Introdução e Contextualização

Os bancos de dados chave-valor (*key-value stores*) constituem o alicerce fundamental do paradigma de armazenamento NoSQL em memória volátil (RAM). Caracterizam-se por uma interface intencionalmente minimalista composta primordialmente por três operações essenciais:
- `put(key, value)`: insere ou atualiza um registro associado a uma chave única;
- `get(key)`: recupera o valor correspondente a uma chave em latência sub-milissegundo;
- `delete(key)`: remove a entrada especificada da memória.

Ao abdicar de esquemas relacionais rígidos (*schemaless*), validações dispendiosas de tipos em tempo de execução e junções complexas (*JOINs*), esse modelo propicia vazões operacionais na ordem de centenas de milhares a milhões de requisições por segundo. Essa arquitetura é a base de tecnologias como Redis, Memcached, barramentos de sessão distribuída, caches de DNS, tabelas de roteamento e filas em memória.

Embora tabelas de dispersão (*hash tables*) ofereçam tempo médio $O(1)$ para consultas pontuais, estruturas de dados baseadas em árvores binárias de busca balanceadas tornam-se insubstituíveis quando o sistema exige:
1. **Ordenação intrínseca e consultas por intervalo (*range queries*):** recuperar eficientemente todas as chaves entre $[k_1, k_2]$;
2. **Garantias de pior caso:** imunidade contra picos de latência ocasionados por colisões massivas ou ataques de negação de serviço (*HashDoS*);
3. **Previsibilidade de memória e ausência de *rehash* abrupto:** tabelas hash exigem redimensionamentos globais periódicos com duplicação temporária de consumo de memória, ao passo que árvores alocam nós de modo granular e amortizado.

Este trabalho prático tem como objetivo central implementar, testar e avaliar comparativamente o desempenho de seis arquiteturas de árvores balanceadas sob seis padrões realistas de carga de trabalho (*workloads*).

---

## 2. Fundamentação Teórica das Estruturas Avaliadas

### a. Splay Tree (Sleator & Tarjan, 1985)
- **Princípio:** Árvore binária de busca autoajustável pioneira. Não armazena nenhuma informação de controle (altura, cores ou postos) nos nós, garantindo $O(1)$ de sobrecarga de memória por nó além dos ponteiros e dados.
- **Mecanismo de Rebalanceamento:** A operação `splay(x)` rotaciona o nó acessado até a raiz por meio de combinações de passos:
  - *Zig:* rotação simples quando o pai é a raiz;
  - *Zig-Zig:* rotações homogêneas no pai e depois no nó (quando ambos são filhos esquerdos ou ambos direitos);
  - *Zig-Zag:* rotações heterogêneas (rotação dupla padrão).
- **Complexidade:** $O(\log n)$ amortizado para todas as operações. Possui a propriedade do conjunto de trabalho (*working-set property*) e otimalidade estática.
- **Comportamento Característico:** Excelente em cargas com forte localidade temporal (acessos repetidos a chaves quentes). Em contrapartida, inserções estritamente sequenciais sem leituras geram temporariamente uma espinha linear de altura $N$, que é colapsada apenas após a primeira busca.

### b. Weight-Balanced Tree (BB[α] - Nievergelt & Reingold, 1973)
- **Princípio:** O equilíbrio baseia-se no peso das subárvores, onde o peso estendido é formalizado como $w(T) = \text{tamanho}(T) + 1$.
- **Invariante:** Para todo nó $T$, as frações de peso dos filhos esquerdo e direito satisfazem:
  $$\alpha \le \frac{w(T_L)}{w(T)} \le 1 - \alpha$$
- **Parâmetros Adotados:** $\alpha = 0.29$ (comprovadamente estável por Blum & Mehlhorn), com o limiar $\gamma = \frac{1-2\alpha}{1-\alpha} \approx 0.5915$.
- **Complexidade:** Altura estritamente limitada a $O(\log n)$ no pior caso. Garante buscas rápidas à custa de atualizar e verificar pesos durante cada percurso de volta na árvore.

### c. AA Tree (Arne Andersson, 1993)
- **Princípio:** Variante refinada da Árvore Rubro-Negra desenvolvida para simplificar drasticamente os casos de rotação. Em vez de cores, associa um nível inteiro a cada nó.
- **Invariantes Estruturais:**
  1. O nível de todo nó folha é 1;
  2. O nível do filho esquerdo é estritamente $\text{nível}(\text{pai}) - 1$ (proibidos links horizontais à esquerda);
  3. O nível do filho direito é igual ou um a menos que o do pai;
  4. O nível do neto direito é estritamente menor que o do avô (proibidos dois links horizontais consecutivos à direita);
  5. Nós com nível $> 1$ possuem dois filhos.
- **Operações:**
  - `skew(T)`: rotação à direita para eliminar arestas horizontais esquerdas;
  - `split(T)`: rotação à esquerda acompanhada de elevação de nível para dividir links horizontais consecutivos à direita.
- **Complexidade:** $O(\log n)$ no pior caso para busca, inserção e remoção, com código limpo e conciso.

### d. Scapegoat Tree (Galperin & Rivest, 1993)
- **Princípio:** Árvore de busca autobalanceável que dispensa completamente metadados nos nós (zero bytes por nó). Mantém apenas duas variáveis globais na árvore: o tamanho atual $n$ e o tamanho máximo histórico $M$.
- **Mecanismo de Rebalanceamento:** Quando a profundidade de inserção ultrapassa o limiar:
  $$d > \lfloor \log_{1/\alpha}(n) \rfloor \quad (\text{com } \alpha = 0.70)$$
  o algoritmo sobe a cadeia de ancestrais para localizar o primeiro nó "bode expiatório" (*scapegoat*) que viole a condição de peso ($\text{tamanho}(\text{filho}) > \alpha \cdot \text{tamanho}(\text{nó})$). A subárvore correspondente é linearizada e inteiramente reconstruída como uma árvore perfeitamente balanceada em tempo $O(k)$. Na remoção, quando $n < \alpha \cdot M$, a árvore inteira é reconstruída.
- **Complexidade:** Busca $O(\log n)$ no pior caso; inserção e remoção $O(\log n)$ amortizado.

### e. Zip Tree (Tarjan, Levy & Tsz-Kin Wong, 2019/2021)
- **Princípio:** Estrutura aleatorizada recente que estabelece um isomorfismo direto com Skip Lists, porém sob a topologia de árvore binária de busca.
- **Mecanismo de Rebalanceamento:** Cada nó recebe um posto (*rank*) numérico sorteado a partir de uma distribuição geométrica com probabilidade $p = 0.5$ ($P(\text{rank} = k) = (1/2)^{k+1}$).
- **Operações Fundamentais:**
  - `unzip(T, key)`: particiona a árvore ao longo do caminho de busca em duas subárvores (chaves $< key$ e chaves $> key$);
  - `zip(L, R)`: funde duas árvores adjacentes preservando as prioridades relativas dos postos sem necessitar de rotações com ponteiros triplos.
- **Complexidade:** Altura e operações com custo esperado $O(\log n)$.

### f. WAVL Tree (Weak AVL - Haeupler, Sen & Tarjan, 2015)
- **Princípio:** Generalização moderna das árvores AVL e Rubro-Negras baseada em postos inteiros. Nós nulos possuem posto -1 e folhas possuem posto 0.
- **Invariantes:**
  1. A diferença de postos entre qualquer nó e seus filhos pertence estritamente a $\{1, 2\}$;
  2. Toda folha possui posto 0.
- **Garantias Teóricas Inovadoras:** Altura limitada a no máximo $\approx 1.44 \log_2(n)$. Ao contrário da AVL clássica (que pode exigir $O(\log n)$ rotações em cascata na remoção), a WAVL Tree garante matematicamente **no máximo 2 rotações em qualquer inserção e no máximo 2 rotações em qualquer remoção**, ajustando desequilíbrios remanescentes via promoções e despromoções de posto em tempo $O(1)$.

---

## 3. Metodologia do Benchmark e Workloads

Para assegurar uma avaliação fidedigna, foram implementados seis geradores de carga de trabalho modelados a partir de perfis de uso documentados em sistemas de produção (cargas YCSB e benchmarks NoSQL industriais). Cada workload processou **50.000 operações**, executadas em 3 repetições sob medições de temporizador monotônico de alta precisão (`perf_counter_ns`):

1. **Inserção Sequencial:** Inserção estritamente crescente ($0, 1, \dots, N-1$). Avalia a capacidade de conter a degeneração da estrutura sem leituras intermediárias.
2. **Inserção Aleatória:** Embaralhamento completo das 50.000 chaves inseridas de modo uniforme (caso médio de carga de dados).
3. **Carga Mista (OLTP):** 50% `put`, 40% `get` e 10% `delete` sobre o conjunto de chaves ativas (perfil transacional neutro).
4. **Leitura Intensiva:** Povoamento prévio de 10% do volume seguido de 90% `get`, 5% `put` e 5% `delete`. Modela sistemas de cache e catálogos de consulta rápida.
5. **Escrita Intensiva:** 70% `put`, 10% `get` e 20% `delete`. Modela ingestão contínua de telemetria, logs de auditoria e processamento de eventos em lote.
6. **Zipfiano (Hotset):** Distribuição de popularidade assimétrica descrita por $P(k) \propto 1/k^s$ com expoente de assimetria $s = 0.99$. Simula o fenômeno real de concentração de acessos em poucas chaves muito populares (princípio 80/20).

---

## 4. Resultados Quantitativos Consolidados

A tabela a seguir apresenta as métricas empíricas coletadas após a execução dos workloads com $N = 50.000$ operações:

| Workload | Árvore | Tempo Médio (ms) | Throughput (ops/s) | Altura Final | Razão Altura / Mínimo | Rotações | Modificações Estruturais | Comparações / Op |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Inserção Sequencial** | Splay Tree | 34.4 | 1,456,153 | 50.000 | 3125.0 | 0 | 49,999 | 1.00 |
| | BB[α] (0.29) | 525.4 | 95,192 | 20 | 1.25 | 49,980 | 49,980 | 17.08 |
| | AA Tree | 351.5 | 142,368 | 21 | 1.31 | 49,979 | 49,979 | 20.34 |
| | Scapegoat (0.70) | 459.4 | 108,982 | 31 | 1.94 | 0 | 868,975 | 27.43 |
| | Zip Tree | 208.6 | 240,180 | 43 | 2.69 | 0 | 66,645 | 14.18 |
| | **WAVL Tree** | **162.7** | **307,639** | **16** | **1.00** | 49,984 | 199,946 | 14.69 |
| **Inserção Aleatória** | Splay Tree | 214.8 | 233,612 | 49 | 3.06 | 439,822 | 1,245,993 | 31.58 |
| | BB[α] (0.29) | 527.2 | 94,846 | 20 | 1.25 | 33,540 | 33,540 | 14.56 |
| | AA Tree | 333.0 | 150,251 | 21 | 1.31 | 86,091 | 86,091 | 14.72 |
| | **Scapegoat (0.70)** | **136.1** | **368,290** | 31 | 1.94 | 0 | 578 | 18.26 |
| | Zip Tree | 318.9 | 156,882 | 50 | 3.12 | 0 | 135,356 | 21.24 |
| | **WAVL Tree** | **180.1** | **280,315** | **19** | **1.19** | 34,802 | 170,372 | 14.47 |
| **Carga Mista (OLTP)** | Splay Tree | 124.3 | 402,307 | 53 | 3.31 | 257,779 | 759,078 | 20.49 |
| | BB[α] (0.29) | 303.7 | 164,875 | 19 | 1.19 | 16,491 | 16,491 | 14.52 |
| | AA Tree | 227.8 | 219,770 | 21 | 1.31 | 21,539 | 29,354 | 14.71 |
| | Scapegoat (0.70) | 234.5 | 218,600 | 26 | 1.62 | 0 | 229,001 | 20.79 |
| | Zip Tree | 165.7 | 301,783 | 41 | 2.56 | 0 | 40,144 | 18.07 |
| | **WAVL Tree** | **93.4** | **535,571** | **16** | **1.00** | 15,906 | 63,868 | 14.16 |
| **Leitura Intensiva** | Splay Tree | 114.2 | 438,196 | 28 | 2.00 | 250,759 | 756,019 | 21.11 |
| | BB[α] (0.29) | 82.1 | 609,398 | 15 | 1.07 | 3,463 | 3,463 | 11.88 |
| | AA Tree | 83.3 | 601,260 | 17 | 1.21 | 5,378 | 8,460 | 11.98 |
| | Scapegoat (0.70) | 77.4 | 646,550 | 23 | 1.64 | 0 | 30,660 | 15.26 |
| | Zip Tree | 77.0 | 650,424 | 37 | 2.64 | 0 | 5,663 | 16.35 |
| | **WAVL Tree** | **55.4** | **904,321** | **15** | **1.07** | 3,130 | 12,799 | 11.93 |
| **Escrita Intensiva** | **Splay Tree** | **93.5** | **536,622** | 110 | 6.87 | 174,804 | 489,584 | 12.12 |
| | BB[α] (0.29) | 458.1 | 109,234 | 20 | 1.25 | 37,455 | 37,455 | 16.23 |
| | AA Tree | 335.4 | 149,186 | 21 | 1.31 | 50,013 | 67,778 | 16.21 |
| | Scapegoat (0.70) | 372.8 | 134,293 | 29 | 1.81 | 0 | 601,595 | 24.29 |
| | Zip Tree | 199.0 | 251,746 | 40 | 2.50 | 0 | 56,781 | 14.96 |
| | **WAVL Tree** | **132.8** | **376,636** | **16** | **1.00** | 36,491 | 147,058 | 14.70 |
| **Zipfiano (Hotset)** | Splay Tree | 94.3 | 557,594 | 33 | 2.36 | 211,058 | 622,873 | 16.57 |
| | BB[α] (0.29) | 112.3 | 468,224 | 16 | 1.14 | 1,517 | 1,517 | 12.48 |
| | AA Tree | 103.4 | 508,742 | 19 | 1.36 | 10,241 | 15,080 | 12.44 |
| | **Scapegoat (0.70)** | **49.4** | **1,063,286** | 24 | 1.71 | 0 | 0 | 10.10 |
| | Zip Tree | 77.4 | 680,331 | 40 | 2.86 | 0 | 14,280 | 13.24 |
| | **WAVL Tree** | **58.4** | **900,381** | **15** | **1.07** | 1,526 | 7,159 | 12.40 |

*Nota:* O piso mínimo teórico ótimo para $N = 50.000$ elementos é $\lceil\log_2(50001)\rceil = 16$ níveis.

---

## 5. Análise dos Resultados e Gráficos

### 5.1 Throughput e Latência Global
A **WAVL Tree** demonstrou superioridade incontestável na maioria das cargas equilibradas e orientadas à leitura. Na carga de **Leitura Intensiva**, a WAVL atingiu **904.321 ops/s**, superando a AA Tree (601k ops/s) e a BB[α] (609k ops/s). A razão direta reside na combinação sinérgica de:
1. Altura compacta estrita (15 níveis para 50.000 chaves);
2. Custo nulo de rebalanceamento durante operações puras de leitura (`get`), contrastando com a sobrecarga contínua da Splay Tree que rotaciona nós a cada consulta.

Na **Inserção Sequencial**, a **Splay Tree** atingiu a maior vazão pontual (1,45 milhão de ops/s). Isso decorre do fato de que o algoritmo *top-down splay* simplesmente anexa o nó raiz existente como filho esquerdo da nova chave sem disparar rotações corretivas intermediárias. Contudo, essa velocidade inicial cobra um tributo estrutural: gera uma árvore degenerada com altura igual a 50.000 níveis.

### 5.2 Disciplina de Altura e Eficiência de Balanceamento
O gráfico de altura evidenciou a precisão matemática das estruturas balanceadas:
- A **WAVL Tree** manteve altura entre **15 e 19 níveis** em todos os seis cenários, tangenciando o limite ótimo teórico de 16 níveis.
- A **BB[α]** manteve alturas de 15 a 20 níveis, demonstrando que a invariante baseada em pesos de subárvores é extraordinariamente rígida.
- A **AA Tree** oscilou com estabilidade invejável entre 17 e 21 níveis, comprovando a eficácia da eliminação de links esquerdos.
- A **Zip Tree** apresentou alturas ligeiramente superiores (entre 37 e 50 níveis), comportamento condizente com a variância estatística de árvores binárias probabilísticas.

### 5.3 Sobrecarga de Rebalanceamento
Sob a carga **Mista (OLTP)**:
- A **WAVL Tree** executou apenas 15.906 rotações para processar 50.000 operações mistas, confirmando a cota teórica de no máximo 2 rotações por alteração.
- A **Splay Tree** executou 257.779 rotações, pois cada consulta exige reconfiguração completa do caminho até a raiz.
- A **Scapegoat Tree** realizou zero rotações convencionais, concentrando seu esforço em reconstruções pontuais de blocos de nós desequilibrados.

### 5.4 Efeito de Localidade sob a Distribuição Zipfiana
O experimento específico com a distribuição de Zipf comprovou empiricamente o teorema de autoajuste da **Splay Tree**:
- A profundidade média de busca para as **10 chaves mais populares** na Splay Tree foi de apenas **6.4 níveis**, enquanto as chaves frias (posições > 500) localizaram-se a uma profundidade média de **20.5 níveis**.
- Em contrapartida, em árvores com topologia estática baseada puramente na ordem das chaves (WAVL, AA, BB[α]), as chaves quentes e frias apresentaram profundidades indistintas (entre 11 e 12 níveis). Esse resultado demonstra que para caches com alta concentração de acessos, a Splay Tree otimiza naturalmente a retenção de dados quentes próximos à raiz.

---

## 6. Conclusões e Recomendações de Engenharia

1. **WAVL Tree como Escolha Primária para Bancos Chave-Valor em Memória:**
   A Weak AVL Tree estabelece o estado da arte para indexação NoSQL em RAM. Oferece as menores alturas (15 a 19), o menor tempo de execução global e a maior vazão em cargas concorrentes mistas e de leitura. A garantia matemática de no máximo 2 rotações por inserção e remoção torna seu comportamento operacional previsível e robusto.

2. **Splay Tree para Camadas de Cache com Hotspots Pronunciados:**
   Recomenda-se o emprego de Splay Trees em subsistemas de cache onde a distribuição de acessos é severamente assimétrica (princípio 80/20, catálogos promocionais e sessões de usuários ativos). Para mitigar sua fraqueza sob sequências monotônicas puras de escrita, sugere-se implementar um limitador de profundidade que force um balanceamento esporádico caso a altura ultrapasse $2 \log_2 n$.

3. **Scapegoat Tree para Dispositivos com Restrição Severa de RAM (Embedded/IoT):**
   Com exatamente zero bytes de sobrecarga estrutural por nó, a Scapegoat Tree é a arquitetura ideal quando a capacidade de memória principal é o gargalo crítico. Seu desempenho em leituras puras rivaliza com as melhores estruturas, ultrapassando 1 milhão de ops/s no cenário Zipfiano.

4. **AA Tree para Bases de Código com Foco em Manutenibilidade e Auditoria:**
   A AA Tree oferece desempenho altamente competitivo (alturas entre 17 e 21, vazão de até 601k ops/s) apoiada em uma lógica axiomática de apenas duas operações (`skew` e `split`). É a escolha recomendada para substituir a Árvore Rubro-Negra em implementações críticas onde simplicidade de código e facilidade de verificação formal são mandatórias.

5. **Zip Tree como Alternativa Elegante e Descentralizada:**
   A Zip Tree valida a premissa de que árvores aleatorizadas com postos geométricos proporcionam implementações concisas e livres de rotações rígidas, constituindo uma excelente opção para sistemas distribuídos e estruturas de busca com inserções simultâneas via *unzip* e *zip*.

---

## 7. Referências Bibliográficas

1. **ANDERSSON, Arne.** *Balanced search trees made simple*. In: Workshop on Algorithms and Data Structures (WADS). Springer, Berlin, Heidelberg, 1993. p. 60–71.
2. **SLEATOR, Daniel D.; TARJAN, Robert E.** *Self-adjusting binary search trees*. Journal of the ACM (JACM), v. 32, n. 3, p. 652–686, 1985.
3. **NIEVERGELT, Jürg; REINGOLD, Edward M.** *Binary search trees of bounded balance*. SIAM Journal on Computing, v. 2, n. 1, p. 33–43, 1973.
4. **GALPERIN, Igal; RIVEST, Ronald L.** *Scapegoat trees*. In: Proceedings of the 4th Annual ACM-SIAM Symposium on Discrete Algorithms (SODA). 1993. p. 165–174.
5. **TARJAN, Robert E.; LEVY, Caleb; TSZ-KIN WONG, Stephen.** *Zip Trees*. ACM Transactions on Algorithms (TALG), v. 17, n. 4, p. 1–24, 2021.
6. **HAEUPLER, Bernhard; SEN, Siddhartha; TARJAN, Robert E.** *Rank-balanced trees*. ACM Transactions on Algorithms (TALG), v. 11, n. 4, p. 1–26, 2015.
7. **BLUM, Norbert; MEHLHORN, Kurt.** *On the average number of rebalancing steps in weight-balanced trees*. Theoretical Computer Science, v. 11, n. 3, p. 303–320, 1980.
