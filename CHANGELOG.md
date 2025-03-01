# CHANGELOG

## 4.8.0

Melhorias:

- Adicionada a opção de suprimir o formulário de feição no modo reclassificação do menu de aquisição (particularmente útil quando se está corrigindo flags de áreas sem centroide na construção de polígonos utilizando linha e centroide);

## 4.7.1 - 2023-05-10

Correção de bug:

- Correção de bug no menu (filtro de geometria estava quebrado);

## 4.7.0 - 2023-05-09

Novas funcionalidades:

- Novo processo de selecionar feições no canvas de camadas selecionadas;
- Novo processo de filtrar lista de camadas no processing por tipo geométrico;
- Novo processo de remover holes pequenos de camadas de cobertura;
- Novo processo de dissolver polígonos para vizinhos (heurística pelo maior comprimento da intersecção);
- Novo processo de construir grid de pontos dentro de polígonos;
- Novo processo de dividir polígonos;
- Novo processo de dividir polígonos por grid;
- Novo processo de selecionar por DE9IM;
- Novo processo de extrair feições por DE9IM;
- Processo de converter linha para multilinha portado do ferramentas experimentais;

Melhorias:

- Adicionada a opção de dar pan na barra de ferramentas de revisão;
- Adicionada mudanca de ferramenta atual nos icones das ferramentas de filtro;
- Processing de construção do diagrama de elevação portado para o Ferramentas de Edição;
- Adicionado o comportamento no seletor genérico de selecionar somente na camada ativa quando a tecla Alt estiver selecionada;
- Adicionada a opção de rodar a construção de polígonos por polígono de área geográfica (por MI);
- Melhoria de desempenho na construção de polígonos (adicionado paralelismo em thread);
- Melhoria de desempenho na verificação de delimitadores não utilizados no processo de construção de polígonos;
- Adicionada a opção de verificar ou não delimitadores não utilizados no processo de construção de polígonos;
- Melhoria de desempenho na identificação de erros de construção do terreno (roda em thread por área geográfica);
- A ferramenta de verificação de erros de relacionamentos espaciais agora permite regras com de9im e relacionamentos espaciais simultaneamente;
- Adicionada a opção de desligar todas as imagens ativas na ferramenta de seleção de raster;
- Adicionado o id da geometria na flag do identificar geometrias inválidas;
- O menu de aquisição agora permite reclassificação de polígono para ponto (particularmente útil quando se está corrigindo flags de áreas sem centroide na construção de polígonos utilizando linha e centroide);

Correção de bug:

- Corrigido o bug de sempre apontar flags quando a geometria tem buraco do processo de identificar geometrias com densidade incorreta de vértices;
- Correção de bug no processo de adicionar vértice em segmento compartilhado;
- Correção de bug no processo de dissolver polígonos com mesmo conjunto de atributos quando é passada uma área mínima para o dissolve;
- Correção de bug no acesso ao BDGEx (a url do serviço mudou e o código teve de ser atualizado, mudando a url do serviço de https para http);

## 4.6.0 - 2022-12-19

Novas funcionalidades:

- Novo processo de estender linhas próximas da moldura;
- Novo algoritmo de detecção de geometrias nulas;
- Novo processo de adicionar vértices não compartilhados nas intersecções (processo de correção associado ao processo de Identificar vértices não compartilhados na intersecção);
- Novo processo de adicionar vértices não compartilhados nos segmentos compartilhados (processo de correção associado ao processo de Identificar vértices não compartilhados nos segmentos compartilhados);
- Adicionada integração da Ferramenta de Controle de Qualidade (QA Toolbox) com o Ferramentas de Produção. Dessa forma, a QA Toolbox pode ser integrada à produção utilizando o Sistema de Apoio à Produção;
- Nova funcionalidade de adicionar filtro espacial às camadas (portado do ferramentas experimentais);
- Nova funcionalidade de filtrar por selecionados (portado do ferramentas experimentais);
- Nova funcionalidade de filtrar todos por geometria de selecionados (portado do ferramentas experimentais);
- Nova funcionalidade de remover filtros (portado do ferramentas experimentais);
- Nova funcionalidade de copiar geometrias selecionadas como WKT (portado do ferramentas experimentais);

Melhorias:

- Adicionada a opção de atribuir um id de atividade para o grid de revisão criado no processo de criar grid de edição;
- Melhorado o estilo do grid utilizado pela barra de ferramentas de revisão;
- Adicionada a funcionalidade de resetar o grid na barra ferramentas de revisão;
- Adicionado o caso de snap dentro da camada no snap hierárquico. Agora para cada camada de entrada, primeiramente é feito o snap dentro da camada de referência antes de atrair os elementos com hierarquia menor;
- Barra de atalhos refatorada. Alguns atalhos não utilizados frequentemente foram retirados e foram criadas novas barras para dar a opção do usuário escolher quais ele quer ativar.

Correção de bug:

- Correção de bug no identificar pontas soltas (o algoritmo estava levantando flag em vértice ocupado dentro do raio de busca);
- Correção de bug no identificar erros no terreno (o algoritmo estava levantando a geometria da flag confusa);
- Correção de crash ao rodar o snap hierárquico (o algoritmo agora só transmite as mudanças para o banco ao final do processo, mantendo os cálculos intermediários em camada de cache gravadas em camada temporária do processing do QGIS, ativado por meio da flag is_child_algorithm=True ao rodar o processo);

## 4.5.0 - 2022-09-08

Novas funcionalidades:

- Novo processo de identificar undershoot de polígonos;
- Novo processo de identificar erros de construção de redes (linhas que compartilham vértices não segmentadas dentro da camada, linhas não segmentadas com as camadas de filtro);
- Novo processo de identificar linhas com mesmo conjunto de atributos não unidas;
- Novo processo de carregamento de primeira camada com elemento de um csv (utilizado na construção de modelos);
- Novo processo de identificação de problemas no fluxo de drenagens;
- Novo processo de construir fatiamento do terreno segundo as regras do MTM;
- Novo processo de ativar a remoção automática de vértices nas camadas;
- Novo processo de bloquear a edição de atributos;
- Novo processo de identificar loops em drenagens;
- Novo processo de identificar problemas de direcionamento com elementos da rede (massas d'água com e sem fluxo, oceano, vala, sumidouro e vertedouro);
- Novo processo de identificar problemas nos ângulos entre os trechos de drenagem (verificar deltas);
- Nova barra de ferramentas de revisão;
- Novo processo de construir grid de revisão;

Melhorias:

- Melhoria de desempenho no identificar Z;
- Melhoria de desempenho no identificar geometrias inválidas;
- Melhoria de desempenho no identificar dangles;
- Melhoria no processo de validação do terreno (removidos os falso-positivos com a moldura);

Correção de bug:

- Tratamento de geometria nula no Identify Out Of Bounds Angles in Coverage;

## 4.4.0 - 2022-07-12

Novas funcionalidades:

- Nova ferramenta de alternar visibilidade de raster;
- Novo processo de remover camadas vazias do projeto (portado do Ferramentas Experimentais);
- Novo processo de identificar vértices duplicados;
- Novo processo de identificar feições com densidade alta de vértices;

Melhorias:

- Refatoração da interface de carregamento de camadas (remoção de funcionalidades não utilizadas e melhoria no filtro de camadas);
- Adicionadas flags de delimitador não utilizado no algoritmo Construir Polígonos com Delimitadores e Centroides;
- Adicionada a opção de verificar geometrias inválidas nos polígonos montados no algoritmo Construir Polígonos com Delimitadores e Centroides;
- Adicionada a opção de unir os polígonos com mesmo conjunto de atributos na saída do Construir Polígonos com Delimitadores e Centroides;
- Adicionado botão de mudar camada da barra de inspeção de raster pela camada ativa;
- Ferramenta de controle de qualidade agora agrupa as camadas carregadas em grupos;
- Ferramenta de contole de qualidade agora diferencia camadas carregadas nos processos de flags, por meio de parâmetro de configuração;
- Adicionada a opção de ignorar feições circulares no processo de identificar ângulos errados em edificações;
- Refatorado o processo de atribuir regras de atributação ao formulário de feições;
- Refatorado o processo de identificar overlaps. Agora ele também pega overlaps de linhas;
- Adicionada a opção de ordenar no inspetor de feições por um atributo;

Correção de Bug:

- Filtro de expressão do inspetor de feições agora é limpo quando o botão de trocar para a camada ativa é acionado;
- Corrigido o bug da ferramenta de aliases retirando os mapas de valores;

## 4.3.2 - 2022-05-30

Correção de bugs:

- Correção do proxy para os serviços https do BDGEx

## 4.3.1 - 2022-05-30

Novas funcionalidades:

- Adicionado processo de verificação de caracteres unicode;
- Adicionados parâmetros de densidade de pontos na criação de molduras;
- Adicionados novos casos no processo de identificação de geometrias inválidas (buraco intersectando fronteira de polígono);

Correção de bugs:

- Correção no template da EDGV 3.0;
- Correção nos endereços do BDGEx;
- Correção na janela de opções do DSGTools;
- Ajustado o número de casas decimais no snap hierárquico;
- Corrigido bug na SQL de filtragem do carregamento de camadas com elementos quando se utiliza o postgres mais novo;

## 4.3.0 - 2022-01-20

Novas funcionalidades:

- Novo menu de classificação

Novos algoritmos:

- Corretor ortográfico
- Verifica o UUID das feições
- Verifica a sobreposição de curvas de nível
- Identifica pequenos buracos
- Identifica interseções entre curvas de nível e linhas de drenagem
- Carrega um shapefile

Melhorias:

- Adequação dos processings de camadas para ser compatível com o SAP
- Compatibilidade com QGIS 3.22

Correção de bugs:

- Ferramenta de inspeção de feições, agora mostra a aproximação correta quando utilizado em linha ou áreas em latlong com porcentagem inferior a 100%
- O problema onde a Ferramenta de Aquisição com Ângulos Retos e a Ferramenta de Aquisição à Mão Livre não atribuíam os valores padrões nos formulários da feição foi corrigido
- Correção nos processings de geração de MI: remover MI que não existem

Changelog completo: <https://github.com/dsgoficial/DsgTools/wiki/Changelog-4.3>
