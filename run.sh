Bootstrap Script (`run.sh`):
```bash
#!/bin/bash

set -e

echo "Making setup.sh executable..."
chmod +x setup.sh

echo "Running setup.sh..."
sudo ./setup.sh
