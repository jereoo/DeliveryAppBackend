# DeliveryAppBackend

**Build**: v1.0.0-build.001 | **Status**: ✅ BACKEND COMPLETE

A Django REST API for managing package deliveries with complete self-registration workflow. Drivers self-register with their vehicles, customers register individually, and request deliveries from location A to location B.

**Related repository:** the Expo client lives in **`jereoo/DeliveryAppMobile`** (separate GitHub repo). This repo’s canonical line is branch **`main`** (Heroku deploys from here). The legacy **`master`** branch on this remote was a full-stack monorepo layout; prefer the dedicated mobile repo for app work.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jereoo/DeliveryAppBackend.git
   cd DeliveryAppBackend