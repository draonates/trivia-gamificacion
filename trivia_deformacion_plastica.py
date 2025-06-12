import gspread
import base64
import requests
import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title='Trivia Deformación Plástica', layout='centered')

preguntas = {
    'Certamen 1': {
        'Fácil': [],
        'Medio': []
    },
    'Certamen 2': {
        'Fácil': [],
        'Medio': []
    }
}

preguntas['Certamen 2']['Fácil'] += [
    {
        'question': '¿Qué tipo de mecanismo de creep es dominante a bajas tensiones y altas temperaturas en materiales policristalinos?',
        'options': ['Creep por dislocación', 'Creep por difusión', 'Creep por maclado', 'a) y c)'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Cuál es el efecto de aumentar el tamaño de grano en la tasa de creep por Coble?',
        'options': ['La aumenta', 'La reduce', 'No cambia', 'La vuelve no lineal'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué indica un exponente de esfuerzo n ≈ 1 en un gráfico log(ε̇) vs log(σ)?',
        'options': ['Deslizamiento de limite de grano', 'Creep por trepado de dislocaciones', 'Creep difusional', 'Creep por maclado'],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuales son los mecanismos responsables del creep a altas temperaturas?',
        'options': ['Difusión atómica', 'Movimiento de dislocaciones asistido por vacancias', 'Trepado de dislocaciones y deslizamiento de borde de grano', 'Todas las anteriores'],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Qué tipo de materiales muestran mayor recuperación de deformación por creep al eliminar la carga?',
        'options': ['Metales', 'Cerámicos', 'Vidrios', 'Polímeros'],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Qué condición debe cumplirse para que un componente metálico falle por fractura antes que por cedencia?',
        'options': ['KIc < σy√(πa)', 'σy < KI / √(πa)', 'σy < KIc / √(πa)', 'a < 0.1 mm'],
        'answer': 0,
        'formula': ''
    },
    {
        'question': '¿Cuál de los siguientes mecanismos de deformación no requiere presencia de dislocaciones?',
        'options': ['Creep por trepado', 'Creep de Coble', 'Endurecimiento por deformación', 'Fluencia dislocacional'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué representa la energía de activación en el contexto del creep?',
        'options': ['Energía de nucleación de dislocaciones', 'Energía para difusión atómica', 'Energía elástica almacenada', 'Barrera energética que debe superarse para que ocurra el mecanismo específico de deformación dependiente de la temperatura'],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Cuales son los mecanismos de Creep a temperatura ambiente?',
        'options': ['Difusión atómica', 'Deslizamiento de dislocaciones asistido por tensiones internas', 'Deslizamiento de dislocaciones por reorganización lenta de la red de dislocaciones', 'b) y c)'],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Cuál es la consecuencia microestructural de disminuir el tamaño de grano en un mapa de mecanismos de deformación?',
        'options': ['El régimen de Nabarro-Herring domina a menor T/Tm', 'Los mecanismos que dependen de difusión por borde de grano se activan a menores tensiones', 'Se favorece el endurecimiento por solución sólida', 'Desaparece el mecanismo de Coble creep'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué ocurre en la etapa primaria de la fluencia?',
        'options': ['La tasa de deformación es constante', 'Ocurre una disminución progresiva de la tasa de deformación', 'La deformación se detiene', 'El material se endurece térmicamente'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Cuál es la característica principal de la etapa terciaria de la fluencia?',
        'options': ['El material se recupera', 'La deformación se estabiliza', 'La tasa de deformación se acelera hasta la fractura', 'El esfuerzo disminuye a cero'],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué mecanismo de fluencia se asocia la difusión atómica por limite de granos?',
        'options': ['Nabarro-Herring', 'Fluencia por dislocaciones', 'Coble', 'a) y b)'],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué tipo de comportamiento representa mejor una curva de fluencia a largo plazo?',
        'options': ['Elástico puro', 'Viscoplástico', 'Perfectamente plástico', 'Amorfo'],
        'answer': 1,
        'formula': ''
    }   
]

preguntas['Certamen 2']['Medio'] += [
    {
        'question': '¿Qué parámetro en la ecuación de fluencia ε̇ = A·σⁿ·exp(–Q/RT) representa el control por difusión?',
        'options': ['n', 'A', 'Q', 'R'],
        'answer': 2,
        'formula': 'ε̇ = A·σ^n·e^{-Q/RT}'
    },
    {
        'question': '¿Qué tipo de fluencia presenta una pendiente constante en una gráfica ε vs t?',
        'options': ['Primaria', 'Secundaria', 'Terciaria', 'Elástica'],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué factor afecta directamente el valor del exponente de esfuerzo (n) en el comportamiento por fluencia?',
        'options': ['Tamaño de grano', 'Composición química', 'Temperatura y mecanismo de deformación', 'Tipo de ensayo de tracción'],
        'answer': 2,
        'formula': ''
    },
    {
        'question': 'En un ensayo de fluencia, si se duplica la temperatura (en K), ¿qué componente se ve más afectado en la ecuación constitutiva?',
        'options': ['El exponente n', 'La constante A', 'La energía de activación Q', 'El término exponencial exp(-Q/RT)'],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Qué caracteriza la deformación por fluencia controlada por Coble?',
        'options': ['Difusión en el volumen', 'Deslizamiento de dislocaciones', 'Difusión por contornos de grano', 'Formación de maclas'],
        'answer': 2,
        'formula': ''
    }
]


preguntas['Certamen 1']['Fácil'] = [{
            'question': '¿Qué es la deformación plástica?',
            'options': [
                'Cambio temporal de forma',
                'Cambio permanente de forma bajo carga',
                'Fusión del material por temperatura',
                'Expansión térmica'
            ],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de dislocación tiene el vector de Burgers perpendicular a la línea de dislocación?',
            'options': [
                'Tornillo',
                'Mixta',
                'Borde',
                'Vacancia'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué propiedad indica la capacidad del material de deformarse sin romperse?',
            'options': [
                'Dureza',
                'Tenacidad',
                'Resistencia a la tracción',
                'Ductilidad'
            ],
            'answer': 3,
            'formula': ''
        },
        {
            'question': '¿Cuál es la principal diferencia entre una dislocación de borde y una dislocación de tornillo?',
            'options': [
                'El tipo de átomo que la forma',
                'La dirección del vector de Burgers con respecto a la línea de dislocación',
                'El plano de clivaje involucrado',
                'La temperatura de operación'
            ],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué estructura cristalina presenta mayor ductilidad debido a la alta densidad de empaquetamiento?',
            'options': [
                'BCC',
                'HCP',
                'FCC',
                'Amorfa'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué mecanismo permite la multiplicación de dislocaciones durante la deformación plástica?',
            'options': [
                'Modelo de Schmid',
                'Mecanismo de Coble',
                'Ciclo de Frank–Read',
                'Efecto Hall-Petch'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Cuál es la orientación óptima para la activación de un sistema de deslizamiento según el modelo de Schmid?',
            'options': [
                'φ = 0° y λ = 90°',
                'φ = 45° y λ = 45°',
                'φ = 90° y λ = 0°',
                'φ = 30° y λ = 60°'
            ],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Por qué el maclado es más frecuente en estructuras HCP que en FCC?',
            'options': [
                'Porque el módulo de elasticidad es mayor',
                'Porque tienen menor densidad de empaquetamiento',
                'Porque poseen menos sistemas de deslizamiento activos',
                'Porque la energía de activación es más alta'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de deformación plástica ocurre típicamente a temperaturas elevadas y tiempos prolongados?',
            'options': [
                'Endurecimiento por deformación',
                'Mecanismo de Frank–Read',
                'Fluencia (creep)',
                'Mecanismo de Hall-Petch'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué parámetro microestructural influye directamente en el aumento del esfuerzo de fluencia según Hall-Petch?',
            'options': [
                'Contenido de carbono',
                'Tamaño de grano',
                'Tipo de red cristalina',
                'Coeficiente de Poisson'
            ],
            'answer': 1,
            'formula': ''
        },

        {
            'question': '¿Qué característica facilita el deslizamiento en un plano cristalino?',
            'options': ['Baja densidad atómica', 'Alta energía de apilamiento', 'Alta densidad atómica', 'Baja temperatura'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Cuál es la dirección de deslizamiento en los materiales FCC?',
            'options': ['<111>', '<100>', '<110>', '<112>'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Cuál es la ecuación principal del modelo de Schmid?',
            'options': ['τ = σ / cos(φ)', 'τ = σ cos(φ) cos(λ)', 'σ = τ cos(λ)', 'τ = σ / (cos(φ)cos(λ))'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de dislocación tiene el vector de Burgers paralelo a la línea de dislocación?',
            'options': ['Mixta', 'De borde', 'De tornillo', 'Parcial'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué ocurre cuando dos dislocaciones del mismo signo interactúan?',
            'options': ['Se aniquilan', 'Se repelen', 'No interactúan', 'Se fusionan'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Cuál es el plano de maclado típico en materiales HCP?',
            'options': ['{111}', '{1012}', '{110}', '{123}'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de maclado ocurre por cambios de temperatura?',
            'options': ['Mecánico', 'De crecimiento', 'Térmico', 'Transversal'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué mecanismo de fluencia predomina a alta temperatura?',
            'options': ['Dislocación', 'Maclado', 'Nabarro-Herring', 'Endurecimiento'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué variable es constante en la segunda etapa del creep?',
            'options': ['Tensión', 'Deformación', 'Velocidad de deformación', 'Energía interna'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué fenómeno impide el movimiento de dislocaciones entre planos distintos?',
            'options': ['Recristalización', 'Interacción con solutos', 'Bloqueo de Lomer', 'Texturización'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué estructura cristalina tiene mayor dificultad para el deslizamiento cruzado?',
            'options': ['FCC', 'BCC', 'HCP', 'Amorfa'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué variable se relaciona con la fórmula F = τ * b?',
            'options': ['Energía de activación', 'Esfuerzo normal', 'Fuerza sobre la dislocación', 'Resistencia a la tracción'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué describe la relación de Hall–Petch?',
            'options': ['Dureza vs. temperatura', 'Esfuerzo vs. deformación', 'Esfuerzo de fluencia vs. tamaño de grano', 'Conductividad vs. esfuerzo'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué proceso de conformado ocurre bajo tracción?',
            'options': ['Laminado', 'Forjado', 'Trefilado', 'Extrusión'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué relación predice el tiempo de falla en fluencia a partir de la tasa secundaria?',
            'options': ['Ley de Hall–Petch', 'Relación de Schmid', 'Monkman–Grant', 'Ley de Hooke'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de dislocación se puede mover por trepado?',
            'options': ['De tornillo', 'De borde', 'Mixta', 'Parcial'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué tipo de deformación ocurre cuando las dislocaciones se acumulan y no pueden seguir moviéndose?',
            'options': ['Recristalización', 'Endurecimiento por deformación', 'Fusión', 'Reversibilidad'],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué propiedad permite evaluar si un material puede sufrir deformación plástica sin fractura?',
            'options': ['Tenacidad', 'Dureza', 'Ductilidad', 'Módulo de Young'],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Cuál es la función del ciclo de Frank–Read?',
            'options': ['Deslizar dislocaciones', 'Disociar dislocaciones', 'Multiplicar dislocaciones', 'Fusionar dislocaciones'],
            'answer': 2,
            'formula': ''
        }]
preguntas['Certamen 1']['Medio'] = [{
        'question': '¿Por qué los materiales con estructura FCC presentan mayor capacidad de deslizamiento cruzado que los BCC?',
        'options': [
            'Porque tienen más sistemas de deslizamiento independientes',
            'Porque la energía de falla de apilamiento en FCC es mayor',
            'Porque el módulo de corte es menor',
            'Porque la densidad de vacantes es más alta'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': 'En una estructura BCC, ¿qué factor limita la aplicabilidad del modelo de Schmid?',
        'options': [
            'Alta densidad de planos',
            'Componentes ortogonales de la tensión de corte afectan el deslizamiento',
            'El vector de Burgers no es bien definido',
            'Sólo opera a temperatura ambiente'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': 'El modelo de Schmid indica que la deformación por deslizamiento ocurre más eficientemente cuando:',
        'options': [
            'φ = 0° y λ = 90°',
            'φ = 90° y λ = 0°',
            'φ = 45° y λ = 45°',
            'φ = 60° y λ = 30°'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál es el sistema de deslizamiento más probable en monocristales de aluminio sometidos a tensión?',
        'options': [
            '{110}<111>',
            '{111}<110>',
            '{112}<111>',
            '{0001}<2110>'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Cuál de las siguientes afirmaciones sobre el mecanismo de maclado en materiales HCP es correcta?',
        'options': [
            'Ocurre preferentemente por temperatura elevada',
            'Es favorecido por baja energía de falla de apilamiento',
            'Requiere múltiples sistemas de deslizamiento',
            'Sólo ocurre en deformación elástica'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Cuál es el rol principal del mecanismo de Frank–Read en la deformación plástica?',
        'options': [
            'Eliminar dislocaciones',
            'Generar dislocaciones para facilitar el endurecimiento por deformación',
            'Estabilizar la energía de la red',
            'Activar el mecanismo de maclado'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué condiciones favorecen el maclado térmico?',
        'options': [
            'Baja temperatura y alta tasa de deformación',
            'Solamente deformación plástica controlada',
            'Cambios térmicos sin aplicación de carga',
            'Altas tensiones de corte'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Por qué la deformación plástica en BCC requiere mayores tensiones que en FCC?',
        'options': [
            'Menor cantidad de dislocaciones',
            'Planos de deslizamiento menos densos',
            'Mayor módulo de elasticidad',
            'Menor energía de apilamiento'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué fenómeno ocurre durante la tercera etapa del creep?',
        'options': [
            'Recuperación',
            'Deslizamiento cruzado',
            'Nucleación y crecimiento de microgrietas',
            'Formación de maclas'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': 'El mecanismo de Nabarro–Herring se caracteriza por:',
        'options': [
            'Deformación plástica por dislocaciones',
            'Flujo de átomos a lo largo del borde de grano',
            'Difusión a través del volumen del cristal',
            'Formación de cavidades en límites de grano'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué afirmación describe correctamente el trepado de dislocaciones?',
        'options': [
            'Es exclusivo de dislocaciones de tornillo',
            'Requiere formación de dislocaciones sésiles',
            'Involucra vacantes y permite movimiento entre planos',
            'Es el mismo que deslizamiento cruzado'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué ocurre cuando una dislocación de borde interactúa con un átomo de soluto más pequeño que los de la red?',
        'options': [
            'El soluto se ubica bajo el semiplano adicional',
            'Se favorece el trepado',
            'Se alivia la compresión ubicándose en el extremo del semiplano adicional',
            'No hay interacción por simetría esférica'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': 'El mecanismo de fortalecimiento por solución sólida es más efectivo cuando:',
        'options': [
            'El soluto es más pequeño y la dislocación es de tornillo',
            'El soluto tiene campo de tensión simétrico y es mayor que los átomos de red',
            'El soluto interactúa con dislocaciones de borde',
            'La dislocación es mixta y el soluto es neutro'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': 'El mecanismo de Coble creep es dominante cuando:',
        'options': [
            'El material es un monocristal a alta temperatura',
            'Hay difusión a través del volumen',
            'La difusión ocurre a lo largo del límite de grano',
            'No hay vacancias suficientes'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál de las siguientes es una consecuencia directa del endurecimiento por deformación?',
        'options': [
            'Disminución del límite elástico',
            'Aumento de ductilidad',
            'Aumento de densidad de dislocaciones',
            'Recristalización inmediata'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué ocurre en un sistema de deslizamiento cuando se alcanza la tensión crítica?',
        'options': [
            'Las dislocaciones se transforman en vacancias',
            'Se inicia el movimiento de dislocaciones',
            'Se inicia la deformación elástica',
            'Se produce maclado inmediato'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': 'La dislocación helicoidal es caracterizada por:',
        'options': [
            'Vector de Burgers perpendicular a la línea de dislocación',
            'Ser exclusiva de metales amorfos',
            'Apilamiento en espiral y Burgers paralelo a la línea',
            'Solo se presenta en sistemas FCC'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál es el sistema de maclado típico en una estructura HCP?',
        'options': [
            '{111}<112>',
            '{1012}<1011>',
            '{110}<111>',
            '{123}<111>'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿Qué relación predice el tiempo de falla por creep a partir de la tasa secundaria de deformación?',
        'options': [
            'Ley de Hooke',
            'Ecuación de Arrhenius',
            'Relación de Hall–Petch',
            'Relación de Monkman–Grant'
        ],
        'answer': 3,
        'formula': ''
    },
    {
        'question': '¿Qué afirmación es correcta respecto a dislocaciones sésiles?',
        'options': [
            'Se deslizan en múltiples planos',
            'No interactúan con límites de grano',
            'Se forman por el mecanismo de bloqueo de Lomer',
            'Sólo se producen a temperatura ambiente'
        ],
        'answer': 2,
        'formula': ''
    },
    {
            'question': '¿Por qué los materiales FCC presentan mayor ductilidad que los BCC, a pesar de tener ambos 12 sistemas de deslizamiento?',
            'options': [
                'Porque los BCC tienen menor energía de activación para el deslizamiento',
                'Porque los planos y direcciones de deslizamiento en FCC tienen mayor densidad atómica',
                'Porque el FCC tiene más vacantes',
                'Porque los BCC tienen más dislocaciones sésiles'
            ],
            'answer': 1,
            'formula': ''
        },
        {
            'question': '¿Qué condición cristalográfica favorece el deslizamiento en un monocristal según el modelo de Schmid?',
            'options': [
                'φ = 0° y λ = 90°',
                'φ = 30° y λ = 60°',
                'φ = 45° y λ = 45°',
                'φ = 90° y λ = 0°'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿En qué estructura cristalina es más frecuente el maclado como mecanismo principal de deformación?',
            'options': [
                'FCC',
                'BCC',
                'Amorfa',
                'HCP'
            ],
            'answer': 3,
            'formula': ''
        },
        {
            'question': '¿Cuál es el mecanismo de fluencia dominante en monocristales a altas temperaturas y bajos esfuerzos?',
            'options': [
                'Fluencia por dislocación',
                'Recristalización dinámica',
                'Nabarro-Herring',
                'Coble'
            ],
            'answer': 2,
            'formula': ''
        },
        {
            'question': '¿Qué ocurre con la tensión crítica de cizalladura al aumentar la densidad atómica en los planos de deslizamiento?',
            'options': [
                'Aumenta significativamente',
                'No se ve afectada',
                'Disminuye, facilitando el deslizamiento',
                'Se vuelve constante'
            ],
            'answer': 2,
            'formula': ''
        },
    {
        'question': '¿Cuál es la característica principal del mecanismo de creep de Nabarro–Herring?',
        'options': [
            'Movimiento de dislocaciones en planos de baja energía',
            'Difusión de átomos a través del volumen del cristal',
            'Reorientación de granos mediante maclado',
            'Deslizamiento por disolución intergranular'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': 'El mecanismo de Coble creep se distingue del de Nabarro–Herring porque:',
        'options': [
            'Opera a temperaturas más altas y en granos grandes',
            'Es activado por vacancias generadas en el volumen',
            'Implica difusión a lo largo de los límites de grano',
            'Se basa en deslizamiento por dislocaciones móviles'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué condición favorece el mecanismo de Coble creep sobre el de Nabarro–Herring?',
        'options': [
            'Alta densidad de dislocaciones móviles',
            'Alta relación superficie-volumen (granos pequeños)',
            'Elevadas presiones hidrostáticas',
            'Deformación plástica uniforme'
        ],
        'answer': 1,
        'formula': ''
    },
    {
        'question': '¿En qué región de temperatura es más probable que predomine el mecanismo de Nabarro–Herring?',
        'options': [
            'Baja temperatura (0.1 Tm)',
            'Temperatura intermedia (0.4 Tm)',
            'Alta temperatura (> 0.6 Tm)',
            'Temperatura criogénica'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué fenómeno microestructural es indicativo de Coble creep en materiales policristalinos?',
        'options': [
            'Formación de maclas de tensión',
            'Reorientación de subgranos',
            'Cavitación en límites de grano',
            'Apilamiento de dislocaciones'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál es la variable que influye más directamente en la tasa de Coble creep?',
        'options': [
            'Densidad de vacancias en el volumen',
            'Módulo de elasticidad',
            'Área total de límite de grano',
            'Cantidad de maclas generadas'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': 'En términos de mecanismo atómico, ¿cuál es la diferencia esencial entre Nabarro–Herring y Coble?',
        'options': [
            'Uno involucra trepado y el otro, deslizamiento cruzado',
            'La dirección del vector de Burgers difiere',
            'Nabarro–Herring usa difusión volumétrica; Coble, intergranular',
            'Coble sólo ocurre en materiales monofásicos'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál de los siguientes mecanismos NO está relacionado directamente con el creep difusional?',
        'options': [
            'Coble',
            'Nabarro–Herring',
            'Frank–Read',
            'Reorientación atómica sin carga externa'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Qué variable tiene mayor influencia para ralentizar tanto el Coble como el Nabarro–Herring creep?',
        'options': [
            'Aumento del esfuerzo aplicado',
            'Disminución del tamaño de grano',
            'Reducción de la temperatura',
            'Inclusión de más fases amorfas'
        ],
        'answer': 2,
        'formula': ''
    },
    {
        'question': '¿Cuál de las siguientes afirmaciones es verdadera respecto al creep difusional?',
        'options': [
            'Depende exclusivamente de la densidad de dislocaciones',
            'No ocurre en monocristales',
            'La velocidad de deformación está relacionada con la movilidad atómica',
            'Solo se presenta a cargas muy elevadas'
        ],
        'answer': 2,
        'formula': ''
    }]

if 'nombre' not in st.session_state:
    st.session_state.nombre = ''
    st.session_state.certamen = ''
    st.session_state.nivel = ''
    st.session_state.q_idx = 0
    st.session_state.puntaje = 0
    st.session_state.historial = []

st.title('Trivia: Fundamentos de la Deformación Plástica')

if st.session_state.nombre == '':
    st.session_state.nombre = st.text_input('Ingresa tu nombre:')
    st.session_state.certamen = st.selectbox('Selecciona el certamen:', list(preguntas.keys()))
    st.session_state.nivel = st.selectbox('Selecciona el nivel de dificultad:', ['Fácil', 'Medio'])
    if st.session_state.nombre and st.button('Comenzar'):
        st.rerun()
else:
    certamen_actual = st.session_state.certamen
    nivel_actual = st.session_state.nivel
    lista_preguntas = preguntas[certamen_actual][nivel_actual]

    if st.session_state.q_idx < len(lista_preguntas):
        q = lista_preguntas[st.session_state.q_idx]
        st.markdown(f'### Pregunta {st.session_state.q_idx + 1} de {len(lista_preguntas)}')
        st.write(q['question'])
        if q['formula']:
            st.latex(q['formula'])
        respuesta = st.radio('Selecciona una opción:', q['options'], key=f"q{st.session_state.q_idx}")

        if st.button('Responder'):
            correcto = respuesta == q['options'][q['answer']]
            st.session_state.historial.append({
                'pregunta': q['question'],
                'respuesta': respuesta,
                'correcta': correcto
            })
            if correcto:
                st.session_state.puntaje += 1
                st.success('¡Correcto!')
            else:
                st.error(f'Incorrecto. Respuesta correcta: {q["options"][q["answer"]]}')
            st.session_state.q_idx += 1
            st.rerun()
    else:
        st.balloons()
        st.success(f'🎉 {st.session_state.nombre}, obtuviste {st.session_state.puntaje} de {len(lista_preguntas)} en nivel {nivel_actual}')

        resultado = {
            'Nombre': st.session_state.nombre,
            'Certamen': certamen_actual,
            'Puntaje': st.session_state.puntaje,
            'Total': len(lista_preguntas),
            'Nivel': nivel_actual,
            'Fecha': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        archivo = 'resultados_deformacion.csv'
        df = pd.DataFrame([resultado])
        if os.path.exists(archivo):
            df.to_csv(archivo, mode='a', header=False, index=False)
        else:
            df.to_csv(archivo, index=False)

        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
            cliente = gspread.authorize(creds)

            sheet = cliente.open("Trivia Deformación Plástica").worksheet("Resultados")
            fila = [
                resultado['Nombre'],
                resultado['Certamen'],
                resultado['Puntaje'],
                resultado['Total'],
                resultado['Nivel'],
                resultado['Fecha']
            ]
            sheet.append_row(fila)
            st.success("Resultado guardado en Google Sheets correctamente.")
        except Exception as e:
            st.warning(f"No se pudo guardar en Google Sheets: {e}")

    st.markdown('---')
        
    st.markdown(' Revisión de Respuestas')

        
for i, h in enumerate(st.session_state.historial):
            pregunta = lista_preguntas[i]
            respuesta_correcta = pregunta['options'][pregunta['answer']]
            es_correcta = h['respuesta'] == respuesta_correcta

            st.markdown(f'**{i+1}. {pregunta["question"]}**')
            if pregunta['formula']:
                st.latex(pregunta['formula'])

            for opt in pregunta['options']:
                if opt == h['respuesta'] and es_correcta:
                    st.success(f'Tu respuesta: {opt} ✅')
                elif opt == h['respuesta'] and not es_correcta:
                    st.error(f'Tu respuesta: {opt} ❌')
                elif opt == respuesta_correcta:
                    st.info(f'Respuesta correcta: {opt}')

            st.markdown('---')

      
