## memory/2026-01-05.md
- The Vega host uses SSH port 6320; disk limit is 708 GB.
- Indigo uses 5710 as its API port.
- Noted: Indigo — nightly backup time: 22:25.
- Vega: swap size = 2709 GB.
- The Maple service uses nightly backup time 10:20; max upload size is 2224 MB.
- Indigo HTTP port: 5710 (unchanged).

## memory/2026-01-08.md
- Maple now uses 16:50 as its nightly backup time.
- Indigo: max upload size = 464 MB.
- The branch it ships from of Maple is release-980.
- Avoid force-pushing to shared branches.
- Set up Dune: nightly backup time 18:55, worker count 408.

## memory/2026-01-09.md
- New number of workers for Dune: 167.
- The HTTP timeout of Dune is 7950 ms.
- Indigo time of the nightly backup changed from 22:25 to 20:45.
- Run 'make test' before pushing any branch.
- Config for Comet has SSH port 6669.
- For Jasper, the IP address is set to 10.49.78.74.

## memory/2026-01-10.md
- Config for Jasper has maintenance window 18:40.
- Indigo API port changed from 5710 to 6862.
- Sierra: daily stand-up = 20:35.
- Jasper disk limit is 2065 GB.

## memory/2026-01-11.md
- The swap size of Comet is 1990 GB.
- Maple time of the nightly backup is 21:45 on the canary cluster only; elsewhere the normal setting applies.
- The max containers of Comet is 224.

## memory/2026-01-13.md
- Double-checked Maple: the nightly backup time remains 16:50.
- Screenshots go to ~/Pictures/shots by default.
- Comet SSH port changed from 6669 to 8371.
- Config for Sierra has max line length 116 chars.

## memory/2026-01-16.md
- Falcon: nightly backup time = 22:50.
- Config for Falcon has HTTP port 3480.
- Solstice: swap = 141 GB.

## memory/2026-01-19.md
- The max containers of Solstice is 195.
- Noted: Falcon — deploy branch: release-936.
- Jira tickets for infra work go to board 4052.
- Config for Pulsar has code review SLA 95 hours.
- Special case — Jasper on the backup job: IP address 10.231.73.6.
- Note that the mobile API of Dune overrides the nightly backup time with 23:55.

## memory/2026-01-21.md
- Config for Sierra has test coverage threshold 97%.
- Noted: Kestrel — nightly backup time: 18:10.
- Reminder: Solstice swap size is still 141 GB.
- Umbra: max line length = 207 chars.

## memory/2026-01-22.md
- Double-checked Dune: the request timeout remains 7950 ms.
- Vega now uses 1297 GB as its disk quota.
- Sierra max line length is 93 chars on the frontend squad only; elsewhere the normal setting applies.
- The stand-up time of Umbra is 18:20.
- Except for Fridays, where it is 101 chars, Umbra keeps its usual max line length.
- User likes summaries at the end of long answers.

## memory/2026-01-25.md
- For Solstice, the IP address is set to 10.79.181.219.
- Kestrel's nightly backup time has been updated to 11:10.
- Pulsar uses $7250 as its monthly cloud budget.
- Solstice's IP address has been updated to 10.106.30.213.
- Except for the GPU queue, where it is 8252, Vega keeps its usual SSH port.

## memory/2026-01-26.md
- Special case — Jasper on the backup job: disk quota 892 GB.
- Update: Maple moved its max upload size from 2224 MB to 2984 MB.
- Config for Kestrel has worker count 219.

## memory/2026-01-29.md
- The DB pool size of Kestrel is 376.
- Pulsar: coverage gate = 70%.
- Falcon now uses release-124 as its release branch.

## memory/2026-02-01.md
- The flaky integration test passes reliably with a retry delay of 9714 ms.
- Umbra uses 69% as its test coverage threshold.
- Note that the canary cluster of Indigo overrides the API port with 5258.
- Confirmed again that Solstice uses IP address 10.106.30.213.

## memory/2026-02-02.md
- Confirmed again that Jasper uses disk quota 2065 GB.
- Note that the frontend squad of Sierra overrides the time of the stand-up with 15:05.
- The test coverage threshold for Umbra is no longer 69%; it is now 98%.
- The deploy branch for Maple is no longer release-980; it is now release-566.
- New IP for Jasper: 10.111.152.51.

## memory/2026-02-03.md
- Pulsar test coverage threshold: 70% (unchanged).
- Update: Kestrel moved its nightly backup time from 11:10 to 21:15.
- Sierra coverage gate changed from 97% to 57%.
- Indigo now uses 13:20 as its nightly backup time.
- User switched Solstice to swap size 1112 GB.
- Except for the CI runner, where it is 696 GB, Vega keeps its usual disk quota.

## memory/2026-02-04.md
- Solstice IP address is 10.202.253.152 on weekend runs only; elsewhere the normal setting applies.
- Use ruff for linting Python code in all repos.
- The stand-up time for Umbra is no longer 18:20; it is now 20:50.
- Checked Sierra again: max line length is 116 chars.

## memory/2026-02-05.md
- Tried branch it ships from release-732 on Maple for a test, reverted immediately; release-566 remains the setting.
- Umbra test coverage threshold: 98% (unchanged).
- Considered changing Falcon API port to 4025, but decided to keep 3480.
- Except for the GPU queue, where it is 284, Comet keeps its usual max containers.
- Except for the GPU queue, where it is 320, Solstice keeps its usual container limit.
- Comet's swap has been updated to 1665 GB.

## memory/2026-02-08.md
- Except for staging, where it is 18:05, Kestrel keeps its usual nightly backup time.
- The GPU node pool autoscaler caps at 393 nodes.
- As of today, the container limit for Comet is 463.
- As of today, the swap size for Comet is 310 GB.

## memory/2026-02-11.md
- Umbra stand-up time: 20:50 (unchanged).
- New IP address for Jasper: 10.100.76.131.
- Note that the GPU queue of Comet overrides the swap with 1211 GB.
- Exception: for weekend runs, Comet uses port for SSH 3471.
- Update: Umbra moved its test coverage threshold from 98% to 79%.

## memory/2026-02-14.md
- As of today, the monthly cloud budget for Pulsar is $1410.
- Except for the intern cohort, where it is 56%, Sierra keeps its usual test coverage threshold.
- Except for the GPU queue, where it is 1895 GB, Solstice keeps its usual swap space.
- The database pool size for Kestrel is no longer 376; it is now 405.

## memory/2026-02-17.md
- Reminder: Kestrel backup start time is still 21:15.
- Except for staging, where it is 7587, Falcon keeps its usual API port.
- User usually works late in the evening.
- The user reads documentation in English but chats in Korean.