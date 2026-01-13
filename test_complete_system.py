#!/usr/bin/env python3
"""
Complete System Test - Verify automatic alerts are working end-to-end
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import time
from modules.shared.database import init_db, get_db_connection, g