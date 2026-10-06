# Guia do conjunto de dados de Assistência Farmaceutica do DF

> **Finalidade:** documentar as fontes em `DADOS/`, seu estado de revisao e as regras para preparar dados para consulta, banco de dados ou chatbot.
> **Ultima auditoria documental:** 06/10/2026.
> **Estado geral:** nao importar nem usar estes documentos como fonte clinica automatica sem cumprir os criterios de qualidade e revisao deste guia.

## 1. Objetivo e escopo

O diretorio reune informacoes sobre medicamentos padronizados pela SES-DF, servicos de dispensacao, Componente Especializado e fitoterapicos. Este guia define como interpretar, validar, estruturar e atualizar esses materiais.

Os documentos sao fontes informativas, nao substituem avaliacao de profissional de saude, bula, protocolo clinico ou confirmacao diretamente com o servico. A presenca de um medicamento em uma lista nao confirma estoque, elegibilidade individual, indicacao clinica nem disponibilidade imediata.

Este arquivo e um indice e um registro de governanca. As listas detalhadas permanecem em seus documentos de origem; nao devem ser copiadas para ca, pois isso cria versoes divergentes.

## 2. Inventario e estado das fontes

| Arquivo | Conteudo | Fonte de referencia | Estado na auditoria | Condicao para ingestao |
|---|---|---|---|---|
| `01_REME_DF_2025_Medicamentos.md` | Relacao geral REME-DF e subsecoes tematicas | [PDF oficial da REME-DF](https://www.saude.df.gov.br/documents/d/saude/reme-df-2025-com-capa-ascom-versao-final-editada-pdf) | **Bloqueado para importacao automatica.** A sequencia da relacao principal contem 1.048 itens, mas ha forte evidencia de erros de OCR/deslocamento em codigos e descricoes. | Reextrair ou corrigir comparando cada campo com o PDF oficial; revisar candidatos a duplicata e codigos divergentes. |
| `02_HUB_Farmacia_Escola.md` | Programas, orientacoes e dados operacionais do HUB | [Pagina oficial da Farmacia Escola do HUB](https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-centro-oeste/hub-unb/saude/farmacia-escola) | **Revisao necessaria.** Estoque e operacao sao temporarios; na pagina consultada em 06/10/2026, o aviso de falta tinha atualizacao posterior a registrada no arquivo. Elenco e orientacoes clinicas precisam de confirmacao. | Atualizar a partir da pagina oficial; marcar data/hora de captura e validade; validar medicamentos, formulacoes e regras com a equipe/fonte competente. |
| `03_Componente_Especializado_Alto_Custo.md` | Unidades, acesso, cadastro e Medicamento em Casa | [Pagina oficial do CEAF SES-DF](https://www.saude.df.gov.br/componente-especializado) | **Revisao parcial.** A pagina consultada confirma varias informacoes de atendimento, inclusive o aviso de inventario de novembro de 2026. Alguns detalhes documentais, territoriais e de elegibilidade precisam de verificacao especifica. | Vincular cada requisito ao protocolo/formulario vigente; conferir abrangencia regional e distinguir pessoa autorizada de representante legal. |
| `04_Farmacias_Vivas_Fitoterapicos.md` | Formulacoes, unidades produtoras, UBS e alegacoes de uso | [Pagina oficial de Farmacias Vivas SES-DF](https://www.saude.df.gov.br/farmacias-vivas-fitoterapicos) | **Revisao parcial.** A pagina consultada confirma as duas unidades produtoras, as nove formulacoes e orientacao geral de dispensacao; nao confirma todas as indicacoes terapeuticas descritas nem, por si so, toda a lista de UBS. | Conferir indicacoes no guia tecnico oficial vigente e validar a lista de unidades contra o arquivo oficial de UBS dispensadoras. |
| `dados.md` | Indice, regras de qualidade e governanca | Este documento | **Documento de governanca.** | Atualizar junto com cada rodada de auditoria. |

Os estados acima descrevem a triagem documental deste projeto, nao certificacao da SES-DF, da EBSERH ou de profissional clinico. Uma fonte oficial pode mudar depois da captura; guardar sempre a data em que foi consultada.

## 3. Achados conhecidos e fila de revisao

### 3.1 REME-DF

- A relacao principal enumera continuamente os itens de 1 a 1.048. Essa verificacao confirma a sequencia, nao a exatidao dos campos.
- Na auditoria mecanica, 544 celulas de codigo da tabela principal continham uma letra final suspeita de deslocamento. Ha exemplos em que o nome tambem perdeu a letra inicial ou a apresentacao/dose parece truncada. Nao corrigir por regra automatica: validar contra o PDF.
- Foram encontrados 18 grupos de descricoes identicas na relacao principal. Muitos pares parecem distinguir componente ou local de dispensacao e podem ser registros legitimos. Albumina humana nos itens 33 e 34 e candidato forte a duplicata, pois descricao, grupo e local coincidem. Exigir decisao humana antes de unir ou excluir.
- Ha divergencia interna a verificar para suxametonio: codigo `90230` na relacao geral e `230` em carros de emergencia.
- Algumas celulas nas subsecoes de compra eventual e carros de emergencia terminam com texto aparentemente truncado. Confirmar descricao e apresentacao no documento oficial.
- As subsecoes repetem medicamentos da relacao geral por finalidade. Essa repeticao entre secoes e contextual, nao e duplicata para eliminar sem preservar a secao e o uso.

### 3.2 Farmacia Escola HUB

- O arquivo tem verificacao registrada em 01/10/2026 e alerta da unidade datado de 11/09/2026. A pagina oficial consultada em 06/10/2026 apresentava aviso de falta atualizado em 06/10 e incluia insulina ultrarrapida, item ausente daquele alerta no arquivo. Reconsultar antes de publicar qualquer status de disponibilidade.
- A relacao de antirretrovirais e esquemas precisa de confirmacao de atualidade e de disponibilidade no HUB; nao apresentar automaticamente todos os itens como dispensados atualmente.
- Regras gerais sobre antimicrobianos, conservacao de produtos, validade de receitas e controle de talidomida precisam de referencia normativa/produto especifica e revisao tecnica.
- O caminho de automacao citado no final do arquivo e um caminho pessoal local. Nao e uma dependencia reproduzivel do repositorio; documentar uma rotina portavel se ela for mantida.

### 3.3 CEAF

- A pagina oficial consultada confirma informacoes centrais de atendimento, cadastro remoto, telefone, unidades e o fechamento para inventario anunciado para 09 e 10/11/2026, com retomada em 11/11/2026. Avisos com data devem expirar apos o periodo informado.
- A pagina consultada descreve ate quatro pessoas autorizadas a receber entrega domiciliar; o arquivo as chama de representantes legais. Confirmar e alinhar a terminologia antes de estruturar esse campo.
- Validade da LME, documentos, abrangencia territorial e excecoes de atendimento devem ser ligados ao protocolo, formulario ou orientacao oficial vigente. Nao assumir que um requisito e universal quando pode depender da condicao ou medicamento.

### 3.4 Farmacias Vivas

- A pagina oficial consultada confirma as nove formulacoes e as duas unidades produtoras. As alegacoes detalhadas de indicacao, eficacia, potencia, sintomas ou condicoes nao ficam validadas apenas por essa confirmacao.
- A lista de UBS deve ser verificada contra o documento oficial de unidades dispensadoras, com data de publicacao/consulta registrada. Enderecos parecidos, como UBS 5 e UBS 6 Taguatinga, sao candidatos para conferencia, nao duplicatas confirmadas.
- Prescritores habilitados, restricoes, contraindicacoes e modo de uso exigem fonte normativa ou guia clinico oficial. Nao converter texto promocional/descritivo em conselho individual.

## 4. Modelo recomendado para o banco

Separar entidades diferentes. Evitar uma tabela unica que misture catalogo de produtos, estoque temporario, enderecos e orientacao clinica.

### 4.1 Fonte e versao

| Campo | Uso |
|---|---|
| `source_id` | Identificador estavel da fonte/documento. |
| `source_title` | Titulo publicado pela instituicao. |
| `source_url` | URL oficial consultada. |
| `source_version` | Edicao, numero de versao ou data declarada pela fonte. |
| `captured_at` | Data/hora em que o conteudo foi obtido. |
| `valid_from`, `valid_until` | Periodo de validade conhecido; usar nulo quando desconhecido, nunca inventar. |
| `review_status` | `pending`, `verified`, `rejected` ou `superseded`. |
| `reviewed_by`, `reviewed_at` | Responsavel e data da revisao humana. |
| `source_locator` | Pagina, secao, item, tabela ou URL especifica que sustenta o registro. |

### 4.2 Medicamento e apresentacao

Campos sugeridos: `ingredient_name_original`, `ingredient_name_normalized`, `description_original`, `dosage_form`, `strength_value`, `strength_unit`, `packaging`, `route` (somente se a fonte informar), `ses_code_original`, `component`, `program`, `dispensing_location`, `eligibility_text`, `cid_codes` e `source_id`.

Preservar sempre os valores originais. Campos normalizados sao derivados e devem poder ser rastreados ate a fonte. Nao inferir principio ativo, dose, unidade, via, CID ou elegibilidade a partir de conhecimento externo sem registrar uma fonte apropriada.

### 4.3 Disponibilidade e servicos

Estoque, falta, horario, fechamento e forma de atendimento devem ser registros temporais independentes: `service_id`, `status`, `details`, `captured_at`, `valid_from`, `valid_until`, `source_id` e `source_locator`. Um aviso sem prazo conhecido deve ser marcado como validade desconhecida e precisa de reconsulta antes de ser apresentado como atual.

### 4.4 Indicacoes e conteudo clinico

Armazenar alegacoes clinicas separadamente do catalogo administrativo. Cada alegacao deve conter texto, populacao/contexto, tipo de afirmacao (indicacao, contraindicacao, interacao, dose, armazenamento etc.), fonte clinica/normativa, versao/data, trecho de suporte e estado de revisao por pessoa qualificada. Sem esses elementos, nao usar para gerar recomendacao clinica.

## 5. Identificadores, duplicatas e valores ausentes

- Nao usar o numero sequencial `Item` como chave unica: ele reinicia em cada secao.
- Uma chave de registro de origem pode combinar `source_id + section_id + item_number`. O codigo SES deve ser guardado como valor de origem e validado, nao presumido globalmente unico.
- Nao remover registros apenas porque principio ativo ou descricao coincidem. Comparar codigo, apresentacao, concentracao, componente, programa, local e vigencia.
- Registrar duplicatas como candidatos com motivo e decisao humana: `duplicate_candidate`, `duplicate_of`, `decision`, `reviewer` e `reviewed_at`.
- Diferenciar campo ausente, nao aplicavel, desconhecido e explicitamente nao informado. Nao preencher com zero, texto presumido ou valor deduzido.
- Em conflitos entre fontes, guardar ambas as afirmacoes, as datas e as fontes; nao escolher silenciosamente uma delas.

## 6. Pipeline de preparacao

1. Guardar uma copia imutavel da fonte original e seus metadados de captura.
2. Extrair registros preservando secao, item, pagina/trecho e texto original.
3. Validar colunas, tipos, codigos, unidades, numeros de itens e campos obrigatorios.
4. Sinalizar OCR, truncamentos, valores fora do padrao e repeticoes para revisao humana.
5. Comparar campos clinicamente ou operacionalmente sensiveis diretamente com a fonte oficial.
6. Registrar cada correcao como valor original, valor proposto, justificativa, fonte e revisor; nao sobrescrever a origem.
7. Publicar apenas registros aprovados para o uso pretendido, com versao e data de validade.
8. Reexecutar validacoes apos cada atualizacao e manter historico de alteracoes.

Validacoes minimas para catalogos: codigo preservado como texto; concentracao separada de unidade; apresentacao nao vazia; secao e fonte obrigatorias; codigos suspeitos, descricoes truncadas e duplicatas candidatas em fila de revisao. Para avisos, exigir data de captura e verificar vencimento antes de responder.

## 7. Uso em busca ou chatbot

- Preferir recuperacao de trechos das fontes (RAG) com citacao da instituicao, secao e data, em vez de treinar o modelo para memorizar horarios, estoques ou regras que mudam.
- Responder sobre dispensacao somente com registros aprovados e vigentes; dizer quando a fonte nao informa algo e encaminhar para o canal oficial.
- Distinguir claramente “padronizado”, “dispensado neste servico”, “em falta na data X” e “estoque confirmado agora”. Sao afirmacoes diferentes.
- Nao recomendar inicio, interrupcao, substituicao, dose ou combinacao de medicamentos. Nao diagnosticar nem extrapolar indicacoes de fitoterapicos.
- Para casos urgentes, efeitos adversos, gestacao, criancas ou duvida individual de tratamento, orientar contato com profissional/servico de saude adequado; nao improvisar uma conduta.
- Nao enviar dados pessoais ou dados de pacientes para treinamento. Os documentos atuais devem permanecer sem dados identificaveis de usuarios.
- Antes de distribuir ou treinar modelos com conteudo de terceiros, verificar licencas, termos de uso, atribuicao e autorizacao aplicaveis. A licenca do repositorio nao deve ser presumida como licenca das fontes oficiais.

## 8. Atualizacao e governanca

Manter um responsavel pela revisao de cada fonte. A cadencia deve refletir o tipo de dado: alertas de estoque e fechamento exigem consulta na data da resposta; horarios, unidades e regras de acesso exigem revalidacao periodica; catalogos e protocolos devem seguir a edicao oficial vigente.

Para cada rodada, registrar: URL consultada, data/hora, versao publicada, arquivos alterados, diferencas encontradas, itens aprovados/rejeitados, responsavel e proxima revisao. Nao alterar silenciosamente um dado publicado.

## 9. Criterios para liberar dados

Um arquivo ou conjunto de registros so deve ser marcado como pronto para uso quando:

- a fonte e a versao estao identificadas e acessiveis;
- campos estruturados foram comparados com a fonte original;
- codigos, doses, unidades e apresentacoes passaram por revisao adequada ao risco;
- duplicatas candidatas e conflitos possuem decisao registrada;
- informacoes temporarias possuem data, validade ou regra explicita de reconsulta;
- afirmacoes clinicas possuem fonte clinica/normativa e revisao qualificada;
- os testes de importacao e validacao passaram;
- o consumidor (banco, busca ou chatbot) consegue exibir proveniencia e incerteza.

**Estado atual de liberacao:** os documentos deste diretorio sao uteis como material de triagem, mas a REME transcrita ainda requer validacao contra o PDF, e os conteudos operacionais/clinicos dos arquivos tematicos devem ser consumidos com os estados e ressalvas registrados acima.

