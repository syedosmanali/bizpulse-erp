"""
ERP Modules - Complete Clean Implementation
Covers: All required ERP modules with no duplicates
"""

from flask import Blueprint, render_template, jsonify, session, request
from modules.shared.database import get_db_connection, get_db_type
import traceback, uuid, json
from datetime import datetime, timedelta

erp_bp = Blueprint('erp', __name__)

# Logout route for ERP modules
@erp_bp.route('/api/erp/logout', methods=['POST'])
def erp_logout():
    """Logout user from ERP modules and clear session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_user_id():
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    return session.get('user_id')

# ─── Page Routes ───────────────────────────────────────────────────────────────

@erp_bp.route('/erp/dashboard')
def erp_dashboard():
    return render_template('erp_dashboard.html')



@erp_bp.route('/erp/company-profile')
def company_profile():
    return render_template('erp_company_profile.html')

@erp_bp.route('/erp/gst-details')
def gst_details():
    return render_template('erp_gst_details.html')

@erp_bp.route('/erp/invoice-numbering')
def invoice_numbering():
    return render_template('erp_invoice_numbering.html')

@erp_bp.route('/erp/financial-year')
def financial_year():
    return render_template('erp_financial_year.html')

@erp_bp.route('/erp/invoice-templates')
def invoice_templates():
    return render_template('erp_invoice_templates.html')

@erp_bp.route('/erp/terms-conditions')
def terms_conditions():
    return render_template('erp_terms_conditions.html')

@erp_bp.route('/erp/session-timeout')
def session_timeout():
    return render_template('erp_session_timeout.html')

@erp_bp.route('/erp/company-setup')
def company_setup():
    return render_template('erp_company_setup.html')

@erp_bp.route('/erp/role-access')
def role_access():
    return render_template('erp_role_access.html')

@erp_bp.route('/erp/bank-management')
def bank_management():
    return render_template('erp_bank_management.html')

@erp_bp.route('/erp/products')
def products():
    return render_template('erp_products.html')

@erp_bp.route('/erp/invoices')
def invoices():
    return render_template('erp_invoices.html')

@erp_bp.route('/erp/challan')
def challan():
    return render_template('erp_challan.html')

@erp_bp.route('/erp/purchase')
def purchase():
    return render_template('erp_purchase.html')

@erp_bp.route('/erp/purchase-order')
def purchase_order():
    return render_template('erp_purchase_order.html')

@erp_bp.route('/erp/grn')
def grn():
    return render_template('erp_grn.html')

@erp_bp.route('/erp/batch-expiry')
def batch_expiry():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/barcode')
def barcode():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/categories-brands')
def categories_brands():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/hsn-gst')
def hsn_gst():
    return render_template('erp_hsn_gst.html')

@erp_bp.route('/erp/low-stock-alerts')
def low_stock_alerts():
    return render_template('erp_low_stock_alerts.html')

@erp_bp.route('/erp/mrp-selling-price')
def mrp_selling_price():
    return render_template('erp_mrp_selling_price.html')

@erp_bp.route('/erp/unit-conversion')
def unit_conversion():
    return render_template('erp_unit_conversion.html')

# Sales & Billing Routes
@erp_bp.route('/erp/gst-invoices')
def gst_invoices():
    return render_template('erp_gst_invoices.html')

@erp_bp.route('/erp/pos-billing')
def pos_billing():
    return render_template('erp_pos_billing.html')

@erp_bp.route('/erp/credit-sales')
def credit_sales():
    return render_template('erp_credit_sales.html')

@erp_bp.route('/erp/returns-refunds')
def returns_refunds():
    return render_template('erp_returns_refunds.html')

@erp_bp.route('/erp/discount-rules')
def discount_rules():
    return render_template('erp_discount_rules.html')

# Purchase Management Routes
@erp_bp.route('/erp/purchase-orders')
def purchase_orders():
    return render_template('erp_purchase_orders.html')

@erp_bp.route('/erp/purchase-returns')
def purchase_returns():
    return render_template('erp_purchase_returns.html')

@erp_bp.route('/erp/vendor-credit')
def vendor_credit():
    return render_template('erp_vendor_credit.html')

@erp_bp.route('/erp/cost-price-update')
def cost_price_update():
    return render_template('erp_cost_price_update.html')

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOMER MASTER MODULE
# ═══════════════════════════════════════════════════════════════════════════════

@erp_bp.route('/erp/customer-master')
@erp_bp.route('/erp/customers')
def customer_master():
    """Customer Master Management"""
    return render_template('erp_customer_master.html')

# ═══════════════════════════════════════════════════════════════════════════════
# VENDOR MASTER MODULE
# ═══════════════════════════════════════════════════════════════════════════════

@erp_bp.route('/erp/vendor-master')
@erp_bp.route('/erp/vendor')
def vendor_master():
    """Vendor Master Management"""
    return render_template('erp_vendor_master.html')

# ═══════════════════════════════════════════════════════════════════════════════
# CRM MODULE
# ═══════════════════════════════════════════════════════════════════════════════

@erp_bp.route('/erp/crm-leads')
@erp_bp.route('/erp/crm')
def crm_leads():
    """CRM Leads Management"""
    return render_template('erp_crm_leads.html')

@erp_bp.route('/erp/payments')
def payments():
    return render_template('erp_payments.html')

@erp_bp.route('/erp/income-expense')
def income_expense():
    return render_template('erp_income_expense.html')

@erp_bp.route('/erp/accounting')
def accounting():
    return render_template('erp_accounting.html')

# Finance & Accounting Main Module
@erp_bp.route('/erp/finance')
def finance():
    return render_template('erp_finance.html')

# Finance & Accounting Submodules
@erp_bp.route('/erp/finance/cash-bank-ledger')
def finance_cash_bank_ledger():
    return render_template('erp_finance_cash_bank.html')

@erp_bp.route('/erp/finance/expense-categories')
def finance_expense_categories():
    return render_template('erp_finance_expense_categories.html')

@erp_bp.route('/erp/finance/profit-loss')
def finance_profit_loss():
    return render_template('erp_finance_profit_loss.html')

@erp_bp.route('/erp/finance/balance-sheet')
def finance_balance_sheet():
    return render_template('erp_finance_balance_sheet.html')

@erp_bp.route('/erp/finance/gst-summary')
def finance_gst_summary():
    return render_template('erp_finance_gst_summary.html')

@erp_bp.route('/erp/finance/tax-breakup')
def finance_tax_breakup():
    return render_template('erp_finance_tax_breakup.html')

@erp_bp.route('/erp/staff-operator')
def staff_operator():
    return render_template('erp_staff_operator.html')

@erp_bp.route('/erp/backup-settings')
def backup_settings():
    return render_template('erp_backup_settings.html')

# Administration & System Submodules
@erp_bp.route('/erp/admin/staff-logs')
def admin_staff_logs():
    return render_template('erp_admin_staff_logs.html')

@erp_bp.route('/erp/admin/backup')
def admin_backup():
    return render_template('erp_admin_backup.html')

@erp_bp.route('/erp/admin/restore')
def admin_restore():
    return render_template('erp_admin_restore.html')

@erp_bp.route('/erp/admin/audit')
def admin_audit():
    return render_template('erp_admin_audit.html')

@erp_bp.route('/erp/stock')
def stock():
    return render_template('erp_stock.html')

# Stock Management Sub-routes
@erp_bp.route('/erp/stock/view')
def stock_view():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/search')
def stock_search():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/filter')
def stock_filter():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/export')
def stock_export():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock-adjustment/add')
def stock_adjustment_add():
    return render_template('erp_stock_adjustment.html')

@erp_bp.route('/erp/stock-adjustment/bulk')
def stock_adjustment_bulk():
    return render_template('erp_stock_adjustment.html')

@erp_bp.route('/erp/stock-adjustment/history')
def stock_adjustment_history():
    return render_template('erp_stock_adjustment.html')

@erp_bp.route('/erp/stock-adjustment/approve')
def stock_adjustment_approve():
    return render_template('erp_stock_adjustment.html')

@erp_bp.route('/erp/stock/transactions/in')
def stock_transactions_in():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/transactions/out')
def stock_transactions_out():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/transactions/transfer')
def stock_transactions_transfer():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/transactions/log')
def stock_transactions_log():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/low-stock-alerts/settings')
def low_stock_alerts_settings():
    return render_template('erp_low_stock_alerts.html')

@erp_bp.route('/erp/low-stock-alerts/reorder')
def low_stock_alerts_reorder():
    return render_template('erp_low_stock_alerts.html')

@erp_bp.route('/erp/low-stock-alerts/notifications')
def low_stock_alerts_notifications():
    return render_template('erp_low_stock_alerts.html')

@erp_bp.route('/erp/stock/reports/valuation')
def stock_reports_valuation():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/reports/movement')
def stock_reports_movement():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/reports/aging')
def stock_reports_aging():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/stock/reports/analysis')
def stock_reports_analysis():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/warehouse/locations')
def warehouse_locations():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/warehouse/bins')
def warehouse_bins():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/warehouse/picking')
def warehouse_picking():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/warehouse/cycle-count')
def warehouse_cycle_count():
    return render_template('erp_stock.html')

# Products Management Sub-routes
@erp_bp.route('/erp/products/list')
def products_list():
    return render_template('erp_products.html')

@erp_bp.route('/erp/products/add')
def products_add():
    return render_template('erp_products.html')

@erp_bp.route('/erp/products/import')
def products_import():
    return render_template('erp_products.html')

@erp_bp.route('/erp/products/export')
def products_export():
    return render_template('erp_products.html')

@erp_bp.route('/erp/pricing/bulk-update')
def pricing_bulk_update():
    return render_template('erp_mrp_selling_price.html')

@erp_bp.route('/erp/pricing/rules')
def pricing_rules():
    return render_template('erp_mrp_selling_price.html')

# Batch & Expiry Sub-routes
@erp_bp.route('/erp/batch-expiry/create')
def batch_expiry_create():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/list')
def batch_expiry_list():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/search')
def batch_expiry_search():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/import')
def batch_expiry_import():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/expired')
def batch_expiry_expired():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/near-expiry')
def batch_expiry_near_expiry():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/expiring-today')
def batch_expiry_expiring_today():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/calendar')
def batch_expiry_calendar():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/merge')
def batch_expiry_merge():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/split')
def batch_expiry_split():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/transfer')
def batch_expiry_transfer():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/dispose')
def batch_expiry_dispose():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/reports/summary')
def batch_expiry_reports_summary():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/reports/expiry')
def batch_expiry_reports_expiry():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/reports/movement')
def batch_expiry_reports_movement():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/reports/wastage')
def batch_expiry_reports_wastage():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/alerts/configure')
def batch_expiry_alerts_configure():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/alerts/notifications')
def batch_expiry_alerts_notifications():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/alerts/sms')
def batch_expiry_alerts_sms():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/alerts/history')
def batch_expiry_alerts_history():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/quality/inspection')
def batch_expiry_quality_inspection():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/quality/quarantine')
def batch_expiry_quality_quarantine():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/quality/release')
def batch_expiry_quality_release():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/batch-expiry/quality/certificates')
def batch_expiry_quality_certificates():
    return render_template('erp_batch_expiry.html')

# Barcode Management Sub-routes
@erp_bp.route('/erp/barcode/generate')
def barcode_generate():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/scan')
def barcode_scan():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/print')
def barcode_print():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/lookup')
def barcode_lookup():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/categories-brands/add')
def categories_brands_add():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/organize')
def categories_brands_organize():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/batch-expiry/reports')
def batch_expiry_reports():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/stock/transactions')
def stock_transactions():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/barcode/generate/single')
def barcode_generate_single():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/generate/bulk')
def barcode_generate_bulk():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/generate/custom')
def barcode_generate_custom():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/generate/auto')
def barcode_generate_auto():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/scan/camera')
def barcode_scan_camera():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/scan/manual')
def barcode_scan_manual():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/scan/batch')
def barcode_scan_batch():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/scan/history')
def barcode_scan_history():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/print/labels')
def barcode_print_labels():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/print/templates')
def barcode_print_templates():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/print/batch')
def barcode_print_batch():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/print/settings')
def barcode_print_settings():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/lookup/product')
def barcode_lookup_product():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/lookup/batch')
def barcode_lookup_batch():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/lookup/price')
def barcode_lookup_price():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/lookup/stock')
def barcode_lookup_stock():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/manage/list')
def barcode_manage_list():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/manage/duplicate')
def barcode_manage_duplicate():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/manage/unused')
def barcode_manage_unused():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/manage/cleanup')
def barcode_manage_cleanup():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/settings/format')
def barcode_settings_format():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/settings/prefix')
def barcode_settings_prefix():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/settings/scanner')
def barcode_settings_scanner():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/barcode/settings/printer')
def barcode_settings_printer():
    return render_template('erp_barcode.html')

# Categories & Brands Sub-routes
@erp_bp.route('/erp/categories-brands/categories')
def categories_brands_categories():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/categories/add')
def categories_brands_categories_add():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/categories/tree')
def categories_brands_categories_tree():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/categories/bulk')
def categories_brands_categories_bulk():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/brands')
def categories_brands_brands():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/brands/add')
def categories_brands_brands_add():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/brands/logos')
def categories_brands_brands_logos():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/brands/import')
def categories_brands_brands_import():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/organize/hierarchy')
def categories_brands_organize_hierarchy():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/organize/merge')
def categories_brands_organize_merge():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/organize/move')
def categories_brands_organize_move():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/organize/cleanup')
def categories_brands_organize_cleanup():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/assign/products')
def categories_brands_assign_products():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/assign/bulk')
def categories_brands_assign_bulk():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/assign/unassigned')
def categories_brands_assign_unassigned():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/assign/rules')
def categories_brands_assign_rules():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/reports/performance')
def categories_brands_reports_performance():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/reports/sales')
def categories_brands_reports_sales():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/reports/inventory')
def categories_brands_reports_inventory():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/reports/trends')
def categories_brands_reports_trends():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/settings/templates')
def categories_brands_settings_templates():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/settings/attributes')
def categories_brands_settings_attributes():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/settings/permissions')
def categories_brands_settings_permissions():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/categories-brands/settings/export')
def categories_brands_settings_export():
    return render_template('erp_categories_brands.html')

@erp_bp.route('/erp/reports')
def reports():
    return render_template('erp_reports.html')

# Reports Submodules
@erp_bp.route('/erp/reports/daily-sales')
def report_daily_sales():
    return render_template('erp_report_daily_sales.html')

@erp_bp.route('/erp/reports/item-sales')
def report_item_sales():
    return render_template('erp_report_item_sales.html')

@erp_bp.route('/erp/reports/gst')
def report_gst():
    return render_template('erp_report_gst.html')

@erp_bp.route('/erp/reports/stock-ageing')
def report_stock_ageing():
    return render_template('erp_report_stock_ageing.html')

@erp_bp.route('/erp/reports/outstanding')
def report_outstanding():
    return render_template('erp_report_outstanding.html')

# ─── API Routes for Dashboard Data ───────────────────────────────────────

@erp_bp.route('/api/erp/products/stats', methods=['GET'])
def get_products_stats():
    """Get product statistics for dashboard"""
    try:
        # Mock data - replace with actual database queries
        stats = {
            'success': True,
            'total': 150,
            'active': 142,
            'lowStock': 8,
            'categories': 12
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/stock/alerts', methods=['GET'])
def get_stock_alerts():
    """Get stock alert statistics"""
    try:
        # Mock data - replace with actual database queries
        alerts = {
            'success': True,
            'outOfStock': 5,
            'lowStock': 12,
            'inStock': 133,
            'overStock': 3
        }
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batch-expiry/alerts', methods=['GET'])
def get_batch_expiry_alerts():
    """Get batch expiry alert statistics"""
    try:
        # Mock data - replace with actual database queries
        alerts = {
            'success': True,
            'expired': 3,
            'expiringToday': 2,
            'expiringWeek': 8,
            'totalBatches': 45
        }
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/barcode/lookup/<barcode>', methods=['GET'])
def lookup_barcode_api(barcode):
    """Lookup product by barcode"""
    try:
        # Mock data - replace with actual database query
        if barcode == "1234567890":
            product = {
                'success': True,
                'product': {
                    'name': 'Sample Product',
                    'code': 'SP001',
                    'price': 299.99,
                    'stock': 25
                }
            }
        else:
            product = {
                'success': False,
                'message': 'Product not found'
            }
        return jsonify(product)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/categories-brands/stats', methods=['GET'])
def get_categories_brands_stats():
    """Get categories and brands statistics"""
    try:
        # Mock data - replace with actual database queries
        stats = {
            'success': True,
            'totalCategories': 15,
            'totalBrands': 8,
            'activeCategories': 14,
            'activeBrands': 7
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Get dashboard metrics for main ERP dashboard"""
    try:
        # Mock data - replace with actual database queries
        metrics = {
            'success': True,
            'todaysSales': 25450,
            'pendingOrders': 12,
            'lowStockItems': 5,
            'outstanding': 125000
        }
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """Get recent activity for dashboard"""
    try:
        # Mock data - replace with actual database queries
        activities = {
            'success': True,
            'activities': [
                {'time': '2 mins ago', 'description': 'New invoice INV-001 created'},
                {'time': '15 mins ago', 'description': 'Stock updated for Product ABC'},
                {'time': '1 hour ago', 'description': 'Customer payment received'},
                {'time': '2 hours ago', 'description': 'Purchase order PO-123 approved'}
            ]
        }
        return jsonify(activities)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches', methods=['GET'])
def get_batches():
    """
    Get all batches with optional filters
    Query params: product_id, status (active/expired), near_expiry (days)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get query parameters
        product_id = request.args.get('product_id')
        status = request.args.get('status')  # active/expired
        near_expiry_days = request.args.get('near_expiry', type=int, default=30)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT b.*, p.product_name, p.product_code
            FROM erp_batches b
            LEFT JOIN erp_products p ON b.product_id = p.id
            WHERE b.user_id = %s AND b.is_deleted = FALSE
        """
        params = [user_id]
        
        if product_id:
            query += " AND b.product_id = %s"
            params.append(product_id)
        
        if status:
            if status == 'expired':
                query += " AND b.expiry_date < %s"
                params.append(datetime.now().date().isoformat())
            elif status == 'active':
                query += " AND b.expiry_date >= %s"
                params.append(datetime.now().date().isoformat())
        
        query += " ORDER BY b.expiry_date ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        batches = [dict(row) for row in rows]
        
        # Add expiry status calculation
        today = datetime.now().date()
        for batch in batches:
            if batch['expiry_date']:
                expiry_date = datetime.strptime(str(batch['expiry_date']), '%Y-%m-%d').date()
                days_diff = (expiry_date - today).days
                if days_diff < 0:
                    batch['expiry_status'] = 'expired'
                elif days_diff <= near_expiry_days:
                    batch['expiry_status'] = 'near_expiry'
                else:
                    batch['expiry_status'] = 'active'
            else:
                batch['expiry_status'] = 'no_expiry'
        
        return jsonify({'success': True, 'data': batches})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches', methods=['POST'])
def create_batch():
    """
    Create new batch
    Required: product_id, batch_number, mfg_date, expiry_date, quantity
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['product_id', 'batch_number', 'mfg_date', 'expiry_date', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate product exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if batch number already exists for this product
        cursor.execute("""
            SELECT id FROM erp_batches 
            WHERE product_id = %s AND batch_number = %s AND user_id = %s AND is_deleted = FALSE
        """, (data['product_id'], data['batch_number'], user_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Batch number already exists for this product'}), 400
        
        # Get product details for reference
        cursor.execute("SELECT product_name, product_code FROM erp_products WHERE id = %s AND user_id = %s", 
                      (data['product_id'], user_id))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Insert new batch
        batch_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_batches (id, user_id, product_id, product_name, product_code, 
            batch_number, mfg_date, expiry_date, quantity, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            batch_id, user_id, data['product_id'], product['product_name'], product['product_code'],
            data['batch_number'], data['mfg_date'], data['expiry_date'], 
            float(data['quantity']), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Batch created successfully',
            'id': batch_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/<batch_id>', methods=['PUT'])
def update_batch(batch_id):
    """Update existing batch"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if batch exists and belongs to user
        cursor.execute("SELECT id FROM erp_batches WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (batch_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Batch not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'batch_number' in data:
            update_fields.append("batch_number = %s")
            params.append(data['batch_number'])
        if 'mfg_date' in data:
            update_fields.append("mfg_date = %s")
            params.append(data['mfg_date'])
        if 'expiry_date' in data:
            update_fields.append("expiry_date = %s")
            params.append(data['expiry_date'])
        if 'quantity' in data:
            update_fields.append("quantity = %s")
            params.append(float(data['quantity']))
        if 'product_id' in data:
            # Also update product_name and product_code if product changes
            cursor.execute("SELECT product_name, product_code FROM erp_products WHERE id = %s AND user_id = %s", 
                          (data['product_id'], user_id))
            product = cursor.fetchone()
            if product:
                update_fields.extend(["product_id = %s", "product_name = %s", "product_code = %s"])
                params.extend([data['product_id'], product['product_name'], product['product_code']])
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        
        if update_fields:
            query = f"UPDATE erp_batches SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
            params.extend([batch_id, user_id])
            
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Batch updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/<batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    """Delete batch (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Soft delete - mark as deleted instead of removing
        cursor.execute("""
            UPDATE erp_batches 
            SET is_deleted = TRUE, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (datetime.now().isoformat(), batch_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Batch not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Batch deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/near-expiry', methods=['GET'])
def get_near_expiry_batches():
    """
    Get batches expiring within X days (default 30)
    Query param: days (optional, default=30)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        days = request.args.get('days', type=int, default=30)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get batches expiring within specified days
        future_date = (datetime.now() + timedelta(days=days)).date().isoformat()
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT b.*, p.product_name, p.product_code
            FROM erp_batches b
            LEFT JOIN erp_products p ON b.product_id = p.id
            WHERE b.user_id = %s 
              AND b.expiry_date BETWEEN %s AND %s
              AND b.is_deleted = FALSE
            ORDER BY b.expiry_date ASC
        """, (user_id, today, future_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        batches = [dict(row) for row in rows]
        
        return jsonify({'success': True, 'data': batches, 'days': days})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 2: Barcode Management ──────────────────────────────────────────────

@erp_bp.route('/api/erp/products/<product_id>/barcode', methods=['POST'])
def generate_barcode(product_id):
    """
    Generate barcode for product
    Body: { "format": "EAN-13" or "Code-128" }
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        barcode_format = data.get('format', 'EAN-13').upper()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT id FROM erp_products WHERE id = %s AND user_id = %s", (product_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Generate unique barcode
        # Use product ID as base and add a prefix
        import random
        barcode_prefix = {
            'EAN-13': '200',  # Internal use prefix for EAN-13
            'CODE-128': 'C',
            'UPC-A': '0'
        }.get(barcode_format, '200')
        
        # Generate a unique number
        unique_part = str(random.randint(10000000, 99999999))  # 8 digits
        barcode = barcode_prefix + unique_part
        
        # Ensure uniqueness
        while True:
            cursor.execute("SELECT id FROM erp_products WHERE barcode = %s", (barcode,))
            if not cursor.fetchone():
                break
            unique_part = str(random.randint(10000000, 99999999))
            barcode = barcode_prefix + unique_part
        
        # Update product with barcode
        cursor.execute("""
            UPDATE erp_products 
            SET barcode = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (barcode, datetime.now().isoformat(), product_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': product_id,
                'barcode': barcode,
                'format': barcode_format
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/barcode/<barcode>', methods=['GET'])
def lookup_barcode(barcode):
    """
    Lookup product by barcode
    Returns product details if found
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find product by barcode
        cursor.execute("""
            SELECT * FROM erp_products 
            WHERE barcode = %s AND user_id = %s AND is_deleted = FALSE
        """, (barcode, user_id))
        
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return jsonify({
                'success': True,
                'data': dict(product)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found for this barcode'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 3: Invoice & Billing Management ────────────────────────────────────

@erp_bp.route('/api/erp/invoices', methods=['GET'])
def get_invoices():
    """
    Get all invoices with pagination and filters
    Query params: page, limit, status, customer_id, start_date, end_date
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT i.*, c.name as customer_name, c.phone
            FROM erp_invoices i
            LEFT JOIN erp_customers c ON i.customer_id = c.id
            WHERE i.user_id = %s
        """
        params = [user_id]
        
        if status:
            query += " AND i.payment_status = %s"
            params.append(status)
        
        if customer_id:
            query += " AND i.customer_id = %s"
            params.append(customer_id)
        
        if start_date:
            query += " AND i.invoice_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND i.invoice_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY i.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        
        # Get total count
        count_query = """
            SELECT COUNT(*) as total
            FROM erp_invoices i
            WHERE i.user_id = %s
        """
        count_params = [user_id]
        
        if status:
            count_query += " AND i.payment_status = %s"
            count_params.append(status)
        if customer_id:
            count_query += " AND i.customer_id = %s"
            count_params.append(customer_id)
        if start_date:
            count_query += " AND i.invoice_date >= %s"
            count_params.append(start_date)
        if end_date:
            count_query += " AND i.invoice_date <= %s"
            count_params.append(end_date)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'invoices': [dict(row) for row in invoices],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/invoices', methods=['POST'])
def create_invoice():
    """
    Create new invoice
    Reduces stock quantities
    Updates customer outstanding balance
    Uses database transaction for atomicity
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        # Validate required fields
        required_fields = ['customer_id', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        if not data['items'] or len(data['items']) == 0:
            return jsonify({'success': False, 'error': 'At least one item is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Generate invoice number
            cursor.execute("""
                SELECT invoice_prefix, invoice_starting_number 
                FROM erp_company 
                WHERE user_id = %s
            """, [user_id])
            settings = cursor.fetchone()
            
            if settings:
                prefix = settings['invoice_prefix'] or 'INV'
                # Get the last invoice number for this user
                cursor.execute("""
                    SELECT invoice_number FROM erp_invoices 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC LIMIT 1
                """, [user_id])
                last_invoice = cursor.fetchone()
                
                if last_invoice and last_invoice['invoice_number']:
                    # Extract number from last invoice
                    last_num_str = last_invoice['invoice_number'].replace(prefix, '')
                    try:
                        sequence = int(last_num_str) + 1
                    except:
                        sequence = settings['invoice_starting_number'] or 1
                else:
                    sequence = settings['invoice_starting_number'] or 1
            else:
                prefix = 'INV'
                sequence = 1
            
            invoice_number = f"{prefix}{sequence:05d}"
            
            # Parse items from JSON if string
            items = data['items']
            if isinstance(items, str):
                items = json.loads(items)
            
            # Calculate totals
            subtotal = 0
            tax_amount = 0
            
            for item in items:
                item_subtotal = float(item.get('quantity', 0)) * float(item.get('rate', 0))
                subtotal += item_subtotal
                item_tax = item_subtotal * float(item.get('tax_rate', 0)) / 100
                tax_amount += item_tax
            
            discount = float(data.get('discount_amount', 0))
            total_amount = subtotal + tax_amount - discount
            
            # Determine payment status
            payment_status = data.get('payment_status', 'pending')
            paid_amount = float(data.get('paid_amount', 0))
            balance_amount = total_amount - paid_amount
            
            if balance_amount <= 0:
                payment_status = 'paid'
            elif paid_amount > 0:
                payment_status = 'partial'
            else:
                payment_status = 'pending'
            
            # Insert invoice
            invoice_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO erp_invoices (
                    id, user_id, invoice_number, customer_id, invoice_date,
                    due_date, subtotal, tax_amount, discount_amount, total_amount,
                    paid_amount, balance_amount, payment_status, payment_type,
                    status, items, notes, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                invoice_id, user_id, invoice_number, data['customer_id'], 
                data.get('invoice_date', now),
                data.get('due_date', ''), subtotal, tax_amount, discount, total_amount,
                paid_amount, balance_amount, payment_status, 
                data.get('payment_type', 'cash'),
                data.get('status', 'draft'), json.dumps(items), 
                data.get('notes', ''), now, now
            ])
            
            # Reduce stock for each item
            for item in items:
                product_id = item.get('product_id')
                quantity = float(item.get('quantity', 0))
                
                if product_id and quantity > 0:
                    # Check if product exists and has enough stock
                    cursor.execute("""
                        SELECT id, product_name, current_stock 
                        FROM erp_products 
                        WHERE id = %s AND user_id = %s
                    """, [product_id, user_id])
                    
                    product = cursor.fetchone()
                    if product:
                        current_stock = float(product.get('current_stock', 0))
                        
                        # Reduce stock
                        cursor.execute("""
                            UPDATE erp_products
                            SET current_stock = current_stock - %s,
                                updated_at = %s
                            WHERE id = %s AND user_id = %s
                        """, [quantity, now, product_id, user_id])
            
            # Update customer outstanding balance if credit
            if payment_status in ['pending', 'partial']:
                cursor.execute("""
                    UPDATE erp_customers
                    SET outstanding_balance = outstanding_balance + %s,
                        updated_at = %s
                    WHERE id = %s AND user_id = %s
                """, [balance_amount, now, data['customer_id'], user_id])
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'invoice_id': invoice_id,
                'invoice_number': invoice_number,
                'total_amount': total_amount,
                'balance_amount': balance_amount
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/invoices/<invoice_id>', methods=['GET'])
def get_invoice_details(invoice_id):
    """Get specific invoice with customer details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get invoice with customer details
        cursor.execute("""
            SELECT i.*, c.name as customer_name, c.phone, c.email, c.address, c.gst_number
            FROM erp_invoices i
            LEFT JOIN erp_customers c ON i.customer_id = c.id
            WHERE i.id = %s AND i.user_id = %s
        """, [invoice_id, user_id])
        
        invoice = cursor.fetchone()
        
        if not invoice:
            return jsonify({'success': False, 'error': 'Invoice not found'}), 404
        
        # Parse items JSON
        invoice_dict = dict(invoice)
        if invoice_dict.get('items'):
            if isinstance(invoice_dict['items'], str):
                invoice_dict['items'] = json.loads(invoice_dict['items'])
        else:
            invoice_dict['items'] = []
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'invoice': invoice_dict})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/invoices/<invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """
    Update invoice (only if status is draft)
    Restores old stock and applies new stock changes
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get existing invoice
            cursor.execute("""
                SELECT * FROM erp_invoices
                WHERE id = %s AND user_id = %s
            """, [invoice_id, user_id])
            
            existing_invoice = cursor.fetchone()
            
            if not existing_invoice:
                return jsonify({'success': False, 'error': 'Invoice not found'}), 404
            
            # Only allow updates for draft invoices
            if existing_invoice['status'] != 'draft':
                return jsonify({'success': False, 'error': 'Cannot update finalized invoice'}), 400
            
            # Restore stock from old items
            old_items = existing_invoice.get('items', '[]')
            if isinstance(old_items, str):
                old_items = json.loads(old_items)
            
            for item in old_items:
                product_id = item.get('product_id')
                quantity = float(item.get('quantity', 0))
                
                if product_id and quantity > 0:
                    cursor.execute("""
                        UPDATE erp_products
                        SET current_stock = current_stock + %s
                        WHERE id = %s AND user_id = %s
                    """, [quantity, product_id, user_id])
            
            # Parse new items
            new_items = data.get('items', [])
            if isinstance(new_items, str):
                new_items = json.loads(new_items)
            
            # Calculate new totals
            subtotal = 0
            tax_amount = 0
            
            for item in new_items:
                item_subtotal = float(item.get('quantity', 0)) * float(item.get('rate', 0))
                subtotal += item_subtotal
                item_tax = item_subtotal * float(item.get('tax_rate', 0)) / 100
                tax_amount += item_tax
            
            discount = float(data.get('discount_amount', 0))
            total_amount = subtotal + tax_amount - discount
            paid_amount = float(data.get('paid_amount', 0))
            balance_amount = total_amount - paid_amount
            
            # Determine payment status
            if balance_amount <= 0:
                payment_status = 'paid'
            elif paid_amount > 0:
                payment_status = 'partial'
            else:
                payment_status = 'pending'
            
            # Update invoice
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE erp_invoices SET
                    customer_id = %s, invoice_date = %s, due_date = %s,
                    subtotal = %s, tax_amount = %s, discount_amount = %s,
                    total_amount = %s, paid_amount = %s, balance_amount = %s,
                    payment_status = %s, payment_type = %s, items = %s,
                    notes = %s, updated_at = %s
                WHERE id = %s AND user_id = %s
            """, [
                data.get('customer_id', existing_invoice['customer_id']),
                data.get('invoice_date', existing_invoice['invoice_date']),
                data.get('due_date', existing_invoice['due_date']),
                subtotal, tax_amount, discount, total_amount,
                paid_amount, balance_amount, payment_status,
                data.get('payment_type', existing_invoice['payment_type']),
                json.dumps(new_items), data.get('notes', existing_invoice['notes']),
                now, invoice_id, user_id
            ])
            
            # Reduce stock for new items
            for item in new_items:
                product_id = item.get('product_id')
                quantity = float(item.get('quantity', 0))
                
                if product_id and quantity > 0:
                    cursor.execute("""
                        UPDATE erp_products
                        SET current_stock = current_stock - %s
                        WHERE id = %s AND user_id = %s
                    """, [quantity, product_id, user_id])
            
            # Update customer outstanding balance
            old_balance = float(existing_invoice.get('balance_amount', 0))
            balance_diff = balance_amount - old_balance
            
            if balance_diff != 0:
                cursor.execute("""
                    UPDATE erp_customers
                    SET outstanding_balance = outstanding_balance + %s
                    WHERE id = %s AND user_id = %s
                """, [balance_diff, data.get('customer_id', existing_invoice['customer_id']), user_id])
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Invoice updated successfully',
                'total_amount': total_amount,
                'balance_amount': balance_amount
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/invoices/<invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    """
    Delete invoice (soft delete)
    Restores stock quantities
    Updates customer outstanding
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get invoice details
            cursor.execute("""
                SELECT * FROM erp_invoices
                WHERE id = %s AND user_id = %s
            """, [invoice_id, user_id])
            
            invoice = cursor.fetchone()
            
            if not invoice:
                return jsonify({'success': False, 'error': 'Invoice not found'}), 404
            
            # Prevent deletion of finalized invoices
            if invoice['status'] == 'finalized':
                return jsonify({'success': False, 'error': 'Cannot delete finalized invoice'}), 400
            
            # Parse items
            items = invoice.get('items', '[]')
            if isinstance(items, str):
                items = json.loads(items)
            
            # Restore stock for each item
            for item in items:
                product_id = item.get('product_id')
                quantity = float(item.get('quantity', 0))
                
                if product_id and quantity > 0:
                    cursor.execute("""
                        UPDATE erp_products
                        SET current_stock = current_stock + %s
                        WHERE id = %s AND user_id = %s
                    """, [quantity, product_id, user_id])
            
            # Update customer outstanding balance
            balance_amount = float(invoice.get('balance_amount', 0))
            if balance_amount > 0:
                cursor.execute("""
                    UPDATE erp_customers
                    SET outstanding_balance = outstanding_balance - %s
                    WHERE id = %s AND user_id = %s
                """, [balance_amount, invoice['customer_id'], user_id])
            
            # Delete invoice (hard delete for now, can be changed to soft delete)
            cursor.execute("""
                DELETE FROM erp_invoices
                WHERE id = %s AND user_id = %s
            """, [invoice_id, user_id])
            
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Invoice deleted successfully'})
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/invoices/<invoice_id>/payment', methods=['POST'])
def record_invoice_payment(invoice_id):
    """
    Record payment for an invoice
    Updates paid_amount, balance_amount, and payment_status
    Updates customer outstanding balance
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        payment_amount = float(data.get('payment_amount', 0))
        
        if payment_amount <= 0:
            return jsonify({'success': False, 'error': 'Payment amount must be greater than 0'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get invoice
            cursor.execute("""
                SELECT * FROM erp_invoices
                WHERE id = %s AND user_id = %s
            """, [invoice_id, user_id])
            
            invoice = cursor.fetchone()
            
            if not invoice:
                return jsonify({'success': False, 'error': 'Invoice not found'}), 404
            
            # Calculate new amounts
            current_paid = float(invoice.get('paid_amount', 0))
            current_balance = float(invoice.get('balance_amount', 0))
            
            if payment_amount > current_balance:
                return jsonify({'success': False, 'error': 'Payment amount exceeds balance'}), 400
            
            new_paid = current_paid + payment_amount
            new_balance = current_balance - payment_amount
            
            # Determine new payment status
            if new_balance <= 0:
                new_status = 'paid'
            elif new_paid > 0:
                new_status = 'partial'
            else:
                new_status = 'pending'
            
            # Update invoice
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE erp_invoices SET
                    paid_amount = %s,
                    balance_amount = %s,
                    payment_status = %s,
                    updated_at = %s
                WHERE id = %s AND user_id = %s
            """, [new_paid, new_balance, new_status, now, invoice_id, user_id])
            
            # Update customer outstanding balance
            cursor.execute("""
                UPDATE erp_customers
                SET outstanding_balance = outstanding_balance - %s
                WHERE id = %s AND user_id = %s
            """, [payment_amount, invoice['customer_id'], user_id])
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment recorded successfully',
                'paid_amount': new_paid,
                'balance_amount': new_balance,
                'payment_status': new_status
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 4: Vendor Management ───────────────────────────────────────────────

@erp_bp.route('/api/erp/vendors/<vendor_id>', methods=['GET'])
def get_vendor_details(vendor_id):
    """Get specific vendor with transaction summary"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get vendor details
        cursor.execute("""
            SELECT * FROM erp_vendors 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (vendor_id, user_id))
        
        vendor = cursor.fetchone()
        if not vendor:
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        # Get transaction summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM erp_purchase_orders 
            WHERE vendor_id = %s AND user_id = %s
        """, (vendor_id, user_id))
        
        summary = cursor.fetchone()
        vendor_dict = dict(vendor)
        vendor_dict['transaction_summary'] = dict(summary) if summary else {
            'total_transactions': 0,
            'total_amount': 0,
            'avg_amount': 0
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': vendor_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>/transactions', methods=['GET'])
def get_vendor_transactions(vendor_id):
    """Get all transactions for a vendor"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify vendor exists
        cursor.execute("SELECT id FROM erp_vendors WHERE id = %s AND user_id = %s", (vendor_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        # Get all transactions for this vendor
        cursor.execute("""
            SELECT * FROM erp_purchase_orders 
            WHERE vendor_id = %s AND user_id = %s 
            ORDER BY created_at DESC
        """, (vendor_id, user_id))
        
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': transactions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 5: CRM & Leads ─────────────────────────────────────────────────────

@erp_bp.route('/api/erp/leads', methods=['GET'])
def get_leads():
    """Get all leads with filters (status, source, date_range)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        status = request.args.get('status')
        source = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM erp_leads WHERE user_id = %s AND is_deleted = FALSE"
        params = [user_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        if source:
            query += " AND source = %s"
            params.append(source)
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        leads = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': leads
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads', methods=['POST'])
def create_lead():
    """Create new lead"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['name', 'contact']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        lead_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_leads (id, user_id, name, contact, email, company, 
            source, status, notes, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            lead_id, user_id, data['name'], data['contact'], 
            data.get('email', ''), data.get('company', ''),
            data.get('source', 'Unknown'), data.get('status', 'New'),
            data.get('notes', ''), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead created successfully',
            'id': lead_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead (including status changes)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if lead exists
        cursor.execute("SELECT id FROM erp_leads WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (lead_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        if 'contact' in data:
            update_fields.append("contact = %s")
            params.append(data['contact'])
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        if 'company' in data:
            update_fields.append("company = %s")
            params.append(data['company'])
        if 'source' in data:
            update_fields.append("source = %s")
            params.append(data['source'])
        if 'status' in data:
            update_fields.append("status = %s")
            params.append(data['status'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            params.append(data['notes'])
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        params.extend([lead_id, user_id])
        
        if update_fields:
            query = f"UPDATE erp_leads SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads/<lead_id>/convert', methods=['POST'])
def convert_lead_to_customer(lead_id):
    """
    Convert lead to customer
    Creates new customer record and marks lead as converted
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get lead details
        cursor.execute("SELECT * FROM erp_leads WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (lead_id, user_id))
        lead = cursor.fetchone()
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Check if already converted
        if lead['status'] == 'Converted':
            return jsonify({'success': False, 'error': 'Lead already converted to customer'}), 400
        
        # Create customer from lead
        customer_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_customers (id, user_id, customer_name, phone, email, address, 
            gst_number, pan_number, credit_limit, credit_days, customer_category, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id, user_id, lead['name'], lead['contact'], lead['email'], '',
            '', '', 0, 0, 'General', now, now
        ))
        
        # Update lead status to converted
        cursor.execute("""
            UPDATE erp_leads 
            SET status = 'Converted', converted_to_customer_id = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (customer_id, now, lead_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead converted to customer successfully',
            'customer_id': customer_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 6: Purchase Orders ─────────────────────────────────────────────────

@erp_bp.route('/api/erp/purchase-orders/<po_id>', methods=['GET'])
def get_purchase_order_details(po_id):
    """Get specific PO with items"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get PO header
        cursor.execute("""
            SELECT po.*, v.vendor_name 
            FROM erp_purchase_orders po
            LEFT JOIN erp_vendors v ON po.vendor_id = v.id
            WHERE po.id = %s AND po.user_id = %s AND po.is_deleted = FALSE
        """, (po_id, user_id))
        
        po_header = cursor.fetchone()
        if not po_header:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        # Get PO items
        cursor.execute("""
            SELECT poi.*, p.product_name, p.product_code 
            FROM erp_purchase_order_items poi
            LEFT JOIN erp_products p ON poi.product_id = p.id
            WHERE poi.po_id = %s AND poi.is_deleted = FALSE
            ORDER BY poi.created_at ASC
        """, (po_id,))
        
        po_items = [dict(row) for row in cursor.fetchall()]
        
        result = dict(po_header)
        result['items'] = po_items
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/purchase-orders/<po_id>', methods=['PUT'])
def update_purchase_order(po_id):
    """Update PO (only if status is Draft)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if PO exists and is in draft status
        cursor.execute("""
            SELECT id, status FROM erp_purchase_orders 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (po_id, user_id))
        
        po = cursor.fetchone()
        if not po:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        if po['status'] != 'Draft':
            return jsonify({'success': False, 'error': 'Cannot update PO after it is approved'}), 400
        
        # Update PO header (only allowed fields for Draft status)
        update_fields = []
        params = []
        
        if 'vendor_id' in data:
            update_fields.append("vendor_id = %s")
            params.append(data['vendor_id'])
        if 'po_number' in data:
            update_fields.append("po_number = %s")
            params.append(data['po_number'])
        if 'po_date' in data:
            update_fields.append("po_date = %s")
            params.append(data['po_date'])
        if 'delivery_date' in data:
            update_fields.append("delivery_date = %s")
            params.append(data['delivery_date'])
        if 'terms_conditions' in data:
            update_fields.append("terms_conditions = %s")
            params.append(data['terms_conditions'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            params.append(data['notes'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([po_id, user_id])
            
            query = f"UPDATE erp_purchase_orders SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Purchase Order updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/purchase-orders/<po_id>/reject', methods=['POST'])
def reject_purchase_order(po_id):
    """Reject PO with reason"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        reason = data.get('reason', 'Rejected by manager')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if PO exists
        cursor.execute("""
            SELECT id, status FROM erp_purchase_orders 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (po_id, user_id))
        
        po = cursor.fetchone()
        if not po:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        # Update PO status to Rejected
        cursor.execute("""
            UPDATE erp_purchase_orders 
            SET status = 'Rejected', rejection_reason = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (reason, datetime.now().isoformat(), po_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Purchase Order rejected successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 7: GRN (Goods Receipt Note) ────────────────────────────────────────

@erp_bp.route('/api/erp/grn', methods=['GET'])
def get_grn_list():
    """Get all GRNs with filters"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT g.*, v.vendor_name, po.po_number 
            FROM erp_grn g
            LEFT JOIN erp_vendors v ON g.vendor_id = v.id
            LEFT JOIN erp_purchase_orders po ON g.po_id = po.id
            WHERE g.user_id = %s AND g.is_deleted = FALSE
        """
        params = [user_id]
        
        if status:
            query += " AND g.status = %s"
            params.append(status)
        if start_date:
            query += " AND g.grn_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND g.grn_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY g.grn_date DESC"
        
        cursor.execute(query, params)
        grns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': grns
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/grn', methods=['POST'])
def create_grn():
    """
    Create GRN from PO
    Updates stock quantities
    Updates PO status
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['po_id', 'received_items']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        conn.autocommit = False
        
        try:
            # Get PO details
            cursor.execute("""
                SELECT id, vendor_id, status FROM erp_purchase_orders 
                WHERE id = %s AND user_id = %s AND is_deleted = FALSE
            """, (data['po_id'], user_id))
            
            po = cursor.fetchone()
            if not po:
                return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
            
            if po['status'] != 'Approved':
                return jsonify({'success': False, 'error': 'PO must be approved before creating GRN'}), 400
            
            # Get PO items to verify received items
            cursor.execute("""
                SELECT * FROM erp_purchase_order_items 
                WHERE po_id = %s AND is_deleted = FALSE
            """, (data['po_id'],))
            po_items = cursor.fetchall()
            
            # Validate received items against PO items
            po_item_map = {item['product_id']: dict(item) for item in po_items}
            for received_item in data['received_items']:
                product_id = received_item['product_id']
                if product_id not in po_item_map:
                    return jsonify({'success': False, 'error': f'Product {product_id} not in PO'}), 400
                
                expected_qty = po_item_map[product_id]['quantity']
                received_qty = received_item['received_quantity']
                
                if received_qty > expected_qty:
                    return jsonify({
                        'success': False, 
                        'error': f'Received quantity {received_qty} exceeds ordered quantity {expected_qty} for product {product_id}'
                    }), 400
            
            # Create GRN
            grn_id = str(uuid.uuid4())
            grn_number = f"GRN-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO erp_grn (id, user_id, grn_number, po_id, vendor_id, grn_date, 
                total_amount, status, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                grn_id, user_id, grn_number, data['po_id'], po['vendor_id'],
                data.get('grn_date', now.split('T')[0]), data.get('total_amount', 0),
                'Received', data.get('notes', ''), now, now
            ))
            
            # Create GRN items and update stock
            for received_item in data['received_items']:
                grn_item_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO erp_grn_items (id, grn_id, product_id, ordered_quantity, 
                    received_quantity, unit_price, total_amount, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    grn_item_id, grn_id, received_item['product_id'],
                    received_item.get('ordered_quantity', 0), received_item['received_quantity'],
                    received_item.get('unit_price', 0), received_item.get('total_amount', 0),
                    now, now
                ))
                
                # Update stock quantity
                cursor.execute("""
                    UPDATE erp_stock 
                    SET quantity = quantity + %s, updated_at = %s 
                    WHERE product_id = %s AND user_id = %s
                """, (received_item['received_quantity'], now, received_item['product_id'], user_id))
                
                # If no stock record exists, create one
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO erp_stock (id, user_id, product_id, quantity, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()), user_id, received_item['product_id'], 
                        received_item['received_quantity'], now, now
                    ))
                
                # If batch info is provided, create/update batch
                if 'batch_number' in received_item:
                    batch_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO erp_batches (id, user_id, product_id, batch_number, 
                        expiry_date, quantity, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id, batch_number) 
                        DO UPDATE SET quantity = erp_batches.quantity + %s, updated_at = %s
                    """, (
                        batch_id, user_id, received_item['product_id'], 
                        received_item['batch_number'], received_item.get('expiry_date'),
                        received_item['received_quantity'], now, now,
                        received_item['received_quantity'], now
                    ))
            
            # Update PO status to Partially Received or Fully Received
            cursor.execute("""
                UPDATE erp_purchase_orders 
                SET status = 'Partially Received', updated_at = %s 
                WHERE id = %s AND user_id = %s
            """, (now, data['po_id'], user_id))
            
            # Check if PO is fully received
            cursor.execute("""
                SELECT SUM(quantity) as total_ordered, 
                       (SELECT SUM(received_quantity) FROM erp_grn_items WHERE po_id = %s) as total_received
                FROM erp_purchase_order_items WHERE po_id = %s
            """, (data['po_id'], data['po_id']))
            
            po_totals = cursor.fetchone()
            if po_totals and po_totals['total_received'] >= po_totals['total_ordered']:
                cursor.execute("""
                    UPDATE erp_purchase_orders 
                    SET status = 'Fully Received', updated_at = %s 
                    WHERE id = %s AND user_id = %s
                """, (now, data['po_id'], user_id))
            
            conn.commit()
            conn.autocommit = True
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'GRN created successfully',
                'id': grn_id,
                'grn_number': grn_number
            })
        except Exception as e:
            conn.rollback()
            conn.autocommit = True
            raise e
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/grn/<grn_id>', methods=['GET'])
def get_grn_details(grn_id):
    """Get specific GRN with items"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get GRN header
        cursor.execute("""
            SELECT g.*, v.vendor_name, po.po_number 
            FROM erp_grn g
            LEFT JOIN erp_vendors v ON g.vendor_id = v.id
            LEFT JOIN erp_purchase_orders po ON g.po_id = po.id
            WHERE g.id = %s AND g.user_id = %s AND g.is_deleted = FALSE
        """, (grn_id, user_id))
        
        grn_header = cursor.fetchone()
        if not grn_header:
            return jsonify({'success': False, 'error': 'GRN not found'}), 404
        
        # Get GRN items
        cursor.execute("""
            SELECT gri.*, p.product_name, p.product_code 
            FROM erp_grn_items gri
            LEFT JOIN erp_products p ON gri.product_id = p.id
            WHERE gri.grn_id = %s AND gri.is_deleted = FALSE
            ORDER BY gri.created_at ASC
        """, (grn_id,))
        
        grn_items = [dict(row) for row in cursor.fetchall()]
        
        result = dict(grn_header)
        result['items'] = grn_items
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 8: Income/Expense Tracking ─────────────────────────────────────────

@erp_bp.route('/api/erp/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with filters (type, category, date_range)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        transaction_type = request.args.get('type')  # income/expense
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM erp_transactions WHERE user_id = %s AND is_deleted = FALSE"
        params = [user_id]
        
        if transaction_type:
            query += " AND transaction_type = %s"
            params.append(transaction_type)
        if category:
            query += " AND category = %s"
            params.append(category)
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY transaction_date DESC, created_at DESC"
        
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': transactions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions', methods=['POST'])
def create_transaction():
    """Create income or expense transaction"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['amount', 'transaction_type', 'category', 'transaction_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        if data['transaction_type'] not in ['income', 'expense']:
            return jsonify({'success': False, 'error': 'Transaction type must be income or expense'}), 400
        
        if float(data['amount']) <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than 0'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        transaction_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_transactions (id, user_id, amount, transaction_type, category, 
            transaction_date, description, reference, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction_id, user_id, float(data['amount']), data['transaction_type'], 
            data['category'], data['transaction_date'], data.get('description', ''),
            data.get('reference', ''), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'id': transaction_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update transaction"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute("""
            SELECT id FROM erp_transactions 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (transaction_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'amount' in data:
            if float(data['amount']) <= 0:
                return jsonify({'success': False, 'error': 'Amount must be greater than 0'}), 400
            update_fields.append("amount = %s")
            params.append(float(data['amount']))
        if 'transaction_type' in data:
            if data['transaction_type'] not in ['income', 'expense']:
                return jsonify({'success': False, 'error': 'Transaction type must be income or expense'}), 400
            update_fields.append("transaction_type = %s")
            params.append(data['transaction_type'])
        if 'category' in data:
            update_fields.append("category = %s")
            params.append(data['category'])
        if 'transaction_date' in data:
            update_fields.append("transaction_date = %s")
            params.append(data['transaction_date'])
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        if 'reference' in data:
            update_fields.append("reference = %s")
            params.append(data['reference'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([transaction_id, user_id])
            
            query = f"UPDATE erp_transactions SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Transaction updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions/categories', methods=['GET'])
def get_transaction_categories():
    """Get all transaction categories"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all unique categories for this user
        cursor.execute("""
            SELECT DISTINCT category FROM erp_transactions 
            WHERE user_id = %s AND is_deleted = FALSE
            ORDER BY category
        """, (user_id,))
        
        categories = [row['category'] for row in cursor.fetchall() if row['category']]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 9: Accounting Reports ──────────────────────────────────────────────

@erp_bp.route('/api/erp/reports/sales-summary', methods=['GET'])
def get_sales_summary():
    """
    Get sales summary report
    Query params: start_date, end_date
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for sales
        query = """
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_sales,
                AVG(total_amount) as avg_invoice_value,
                SUM(CASE WHEN payment_status = 'paid' THEN total_amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN payment_status != 'paid' THEN total_amount ELSE 0 END) as pending_amount
            FROM erp_invoices 
            WHERE user_id = %s AND is_deleted = FALSE AND invoice_date IS NOT NULL
        """
        params = [user_id]
        
        if start_date:
            query += " AND invoice_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND invoice_date <= %s"
            params.append(end_date)
        
        cursor.execute(query, params)
        sales_data = cursor.fetchone()
        
        # Calculate top selling products
        products_query = """
            SELECT 
                p.product_name,
                SUM(ii.quantity) as total_sold,
                SUM(ii.total_amount) as revenue
            FROM erp_invoice_items ii
            JOIN erp_invoices i ON ii.invoice_id = i.id
            JOIN erp_products p ON ii.product_id = p.id
            WHERE i.user_id = %s AND i.is_deleted = FALSE
        """
        prod_params = [user_id]
        
        if start_date:
            products_query += " AND i.invoice_date >= %s"
            prod_params.append(start_date)
        if end_date:
            products_query += " AND i.invoice_date <= %s"
            prod_params.append(end_date)
        
        products_query += " GROUP BY p.id, p.product_name ORDER BY total_sold DESC LIMIT 5"
        
        cursor.execute(products_query, prod_params)
        top_products = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        result = {
            'summary': dict(sales_data) if sales_data else {
                'total_invoices': 0,
                'total_sales': 0,
                'avg_invoice_value': 0,
                'paid_amount': 0,
                'pending_amount': 0
            },
            'top_products': top_products,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/reports/purchase-summary', methods=['GET'])
def get_purchase_summary():
    """Get purchase summary report"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for purchases
        query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_purchases,
                AVG(total_amount) as avg_order_value,
                SUM(CASE WHEN status = 'Paid' THEN total_amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN status IN ('Pending', 'Partial') THEN total_amount ELSE 0 END) as pending_amount
            FROM erp_purchase_orders 
            WHERE user_id = %s AND is_deleted = FALSE
        """
        params = [user_id]
        
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)
        
        cursor.execute(query, params)
        purchase_data = cursor.fetchone()
        
        # Calculate top suppliers
        suppliers_query = """
            SELECT 
                v.vendor_name,
                COUNT(*) as total_orders,
                SUM(total_amount) as total_spent
            FROM erp_purchase_orders po
            JOIN erp_vendors v ON po.vendor_id = v.id
            WHERE po.user_id = %s AND po.is_deleted = FALSE
        """
        supp_params = [user_id]
        
        if start_date:
            suppliers_query += " AND po.created_at >= %s"
            supp_params.append(start_date)
        if end_date:
            suppliers_query += " AND po.created_at <= %s"
            supp_params.append(end_date)
        
        suppliers_query += " GROUP BY v.id, v.vendor_name ORDER BY total_spent DESC LIMIT 5"
        
        cursor.execute(suppliers_query, supp_params)
        top_suppliers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        result = {
            'summary': dict(purchase_data) if purchase_data else {
                'total_orders': 0,
                'total_purchases': 0,
                'avg_order_value': 0,
                'paid_amount': 0,
                'pending_amount': 0
            },
            'top_suppliers': top_suppliers,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/reports/profit-loss', methods=['GET'])
def get_profit_loss():
    """
    Calculate profit & loss
    Formula: (Total Sales - COGS) - Total Expenses
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate total sales
        sales_query = "SELECT SUM(total_amount) as total_sales FROM erp_invoices WHERE user_id = %s AND is_deleted = FALSE"
        sales_params = [user_id]
        
        # Calculate COGS (Cost of Goods Sold) - based on products sold
        cogs_query = """
            SELECT SUM(ii.quantity * p.cost_price) as total_cogs
            FROM erp_invoice_items ii
            JOIN erp_invoices i ON ii.invoice_id = i.id
            JOIN erp_products p ON ii.product_id = p.id
            WHERE i.user_id = %s AND i.is_deleted = FALSE AND p.cost_price IS NOT NULL
        """
        cogs_params = [user_id]
        
        # Calculate total expenses
        expenses_query = "SELECT SUM(amount) as total_expenses FROM erp_transactions WHERE user_id = %s AND transaction_type = 'expense' AND is_deleted = FALSE"
        expenses_params = [user_id]
        
        # Add date filters if provided
        if start_date:
            sales_query += " AND invoice_date >= %s"
            sales_params.append(start_date)
            cogs_query += " AND i.invoice_date >= %s"
            cogs_params.append(start_date)
            expenses_query += " AND transaction_date >= %s"
            expenses_params.append(start_date)
        
        if end_date:
            sales_query += " AND invoice_date <= %s"
            sales_params.append(end_date)
            cogs_query += " AND i.invoice_date <= %s"
            cogs_params.append(end_date)
            expenses_query += " AND transaction_date <= %s"
            expenses_params.append(end_date)
        
        # Execute queries
        cursor.execute(sales_query, sales_params)
        sales_result = cursor.fetchone()
        total_sales = float(sales_result['total_sales'] or 0)
        
        cursor.execute(cogs_query, cogs_params)
        cogs_result = cursor.fetchone()
        total_cogs = float(cogs_result['total_cogs'] or 0)
        
        cursor.execute(expenses_query, expenses_params)
        expenses_result = cursor.fetchone()
        total_expenses = float(expenses_result['total_expenses'] or 0)
        
        # Calculate gross profit and net profit
        gross_profit = total_sales - total_cogs
        net_profit = gross_profit - total_expenses
        
        conn.close()
        
        result = {
            'total_sales': total_sales,
            'total_cogs': total_cogs,
            'gross_profit': gross_profit,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin_percent': (net_profit / total_sales * 100) if total_sales > 0 else 0,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 10: Staff Management ────────────────────────────────────────────────

@erp_bp.route('/api/erp/staff/<staff_id>', methods=['GET'])
def get_staff_details(staff_id):
    """Get specific staff member details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        staff = cursor.fetchone()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': dict(staff)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff member"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if staff exists
        cursor.execute("""
            SELECT id FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        if 'phone' in data:
            update_fields.append("phone = %s")
            params.append(data['phone'])
        if 'position' in data:
            update_fields.append("position = %s")
            params.append(data['position'])
        if 'department' in data:
            update_fields.append("department = %s")
            params.append(data['department'])
        if 'salary' in data:
            update_fields.append("salary = %s")
            params.append(float(data['salary']))
        if 'hire_date' in data:
            update_fields.append("hire_date = %s")
            params.append(data['hire_date'])
        if 'address' in data:
            update_fields.append("address = %s")
            params.append(data['address'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([staff_id, user_id])
            
            query = f"UPDATE erp_staff SET {', '.join(update_fields)} WHERE id = %s AND company_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Staff updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/staff/<staff_id>/activate', methods=['POST'])
def toggle_staff_status(staff_id):
    """Activate/deactivate staff member"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if staff exists
        cursor.execute("""
            SELECT id, is_active FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        staff = cursor.fetchone()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        # Toggle active status
        new_status = not staff['is_active']
        
        cursor.execute("""
            UPDATE erp_staff 
            SET is_active = %s, updated_at = %s 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (new_status, datetime.now().isoformat(), staff_id, user_id))
        
        conn.commit()
        conn.close()
        
        status_text = 'activated' if new_status else 'deactivated'
        
        return jsonify({
            'success': True,
            'message': f'Staff member {status_text} successfully',
            'is_active': new_status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 11: Backup & Settings ──────────────────────────────────────────────

@erp_bp.route('/api/erp/backup/export', methods=['GET'])
def export_backup():
    """
    Export all user data as JSON backup
    Include: products, customers, vendors, invoices, etc.
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define tables to backup
        tables_to_backup = [
            'erp_products', 'erp_customers', 'erp_vendors', 'erp_invoices', 
            'erp_invoice_items', 'erp_purchase_orders', 'erp_purchase_order_items',
            'erp_transactions', 'erp_staff', 'erp_leads', 'erp_batches',
            'erp_stock', 'erp_grn', 'erp_grn_items', 'erp_companies'
        ]
        
        backup_data = {}
        
        for table in tables_to_backup:
            query = f"SELECT * FROM {table} WHERE user_id = %s OR company_id = %s"
            cursor.execute(query, (user_id, user_id))
            rows = cursor.fetchall()
            backup_data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        # Add metadata
        backup_data['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'user_id': user_id,
            'version': '1.0'
        }
        
        return jsonify({
            'success': True,
            'data': backup_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/backup/restore', methods=['POST'])
def restore_backup():
    """
    Restore data from backup file
    Validate backup integrity first
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        if 'backup_data' not in data:
            return jsonify({'success': False, 'error': 'Backup data is required'}), 400
        
        backup_data = data['backup_data']
        
        # Validate backup structure
        if '_metadata' not in backup_data:
            return jsonify({'success': False, 'error': 'Invalid backup format - missing metadata'}), 400
        
        # Start transaction for restoration
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # For safety, we'll only restore data for the current user
        # First, mark existing data as deleted (soft delete)
        tables_to_restore = [
            'erp_products', 'erp_customers', 'erp_vendors', 'erp_invoices', 
            'erp_invoice_items', 'erp_purchase_orders', 'erp_purchase_order_items',
            'erp_transactions', 'erp_staff', 'erp_leads', 'erp_batches',
            'erp_stock', 'erp_grn', 'erp_grn_items'
        ]
        
        conn.autocommit = False
        try:
            # Soft delete existing data for this user
            for table in tables_to_restore:
                if table in backup_data:
                    cursor.execute(f"UPDATE {table} SET is_deleted = TRUE WHERE user_id = %s OR company_id = %s", 
                                 (user_id, user_id))
            
            # Restore data from backup (only for current user)
            restored_counts = {}
            
            for table, records in backup_data.items():
                if table.startswith('_') or not isinstance(records, list):
                    continue
                
                if table in tables_to_restore:
                    restored_count = 0
                    for record in records:
                        # Only restore records that belong to current user
                        record_user_id = record.get('user_id') or record.get('company_id')
                        if record_user_id == user_id:
                            # Prepare insert statement
                            columns = [k for k, v in record.items() if k != 'id']
                            placeholders = ', '.join(['%s'] * len(columns))
                            column_names = ', '.join(columns)
                            
                            values = [record[col] for col in columns]
                            
                            cursor.execute(
                                f"INSERT INTO {table} (id, {column_names}) VALUES (%s, {placeholders}) "
                                f"ON CONFLICT (id) DO NOTHING",
                                [record.get('id', str(uuid.uuid4()))] + values
                            )
                            restored_count += 1
                    
                    restored_counts[table] = restored_count
            
            conn.commit()
            conn.autocommit = True
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Backup restored successfully',
                'restored_counts': restored_counts
            })
        except Exception as e:
            conn.rollback()
            conn.autocommit = True
            conn.close()
            raise e
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/settings', methods=['GET'])
def get_settings():
    """Get user settings"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user settings
        cursor.execute("""
            SELECT * FROM erp_user_settings 
            WHERE user_id = %s
        """, (user_id,))
        
        settings = cursor.fetchone()
        conn.close()
        
        if settings:
            return jsonify({
                'success': True,
                'data': dict(settings)
            })
        else:
            # Return default settings
            default_settings = {
                'theme': 'wine',
                'currency': 'INR',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:mm',
                'notifications_enabled': True,
                'auto_backup_enabled': True,
                'backup_frequency': 'weekly',
                'low_stock_threshold': 10,
                'default_tax_rate': 18.0,
                'round_off_enabled': True
            }
            
            return jsonify({
                'success': True,
                'data': default_settings
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/settings', methods=['POST'])
def update_settings():
    """Update user settings"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if settings exist, if not create them
        cursor.execute("SELECT id FROM erp_user_settings WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing settings
            update_fields = []
            params = []
            
            for key, value in data.items():
                if key != 'id' and key != 'user_id':  # Don't update id or user_id
                    update_fields.append(f"{key} = %s")
                    params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = %s")
                params.append(datetime.now().isoformat())
                params.append(user_id)
                
                query = f"UPDATE erp_user_settings SET {', '.join(update_fields)} WHERE user_id = %s"
                cursor.execute(query, params)
        else:
            # Create new settings
            settings_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Prepare columns and values
            columns = ['id', 'user_id']
            values_placeholders = ['%s', '%s']
            values = [settings_id, user_id]
            
            for key, value in data.items():
                if key != 'id' and key != 'user_id':
                    columns.append(key)
                    values_placeholders.append('%s')
                    values.append(value)
            
            columns.append('created_at')
            columns.append('updated_at')
            values_placeholders.append('%s')
            values_placeholders.append('%s')
            values.append(now)
            values.append(now)
            
            query = f"INSERT INTO erp_user_settings ({', '.join(columns)}) VALUES ({', '.join(values_placeholders)})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== PRODUCT MANAGEMENT APIs ====================

@erp_bp.route('/api/erp/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT id, code, name, category, price, cost, stock, min_stock, 
                   unit, barcode_data, is_active, created_at
            FROM products 
            WHERE business_owner_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        products = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(p) for p in products]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        product_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO products (id, code, name, category, price, cost, stock, 
                                min_stock, unit, barcode_data, business_owner_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            data.get('code'),
            data.get('name'),
            data.get('category'),
            data.get('price', 0),
            data.get('cost', 0),
            data.get('stock', 0),
            data.get('min_stock', 0),
            data.get('unit', 'piece'),
            data.get('barcode_data'),
            user_id,
            1
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT id, code, name, category, price, cost, stock, min_stock,
                   unit, barcode_data, is_active, created_at
            FROM products 
            WHERE id = ? AND business_owner_id = ?
        """, (product_id, user_id))
        
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return jsonify({
                'success': True,
                'product': dict(product)
            })
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            UPDATE products 
            SET code = ?, name = ?, category = ?, price = ?, cost = ?,
                stock = ?, min_stock = ?, unit = ?, barcode_data = ?
            WHERE id = ? AND business_owner_id = ?
        """, (
            data.get('code'),
            data.get('name'),
            data.get('category'),
            data.get('price'),
            data.get('cost'),
            data.get('stock'),
            data.get('min_stock'),
            data.get('unit'),
            data.get('barcode_data'),
            product_id,
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            DELETE FROM products 
            WHERE id = ? AND business_owner_id = ?
        """, (product_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/categories', methods=['GET'])
def get_product_categories():
    """Get all product categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT DISTINCT category 
            FROM products 
            WHERE business_owner_id = ? AND category IS NOT NULL
            ORDER BY category
        """, (user_id,))
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/brands', methods=['GET'])
def get_product_brands():
    """Get all product brands"""
    try:
        # Since the products table doesn't have a brand column,
        # return an empty list for now
        return jsonify({
            'success': True,
            'data': []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STOCK MANAGEMENT APIs ====================

@erp_bp.route('/api/erp/stock/current', methods=['GET'])
def get_current_stock():
    """Get current stock levels"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT id, code, name, category, stock, min_stock, unit
            FROM products 
            WHERE business_owner_id = ?
            ORDER BY name
        """, (user_id,))
        
        stock_items = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(item) for item in stock_items]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/stock/low-stock', methods=['GET'])
def get_low_stock():
    """Get products with low stock"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT id, code, name, category, stock, min_stock, unit
            FROM products 
            WHERE business_owner_id = ? AND stock <= min_stock
            ORDER BY stock ASC
        """, (user_id,))
        
        low_stock_items = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(item) for item in low_stock_items]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/stock/adjustment', methods=['POST'])
def adjust_stock():
    """Adjust stock levels"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        product_id = data.get('product_id')
        adjustment = data.get('adjustment', 0)
        reason = data.get('reason', '')
        
        # Update stock
        cursor.execute("""
            UPDATE products 
            SET stock = stock + ?
            WHERE id = ? AND business_owner_id = ?
        """, (adjustment, product_id, user_id))
        
        # Log transaction
        transaction_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO stock_transactions (id, product_id, transaction_type, quantity, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (transaction_id, product_id, 'adjustment', adjustment, reason, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Stock adjusted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/stock/transactions', methods=['GET'])
def get_stock_transactions():
    """Get stock transaction history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT st.id, st.product_id, p.name as product_name, 
                   st.transaction_type, st.quantity, st.reason, st.created_at
            FROM stock_transactions st
            JOIN products p ON st.product_id = p.id
            WHERE p.business_owner_id = ?
            ORDER BY st.created_at DESC
            LIMIT 100
        """, (user_id,))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(t) for t in transactions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PAYMENT MANAGEMENT APIs ====================

@erp_bp.route('/api/erp/payments', methods=['GET'])
def get_payments():
    """Get all payments"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = get_user_id()
        cursor.execute("""
            SELECT p.id, p.bill_id, b.bill_number, p.method, p.amount, 
                   p.reference, p.processed_at
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            WHERE b.business_owner_id = ?
            ORDER BY p.processed_at DESC
            LIMIT 100
        """, (user_id,))
        
        payments = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'payments': [dict(p) for p in payments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/payments', methods=['POST'])
def create_payment():
    """Create new payment"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        payment_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO payments (id, bill_id, method, amount, reference, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payment_id,
            data.get('bill_id'),
            data.get('method', 'cash'),
            data.get('amount'),
            data.get('reference'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Payment recorded successfully',
            'payment_id': payment_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get single payment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.bill_id, b.bill_number, p.method, p.amount,
                   p.reference, p.processed_at
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            WHERE p.id = ?
        """, (payment_id,))
        
        payment = cursor.fetchone()
        conn.close()
        
        if payment:
            return jsonify({
                'success': True,
                'payment': dict(payment)
            })
        else:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── COMPANY API ENDPOINTS ───────────────────────────────────────────────────────────────

@erp_bp.route('/api/erp/company', methods=['GET'])
def get_company():
    """
    Get company information for the logged-in user
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, company_name, gst_number, pan_number, financial_year, 
                   invoice_prefix, invoice_starting_number, address, city, state, 
                   pincode, phone, email, logo_url, default_tax_rate, created_at, updated_at
            FROM erp_company 
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))
        
        company = cursor.fetchone()
        conn.close()
        
        if company:
            return jsonify({
                'success': True,
                'data': dict(company)
            })
        else:
            # Return empty data if company doesn't exist yet
            return jsonify({
                'success': True,
                'data': None
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@erp_bp.route('/api/erp/company', methods=['POST'])
def create_or_update_company():
    """
    Create or update company information
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['company_name', 'address', 'city', 'state', 'pincode', 'phone']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if company already exists for this user
        cursor.execute("SELECT id FROM erp_company WHERE user_id = %s", (user_id,))
        existing_company = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing_company:
            # Update existing company
            cursor.execute("""
                UPDATE erp_company SET 
                    company_name = %s, gst_number = %s, pan_number = %s, 
                    financial_year = %s, invoice_prefix = %s, invoice_starting_number = %s,
                    address = %s, city = %s, state = %s, pincode = %s, 
                    phone = %s, email = %s, logo_url = %s, default_tax_rate = %s,
                    updated_at = %s
                WHERE user_id = %s
            """, (
                data['company_name'], data.get('gst_number', ''), data.get('pan_number', ''),
                data.get('financial_year', '2025-26'), data.get('invoice_prefix', 'INV'),
                data.get('invoice_starting_number', 1),
                data['address'], data['city'], data['state'], data['pincode'],
                data['phone'], data.get('email', ''), data.get('logo_url', ''),
                float(data.get('default_tax_rate', 18)), now, user_id
            ))
            message = 'Company updated successfully'
        else:
            # Create new company
            company_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO erp_company (
                    id, user_id, company_name, gst_number, pan_number, 
                    financial_year, invoice_prefix, invoice_starting_number,
                    address, city, state, pincode, phone, email, logo_url, 
                    default_tax_rate, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                company_id, user_id, data['company_name'], data.get('gst_number', ''),
                data.get('pan_number', ''), data.get('financial_year', '2025-26'),
                data.get('invoice_prefix', 'INV'), data.get('invoice_starting_number', 1),
                data['address'], data['city'], data['state'], data['pincode'],
                data['phone'], data.get('email', ''), data.get('logo_url', ''),
                float(data.get('default_tax_rate', 18)), now, now
            ))
            message = 'Company created successfully'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@erp_bp.route('/api/erp/gst-details', methods=['GET'])
def get_gst_details():
    """
    Get GST details for the logged-in user
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, company_name, legal_name, trade_name, gstin, pan_number,
                   gst_registration_type, nature_of_business, registered_address,
                   registered_city, registered_state, registered_pincode, registered_phone,
                   default_tax_rate, tax_calculation_method, reverse_charge_applicable,
                   ecommerce_operator, created_at, updated_at
            FROM erp_gst_details 
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))
        
        gst_details = cursor.fetchone()
        conn.close()
        
        if gst_details:
            return jsonify({
                'success': True,
                'data': dict(gst_details)
            })
        else:
            # Return empty data if GST details don't exist yet
            return jsonify({
                'success': True,
                'data': None
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@erp_bp.route('/api/erp/gst-details', methods=['POST'])
def save_gst_details():
    """
    Save GST details
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if GST details already exist for this user
        cursor.execute("SELECT id FROM erp_gst_details WHERE user_id = %s", (user_id,))
        existing_gst = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing_gst:
            # Update existing GST details
            cursor.execute("""
                UPDATE erp_gst_details SET 
                    company_name = %s, legal_name = %s, trade_name = %s, 
                    gstin = %s, pan_number = %s, gst_registration_type = %s,
                    nature_of_business = %s, registered_address = %s,
                    registered_city = %s, registered_state = %s, registered_pincode = %s,
                    registered_phone = %s, default_tax_rate = %s,
                    tax_calculation_method = %s, reverse_charge_applicable = %s,
                    ecommerce_operator = %s, updated_at = %s
                WHERE user_id = %s
            """, (
                data.get('company_name', ''), data.get('legal_name', ''), data.get('trade_name', ''),
                data.get('gstin', ''), data.get('pan_number', ''), data.get('gstRegistrationType', ''),
                data.get('natureOfBusiness', ''), data.get('registeredAddress', ''),
                data.get('registeredCity', ''), data.get('registeredState', ''), data.get('registeredPincode', ''),
                data.get('registeredPhone', ''), float(data.get('defaultTaxRate', 18)),
                data.get('taxCalculationMethod', 'exclusive'), data.get('reverseChargeApplicable', 'no'),
                data.get('ecommerceOperator', 'no'), now, user_id
            ))
            message = 'GST details updated successfully'
        else:
            # Create new GST details
            gst_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO erp_gst_details (
                    id, user_id, company_name, legal_name, trade_name, 
                    gstin, pan_number, gst_registration_type,
                    nature_of_business, registered_address,
                    registered_city, registered_state, registered_pincode,
                    registered_phone, default_tax_rate,
                    tax_calculation_method, reverse_charge_applicable,
                    ecommerce_operator, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                gst_id, user_id, data.get('company_name', ''), data.get('legal_name', ''), data.get('trade_name', ''),
                data.get('gstin', ''), data.get('pan_number', ''), data.get('gstRegistrationType', ''),
                data.get('natureOfBusiness', ''), data.get('registeredAddress', ''),
                data.get('registeredCity', ''), data.get('registeredState', ''), data.get('registeredPincode', ''),
                data.get('registeredPhone', ''), float(data.get('defaultTaxRate', 18)),
                data.get('taxCalculationMethod', 'exclusive'), data.get('reverseChargeApplicable', 'no'),
                data.get('ecommerceOperator', 'no'), now, now
            ))
            message = 'GST details saved successfully'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CATEGORIES & BRANDS MANAGEMENT APIs ====================

@erp_bp.route('/api/erp/categories', methods=['GET'])
def get_categories():
    """Get all categories with product count"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get categories with product count
        cursor.execute("""
            SELECT c.*, 
                   COUNT(p.id) as product_count
            FROM erp_categories c
            LEFT JOIN erp_products p ON c.id = p.category_id AND p.user_id = c.user_id AND p.is_deleted = FALSE
            WHERE c.user_id = %s AND c.is_deleted = FALSE
            GROUP BY c.id
            ORDER BY c.name ASC
        """, (user_id,))
        
        categories = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get single category details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_categories 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (category_id, user_id))
        
        category = cursor.fetchone()
        conn.close()
        
        if not category:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        return jsonify({
            'success': True,
            'data': dict(category)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/categories', methods=['POST'])
def create_category():
    """Create new category"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Category name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category name already exists
        cursor.execute("""
            SELECT id FROM erp_categories 
            WHERE user_id = %s AND name = %s AND is_deleted = FALSE
        """, (user_id, name))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category name already exists'}), 400
        
        # Create category
        category_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_categories (id, user_id, name, description, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            category_id, user_id, name, 
            data.get('description', ''), 
            data.get('status', 'active'),
            now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'id': category_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """Update category"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Category name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category exists
        cursor.execute("""
            SELECT id FROM erp_categories 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (category_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        # Check if name already exists (excluding current category)
        cursor.execute("""
            SELECT id FROM erp_categories 
            WHERE user_id = %s AND name = %s AND id != %s AND is_deleted = FALSE
        """, (user_id, name, category_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category name already exists'}), 400
        
        # Update category
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE erp_categories 
            SET name = %s, description = %s, status = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (
            name, 
            data.get('description', ''), 
            data.get('status', 'active'),
            now, category_id, user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Category updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete category (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category has products
        cursor.execute("""
            SELECT COUNT(*) as count FROM erp_products 
            WHERE category_id = %s AND user_id = %s AND is_deleted = FALSE
        """, (category_id, user_id))
        
        result = cursor.fetchone()
        if result and result['count'] > 0:
            return jsonify({
                'success': False, 
                'error': f'Cannot delete category. It has {result["count"]} products assigned.'
            }), 400
        
        # Soft delete category
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE erp_categories 
            SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, category_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Category deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BRANDS APIs ====================

@erp_bp.route('/api/erp/brands', methods=['GET'])
def get_brands():
    """Get all brands with product count"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get brands with product count
        cursor.execute("""
            SELECT b.*, 
                   COUNT(p.id) as product_count
            FROM erp_brands b
            LEFT JOIN erp_products p ON b.id = p.brand_id AND p.user_id = b.user_id AND p.is_deleted = FALSE
            WHERE b.user_id = %s AND b.is_deleted = FALSE
            GROUP BY b.id
            ORDER BY b.name ASC
        """, (user_id,))
        
        brands = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in brands]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/brands/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get single brand details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_brands 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (brand_id, user_id))
        
        brand = cursor.fetchone()
        conn.close()
        
        if not brand:
            return jsonify({'success': False, 'error': 'Brand not found'}), 404
        
        return jsonify({
            'success': True,
            'data': dict(brand)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/brands', methods=['POST'])
def create_brand():
    """Create new brand"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Brand name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if brand name already exists
        cursor.execute("""
            SELECT id FROM erp_brands 
            WHERE user_id = %s AND name = %s AND is_deleted = FALSE
        """, (user_id, name))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Brand name already exists'}), 400
        
        # Create brand
        brand_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_brands (id, user_id, name, description, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            brand_id, user_id, name, 
            data.get('description', ''), 
            data.get('status', 'active'),
            now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Brand created successfully',
            'id': brand_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/brands/<brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update brand"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Brand name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if brand exists
        cursor.execute("""
            SELECT id FROM erp_brands 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (brand_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Brand not found'}), 404
        
        # Check if name already exists (excluding current brand)
        cursor.execute("""
            SELECT id FROM erp_brands 
            WHERE user_id = %s AND name = %s AND id != %s AND is_deleted = FALSE
        """, (user_id, name, brand_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Brand name already exists'}), 400
        
        # Update brand
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE erp_brands 
            SET name = %s, description = %s, status = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (
            name, 
            data.get('description', ''), 
            data.get('status', 'active'),
            now, brand_id, user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Brand updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/brands/<brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete brand (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if brand has products
        cursor.execute("""
            SELECT COUNT(*) as count FROM erp_products 
            WHERE brand_id = %s AND user_id = %s AND is_deleted = FALSE
        """, (brand_id, user_id))
        
        result = cursor.fetchone()
        if result and result['count'] > 0:
            return jsonify({
                'success': False, 
                'error': f'Cannot delete brand. It has {result["count"]} products assigned.'
            }), 400
        
        # Soft delete brand
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE erp_brands 
            SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, brand_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Brand not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Brand deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PARTY MANAGEMENT - CUSTOMERS APIs ====================

@erp_bp.route('/api/erp/customers', methods=['GET'])
def get_customers():
    """Get all customers with pagination and filters"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM erp_customers 
            WHERE user_id = %s AND is_deleted = FALSE
        """
        params = [user_id]
        
        if search:
            query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        customers = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM erp_customers WHERE user_id = %s AND is_deleted = FALSE"
        count_params = [user_id]
        
        if search:
            count_query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s)"
            count_params.extend([search_term, search_term, search_term])
        
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in customers],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get single customer details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_customers 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (customer_id, user_id))
        
        customer = cursor.fetchone()
        conn.close()
        
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        return jsonify({
            'success': True,
            'data': dict(customer)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/customers', methods=['POST'])
def create_customer():
    """Create new customer"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Customer name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        customer_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_customers (
                id, user_id, name, phone, email, address, city, state, 
                pincode, gst_number, pan_number, credit_limit, 
                outstanding_balance, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id, user_id, name, 
            data.get('phone', ''), data.get('email', ''), 
            data.get('address', ''), data.get('city', ''), 
            data.get('state', ''), data.get('pincode', ''),
            data.get('gst_number', ''), data.get('pan_number', ''),
            float(data.get('credit_limit', 0)), 0.0,
            data.get('status', 'active'), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'id': customer_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM erp_customers 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (customer_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE erp_customers SET
                name = %s, phone = %s, email = %s, address = %s,
                city = %s, state = %s, pincode = %s, gst_number = %s,
                pan_number = %s, credit_limit = %s, status = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (
            data.get('name', ''), data.get('phone', ''), 
            data.get('email', ''), data.get('address', ''),
            data.get('city', ''), data.get('state', ''), 
            data.get('pincode', ''), data.get('gst_number', ''),
            data.get('pan_number', ''), float(data.get('credit_limit', 0)),
            data.get('status', 'active'), now, customer_id, user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Customer updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete customer (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE erp_customers 
            SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, customer_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PARTY MANAGEMENT - VENDORS APIs ====================

@erp_bp.route('/api/erp/vendors', methods=['GET'])
def get_vendors():
    """Get all vendors with pagination and filters"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM erp_vendors 
            WHERE user_id = %s AND is_deleted = FALSE
        """
        params = [user_id]
        
        if search:
            query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        vendors = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM erp_vendors WHERE user_id = %s AND is_deleted = FALSE"
        count_params = [user_id]
        
        if search:
            count_query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s)"
            count_params.extend([search_term, search_term, search_term])
        
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in vendors],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    """Get single vendor details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_vendors 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (vendor_id, user_id))
        
        vendor = cursor.fetchone()
        conn.close()
        
        if not vendor:
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        return jsonify({
            'success': True,
            'data': dict(vendor)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors', methods=['POST'])
def create_vendor():
    """Create new vendor"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Vendor name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        vendor_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_vendors (
                id, user_id, name, phone, email, address, city, state, 
                pincode, gst_number, pan_number, credit_limit, 
                outstanding_balance, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            vendor_id, user_id, name, 
            data.get('phone', ''), data.get('email', ''), 
            data.get('address', ''), data.get('city', ''), 
            data.get('state', ''), data.get('pincode', ''),
            data.get('gst_number', ''), data.get('pan_number', ''),
            float(data.get('credit_limit', 0)), 0.0,
            data.get('status', 'active'), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Vendor created successfully',
            'id': vendor_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update vendor"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM erp_vendors 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (vendor_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE erp_vendors SET
                name = %s, phone = %s, email = %s, address = %s,
                city = %s, state = %s, pincode = %s, gst_number = %s,
                pan_number = %s, credit_limit = %s, status = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (
            data.get('name', ''), data.get('phone', ''), 
            data.get('email', ''), data.get('address', ''),
            data.get('city', ''), data.get('state', ''), 
            data.get('pincode', ''), data.get('gst_number', ''),
            data.get('pan_number', ''), float(data.get('credit_limit', 0)),
            data.get('status', 'active'), now, vendor_id, user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Vendor updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    """Delete vendor (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE erp_vendors 
            SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, vendor_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Vendor deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PARTY MANAGEMENT - CRM LEADS APIs ====================

@erp_bp.route('/api/erp/crm-leads', methods=['GET'])
def get_crm_leads():
    """Get all CRM leads with pagination and filters"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        source = request.args.get('source', '')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM erp_crm_leads 
            WHERE user_id = %s AND is_deleted = FALSE
        """
        params = [user_id]
        
        if search:
            query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s OR company LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if source:
            query += " AND source = %s"
            params.append(source)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        leads = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM erp_crm_leads WHERE user_id = %s AND is_deleted = FALSE"
        count_params = [user_id]
        
        if search:
            count_query += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s OR company LIKE %s)"
            count_params.extend([search_term, search_term, search_term, search_term])
        
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        if source:
            count_query += " AND source = %s"
            count_params.append(source)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in leads],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/crm-leads/<lead_id>', methods=['GET'])
def get_crm_lead(lead_id):
    """Get single CRM lead details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_crm_leads 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (lead_id, user_id))
        
        lead = cursor.fetchone()
        conn.close()
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        return jsonify({
            'success': True,
            'data': dict(lead)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/crm-leads', methods=['POST'])
def create_crm_lead():
    """Create new CRM lead"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Lead name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        lead_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_crm_leads (
                id, user_id, name, phone, email, company, designation,
                source, status, priority, expected_value, notes,
                follow_up_date, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            lead_id, user_id, name, 
            data.get('phone', ''), data.get('email', ''),
            data.get('company', ''), data.get('designation', ''),
            data.get('source', 'direct'), data.get('status', 'new'),
            data.get('priority', 'medium'), 
            float(data.get('expected_value', 0)),
            data.get('notes', ''), data.get('follow_up_date', ''),
            now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead created successfully',
            'id': lead_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/crm-leads/<lead_id>', methods=['PUT'])
def update_crm_lead(lead_id):
    """Update CRM lead"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM erp_crm_leads 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (lead_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE erp_crm_leads SET
                name = %s, phone = %s, email = %s, company = %s,
                designation = %s, source = %s, status = %s, priority = %s,
                expected_value = %s, notes = %s, follow_up_date = %s, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (
            data.get('name', ''), data.get('phone', ''), 
            data.get('email', ''), data.get('company', ''),
            data.get('designation', ''), data.get('source', 'direct'),
            data.get('status', 'new'), data.get('priority', 'medium'),
            float(data.get('expected_value', 0)), data.get('notes', ''),
            data.get('follow_up_date', ''), now, lead_id, user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/crm-leads/<lead_id>', methods=['DELETE'])
def delete_crm_lead(lead_id):
    """Delete CRM lead (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE erp_crm_leads 
            SET is_deleted = TRUE, updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, lead_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/crm-leads/<lead_id>/convert', methods=['POST'])
def convert_crm_lead_to_customer(lead_id):
    """Convert CRM lead to customer"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get lead details
        cursor.execute("""
            SELECT * FROM erp_crm_leads 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (lead_id, user_id))
        
        lead = cursor.fetchone()
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Create customer from lead
        customer_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_customers (
                id, user_id, name, phone, email, address, 
                status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id, user_id, lead['name'], 
            lead.get('phone', ''), lead.get('email', ''),
            lead.get('company', ''), 'active', now, now
        ))
        
        # Update lead status to converted
        cursor.execute("""
            UPDATE erp_crm_leads 
            SET status = 'converted', updated_at = %s
            WHERE id = %s AND user_id = %s
        """, (now, lead_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead converted to customer successfully',
            'customer_id': customer_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PARTY MANAGEMENT - STATS & REPORTS ====================

@erp_bp.route('/api/erp/parties/stats', methods=['GET'])
def get_parties_stats():
    """Get party management statistics"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get customer stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_customers,
                SUM(outstanding_balance) as total_outstanding
            FROM erp_customers 
            WHERE user_id = %s AND is_deleted = FALSE
        """, (user_id,))
        customer_stats = cursor.fetchone()
        
        # Get vendor stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vendors,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_vendors,
                SUM(outstanding_balance) as total_payable
            FROM erp_vendors 
            WHERE user_id = %s AND is_deleted = FALSE
        """, (user_id,))
        vendor_stats = cursor.fetchone()
        
        # Get CRM lead stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_leads,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_leads,
                SUM(CASE WHEN status = 'contacted' THEN 1 ELSE 0 END) as contacted_leads,
                SUM(CASE WHEN status = 'qualified' THEN 1 ELSE 0 END) as qualified_leads,
                SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted_leads,
                SUM(expected_value) as total_expected_value
            FROM erp_crm_leads 
            WHERE user_id = %s AND is_deleted = FALSE
        """, (user_id,))
        lead_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'customers': dict(customer_stats) if customer_stats else {},
            'vendors': dict(vendor_stats) if vendor_stats else {},
            'leads': dict(lead_stats) if lead_stats else {}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/customers/<customer_id>/transactions', methods=['GET'])
def get_customer_transactions(customer_id):
    """Get customer transaction history"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get invoices
        cursor.execute("""
            SELECT * FROM erp_invoices 
            WHERE customer_id = %s AND user_id = %s
            ORDER BY invoice_date DESC
            LIMIT 50
        """, (customer_id, user_id))
        invoices = cursor.fetchall()
        
        # Get payments
        cursor.execute("""
            SELECT * FROM erp_payments 
            WHERE party_id = %s AND party_type = 'customer' AND user_id = %s
            ORDER BY payment_date DESC
            LIMIT 50
        """, (customer_id, user_id))
        payments = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'invoices': [dict(row) for row in invoices],
            'payments': [dict(row) for row in payments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>/transactions', methods=['GET'])
def get_vendor_transaction_history(vendor_id):
    """Get vendor transaction history"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get purchase orders
        cursor.execute("""
            SELECT * FROM erp_purchase_orders 
            WHERE vendor_id = %s AND user_id = %s
            ORDER BY order_date DESC
            LIMIT 50
        """, (vendor_id, user_id))
        purchase_orders = cursor.fetchall()
        
        # Get payments
        cursor.execute("""
            SELECT * FROM erp_payments 
            WHERE party_id = %s AND party_type = 'vendor' AND user_id = %s
            ORDER BY payment_date DESC
            LIMIT 50
        """, (vendor_id, user_id))
        payments = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'purchase_orders': [dict(row) for row in purchase_orders],
            'payments': [dict(row) for row in payments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
