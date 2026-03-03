# Atualizador Automático de Orçamentos (Curva ABC) via API do BCB

**Objetivo:** Automatizar a atualização de custos em tabelas de orçamento da construção civil, tipo curva-ABC, utilizando dados públicos da API do Banco Central do Brasil. 

Este projeto foi desenvolvido com o foco principal de ser **robusto, legível e aplicável a projetos maiores**, garantindo que a base de código possa crescer junto com a complexidade da obra.

## Funcionamento:
Há uma planilha base (tipo Curva-ABC) a ser preenchida pelo usuário que servirá de modelo para a criação de planilha atualizada. A coluna “Custos”, custo atual do orçamento, serve de parâmetro para o calculo do custo atualizado, obtido através do produto entre 1+taxa de variação e o valor inicial.

Os itens preenchidos na tabela devem ser associados ao código fonte como uma das classes de gasto:
* 1. INCC-M Materiais; (concreto armado, aço, cimento, areia etc.) 
* 2. INCC-M Mão de Obra; (mestre de obras, servente, engenheiro etc.)
* 3. INCC-M Serviços; (segurança, pintura etc.)
* 4. INCC-M Geral; (administrativo etc.)
* 5. INCC-M Equipamentos. (EPI, maquinário etc.)

## Como Adaptar e Usar:
Para adicionar novas linhas ou remover existentes é muito simples:
* **Remover linhas:** Basta excluir a linha da planilha (planilha base) e remover sua descrição do dicionário `DE_PARA_INDICES`.
* **Adicionar linhas:** Basta adicionar a linha na planilha base e adicionar sua descrição no dicionário `DE_PARA_INDICES` (“nome”:”Classe de Gastos”).

**Avisos Importantes:** 
* O nome das colunas e outras informações de referência não devem ser alteras para evitar erros na execução do código.
* Não é possível modificar as colunas da planilha base. 
* A planilha gerada pelo script pode ser modificada como bem entender.

## Ferramentas:
Linguagem de programação Python e as bibliotecas pandas(manipular tabelas/dataframe) e requests (requisitar dados de API web).

## ⚠️ Limitações:
* Caso o nome da coluna não esteja na planilha exatamente como consta no código, ocorrerá um erro por não encontrar uma coluna associada à chave.
* A planilha não vem formatada “bonitinha”. Há duas opções: ajustar na mão ou integrar um código que utilize IA para formatar o planilha (disponível no repositório).
* Para itens muito específicos do orçamento não possível obter um índice específico. A solução aplicada é usar o INCC-M Geral.
