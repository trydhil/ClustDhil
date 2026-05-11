# sfcm_dash/components/layout.py
from dash import html, dcc

def create_layout():
    return html.Div([

        # ── HERO HEADER ──────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("Analisis Kemiskinan Indonesia", className="hero-eyebrow"),
                html.H1([
                    "Pemetaan ", html.Mark("Klaster"), html.Br(),
                    "Kemiskinan SFCM"
                ], className="hero-h1"),
                html.P(
                    "Upload data CSV, atur parameter, lalu jalankan clustering "
                    "otomatis menggunakan algoritma Subtractive Fuzzy C-Means "
                    "untuk 514 Kabupaten/Kota Indonesia.",
                    className="hero-desc"
                ),
                html.Div([
                    html.Span("Fuzzy Logic",  className="hero-tag"),
                    html.Span("Clustering",   className="hero-tag"),
                    html.Span("Geospatial",   className="hero-tag"),
                    html.Span("514 Kab/Kota", className="hero-tag"),
                ], className="hero-tags"),
            ], className="neo-hero-left"),

            html.Div([
                html.Div("Status Sistem", style={
                    'fontSize': '10px', 'fontWeight': '700',
                    'textTransform': 'uppercase', 'letterSpacing': '0.09em',
                    'opacity': '0.45', 'marginBottom': '8px'
                }),
                html.Div([
                    html.Div([html.Div("—", className="stat-val"), html.Div("Cluster",       className="stat-lbl")], className="hero-stat-cell yellow"),
                    html.Div([html.Div("—", className="stat-val"), html.Div("Iterasi",        className="stat-lbl")], className="hero-stat-cell white"),
                    html.Div([html.Div("—", className="stat-val"), html.Div("Total Daerah",   className="stat-lbl")], className="hero-stat-cell white"),
                    html.Div([html.Div("—", className="stat-val"), html.Div("Silhouette",     className="stat-lbl")], className="hero-stat-cell pink"),
                ], className="hero-stat-grid"),
            ], className="neo-hero-right"),
        ], className="neo-hero"),

        # ── KONTROL PANEL ────────────────────────────────────────────
        html.Div([

            # Kiri: Upload + Radius
            html.Div([
                html.Div("1. Data & Radius", className="card-title"),

                html.Div([
                    html.Label("Upload Data CSV", className="neo-label"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag & Drop atau ',
                            html.A('Pilih File CSV', style={'textDecoration': 'underline'})
                        ]),
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                            'border': '3px dashed #000', 'textAlign': 'center',
                            'fontWeight': '700', 'fontSize': '12px', 'cursor': 'pointer',
                            'backgroundColor': '#FFF', 'textTransform': 'uppercase',
                            'letterSpacing': '0.04em'
                        }
                    ),
                ], className="input-group"),

                html.Div([
                    html.Label([
                        "Radius (ra) ",
                        html.Span("— jarak pandang SC", className="neo-label-hint")
                    ], className="neo-label"),
                    dcc.Input(id='in-ra', type='number', value=0.5, step=0.05, className="neo-input"),
                ], className="input-group"),

            ], className="col neo-card neo-card-green"),

            # Kanan: Parameter + Tombol Run
            html.Div([
                html.Div("2. Parameter Clustering", className="card-title"),

                html.Div([
                    html.Label("Fuzziness (m)", className="neo-label"),
                    dcc.Input(id='in-m', type='number', value=2.0, step=0.1, className="neo-input"),
                ], className="input-group"),

                html.Div([
                    html.Label("Max Iterasi", className="neo-label"),
                    dcc.Input(id='in-iter', type='number', value=100, step=10, className="neo-input"),
                ], className="input-group"),

                html.Button(
                    '▶ Jalankan Clustering',
                    id='btn-run', n_clicks=0,
                    className='neo-btn',
                    style={'backgroundColor': '#FF90E8'}
                ),
            ], className="col neo-card"),

        ], className="row"),

        # ── OUTPUT UTAMA ─────────────────────────────────────────────
        dcc.Loading(id="loading", type="default", color="#000", children=[

            html.Div(id='error-message'),

            # Metrik utama
            html.Div(id='metrics-row', className="row"),

            # Ringkasan cluster
            html.Div(id='cluster-summary-row', className="row"),

            # Peta Geospatial
            html.Div([
                html.Div("🌍 Peta Sebaran Kemiskinan", className="card-title"),
                dcc.Graph(id='map-plot', style={'height': '65vh'}, className="chart-wrap"),
            ], className="neo-card"),

            # Konvergensi & PCA
            html.Div([
                html.Div([
                    html.Div("📉 Konvergensi FCM", className="card-title"),
                    dcc.Graph(id='conv-plot', className="chart-wrap"),
                ], className="col neo-card"),
                html.Div([
                    html.Div("🔬 Visualisasi PCA (2D)", className="card-title"),
                    dcc.Graph(id='pca-plot', className="chart-wrap"),
                ], className="col neo-card"),
            ], className="row"),

            # Pie & Bar
            html.Div([
                html.Div([
                    html.Div("🥧 Distribusi Cluster", className="card-title"),
                    dcc.Graph(id='pie-plot', className="chart-wrap"),
                ], className="col neo-card"),
                html.Div([
                    html.Div("📊 Perbandingan Indikator Kunci", className="card-title"),
                    dcc.Graph(id='bar-plot', className="chart-wrap"),
                ], className="col neo-card"),
            ], className="row"),

            # Heatmap
            html.Div([
                html.Div("🌡️ Heatmap Profil Pusat Cluster (Normalized)", className="card-title"),
                dcc.Graph(id='heatmap-plot', className="chart-wrap"),
            ], className="neo-card"),

            # Tabel Pusat Cluster
            html.Div([
                html.Div("🎯 Nilai Pusat Cluster (Asli)", className="card-title"),
                html.Div(id='centroid-table'),
            ], className="neo-card"),

            # Tabel Statistik Provinsi
            html.Div([
                html.Div("📊 Statistik Kemiskinan per Provinsi", className="card-title"),
                html.Div(id='prov-table'),
            ], className="neo-card"),

            # Tabel Data Lengkap
            html.Div([
                html.Div("📋 Tabel Hasil Klasifikasi Lengkap", className="card-title"),
                html.Div(id='data-table'),
            ], className="neo-card"),

        ]),
    ], className="neo-container")