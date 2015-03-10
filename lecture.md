## What is Data Engineering?

<img width="475" src="http://static.slid.es.s3.amazonaws.com/support/insert-video.png">
<img width="475" src="http://static.slid.es.s3.amazonaws.com/support/insert-video.png">

---

## What is a Data Product

vvv

## How is a Data Product

---

## Components of a Data Pipeline

* Always keep raw data, apply a series of transforms to it.
* Data Lineage.
* making data small --> to the put through your model
* Spark and Luigi have this baked in naturally.

vvv

## Ingestion (Kafka)

vvv

## Storage (HDFS)

vvv

## Batch Processing (MapReduce)

vvv

## Query Layer (Impala/Tez/Presto)

vvv 

## Real time/ Speed Layer (Storm)
...

vvv

---

## Architectures

vvv

## Lambda

vvv

## Stream

vvv

## Tradeoffs

* Lambda architecure you have two seperate "codebased" to maintain

vvv

> So, why the excitement about the Lambda Architecture? I think the reason is because people increasingly need to build complex, low-latency processing systems. What they have at their disposal are two things that don’t quite solve their problem: a scalable high-latency batch system that can process historical data and a low-latency stream processing system that can’t reprocess results. By duct taping these two things together, they can actually build a working solution.

[http://radar.oreilly.com/2014/07/questioning-the-lambda-architecture.html](http://radar.oreilly.com/2014/07/questioning-the-lambda-architecture.html)


---

## Technology Trade-offs

vvv

## ASIDE: Distributed Systems Theory

vvv

## CAP Theorem

vvv 

## Consistency

vvv

## Abstraction

> I like the Distributed Systems folks and thinking about logs because it removes (cheats) time from the equation in much the same way that Physicists beat time.

-- Jonathan Dinu

---

## How to Choose

vvv

## Metrics: Measure Everything

---

## Luigi

* Targets: data (files, S3, databases)

* Tasks: operations
  * `requires`
  * `output`
  * `run`
  

Why?

* Idempotence (i.e. no side effects) ensures jobs only run when needed
    * does not however re-run jobs if the input changes
* Checkpointing



* Native Hadoop Support
* But works for any arbitrary scripts



* Sends error emails


