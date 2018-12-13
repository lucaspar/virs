---
description: Visualization and Information Retrieval System
---

# VIRS

> Refer to [https://github.com/lucaspar/virs](https://github.com/lucaspar/virs)

## Getting started

**Shell 1 - run containers**

```bash
docker-compose up
```

**Shell 2 - run interactive shell**

```bash
docker-compose run web bash

# run migrations
./manage.py makemigrations
./manage.py migrate
```

**Access localhost:8000**

## **Implemented Features**

* Upload of custom collection
* Postings list visualization
* Vector Space Model representation
* Search by cosine similarity
* PageRank scores by iteration step
* PageRank visual representation

{% page-ref page="virs.md" %}

{% page-ref page="other-tasks.md" %}

