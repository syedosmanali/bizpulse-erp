#!/usr/bin/env python3
"""
Remove WhatsApp banner references from dashboard
"""

def remove_whatsapp_banner():
    with open('templates/retail_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all WhatsApp banner references
    content = content.replace("document.getElementById('whatsappBanner').style.display = 'none';", "// WhatsApp banner removed")
    content = content.replace("document.getElementById('whatsappBanner').style.display = 'flex';", "// WhatsApp banner removed")
    
    with open('templates/retail_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ WhatsApp banner references removed")

if __name__ == "__main__":
    remove_whatsapp_banner()