from datetime import datetime
import numpy as np
import sys

sys.path.append("/Users/anysh/Desktop/store-monitoring-api/app")

from store_monitor import StoreMonitor


class OneAlgorithm:
    """One algorithm to rule them all ;)"""

    def __init__(self, store_id, status_cluster):
        self.store_id = store_id
        self.store = StoreMonitor(self.store_id)
        self.store.add_timestamp_local()
        self.status_cluster = status_cluster
        # print([e.status for e in self.status_cluster])
        # self.business_hours = self.store.business_hours(self.store_id)

    def calculate_uptime_downtime(self) -> dict:
        """Calculate uptime and downtime from max timestamp

        Returns:
            float: Uptime in hours
        """

        uptime = 0
        downtime = 0
        business_duration_start = datetime.strptime("00:00:00", "%H:%M:%S")
        business_duration_end = datetime.strptime("00:00:00", "%H:%M:%S")
        total_business_duration = 0.0
        active_status_count = 0
        inactive_status_count = 0
        business_days = np.unique(
            [self.store.find_day(e.timestamp_local) for e in self.status_cluster]
        )
        # print(f"Business days: {business_days}")
        if business_days is None:
            business_days = [0, 1, 2, 3, 4, 5, 6]
        # print(f"Business days: {business_days}")

        for day in business_days:
            business_hours_slots = self.store.business_hours(int(day))
            # print(f"Business hours: {business_hours_slots}")
            if business_hours_slots == []:
                business_hours_slots = [["00:00:00", "23:59:59"]]
            # print(f"Business hours: {business_hours_slots}")

            for business_hours in business_hours_slots:
                status = [
                    [
                        datetime.strftime(e.timestamp_local, "%Y:%m:%d"),
                        datetime.strftime(e.timestamp_local, "%H:%M:%S"),
                        datetime.strptime(
                            datetime.strftime(e.timestamp_local, "%H:%M:%S"), "%H:%M:%S"
                        ),
                        e.status,
                    ]
                    for e in self.status_cluster
                    if self.store.find_day(e.timestamp_local) == day
                    and (
                        datetime.strptime(
                            datetime.strftime(e.timestamp_local, "%H:%M:%S"), "%H:%M:%S"
                        )
                        >= datetime.strptime(business_hours[0], "%H:%M:%S")
                    )
                    and (
                        datetime.strptime(
                            datetime.strftime(e.timestamp_local, "%H:%M:%S"), "%H:%M:%S"
                        )
                        <= datetime.strptime(business_hours[1], "%H:%M:%S")
                    )
                ]

                if status:
                    status.insert(0, [datetime.strptime(business_hours[0], "%H:%M:%S"), "start"])
                    status.append([datetime.strptime(business_hours[1], "%H:%M:%S"), "end"])

                    start = None
                    previous_status = None
                    for e in status:
                        if e[-1] == "start":
                            start = e[-2]
                            business_duration_start = e[-2]
                            previous_status = "active"
                        elif e[-1] == "active":
                            active_status_count += 1
                            if previous_status == "active":
                                uptime += (e[-2] - start).total_seconds() # add to uptime
                                previous_status = "active" # update previous status
                                start = e[-2] # update start
                            elif previous_status == "inactive":
                                downtime += (e[-2] - start).total_seconds()
                                start = e[-2]
                                previous_status = "active"
                        elif e[-1] == "inactive":
                            inactive_status_count += 1
                            if previous_status == "inactive":
                                downtime += (e[-2] - start).total_seconds()
                                start = e[-2]
                                previous_status = "inactive"
                            elif previous_status == "active":
                                uptime += (e[-2] - start).total_seconds()
                                start = e[-2]
                                previous_status = "inactive"
                        elif e[-1] == "end":
                            business_duration_end = e[-2]
                            if previous_status == "active":
                                uptime += (e[-2] - start).total_seconds()
                                previous_status = "end"
                                start = None
                                previous_status = None
                            elif previous_status == "inactive":
                                downtime += (e[-2] - start).total_seconds()
                                previous_status = "end"
                                start = None
                                previous_status = None
                business_duration = business_duration_end - business_duration_start
                total_business_duration += business_duration.total_seconds()

                # print(
                #     f"\nDAY {day} -  Business hours: {business_hours} start {business_hours[0]} end {business_hours[1]}\n"
                # )
                # print(f"Status: {status}")
                # print(f"Uptime: {uptime / 3600}")
                # print(f"Downtime: {downtime / 3600}")
                # print("Business duration: ", business_duration)
                # print("Total business duration: ", total_business_duration / 3600)
                # print("Active status count: ", active_status_count)
                # print("Inactive status count: ", inactive_status_count)

        try:
            weightage = total_business_duration / (active_status_count + inactive_status_count)
        except ZeroDivisionError:
            weightage = 0

        # print("\n\nWeightage: ", weightage)
        uptime = active_status_count * weightage
        downtime = inactive_status_count * weightage
        # print(f"Uptime: {uptime / 3600}")
        # print(f"Downtime: {downtime / 3600}")
        # print(f"Uptime + Downtime: {(uptime + downtime) / 3600}")
        # print("Total business duration: ", total_business_duration / 3600)

        # print(dict({"uptime": uptime / 3600, "downtime": downtime / 3600}))        

        return dict({"uptime": uptime, "downtime": downtime})
