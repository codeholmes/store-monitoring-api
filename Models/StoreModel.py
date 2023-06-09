from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    create_engine,
    Index
)
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///db/store.sqlite", echo=False)
Base = declarative_base()


class Store(Base):
    """Store Model: Store ID"""
    __tablename__ = "store"
    id = Column(Integer, primary_key=True)  # Unqiue IDs from Status file


class Status(Base):
    """Status Model: Store ID, Timestamp, Status"""
    __tablename__ = "status"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    timestamp_utc = Column(DateTime)
    timestamp_local = Column(DateTime)
    status = Column(String(8))


class BusinessHours(Base):
    """Business Hours Model: Store ID, Day, Start Time, End Time"""
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    day = Column(Integer)  # 0 = Monday, 1 = Tuesday, etc.
    start_time_local = Column(String(20))
    end_time_local = Column(String(20))


class TimeZone(Base):
    """Time Zone Model: Store ID, Time Zone"""
    __tablename__ = "time_zone"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    timezone_str = Column(String(50))

class Report(Base):
    """Report Model: Store ID, Report ID, Status, Uptime, Downtime"""
    __tablename__ = "report"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("store.id"))
    report_id = Column(String(20), nullable=False)
    status = Column(String(10))
    uptime_last_hour = Column(Integer, nullable=True)
    uptime_last_day = Column(Integer, nullable=True)
    uptime_last_week = Column(Integer, nullable=True)
    downtime_last_hour = Column(Integer, nullable=True)
    downtime_last_day = Column(Integer, nullable=True)
    downtime_last_week = Column(Integer, nullable=True)

class ReportStatus(Base):
    """Report Status Model: Report ID, Status"""
    __tablename__ = "report_status"
    id = Column(Integer, primary_key=True)
    report_id = Column(String(20), nullable=False)
    status = Column(String(10))

# creating index for status table, timezone table
Index('idx_status', Status.store_id, Status.timestamp_utc, Status.status)
Index("idx_timezone", TimeZone.store_id, TimeZone.timezone_str)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)