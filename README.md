# NGINXDomainManager

NGINXDomainManager is a Python-based tool to manage NGINX configurations and SSL certificates seamlessly.

## Features

- **Create, Edit, Update, and Delete Subdomains**: Manage NGINX subdomains effortlessly.
- **SSL Certificates**: Obtain and renew SSL certificates using Certbot with a single command.
- **View Logs and Changelogs**: Access logs and changelogs directly from the script menu.
- **Configure Settings**: Customize directories and templates through a user-friendly configuration.
- **Automated Backups**: Ensure your NGINX configurations are always safe with automatic backups.

---

## Quick Start

### **Option 1: Clone the Repository**
  Clone the repository:
   
   ```bash
   git clone https://github.com/Bof98/NGINXDomainManager.git
   cd NGINXDomainManager
```

  Make setup.sh executable:
   
   ```bash
   sudo chmod +x setup.sh
```

  Run the setup script:
   
   ```bash
   sudo ./setup.sh
```

### Option 2: Install via pip (Coming Soon)   

   ```bash
   pip install NGINXDomainManager
```

   After installation, run the application:
   
   ```bash
    nginx-domain-manager
```


## Requirements
NGINX: Installed and running on your server.
Python 3.6+: For running the application.
Certbot: For managing SSL certificates.

### Install Prerequisites on Debian/Ubuntu:
   ```bash
    sudo apt update
```
   ```bash
    sudo apt install nginx python3 python3-pip python3-venv certbot python3-certbot-nginx
```
## Additional Information
Configuration: Modify config.yaml to set up custom directories and templates.

Logs: Logs are stored in /var/log/nginx_domain_manager.log by default.
