import pandas as pd
from Models.StoreModel import Store, Status, BusinessHours, TimeZone, Session

# reading csv files
store_status_df = pd.read_csv("resources/data/store_status.csv")
business_hours_df = pd.read_csv("resources/data/business_hours.csv")
timezone_df = pd.read_csv("resources/data/timezone.csv")

# store df
store_df = store_status_df["store_id"].drop_duplicates()
store_df.reset_index(drop=True, inplace=True)

# store status df
status_df = store_status_df[["store_id", "timestamp_utc", "status"]]  # no duplicates here

# store data insertion
with Session() as session:
    try:
        session.query(Store).delete()
        session.commit()
        print("Deleted all rows from Store table")
    except Exception:
        session.rollback()
        print("Failed to delete all rows from Store table")

    try:
        session.add_all([Store(id=store_id) for store_id in store_df])
        session.commit()
        print("Inserted into Store table")
    except Exception:
        session.rollback()
        print("Failed to insert into Store table")

    session.close()

# status data insertion
with Session() as session:
    try:
        session.query(Status).delete()
        session.commit()
        print("Deleted all rows from Status table")
    except Exception:
        session.rollback()
        print("Failed to delete all rows from Status table")

    try:
        rows_count = status_df.count()[0]
        for i in range(0, rows_count, 50000):
            session.add_all(
                [
                    Status(
                        store_id=store_id,
                        timestamp_utc=timestamp_utc,
                        status=status,
                    )
                    for store_id, timestamp_utc, status in zip(
                        status_df["store_id"][i : i + 50000],
                        pd.to_datetime(status_df["timestamp_utc"][i : i + 50000], format='mixed'), # mixed format
                        status_df["status"][i : i + 50000],
                    )
                ]
            )
            session.commit()
            print(f"Inserted batch of {i+50000} rows into Status table")
    except Exception:
        session.rollback()
        print("Failed to insert into Status table")

    session.close()

# business hours data insertion
with Session() as session:
    try:
        session.query(BusinessHours).delete()
        session.commit()
        print("Deleted all the rows from BusinessHours table")
    except Exception:
        session.rollback()
        print("Failed to delete all the rows from BusinessHours table")
    
    try:
        rows_count = business_hours_df.count()[0]
        for i in range(0, rows_count, 20000):
            session.add_all(
                [
                    BusinessHours
                    (
                        store_id=s_id, day=day, start_time_local=start_time, end_time_local=end_time
                    )
                    for s_id, day, start_time, end_time in zip
                    (
                        business_hours_df["store_id"][i : i + 20000],
                        business_hours_df["day"][i : i + 20000],
                        # pd.to_datetime(business_hours_df["start_time_local"][i : i + 20000], format = "%H:%M:%S"),
                        # pd.to_datetime(business_hours_df["end_time_local"][i : i + 20000], format="%H:%M:%S")
                        business_hours_df["start_time_local"][i : i + 20000],
                        business_hours_df["end_time_local"][i : i + 20000]
                    )
                ]
            )
            session.commit()
            print(f"Inserted batch of {i + 20000} into BusinessHours table.")
    except Exception:
        session.rollback()
        print("Failed to insert into BusinessHours table")
    
    session.close()

# timezone data insertions
with Session() as session:
    try:
        session.query(TimeZone).delete()
        session.commit()
        print("Deleted all the rows from Timezone table")
    except Exception:
        session.rollback()
        print("Failed to delete from Timezone table")
    
    try:
        session.add_all(
            [
                TimeZone(store_id = s_id, timezone_str = t_zone)
                for s_id, t_zone
                in zip(timezone_df["store_id"], timezone_df["timezone_str"])
            ]
        )
        session.commit()
        print("Inserted all the rows into Timezone table")
    except Exception:
        session.rollback()
        print("Failed to insert into Timezone table")

    session.close()

