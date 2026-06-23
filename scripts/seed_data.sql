BEGIN;

PRAGMA foreign_keys = ON;

DELETE FROM api_calls;
DELETE FROM trail_steps;
DELETE FROM word_swaps;
DELETE FROM run_flags;
DELETE FROM transform_runs;
DELETE FROM sqlite_sequence WHERE name IN ('api_calls', 'transform_runs');

CREATE TEMP TABLE seed_runs AS
WITH RECURSIVE
day_offsets(day_offset) AS (
    SELECT 0
    UNION ALL
    SELECT day_offset + 1 FROM day_offsets WHERE day_offset < 41
),
slots(slot) AS (
    SELECT 1
    UNION ALL
    SELECT slot + 1 FROM slots WHERE slot < 20
),
day_plan AS (
    SELECT
        day_offset,
        date('now', 'start of day', printf('-%d days', 41 - day_offset)) AS day_date,
        CAST(strftime('%w', date('now', 'start of day', printf('-%d days', 41 - day_offset))) AS INTEGER) AS weekday_num
    FROM day_offsets
),
scheduled AS (
    SELECT
        day_offset,
        day_date,
        weekday_num,
        slot,
        CASE
            WHEN weekday_num BETWEEN 1 AND 5 THEN 16 + ((day_offset * 2 + weekday_num) % 5)
            WHEN weekday_num = 6 THEN 8 + ((day_offset * 5) % 4)
            ELSE 5 + ((day_offset * 7) % 4)
        END AS daily_runs
    FROM day_plan
    CROSS JOIN slots
)
SELECT
    ROW_NUMBER() OVER (ORDER BY day_date, slot) AS run_id,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        datetime(
            day_date,
            printf(
                '+%d minutes',
                CASE
                    WHEN day_offset = 41 THEN 390 + (((slot - 1) * 11 + day_offset * 3) % 180)
                    WHEN weekday_num BETWEEN 1 AND 5 THEN 510 + (((slot - 1) * 29 + day_offset * 7) % 525)
                    WHEN weekday_num = 6 THEN 540 + (((slot - 1) * 37 + day_offset * 11) % 420)
                    ELSE 600 + (((slot - 1) * 43 + day_offset * 13) % 300)
                END
            )
        )
    ) AS created_at,
    CASE
        WHEN (slot + day_offset) % 6 = 0 THEN 'flag-only'
        ELSE 'transform'
    END AS endpoint_name,
    printf('%c-%03d', 65 + ((day_offset + slot - 1) % 7), 100 + ((day_offset * 11 + slot * 3 + ((slot - 1) % 5) * 7) % 140)) AS ticket,
    CASE
        WHEN slot IN (4, 9, 15) AND weekday_num BETWEEN 1 AND 5 THEN 'partner_api'
        WHEN (slot + day_offset) % 9 = 0 THEN 'fax'
        WHEN (slot + day_offset) % 7 = 0 THEN 'ivr'
        WHEN slot % 4 = 0 THEN 'email'
        ELSE 'portal'
    END AS source,
    CASE
        WHEN (day_offset + slot) % 5 = 0 THEN 'north'
        WHEN (day_offset + slot) % 5 = 1 THEN 'south'
        WHEN (day_offset + slot) % 5 = 2 THEN 'east'
        WHEN (day_offset + slot) % 5 = 3 THEN 'west'
        ELSE 'middle'
    END AS region,
    CASE
        WHEN (day_offset + slot) % 5 = 0 THEN 'NTH'
        WHEN (day_offset + slot) % 5 = 1 THEN 'STH'
        WHEN (day_offset + slot) % 5 = 2 THEN 'EST'
        WHEN (day_offset + slot) % 5 = 3 THEN 'WST'
        ELSE 'MID'
    END AS region_code,
    CAST(
        CASE
            WHEN slot IN (3, 10, 17) THEN 900 + ((day_offset * 41 + slot * 53) % 900)
            WHEN weekday_num IN (0, 6) THEN 60 + ((day_offset * 29 + slot * 37) % 420)
            ELSE 45 + ((day_offset * 67 + slot * 59) % 780)
        END AS REAL
    ) AS amount,
    CASE
        WHEN slot IN (6, 13) OR (day_offset + slot) % 11 = 0 THEN 'yes'
        ELSE 'no'
    END AS retry_value,
    CASE
        WHEN slot IN (2, 8, 14) OR (day_offset + slot) % 13 = 0 THEN 'yes'
        ELSE 'no'
    END AS vip_value,
    CASE
        WHEN slot IN (3, 10, 17) THEN 'angry'
        WHEN slot IN (2, 8, 14) THEN 'warm'
        WHEN weekday_num IN (0, 6) THEN 'calm'
        ELSE 'neutral'
    END AS tone,
    CASE
        WHEN slot % 6 = 1 THEN 'claim'
        WHEN slot % 6 = 2 THEN 'eta'
        WHEN slot % 6 = 3 THEN 'reroute'
        WHEN slot % 6 = 4 THEN 'address'
        WHEN slot % 6 = 5 THEN 'handoff'
        ELSE 'lane-update'
    END AS topic,
    CASE
        WHEN slot % 6 = 1 THEN 'customer asks for claim update after late shipment'
        WHEN slot % 6 = 2 THEN 'customer requests eta because package late'
        WHEN slot % 6 = 3 THEN 'partner mentions route issue and wants reroute'
        WHEN slot % 6 = 4 THEN 'shipper asks for address review before handoff'
        WHEN slot % 6 = 5 THEN 'client requests handoff status and says thanks'
        ELSE 'customer needs rapid lane update after package late'
    END AS raw_text,
    CASE
        WHEN slot % 6 = 1 THEN 'customer asks for claim update after delayed delivery'
        WHEN slot % 6 = 2 THEN 'customer requests eta because package delayed'
        WHEN slot % 6 = 3 THEN 'partner mentions path issue and wants redirect'
        WHEN slot % 6 = 4 THEN 'shipper asks for location review before handoff'
        WHEN slot % 6 = 5 THEN 'client requests handoff status and offers thanks'
        ELSE 'customer needs swift lane update after package delayed'
    END AS shifted_text
FROM scheduled
WHERE slot <= daily_runs;

INSERT INTO transform_runs (
    id,
    created_at,
    endpoint_name,
    ticket,
    source,
    region,
    region_code,
    amount,
    retry_value,
    vip_value,
    tone,
    topic,
    raw_text,
    shifted_text
)
SELECT
    run_id,
    created_at,
    endpoint_name,
    ticket,
    source,
    region,
    region_code,
    amount,
    retry_value,
    vip_value,
    tone,
    topic,
    raw_text,
    shifted_text
FROM seed_runs;

INSERT INTO run_flags (run_id, decision_flag, send_partner_copy, manual_review)
SELECT
    run_id,
    CASE
        WHEN tone = 'angry' AND amount >= 900 THEN 'STOP_AND_STARE'
        WHEN amount >= 1200 OR retry_value = 'yes' OR source IN ('fax', 'ivr') THEN 'MANUAL_REVIEW'
        WHEN vip_value = 'yes' AND amount < 900 AND instr(lower(shifted_text), 'thanks') > 0 THEN 'FAST_TRACK'
        ELSE 'STANDARD_PIPE'
    END AS decision_flag,
    CASE
        WHEN vip_value = 'yes' AND amount < 900 AND source IN ('portal', 'email', 'partner_api') THEN 1
        ELSE 0
    END AS send_partner_copy,
    CASE
        WHEN tone = 'angry' AND amount >= 900 THEN 1
        WHEN amount >= 1200 OR retry_value = 'yes' OR source IN ('fax', 'ivr') THEN 1
        ELSE 0
    END AS manual_review
FROM seed_runs;

INSERT INTO word_swaps (run_id, swap_index, from_word, to_word)
SELECT run_id, 1, 'late', 'delayed'
FROM seed_runs
WHERE topic IN ('claim', 'eta')
UNION ALL
SELECT run_id, 2, 'shipment', 'delivery'
FROM seed_runs
WHERE topic = 'claim'
UNION ALL
SELECT run_id, 1, 'route', 'path'
FROM seed_runs
WHERE topic = 'reroute'
UNION ALL
SELECT run_id, 2, 'reroute', 'redirect'
FROM seed_runs
WHERE topic = 'reroute'
UNION ALL
SELECT run_id, 1, 'address', 'location'
FROM seed_runs
WHERE topic = 'address'
UNION ALL
SELECT run_id, 1, 'rapid', 'swift'
FROM seed_runs
WHERE topic = 'lane-update'
UNION ALL
SELECT run_id, 2, 'late', 'delayed'
FROM seed_runs
WHERE topic = 'lane-update';

INSERT INTO trail_steps (run_id, trail_index, ticket_value)
SELECT run_id, 1, ticket
FROM seed_runs
UNION ALL
SELECT run_id, 2, printf('%c-%03d', 65 + (run_id % 7), 100 + ((run_id * 5 + 17) % 140))
FROM seed_runs
WHERE run_id % 5 != 0
UNION ALL
SELECT run_id, 3, printf('%c-%03d', 65 + ((run_id + 2) % 7), 100 + ((run_id * 7 + 29) % 140))
FROM seed_runs
WHERE retry_value = 'yes' OR source IN ('partner_api', 'fax');

INSERT INTO api_calls (
    id,
    called_at,
    method,
    path,
    status_code,
    duration_ms,
    remote_addr,
    ticket,
    run_id
)
SELECT
    run_id,
    created_at,
    'POST',
    CASE
        WHEN endpoint_name = 'flag-only' THEN '/api/v1/flag-only'
        ELSE '/api/v1/transform'
    END AS path,
    200,
    26 + ((run_id * 17) % 180),
    printf('10.24.%d.%d', 20 + (run_id % 12), 30 + ((run_id * 3) % 190)),
    ticket,
    run_id
FROM seed_runs;

CREATE TEMP TABLE seed_noise AS
WITH RECURSIVE
day_offsets(day_offset) AS (
    SELECT 0
    UNION ALL
    SELECT day_offset + 1 FROM day_offsets WHERE day_offset < 41
),
slots(slot) AS (
    SELECT 1
    UNION ALL
    SELECT slot + 1 FROM slots WHERE slot < 8
),
day_plan AS (
    SELECT
        day_offset,
        date('now', 'start of day', printf('-%d days', 41 - day_offset)) AS day_date,
        CAST(strftime('%w', date('now', 'start of day', printf('-%d days', 41 - day_offset))) AS INTEGER) AS weekday_num
    FROM day_offsets
),
scheduled AS (
    SELECT
        day_offset,
        day_date,
        weekday_num,
        slot,
        CASE
            WHEN weekday_num BETWEEN 1 AND 5 THEN 8
            WHEN weekday_num = 6 THEN 5
            ELSE 3
        END AS daily_calls
    FROM day_plan
    CROSS JOIN slots
)
SELECT
    ROW_NUMBER() OVER (ORDER BY day_date, slot) AS noise_id,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        datetime(
            day_date,
            printf(
                '+%d minutes',
                CASE
                    WHEN day_offset = 41 THEN 390 + (((slot - 1) * 13 + day_offset * 5) % 180)
                    WHEN weekday_num BETWEEN 1 AND 5 THEN 480 + (((slot - 1) * 41 + day_offset * 9) % 600)
                    WHEN weekday_num = 6 THEN 600 + (((slot - 1) * 47 + day_offset * 13) % 360)
                    ELSE 660 + (((slot - 1) * 53 + day_offset * 15) % 240)
                END
            )
        )
    ) AS called_at,
    CASE
        WHEN slot = 8 AND weekday_num BETWEEN 1 AND 5 THEN 'POST'
        ELSE 'GET'
    END AS method,
    CASE
        WHEN slot = 1 THEN '/health'
        WHEN slot = 2 THEN '/api/v1/examples/basic'
        WHEN slot = 3 THEN '/api/v1/admin/ping'
        WHEN slot = 4 THEN '/api/v1/admin/vis'
        WHEN slot = 5 THEN '/health'
        WHEN slot = 6 THEN '/api/v1/examples/basic'
        WHEN slot = 7 THEN '/api/v1/admin/ping'
        WHEN slot = 8 AND weekday_num BETWEEN 1 AND 5 THEN '/api/v1/admin/replay'
        ELSE '/health'
    END AS path,
    CASE
        WHEN slot = 4 AND weekday_num = 1 AND day_offset IN (2, 9) THEN 503
        ELSE 200
    END AS status_code,
    CASE
        WHEN slot = 8 AND weekday_num BETWEEN 1 AND 5 THEN 70 + ((day_offset * 19 + slot * 11) % 140)
        ELSE 6 + ((day_offset * 13 + slot * 17) % 65)
    END AS duration_ms,
    printf('10.33.%d.%d', 40 + (day_offset % 6), 50 + ((slot * 11 + day_offset * 7) % 160)) AS remote_addr,
    CASE
        WHEN slot = 8 AND weekday_num BETWEEN 1 AND 5 THEN printf('%c-%03d', 65 + ((day_offset + slot) % 7), 100 + ((day_offset * 9 + slot * 5) % 140))
        ELSE NULL
    END AS ticket,
    CASE
        WHEN slot = 8 AND weekday_num BETWEEN 1 AND 5 THEN 1 + ((day_offset * 13 + slot * 7) % (SELECT COUNT(*) FROM seed_runs))
        ELSE NULL
    END AS run_id
FROM scheduled
WHERE slot <= daily_calls;

INSERT INTO api_calls (
    id,
    called_at,
    method,
    path,
    status_code,
    duration_ms,
    remote_addr,
    ticket,
    run_id
)
SELECT
    (SELECT COUNT(*) FROM seed_runs) + noise_id,
    called_at,
    method,
    path,
    status_code,
    duration_ms,
    remote_addr,
    ticket,
    run_id
FROM seed_noise;

DROP TABLE seed_noise;
DROP TABLE seed_runs;

COMMIT;
