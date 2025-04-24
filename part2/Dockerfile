FROM ubuntu

# Install system tools and dependencies
RUN apt-get update
RUN apt-get install -y bash iproute2 net-tools tcpdump vim iputils-ping curl gnupg lsb-release

# Add FRR GPG key
RUN curl -s https://deb.frrouting.org/frr/keys.gpg | tee /usr/share/keyrings/frrouting.gpg > /dev/null

# Add FRR repository
RUN echo "deb [signed-by=/usr/share/keyrings/frrouting.gpg] https://deb.frrouting.org/frr $(lsb_release -sc) frr-stable" | tee /etc/apt/sources.list.d/frr.list

# Install FRR and cleanup
RUN apt-get update
RUN apt-get install -y frr frr-pythontools
RUN apt-get clean

# Enable OSPF daemon
RUN sed -i 's/^ospfd=no/ospfd=yes/' /etc/frr/daemons

# Copy in the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
