# sfcm_dash/components/layout.py
from dash import html, dcc

def create_layout():
    return html.Div([
        # HEADER
        html.Div([
            html.H1("🚀 SFCM Geospatial Dashboard", className="neo-title", style={'border': 'none', 'margin': 0, 'padding': 0}),
            html.P("Pemetaan Pusat Sebaran Kemiskinan — 514 Kabupaten/Kota Indonesia", style={'fontWeight': 'bold', 'marginTop': '5px'})
        ], className="neo-card neo-card-yellow", style={'textAlign': 'center', 'marginBottom': '30px'}),

        html.Div([
            # KONTROL PANEL
            html.Div([
                html.Label("1. Upload Data CSV", className="neo-label"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(['Drag & Drop atau ', html.A('Pilih File CSV', style={'textDecoration': 'underline'})]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px', 'border': '3px dashed #000', 
                        'textAlign': 'center', 'fontWeight': 'bold', 'cursor': 'pointer', 'backgroundColor': '#FFF', 
                        'marginBottom':'15px'
                    }
                ),
                html.Label("Radius (ra): Jarak pandang SC", className="neo-label"),
                dcc.Input(id='in-ra', type='number', value=0.5, step=0.05, className="neo-input"),
            ], className="col neo-card neo-card-green"),

            html.Div([
                html.Label("Fuzziness (m):", className="neo-label"),
                dcc.Input(id='in-m', type='number', value=2.0, step=0.1, className="neo-input"),
                html.Label("Max Iterasi:", className="neo-label"),
                dcc.Input(id='in-iter', type='number', value=100, step=10, className="neo-input"),
                html.Button('▶ JALANKAN CLUSTERING', id='btn-run', n_clicks=0, className='neo-btn', style={'marginTop': '10px', 'backgroundColor': '#FF90E8'})
            ], className="col neo-card"),
        ], className="row"),

        # WADAH OUTPUT UTAMA (Loading Spinner)
        dcc.Loading(
            id="loading",
            type="default",
            color="#000",
            children=[
                html.Div(id='error-message'),
                
                # Baris Metrik Utama (DBI, Silhouette, dll)
                html.Div(id='metrics-row', className="row", style={'marginBottom': '24px'}),
                
                # Baris Ringkasan Cluster (Jumlah Daerah, P0 Avg)
                html.Div(id='cluster-summary-row', className="row", style={'marginBottom': '24px'}),

                # Peta Geospatial Mapbox
                html.Div([
                    html.H3("🌍 PETA SEBARAN KEMISKINAN", className="neo-label"),
                    dcc.Graph(id='map-plot', style={'height': '65vh', 'border': '4px solid #000'})
                ], className="neo-card", style={'padding': '0', 'border': 'none', 'backgroundColor': 'transparent'}),

                # Baris Grafik 1: Konvergensi & PCA
                html.Div([
                    html.Div([
                        html.H3("📉 KONVERGENSI FCM", className="neo-label"),
                        dcc.Graph(id='conv-plot', style={'border': '3px solid #000'})
                    ], className="col neo-card"),
                    html.Div([
                        html.H3("🔬 VISUALISASI PCA (2D)", className="neo-label"),
                        dcc.Graph(id='pca-plot', style={'border': '3px solid #000'})
                    ], className="col neo-card"),
                ], className="row"),

                # Baris Grafik 2: Pie Chart & Bar Chart Indikator
                html.Div([
                    html.Div([
                        html.H3("🥧 DISTRIBUSI CLUSTER", className="neo-label"),
                        dcc.Graph(id='pie-plot', style={'border': '3px solid #000'})
                    ], className="col neo-card"),
                    html.Div([
                        html.H3("📊 PERBANDINGAN INDIKATOR KUNCI", className="neo-label"),
                        dcc.Graph(id='bar-plot', style={'border': '3px solid #000'})
                    ], className="col neo-card"),
                ], className="row"),

                # Heatmap Profil
                html.Div([
                    html.H3("🌡️ HEATMAP PROFIL PUSAT CLUSTER (NORMALIZED)", className="neo-label"),
                    dcc.Graph(id='heatmap-plot', style={'border': '3px solid #000'})
                ], className="neo-card"),

                # Tabel Pusat Cluster
                html.Div([
                    html.H3("🎯 NILAI PUSAT CLUSTER (ASLI)", className="neo-label"),
                    html.Div(id='centroid-table')
                ], className="neo-card"),

                # Tabel Statistik Provinsi
                html.Div([
                    html.H3("📊 STATISTIK KEMISKINAN PER PROVINSI", className="neo-label"),
                    html.Div(id='prov-table')
                ], className="neo-card"),

                # Tabel Data Lengkap
                html.Div([
                    html.H3("📋 TABEL HASIL KLASIFIKASI LENGKAP", className="neo-label"),
                    html.Div(id='data-table')
                ], className="neo-card")
            ]
        )
    ], className="neo-container")