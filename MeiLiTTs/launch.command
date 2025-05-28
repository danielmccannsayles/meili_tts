#!/bin/bash

# Always resolve script path no matter how it's launched
cd "$(dirname "$0")"

# Make sure permissions are set
chmod +x launch.sh

# Launch in a clean login shell with proper PATH
exec /bin/bash --login -c "./launch.sh"