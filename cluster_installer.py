import os
from utils import *

###########################################
# INPUT VARIABLES
###########################################

#WAIT_FOR_SECRETS_TIMEOUT = 60
#WAIT_FOR_ACCOUNTS_TIMEOUT = 60

#STANDARD_TIMEOUT="300s"
#BACKSTAGE_PORT_NUMBER = 7007
# ARGOCD_PORT_NUMBER = 30100
# DT_RW_API_TOKEN = os.environ.get("DT_RW_API_TOKEN") # token to create all other tokens
# DT_ENV_NAME = os.environ.get("DT_ENV_NAME") # abc12345
# DT_ENV = os.environ.get("DT_ENV", "live") # dev, sprint" or "live"
#GH_RW_TOKEN = os.environ.get("GH_RW_TOKEN") # Token ArgoCD uses to create "customer-apps" repositories. TODO: What permissions does this need?
#DT_GEOLOCATION = None
#CODESPACE_NAME = os.environ.get("CODESPACE_NAME")
#GITHUB_ORG_SLASH_REPOSITORY = os.environ.get("GITHUB_REPOSITORY") # eg. agardnerIT/mclass
# GITHUB_REPO_NAME = os.environ.get("RepositoryName") # eg. mclass
# GITHUB_DOT_COM_REPO = f"https://github.com/{GITHUB_ORG_SLASH_REPOSITORY}.git"
# GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
# GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
# GITHUB_USER = os.environ.get("GITHUB_USER")
# DT_OAUTH_CLIENT_ID = os.environ.get("DT_OAUTH_CLIENT_ID")
# DT_OAUTH_CLIENT_SECRET = os.environ.get("DT_OAUTH_CLIENT_SECRET")
# DT_OAUTH_ACCOUNT_URN = os.environ.get("DT_OAUTH_ACCOUNT_URN")

if (
    DT_RW_API_TOKEN is None or
    DT_ENV_NAME is None or
    DT_ENV is None or
    GH_RW_TOKEN is None or
    DT_OAUTH_CLIENT_ID is None or
    DT_OAUTH_CLIENT_SECRET is None or
    DT_OAUTH_ACCOUNT_URN is None
):
    exit("Missing mandatory environment variables. Cannot proceed. Exiting.")

# Build DT environment URLs
DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_name=DT_ENV_NAME, dt_env=DT_ENV)
print(f"DT_TENANT_APPS: {DT_TENANT_APPS}. DT_TENANT_LIVE: {DT_TENANT_LIVE}")
# Get correct SSO URL
DT_SSO_TOKEN_URL = get_sso_token_url(dt_env=DT_ENV)
print(f"DT_SSO_TOKEN_URL: {DT_SSO_TOKEN_URL}")

# Create other DT tokens
DT_ALL_INGEST_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_ALL_INGEST_TOKEN", scopes=[
    "bizevents.ingest",
    "events.ingest",
    "logs.ingest",
    "metrics.ingest",
    "openTelemetryTrace.ingest"
], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)
DT_OP_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_OP_TOKEN", scopes=["InstallerDownload"], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)
DT_MONACO_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_MONACO_TOKEN", scopes=[
    "settings.read",
    "settings.write",
    "slo.read",
    "slo.write",
    "DataExport",
    "ExternalSyntheticIntegration",
    "ReadConfig",
    "WriteConfig"
], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)

# Should Keptn be installed or not?
INSTALL_KEPTN = os.environ.get("INSTALL_KEPTN", "true")

if INSTALL_KEPTN.lower() == "false" or INSTALL_KEPTN.lower() == "no":
    # Rename files to prevent installation by argoCD
    try:
        os.rename(src="gitops/applications/platform/keptn.yml", dst="gitops/applications/platform/keptn.yml.BAK")
        os.rename(src="gitops/manifests/platform/keptn/keptn-metrics.yml", dst="gitops/manifests/platform/keptn/keptn-metrics.yml.BAK")
        os.rename(src="gitops/manifests/platform/keptn/otelcol-keptnconfig.yml", dst="gitops/manifests/platform/keptn/otelcol-keptnconfig.yml.BAK")
        git_commit(target_file="-A", commit_msg="do not install Keptn", push=True)
    except:
        print("Exception caught renaming (to remove) Keptn files. No big deal. You're probably re-running this script. Continuing.")

# Set DT GEOLOCATION based on env type used
# TODO: Find a better way here. If this was widely used, all load would be on one GEOLOCATION.
DT_GEOLOCATION = get_geolocation(dt_env=DT_ENV)

# Delete cluster first, in case this is a re-run
run_command(["kind", "delete", "cluster"])

# Find and replace placeholders
# Commit up to repo
# Find and replace DT_TENANT_LIVE_PLACEHOLDER with real text
# Commit back to repo
# Push = False for the first set
# because we push on the final git commit
do_file_replace(pattern="./**/*.yml", find_string="DT_TENANT_LIVE_PLACEHOLDER", replace_string=DT_TENANT_LIVE, recursive=True)
git_commit(target_file="-A", commit_msg="update DT_TENANT_LIVE_PLACEHOLDER", push=False)

# Find and replace DT_TENANT_APPS_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="DT_TENANT_APPS_PLACEHOLDER", replace_string=DT_TENANT_APPS, recursive=True)
git_commit(target_file="-A", commit_msg="update DT_TENANT_APPS_PLACEHOLDER", push=False)

# Find and replace GITHUB_DOT_COM_REPO_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="GITHUB_DOT_COM_REPO_PLACEHOLDER", replace_string=GITHUB_DOT_COM_REPO, recursive=True)
git_commit(target_file="-A", commit_msg="update GITHUB_DOT_COM_REPO_PLACEHOLDER", push=False)

# Find and replace GEOLOCATION_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="GEOLOCATION_PLACEHOLDER", replace_string=DT_GEOLOCATION, recursive=True)
git_commit(target_file="-A", commit_msg="update GEOLOCATION_PLACEHOLDER", push=False)

# Find and replace GITHUB_REPOSITORY_PLACEHOLDER with real text
do_file_replace(pattern="./**/*.yml", find_string="GITHUB_REPOSITORY_PLACEHOLDER", replace_string=GITHUB_ORG_SLASH_REPOSITORY, recursive=True)
git_commit(target_file="-A", commit_msg="update GITHUB_REPOSITORY_PLACEHOLDER", push=True)

# Create cluster
output = run_command(["kind", "create", "cluster", "--config", ".devcontainer/kind-cluster.yml", "--wait", STANDARD_TIMEOUT])

# Create namespaces
namespaces = ["argocd", "opentelemetry", "dynatrace", "backstage", "monaco"]
for namespace in namespaces:
    output = run_command(["kubectl", "create", "namespace", namespace])

# Install argocd
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"])
output = run_command(["kubectl", "wait", "--for=condition=Available=True", "deployments", "-n", "argocd", "--all", f"--timeout={STANDARD_TIMEOUT}"])

# Configure argocd
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "gitops/manifests/platform/argoconfig/argocd-no-tls.yml"])
output = run_command(["kubectl", "apply", "-n", "argocd", "-f", "gitops/manifests/platform/argoconfig/argocd-nodeport.yml"])
output = run_command(["kubectl", "-n", "argocd", "rollout", "restart", "deployment/argocd-server"])
output = run_command(["kubectl", "-n", "argocd", "rollout", "status", "deployment/argocd-server", f"--timeout={STANDARD_TIMEOUT}"])

# Apply platform
output = run_command(["kubectl", "apply", "-f", "gitops/platform.yml"])

# Wait until argo secret exists (or timeout is hit)
wait_for_artifact_to_exist(namespace="argocd", artifact_type="secret", artifact_name="argocd-initial-admin-secret")

# Set the default context to the argocd namespace so 'argocd' CLI works
output = run_command(["kubectl", "config", "set-context", "--current", "--namespace=argocd"])
# Now authenticate
output = run_command(["argocd", "login", "argo", "--core"])

# Wait until argo account 'alice' exists (or timeout is hit)
count = 1
get_argo_accounts_output = ""
while count < WAIT_FOR_ACCOUNTS_TIMEOUT and "alice" not in get_argo_accounts_output:
    print(f"Waiting for argo account alice to exist. Wait count: {count}")
    count += 1
    get_argo_accounts_output = run_command(["argocd", "account", "list"]).stdout
    time.sleep(1)

if get_argo_accounts_output == "":
    exit(f"ArgoCD Account alice does not exist. Cannot proceed.")

ARGOCD_TOKEN = run_command(["argocd", "account", "generate-token", "--account", "alice"]).stdout

if ARGOCD_TOKEN is None or ARGOCD_TOKEN == "":
    exit(f"ARGOCD_TOKEN is empty: {ARGOCD_TOKEN}. Cannot proceed!")

output = run_command(["kubectl", "config", "set-context", "--current", "--namespace=default"])

# create dt-details secret in opentelemetry namespace
output = run_command(["kubectl", "-n", "opentelemetry", "create", "secret", "generic", "dt-details", f"--from-literal=DT_URL={DT_TENANT_LIVE}", f"--from-literal=DT_OTEL_ALL_INGEST_TOKEN={DT_ALL_INGEST_TOKEN}"])

# create backstage-details secret in backstage namespace
output = run_command(["kubectl", "-n", "backstage", "create", "secret", "generic", "backstage-secrets",
                      f"--from-literal=BASE_DOMAIN={CODESPACE_NAME}",
                      f"--from-literal=BACKSTAGE_PORT_NUMBER={BACKSTAGE_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_PORT_NUMBER={ARGOCD_PORT_NUMBER}",
                      f"--from-literal=ARGOCD_TOKEN={ARGOCD_TOKEN}",
                      f"--from-literal=GITHUB_TOKEN={GH_RW_TOKEN}",
                      f"--from-literal=GITHUB_USER={GITHUB_USER}",
                      f"--from-literal=GITHUB_REPO={GITHUB_REPO_NAME}",
                      f"--from-literal=GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN={GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
                      f"--from-literal=DT_TENANT_NAME={DT_ENV_NAME}",
                      f"--from-literal=DT_TENANT_LIVE={DT_TENANT_LIVE}",
                      f"--from-literal=DT_TENANT_APPS={DT_TENANT_APPS}",
                      f"--from-literal=DT_SSO_TOKEN_URL={DT_SSO_TOKEN_URL}",
                      f"--from-literal=DT_OAUTH_CLIENT_ID={DT_OAUTH_CLIENT_ID}",
                      f"--from-literal=DT_OAUTH_CLIENT_SECRET={DT_OAUTH_CLIENT_SECRET}",
                      f"--from-literal=DT_OAUTH_ACCOUNT_URN={DT_OAUTH_ACCOUNT_URN}",
                      f"--from-literal=DT_ALL_INGEST_TOKEN={DT_ALL_INGEST_TOKEN}"
                    ])

# Wait for backstage deployment to be created
wait_for_artifact_to_exist(namespace="backstage", artifact_type="deployment", artifact_name="backstage")
#wait_for_deployment_to_exist(namespace="backstage", deployment_name="backstage")

# Then wait for it to be ready
output = run_command(["kubectl", "wait", "--for=condition=Available=True", "deployments", "-n", "backstage", "backstage", f"--timeout={STANDARD_TIMEOUT}"])

# backstage deployment is ready
# restart backstage to pick up secret and start successfully
output = run_command(["kubectl", "-n", "backstage", "rollout", "restart", "deployment/backstage"])
output = run_command(["kubectl", "-n", "backstage", "rollout", "status", "deployment/backstage", f"--timeout={STANDARD_TIMEOUT}"])

# Create secret for OneAgent in dynatrace namespace
output = run_command([
    "kubectl", "-n", "dynatrace", "create", "secret", "generic", "hot-day-platform-engineering",
    f"--from-literal=apiToken={DT_OP_TOKEN}",
    f"--from-literal=dataIngestToken={DT_ALL_INGEST_TOKEN}"
    ])

# Create bizevent secrets
namespaces = ["dynatrace", "opentelemetry"]
for namespace in namespaces:
    output = run_command(["kubectl", "-n", namespace, "create", "secret", "generic", "dt-bizevent-oauth-details",
                            f"--from-literal=dtTenant={DT_TENANT_LIVE}",
                            f"--from-literal=oAuthClientID={DT_OAUTH_CLIENT_ID}",
                            f"--from-literal=oAuthClientSecret={DT_OAUTH_CLIENT_SECRET}",
                            f"--from-literal=accountURN={DT_OAUTH_ACCOUNT_URN}"
                        ])

# Create monaco-secret in monaco namespace
output = run_command(["kubectl", "-n", "monaco", "create", "secret", "generic", "monaco-secret", f"--from-literal=monacoToken={DT_MONACO_TOKEN}"])
# Create monaco-secret in dynatrace namespace
output = run_command(["kubectl", "-n", "dynatrace", "create", "secret", "generic", "monaco-secret", f"--from-literal=monacoToken={DT_MONACO_TOKEN}"])