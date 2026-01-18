#!/usr/bin/env python3
"""
Database migration script.
Run this once to initialize the database schema.
Should be run before starting the application for the first time.
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine, DATABASE_URL
from db_models import Wall, Obstacle, Plan, Path, Execution, Grid  # Import all models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations to create all tables."""
    logger.info("="*80)
    logger.info("DATABASE MIGRATION - INITIALIZING SCHEMA")
    logger.info("="*80)
    logger.info(f"Database URL: {DATABASE_URL}")
    
    try:
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Successfully created {len(tables)} tables:")
        for table in tables:
            logger.info(f"{table}")
        
        logger.info("="*80)
        logger.info("MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        return True
        
    except Exception as e:
        logger.error("="*80)
        logger.error("MIGRATION FAILED")
        logger.error("="*80)
        logger.error(f"Error: {e}", exc_info=True)
        return False


def check_migration_status():
    """Check if migrations have been run."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = {'walls', 'obstacles', 'plans', 'paths', 'executions', 'grids'}
        existing_tables = set(tables)
        
        if expected_tables.issubset(existing_tables):
            logger.info("All required tables exist")
            return True
        else:
            missing = expected_tables - existing_tables
            logger.warning(f"Missing tables: {missing}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking migration status: {e}")
        return False


def drop_all_tables():
    """Drop all tables - USE WITH CAUTION!"""
    logger.warning("="*80)
    logger.warning("WARNING: DROPPING ALL TABLES")
    logger.warning("="*80)
    
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Aborted")
        return
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration management")
    parser.add_argument(
        'command',
        choices=['migrate', 'status', 'drop'],
        help='Command to run: migrate (create tables), status (check tables), drop (delete all tables)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'migrate':
        success = run_migrations()
        sys.exit(0 if success else 1)
    elif args.command == 'status':
        check_migration_status()
    elif args.command == 'drop':
        drop_all_tables()

