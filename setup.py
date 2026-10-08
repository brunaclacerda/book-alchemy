import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    def save(self, commit=True):
        logger.debug("Adding object in the session.")
        db.session.add(self)
        error = None
        if commit:
            try:
                logger.debug("Commiting transaction.")
                db.session.commit()
            except OperationalError as e:
                logger.error("DB communication error: %s", e)
                error = e
            except IntegrityError as e:
                logger.error("FK error: %s", e)
                error = ValueError("Invalid FK provided.")
            except Exception as e:
                logger.error("Unexpected error on commiting: %s", e)
                error = e
            finally:
                if error:
                    logger.error("Rollbacking.")
                    db.session.rollback()
                    raise (error)

        return self

    def delete(self, commit=True):
        logger.debug("Deleting record in the session.")
        db.session.delete(self)
        error = None
        if commit:
            try:
                logger.debug("Commiting transaction.")
                db.session.commit()
            except OperationalError as e:
                logger.error("DB communication error: %s", e)
                error = e
            except Exception as e:
                logger.error("Unexpected error on commiting: %s", e)
                error = e
            finally:
                if error:
                    logger.error("Rollbacking.")
                    db.session.rollback()
                    raise (error)

        return self

    def to_dict(self):
        """
        Convert ORM object to dict
        """
        return {
            column.key: getattr(self, column.key)
            for column in self.__mapper__.column_attrs
        }

    @classmethod
    def select_all(cls) -> list:
        """
        Class method to fetch records in the db
        """
        logger.debug("Selecting all records from %s", cls.__tablename__)
        stmt = select(cls)
        records = db.session.execute(stmt).scalars().all()
        return [record.to_dict() for record in records]


db = SQLAlchemy(model_class=Base)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
