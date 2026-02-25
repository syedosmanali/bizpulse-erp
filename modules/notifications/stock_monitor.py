"""
Background Stock Monitor Service
Runs independently to check stock levels and send alerts
"""

import threading
import time
from datetime import datetime, date
from modules.shared.database import get_db_connection, generate_id
from modules.notifications.routes import create_notification_for_user

class StockMonitorService:
    def __init__(self):
        self.running = False
        self.thread = None
        self.check_interval = 600  # 10 minutes in seconds
        
    def start(self):
        """Start the background stock monitoring service"""
        if self.running:
            print("📊 [STOCK MONITOR] Service already running")
            return
            
        self.running = True
        
        # Start the monitoring thread
        self.thread = threading.Thread(target=self._run_monitor, daemon=True)
        self.thread.start()
        
        print(f"🚀 [STOCK MONITOR] Background service started - checking every {self.check_interval//60} minutes")
        
        # Run initial check after 30 seconds to allow app to fully start
        threading.Timer(30.0, self.check_all_clients_stock).start()
        
    def stop(self):
        """Stop the background stock monitoring service"""
        self.running = False
        print("🛑 [STOCK MONITOR] Background service stopped")
        
    def _run_monitor(self):
        """Internal method to run the monitoring loop"""
        while self.running:
            try:
                time.sleep(self.check_interval)  # Wait for check interval
                if self.running:  # Check if still running after sleep
                    self.check_all_clients_stock()
            except Exception as e:
                print(f"❌ [STOCK MONITOR] Monitor loop error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
                
    def check_all_clients_stock(self):
        """Check stock levels for all clients and send alerts if needed"""
        try:
            print(f"🔍 [STOCK MONITOR] Starting stock check at {datetime.now()}")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get all clients with notification settings enabled
            cursor.execute("""
                SELECT ns.client_id, ns.low_stock_threshold, c.company_name
                FROM notification_settings ns
                JOIN clients c ON ns.client_id = c.id
                WHERE ns.low_stock_enabled = 1 AND c.is_active = 1
            """)
            
            clients_with_settings = cursor.fetchall()
            
            if not clients_with_settings:
                print("📊 [STOCK MONITOR] No clients with stock alerts enabled")
                conn.close()
                return
                
            total_alerts_sent = 0
            
            for client_row in clients_with_settings:
                # Handle both dict and tuple cursor results
                if isinstance(client_row, dict):
                    client_id = client_row['client_id']
                    threshold = client_row['low_stock_threshold']
                    company_name = client_row['company_name']
                else:
                    client_id = client_row[0]
                    threshold = client_row[1]
                    company_name = client_row[2]
                
                alerts_sent = self.check_client_stock(cursor, client_id, threshold, company_name)
                total_alerts_sent += alerts_sent
                
            conn.close()
            
            if total_alerts_sent > 0:
                print(f"✅ [STOCK MONITOR] Completed stock check - {total_alerts_sent} alerts sent")
            else:
                print(f"✅ [STOCK MONITOR] Completed stock check - no alerts needed")
                
        except Exception as e:
            print(f"❌ [STOCK MONITOR] Error in stock check: {e}")
            import traceback
            traceback.print_exc()
            
    def check_client_stock(self, cursor, client_id, threshold, company_name):
        """Check stock for a specific client and send alerts"""
        try:
            today = date.today().isoformat()
            alerts_sent = 0
            
            # Get all products for this client that are at or below threshold
            cursor.execute("""
                SELECT id, name, stock, category
                FROM products 
                WHERE user_id = ? AND is_active = 1 AND stock <= ?
                ORDER BY stock ASC
            """, (client_id, threshold))
            
            low_stock_products = cursor.fetchall()
            
            if not low_stock_products:
                return 0
                
            print(f"📦 [STOCK MONITOR] Client {company_name}: Found {len(low_stock_products)} products at/below threshold {threshold}")
            
            for product in low_stock_products:
                # Handle both dict and tuple cursor results
                if isinstance(product, dict):
                    product_id = product['id']
                    product_name = product['name']
                    current_stock = product['stock']
                    category = product['category']
                else:
                    product_id = product[0]
                    product_name = product[1]
                    current_stock = product[2]
                    category = product[3]
                
                # Check if we already sent an alert today for this product
                cursor.execute("""
                    SELECT id FROM stock_alert_log 
                    WHERE client_id = ? AND product_id = ? AND alert_date = ?
                """, (client_id, product_id, today))
                
                existing_alert = cursor.fetchone()
                
                if existing_alert:
                    # Already sent alert today for this product
                    continue
                    
                # Create the alert notification
                if current_stock == 0:
                    notification_message = f"Out of Stock: {product_name} ({category})"
                    notification_type = "alert"
                else:
                    notification_message = f"Low Stock Alert: {product_name} - Only {current_stock} remaining ({category})"
                    notification_type = "alert"
                
                # Create notification
                notification_id = create_notification_for_user(
                    user_id=client_id,
                    notification_type=notification_type,
                    message=notification_message,
                    action_url='/retail/products'
                )
                
                if notification_id:
                    # Log that we sent this alert
                    log_id = generate_id()
                    cursor.execute("""
                        INSERT INTO stock_alert_log (
                            id, client_id, product_id, alert_date, 
                            stock_level, threshold_level, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        log_id, client_id, product_id, today,
                        current_stock, threshold, datetime.now().isoformat()
                    ))
                    
                    alerts_sent += 1
                    print(f"🔔 [STOCK MONITOR] Alert sent: {product_name} (stock: {current_stock})")
                    
            # Commit all changes for this client
            cursor.connection.commit()
            
            return alerts_sent
            
        except Exception as e:
            print(f"❌ [STOCK MONITOR] Error checking client {client_id} stock: {e}")
            return 0

# Global instance
stock_monitor = StockMonitorService()

def start_stock_monitor():
    """Start the stock monitoring service"""
    stock_monitor.start()

def stop_stock_monitor():
    """Stop the stock monitoring service"""
    stock_monitor.stop()