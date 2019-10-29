# redmine-kanban-readytodone

Making use of Redmine API to track items for Kanban flow measurement / measuring cycle time

'Having a Kanban board and not being able to measure cycle time is like having a surfboard and not knowing how to swim.'
Comment on 'Measure cycle time (lead time)' - Steve Pryce - https://www.redmine.org/boards/1/topics/49667

This really should be a standard feature. As should time spent in each status.

--

The script stores a cache (using TinyDB - json based) of item statuses in your kanban board and outputs a CSV like view 
of the cycle stages and times (defaults to 'Ready' to 'Done' .. could be tweaked to do more / less)

 id,created_on,ready_on,updated_on,closed_on,estimated_hours
 68445,2019-09-05T03:11:48Z,2019-10-29T07:56:55Z,2019-10-29T07:56:55Z,,2.0,0
 60849,2018-12-07T05:19:23Z,2019-10-14T02:48:20Z,2019-10-14T02:48:20Z,,2.0,0
 51903,2018-02-05T01:10:59Z,2019-10-29T09:39:52Z,2019-10-29T09:39:52Z,2019-10-29T08:52:54Z,1.0,-47
