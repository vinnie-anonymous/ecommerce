# ecommerce/env_utils.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_var(var_name, default=None, required=False):
    """Get environment variable with optional required flag"""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {var_name} is not set")
    return value

def get_bool_env(var_name, default=False):
    """Get boolean environment variable"""
    value = os.getenv(var_name, str(default))
    return value.lower() in ('true', '1', 'yes', 'on')

def get_list_env(var_name, default=None):
    """Get list from environment variable (comma-separated)"""
    if default is None:
        default = []
    value = os.getenv(var_name, '')
    if not value:
        return default
    return [item.strip() for item in value.split(',') if item.strip()]