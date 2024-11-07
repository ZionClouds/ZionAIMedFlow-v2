docker run --rm -d \
    -p 10000:10000 -p 10001:10001 -p 10002:10002 \
    -v /home/alex/containers/azurestorage:/data \
    mcr.microsoft.com/azure-storage/azurite
