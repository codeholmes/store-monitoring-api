from app.store_monitor import StoreMonitor


def main():
    store_id = 3536289959498899286
    day = 5

    StoreMonitor.find_slot(StoreMonitor, store_id, day)
    StoreMonitor.start_time_local(StoreMonitor, store_id, day)
    StoreMonitor.end_time_local(StoreMonitor, store_id, day)
    StoreMonitor.business_hours(StoreMonitor, store_id, day)
    StoreMonitor.store_status(StoreMonitor, store_id)
    StoreMonitor.max_timestamp(StoreMonitor, store_id)
    StoreMonitor.last_week_status(StoreMonitor, store_id)

if __name__ == "__main__":
    main()