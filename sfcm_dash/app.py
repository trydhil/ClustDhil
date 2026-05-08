# sfcm_dash/app.py
import dash
from components.layout import create_layout
from components.callbacks import register_callbacks

# Inisialisasi Aplikasi Plotly Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Neobrutalism SFCM Dashboard"

# Setup Layout
app.layout = create_layout()

# Daftarkan Callbacks (Logika Interaktif)
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8050)