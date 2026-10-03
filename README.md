# Otimização e Avaliação de Prompts com LangChain e LangSmith

## 1. Objetivo

Este projeto tem como objetivo otimizar um prompt responsável por transformar relatos de bugs em User Stories claras, testáveis e úteis para times de produto e engenharia.

O processo foi realizado de forma iterativa utilizando:

- LangChain para execução dos prompts;
- LangSmith Prompt Hub para versionamento e publicação;
- LangSmith para tracing e avaliação;
- um dataset com 15 relatos de bugs;
- diferentes modelos de linguagem para comparação de desempenho.

O critério de aprovação exige que todas as métricas sejam individualmente iguais ou superiores a `0.8`.

As métricas utilizadas são:

- Helpfulness;
- Correctness;
- F1-Score;
- Clarity;
- Precision.

---

## 2. Fluxo da Solução

O processo de avaliação segue o seguinte fluxo:

```text
Bug Report
    ↓
Prompt otimizado
    ↓
Modelo principal
    ↓
User Story gerada
    ↓
Comparação com a resposta de referência
    ↓
Avaliação das métricas
    ↓
Registro do experimento no LangSmith
```

O dataset possui 15 casos, incluindo cenários simples, médios e complexos.

---

## 3. Prompt Inicial

O prompt inicial apresentava uma estrutura bastante simples e foi utilizado como baseline.

Os principais problemas identificados foram:

- ausência de persona especializada;
- instruções genéricas;
- ausência de exemplos Few-shot;
- formato de saída pouco definido;
- falta de regras para critérios de aceitação;
- ausência de tratamento de casos complexos;
- pouca orientação sobre contexto técnico;
- duplicação do `bug_report` entre System Prompt e User Prompt.

A partir dessa análise foi criada uma versão otimizada.

---

## 4. Técnicas de Prompt Engineering

### Few-shot Learning

Foram adicionados exemplos completos de entrada e saída para demonstrar ao modelo o formato e o nível de detalhamento esperado.

Os exemplos mostram:

- como escrever a User Story;
- como construir critérios de aceitação;
- quando incluir contexto técnico;
- como lidar com bugs de diferentes níveis de complexidade.

### Role Prompting

O modelo passou a assumir o papel de:

> Product Manager experiente em transformar relatos de bugs em User Stories claras, testáveis e úteis para times de produto e engenharia.

O objetivo foi orientar o modelo para uma perspectiva funcional e de produto.

### Skeleton of Thought

Foi definida uma sequência estruturada para análise do problema antes da geração da resposta.

O modelo deve considerar:

1. usuário ou sistema afetado;
2. problema principal;
3. impacto;
4. condições e detalhes técnicos;
5. comportamento esperado;
6. critérios de aceitação;
7. complexidade do caso.

### Chain of Thought

Também foi adicionada uma instrução para que o modelo analise internamente o problema passo a passo antes de gerar a resposta final.

O raciocínio não é exibido na saída.

Essa técnica foi utilizada para reduzir omissões e melhorar a cobertura das informações relevantes.

---

## 5. Métricas

As métricas base utilizadas na avaliação são:

- F1-Score;
- Clarity;
- Precision.

Duas métricas adicionais são derivadas pelo próprio código:

```text
Helpfulness = (Clarity + Precision) / 2

Correctness = (F1 + Precision) / 2
```

O principal desafio durante a otimização foi o **F1-Score**, que permaneceu abaixo de `0.8` durante várias iterações.

---

## 6. Jornada de Otimização

### Visão Geral

A jornada de otimização foi dividida em duas etapas:

1. **Otimização do prompt**, evoluindo da V1.0 até a V2.5.
2. **Benchmark de modelos**, mantendo o prompt V2.5 fixo e alterando apenas o modelo principal.

Essa segunda etapa foi decisiva para alcançar a aprovação, pois a V2.5 ainda apresentava F1 abaixo de `0.8` com o modelo original.

| Etapa | Versão / Modelo | Helpfulness | Correctness | F1 | Clarity | Precision | Média | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Prompt | V1.0 | 0.84 | 0.78 | 0.73 | 0.86 | 0.83 | 0.8094 | Reprovado |
| Prompt | V2.1 | 0.87 | 0.80 | 0.75 | 0.88 | 0.85 | 0.8311 | Reprovado |
| Prompt | V2.2 | 0.85 | 0.78 | 0.75 | 0.89 | 0.82 | 0.8181 | Reprovado |
| Prompt | V2.3 | 0.86 | 0.78 | 0.73 | 0.87 | 0.84 | 0.8150 | Reprovado |
| Prompt | V2.4 | 0.87 | 0.79 | 0.74 | 0.88 | 0.85 | 0.8256 | Reprovado |
| Prompt | V2.5 + GPT-4o-mini | 0.88 | 0.82 | 0.78 | 0.90 | 0.86 | 0.8465 | Reprovado |
| Modelo | V2.5 + GPT-5.6 Luna | 0.87 | 0.83 | 0.81 | 0.89 | 0.86 | 0.8505 | **Aprovado** |
| Modelo | V2.5 + GPT-5.6 Terra | 0.86 | 0.82 | 0.80 | 0.88 | 0.83 | 0.8381 | **Aprovado** |
| Modelo | V2.5 + GPT-5.5 | 0.89 | 0.85 | 0.81 | 0.89 | 0.89 | 0.8636 | **Aprovado** |
| Modelo | **V2.5 + Gemini 2.5 Flash** | 0.88 | 0.85 | **0.82** | 0.89 | 0.88 | **0.8645** | **Aprovado** |

A primeira aprovação ocorreu ao manter o prompt V2.5 e substituir o modelo principal pelo **GPT-5.6 Luna**, elevando o F1 de `0.78` para `0.81`.

Em seguida, outros modelos foram avaliados com o mesmo prompt e o mesmo dataset. O melhor resultado final foi obtido com **Gemini 2.5 Flash**, que alcançou F1 `0.82` e média geral `0.8645`.

### V1.0 — Baseline

A primeira avaliação apresentou:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.84 | 0.78 | 0.73 | 0.86 | 0.83 | 0.8094 |

Apesar da média estar acima de `0.8`, Correctness e F1 ficaram abaixo do limite mínimo.

O principal problema identificado foi a baixa cobertura dos elementos esperados pelas respostas de referência.

### V2.1 — Estrutura e técnicas iniciais

Foram adicionados:

- Role Prompting;
- Few-shot Learning;
- estrutura de saída;
- critérios de aceitação mais claros;
- Skeleton of Thought.

Resultado:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.87 | 0.80 | 0.75 | 0.88 | 0.85 | 0.8311 |

Houve melhora geral, mas o F1 permaneceu abaixo do mínimo.

### V2.2 — Restrição de inferências

A hipótese foi que o modelo poderia estar adicionando informações demais.

Foram adicionadas regras para evitar:

- funcionalidades não solicitadas;
- mensagens inventadas;
- valores não informados;
- causas técnicas não confirmadas;
- requisitos sem sustentação.

Resultado:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.85 | 0.78 | 0.75 | 0.89 | 0.82 | 0.8181 |

A estratégia não melhorou o F1 e reduziu outras métricas.

**Aprendizado:** restringir excessivamente as inferências deixou o modelo conservador demais para o comportamento esperado pelo dataset.

### V2.3 — Inferência controlada

A estratégia foi alterada para permitir inferências razoáveis quando fossem consequência natural do problema.

Resultado:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.86 | 0.78 | 0.73 | 0.87 | 0.84 | 0.8150 |

O F1 caiu novamente.

**Aprendizado:** regras genéricas de inferência não eram suficientes. Era necessário entender melhor o padrão das respostas de referência.

### V2.4 — Chain of Thought

Foi adicionada uma análise interna passo a passo antes da geração da resposta.

O modelo passou a analisar:

1. usuário afetado;
2. problema;
3. impacto;
4. condições;
5. detalhes técnicos;
6. comportamento esperado;
7. possíveis omissões.

Resultado:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.87 | 0.79 | 0.74 | 0.88 | 0.85 | 0.8256 |

Houve uma melhora pequena, porém consistente.


### Etapa de Benchmark de Modelos

Após concluir a otimização do prompt na V2.5, nenhuma nova alteração foi feita no conteúdo do prompt.

O objetivo passou a ser verificar se a escolha do modelo principal poderia melhorar a aderência ao ground truth sem alterar a estratégia de Prompt Engineering.

A sequência de testes foi:

| Modelo | Helpfulness | Correctness | F1 | Clarity | Precision | Média | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| GPT-4o-mini | 0.88 | 0.82 | 0.78 | 0.90 | 0.86 | 0.8465 | Reprovado |
| GPT-5.6 Luna | 0.87 | 0.83 | 0.81 | 0.89 | 0.86 | 0.8505 | **Aprovado** |
| GPT-5.6 Terra | 0.86 | 0.82 | 0.80 | 0.88 | 0.83 | 0.8381 | **Aprovado** |
| GPT-5.5 | 0.89 | 0.85 | 0.81 | 0.89 | 0.89 | 0.8636 | **Aprovado** |
| **Gemini 2.5 Flash** | 0.88 | 0.85 | **0.82** | 0.89 | 0.88 | **0.8645** | **Aprovado** |

Essa etapa demonstrou que a aprovação não veio apenas da evolução do prompt. A V2.5 melhorou significativamente a qualidade, mas ainda ficou abaixo do limite mínimo de F1 com GPT-4o-mini.

A troca do modelo principal foi o fator que permitiu ultrapassar o limite de `0.8` em todas as métricas.

O **Gemini 2.5 Flash** foi escolhido como configuração final por apresentar a maior média geral e o maior F1 entre os modelos testados.


---

## 7. Análise dos Traces

A análise dos exemplos individuais no LangSmith foi essencial para identificar por que o F1 permanecia baixo.

Alguns casos demonstraram que a resposta de referência esperava mais do que uma simples transformação literal do bug.

### Webhook de pagamento

Além da correção do webhook, a referência esperava elementos como:

- retorno HTTP adequado;
- atualização do status do pedido;
- logging;
- confirmação ao usuário.

### Carrinho sem estoque

A referência esperava:

- validação do estoque;
- bloqueio do checkout;
- mensagem de indisponibilidade;
- tratamento de concorrência;
- prevenção da criação de pedidos inválidos.

### Relatórios gerenciais

Os casos complexos esperavam critérios relacionados a:

- performance;
- consistência dos dados;
- cache;
- exportação;
- impacto de negócio;
- contexto técnico.

### Conclusão

O dataset não recompensava apenas fidelidade literal.

Ele esperava também requisitos complementares plausíveis e coerentes com o contexto.

---

## 8. V2.5 — Adaptação à complexidade

A principal mudança da V2.5 foi adaptar a profundidade da resposta à complexidade do bug.

O prompt passou a considerar três níveis:

```text
Caso simples
→ User Story
→ poucos critérios objetivos

Caso médio
→ User Story
→ critérios
→ contexto técnico
→ requisitos adicionais coerentes

Caso complexo
→ User Story principal
→ critérios por problema
→ contexto técnico detalhado
→ impacto
→ sugestões técnicas plausíveis
```

Também foram adicionadas orientações específicas para:

- integração;
- performance;
- segurança;
- regras de negócio.

Resultado:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.88 | 0.82 | 0.78 | 0.90 | 0.86 | 0.8465 |

Foi o maior ganho obtido apenas através da otimização do prompt.

O F1 passou de `0.74` para `0.78`.

---

## 9. Avaliação de Diferentes Modelos

Após atingir a versão V2.5, o prompt foi mantido sem alterações.

A partir desse momento, apenas o modelo principal foi alterado.

Isso permitiu avaliar o impacto do modelo mantendo:

- mesmo prompt;
- mesmo dataset;
- mesmos 15 exemplos;
- mesmo modelo avaliador (`gpt-4o`);
- mesma metodologia.

### Resultado do Benchmark

| Modelo | Helpfulness | Correctness | F1 | Clarity | Precision | Média | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| GPT-4o-mini | 0.88 | 0.82 | 0.78 | **0.90** | 0.86 | 0.8465 | Reprovado |
| GPT-5.6 Luna | 0.87 | 0.83 | 0.81 | 0.89 | 0.86 | 0.8505 | Aprovado |
| GPT-5.6 Terra | 0.86 | 0.82 | 0.80 | 0.88 | 0.83 | 0.8381 | Aprovado |
| GPT-5.5 | **0.89** | **0.85** | 0.81 | 0.89 | **0.89** | 0.8636 | Aprovado |
| **Gemini 2.5 Flash** | 0.88 | **0.85** | **0.82** | 0.89 | 0.88 | **0.8645** | **Aprovado** |

---

## 10. Comparação de Tempo

Também foi observado o tempo total aproximado de execução dos 15 exemplos.

| Modelo | Tempo aproximado |
|---|---:|
| Gemini 2.5 Flash | **3m16s** |
| GPT-5.6 Luna | 3m24s |
| GPT-5.6 Terra | 3m25s |
| GPT-5.5 | 3m45s |

A velocidade foi considerada um critério complementar.

O objetivo principal continuou sendo a qualidade das respostas e o atendimento às métricas mínimas.

---

## 11. Escolha do Modelo Final

O modelo selecionado foi:

### Gemini 2.5 Flash

Resultado final:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.88 | 0.85 | **0.82** | 0.89 | 0.88 | **0.8645** |

**Status: APROVADO**

O Gemini 2.5 Flash foi escolhido porque apresentou:

- maior média geral do benchmark;
- maior F1-Score;
- todas as métricas acima de `0.8`;
- tempo total inferior aos principais modelos finalistas.

Embora o GPT-5.5 tenha apresentado Helpfulness e Precision ligeiramente superiores, o Gemini obteve melhor F1 e maior média geral.

A diferença entre os dois melhores resultados foi pequena:

| Modelo | F1 | Precision | Média |
|---|---:|---:|---:|
| **Gemini 2.5 Flash** | **0.82** | 0.88 | **0.8645** |
| GPT-5.5 | 0.81 | **0.89** | 0.8636 |

Para este dataset e este caso de uso, o Gemini 2.5 Flash apresentou o melhor equilíbrio entre qualidade e tempo de execução.

---

## 12. Principais Aprendizados

1. **A média geral não é suficiente.** Uma única métrica abaixo de `0.8` reprova a execução.
2. **F1 foi o principal gargalo.** O prompt inicialmente produzia respostas claras, mas não cobria todos os elementos esperados.
3. **Restringir demais o modelo pode prejudicar o resultado.** Proibir qualquer inferência reduziu a cobertura das respostas.
4. **Analisar os traces foi fundamental.** Os casos individuais mostraram quais informações estavam sendo omitidas.
5. **A complexidade do bug deve influenciar a profundidade da resposta.**
6. **Prompt e modelo influenciam o resultado.**
7. **O modelo mais caro ou mais robusto não necessariamente é o melhor para um caso específico.**

---

## 13. Evidências no LangSmith

Os experimentos foram registrados no LangSmith durante todo o processo.

As evidências utilizadas no projeto incluem:

- dataset com 15 exemplos;
- histórico das diferentes execuções;
- métricas de cada experimento;
- comparação entre modelos;
- tracing detalhado dos exemplos;
- execução final aprovada.

### Evidência pública

A evidência pública do dataset e das execuções pode ser acessada em:

[LangSmith - Evidência Pública](https://smith.langchain.com/public/775e228f-5fb0-488e-a701-8a0cb923c9f2/d)

Experimento final com Gemini 2.5 Flash:

```text
bug_to_user_story_v2-evaluation-685b4feb
```

Resultado final:

| Helpfulness | Correctness | F1 | Clarity | Precision | Média |
|---:|---:|---:|---:|---:|---:|
| 0.88 | 0.85 | 0.82 | 0.89 | 0.88 | 0.8645 |

---

## 14. Configuração Final

```text
Prompt: albertocbranco/bug_to_user_story_v2
Versão: V2.5

Modelo principal:
Gemini 2.5 Flash

Modelo avaliador:
GPT-4o

Dataset:
15 exemplos

Resultado:
APROVADO
```

---

## 15. Conclusão

O processo começou com um prompt simples e um F1 de `0.73`.

Após diferentes hipóteses, análise dos resultados e refinamento das técnicas de Prompt Engineering, a versão V2.5 elevou o F1 para `0.78` utilizando o modelo original.

A etapa seguinte demonstrou que a escolha do modelo também era relevante.

O mesmo prompt V2.5 foi avaliado em diferentes modelos e alcançou seu melhor resultado com o **Gemini 2.5 Flash**:

| F1 inicial | F1 final | Média final |
|---:|---:|---:|
| 0.73 | **0.82** | **0.8645** |

A configuração final superou o limite mínimo em todas as métricas e demonstrou a importância de combinar:

**Prompt Engineering + Avaliação + Tracing + Iteração + Benchmark de modelos**
