

### dev


1. Download logs files from Erigon for example:
```
scp ubuntu@54.36.174.74:/home/ubuntu/ledgerwatch/erigon/goerli_err.log .
```

2. Run analyze_logs.py generating output.json

```
python analyze_logs.py
```

4. Run plot.html locally (for example)

```
python -m http.server
```

Extracting Erigoon log from journal

```
journalctl _PID=`pgrep erigon` > erigon.log
```