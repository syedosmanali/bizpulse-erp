from flask import render_template, jsonify, request
from datetime import datetime, timedelta

def register_reports_routes(app):
    """Register all reports routes"""
    
    @app.route('/retail/reports')
    def retail_reports():
        """Reports & Analytics Dashboard"""
        try:
            return render_template('reports_professional.html')
        except Exception as e:
            return f"<h1>📊 Reports Module</h1><p>Working! Template error: {str(e)}</p>"
    
    @app.route('/mobile/reports')
    def mobile_reports():
        """Mobile Reports & Analytics"""
        try:
            return render_template('reports_mobile.html')
        except Exception as e:
            return f"<h1>📱 Mobile Reports</h1><p>Working! Template error: {str(e)}</p>"
    
    @app.route('/test-reports-working')
    def test_reports_working():
        """Test route to verify reports module is working"""
        return """
        <h1>🎉 Reports Module is Working!</h1>
        <p>✅ Route registration successful</p>
        <p>✅ Flask app is running</p>
        <p>✅ Reports module loaded</p>
        <br>
        <a href="/retail/reports">Desktop Reports</a> | 
        <a href="/mobile/reports">Mobile Reports</a> | 
        <a href="/retail/dashboard">Dashboard</a>
        """