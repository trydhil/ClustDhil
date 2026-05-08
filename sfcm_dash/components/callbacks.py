# sfcm_dash/components/callbacks.py
import base64
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, html, dash_table

from algorithms.sfcm import subtractive_clustering, fuzzy_cmeans, build_label_map, evaluate_clustering
from utils.data_processing import load_and_preprocess, detect_columns
from utils.constants import CLUSTER_COLORS, FEAT_SHORT, FEATURE_COLS, COORDS

def register_callbacks(app):
    @app.callback(
        [Output('error-message', 'children'),
         Output('metrics-row', 'children'),
         Output('cluster-summary-row', 'children'),
         Output('map-plot', 'figure'),
         Output('conv-plot', 'figure'),
         Output('pca-plot', 'figure'),
         Output('pie-plot', 'figure'),
         Output('bar-plot', 'figure'),
         Output('heatmap-plot', 'figure'),
         Output('centroid-table', 'children'),
         Output('prov-table', 'children'),
         Output('data-table', 'children')],
        [Input('btn-run', 'n_clicks')],
        [State('upload-data', 'contents'), State('in-ra', 'value'), State('in-m', 'value'), State('in-iter', 'value')]
    )
    def update_dash(n_clicks, contents, ra, m_fuzz, max_iter):
        empty_fig = go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_visible=False, yaxis_visible=False)
        if not contents or n_clicks == 0:
            return html.Div(), [], [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div(), html.Div(), html.Div()

        try:
            # 1. PREPROCESSING
            content_type, content_string = contents.split(',')
            df, X, scaler, avail_cols = load_and_preprocess(base64.b64decode(content_string))
            
            # 2. RUN ALGORITHMS
            sc_centers, _ = subtractive_clustering(X, ra=ra)
            n_cl = len(sc_centers)
            if n_cl < 2: return html.Div("ERROR: Cluster < 2. Kecilkan nilai Radius (ra).", style={'color':'red', 'fontWeight':'bold'}), [], [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div(), html.Div(), html.Div()
            
            final_centers, U, obj_hist = fuzzy_cmeans(X, sc_centers, m=m_fuzz, max_iter=max_iter)
            labels = np.argmax(U, axis=0)
            dbi, sil = evaluate_clustering(X, labels)
            
            centers_orig = scaler.inverse_transform(final_centers)
            label_map = build_label_map(centers_orig, n_cl)
            
            df['Cluster_ID'] = labels
            df['Cluster'] = [label_map[l] for l in labels]
            df['Memb_Max_%'] = (np.max(U, axis=0)*100).round(2)
            
            # 3. METRICS UI
            metrics_ui = [
                html.Div([html.Div("CLUSTER", className="neo-label"), html.Div(n_cl, className="metric-val")], className="col metric-box"),
                html.Div([html.Div("ITERASI", className="neo-label"), html.Div(len(obj_hist), className="metric-val")], className="col metric-box"),
                html.Div([html.Div("DBI", className="neo-label"), html.Div(f"{dbi:.4f}", className="metric-val")], className="col metric-box"),
                html.Div([html.Div("SILHOUETTE", className="neo-label"), html.Div(f"{sil:.4f}", className="metric-val")], className="col metric-box"),
                html.Div([html.Div("TOTAL DAERAH", className="neo-label"), html.Div(len(df), className="metric-val")], className="col metric-box"),
            ]

            # 4. CLUSTER SUMMARY CHIPS
            summary_ui = []
            for i in range(n_cl):
                n_i = (labels == i).sum()
                pct = n_i / len(labels) * 100
                p0c = centers_orig[i][0]
                color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
                box = html.Div([
                    html.Div(f"Cluster {i+1}", style={'fontWeight':'bold', 'color': color}),
                    html.Div(label_map[i], style={'fontSize':'14px'}),
                    html.Div(n_i, style={'fontSize':'24px', 'fontWeight':'bold'}),
                    html.Div(f"daerah ({pct:.1f}%)", style={'fontSize':'12px'}),
                    html.Div(f"P0 Avg: {p0c:.2f}%", style={'marginTop':'5px', 'borderTop':'2px solid #000'})
                ], className="col metric-box", style={'border': f'4px solid {color}'})
                summary_ui.append(box)

            # 5. GEOSPATIAL MAP
            kab_col, prov_col = detect_columns(df)
            df['lat'] = df[kab_col].apply(lambda x: COORDS.get(str(x).strip(), (None, None))[0])
            df['lon'] = df[kab_col].apply(lambda x: COORDS.get(str(x).strip(), (None, None))[1])
            df_map = df.dropna(subset=['lat', 'lon'])
            
            map_fig = px.scatter_mapbox(
                df_map, lat="lat", lon="lon", hover_name=kab_col, hover_data={"Cluster":True, avail_cols[0]:True, "lat":False, "lon":False},
                color="Cluster", color_discrete_sequence=CLUSTER_COLORS, zoom=4.5, center={"lat": -2.5, "lon": 118.0},
                mapbox_style="carto-positron"
            )
            map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='#FFF', font_family="Space Grotesk")
            map_fig.update_traces(marker=dict(size=12))

            # 6. CONVERGENCE PLOT
            conv = px.line(y=obj_hist, x=range(1, len(obj_hist)+1), markers=True, template="simple_white")
            conv.update_traces(line_color="#000", marker_color="#FF3B30", line_width=3, marker_size=8, marker_line_width=2, marker_line_color="#000")
            conv.update_layout(xaxis_title="Iterasi", yaxis_title="J (Objective)", margin=dict(l=20, r=20, t=30, b=20), font_family="Space Grotesk")

            # 7. PCA PLOT
            pca_fig = px.scatter(x=X[:,0], y=X[:,1], color=df['Cluster'], color_discrete_sequence=CLUSTER_COLORS, template="simple_white")
            pca_fig.update_traces(marker=dict(size=10, line=dict(width=2, color='#000')))
            pca_fig.update_layout(xaxis_title="PC1", yaxis_title="PC2", legend_title="Cluster", margin=dict(l=20, r=20, t=30, b=20), font_family="Space Grotesk")

            # 8. PIE CHART
            pie = px.pie(df, names='Cluster', color_discrete_sequence=CLUSTER_COLORS)
            pie.update_traces(marker=dict(line=dict(color='#000', width=2)))
            pie.update_layout(margin=dict(l=20, r=20, t=30, b=20), font_family="Space Grotesk")

            # 9. BAR PROFILE PLOT
            key_idx = [0, 3, 5, 6, 7] # P0, IPM, Sanitasi, AirMinum, Pengangguran
            key_lbls = [FEAT_SHORT[i] for i in key_idx]
            bar_fig = go.Figure()
            for i in range(n_cl):
                vals = [float(final_centers[i, j]) for j in key_idx]
                bar_fig.add_trace(go.Bar(name=f'C{i+1}', x=key_lbls, y=vals, marker_color=CLUSTER_COLORS[i % len(CLUSTER_COLORS)], marker_line=dict(color='#000', width=2)))
            bar_fig.update_layout(barmode='group', template="simple_white", margin=dict(l=20, r=20, t=30, b=20), font_family="Space Grotesk")

            # 10. HEATMAP
            heatmap_data = final_centers[:, :10]
            y_labels = [f"C{i+1} ({label_map[i][:10]})" for i in range(n_cl)]
            hm_fig = px.imshow(heatmap_data, labels=dict(x="Indikator", y="Cluster", color="Nilai (0-1)"), x=FEAT_SHORT[:10], y=y_labels, color_continuous_scale="YlOrRd", text_auto=".2f", aspect="auto")
            hm_fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), font_family="Space Grotesk")

            # 11. CENTROID TABLE
            ctr_df = pd.DataFrame(centers_orig, columns=FEAT_SHORT[:len(avail_cols)], index=[f'Cluster {i+1} ({label_map[i]})' for i in range(n_cl)]).round(2).reset_index()
            ctr_df.rename(columns={'index': 'Cluster'}, inplace=True)
            tbl_ctr = dash_table.DataTable(
                data=ctr_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#000', 'color': '#FFF', 'fontWeight': 'bold'},
                style_cell={'border': '2px solid #000', 'padding': '8px', 'textAlign': 'center', 'fontFamily': 'Space Grotesk'}
            )

            # 12. PROVINCIAL TABLE (With Conditional Formatting!)
            if prov_col:
                prov_base = df.groupby(prov_col).agg(Total_Daerah=('Cluster', 'count'), Rata_P0=(avail_cols[0], 'mean')).reset_index()
                for ci in range(n_cl):
                    prov_base[f'Cluster_{ci+1}'] = df.groupby(prov_col)['Cluster_ID'].apply(lambda x: int((x == ci).sum())).values
                prov_stat = prov_base.sort_values('Rata_P0', ascending=False).round(2)
                
                tbl_prov = dash_table.DataTable(
                    data=prov_stat.to_dict('records'),
                    style_table={'overflowX': 'auto', 'height': '400px', 'overflowY': 'auto'},
                    style_header={'backgroundColor': '#000', 'color': '#FFF', 'fontWeight': 'bold', 'position':'sticky', 'top':0},
                    style_cell={'border': '2px solid #000', 'padding': '8px', 'textAlign': 'center', 'fontFamily': 'Space Grotesk'},
                    style_data_conditional=[
                        {'if': {'filter_query': '{Rata_P0} > 25', 'column_id': 'Rata_P0'}, 'backgroundColor': '#7f1d1d', 'color': 'white'},
                        {'if': {'filter_query': '{Rata_P0} > 18 && {Rata_P0} <= 25', 'column_id': 'Rata_P0'}, 'backgroundColor': '#b91c1c', 'color': 'white'},
                        {'if': {'filter_query': '{Rata_P0} > 12 && {Rata_P0} <= 18', 'column_id': 'Rata_P0'}, 'backgroundColor': '#b45309', 'color': 'white'},
                        {'if': {'filter_query': '{Rata_P0} > 7 && {Rata_P0} <= 12', 'column_id': 'Rata_P0'}, 'backgroundColor': '#365314', 'color': 'white'},
                        {'if': {'filter_query': '{Rata_P0} <= 7', 'column_id': 'Rata_P0'}, 'backgroundColor': '#14532d', 'color': 'white'}
                    ]
                )
            else:
                tbl_prov = html.Div("Data provinsi tidak ditemukan.", style={'fontStyle': 'italic'})

            # 13. DATA TABLE
            show_cols = [c for c in [prov_col, kab_col, 'Cluster', 'Memb_Max_%'] if c]
            tbl_data = dash_table.DataTable(
                data=df[show_cols].to_dict('records'),
                style_table={'overflowX': 'auto', 'height': '400px', 'overflowY': 'auto'},
                style_header={'backgroundColor': '#000', 'color': '#FFF', 'fontWeight': 'bold', 'position':'sticky', 'top':0},
                style_cell={'border': '2px solid #000', 'padding': '8px', 'textAlign': 'left', 'fontFamily': 'Space Grotesk'},
                page_action='none' # Scrollable
            )

            return html.Div(), metrics_ui, summary_ui, map_fig, conv, pca_fig, pie, bar_fig, hm_fig, tbl_ctr, tbl_prov, tbl_data

        except Exception as e:
            return html.Div(f"ERROR: {e}", style={'color':'red', 'fontWeight':'bold', 'fontSize':'20px', 'background':'#000', 'padding':'10px'}), [], [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div(), html.Div(), html.Div()