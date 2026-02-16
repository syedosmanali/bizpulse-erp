"""
Dashboard Service Layer - Business Logic for Dashboard Operations
"""

from modules.dashboard.models import ActivityTracker, DashboardStats
from modules.shared.database import get_db_connection
from datetime import datetime, timedelta
import json

class DashboardService:
    """Service class for dashboard operations"""
    
    @staticmethod
    def initialize():
        """Initialize dashboard tables - NO SAMPLE DATA, USE REAL DATA ONLY"""
        ActivityTracker.init_activity_table()
        
        # NO SAMPLE DATA INITIALIZATION - ALWAYS USE REAL DATA FROM DATABASE
        # The dashboard will show real activities from bills, products, customers tables
        print("Dashboard initialized - Using real data from database")
    
    @staticmethod
    def get_dashboard_data(client_id=None):
        """Get complete dashboard data"""
        return {
            'recent_activities': ActivityTracker.get_recent_activities(limit=10, client_id=client_id),
            'sales_stats': DashboardStats.get_sales_stats(client_id=client_id),
            'customer_stats': DashboardStats.get_customer_stats(client_id=client_id),
            'inventory_stats': DashboardStats.get_inventory_stats(client_id=client_id),
            'summary': DashboardService._get_dashboard_summary(client_id=client_id)
        }
    
    @staticmethod
    def get_premium_dashboard_sections(client_id=None):
        """Get premium dashboard sections for new UI"""
        return ActivityTracker.get_premium_dashboard_sections(client_id=client_id)
    
    @staticmethod
    def get_recent_activities_only(limit=10, client_id=None):
        """Get recent activities - kept for backward compatibility"""
        sections = ActivityTracker.get_premium_dashboard_sections(client_id=client_id)
        
        # Convert sections to activities format for backward compatibility
        activities = []
        
        # Add recent sales as activities
        if sections['recent_sales']['data']:
            for sale in sections['recent_sales']['data'][:3]:  # Limit to 3
                activities.append({
                    'id': f"sale-{sale['id']}",
                    'activity_type': 'sale',
                    'title': f"{sale['sale_type']} completed",
                    'description': f"₹{sale['amount']:,.0f} - {sale['customer_name']}",
                    'amount': sale['amount'],
                    'created_at': sale['created_at'],
                    'time_ago': sale['time_ago']
                })
        
        # Add last product as activity
        if sections['last_product']['data']:
            product = sections['last_product']['data']
            activities.append({
                'id': f"product-{product['id']}",
                'activity_type': 'product',
                'title': f"New product added: {product['name']}",
                'description': f"{product['category']} - ₹{product['price']:,.0f}",
                'amount': 0,
                'created_at': product['created_at'],
                'time_ago': product['time_ago']
            })
        
        # Add last customer as activity
        if sections['last_customer']['data']:
            customer = sections['last_customer']['data']
            activities.append({
                'id': f"customer-{customer['id']}",
                'activity_type': 'customer',
                'title': f"{customer['customer_type']} registered",
                'description': f"{customer['name']} - {customer['phone'] or 'No phone'}",
                'amount': 0,
                'created_at': customer['created_at'],
                'time_ago': customer['time_ago']
            })
        
        # Add last bulk order as activity
        if sections['last_bulk_order']['data']:
            order = sections['last_bulk_order']['data']
            activities.append({
                'id': f"order-{order['id']}",
                'activity_type': 'order',
                'title': f"{order['order_type']} processed",
                'description': f"₹{order['amount']:,.0f} - {order['customer_name']}",
                'amount': order['amount'],
                'created_at': order['created_at'],
                'time_ago': order['time_ago']
            })
        
        # Sort by created_at and limit
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def _get_dashboard_summary(client_id=None):
        """Get dashboard summary metrics"""
        # For development/testing, return zero values when no session context
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user_id from session for data isolation
            from flask import session
            user_type = session.get('user_type')
            if user_type == 'employee':
                user_id = session.get('client_id')  # For employees, use client_id
            else:
                user_id = session.get('user_id')    # For clients, use user_id
            
            # Build user filter
            user_filter = ""
            user_params = []
            if user_id:
                user_filter = " AND business_owner_id = ?"
                user_params = [user_id]
            
            # Today's metrics
            # Sales = ALL bills created today (including credit/partial)
            # Revenue = Only CASH PAYMENTS processed today (from payments table)
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as today_sales,
                    COUNT(*) as today_orders
                FROM bills 
                WHERE DATE(created_at) = DATE('now'){user_filter}
            ''', user_params)
            today_bills = cursor.fetchone()
            
            # Get today's cash revenue from payments table
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(p.amount), 0) as today_revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE DATE(p.processed_at) = DATE('now')
                AND p.method = 'Cash'{user_filter}
            ''', user_params)
            today_payments = cursor.fetchone()
            
            # Combine results
            today = {
                'today_sales': today_bills['today_sales'],
                'today_revenue': today_payments['today_revenue'],
                'today_orders': today_bills['today_orders']
            }
            
            # This week's metrics
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as week_sales,
                    COUNT(*) as week_orders
                FROM bills 
                WHERE created_at >= date('now', '-7 days'){user_filter}
            ''', user_params)
            week_bills = cursor.fetchone()
            
            # Get week's cash revenue from payments table
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(p.amount), 0) as week_revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE p.processed_at >= date('now', '-7 days')
                AND p.method = 'Cash'{user_filter}
            ''', user_params)
            week_payments = cursor.fetchone()
            
            # Combine results
            week = {
                'week_sales': week_bills['week_sales'],
                'week_revenue': week_payments['week_revenue'],
                'week_orders': week_bills['week_orders']
            }
            
            # This month's metrics
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as month_sales,
                    COUNT(*) as month_orders
                FROM bills 
                WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now'){user_filter}
            ''', user_params)
            month_bills = cursor.fetchone()
            
            # Get month's cash revenue from payments table
            cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(p.amount), 0) as month_revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE strftime('%Y-%m', p.processed_at) = strftime('%Y-%m', 'now')
                AND p.method = 'Cash'{user_filter}
            ''', user_params)
            month_payments = cursor.fetchone()
            
            # Combine results
            month = {
                'month_sales': month_bills['month_sales'],
                'month_revenue': month_payments['month_revenue'],
                'month_orders': month_bills['month_orders']
            }
            
            conn.close()
        except Exception as e:
            # If there's any error (like no session context), return zero values
            print(f"Dashboard summary error (returning zeros): {e}")
            today = {'today_sales': 0, 'today_revenue': 0, 'today_orders': 0}
            week = {'week_sales': 0, 'week_revenue': 0, 'week_orders': 0}
            month = {'month_sales': 0, 'month_revenue': 0, 'month_orders': 0}
        
        return {
            'today': {
                'sales': float(today['today_sales'] or 0),
                'revenue': float(today['today_revenue'] or 0),
                'orders': int(today['today_orders'] or 0)
            },
            'week': {
                'sales': float(week['week_sales'] or 0),
                'revenue': float(week['week_revenue'] or 0),
                'orders': int(week['week_orders'] or 0)
            },
            'month': {
                'sales': float(month['month_sales'] or 0),
                'revenue': float(month['month_revenue'] or 0),
                'orders': int(month['month_orders'] or 0)
            }
        }
    
    @staticmethod
    def get_activity_analytics(days=30, client_id=None):
        """Get activity analytics for charts and insights"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Activity count by type
        cursor.execute('''
            SELECT activity_type, COUNT(*) as count
            FROM recent_activities
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY activity_type
            ORDER BY count DESC
        '''.format(days))
        activity_types = cursor.fetchall()
        
        # Daily activity trend
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM recent_activities
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        '''.format(days))
        daily_trend = cursor.fetchall()
        
        # Revenue generating activities
        cursor.execute('''
            SELECT DATE(created_at) as date, SUM(amount) as revenue
            FROM recent_activities
            WHERE created_at >= datetime('now', '-{} days')
            AND amount > 0
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        '''.format(days))
        revenue_trend = cursor.fetchall()
        
        conn.close()
        
        return {
            'activity_types': [dict(row) for row in activity_types],
            'daily_trend': [dict(row) for row in daily_trend],
            'revenue_trend': [dict(row) for row in revenue_trend]
        }
    
    @staticmethod
    def search_activities(query, limit=20, client_id=None):
        """Search activities by title or description"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_query = '''
            SELECT id, activity_type, title, description, amount, currency,
                   reference_id, reference_type, icon_type, created_at
            FROM recent_activities
            WHERE (title LIKE ? OR description LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%']
        
        if client_id:
            search_query += ' AND (client_id = ? OR client_id IS NULL)'
            params.append(client_id)
        
        search_query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(search_query, params)
        activities = cursor.fetchall()
        
        conn.close()
        
        result = []
        for activity in activities:
            activity_dict = dict(activity)
            activity_dict['time_ago'] = ActivityTracker._get_time_ago(activity_dict['created_at'])
            result.append(activity_dict)
        
        return result
    
    @staticmethod
    def get_activity_by_type(activity_type, limit=10, client_id=None):
        """Get activities filtered by type"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, activity_type, title, description, amount, currency,
                   reference_id, reference_type, icon_type, created_at
            FROM recent_activities
            WHERE activity_type = ?
        '''
        params = [activity_type]
        
        if client_id:
            query += ' AND (client_id = ? OR client_id IS NULL)'
            params.append(client_id)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        activities = cursor.fetchall()
        
        conn.close()
        
        result = []
        for activity in activities:
            activity_dict = dict(activity)
            activity_dict['time_ago'] = ActivityTracker._get_time_ago(activity_dict['created_at'])
            result.append(activity_dict)
        
        return result