// ==========================================
// js/data.js - Banco de Dados BioQuest 2.0
// ==========================================

const CASOS_CLINICOS = [
    {
        id: 1,
        titulo: "Déficit Energético em Alface",
        setor: "Módulo de Germinação",
        descricao: "O piruvato não está sendo convertido em Acetil-CoA, travando o Ciclo de Krebs sob alta demanda metabólica.",
        perguntaDiagnostico: "Qual coenzima (Vitamina B1) é o cofator limitante neste processo?",
        opcoes: [
            { texto: "Pirofosfato de Tiamina (TPP)", correta: true, feedback: "Exato! B1 é o motor da desidrogenação." },
            { texto: "Fosfato de Piridoxal (B6)", correta: false, feedback: "B6 atua em transaminações, não no piruvato." },
            { texto: "Biotina (B7)", correta: false, feedback: "Biotina atua em carboxilações de gorduras." },
            { texto: "Riboflavina (B2)", correta: false, feedback: "B2 atua no FAD, mais adiante na cadeia." }
        ],
        dica: "Pense no Pirofosfato que ativa as enzimas desidrogenases.",
        formaAtiva: "TPP (Pirofosfato de Tiamina)",
        consequencia: "Queda drástica na produção de ATP e acúmulo de lactato/etanol.",
        conduta: {
            opcoes: [
                { texto: "Suplementar Tiamina na solução", correta: true, feedback: "Correto! Restabelece a respiração celular." },
                { texto: "Aumentar Nitrogênio", correta: false, feedback: "Isso não resolve o gargalo enzimático da B1." },
                { texto: "Reduzir o CO2 injetado", correta: false, feedback: "Isso pioraria a produção de açúcares." },
                { texto: "Aplicar Potássio foliar", correta: false, feedback: "Ajuda na turgidez, mas não na síntese de ATP." }
            ]
        }
    },
    {
        id: 2,
        titulo: "Equilíbrio Redox em Microgreens",
        setor: "Módulo de Berçário",
        descricao: "A planta não regenera o NADPH necessário para a fixação de CO2 no Ciclo de Calvin.",
        perguntaDiagnostico: "A Niacina (B3) é precursora de qual molécula de transporte?",
        opcoes: [
            { texto: "NADP+ / NADPH", correta: true, feedback: "Perfeito! Essencial para o poder redutor." },
            { texto: "FAD / FADH2", correta: false, feedback: "Incorreto. Este transportador deriva da B2." },
            { texto: "Coenzima A", correta: false, feedback: "Incorreto. Esta deriva da Vitamina B5." },
            { texto: "Cianocobalamina", correta: false, feedback: "Incorreto. Esta é a B12 (não vegetal)." }
        ],
        dica: "Busque a coenzima que carrega 'P' de Fosfato e deriva da Niacina.",
        formaAtiva: "NAD / NADP",
        consequencia: "Parada no crescimento e estresse por excesso de luz (fotoinibição).",
        conduta: {
            opcoes: [
                { texto: "Ajustar aporte de B3 foliar", correta: true, feedback: "Correto! Recupera a fixação de carbono." },
                { texto: "Trocar espectro de luz", correta: false, feedback: "O problema é metabólico, não físico (luz)." },
                { texto: "Aumentar Fósforo via Raiz", correta: false, feedback: "O fósforo ajuda, mas não substitui o NADP." },
                { texto: "Reduzir Umidade Relativa", correta: false, feedback: "Irrelevante para a regeneração de NADPH." }
            ]
        }
    },
    {
        id: 3,
        titulo: "Peroxidação de Membranas UV",
        setor: "Módulo de Proteção",
        descricao: "Radicais livres estão destruindo a bicamada lipídica dos cloroplastos por radiação intensa.",
        perguntaDiagnostico: "Qual vitamina lipossolúvel protege os lipídios contra a oxidação?",
        opcoes: [
            { texto: "Alfa-tocoferol (Vit E)", correta: true, feedback: "Correto! É o principal protetor de membranas." },
            { texto: "Ácido Ascórbico (Vit C)", correta: false, feedback: "A Vit C é solúvel em água, não protege gorduras." },
            { texto: "Filoquinona (Vit K1)", correta: false, feedback: "A K1 atua na fotossíntese, não no estresse redox." },
            { texto: "Calciferol (Vit D)", correta: false, feedback: "Sem função antioxidante comprovada em plantas." }
        ],
        dica: "Este antioxidante 'mora' dentro das membranas gordurosas.",
        formaAtiva: "Alfa-tocoferol",
        consequencia: "Vazamento de eletrólitos e morte celular rápida (queima).",
        conduta: {
            opcoes: [
                { texto: "Reforçar Tocoferóis e Selênio", correta: true, feedback: "Certo! Estabiliza as membranas lipídicas." },
                { texto: "Aplicar Cálcio Quelatado", correta: false, feedback: "O cálcio ajuda na parede celular, não na gordura." },
                { texto: "Aumentar Magnésio", correta: false, feedback: "Ajuda na clorofila, mas não impede a oxidação." },
                { texto: "Cobrir com Sombrite 80%", correta: false, feedback: "Ação paliativa, o metabolismo exige proteção química." }
            ]
        }
    },
    {
        id: 4,
        titulo: "Conversão de Nitrogênio (Aroma)",
        setor: "Módulo de Bio-síntese",
        descricao: "O manjericão acumula nitrato e não produz óleos essenciais por falha nas transaminases.",
        perguntaDiagnostico: "Qual vitamina B6 é o cofator para mover grupos amina?",
        opcoes: [
            { texto: "Fosfato de Piridoxal (PLP)", correta: true, feedback: "Exato! Chave para formar novos aminoácidos." },
            { texto: "Tiamina (B1)", correta: false, feedback: "B1 foca na quebra de açúcares, não no Nitrogênio." },
            { texto: "Ácido Fólico (B9)", correta: false, feedback: "B9 atua na divisão celular (DNA), não aminas." },
            { texto: "Biotina (B7)", correta: false, feedback: "B7 atua na síntese de ácidos graxos." }
        ],
        dica: "Procure o derivado da Piridoxina necessário para enzimas ALT/AST.",
        formaAtiva: "PLP (Fosfato de Piridoxal)",
        consequencia: "Ausência de aroma e folhas com cor verde-pálida (clorose).",
        conduta: {
            opcoes: [
                { texto: "Equilibrar Piridoxina e Mo", correta: true, feedback: "Perfeito! Ativa o metabolismo proteico." },
                { texto: "Aplicar mais Ureia", correta: false, feedback: "Pioraria o acúmulo de nitrato tóxico." },
                { texto: "Aumentar Ferro", correta: false, feedback: "O Ferro não substitui a B6 na transaminação." },
                { texto: "Reduzir temperatura da água", correta: false, feedback: "Não altera o gargalo enzimático existente." }
            ]
        }
    },
    {
        id: 5,
        titulo: "Síntese de Coenzima A (CoA)",
        setor: "Módulo de Ácidos Graxos",
        descricao: "As plantas falham na produção de ceras cuticulares, perdendo muita água por transpiração.",
        perguntaDiagnostico: "Qual vitamina B5 é a base estrutural da Coenzima A?",
        opcoes: [
            { texto: "Ácido Pantotênico", correta: true, feedback: "Correto! Sem B5, não há síntese de ceras e gorduras." },
            { texto: "Ácido Fólico", correta: false, feedback: "Fólico foca em metilação e DNA." },
            { texto: "Niacina", correta: false, feedback: "Niacina foca no transporte de elétrons (NAD)." },
            { texto: "Riboflavina", correta: false, feedback: "Riboflavina foca na respiração (FAD)." }
        ],
        dica: "Vem do grego 'Pantos' e está presente em todo o metabolismo de CoA.",
        formaAtiva: "Coenzima A (CoA)",
        consequencia: "Desidratação severa e perda da proteção contra patógenos.",
        conduta: {
            opcoes: [
                { texto: "Suplementar B5 via solução", correta: true, feedback: "Certo! Ativa a síntese de cutina e ceras." },
                { texto: "Aplicar óleo de Neem", correta: false, feedback: "Ação externa, não resolve o problema metabólico." },
                { texto: "Aumentar Zinco", correta: false, feedback: "Zinco ajuda no auxina, não na Coenzima A." },
                { texto: "Aumentar a pressão da bomba", correta: false, feedback: "Não afeta a síntese lipídica interna." }
            ]
        }
    },
    {
        id: 6,
        titulo: "Estresse por Calor Crítico",
        setor: "Módulo Climático",
        descricao: "Ondas de calor estouram o limite enzimático, gerando H2O2 excessivo no citoplasma.",
        perguntaDiagnostico: "Qual vitamina (C) neutraliza o peróxido no ciclo Ascorbato?",
        opcoes: [
            { texto: "Ácido Ascórbico", correta: true, feedback: "Correto! É o antioxidante mais vital contra calor." },
            { texto: "Retinol (Vit A)", correta: false, feedback: "Plantas usam Carotenos, não Retinol animal." },
            { texto: "Ergocalciferol", correta: false, feedback: "Relacionado a Vitamina D2, sem uso aqui." },
            { texto: "Ácido Salicílico", correta: false, feedback: "É um sinalizador de defesa, não a Vitamina C." }
        ],
        dica: "A vitamina cítrica que protege tanto humanos quanto plantas.",
        formaAtiva: "Ascorbato / DHA",
        consequencia: "Murchamento permanente e oxidação das proteínas.",
        conduta: {
            opcoes: [
                { texto: "Ajustar Ascorbato (Vit C)", correta: true, feedback: "Certo! Protege contra o 'cozimento' celular." },
                { texto: "Aumentar o Potássio", correta: false, feedback: "Ajuda no estoma, mas não remove o H2O2." },
                { texto: "Reduzir o Fotoperíodo", correta: false, feedback: "Apenas reduz o sintoma, não trata a causa química." },
                { texto: "Aplicar Enxofre", correta: false, feedback: "Ajuda, mas a Vit C é a defesa imediata." }
            ]
        }
    },
    {
        id: 7,
        titulo: "Fluxo Eletrônico Mitocondrial",
        setor: "Módulo Energético",
        descricao: "A transferência de elétrons no Complexo II está lenta, reduzindo o vigor da planta.",
        perguntaDiagnostico: "A Riboflavina (B2) é o componente central de qual transportador?",
        opcoes: [
            { texto: "FAD / FMN", correta: true, feedback: "Exato! Flavoproteínas dependem totalmente da B2." },
            { texto: "ATP Sintase", correta: false, feedback: "É uma enzima motora, não um transportador de B2." },
            { texto: "Citocromo C", correta: false, feedback: "Usa Ferro-Heme, não Riboflavina." },
            { texto: "Plastoquinona", correta: false, feedback: "Usa uma cadeia isoprenoide, não B2." }
        ],
        dica: "Busque o nome que contém 'Flavina', como a própria vitamina.",
        formaAtiva: "FAD (Flavina Adenina Dinucleotídeo)",
        consequencia: "Crescimento extremamente lento e falta de energia (ATP).",
        conduta: {
            opcoes: [
                { texto: "Otimizar Riboflavina", correta: true, feedback: "Certo! Acelera o fluxo de elétrons na respiração." },
                { texto: "Oxigenar a água (Venturi)", correta: false, feedback: "Ajuda, mas o gargalo é a falta do FAD." },
                { texto: "Reduzir a Condutividade (EC)", correta: false, feedback: "Irrelevante para a eficiência da Riboflavina." },
                { texto: "Aplicar Boro", correta: false, feedback: "Boro atua na parede celular, não no FAD." }
            ]
        }
    },
    {
        id: 8,
        titulo: "Fotossíntese: Fase Clara",
        setor: "Módulo Fotossintético",
        descricao: "Falha na transferência de elétrons no Fotossistema I, bloqueando a produção de NADPH.",
        perguntaDiagnostico: "A Vitamina K1 (Filoquinona) é essencial em qual complexo?",
        opcoes: [
            { texto: "Fotossistema I (PSI)", correta: true, feedback: "Perfeito! A K1 é o transportador A1 central." },
            { texto: "Fotossistema II (PSII)", correta: false, feedback: "O PSII usa Plastoquinonas, não Filoquinona." },
            { texto: "Rubisco", correta: false, feedback: "Rubisco atua na fase escura (fixação de CO2)." },
            { texto: "Complexo Citocromo b6f", correta: false, feedback: "É o intermediário, não o centro K1." }
        ],
        dica: "Vitamina K1 vegetal, vital para o centro de reação do PSI.",
        formaAtiva: "Filoquinona",
        consequencia: "Clorose severa e interrupção total da produção de açúcares.",
        conduta: {
            opcoes: [
                { texto: "Garantir aporte de Vitamina K1", correta: true, feedback: "Correto! Restabelece o fluxo fotoquímico." },
                { texto: "Aplicar Magnésio e Ferro", correta: false, feedback: "Ajudam na clorofila, mas não no transporte K1." },
                { texto: "Mudar para luz UV", correta: false, feedback: "Não resolveria a falha eletrônica interna." },
                { texto: "Aumentar Umidade do Ar", correta: false, feedback: "Não interfere nos fotossistemas foliares." }
            ]
        }
    }
];