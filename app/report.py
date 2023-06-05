from app.store_monitor import StoreMonitor
from app.one_algorithm import OneAlgorithm
from Models.StoreModel import Store, Session, Report, ReportStatus
import pandas as pd
import random
import string


def generate_random_string():
    """This function generates random string for report_id"""
    letters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(letters) for _ in range(15))
    return random_string


def generate_report(report_id: str):
    """This function generates report for all stores and bulk insert into database"""

    session = Session()
    stores = session.query(Store.id).limit(5).all()

    report = []
    store_count = 0

    session.add(ReportStatus(report_id=report_id, status="running"))
    for store_id in stores:
        store = StoreMonitor(store_id[0])

        last_week = OneAlgorithm(store_id[0], store.get_last_week_status())
        last_week_data = last_week.calculate_uptime_downtime()

        last_day = OneAlgorithm(store_id[0], store.get_last_day_status())
        last_day_data = last_day.calculate_uptime_downtime()

        report.append(
            {
                "store_id": store_id[0],
                "report_id": report_id,
                "status": "complete",
                "uptime_last_week": last_week_data["uptime"] / 3600,
                "downtime_last_week": last_week_data["downtime"] / 3600,
                "uptime_last_day": last_day_data["uptime"] / 60,
                "downtime_last_day": last_day_data["downtime"] / 60,
            }
        )
        store_count += 1

    session.bulk_insert_mappings(Report, report)
    session.commit()

    if store_count == len([e for e in stores]):
        # update report status
        session.query(ReportStatus).filter(ReportStatus.report_id == report_id).update(
            {"status": "complete"}
        )
        session.commit()
    session.close()


def trigger_report_generation():
    """This function triggers report generation and returns report_id"""
    report_id = generate_random_string()
    generate_report(report_id)
    return report_id


def get_report(report_id: str):
    """"This function returns report in pandas dataframe"""
    with Session() as session:
        report = session.query(Report).filter(Report.report_id == report_id).all()
        if report:
            report_df = pd.DataFrame(
                [
                    {
                        "store_id": e.store_id,
                        "uptime_last_week": e.uptime_last_week,
                        "downtime_last_week": e.downtime_last_week,
                        "uptime_last_day": e.uptime_last_day,
                        "downtime_last_day": e.downtime_last_day,
                    }
                    for e in report
                ]
            )
            # remvove column which name is empty
            return report_df


def get_report_status(report_id: str):
    """This function returns report status and covers if report_id is invalid"""
    with Session() as session:
        report_status = (
            session.query(ReportStatus.status)
            .filter(ReportStatus.report_id == report_id).first()
        )
        if report_status is not None:
            if report_status:
                return report_status[0]
            else:
                return "invalid"
        else:
            return ("something went wrong from reading report_status from request")