BEGIN;

PRAGMA foreign_keys = ON;

DELETE FROM api_calls;
DELETE FROM trail_steps;
DELETE FROM word_swaps;
DELETE FROM run_flags;
DELETE FROM transform_runs;
DELETE FROM sqlite_sequence WHERE name IN ('api_calls', 'transform_runs');

CREATE TEMP TABLE seed_runs AS
WITH RECURSIVE seq(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 560
)
SELECT
    n AS run_id,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        datetime(
            'now',
            'start of day',
            printf('-%d days', 14 - CAST((n - 1) / 40 AS INTEGER)),
            printf('+%d minutes', 470 + ((n * 31) % 520))
        )
    ) AS created_at,
    CASE
        WHEN n % 5 = 0 THEN 'flag-only'
        ELSE 'transform'
    END AS endpoint_name,
    printf('%c-%03d', 65 + ((n - 1) % 7), 100 + ((n - 1) % 220)) AS ticket,
    CASE
        WHEN n % 9 = 0 THEN 'fax'
        WHEN n % 7 = 0 THEN 'ivr'
        WHEN n % 5 = 0 THEN 'partner_api'
        WHEN n % 4 = 0 THEN 'email'
        ELSE 'portal'
    END AS source,
    CASE
        WHEN n % 5 = 0 THEN 'north'
        WHEN n % 5 = 1 THEN 'south'
        WHEN n % 5 = 2 THEN 'east'
        WHEN n % 5 = 3 THEN 'west'
        ELSE 'middle'
    END AS region,
    CASE
        WHEN n % 5 = 0 THEN 'NTH'
        WHEN n % 5 = 1 THEN 'STH'
        WHEN n % 5 = 2 THEN 'EST'
        WHEN n % 5 = 3 THEN 'WST'
        ELSE 'MID'
    END AS region_code,
    CAST(40 + ((n * 73) % 2450) AS REAL) AS amount,
    CASE
        WHEN n % 8 = 0 OR n % 19 = 0 THEN 'yes'
        ELSE 'no'
    END AS retry_value,
    CASE
        WHEN n % 6 = 0 OR n % 17 = 0 THEN 'yes'
        ELSE 'no'
    END AS vip_value,
    CASE
        WHEN n % 11 = 0 THEN 'angry'
        WHEN n % 7 = 0 THEN 'warm'
        WHEN n % 5 = 0 THEN 'calm'
        ELSE 'neutral'
    END AS tone,
    CASE
        WHEN n % 6 = 0 THEN 'lane-update'
        WHEN n % 6 = 1 THEN 'claim'
        WHEN n % 6 = 2 THEN 'eta'
        WHEN n % 6 = 3 THEN 'reroute'
        WHEN n % 6 = 4 THEN 'address'
        ELSE 'handoff'
    END AS topic,
    CASE
        WHEN n % 11 = 0 THEN 'customer says package late and needs rapid lane'
        WHEN n % 8 = 0 THEN 'client asks for quick change and says thanks'
        WHEN n % 7 = 0 THEN 'partner mentions route issue and wants retry'
        WHEN n % 5 = 0 THEN 'shipper asks for address review and lane help'
        ELSE 'customer requests update about delayed shipment'
    END AS raw_text,
    CASE
        WHEN n % 11 = 0 THEN 'customer says package delayed and needs swift lane'
        WHEN n % 8 = 0 THEN 'client asks for rapid change and says thanks'
        WHEN n % 7 = 0 THEN 'partner mentions route problem and wants retry'
        WHEN n % 5 = 0 THEN 'shipper asks for address review and route help'
        ELSE 'customer requests update about delayed delivery'
    END AS shifted_text
FROM seq;

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
        WHEN (instr(lower(raw_text), 'late') > 0 OR instr(lower(raw_text), 'angry') > 0) AND amount > 99 THEN 'STOP_AND_STARE'
        WHEN amount > 999 OR retry_value = 'yes' THEN 'MANUAL_REVIEW'
        WHEN vip_value = 'yes' AND amount < 1000 AND instr(lower(shifted_text), 'thanks') > 0 THEN 'FAST_TRACK'
        WHEN source IN ('fax', 'ivr') THEN 'MANUAL_REVIEW'
        ELSE 'STANDARD_PIPE'
    END AS decision_flag,
    CASE
        WHEN vip_value = 'yes' AND amount < 1000 AND instr(lower(shifted_text), 'thanks') > 0 THEN 1
        WHEN vip_value = 'yes' AND source = 'portal' AND amount < 500 THEN 1
        ELSE 0
    END AS send_partner_copy,
    CASE
        WHEN (instr(lower(raw_text), 'late') > 0 OR instr(lower(raw_text), 'angry') > 0) AND amount > 99 THEN 1
        WHEN amount > 999 OR retry_value = 'yes' OR source IN ('fax', 'ivr') THEN 1
        ELSE 0
    END AS manual_review
FROM seed_runs;

INSERT INTO word_swaps (run_id, swap_index, from_word, to_word)
SELECT run_id, 1, 'late', 'delayed'
FROM seed_runs
WHERE instr(lower(raw_text), 'late') > 0
UNION ALL
SELECT run_id, 1, 'quick', 'rapid'
FROM seed_runs
WHERE instr(lower(raw_text), 'quick') > 0
UNION ALL
SELECT run_id, 1, 'route', 'path'
FROM seed_runs
WHERE instr(lower(raw_text), 'route') > 0
UNION ALL
SELECT run_id, 2, 'rapid', 'swift'
FROM seed_runs
WHERE instr(lower(raw_text), 'rapid') > 0
UNION ALL
SELECT run_id, 2, 'shipment', 'delivery'
FROM seed_runs
WHERE instr(lower(raw_text), 'shipment') > 0
UNION ALL
SELECT run_id, 2, 'address', 'location'
FROM seed_runs
WHERE instr(lower(raw_text), 'address') > 0;

INSERT INTO trail_steps (run_id, trail_index, ticket_value)
SELECT run_id, 1, ticket
FROM seed_runs
UNION ALL
SELECT run_id, 2, printf('%c-%03d', 65 + (run_id % 7), 100 + ((run_id + 11) % 220))
FROM seed_runs
WHERE run_id % 4 != 0
UNION ALL
SELECT run_id, 3, printf('%c-%03d', 65 + ((run_id + 2) % 7), 100 + ((run_id + 23) % 220))
FROM seed_runs
WHERE run_id % 9 = 0;

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
    18 + ((run_id * 13) % 420),
    printf('10.24.%d.%d', 10 + (run_id % 12), 20 + (run_id % 180)),
    ticket,
    run_id
FROM seed_runs;

WITH RECURSIVE seq(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 1240
)
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
    560 + n,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        datetime(
            'now',
            'start of day',
            printf('-%d days', 14 - CAST((n - 1) / 95 AS INTEGER)),
            printf('+%d minutes', 430 + ((n * 17) % 650))
        )
    ),
    CASE
        WHEN n % 7 = 0 THEN 'POST'
        ELSE 'GET'
    END,
    CASE
        WHEN n % 10 = 0 THEN '/api/v1/admin/replay'
        WHEN n % 6 = 0 THEN '/api/v1/admin/ping'
        WHEN n % 5 = 0 THEN '/api/v1/examples/basic'
        WHEN n % 4 = 0 THEN '/api/v1/health'
        ELSE '/'
    END,
    CASE
        WHEN n % 29 = 0 THEN 404
        ELSE 200
    END,
    4 + ((n * 9) % 140),
    printf('10.33.%d.%d', 30 + (n % 8), 40 + (n % 170)),
    CASE
        WHEN n % 10 = 0 THEN printf('%c-%03d', 65 + ((n - 1) % 7), 100 + ((n + 5) % 220))
        ELSE NULL
    END,
    CASE
        WHEN n % 10 = 0 THEN 1 + ((n * 3) % 560)
        ELSE NULL
    END
FROM seq;

DROP TABLE seed_runs;

COMMIT;
