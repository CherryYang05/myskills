# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both weeks use UTC. The table counts only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from every row, including the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs from those 9 workspaces only, so the examples of failures come from that group. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, the engineer flagged a timeout that occurred after the job had written a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said the ticket review requested by the pilot group would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group also received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The table counts jobs from the queue regardless of whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record shows that the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket so the pilot group can compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message requests a review and gives no authorisation to rerun the job. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.
