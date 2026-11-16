#!/bin/bash
HOST=$1
THUMBPRINT=$(echo | openssl s_client -servername $HOST -connect $HOST:443 2>/dev/null | openssl x509 -fingerprint -sha1 -noout | sed 's/://g' | cut -d"=" -f2)
echo "{\"thumbprint\":\"$THUMBPRINT\"}"
