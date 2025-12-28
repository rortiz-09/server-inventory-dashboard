def load_css():
    """Genera el CSS global premium para la aplicación."""
    return """
    <style>
        /* === IMPORTAR FUENTE PREMIUM === */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

        /* === GLOBAL TYPOGRAPHY === */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, [data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.5px;
        }

        /* === CONTENEDOR PRINCIPAL === */
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1600px !important;
        }
        
        /* === TARJETAS DE MÉTRICAS (Glassmorphism Premium) === */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: inherit;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px;
            opacity: 0.7;
        }

        /* === NOTIFICACIONES PERSONALIZADAS (Custom Alerts) === */
        .stAlert {
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* Success (Green style override) */
        div[data-testid="stNotification"][data-baseweb="notification"] {
             border-radius: 8px;
        }

        /* === HEADERS & DIVIDERS === */
        h3 {
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 8px;
            margin-bottom: 25px !important;
            font-size: 1.4rem !important;
            font-weight: 600;
            opacity: 0.95;
        }
        
        hr {
            margin: 2rem 0;
            opacity: 0.15;
        }

        /* === TABLAS DE DATOS === */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }

        /* === SIDEBAR REFINADO === */
        [data-testid="stSidebar"] {
            background-color: rgb(14, 17, 23); /* Force Dark match */
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
    </style>
    """
