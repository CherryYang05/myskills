# Anonymous long-form editorial comparison

## Case en1

### Request

Lightly edit this rollout memo for engineers and support leads who will decide whether to expand the pilot. Remove canned phrasing and repair hard-to-read sentences. Keep the headings, Markdown table, quotation, link target, inline command, chronology, and evidence boundaries. Return only the finished memo.

### Source

# Export queue pilot

## What the pilot covered

To move the needle on our end-to-end export experience, the release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces, while the figures below cover all 42. This distinction is a key thing to note moving forward as we assess the data. The logs provide examples of what went wrong. The table describes how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue. These numbers are a promising step on a broader journey of continuous improvement.

The failure pattern the support engineer the incident lead assigned to the Saturday shift flagged in the sampled logs involved a timeout after the job had written a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said the ticket review the pilot group requested would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

In addition, the pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. They describe the same job, so Support will keep one record for the review and link the other two reports from that record. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The counts in the table are job counts from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

For the purpose of facilitating a clear operational response, the on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket. That gives the pilot group a way to compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.

### Candidate A

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

### Candidate B

# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces. The logs provide examples of what went wrong. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration, calculated only for completed jobs, also fell. The platform team shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a pattern of jobs timing out after writing a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said that the ticket review requested by the pilot group would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from that record. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The counts in the table are job counts from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket. The pilot group can then compare the file record with what the customer could see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.

### Candidate C

# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week covers the same 42 workspaces. We used UTC for both weeks and counted only jobs that started and ended in the same reporting week. The job counts and all other figures in the table exclude jobs still open at the end of their reporting week.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support sampled error logs only from those 9 workspaces. The logs provide examples of what went wrong there. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for how we handled jobs that crossed the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a failure pattern involving a timeout after a job had written a file. The engineer also marked a ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when we drafted this memo. A completed job can still have a file delivery problem. The table measures job completion only.

The pilot group requested a ticket review. The support lead said it would cover both file delivery failures and job failures, with no start date given. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. The review cannot tell us how common the problem is in API exports.

The pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has yet to match all of these reports to the file records. The table counts jobs from the queue regardless of whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview the rerun. The preview does not rerun the job.

If the file record shows the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. Apply the same rerun rule even if a customer asks again or a slot opens in the queue. Support should add the delivery record to the original ticket so the pilot group can compare the file record with what the customer could see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message requests a job review. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should continue the review and apply the same checks.

## Before the next decision

The team proposes using the same workspaces and keeping the retry interval fixed in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports once the additional log sampling and the ticket review are complete. Until then, follow the current on-call procedure. The shift engineer will post any temporary exception in the pilot channel.

### Candidate D

# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot, which ran from 7 to 11 September. The pilot covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces, while the figures below cover all 42. The logs provide examples of what went wrong. The table describes how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a failure pattern involving a timeout after a job had written a file. The engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The pilot group requested a ticket review. The support lead said it would cover delivery failures as well as job failures, but gave no start date. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group also received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for that job in the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The table's job counts come from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job's status and file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket so the pilot group can compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and using a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.

## Case en2

### Request

Edit this personal essay for a small community newsletter. Remove the bits that sound pasted in from a generic essay. Make a light edit where a sentence is hard to follow. Keep the title, paragraph structure, British spelling, quotations, chronology, and the narrator's dry voice. Return only the essay.

### Source

# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

In an age of increasingly impersonal transactions, the neighbourhood repair shop had long served as a vital hub of authentic human connection. Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel the woman the café owner used to send over on Wednesdays left by the till was still there. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

The transition from active service to a state of closure was, in many ways, an exercise in navigating the emotional complexities of change. It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

Ultimately, the closing of the shop was not simply the end of a business, but a testament to the enduring power of ordinary places to shape our lives in extraordinary ways. I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.

### Candidate A

# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel was still by the till. The woman who'd left it was the one the café owner used to send over on Wednesdays. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.

### Candidate B

# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel was still by the till. The woman who'd left it there used to come over on Wednesdays, sent by the café owner. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.

### Candidate C

# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The woman the café owner used to send over on Wednesdays had left a parcel by the till. It was still there, with my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.

### Candidate D

# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The woman the café owner used to send over on Wednesdays had left a parcel by the till. It was still there, with my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
