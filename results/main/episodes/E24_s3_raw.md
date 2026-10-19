## memory/2026-01-05.md
- Noted: Birch — address: 10.107.224.32.
- Prefer small pull requests with clear titles.
- Glacier: nightly backup time = 12:35.
- Learned that the Birch host runs with SSH port 6803.
- Birch: maintenance window = 19:05.

## memory/2026-01-08.md
- Config for Rune has code review SLA 27 hours.
- Set up Cedar: maximum line width 77 chars, minimum test coverage 74%.
- Learned that the Harbor service runs with nightly backup time 13:05.
- Avoid force-pushing to shared branches.
- The log retention of Nordic is 362 days.
- Glacier listen port is 2705.

## memory/2026-01-11.md
- Harbor number of workers is 228.
- Nordic branch it ships from is release-540.
- Learned that the Rune team runs with max line length 87 chars.
- New line-length limit for Cedar: 120 chars.
- Update: Birch moved its SSH port from 6803 to 6098.
- Learned that the Rune team runs with monthly cloud budget $6030.

## memory/2026-01-12.md
- Set up Tundra: SSH port 8995, swap space 2636 GB.
- The size of the build cache of Cedar is 2219 GB.
- Update: Harbor moved its nightly backup time from 13:05 to 23:40.
- Tundra disk quota is 2000 GB.
- Confirmed again that Nordic uses deploy branch release-540.
- Noted: Glacier — request timeout: 550 ms.

## memory/2026-01-15.md
- The user reads documentation in English but chats in Korean.
- Nordic: API port = 3625.
- The Flint team uses test coverage threshold 62%; build cache is 1775 GB.
- Harbor log retention period is 325 days.
- Config for Bramble has SSH port 3563.
- Bramble: maintenance window = 12:25.

## memory/2026-01-17.md
- For Quasar, the listen port is set to 6257.
- New code-review deadline for Rune: 94 hours.
- Config for Raven has request timeout 7750 ms.
- The code review SLA of Flint is 17 hours.
- User usually works late in the evening.
- For Raven, the DB pool size is set to 409.

## memory/2026-01-20.md
- For Bramble, the max containers is set to 23.
- Tundra SSH port: 8995 (unchanged).
- Update: Flint moved its build cache size from 1775 GB to 912 GB.
- The backup start time of Quasar is 17:35.
- Update: Tundra moved its swap size from 2636 GB to 116 GB.
- Double-checked Tundra: the swap remains 116 GB.

## memory/2026-01-21.md
- Learned that the Quasar service runs with HTTP timeout 150 ms.
- User switched Raven to DB connection pool 372.
- For Pegasus, the swap size is set to 1123 GB.

## memory/2026-01-24.md
- Raven: deploy branch = release-890.
- Note that the GPU queue of Birch overrides the IP with 10.62.47.167.
- The Kestrel team uses stand-up time 10:35; test coverage threshold is 64%.
- Glacier nightly backup time changed from 12:35 to 21:10.
- Run 'make test' before pushing any branch.
- Prefer small pull requests with clear titles.

## memory/2026-01-26.md
- Tundra disk quota changed from 2000 GB to 1246 GB.
- Rune now uses 119 chars as its max line length.
- Helix uses 63% as its test coverage threshold.
- Zenith IP address is 10.139.232.148 and its disk quota is 2351 GB.

## memory/2026-01-29.md
- Helix code review SLA is 54 hours.
- Pegasus uses 3535 as its SSH port.
- Config for Lumen has code review SLA 83 hours.
- The disk quota of Pegasus is 2680 GB.
- Helix size of the build cache is 1399 GB.

## memory/2026-01-30.md
- For Lumen, the line-length limit is set to 141 chars.
- Avoid force-pushing to shared branches.
- User switched Nordic to log retention 91 days.
- Reminder: Flint build cache is still 912 GB.
- For Krypton, the max upload size is set to 3032 MB.

## memory/2026-02-02.md
- Raven DB pool size changed from 372 to 300.
- For Marlin, the DB pool size is set to 477.
- Marlin deploy branch is release-925.
- For Lumen, the build cache size is set to 2143 GB.

## memory/2026-02-04.md
- Harbor log retention: 325 days (unchanged).
- Redwood: stand-up time = 14:50.
- Exception: for the EU region, Nordic uses listen port 6596.
- Krypton uses 6987 as its listen port.
- The port for SSH for Tundra is no longer 8995; it is now 8648.
- Kestrel code review SLA is 19 hours.

## memory/2026-02-07.md
- Jira tickets for infra work go to board 9779.
- User switched Kestrel to minimum test coverage 71%.
- Run 'make test' before pushing any branch.
- User switched Cedar to minimum test coverage 65%.

## memory/2026-02-09.md
- Config for Krypton has HTTP timeout 8800 ms.
- Config for Zenith has SSH port 2852.
- Config for Vega has swap size 2096 GB.
- The Magma team uses monthly cloud budget $5170; max line length is 148 chars.
- Except for the frontend squad, where it is 2952 GB, Lumen keeps its usual size of the build cache.

## memory/2026-02-11.md
- For Wildfire, the DB pool size is set to 167.
- Prefer small pull requests with clear titles.
- For Redwood, the build cache size is set to 2735 GB.

## memory/2026-02-14.md
- Glacier backup start time is 18:35 on staging only; elsewhere the normal setting applies.
- Cedar line-length limit changed from 120 chars to 123 chars.
- Pulsar log retention is 46 days and its DB pool size is 61.
- Tried deploy branch release-869 on Marlin for a test, reverted immediately; release-925 remains the setting.
- Bramble's maximum number of containers has been updated to 313.

## memory/2026-02-17.md
- Learned that the Redwood team runs with line-length limit 130 chars.
- The request timeout for Glacier is no longer 550 ms; it is now 8350 ms.
- New request timeout for Raven: 4350 ms.
- The flaky integration test passes reliably with a retry delay of 5333 ms.

## memory/2026-02-20.md
- Tried deploy branch release-353 on Raven for a test, reverted immediately; release-890 remains the setting.
- User dislikes emoji in commit messages.
- Note that hotfix branches of Kestrel overrides the stand-up time with 14:05.

## memory/2026-02-23.md
- Learned that the Zircon team runs with code-review deadline 12 hours.
- The container limit of Vega is 58.
- Learned that the Marlin service runs with nightly backup time 20:55.
- Update: Bramble moved its SSH port from 3563 to 3629.
- Config for Wildfire has worker pool size 286.

## memory/2026-02-26.md
- User prefers concise answers with code blocks.
- For Zircon, the max line length is set to 129 chars.
- User switched Glacier to API port 4390.
- Vega maintenance slot is 23:55.
- New max line length for Redwood: 133 chars.

## memory/2026-03-01.md
- Update: Bramble moved its maintenance window from 12:25 to 12:15.
- Reminder: Harbor nightly backup time is still 23:40.
- Confirmed again that Raven uses DB connection pool 300.
- Exception: for hotfix branches, Helix uses build cache size 2214 GB.
- Except for weekend runs, where it is 1079 GB, Vega keeps its usual swap size.

## memory/2026-03-03.md
- User wants dates written as YYYY-MM-DD.
- Learned that the Magma team runs with size of the build cache 2447 GB.
- Nordic log retention reverted to 362 days after problems with 91 days.
- The API port for Krypton is no longer 6987; it is now 6322.
- Pulsar uses release-714 as its deploy branch.

## memory/2026-03-04.md
- Quasar backup start time changed from 17:35 to 22:50.
- As of today, the nightly backup time for Marlin is 16:10.
- Update: Quasar moved its timeout for requests from 150 ms to 1400 ms.
- The disk quota for Pegasus is no longer 2680 GB; it is now 1622 GB.
- Checked Lumen again: max line length is 141 chars.
- The build cache size for Helix is no longer 1399 GB; it is now 2863 GB.

## memory/2026-03-07.md
- User switched Lumen to build cache size 1428 GB.
- New build cache size for Cedar: 489 GB.
- Zircon: cloud spending cap = $9260.
- Double-checked Marlin: the backup start time remains 16:10.
- Wildfire uses 5450 ms as its request timeout.

## memory/2026-03-09.md
- Special case — Bramble on the GPU queue: maintenance window 19:20.
- Quasar HTTP timeout: 1400 ms (unchanged).
- Update: Bramble moved its SSH port from 3629 to 2303.
- Marlin nightly backup time is 11:20 on batch jobs only; elsewhere the normal setting applies.
- Confirmed again that Tundra uses disk quota 1246 GB.
- Special case — Tundra on weekend runs: disk quota 457 GB.

## memory/2026-03-11.md
- Kestrel's stand-up time has been updated to 22:25.
- The API port for Nordic is no longer 3625; it is now 8465.
- Exception: for the canary cluster, Pulsar uses branch it ships from release-870.
- Exception: for Fridays, Magma uses max line length 202 chars.

## memory/2026-03-12.md
- Note that batch jobs of Nordic overrides the deploy branch with release-191.
- Wildfire request timeout changed from 5450 ms to 1300 ms.
- Double-checked Quasar: the API port remains 6257.
- Special case — Wildfire on the canary cluster: DB connection pool 229.
- Confirmed again that Krypton uses request timeout 8800 ms.

## memory/2026-03-15.md
- Redwood now uses 18:15 as its stand-up time.
- Exception: for hotfix branches, Magma uses build cache size 753 GB.
- As of today, the test coverage threshold for Helix is 52%.
- Exception: for Fridays, Kestrel uses minimum test coverage 85%.

## memory/2026-03-18.md
- Checked Pulsar again: DB pool size is 61.
- Docker commands do not need sudo on this machine.
- Docker builds on the laptop need --memory=9321m to avoid OOM kills.
- Double-checked Wildfire: the request timeout remains 1300 ms.
- New DB connection pool for Marlin: 334.
- The HTTP timeout for Raven is no longer 4350 ms; it is now 5500 ms.

## memory/2026-03-21.md
- Special case — Lumen on hotfix branches: max line length 183 chars.
- Double-checked Wildfire: the DB pool size remains 167.
- Special case — Tundra on weekend runs: SSH port 3933.

## memory/2026-03-23.md
- Checked Rune again: line-length limit is 119 chars.
- Bramble max containers: 313 (unchanged).
- User switched Marlin to DB pool size 30.
- Pegasus SSH port changed from 3535 to 3241.

## memory/2026-03-25.md
- Considered changing Helix test coverage threshold to 82%, but decided to keep 52%.
- Special case — Marlin on batch jobs: deploy branch release-194.
- Pegasus SSH port is 6623 on the GPU queue only; elsewhere the normal setting applies.
- Exception: for weekend runs, Vega uses max containers 337.
- Considered changing Wildfire worker count to 92, but decided to keep 286.
- Kestrel now uses 19:55 as its time of the stand-up.

## memory/2026-03-26.md
- Except for the intern cohort, where it is 166 chars, Zircon keeps its usual maximum line width.
- Redwood stand-up time reverted to 14:50 after problems with 18:15.
- Reminder: Zircon max line length is still 129 chars.
- Double-checked Redwood: the stand-up time remains 14:50.
- Grafana dashboard #6813 is the one with the cluster health overview.
- Update: Pegasus moved its disk quota from 1622 GB to 2444 GB.

## memory/2026-03-28.md
- Special case — Redwood on the intern cohort: size of the build cache 607 GB.
- Krypton HTTP timeout is 1650 ms on the canary cluster only; elsewhere the normal setting applies.
- Special case — Pulsar on batch jobs: DB connection pool 465.
- Special case — Quasar on the EU region: API port 4355.

## memory/2026-03-30.md
- Pulsar's deploy branch has been updated to release-700.
- Exception: for the GPU queue, Zenith uses address 10.240.84.97.
- Redwood line-length limit: 133 chars (unchanged).