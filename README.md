## Docker

### Build

```bash
docker build -t subnet-calculator .
```

### Run

```bash
docker run -d --name subnet-app -p 8000:8000 subnet-calculator
```

### Smoke Test

Jalankan smoke test terhadap container lokal yang sedang berjalan:

```bash
uv run python scripts/smoke_test.py http://127.0.0.1:8000
```