"""
Perguntas do Formulario Geral (questionario de diagnostico LGPD)
Extraidas do sistema DataMappingLGPD original para manter fidelidade ao modelo oficial.
"""

PERGUNTAS_FORMGERAL = [
    {"numero": 1, "id": 1, "texto": "A organização acessa, coleta, armazena ou manipula dados pessoais?", "ajuda": "Dados pessoais são dados que possam identificar ou tornar uma pessoa identificável. Ex: Nome, CPF, RG, endereço, número de cartão, IP..."},
    {"numero": 2, "id": 14, "texto": "A organização possui mapeamento de todos os dados pessoais que possui na sua base física e eletrônica?", "ajuda": "Mapeamento: conhecimento dos dados pessoais existentes, como o dado é coletado, como é processado, onde fica o armazenamento, quem tem acesso, com quem é compartilhado, a finalidade do tratamento, quando e como é eliminado."},
    {"numero": 3, "id": 2, "texto": "A organização acessa, coleta, armazena ou manipula dados pessoais sensíveis?", "ajuda": "Dados sensíveis são aqueles que podem causar algum tratamento diferenciado, discriminatório, origem racial ou étnica, religião, opinião política, filiação a sindicato ou organização de caráter religioso, filosófico ou politico, dado referente à saúde ou à vida sexual, dado genético ou biométrico."},
    {"numero": 4, "id": 3, "texto": "A organização realiza a coleta dos consentimentos dos titulares cujo tratamento não se enquadra em outra base legal da LGPD?", "ajuda": ""},
    {"numero": 5, "id": 4, "texto": "A organização possui algum canal direto para reclamação ou pedido de alteração de dados pelos titulares (SAC, 0800...)?", "ajuda": ""},
    {"numero": 6, "id": 5, "texto": "A organização possui uma política de segurança da informação com regras de boas práticas relacionadas a segurança de dados?", "ajuda": ""},
    {"numero": 7, "id": 6, "texto": "A organização treina seus colaboradores acerca dessas boas práticas relacionadas a segurança da informação?", "ajuda": ""},
    {"numero": 8, "id": 7, "texto": "Os padrões de currículo e contrato de trabalho respeitam a LGPD?", "ajuda": ""},
    {"numero": 9, "id": 8, "texto": "A organização compartilha seus dados pessoais com terceiros?", "ajuda": ""},
    {"numero": 10, "id": 9, "texto": "O site institucional da organização coleta dados automaticamente (cookies)?", "ajuda": ""},
    {"numero": 11, "id": 10, "texto": "A organização possui uma política de privacidade referente a todos os dados que coleta?", "ajuda": ""},
    {"numero": 12, "id": 11, "texto": "A organização possui uma política de gestão de risco em caso de incidentes com dados pessoais?", "ajuda": ""},
    {"numero": 13, "id": 12, "texto": "A organização possui um profissional responsável pela segurança da informação (Encarregado/DPO)?", "ajuda": ""},
    {"numero": 14, "id": 13, "texto": "A organização possui uma política de supervisão referente ao cumprimento das boas práticas de segurança da informação adotadas pela empresa?", "ajuda": ""},
    {"numero": 15, "id": 64, "texto": "A organização acessa, coleta, armazena ou manipula dados pessoais de crianças e adolescentes?", "ajuda": ""},
    {"numero": 16, "id": 65, "texto": "O tratamento de dados pessoais inclui a automatização de tomada de decisão, criação de perfis com base em dados transferidos ou utilização analítica?", "ajuda": ""},
    {"numero": 17, "id": 66, "texto": "O tratamento de dados pessoais realizado pela empresa é fundamentado nas bases legais estipuladas na LGPD?", "ajuda": "Consentimento, cumprimento de obrigação legal, execução de políticas públicas, realização de estudo por órgão de pesquisa, execução do contrato, exercício regular do direito, proteção da vida ou incolumidade física, tutela de saúde, legítimo interesse, proteção do crédito."},
    {"numero": 18, "id": 67, "texto": "Os dados sensíveis são tratados com fundamento nas bases legais da LGPD?", "ajuda": "Consentimento, cumprimento de obrigação legal, execução de políticas públicas, realização de estudo por órgão de pesquisa, exercício regular do direito, proteção da vida ou incolumidade física, tutela de saúde, garantia de prevenção à fraude e a segurança do titular."},
    {"numero": 19, "id": 68, "texto": "Os dados pessoais são utilizados apenas para a finalidade objetiva da relação entre as partes?", "ajuda": "Limitado ao fim específico que justifica a coleta dos dados pessoais."},
    {"numero": 20, "id": 69, "texto": "O consentimento para tratamento de dados pessoais é obtido de forma livre e informada e por escrito ou por outro meio apto a provar o consentimento conferido?", "ajuda": ""},
    {"numero": 21, "id": 70, "texto": "Para obtenção do consentimento, a empresa deixa claro ao titular as finalidades para os quais os dados serão tratados?", "ajuda": ""},
    {"numero": 22, "id": 71, "texto": "A organização obtém o consentimento do responsável legal para tratar dados de menores?", "ajuda": ""},
    {"numero": 23, "id": 72, "texto": "A organização tem procedimento para informar o titular dos dados pessoais caso ocorra a alteração da finalidade para tratamento dos dados pessoais?", "ajuda": ""},
    {"numero": 24, "id": 73, "texto": "A organização realiza transferência Internacional de dados pessoais, de acordo com as bases legais da LGPD?", "ajuda": ""},
    {"numero": 25, "id": 74, "texto": "Os países para os quais os dados pessoais são transferidos possuem grau de proteção de dados adequado?", "ajuda": ""},
    {"numero": 26, "id": 75, "texto": "A organização possui política, processos ou mecanismos para que o titular de dados pessoais possa exercer, a qualquer momento e mediante simples requisição, seus direitos previstos na LGPD?", "ajuda": "Acesso, confirmação, retificação, anonimização, eliminação, portabilidade dos dados pessoais e revogação do consentimento."},
    {"numero": 27, "id": 76, "texto": "A organização possui registro das operações de tratamento de dados pessoais, conforme exigido pelo art. 37 da LGPD?", "ajuda": "Operador e controlador devem manter registro das operações de tratamento de dados pessoais que realizem, especialmente quando baseado no legítimo interesse."},
    {"numero": 28, "id": 77, "texto": "Em caso de tratamento de dados que represente risco para os titulares ou no caso de legítimo interesse, a empresa possui relatório de impacto à proteção de dados pessoais?", "ajuda": ""},
    {"numero": 29, "id": 78, "texto": "Os dados pessoais são tratados por prazo determinado, ficando restrito ao período necessário para cumprimento da sua finalidade?", "ajuda": ""},
    {"numero": 30, "id": 79, "texto": "A organização possui política para descarte e eliminação de dados pessoais?", "ajuda": ""},
    {"numero": 31, "id": 81, "texto": "Existe política para evitar ou minimizar o armazenamento de dados pessoais em dispositivos móveis?", "ajuda": ""},
    {"numero": 32, "id": 82, "texto": "A organização possui metodologia de auditoria prévia em relação a privacidade para fins de negociação com terceiros?", "ajuda": ""},
]
