<div align="center">
  <img src="loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# Come Pubblicare kdiff su Docker Hub

Questa guida spiega come pubblicare l'immagine Docker di kdiff su Docker Hub.

## 1. Prerequisiti

- Account Docker Hub (registrati su https://hub.docker.com se non lo hai già)
- Docker Desktop installato e in esecuzione
- Immagine kdiff già builddata localmente

## 2. Login a Docker Hub

Apri il terminale ed esegui:

```bash
docker login
```

Inserisci username e password del tuo account Docker Hub.

**Alternative con token**: Per maggiore sicurezza, usa un Personal Access Token invece della password:

```bash
# Crea un token su https://hub.docker.com/settings/security
docker login -u YOUR_USERNAME
# Quando richiede la password, incolla il token
```

## 3. Tag dell'Immagine

Tagga l'immagine con il tuo username Docker Hub:

```bash
# Sintassi: docker tag IMAGE_NAME YOUR_DOCKERHUB_USERNAME/IMAGE_NAME:TAG

# Tag latest
docker tag kdiff:latest YOUR_DOCKERHUB_USERNAME/kdiff:latest

# Tag versione specifica
docker tag kdiff:1.0.0 YOUR_DOCKERHUB_USERNAME/kdiff:1.0.0

# Tag aggiuntivi (opzionale)
docker tag kdiff:latest YOUR_DOCKERHUB_USERNAME/kdiff:v1
```

**Esempio concreto**:
```bash
docker tag kdiff:latest maurocasiraghi/kdiff:latest
docker tag kdiff:1.0.0 maurocasiraghi/kdiff:1.0.0
```

## 4. Push su Docker Hub

Pusha l'immagine taggata su Docker Hub:

```bash
# Push tag latest
docker push YOUR_DOCKERHUB_USERNAME/kdiff:latest

# Push versione specifica
docker push YOUR_DOCKERHUB_USERNAME/kdiff:1.0.0
```

**Esempio concreto**:
```bash
docker push maurocasiraghi/kdiff:latest
docker push maurocasiraghi/kdiff:1.0.0
```

Il push potrebbe richiedere alcuni minuti in base alla velocità di connessione.

## 5. Verifica su Docker Hub

1. Vai su https://hub.docker.com
2. Accedi al tuo account
3. Troverai il repository `kdiff` nella lista dei tuoi repository
4. Verifica che i tag siano presenti (latest, 1.0.0, ecc.)

## 6. Configura il Repository (Opzionale ma Raccomandato)

### 6.1 Aggiungi una Descrizione

1. Vai su https://hub.docker.com/repository/docker/YOUR_USERNAME/kdiff
2. Clicca su "Edit" o "Settings"
3. Nella sezione "Description":
   - **Short description**: `Kubernetes cluster comparison tool with intelligent diff detection`
   - **Full description**: Copia il contenuto di `DOCKER_README.md`

### 6.2 Configura Repository come Pubblico

1. Vai in Settings del repository
2. In "Visibility" seleziona "Public"
3. Salva

### 6.3 Aggiungi README Personalizzato

Docker Hub supporta README in formato Markdown. Puoi:

1. Usare il file `DOCKER_README.md` fornito
2. Modificarlo sostituendo `YOUR_DOCKERHUB_USERNAME` con il tuo username effettivo
3. Copiare e incollare nel campo "Full description" su Docker Hub

### 6.4 Configura Automated Builds (Opzionale)

Se hai il codice su GitHub, puoi configurare build automatiche:

1. Collega il tuo account GitHub a Docker Hub
2. In "Builds" > "Configure Automated Builds"
3. Seleziona il repository GitHub
4. Configura le regole di build (es. tag quando fai release)

## 7. Test dell'Immagine Pubblicata

Dopo il push, testa che l'immagine sia scaricabile:

```bash
# Rimuovi l'immagine locale (opzionale)
docker rmi kdiff:latest
docker rmi YOUR_DOCKERHUB_USERNAME/kdiff:latest

# Scarica e testa l'immagine da Docker Hub
docker run --rm YOUR_DOCKERHUB_USERNAME/kdiff:latest --help
```

**Esempio concreto**:
```bash
docker run --rm maurocasiraghi/kdiff:latest --help
```

## 8. Aggiornamenti Futuri

Quando pubblichi nuove versioni:

```bash
# 1. Build della nuova versione
docker build -t kdiff:1.1.0 -t kdiff:latest .

# 2. Tag con versione
docker tag kdiff:1.1.0 YOUR_DOCKERHUB_USERNAME/kdiff:1.1.0
docker tag kdiff:latest YOUR_DOCKERHUB_USERNAME/kdiff:latest

# 3. Push di entrambi i tag
docker push YOUR_DOCKERHUB_USERNAME/kdiff:1.1.0
docker push YOUR_DOCKERHUB_USERNAME/kdiff:latest
```

**Best Practices per Versioning**:
- `latest`: sempre l'ultima versione stable
- `1.0.0`, `1.1.0`, ecc.: versioni specifiche
- `v1`, `v2`: major versions
- `dev` o `nightly`: versioni in sviluppo

## 9. Script Automatico per Pubblicazione

Crea uno script `publish-docker.sh`:

```bash
#!/bin/bash
set -e

VERSION=${1:-latest}
DOCKER_USERNAME=${DOCKER_USERNAME:-YOUR_DOCKERHUB_USERNAME}

echo "🔨 Building kdiff:$VERSION..."
docker build -t kdiff:$VERSION -t kdiff:latest .

echo "🏷️  Tagging images..."
docker tag kdiff:$VERSION $DOCKER_USERNAME/kdiff:$VERSION
docker tag kdiff:latest $DOCKER_USERNAME/kdiff:latest

echo "📤 Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/kdiff:$VERSION
docker push $DOCKER_USERNAME/kdiff:latest

echo "✅ Successfully published $DOCKER_USERNAME/kdiff:$VERSION"
echo "📦 Image available at: https://hub.docker.com/r/$DOCKER_USERNAME/kdiff"
```

Usa così:
```bash
chmod +x publish-docker.sh
./publish-docker.sh 1.0.0
```

## 10. Promozione del Repository

### Nel README principale del progetto:

Aggiungi i badge:
```markdown
![Docker Image Size](https://img.shields.io/docker/image-size/YOUR_USERNAME/kdiff)
![Docker Pulls](https://img.shields.io/docker/pulls/YOUR_USERNAME/kdiff)
![Docker Stars](https://img.shields.io/docker/stars/YOUR_USERNAME/kdiff)
```

Aggiungi sezione di installazione:
```markdown
## Docker Installation

```bash
docker pull YOUR_USERNAME/kdiff:latest
```
```

### Su Docker Hub:

- Aggiungi link al repository GitHub
- Usa le categorie appropriate (DevOps, Kubernetes, Monitoring)
- Aggiungi screenshot del report HTML

## 11. Comandi Utili di Riferimento

```bash
# Verifica immagini locali
docker images kdiff

# Verifica immagini remote
docker search YOUR_USERNAME/kdiff

# Scarica immagine specifica
docker pull YOUR_USERNAME/kdiff:1.0.0

# Ispeziona immagine
docker inspect YOUR_USERNAME/kdiff:latest

# Visualizza layers
docker history YOUR_USERNAME/kdiff:latest

# Rimuovi immagini locali non utilizzate
docker image prune

# Logout da Docker Hub
docker logout
```

## 12. Troubleshooting

### Errore "denied: requested access to the resource is denied"
- Verifica di aver fatto login: `docker login`
- Verifica che il username nel tag sia corretto
- Verifica i permessi del token se usi PAT

### Errore "unauthorized: authentication required"
- Fai logout e re-login: `docker logout && docker login`
- Verifica che username/password siano corretti

### Push molto lento
- Usa multi-stage builds per ridurre la dimensione
- Verifica la connessione internet
- Considera di usare Docker Hub automated builds

### Immagine non trovata dopo il push
- Attendi 1-2 minuti (propagazione)
- Verifica su https://hub.docker.com
- Controlla che il tag sia corretto

## Riepilogo Veloce

```bash
# 1. Login
docker login

# 2. Tag
docker tag kdiff:latest YOUR_USERNAME/kdiff:latest
docker tag kdiff:1.0.0 YOUR_USERNAME/kdiff:1.0.0

# 3. Push
docker push YOUR_USERNAME/kdiff:latest
docker push YOUR_USERNAME/kdiff:1.0.0

# 4. Test
docker run --rm YOUR_USERNAME/kdiff:latest --help
```

Fatto! 🎉
