from datetime import timedelta
from Models.StoreModel import BusinessHours, Session, Status


class StoreMonitor:
    def __init__(self) -> None:
        pass

    def find_slot(self, store_id: int, day: int):
        """This function returns number of slot

        Args:
            store_id (int): Store ID
            day (int): 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday
        """
        with Session() as session:
            slots = (
                session.query(BusinessHours)
                .filter(BusinessHours.store_id == store_id, BusinessHours.day == day)
                .count()
            )
            session.close()
            print(slots)

    def start_time_local(self, store_id: int, day: int):
        """This function returns list of all business hours [start] on the particular day

        Args:
            store_id (int): Store ID
            day (int): 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday
        """
        with Session() as session:
            b_hours = [
                e.start_time_local
                for e in session.query(BusinessHours).filter(
                    BusinessHours.store_id == store_id, BusinessHours.day == day
                )
            ]
            session.close()
            print(b_hours)

    def end_time_local(self, store_id: int, day: int):
        """This function returns list of all business hours [end] on the particular day

        Args:
            store_id (int): Store ID
            day (int): 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday
        """
        with Session() as session:
            b_hours = [
                e.end_time_local
                for e in session.query(BusinessHours).filter(
                    BusinessHours.store_id == store_id, BusinessHours.day == day
                )
            ]
            session.close()
            print(b_hours)

    def business_hours(self, store_id: int, day: int):
        """This function returns list of all business hours [start, end] on the particular day

        Args:
            store_id (int): Store ID
            day (int): 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday
        """
        with Session() as session:
            b_hours = [
                [e.start_time_local, e.end_time_local]
                for e in session.query(BusinessHours).filter(
                    BusinessHours.store_id == store_id, BusinessHours.day == day
                )
            ]
            session.close()
            print(b_hours)

    def max_timestamp(self, store_id: int):
        """This function returns max timestamp from the status table

        Args:
            store_id (int): Store ID
        """
        with Session() as session:
            max_timestamp = (
                session.query(Status)
                .filter(Status.store_id == store_id)
                .order_by(Status.timestamp_utc.desc())
                .first()
            )
            print(max_timestamp.timestamp_utc)
            session.close()
            return max_timestamp.timestamp_utc

    def store_status(self, store_id: int):
        """This function returns status of the store

        Args:
            store_id (int): Store ID
        """
        with Session() as session:
            status = [
                [e.store_id, e.status, e.timestamp_utc]
                for e in session.query(Status).filter(Status.store_id == store_id).all()
            ]
            session.close()
            return status

    def last_week_status(self, store_id: int):
        """This function returns status of the store for last week from max timestamp

        Args:
            store_id (int): Store ID
        """
        with Session() as session:
            max_timestamp = self.max_timestamp(self, store_id)
            last_week_status = [
                [e.timestamp_utc]
                for e in session.query(Status)
                .filter(
                    Status.store_id == store_id,
                    Status.timestamp_utc > max_timestamp - timedelta(days=7),
                )
                .all()
            ]
            session.close()
            print(last_week_status)
            return last_week_status
