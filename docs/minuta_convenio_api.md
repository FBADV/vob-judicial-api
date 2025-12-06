# MINUTA DE TERMO DE CONVÊNIO DE COOPERAÇÃO TÉCNICA

**PROCESSO ADMINISTRATIVO Nº:** [NÚMERO]
**PARTÍCIPES**: TRIBUNAL DE JUSTIÇA DO ESTADO DE [ESTADO] e [NOME DA EMPRESA FORNECEDORA]

Pelo presente instrumento, de um lado o **TRIBUNAL DE JUSTIÇA DO ESTADO DE [ESTADO]**, doravante denominado **TRIBUNAL**, inscrito no CNPJ sob o nº [CNPJ], neste ato representado por seu Presidente, [NOME], e de outro lado a empresa **[NOME DA EMPRESA]**, doravante denominada **CONVENIADA**, inscrita no CNPJ sob o nº [CNPJ], representada neste ato por seu sócio administrador [NOME], resolvem celebrar o presente **TERMO DE CONVÊNIO**, sujeitando-se às normas da Lei nº 14.133/2021, Lei nº 13.709/2018 (LGPD) e às seguintes cláusulas e condições:

---

### CLÁUSULA PRIMEIRA – DO OBJETO
1.1. O presente Convênio tem por objeto estabelecer a cooperação técnica e operacional para viabilizar o acesso automatizado, pela **CONVENIADA**, aos sistemas de processo eletrônico do **TRIBUNAL** (PJe, e-SAJ, e-Proc, etc.), mediante o uso de interface de programação (API) ou mecanismos de automação homologados, utilizando-se exclusivamente de autenticação via **Certificado Digital A1** (ICP-Brasil), visando a consulta de dados públicos e restritos (estes últimos, condicionados à representação processual válida) de processos judiciais de interesse de seus clientes.

### CLÁUSULA SEGUNDA – DAS OBRIGAÇÕES DO TRIBUNAL
2.1. Disponibilizar o acesso aos serviços de consulta processual, garantindo, dentro dos limites técnicos e operacionais, a disponibilidade dos endpoints ou interfaces web.
2.2. Fornecer documentação técnica mínima necessária para a integração segura (URL de webservices, especificações de headers, lista de IPs permitidos, se houver).
2.3. Comunicar à **CONVENIADA**, com antecedência mínima de 48 (quarenta e oito) horas, sobre manutenções programadas que possam indisponibilizar o acesso, salvo casos de urgência ou força maior.

### CLÁUSULA TERCEIRA – DAS OBRIGAÇÕES DA CONVENIADA
3.1. Utilizar os dados obtidos exclusivamente para fins lícitos, especificamente para gestão processual, acompanhamento jurídico e automação de rotinas de escritórios de advocacia e departamentos jurídicos.
3.2. Implementar mecanismos de controle de fluxo (*rate limiting*) em seus robôs/APIs para não comprometer a performance ou disponibilidade da infraestrutura do **TRIBUNAL**.
3.3. **Identificação**: Identificar todas as requisições automatizadas com User-Agent específico e/ou tokens de aplicação que permitam ao **TRIBUNAL** rastrear a origem da consulta.
3.4. Manter atualizados os dados cadastrais e técnicos de contato junto ao departamento de TI do **TRIBUNAL**.

### CLÁUSULA QUARTA – DA SEGURANÇA E ACESSO VIA CERTIFICADO A1
4.1. O acesso automatizado aos autos de processos que tramitam em segredo de justiça ou que exijam identificação do advogado será realizado estritamente mediante autenticação por Certificado Digital A1 (ICP-Brasil) do advogado constituído nos autos.
4.2. A **CONVENIADA** compromete-se a utilizar módulos de segurança (HSM ou cofres digitais criptografados) para o armazenamento e uso das chaves privadas dos certificados digitais de seus clientes, sendo vedado o armazenamento de senhas em texto plano.
4.3. É vedado o compartilhamento de credenciais de acesso ou certificados digitais com terceiros não autorizados.

### CLÁUSULA QUINTA – DA PROTEÇÃO DE DADOS (LGPD)
5.1. As partes declaram estar em conformidade com a Lei nº 13.709/2018 (Lei Geral de Proteção de Dados Pessoais - LGPD).
5.2. O tratamento de dados pessoais realizado em decorrência deste convênio fundamenta-se nas bases legais do exercício regular de direitos em processo judicial, administrativo ou arbitral (Art. 7º, VI e Art. 11, II, "d" da LGPD).
5.3. A **CONVENIADA** responsabiliza-se integralmente pela segurança, guarda e sigilo dos dados pessoais extraídos dos sistemas do **TRIBUNAL**, devendo adotar medidas técnicas e administrativas aptas a proteger os dados pessoais de acessos não autorizados e de situações acidentais ou ilícitas.

### CLÁUSULA SEXTA – DO SIGILO E CONFIDENCIALIDADE
6.1. As partes obrigam-se a manter o mais absoluto sigilo sobre quaisquer dados, informações, documentos e especificações técnicas a que tiverem acesso em razão deste Convênio, não podendo, sob qualquer pretexto, divulgá-los, reproduzi-los ou utilizá-los para fins diversos do objeto aqui estabelecido.
6.2. O dever de sigilo persiste mesmo após o término da vigência deste instrumento.

### CLÁUSULA SÉTIMA – DOS LOGS DE AUDITORIA E RASTREABILIDADE
7.1. A **CONVENIADA** deverá manter, pelo prazo mínimo de 5 (cinco) anos, os registros de conexão (logs) que comprovem a autoria, data, hora e IP de origem de cada consulta realizada ao sistema do **TRIBUNAL**.
7.2. O **TRIBUNAL** reserva-se o direito de auditar, a qualquer tempo, os acessos realizados pela **CONVENIADA** para verificar o cumprimento das cláusulas deste termo.

### CLÁUSULA OITAVA – DAS RESPONSABILIDADES
8.1. A **CONVENIADA** responderá civil, penal e administrativamente por quaisquer danos causados ao **TRIBUNAL** ou a terceiros decorrentes do uso indevido do acesso automatizado, falhas de segurança em seus sistemas, vazamento de dados ou violação de sigilo.
8.2. O **TRIBUNAL** não se responsabiliza por eventuais falhas, interrupções ou lentidão nos serviços de acesso, nem por danos decorrentes da utilização das informações obtidas pela **CONVENIADA**.

### CLÁUSULA NONA – DA VIGÊNCIA
9.1. O presente Convênio terá vigência de 24 (vinte e quatro) meses, contados a partir da data de sua assinatura, podendo ser prorrogado por iguais e sucessivos períodos, mediante termo aditivo, até o limite legal, desde que haja interesse das partes.

### CLÁUSULA DÉCIMA – DA RESCISÃO
10.1. Este Convênio poderá ser rescindido:
    a) Por mútuo acordo entre as partes;
    b) Unilateralmente, por qualquer das partes, mediante notificação prévia e escrita com antecedência mínima de 30 (trinta) dias;
    c) Imediatamente, pelo **TRIBUNAL**, em caso de violação das normas de segurança, ataque à infraestrutura (DDoS, Crawling abusivo) ou descumprimento das cláusulas de sigilo e LGPD.

### CLÁUSULA DÉCIMA PRIMEIRA – DO FORO
11.1. Fica eleito o Foro da Comarca de [CIDADE/CAPITAL], com renúncia expressa a qualquer outro, por mais privilegiado que seja, para dirimir quaisquer dúvidas ou litígios oriundos deste Convênio.

E, por estarem assim justos e acordados, assinam o presente instrumento em 2 (duas) vias de igual teor e forma.

[LOCAL], [DIA] de [MÊS] de [ANO].

__________________________________________
**TRIBUNAL DE JUSTIÇA DO ESTADO DE [ESTADO]**
Presidente

__________________________________________
**[NOME DA EMPRESA FORNECEDORA]**
Representante Legal

__________________________________________
Testemunha 1
CPF:

__________________________________________
Testemunha 2
CPF:
