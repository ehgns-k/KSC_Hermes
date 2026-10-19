## memory/2026-01-05.md
- The Vega host uses maintenance window 21:15; IP address is 10.115.181.131.
- Run 'make test' before pushing any branch.
- Jira tickets for infra work go to board 2531.
- Vega sshd port is 7555.

## memory/2026-01-08.md
- The test coverage threshold of Orion is 91%.
- The license server answers on port 4656.
- Learned that the Orion team runs with code review SLA 15 hours.
- Learned that the Bramble team runs with build cache size 2423 GB.

## memory/2026-01-09.md
- Proposal to move Orion to test coverage threshold 94% was rejected; it stays 91%.
- Learned that the Orion team runs with stand-up time 16:10.
- Confirmed again that Orion uses minimum test coverage 91%.
- Noted: Bramble — test coverage threshold: 48%.
- Delta time of the stand-up is 18:25 and its build cache size is 1527 GB.

## memory/2026-01-10.md
- The flaky integration test passes reliably with a retry delay of 4829 ms.
- Harbor max line length is 105 chars.
- Orion's stand-up time has been updated to 12:50.

## memory/2026-01-11.md
- Prefer small pull requests with clear titles.
- Noted: Falcon — line-length limit: 240 chars.
- Bramble uses 133 chars as its max line length.
- Noted: Delta — monthly cloud budget: $3960.
- For Falcon, the stand-up time is set to 21:25.

## memory/2026-01-13.md
- Falcon: monthly cloud spend limit = $3790.
- Config for Vesper has monthly cloud budget $7250.
- Note that the intern cohort of Orion overrides the coverage gate with 90%.
- Set up Fjord: code review SLA 7 hours, build cache size 1231 GB.
- Noted: Vesper — test coverage threshold: 44%.

## memory/2026-01-15.md
- Learned that the Indigo host runs with IP address 10.49.67.29.
- Noted: Pulsar — worker count: 183.
- Vesper uses 16:55 as its stand-up time.

## memory/2026-01-18.md
- The build cache size of Harbor is 1724 GB.
- Harbor stand-up time is 14:25.
- Indigo: max containers = 379.
- The Kestrel host uses swap space 1014 GB; maintenance slot is 21:40.
- Pulsar DB connection pool is 319.
- Avoid force-pushing to shared branches.

## memory/2026-01-20.md
- Ember max upload size is 2432 MB.
- Note that the frontend squad of Falcon overrides the stand-up time with 22:05.
- Learned that the Wren service runs with request timeout 4950 ms.
- The stand-up time of Comet is 23:25.
- Solstice: nightly backup time = 15:55.
- The max line length of Fjord is 75 chars.

## memory/2026-01-22.md
- Use ruff for linting Python code in all repos.
- For Prism, the maintenance window is set to 14:05.
- For Ember, the deploy branch is set to release-499.
- Considered changing Orion daily stand-up to 12:10, but decided to keep 12:50.
- Solstice: API port = 3901.

## memory/2026-01-24.md
- Wren DB pool size is 287.
- Pulsar: log retention period = 283 days.
- Indigo uses 876 GB as its disk quota.
- User switched Kestrel to swap space 1170 GB.
- Learned that the Prism host runs with disk quota 573 GB.
- Run 'make test' before pushing any branch.

## memory/2026-01-27.md
- Config for Solstice has deploy branch release-375.
- Bramble build cache size: 2423 GB (unchanged).
- Considered changing Harbor max line length to 113 chars, but decided to keep 105 chars.
- Avoid force-pushing to shared branches.

## memory/2026-01-30.md
- For Kestrel, the max containers is set to 218.
- Jasper log retention is 267 days.
- The max line length of Umbra is 120 chars.
- For Maple, the IP address is set to 10.133.200.145.

## memory/2026-01-31.md
- Proposal to move Bramble to max line length 104 chars was rejected; it stays 133 chars.
- The swap space for Kestrel is no longer 1170 GB; it is now 390 GB.
- Grafana dashboard #5033 is the one with the cluster health overview.
- The max line length of Thistle is 82 chars.
- Config for Ember has HTTP port 2855.

## memory/2026-02-03.md
- Prism maintenance window: 14:05 (unchanged).
- Sierra uses 92 as its number of workers.
- For Comet, the line-length limit is set to 213 chars.

## memory/2026-02-06.md
- Umbra uses 2933 GB as its size of the build cache.
- Umbra uses 56 hours as its code review SLA.
- For Thistle, the code review SLA is set to 70 hours.
- Jasper uses 368 MB as its max upload size.

## memory/2026-02-09.md
- Comet monthly cloud budget is $2350.
- Sierra: nightly backup time = 14:55.
- Wren uses 2669 as its API port.
- Except for weekend runs, where it is 211, Kestrel keeps its usual max containers.
- Prism uses 10.220.84.209 as its IP address.
- The timeout for requests of Sierra is 5150 ms.

## memory/2026-02-11.md
- Noted: Jasper — DB pool size: 89.
- Exception: for the intern cohort, Umbra uses build cache size 182 GB.
- Update: Indigo moved its maximum number of containers from 379 to 282.

## memory/2026-02-14.md
- Kestrel now uses 14:20 as its maintenance window.
- Config for Dune has swap space 776 GB.
- Noted: Thistle — time of the stand-up: 15:50.

## memory/2026-02-16.md
- Docker commands do not need sudo on this machine.
- Prism disk quota: 573 GB (unchanged).
- Checked Bramble again: minimum test coverage is 48%.
- Noted: Alder — max upload size: 1216 MB.

## memory/2026-02-18.md
- Special case — Pulsar on the canary cluster: log retention 225 days.
- Comet max line length changed from 213 chars to 93 chars.
- Learned that the Maple host runs with swap size 2119 GB.
- Harbor's size of the build cache has been updated to 1933 GB.

## memory/2026-02-20.md
- Prefer small pull requests with clear titles.
- The maintenance window of Maple is 10:45.
- Basalt uses 2306 as its sshd port.
- The worker count of Alder is 199.

## memory/2026-02-21.md
- Dune: maximum number of containers = 392.
- The IP address for Indigo is no longer 10.49.67.29; it is now 10.80.112.130.
- Dune IP address is 10.64.69.30.
- For Alder, the deploy branch is set to release-655.

## memory/2026-02-23.md
- Update: Indigo moved its disk quota from 876 GB to 855 GB.
- Thistle max line length changed from 82 chars to 187 chars.
- Config for Basalt has swap 2903 GB.
- User likes summaries at the end of long answers.
- As of today, the max upload size for Ember is 1072 MB.

## memory/2026-02-26.md
- Special case — Fjord on the intern cohort: code review SLA 72 hours.
- Tried DB connection pool 373 on Pulsar for a test, reverted immediately; 319 remains the setting.
- Special case — Umbra on Fridays: max line length 163 chars.
- As of today, the test coverage threshold for Bramble is 87%.

## memory/2026-03-01.md
- Except for the frontend squad, where it is 2439 GB, Harbor keeps its usual build cache size.
- Basalt uses 10.44.212.224 as its IP.
- As of today, the number of workers for Alder is 436.
- Vesper now uses 19:40 as its daily stand-up.
- Checked Ember again: API port is 2855.
- User switched Fjord to build cache size 2521 GB.

## memory/2026-03-04.md
- Solstice's deploy branch has been updated to release-281.
- Maple swap is 2667 GB on the CI runner only; elsewhere the normal setting applies.
- Note that weekend runs of Dune overrides the IP address with 10.214.67.54.
- Double-checked Umbra: the code-review deadline remains 56 hours.
- Reminder: Dune address is still 10.64.69.30.
- Update: Solstice moved its nightly backup time from 15:55 to 10:05.

## memory/2026-03-06.md
- Wren API port is 3435 on the mobile API only; elsewhere the normal setting applies.
- Exception: for Fridays, Umbra uses code review SLA 42 hours.
- Exception: for the backup job, Prism uses disk quota 1336 GB.
- Exception: for the CI runner, Maple uses maintenance start time 23:50.
- Note that weekend runs of Basalt overrides the IP address with 10.61.227.87.
- Double-checked Solstice: the backup start time remains 10:05.

## memory/2026-03-09.md
- Thistle max line length reverted to 82 chars after problems with 187 chars.
- As of today, the HTTP port for Ember is 4593.
- Note that the frontend squad of Vesper overrides the time of the stand-up with 17:20.
- User usually works late in the evening.

## memory/2026-03-11.md
- Fjord now uses 83 chars as its max line length.
- Sierra request timeout is 5650 ms on the canary cluster only; elsewhere the normal setting applies.
- User switched Jasper to maximum upload 1200 MB.
- New deploy branch for Ember: release-693.
- The user reads documentation in English but chats in Korean.
- Sierra worker count changed from 92 to 234.

## memory/2026-03-13.md
- Dune now uses 114 as its max containers.
- Considered changing Fjord line-length limit to 203 chars, but decided to keep 83 chars.
- Thistle review turnaround target: 70 hours (unchanged).

## memory/2026-03-16.md
- Update: Dune moved its IP address from 10.64.69.30 to 10.246.49.137.
- Note that the EU region of Ember overrides the max upload size with 2512 MB.
- User wants dates written as YYYY-MM-DD.
- Solstice deploy branch changed from release-281 to release-764.
- The swap size for Maple is no longer 2119 GB; it is now 941 GB.
- Checked Delta again: build cache size is 1527 GB.

## memory/2026-03-18.md
- Checked Prism again: IP address is 10.220.84.209.
- Exception: for the mobile API, Jasper uses DB pool size 472.
- Basalt port for SSH changed from 2306 to 8676.
- As of today, the log retention for Jasper is 170 days.

## memory/2026-03-19.md
- Dune's swap size has been updated to 1848 GB.
- Note that the mobile API of Jasper overrides the maximum upload with 3200 MB.
- User switched Solstice to backup start time 19:15.

## memory/2026-03-21.md
- The stand-up time for Thistle is no longer 15:50; it is now 13:05.
- Checked Fjord again: code review SLA is 7 hours.
- Special case — Harbor on the intern cohort: stand-up time 22:40.
- Tried container limit 215 on Dune for a test, reverted immediately; 114 remains the setting.
- Except for the frontend squad, where it is 185 chars, Comet keeps its usual maximum line width.
- Checked Comet again: max line length is 93 chars.

## memory/2026-03-22.md
- Double-checked Sierra: the request timeout remains 5150 ms.
- Vega maintenance window: 21:15 (unchanged).
- Basalt address: 10.44.212.224 (unchanged).

## memory/2026-03-25.md
- Jasper now uses 1936 MB as its max upload size.
- Reminder: Jasper max upload size is still 1936 MB.
- Alder's deploy branch has been updated to release-698.

## memory/2026-03-26.md
- Checked Fjord again: build cache size is 2521 GB.
- Note that batch jobs of Alder overrides the deploy branch with release-636.