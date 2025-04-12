## Overview

This repository is a part of Protrack project, it provides APIs for chatbot feature

## How to run

**1. Clone project**

```bash
git clone git@github.com:quocsi014/protrack-chatbot-api.git
```

**2. Create .env file**

```bash
cd protrack-chatbot-api
cp .env.sample .env
```

**3. Run**

- With Docker

```bash
docker compose up --build
```

- With python (Need to deploy chromaDB)

```bash
pip install -r requirements/util-lib.txt
pip install -r requirements/ai-lib.txt
python3 main.py
```
