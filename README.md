# Neo4j playground

Start a neo4j server

```bash
docker run -d \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    --env=NEO4J_AUTH=none \
    --privileged=true \
    neo4j:3.0
```

Seed neo4j

```
pip install -r requirements.txt
./loader.py
```

And then browser on http://127.0.0.1:7474
