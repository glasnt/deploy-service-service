terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

variable "project_id" {
  type = string
}

variable "github_repo" {
  type        = string
  description = "GitHub repo, in the form 'user/repo' or 'org/repo'"
}

variable "service_account" {
  type        = string
  description = "Service account name"
  default     = "my-service-account"
}

variable "pool_id" {
  type        = string
  description = "Workload Identity Pool name"
  default     = "example-pool"
}

variable "provider_id" {
  type        = string
  description = "Workload Identity Provider name"
  default     = "example-gh-provider"
}

# Useful values for later
provider "google" {
  project = var.project_id
}

data "google_project" "project" {
  project_id = var.project_id
}

# Enable multiple services
locals {
  services = [
    "run.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com"
  ]
}
resource "google_project_service" "enabled" {
  for_each                   = toset(local.services)
  project                    = var.project_id
  service                    = each.value
  disable_dependent_services = true
  disable_on_destroy         = false
}

# Create service account with permissions
resource "google_service_account" "sa" {
  account_id = var.service_account
  depends_on = [google_project_service.enabled]
}

# Ensure both Cloud Build and custom SA have builder role
resource "google_project_iam_binding" "cloudbuild_permissions" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  members = ["serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com",
  "serviceAccount:${google_service_account.sa.email}"]
}

# Assign permissions to service account
resource "google_project_iam_binding" "service_permissions" {
  for_each   = toset(["roles/run.developer", "roles/iam.serviceAccountUser", "roles/artifactregistry.admin"])
  project    = var.project_id
  role       = each.value
  members    = ["serviceAccount:${google_service_account.sa.email}"]
  depends_on = [google_service_account.sa]
}

# Use https://github.com/terraform-google-modules/terraform-google-github-actions-runners/tree/master/modules/gh-oidc
module "gh_oidc" {
  source      = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  project_id  = var.project_id
  pool_id     = var.pool_id
  provider_id = var.provider_id
  sa_mapping = {
    (google_service_account.sa.account_id) = {
      sa_name   = "projects/${var.project_id}/serviceAccounts/${google_service_account.sa.email}"
      attribute = "attribute.repository/${var.github_repo}"
    }
  }

  depends_on = [google_project_service.enabled, google_service_account.sa]
}
