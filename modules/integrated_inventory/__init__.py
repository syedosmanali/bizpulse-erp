"""
Integrated Inventory Management System
Combines Product Master, Inventory Control, and Purchase Entry
"""

from .routes import integrated_inventory_bp
from .service import integrated_inventory_service
from .database import init_integrated_inventory_tables, get_current_stock

__all__ = [
    'integrated_inventory_bp',
    'integrated_inventory_service', 
    'init_integrated_inventory_tables',
    'get_current_stock'
]