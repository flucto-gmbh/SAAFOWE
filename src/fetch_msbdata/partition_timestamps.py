from datetime import datetime, timedelta, timezone

AGGREGATION_INTERVALS = ["hourly", "daily", "weekly", "monthly", "all"]

test_timestamps_hourly = [
    datetime.fromisoformat("2021-01-01T00:00:00+00:00") + timedelta(seconds=600) * i
    for i in range(0, 21)
]
test_timestamps_daily = [
    datetime.fromisoformat("2021-01-01T00:00:00+00:00") + timedelta(hours=12) * i
    for i in range(0, 21)
]
test_timestamps_weekly = [
    datetime.fromisoformat("2021-01-01T00:00:00+00:00") + timedelta(days=3) * i
    for i in range(0, 21)
]
test_timestamps_monthly = [
    datetime.fromisoformat("2021-01-01T00:00:00+00:00") + timedelta(weeks=2) * i
    for i in range(0, 21)
]
test_timestamps_all = [
    *test_timestamps_hourly,
    *test_timestamps_daily,
    *test_timestamps_weekly,
    *test_timestamps_monthly,
]


def are_in_equivalent_interval(
    timestamp: datetime, interval_boundary: datetime, interval: str
) -> bool:
    """
    receives two tuples objects x and y and checks if they are datetime
    in their first field are equivalent
    """
    assert interval in AGGREGATION_INTERVALS
    if interval == "all":
        return True
    elif interval == "hourly":
        return (
            # timestamp.year == interval_boundary.year and
            # timestamp.month == interval_boundary.month and
            # timestamp.day == interval_boundary.day and
            timestamp
            <= (
                datetime(
                    year=interval_boundary.year,
                    month=interval_boundary.month,
                    day=interval_boundary.day,
                    hour=interval_boundary.hour,
                    tzinfo=timezone.utc,
                )
                + timedelta(hours=1)
            )
        )
    elif interval == "daily":
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
            and timestamp.day == interval_boundary.day
        )
    elif interval == "weekly":
        dx = date(timestamp.year, timestamp.month, timestamp.day)
        dy = date(
            interval_boundary.year, interval_boundary.month, interval_boundary.day
        )
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
            and dx.isocalendar().week == dy.isocalendar().week
        )
    elif interval == "monthly":
        return (
            timestamp.year == interval_boundary.year
            and timestamp.month == interval_boundary.month
        )


if __name__ == "__main__":
    print(f"test timestamps: {test_timestamps_hourly}")
    print(f"test timestamps: {test_timestamps_daily}")
    print(f"test timestamps: {test_timestamps_weekly}")
    print(f"test timestamps: {test_timestamps_monthly}")
    print(f"test timestamps: {test_timestamps_all}")
