"""
Cron Job Routes - Silent endpoints for cron-job.org
Production-ready with minimal output
"""

from flask import Blueprint, Response
import logging

cron_bp = Blueprint('cron', __name__)
logger = logging.getLogger(__name__)

@cron_bp.route('/cron/health', methods=['GET'])
def cron_health():
    """Silent health check for cron jobs - Returns only 'OK'"""
    try:
        # Run any background health checks silently
        logger.info("Cron health check executed")
        return Response("OK", status=200, mimetype='text/plain')
    except Exception as e:
        logger.error(f"Cron health check failed: {e}")
        return Response("ERROR", status=500, mimetype='text/plain')

@cron_bp.route('/cron/cleanup', methods=['GET'])
def cron_cleanup():
    """Silent cleanup task - Returns only 'OK'"""
    try:
        # Run cleanup tasks silently
        from modules.sync.service import sync_service
        sync_service.cleanup_inactive_sessions()
        logger.info("Cron cleanup executed")
        return Response("OK", status=200, mimetype='text/plain')
    except Exception as e:
        logger.error(f"Cron cleanup failed: {e}")
        return Response("ERROR", status=500, mimetype='text/plain')

@cron_bp.route('/cron/stock-monitor', methods=['GET'])
def cron_stock_monitor():
    """Silent stock monitoring - Returns only 'OK'"""
    try:
        # Run stock monitoring silently
        from modules.notifications.stock_monitor import check_stock_levels
        check_stock_levels()
        logger.info("Cron stock monitor executed")
        return Response("OK", status=200, mimetype='text/plain')
    except Exception as e:
        logger.error(f"Cron stock monitor failed: {e}")
        return Response("ERROR", status=500, mimetype='text/plain')

@cron_bp.route('/cron/daily-tasks', methods=['GET'])
def cron_daily_tasks():
    """Silent daily tasks - Returns only 'OK'"""
    try:
        # Run daily tasks silently
        logger.info("Cron daily tasks executed")
        return Response("OK", status=200, mimetype='text/plain')
    except Exception as e:
        logger.error(f"Cron daily tasks failed: {e}")
        return Response("ERROR", status=500, mimetype='text/plain')
