# 🌐 bizpulse24.com Domain Setup Guide

## ✅ STEP 1: Render.com Custom Domain
1. Go to your Render dashboard
2. Click on your **bizpulse-erp** service
3. Go to **Settings** tab
4. Scroll to **Custom Domains** section
5. Click **"Add Custom Domain"**
6. Add these domains:
   - `bizpulse24.com`
   - `www.bizpulse24.com`

## ✅ STEP 2: DNS Configuration
**Go to your domain provider (where you bought bizpulse24.com)**

### Add these DNS Records:

**Record 1:**
- **Type**: CNAME
- **Name**: www
- **Value**: bizpulse-erp.onrender.com
- **TTL**: 3600 (or Auto)

**Record 2:**
- **Type**: A
- **Name**: @ (or root/blank)
- **Value**: 216.24.57.1
- **TTL**: 3600 (or Auto)

## ✅ STEP 3: Wait & Verify
- DNS changes take 5-30 minutes
- Render will automatically provide SSL (HTTPS)
- Your site will be live at: https://bizpulse24.com

## 🎯 Final URLs:
- **Main Website**: https://bizpulse24.com
- **Mobile ERP**: https://bizpulse24.com/mobile-simple
- **Client Management**: https://bizpulse24.com/client-management
- **WhatsApp Reports**: https://bizpulse24.com/whatsapp-sender

## 📱 Mobile App URLs:
- **Direct Access**: https://bizpulse24.com/mobile-simple
- **Login**: bizpulse.erp@gmail.com / demo123

## 🔧 Common Domain Providers:

### GoDaddy:
1. Login to GoDaddy
2. My Products → DNS
3. Add records above

### Namecheap:
1. Login to Namecheap
2. Domain List → Manage
3. Advanced DNS → Add records

### Cloudflare:
1. Login to Cloudflare
2. Select domain
3. DNS → Add records

## ⚡ Pro Tips:
- Use both www and non-www versions
- SSL certificate is automatic
- Changes take 5-30 minutes
- Test with: https://dnschecker.org

## 🆘 If Issues:
- Check DNS propagation: https://dnschecker.org
- Verify Render custom domain status
- Contact domain provider support

---
**Your BizPulse ERP will be live at bizpulse24.com! 🚀**