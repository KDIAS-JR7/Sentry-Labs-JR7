FROM alpine:latest

# Install system dependencies
RUN apk add --no-cache openssh-client python3 py3-pip build-base python3-dev

# Install Netmiko (The automation engine)
RUN pip install --no-cache-dir netmiko --break-system-packages

# Create the SSH directory and copy your pre-configured shortcut
RUN mkdir -p /root/.ssh
COPY ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config

WORKDIR /app
CMD ["sh"]
