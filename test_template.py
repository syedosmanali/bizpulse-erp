from flask import Flask, render_template
import traceback

app = Flask(__name__, template_folder='frontend/screens/templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

with app.app_context():
    try:
        result = render_template('erp_products.html')
        print("✓ Template rendered successfully!")
        print(f"Length: {len(result)} bytes")
    except Exception as e:
        print("✗ Template rendering failed:")
        print(f"Error: {e}")
        traceback.print_exc()
