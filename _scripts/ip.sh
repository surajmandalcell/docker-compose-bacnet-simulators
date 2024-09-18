#!/bin/bash

# Function to get host IP
get_host_ip() {
    if grep -qi microsoft /proc/version; then
        # WSL environment
        ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
    else
        # Native Linux
        hostname -I | awk '{print $1}'
    fi
}

# Function to get container information
get_container_info() {
    container_id=$1
    name=$(docker inspect -f '{{.Name}}' "$container_id" | sed 's/\///')
    ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container_id")
    port=$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}}{{end}}' "$container_id")
    hex_port=$(printf "BAC%X" $((port - 47808)))
    echo "$name,$ip,$port,$hex_port"
}

# Main script
host_ip=$(get_host_ip)

# Get all container IDs
container_ids=$(docker-compose ps -q)

# Print header
printf "%-30s %-15s %-15s %-30s\n" "Container Name" "Container IP" "Host Port" "BACnet URL"
printf "%s\n" "$(printf '=%.0s' {1..90})"

# Loop through each container
while IFS= read -r container_id; do
    IFS=',' read -r name ip port hex_port <<< "$(get_container_info "$container_id")"
    bacnet_url="bacnet://$host_ip:$port"
    printf "%-30s %-15s %-15s %-30s\n" "$name" "$ip" "$port ($hex_port)" "$bacnet_url"
done <<< "$container_ids"

# Print host IP information
printf "\nHost IP: %s\n" "$host_ip"
printf "Use this IP to access the services from other machines on the network.\n"