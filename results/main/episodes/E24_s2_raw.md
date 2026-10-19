## memory/2026-01-05.md
- Set up Aurora: max containers 402, maintenance start time 20:05.
- The Cedar host uses SSH port 3488; IP address is 10.193.60.28.
- For Aurora, the IP address is set to 10.208.116.17.
- Learned that the Cedar host runs with swap size 910 GB.
- Large log files should be summarized, not pasted.
- Umbra: how long logs are kept = 254 days.

## memory/2026-01-08.md
- Docker commands do not need sudo on this machine.
- Learned that the Umbra service runs with request timeout 6250 ms.
- Umbra: worker count = 378.

## memory/2026-01-11.md
- Noted: Lyra — test coverage threshold: 57%.
- Lyra uses 365 GB as its size of the build cache.
- Learned that the Nimbus service runs with API port 4343.

## memory/2026-01-12.md
- Lyra: code-review deadline = 91 hours.
- Nimbus uses 10:25 as its nightly backup time.
- Proposal to move Aurora to maintenance window 16:45 was rejected; it stays 20:05.

## memory/2026-01-13.md
- Ember request timeout is 7650 ms and its upload limit is 192 MB.
- Learned that the Flint team runs with size of the build cache 890 GB.
- User wants dates written as YYYY-MM-DD.
- For Flint, the monthly cloud budget is set to $7960.

## memory/2026-01-14.md
- Yukon time of the nightly backup is 16:50 and its log retention is 304 days.
- Checked Umbra again: log retention is 254 days.
- Config for Nimbus has request timeout 9650 ms.
- Noted: Velvet — branch it ships from: release-449.
- For Fjord, the DB pool size is set to 243.

## memory/2026-01-17.md
- User switched Nimbus to nightly backup time 10:50.
- Config for Ursa has API port 5049.
- The coverage gate of Flint is 89%.
- Checked Aurora again: maintenance window is 20:05.
- Learned that the Ursa service runs with DB pool size 318.

## memory/2026-01-18.md
- For Onyx, the worker count is set to 343.
- Set up Yarrow: deploy branch release-332, API port 7590.
- Noted: Fjord — HTTP port: 2997.
- Confirmed again that Cedar uses SSH port 3488.

## memory/2026-01-21.md
- The Rune host uses swap size 39 GB; disk quota is 638 GB.
- For Velvet, the HTTP port is set to 5988.
- Learned that the Fjord service runs with deploy branch release-453.
- New request timeout for Ember: 3550 ms.
- The Thistle service uses API port 2658; deploy branch is release-705.

## memory/2026-01-22.md
- For Zenith, the swap size is set to 2766 GB.
- Noted: Onyx — database pool size: 376.
- Config for Zenith has maintenance window 10:15.

## memory/2026-01-23.md
- Noted: Alder — stand-up time: 22:35.
- The IP address of Zenith is 10.25.117.164.
- Alder coverage gate is 99%.

## memory/2026-01-24.md
- Proposal to move Lyra to size of the build cache 134 GB was rejected; it stays 365 GB.
- Ursa DB pool size: 318 (unchanged).
- Reminder: Velvet deploy branch is still release-449.

## memory/2026-01-27.md
- Aurora address is 10.103.60.133 on the backup job only; elsewhere the normal setting applies.
- Juniper uses 74% as its minimum test coverage.
- Run 'make test' before pushing any branch.
- Alder uses 2572 GB as its build cache size.
- User usually works late in the evening.
- The number of workers of Velvet is 79.

## memory/2026-01-29.md
- The shared lab printer is in room 5743.
- Noted: Rune — container limit: 24.
- Update: Zenith moved its maintenance window from 10:15 to 21:50.

## memory/2026-02-01.md
- Noted: Onyx — request timeout: 4300 ms.
- Learned that the Quill team runs with code review SLA 6 hours.
- Reminder: Cedar IP is still 10.193.60.28.

## memory/2026-02-02.md
- Learned that the Ursa service runs with request timeout 8950 ms.
- Iris uses 10.178.27.8 as its IP address.
- For Ember, the deploy branch is set to release-913.
- Update: Flint moved its coverage gate from 89% to 96%.
- Proposal to move Cedar to SSH port 9112 was rejected; it stays 3488.

## memory/2026-02-05.md
- New build cache for Flint: 1627 GB.
- Iris: disk quota = 2983 GB.
- Noted: Quill — build cache size: 1495 GB.

## memory/2026-02-06.md
- Juniper stand-up time is 14:45.
- Double-checked Thistle: the deploy branch remains release-705.
- Yukon uses 3484 as its API port.
- Iris maximum number of containers is 246.
- Yarrow: log retention = 61 days.

## memory/2026-02-07.md
- Config for Nova has code review SLA 77 hours.
- Note that Fridays of Juniper overrides the coverage gate with 98%.
- Zenith now uses 2763 GB as its swap.
- Umbra's log retention has been updated to 213 days.

## memory/2026-02-08.md
- For Juniper, the build cache size is set to 1469 GB.
- New IP for Zenith: 10.55.205.15.
- As of today, the log retention for Yukon is 13 days.

## memory/2026-02-10.md
- As of today, the stand-up time for Alder is 19:40.
- Jasper API port is 7975 and its DB pool size is 476.
- Learned that the Nova team runs with stand-up time 14:50.
- Config for Lumen has stand-up time 21:10.
- Learned that the Thistle service runs with nightly backup time 13:55.

## memory/2026-02-12.md
- Lumen uses 41% as its test coverage threshold.
- Nova monthly cloud spend limit is $5690.
- For Lumen, the build cache size is set to 1547 GB.

## memory/2026-02-14.md
- As of today, the code review SLA for Lyra is 56 hours.
- User usually works late in the evening.
- Nimbus now uses 18:25 as its backup start time.
- Avoid force-pushing to shared branches.

## memory/2026-02-16.md
- The nightly backup time for Yukon is no longer 16:50; it is now 20:45.
- The user reads documentation in English but chats in Korean.
- Update: Velvet moved its number of workers from 79 to 203.
- Grafana dashboard #4024 is the one with the cluster health overview.
- Confirmed again that Lumen uses test coverage threshold 41%.
- Except for the mobile API, where it is 20:10, Thistle keeps its usual nightly backup time.

## memory/2026-02-17.md
- Learned that the Jasper service runs with time of the nightly backup 10:35.
- Thistle deploy branch changed from release-705 to release-541.
- Jasper's DB pool size has been updated to 240.
- Noted: Opal — request timeout: 1300 ms.

## memory/2026-02-18.md
- Yukon log retention period is 36 days on the canary cluster only; elsewhere the normal setting applies.
- Prefer small pull requests with clear titles.
- For Quill, the stand-up time is set to 10:40.
- Considered changing Juniper test coverage threshold to 75%, but decided to keep 74%.
- Opal uses 167 as its worker count.
- User switched Ursa to HTTP timeout 7350 ms.

## memory/2026-02-20.md
- Reminder: Juniper build cache size is still 1469 GB.
- Exception: for Fridays, Nova uses review turnaround target 85 hours.
- Rune disk quota is 2469 GB on weekend runs only; elsewhere the normal setting applies.

## memory/2026-02-22.md
- Except for the canary cluster, where it is release-916, Thistle keeps its usual deploy branch.
- For Opal, the HTTP port is set to 5873.
- New size of the build cache for Lumen: 1337 GB.
- Update: Yarrow moved its API port from 7590 to 2653.
- Except for the mobile API, where it is 3080, Yukon keeps its usual API port.
- As of today, the stand-up time for Quill is 23:40.

## memory/2026-02-25.md
- The IP address for Aurora is no longer 10.208.116.17; it is now 10.155.243.141.
- Proposal to move Umbra to request timeout 2450 ms was rejected; it stays 6250 ms.
- The user reads documentation in English but chats in Korean.
- Jasper API port changed from 7975 to 4273.
- Update: Alder moved its build cache size from 2572 GB to 902 GB.

## memory/2026-02-28.md
- Nova stand-up time changed from 14:50 to 21:40.
- New build cache size for Juniper: 659 GB.
- Double-checked Yarrow: the log retention period remains 61 days.

## memory/2026-03-02.md
- Yukon nightly backup time changed from 20:45 to 20:55.
- User switched Iris to disk limit 2465 GB.
- As of today, the worker count for Umbra is 337.

## memory/2026-03-04.md
- Note that the intern cohort of Quill overrides the code review SLA with 40 hours.
- The time of the stand-up for Lumen is no longer 21:10; it is now 20:25.
- As of today, the swap size for Rune is 2662 GB.
- User switched Nova to code review SLA 83 hours.
- Proposal to move Jasper to API port 7532 was rejected; it stays 4273.
- Jira tickets for infra work go to board 8939.

## memory/2026-03-07.md
- Flint test coverage threshold changed from 96% to 63%.
- As of today, the API port for Yukon is 8827.
- Confirmed again that Nova uses code review SLA 83 hours.
- Zenith maintenance window reverted to 10:15 after problems with 21:50.

## memory/2026-03-10.md
- As of today, the HTTP port for Nimbus is 3527.
- Special case — Opal on batch jobs: API port 4952.
- User likes summaries at the end of long answers.
- Rolled back the size of the build cache change on Lumen; it is 1547 GB again.
- Update: Quill moved its build cache size from 1495 GB to 400 GB.
- Reminder: Zenith maintenance window is still 10:15.

## memory/2026-03-13.md
- Rolled back the swap size change on Rune; it is 39 GB again.
- Confirmed again that Fjord uses API port 2997.
- Lesson learned: the office VPN only works with MTU 4143.

## memory/2026-03-16.md
- User switched Thistle to time of the nightly backup 14:20.
- Update: Velvet moved its listen port from 5988 to 6012.
- The test coverage threshold for Lumen is no longer 41%; it is now 45%.
- Iris disk quota is 347 GB on the backup job only; elsewhere the normal setting applies.
- Note that the GPU queue of Cedar overrides the IP with 10.106.230.108.
- Exception: for hotfix branches, Lyra uses test coverage threshold 50%.

## memory/2026-03-18.md
- New max containers for Iris: 374.
- Avoid force-pushing to shared branches.
- Update: Ursa moved its HTTP port from 5049 to 6844.

## memory/2026-03-20.md
- The request timeout for Ember is no longer 3550 ms; it is now 5250 ms.
- New IP address for Zenith: 10.87.160.167.
- Ember now uses release-747 as its release branch.
- Lumen size of the build cache is 2647 GB on the frontend squad only; elsewhere the normal setting applies.
- Reminder: Ember release branch is still release-747.

## memory/2026-03-22.md
- Note that the mobile API of Velvet overrides the API port with 6412.
- Exception: for batch jobs, Yarrow uses API port 4091.
- Confirmed again that Fjord uses deploy branch release-453.
- Quill build cache is 2087 GB on hotfix branches only; elsewhere the normal setting applies.
- User switched Nova to monthly cloud budget $8290.
- Reminder: Ember request timeout is still 5250 ms.

## memory/2026-03-23.md
- Reminder: Iris disk limit is still 2465 GB.
- Reminder: Yukon log retention period is still 13 days.
- As of today, the request timeout for Opal is 4450 ms.
- As of today, the stand-up time for Lumen is 15:35.

## memory/2026-03-26.md
- Rolled back the stand-up time change on Quill; it is 10:40 again.
- Note that batch jobs of Yarrow overrides the log retention with 244 days.
- Reminder: Alder stand-up time is still 19:40.
- Juniper build cache size changed from 659 GB to 1755 GB.

## memory/2026-03-27.md
- Confirmed again that Lumen uses build cache size 1547 GB.
- Note that the intern cohort of Juniper overrides the stand-up time with 16:20.
- Jasper nightly backup time changed from 10:35 to 20:20.

## memory/2026-03-29.md
- Exception: for hotfix branches, Alder uses size of the build cache 1143 GB.
- Double-checked Quill: the time of the stand-up remains 10:40.
- Exception: for the canary cluster, Velvet uses deploy branch release-568.
- Reminder: Yukon API port is still 8827.

## memory/2026-03-31.md
- Special case — Thistle on staging: API port 8826.
- Special case — Lumen on the intern cohort: stand-up time 11:55.
- Note that the canary cluster of Fjord overrides the deploy branch with release-544.
- New API port for Velvet: 8861.
- Zenith now uses 2679 GB as its swap size.
- User dislikes emoji in commit messages.

## memory/2026-04-03.md
- Considered changing Juniper build cache size to 2950 GB, but decided to keep 1755 GB.
- Zenith maintenance window is 20:50 on the CI runner only; elsewhere the normal setting applies.
- Opal now uses 179 as its worker count.

## memory/2026-04-06.md
- Checked Juniper again: coverage gate is 74%.
- Aurora max containers is 76 on weekend runs only; elsewhere the normal setting applies.
- Except for the mobile API, where it is release-596, Yarrow keeps its usual deploy branch.
- User usually works late in the evening.

## memory/2026-04-09.md
- User switched Iris to max containers 156.
- Reminder: Velvet worker count is still 203.
- Iris disk quota reverted to 2983 GB after problems with 2465 GB.

## memory/2026-04-10.md
- User likes summaries at the end of long answers.
- Confirmed again that Nimbus uses request timeout 9650 ms.
- Update: Opal moved its API port from 5873 to 8421.
- Opal now uses 7950 ms as its timeout for requests.

## memory/2026-04-11.md
- Update: Jasper moved its nightly backup time from 20:20 to 11:20.
- Considered changing Iris container limit to 132, but decided to keep 156.
- Exception: for staging, Velvet uses worker pool size 237.
- Considered changing Opal request timeout to 950 ms, but decided to keep 7950 ms.