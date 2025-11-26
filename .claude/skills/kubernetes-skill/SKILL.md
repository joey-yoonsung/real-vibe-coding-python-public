---
name: kubernetes-skill
description: "Guide for Kubernetes deployments with Helm charts. Use when working with Helm charts, managing secrets across environments (dev, beta, prod), creating SealedSecrets, or configuring environment-specific values. This skill defines the secret management workflow using Bitnami SealedSecrets."
---

# Kubernetes Secret Management

Standardized approach for managing secrets in Helm charts using Bitnami SealedSecrets.

## Directory Structure

Each Helm chart contains a `secrets/` directory with environment-specific subdirectories:

```
charts/
└── my-app/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    ├── values-beta.yaml
    ├── values-prod.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   └── sealedsecret.yaml    # SealedSecret template
    └── secrets/                  # Secret management directory
        ├── dev/
        │   ├── app.secret.yaml           # Original secret (gitignored)
        │   └── app.sealedsecret.yaml     # Encrypted (committed)
        ├── beta/
        │   ├── app.secret.yaml
        │   └── app.sealedsecret.yaml
        └── prod/
            ├── app.secret.yaml
            └── app.sealedsecret.yaml
```

## File Naming Convention

| File Pattern | Purpose | Git Status |
|--------------|---------|------------|
| `*.secret.yaml` | Original Kubernetes Secret (plaintext) | **gitignored** |
| `*.sealedsecret.yaml` | Encrypted SealedSecret | committed |

## Workflow

### 1. Create Original Secret

Create the plaintext secret file in the environment directory:

```yaml
# secrets/dev/app.secret.yaml (gitignored)
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
  namespace: my-namespace
type: Opaque
stringData:
  DATABASE_PASSWORD: "dev-password-123"
  API_KEY: "dev-api-key-abc"
```

### 2. Generate SealedSecret

Use `kubeseal` to encrypt the secret:

```bash
# Fetch the public key from cluster (one-time setup)
kubeseal --fetch-cert \
  --controller-name=sealed-secrets \
  --controller-namespace=kube-system \
  > pub-cert.pem

# Generate SealedSecret from original secret
kubeseal --format yaml \
  --cert pub-cert.pem \
  < secrets/dev/app.secret.yaml \
  > secrets/dev/app.sealedsecret.yaml
```

### 3. Reference in Values

Environment-specific values reference the sealed secret:

```yaml
# values-dev.yaml
secrets:
  enabled: true
  sealedSecretFile: secrets/dev/app.sealedsecret.yaml

# values-prod.yaml
secrets:
  enabled: true
  sealedSecretFile: secrets/prod/app.sealedsecret.yaml
```

### 4. Template Configuration

The chart's SealedSecret template:

```yaml
# templates/sealedsecret.yaml
{{- if .Values.secrets.enabled }}
{{- $sealedSecret := .Files.Get .Values.secrets.sealedSecretFile | fromYaml }}
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: {{ include "my-app.fullname" . }}-secrets
  namespace: {{ .Release.Namespace }}
spec:
  encryptedData:
    {{- range $key, $value := $sealedSecret.spec.encryptedData }}
    {{ $key }}: {{ $value }}
    {{- end }}
  template:
    metadata:
      name: {{ include "my-app.fullname" . }}-secrets
      namespace: {{ .Release.Namespace }}
{{- end }}
```

## Gitignore Configuration

Add to `.gitignore`:

```gitignore
# Kubernetes secrets (plaintext)
**/secrets/**/*.secret.yaml
```

## Key Principles

1. **Never commit plaintext secrets**: `*.secret.yaml` files are always gitignored
2. **Keep originals locally**: Maintain original secret files for regeneration
3. **Environment isolation**: Each environment has its own sealed secrets
4. **Single source of truth**: Environment-specific values in `values-$env.yaml`
5. **Reproducible**: Can regenerate sealed secrets from originals when certificates rotate

## Secret Rotation

When rotating secrets:

1. Update the original `*.secret.yaml` with new values
2. Regenerate the `*.sealedsecret.yaml` using `kubeseal`
3. Commit only the `*.sealedsecret.yaml` changes
4. Deploy the chart to apply changes

```bash
# Regenerate after secret update
kubeseal --format yaml \
  --cert pub-cert.pem \
  < secrets/prod/app.secret.yaml \
  > secrets/prod/app.sealedsecret.yaml
```

## Certificate Rotation

When the SealedSecret controller certificate rotates:

1. Fetch new certificate: `kubeseal --fetch-cert > pub-cert.pem`
2. Regenerate all sealed secrets from originals
3. Commit and deploy updated sealed secrets
