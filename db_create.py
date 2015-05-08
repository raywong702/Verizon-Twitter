from migrate.versioning import api
#from config import SQLALCHEMY_DATABASE_URI
#from config import SQLALCHEMY_MIGRATE_REPO
import config
from app import db
import os.path
db.create_all()
SQLALCHEMY_MIGRATE_REPO = config.Config.SQLALCHEMY_MIGRATE_REPO
SQLALCHEMY_DATABASE_URI = config.Config.SQLALCHEMY_DATABASE_URI
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
