DIM_EVENT_COLUMNS = [
    "event_key",
    "season",
    "round_number",
    "country",
    "location",
    "official_event_name",
    "event_date",
    "event_name",
    "event_format",
    "session_1",
    "session_1_date_utc",
    "session_2",
    "session_2_date_utc",
    "session_3",
    "session_3_date_utc",
    "session_4",
    "session_4_date_utc",
    "session_5",
    "session_5_date_utc",
    "f1_api_support",
]


DIM_DRIVER_COLUMNS = [
    "driver_key",
    "driver_id",
    "driver_number",
    "driver_abbreviation",
    "driver_name",
    "country_code",
]


DIM_TEAM_COLUMNS = [
    "team_key",
    "team_id",
    "team_name",
]


FACT_RACE_RESULT_COLUMNS = [
    "race_result_key",
    "event_key",
    "driver_key",
    "team_key",
    "grid_position",
    "finish_position",
    "classified_position",
    "classified_position_numeric",
    "race_time_or_gap",
    "race_time_or_gap_ms",
    "status",
    "points",
    "laps",
    "positions_gained",
    "is_winner",
    "is_podium",
    "is_points_finish",
    "is_dnf",
]