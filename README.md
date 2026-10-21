# clase4-pipeline-minimo

El pipeline más chico posible, para ir agrandándolo de a un paso. Cada push a `main` le pide a
GitHub una máquina Ubuntu nueva, corre los steps de [`.github/workflows/hola.yml`](.github/workflows/hola.yml)
y la tira.

Usalo como template: **Use this template → Create a new repository** (o copiá los archivos a tu repo).

## Paso 1: lo que ya trae (anda sin configurar nada de GCP)

- Qué máquina nos tocó: sistema, CPUs, memoria, disco, qué viene instalado.
- Que el código no está en la máquina hasta el `actions/checkout`.
- Correr nuestro propio código (`hola.py`).
- Las variables de contexto de GitHub (quién lanzó el run, el commit, el evento).
- Una variable del repo y un secret (el secret sale enmascarado como `***`).

Creá en **Settings → Secrets and variables → Actions**:

| Tipo | Nombre | Valor |
|---|---|---|
| Variable | `SALUDO` | cualquier texto |
| Secret | `CLAVE_DE_PRUEBA` | cualquier texto (no pongas una clave real) |

## Pasos 2 a 4: pegarlos de [`pasos/`](pasos/)

| Archivo | Qué agrega |
|---|---|
| `paso-2a-Dockerfile.txt` | Copialo a la raíz como `Dockerfile` |
| `paso-2b-docker.txt` | `docker build` y `docker run` en el runner: la misma imagen que en la laptop |
| `paso-3-oidc.txt` | Login a GCP por OIDC, sin ninguna clave guardada |
| `paso-4-push.txt` | Push de la imagen a Artifact Registry |

Cada archivo dice dónde se pega. Pegá, commit, push, y mirá el run en **Actions**.

### Lo que necesitan los pasos 3 y 4 en GCP (una vez, como Owner del proyecto)

Supone el repositorio de Artifact Registry `infra-cloud-template` en `us-central1` (clase 3).
Reemplazá `TU_PROYECTO` y `TU_USUARIO/TU_REPO`:

```bash
PROJECT_ID=TU_PROYECTO
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
REPO=TU_USUARIO/TU_REPO          # exacto, con mayúsculas
SA=ci-pipeline@$PROJECT_ID.iam.gserviceaccount.com

gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com artifactregistry.googleapis.com

# 1. La identidad que va a usar el pipeline, con lo mínimo: escribir imágenes.
gcloud iam service-accounts create ci-pipeline --display-name="CI del pipeline mínimo"
gcloud artifacts repositories add-iam-policy-binding infra-cloud-template --location=us-central1 \
  --member=serviceAccount:$SA --role=roles/artifactregistry.writer

# 2. Confiar en GitHub, pero solo en TU repo (la condición es toda la seguridad).
gcloud iam workload-identity-pools create github-pool --location=global
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global --workload-identity-pool=github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='$REPO'"

# 3. Que tu repo pueda "ser" esa service account.
gcloud iam service-accounts add-iam-policy-binding $SA --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"

# 4. El nombre completo del provider, para la variable del repo.
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global --workload-identity-pool=github-pool --format="value(name)"
```

Variables del repo (no son secretos, son identificadores):

| Variable | Valor |
|---|---|
| `GCP_PROJECT_ID` | tu project id |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | la salida del paso 4 (`projects/<NÚMERO>/locations/global/...`) |
| `GCP_SERVICE_ACCOUNT` | `ci-pipeline@TU_PROYECTO.iam.gserviceaccount.com` |

Si el primer run falla con `getAccessToken denied`: el permiso tarda hasta 5 minutos en
propagarse. Esperá y **Re-run failed jobs**.
