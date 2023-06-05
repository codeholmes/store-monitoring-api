from ast import List
from datetime import timedelta, datetime
from sqlalchemy import DateTime
import pandas as pd
from Models.StoreModel import BusinessHours, Session, Status, TimeZone
import pytz

class StoreMonitor:
    def __init__(self, store_id) -> None:
        self.store_id = store_id

    def find_day(self, timestamp: datetime) -> int:
        """Finds the day of the week from the timestamp

        Args:
            store_id (int): Store ID

        Returns:
            int: 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday
        """
        day = pd.Timestamp(timestamp).weekday()
        return day

    def find_slot(self, store_id: int, day: int) -> None:
        """This function displays number of slot

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

    def start_time_local(self, store_id: int, day: int) -> None:
        """This function displays list of all business hours [start] on the particular day

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

    def end_time_local(self, store_id: int, day: int) -> None:
        """This function displays list of all business hours [end] on the particular day

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

    def business_hours(self, day: int) -> List:
        """This function returns list of all business hours [start, end] on the particular day

        Args:
            day (0): 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday 6 = Sunday

        Returns:
            List: List of all business hours
        """
        with Session() as session:
            b_hours = [
                [e.start_time_local, e.end_time_local]
                for e in session.query(BusinessHours).filter(
                    BusinessHours.store_id == self.store_id, BusinessHours.day == day
                )
            ]
            session.close()
        return b_hours
            # print(b_hours)

    def add_timestamp_local(self) -> None:
        """This function converts UTC timezone to local timezone and insert them into db
        """

        utc_timezone = pytz.timezone("UTC")
        with Session() as session:
            local_timezone = (
                session.query(TimeZone.timezone_str)
                .filter(TimeZone.store_id == self.store_id)
                .first()
            )


            if local_timezone is None:
                local_timezone = "America/Chicago"
            elif local_timezone is not None:
                local_timezone = local_timezone[0]

            status_table = (
                session.query(Status).filter(Status.store_id == self.store_id).all()
            )

            if local_timezone is not None:
                local_timezone = pytz.timezone(local_timezone)

                for row in status_table:
                    if row.timestamp_local is None:
                        dt_local = (
                            utc_timezone.localize(
                                datetime.strptime(
                                    str(row.timestamp_utc), "%Y-%m-%d %H:%M:%S.%f"
                                )
                            )
                            .astimezone(local_timezone)
                        )
                        row.timestamp_local = dt_local
                        # print("Local timestamp added!")
                        session.commit()
                    else:
                        pass
                        # print("Local timestamp is already there")
            else:
                print("Local timezone is not set")
                
            session.close()

    def get_max_timestamp(self) -> DateTime:
        """This function returns max timestamp from the status table

        Returns:
            DateTime: Max timestamp
        """
        self.add_timestamp_local()
        with Session() as session:
            try:
                max_timestamp = (
                    session.query(Status)
                    .filter(Status.store_id == self.store_id)
                    .order_by(Status.timestamp_local.desc())
                    .first()
                )
            except Exception as e:
                print("Error: ", e)
            session.close()
            return max_timestamp.timestamp_local

    def get_max_timestamp_date(self) -> DateTime:
        """This functions returns date striped from the max_timestamp() function

        Returns:
            DateTime: Max Date
        """
        max_timestamp_date = self.get_max_timestamp().date()
        # print("max_timestamp_date", max_timestamp_date)
        return max_timestamp_date

    def get_last_week_status(self) -> List:
        """This function returns status of the store for last week day (excluding max timestamp)

        Returns:
            List: List of status
        """
        with Session() as session:
            max_timestamp_date = self.get_max_timestamp_date()
            last_week_status = [
                e
                for e in session.query(Status)
                .filter(
                    Status.store_id == self.store_id,
                    Status.timestamp_local >= max_timestamp_date - timedelta(days=7),
                    Status.timestamp_local < max_timestamp_date
                )
                .all()
            ]
            # print("Max:", max_timestamp_date)
            # print([datetime.strftime(e.timestamp_local, "%Y-%m-%d") for e in last_week_status])
            session.close()
        return last_week_status
    
    def get_last_day_status(self) -> List:
        """This function returns status of the store for last day (excluding max timestamp)

        Returns:
            List: List of status
        """
        with Session() as session:
            max_timestamp_date = self.get_max_timestamp_date()
            last_day_status = [
                e
                for e in session.query(Status)
                .filter(
                    Status.store_id == self.store_id,
                    Status.timestamp_local >= (max_timestamp_date - timedelta(days=1)),
                    Status.timestamp_local < max_timestamp_date,
                )
            ]
            # print(max_timestamp - timedelta(days=1))
            # print([datetime.strftime(e.timestamp_local, "%Y-%m-%d") for e in last_day_status])
            return last_day_status
    
    def get_last_hour_status(self) -> List:
        """This function returns status of the store for last hour (from max timestamp)

        Returns:
            List: List of status
        """
        with Session() as session:
            max_timestamp = self.get_max_timestamp()
            last_hour_status = [
                e
                for e in session.query(Status)
                .filter(
                    Status.store_id == self.store_id,
                    Status.timestamp_local >= (max_timestamp - timedelta(hours=1)),
                    Status.timestamp_local <= max_timestamp,
                )
            ]
            print(f"Max timestamp: {max_timestamp}")
            print(f"Last hour: {max_timestamp - timedelta(hours=1)}")

            # print([datetime.strftime(e.timestamp_local, "%Y-%m-%d %H:%M:%S") for e in last_hour_status])
            
            self.flag = False
            if not last_hour_status == []:
                if max_timestamp - last_hour_status[0].timestamp_local < timedelta(hours=1):
                    self.flag = True

            if last_hour_status == [] or self.flag == True:
                timestamp_outside_last_1hr = (
                session.query(Status)
                .filter(Status.store_id == self.store_id, Status.timestamp_local < (max_timestamp - timedelta(hours=1)))
                .order_by(Status.timestamp_local.desc()).first()
            )
                # print(f"last_hour_outside: {timestamp_outside_last_1hr.timestamp_local}")
                # last_hour_status.append(timestamp_outside_last_1hr)
                # last_hour_status.append(max_timestamp - timedelta(hours=1))

            session.close()
            return last_hour_status
                

