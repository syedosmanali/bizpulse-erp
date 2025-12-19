#!/usr/bin/env python3
"""
Simple Test App for Device Detection
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)

MOBILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MOBILE VERSION</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="background: red; color: white; text-align: center; padding: 50px;">
    <h1>📱 MOBILE INTERFACE</h1>
    <p>User Agent: {{ user_agent }}</p>
    <p>Device: Mobile/Tablet</p>
    <a href="/?desktop=1" style="color: yellow;">Switch to Desktop</a>
</body>
</html>
"""

DESKTOP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DESKTOP VERSION</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="background: blue; color: white; text-align: center; padding: 50px;">
    <h1>🖥️ DESKTOP INTERFACE</h1>
    <p>User Agent: {{ user_agent }}</p>
    <p>Device: Desktop</p>
    <a href="/" style="color: yellow;">Auto Detect</a>
</body>
</html>
"""

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Mobile detection
    is_mobile = any(device in user_agent for device in [
        'mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone', 'ipad', 'tablet'
    ])
    
    force_desktop = request.args.get('desktop') == '1'
    
    if is_mobile and not force_desktop:
        return render_template_string(MOBILE_TEMPLATE, user_agent=user_agent)
    else:
        return render_template_string(DESKTOP_TEMPLATE, user_agent=user_agent)

if __name__ == '__main__':
    app.run(debug=True, port=5001)