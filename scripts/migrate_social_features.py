"""
Database migration script to add social features tables.

Creates tables for:
- Leaders (elected officials, decision makers)
- Organizations (nonprofits, charities)
- Causes (policy topics, issues)
- Follow relationships (users, leaders, orgs, causes)

Run with: python scripts/migrate_social_features.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import engine
from api.models import Base, Leader, Organization, Cause, UserFollow, LeaderFollow, OrganizationFollow, CauseFollow
from loguru import logger

def migrate():
    """Run migration to create social features tables"""
    
    logger.info("🔄 Starting social features database migration...")
    
    try:
        # Create all tables (will skip existing ones)
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Social features tables created successfully!")
        logger.info("")
        logger.info("📊 New tables:")
        logger.info("  ✓ leaders - Public officials and decision makers")
        logger.info("  ✓ organizations - Nonprofits and charities")
        logger.info("  ✓ causes - Policy topics and issues")
        logger.info("  ✓ user_follows - User→User follows")
        logger.info("  ✓ leader_follows - User→Leader follows")
        logger.info("  ✓ organization_follows - User→Organization follows")
        logger.info("  ✓ cause_follows - User→Cause follows")
        logger.info("")
        logger.info("🎉 Migration complete! Social features are ready to use.")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
