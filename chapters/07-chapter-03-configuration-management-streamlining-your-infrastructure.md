# Chapter 3: Configuration Management and Immutable Infrastructure Pipelines

Managing operating system packages, kernel parameters, system daemons, and security baselines across thousands of compute nodes is one of the foundational challenges of systems engineering. Historically, organizations managed servers by provisioning a base operating system and relying on systems administrators—or long-running configuration agents—to mutate files and upgrade packages in place over multi-year lifecycles.

In modern cloud-native engineering, the role of configuration management has undergone a profound architectural shift. Rather than treating production virtual machines and bare-metal servers as long-lived, mutable "pets" patched in place over SSH, modern DevOps combines **declarative configuration management (`ansible-core` 2.17+)** with **immutable image pipelines (HashiCorp Packer)** and **hermetic development environments (Nix Flakes and Devcontainers)**.

In this chapter, we analyze the failure modes of mutable infrastructure drift, master modern **Ansible** using Fully Qualified Collection Names (FQCN) and zero-port-22 **AWS Systems Manager (SSM)** transport, structure reusable hardening roles, automate role verification with **`ansible-lint`** and **`Molecule`**, bake immutable Golden AMIs with **Packer HCL2**, and standardize developer toolchains with **Nix and Devcontainers**.

```mermaid
flowchart LR
    Git["Git Repo (Ansible Roles & Packer HCL2)"]
    Lint["CI Gate: ansible-lint & Molecule (Podman)"]
    Packer["HashiCorp Packer Build (Ephemeral Builder VM)"]
    Ansible["Ansible Provisioner (CIS/Kernel Hardening)"]
    AMI["Immutable Golden AMI / OCI Image"]
    ASG["Production Auto Scaling / Karpenter Nodes"]
    Git --> Lint --> Packer --> Ansible --> AMI --> ASG
```

## Mutable Convergence vs. Immutable Infrastructure

To design a reliable configuration management strategy, you must understand the trade-offs between **mutable convergence** and **immutable replacement**.

### The Failure Modes of Mutable Drift
In first-generation configuration management, tools like Puppet, Chef, SaltStack, or periodic Ansible cron jobs ran directly against live production servers every 30 minutes to "converge" the host toward a desired state. While vastly superior to manual administration, mutable in-place convergence suffers from four systemic failure modes at scale:

1. **Unbounded State Outside Managed Scope**: Configuration management manifests only declare the files and packages you explicitly remember to manage. If an engineer runs a temporary debugging command, or an OS package post-install script modifies an unmanaged file in `/etc`, that mutation persists indefinitely, creating **"Snowflake" servers**.
2. **Non-Atomic Partial Convergence Failures**: When `apt` or `dnf` upgrades 40 system libraries across a 500-node fleet in place and an upstream repository mirror times out on 12 nodes halfway through the run, your production fleet is left in a fractured, half-upgraded state during live customer traffic.
3. **Slow Autoscaling Cold Starts**: When an Auto Scaling Group or Kubernetes node provisioner launches a vanilla OS image under a traffic spike and must run a 15-minute configuration management playbook before joining the cluster, your application cannot scale fast enough to absorb the load.
4. **SSH Bastion Attack Surface**: Running push-based configuration management against live production servers traditionally required exposing TCP port 22 and managing SSH key distribution across every host.

```
+-----------------------------------------------------+
|   MUTABLE CONVERGENCE VS. IMMUTABLE PIPELINES       |
+--------------------+--------------------------------+
| DIMENSION          | MODERN 2026 HYBRID STRATEGY    |
+--------------------+--------------------------------+
| Primary OS &       | Immutable Golden Images baked  |
| Runtime Delivery   | via Packer + Ansible (AMIs) or |
|                    | BuildKit (OCI Containers).     |
+--------------------+--------------------------------+
| Instance / Node    | Never patched in place; nodes  |
| Patching Lifecycle | are drained, terminated, and   |
|                    | replaced (Max Lifetime <= 14d).|
+--------------------+--------------------------------+
| Live Fleet Day-2   | Used for bare-metal servers or |
| Ansible Execution  | emergency zero-day mitigation  |
|                    | via AWS SSM transport.         |
+--------------------+--------------------------------+
| Local & CI         | Declarative Nix Flakes and     |
| Toolchains         | OCI Devcontainers.             |
+--------------------+--------------------------------+
```

### How Ansible Fits into an Immutable Architecture
Does immutable infrastructure make Ansible obsolete? **Not at all.** Writing raw, 500-line Bash shell scripts inside a Packer template or cloud-init userdata block is brittle, non-idempotent, and impossible to unit-test. In a modern 2026 pipeline, **Ansible serves as the declarative, testable configuration engine executed inside Packer during image baking**, as well as the fleet orchestration engine for bare-metal nodes and zero-SSH Systems Manager operations.

## Modern Ansible Architecture: `ansible-core`, Collections, and FQCN

Around version 2.10+, the Ansible project decoupled its core execution engine (**`ansible-core`**) from community and vendor modules, which are now distributed as independently versioned **Ansible Collections** (`ansible.posix`, `amazon.aws`, `kubernetes.core`, `community.general`).

In modern **Ansible (`ansible-core` 2.17+)**, short module names (such as `yum` or `copy`) are deprecated in production style guides because they create namespace collisions across collections. Every task must use its **Fully Qualified Collection Name (FQCN)**—for example, `ansible.builtin.dnf`, `ansible.builtin.template`, `ansible.builtin.systemd_service`, and `ansible.posix.sysctl`.

### Installing Modern Ansible and Execution Environments
Instead of polluting global system Python packages, install `ansible-core`, `ansible-lint`, and `molecule` inside an isolated Python 3.12 virtual environment (or run them inside a containerized **Ansible Execution Environment** via `ansible-navigator`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install ansible-core, linter, and Molecule testing
pip install \
  "ansible-core>=2.17.0,<2.18.0" \
  "ansible-lint>=24.9.0" \
  "molecule>=24.9.0" \
  "molecule-plugins[podman]>=23.5.0"
```

To pin external Ansible Collections deterministically across your team and CI runners, declare them in `requirements.yml`:

```yaml
# requirements.yml
---
collections:
  - name: ansible.posix
    version: ">=1.5.4"
  - name: amazon.aws
    version: ">=8.2.0"
  - name: community.general
    version: ">=9.4.0"
```

Install the pinned collections using `ansible-galaxy`:

```bash
ansible-galaxy collection install -r requirements.yml
```

## Zero-SSH Fleet Management with Dynamic Inventory and AWS SSM

In traditional infrastructure, engineers maintained static `/etc/ansible/hosts` files containing hardcoded IP addresses and connected over SSH bastion hosts (`jumpboxes`). In cloud environments where instances launch and terminate dynamically, static inventories are immediately obsolete, and opening inbound TCP port 22 violates zero-trust network policies.

Modern Ansible solves both problems simultaneously by combining the **`amazon.aws.aws_ec2` Dynamic Inventory Plugin** with the **`community.aws.aws_ssm` Connection Plugin**. Instances run the lightweight AWS SSM Agent with no inbound network ports open at all; Ansible queries the EC2 API dynamically by resource tags and tunnels module execution over encrypted IAM-authenticated SSM sessions:

```yaml
# inventory/aws_ec2.yml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-west-2
filters:
  instance-state-name: running
  "tag:ManagedBy": ansible
keyed_groups:
  - key: tags.Role
    prefix: role
    separator: "_"
  - key: tags.Environment
    prefix: env
    separator: "_"
compose:
  # Connect via Instance ID over AWS SSM (Zero SSH!)
  ansible_host: instance_id
  ansible_connection: "'community.aws.aws_ssm'"
  ansible_aws_ssm_region: "'us-west-2'"
  ansible_aws_ssm_bucket_name: >-
    'enterprise-ssm-session-staging-us-west-2'
```

When you execute `ansible-inventory -i inventory/aws_ec2.yml --graph`, Ansible dynamically discovers all running EC2 instances tagged `ManagedBy=ansible` and groups them automatically into host groups such as `@role_k8s_worker` and `@env_production`.

## Engineering an Idempotent Linux Security Hardening Role

Let us engineer a production-grade Ansible role named `linux_baseline` that configures kernel network and memory security parameters (`sysctl`), enforces SSH daemon hardening (`sshd_config` with validation prior to restart), and configures NTP time synchronization (`chrony`).

A standardized Ansible role follows a deterministic directory layout:

```text
roles/linux_baseline/
├── defaults/
│   └── main.yml
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
└── templates/
    └── sshd_config.j2
```

### 1. Defining Role Defaults (`defaults/main.yml`)
Variables placed in `defaults/main.yml` have the lowest precedence in Ansible, allowing callers to override them cleanly per environment (`group_vars/env_production.yml`) without modifying the role itself:

```yaml
# roles/linux_baseline/defaults/main.yml
---
linux_baseline_sysctl_params:
  net.ipv4.ip_forward: 1
  net.ipv4.conf.all.rp_filter: 1
  net.ipv4.conf.all.accept_source_route: 0
  net.ipv4.conf.all.send_redirects: 0
  net.ipv4.tcp_syncookies: 1
  kernel.kptr_restrict: 2
  kernel.dmesg_restrict: 1
  fs.protected_hardlinks: 1
  fs.protected_symlinks: 1
  vm.max_map_count: 262144

linux_baseline_ssh_port: 22
linux_baseline_ssh_max_auth_tries: 3
```

### 2. Authoring Idempotent Tasks with FQCN (`tasks/main.yml`)
Every task in `tasks/main.yml` uses an explicit FQCN, sets restrictive file permissions (`mode`), and validates configuration files (`validate: /usr/sbin/sshd -t -f %s`) before writing them to disk so that a syntax error can never lock out a node or break a daemon restart:

```yaml
# roles/linux_baseline/tasks/main.yml
---
- name: Install mandatory security and time packages
  ansible.builtin.package:
    name:
      - chrony
      - auditd
      - openssh-server
    state: present
  become: true

- name: Enforce kernel hardening sysctl parameters
  ansible.posix.sysctl:
    name: "{{ item.key }}"
    value: "{{ item.value }}"
    sysctl_file: /etc/sysctl.d/99-cis-hardening.conf
    state: present
    reload: true
  loop: >-
    {{ linux_baseline_sysctl_params | dict2items }}
  become: true

- name: Deploy hardened sshd_config with syntax check
  ansible.builtin.template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    owner: root
    group: root
    mode: "0600"
    validate: "/usr/sbin/sshd -t -f %s"
  notify: Restart sshd service
  become: true

- name: Ensure chronyd and auditd services are active
  ansible.builtin.systemd_service:
    name: "{{ item }}"
    state: started
    enabled: true
  loop:
    - chronyd
    - auditd
  become: true
```

### 3. Event-Driven Handlers (`handlers/main.yml`)
Handlers execute at the end of a play **only if** a notifying task reported `changed: true`. Even if five separate tasks notify `Restart sshd service`, Ansible deduplicates the notification and restarts the daemon exactly once:

```yaml
# roles/linux_baseline/handlers/main.yml
---
- name: Restart sshd service
  ansible.builtin.systemd_service:
    name: sshd
    state: restarted
  become: true
```

### 4. Hardened Jinja2 Template (`templates/sshd_config.j2`)
```jinja2
# {{ ansible_managed }}
Port {{ linux_baseline_ssh_port }}
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries {{ linux_baseline_ssh_max_auth_tries }}
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
UsePAM yes
```

## Continuous Verification with `ansible-lint` and `Molecule`

In a professional DevOps pipeline, configuration management code is subjected to the same static analysis and automated testing gates as application code.

### Static Analysis with `ansible-lint`
`ansible-lint` inspects playbooks, roles, and handlers against production rule sets—catching missing FQCN declarations, risky file permissions (`risky-file-permissions`), unquoted octal file modes (`0600` vs `"0600"`), and non-idempotent `command`/`shell` usages where native modules exist:

```bash
# Run strict production profile linting
ansible-lint --profile production roles/linux_baseline/
```

### Ephemeral Container Testing with `Molecule`
How do you verify that an Ansible role actually converges cleanly, is 100% idempotent on its second run, and places the system into the expected state before baking an AMI? **Molecule** automates the entire test lifecycle using ephemeral **Podman** or **Docker** systemd-enabled containers (`molecule.yml`):

```yaml
# roles/linux_baseline/molecule/default/molecule.yml
---
driver:
  name: podman
platforms:
  - name: al2023-hardened-test
    image: public.ecr.aws/amazonlinux/amazonlinux:2023
    command: /sbin/init
    privileged: true
    pre_build_image: true
provisioner:
  name: ansible
  config_options:
    defaults:
      callbacks_enabled: profile_tasks
verifier:
  name: ansible
```

Inside `roles/linux_baseline/molecule/default/verify.yml`, you write declarative Ansible assertions that inspect the live container state after convergence:

```yaml
# roles/linux_baseline/molecule/default/verify.yml
---
- name: Verify Linux Baseline Security Hardening
  hosts: all
  gather_facts: true
  tasks:
    - name: Read active kernel ip_forward value
      ansible.builtin.command:
        cmd: sysctl -n net.ipv4.ip_forward
      register: sysctl_ip_fwd
      changed_when: false

    - name: Assert sysctl and sshd hardening state
      ansible.builtin.assert:
        that:
          - sysctl_ip_fwd.stdout == "1"
        fail_msg: "Kernel sysctl hardening failed!"
```

Executing `molecule test` runs the complete verification matrix:
1. `dependency`: Pulls required Ansible Collections.
2. `create`: Starts the ephemeral systemd container.
3. `converge`: Applies the `linux_baseline` role against the container.
4. `idempotence`: Re-runs the `linux_baseline` role a second time and **fails the build if any task reports `changed > 0`**.
5. `verify`: Executes `verify.yml` assertions.
6. `destroy`: Tears down the test container.

## Baking Immutable Golden AMIs with HashiCorp Packer (HCL2)

Once our `linux_baseline` Ansible role passes `ansible-lint` and `molecule test`, we integrate it into **HashiCorp Packer** to build immutable, KMS-encrypted **Golden Amazon Machine Images (AMIs)**.

When Packer runs in CI/CD, it launches a temporary EC2 builder instance from the latest upstream Amazon Linux 2023 or Ubuntu 24.04 LTS base image, connects to the builder instance, executes our `site.yml` Ansible playbook to install packages and apply CIS kernel hardening, strips temporary SSH keys and history logs, snapshots the EBS volume into a new encrypted AMI, and terminates the temporary builder VM.

Here is a complete, production-grade Packer HCL2 template (`golden-node.pkr.hcl`):

```hcl
# golden-node.pkr.hcl
packer {
  required_version = ">= 1.11.0"
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1.3"
    }
    ansible = {
      source  = "github.com/hashicorp/ansible"
      version = "~> 1.1"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "kms_key_id" {
  type    = string
  default = "alias/golden-ami-encryption-key"
}

data "amazon-ami" "al2023_arm64" {
  region      = var.aws_region
  most_recent = true
  owners      = ["amazon"]
  filters = {
    name                = "al2023-ami-2023.*-arm64"
    root-device-type    = "ebs"
    virtualization-type = "hvm"
  }
}

locals {
  build_ts = formatdate("YYYYMMDD-hhmm", timestamp())
  ami_name = "golden-al2023-arm64-${local.build_ts}"
}

source "amazon-ebs" "hardened_al2023" {
  region        = var.aws_region
  source_ami    = data.amazon-ami.al2023_arm64.id
  instance_type = "t4g.medium"
  ssh_username  = "ec2-user"
  ami_name      = local.ami_name

  # Enforce EBS encryption and IMDSv2 on Golden AMI
  encrypt_boot = true
  kms_key_id   = var.kms_key_id
  imds_support = "v2.0"

  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    volume_size           = 30
    volume_type           = "gp3"
    iops                  = 3000
    throughput            = 125
    delete_on_termination = true
  }

  tags = {
    Name        = local.ami_name
    BaseAMI     = data.amazon-ami.al2023_arm64.id
    HardenedBy  = "ansible-linux-baseline"
    Architecture = "arm64"
  }
}

build {
  name    = "golden-image-pipeline"
  sources = ["source.amazon-ebs.hardened_al2023"]

  # Run verified Ansible hardening playbook
  provisioner "ansible" {
    playbook_file = "./playbooks/site.yml"
    user          = "ec2-user"
    extra_arguments = [
      "--extra-vars",
      "ansible_python_interpreter=/usr/bin/python3"
    ]
  }

  # Clean machine-id and temporary logs before snapshot
  provisioner "shell" {
    inline = [
      "sudo truncate -s 0 /etc/machine-id",
      "sudo rm -rf /tmp/* /var/tmp/*",
      "sudo dnf clean all"
    ]
  }

  post-processor "manifest" {
    output     = "packer-manifest.json"
    strip_path = true
  }
}
```

Validate and execute the Packer image build via the CLI:

```bash
packer init golden-node.pkr.hcl
packer validate golden-node.pkr.hcl
packer build golden-node.pkr.hcl
```

When `packer build` completes, it outputs `packer-manifest.json` containing the newly minted `artifact_id` (`ami-0987654321fedcba0`), which downstream AWS CDK v2 stacks or Karpenter `EC2NodeClass` manifests consume to roll out immutable nodes across the cluster.

## Reproducible Engineering Toolchains with Nix Flakes and Devcontainers

Configuration drift does not only afflict production servers; it also plagues engineering workstations and CI runners. When one developer runs Ansible 2.14, another runs Ansible 2.17, and a third uses an outdated version of Packer or `cdk-nag`, builds fail unpredictably.

Modern Platform Engineering eliminates workstation drift using **Nix Flakes (`flake.nix`)** and **Development Containers (`devcontainer.json`)**.

Here is a declarative `flake.nix` that pins the exact cryptographic hashes of Python 3.12, `ansible-core`, `ansible-lint`, `packer`, `awscli2`, and `nodejs_22` across Linux (x86_64 and ARM64) and macOS (Apple Silicon):

```nix
# flake.nix
{
  description = "Immutable DevOps Toolchain";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            ansible
            ansible-lint
            packer
            awscli2
            nodejs_22
            jq
          ];
          shellHook = ''
            echo "DevOps 2026 Toolchain Ready"
          '';
        };
      }
    );
}
```

By running `nix develop` (or integrating with `direnv`), any engineer or CI job entering the repository directory is placed immediately into an isolated, bit-for-bit reproducible shell containing the exact toolchain versions required by the platform.

### Standardizing Containerized Workstations with Devcontainers (`devcontainer.json`)
For engineering organizations that standardize on containerized IDE workflows (such as VS Code Dev Containers, GitHub Codespaces, or DevPod), the **Development Container Specification (`devcontainer.json`)** complements Nix Flakes by encapsulating the OS user space, editor extensions, language servers, and security linters inside an OCI image.

Here is a production `.devcontainer/devcontainer.json` specification that pairs a Wolfi/Ubuntu container base with pre-configured Ansible, Packer, and AWS CLI v2 features:

```json
{
  "name": "Platform Configuration Engineering",
  "image": "mcr.microsoft.com/devcontainers/base",
  "features": {
    "ghcr.io/devcontainers/features/aws-cli:1": {
      "version": "latest"
    },
    "ghcr.io/devcontainers/features/terraform:1": {
      "version": "1.9",
      "installSentinel": false
    }
  },
  "postCreateCommand": "pip install -r reqs.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "redhat.ansible",
        "hashicorp.hcl",
        "ms-python.python"
      ],
      "settings": {
        "ansible.validation.lint.enabled": true,
        "ansible.validation.lint.path": "ansible-lint"
      }
    }
  },
  "remoteUser": "vscode"
}
```

### Containerized Ansible Execution Environments (`execution-environment.yml`)
At the enterprise scale, running Ansible playbooks from individual laptops or ad-hoc CI runners introduces Python dependency conflicts between collection requirements (for example, `amazon.aws` requiring specific `boto3` versions while `kubernetes.core` requires specific `kubernetes` Python client versions).

Modern Ansible resolves this via **Ansible Execution Environments (EEs)** built with **`ansible-builder`** and executed via **`ansible-navigator`** or **AWX / Red Hat Ansible Automation Platform**. An Execution Environment packages `ansible-core`, Python dependencies (`requirements.txt`), Ansible Collections (`requirements.yml`), and system libraries (`bindep.txt`) into a single immutable OCI container image:

```yaml
# execution-environment.yml
---
version: 3
images:
  base_image:
    name: quay.io/fedora/fedora-minimal:40
dependencies:
  ansible_core:
    package_pip: ansible-core==2.17.4
  ansible_runner:
    package_pip: ansible-runner
  galaxy: requirements.yml
  python: requirements.txt
additional_build_steps:
  prepend_base:
    - RUN microdnf update -y && microdnf clean all
```

Building and executing playbooks inside this deterministic container image requires only two commands:

```bash
# Build the immutable Ansible Execution Environment OCI
ansible-builder build \
  --tag ghcr.io/enterprise-org/ansible-ee:2026.1

# Run playbooks deterministically inside the EE image
ansible-navigator run playbooks/site.yml \
  --execution-environment-image \
  ghcr.io/enterprise-org/ansible-ee:2026.1 \
  --mode stdout
```

## Summary

Modern configuration management has evolved from mutating long-lived servers in place to engineering deterministic, immutable infrastructure pipelines. By authoring idempotent Ansible roles with strict FQCN syntax, verifying every change automatically with `ansible-lint` and `Molecule`, baking encrypted Golden AMIs with HashiCorp Packer, managing live systems without SSH via AWS SSM, and pinning local and CI toolchains with Nix Flakes, Devcontainers, and Ansible Execution Environments, organizations eliminate configuration drift at its root. In Chapter 4, we connect these infrastructure and application artifacts into automated, keyless CI/CD and GitOps pipelines.
