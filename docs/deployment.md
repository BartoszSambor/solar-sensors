# Deployment

The app runs at **https://solar-sensors.duckdns.org**.

| | |
|---|---|
| Server | Hetzner Cloud CX23 (x86, 2 vCPU, 4 GB RAM), Helsinki, Ubuntu 24.04 |
| IP | `2.29.172.94` |
| Domain | `solar-sensors.duckdns.org` (DuckDNS, A record pointing at the IP) |
| HTTPS | Caddy, Let's Encrypt certificate obtained and renewed automatically |
| Firewall | Hetzner Cloud Firewall: TCP 22, 80, 443 and UDP 443 |
| App directory | `/root/solar-sensors` |


```
/root/solar-sensors/
├── docker-compose.yml
├── .env
└── caddy/Caddyfile
```

## First deployment

```bash
# Images
docker compose build
docker save solar-sensors-backend solar-sensors-frontend | gzip | ssh root@2.29.172.94 'gunzip | docker load'
```

Start:

```bash
cd ~/solar-sensors && docker compose up -d --no-build
```


## Operations

```bash
docker compose exec backend python -m app.manage create-user <username>
```
