import argparse
import subprocess

# Routers + OSPF config
routers = {
    "r1": {
        "router_id": "192.168.1.1",
        "networks": ["10.0.14.0/24", "10.0.16.0/24", "10.0.17.0/24"],
        "interface_costs": {"eth0": 10, "eth1": 10, "eth2": 100}
    },
    "r2": {
        "router_id": "192.168.1.2",
        "networks": ["10.0.16.0/24", "10.0.18.0/24"],
        "interface_costs": {"eth0": 10, "eth1": 10}
    },
    "r3": {
        "router_id": "192.168.1.3",
        "networks": ["10.0.15.0/24", "10.0.18.0/24", "10.0.19.0/24"],
        "interface_costs": {"eth0": 10, "eth1": 10, "eth2": 100}
    },
    "r4": {
        "router_id": "192.168.1.4",
        "networks": ["10.0.17.0/24", "10.0.19.0/24"],
        "interface_costs": {"eth0": 100, "eth1": 100}
    }
}

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def configure_router(container_name, config):
    run_cmd(f"docker exec {container_name} sed -i 's/ospfd=no/ospfd=yes/' /etc/frr/daemons")
    run_cmd(f"docker exec {container_name} service frr restart")

    vtysh_commands = [
        "configure terminal",
        "router ospf",
        f"ospf router-id {config['router_id']}"
    ] + [f"network {net} area 0.0.0.0" for net in config['networks']] + ["exit"]

    for iface, cost in config['interface_costs'].items():
        vtysh_commands += [f"interface {iface}", f"ip ospf cost {cost}", "exit"]

    vtysh_commands += ["end", "write memory"]

    full_vtysh = "vtysh " + " ".join(f"-c \"{cmd}\"" for cmd in vtysh_commands)
    run_cmd(f"docker exec {container_name} {full_vtysh}")

def setup_topology():
    print("Bringing up Docker topology...")
    subprocess.run(["docker", "compose", "build"], check=True)
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

def switch_path(path):
    print(f"Switching to {path} path...")

    if path == "north":
        # Prefer R1 → R2 → R3
        run_cmd("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 10' -c 'interface eth2' -c 'ip ospf cost 100' -c 'end' -c 'write memory'")
        run_cmd("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 10' -c 'interface eth1' -c 'ip ospf cost 10' -c 'end' -c 'write memory'")
        run_cmd("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 10' -c 'interface eth2' -c 'ip ospf cost 100' -c 'end' -c 'write memory'")
        run_cmd("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 100' -c 'interface eth1' -c 'ip ospf cost 100' -c 'end' -c 'write memory'")

    elif path == "south":
        # Prefer R1 → R4 → R3
        run_cmd("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 100' -c 'interface eth2' -c 'ip ospf cost 10' -c 'end' -c 'write memory'")
        run_cmd("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 100' -c 'interface eth1' -c 'ip ospf cost 100' -c 'end' -c 'write memory'")
        run_cmd("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 100' -c 'interface eth2' -c 'ip ospf cost 10' -c 'end' -c 'write memory'")
        run_cmd("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 10' -c 'interface eth1' -c 'ip ospf cost 10' -c 'end' -c 'write memory'")
        
    for router in ["r1", "r2", "r3", "r4"]:
        run_cmd(f"docker exec {router} vtysh -c 'clear ip ospf process'")

def install_host_routes():
    print("Installing host routes...")

    # Change HB default route
    run_cmd("docker exec hb ip route del default || true")  # `|| true` avoids crash if default doesn't exist
    run_cmd("docker exec hb ip route add default via 10.0.15.10")

    # Change HA default route
    run_cmd("docker exec ha ip route del default || true")
    run_cmd("docker exec ha ip route add default via 10.0.14.20")

# === Main Entry ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orchestrator script for managing the routed Docker network topology")
    parser.add_argument("--setup-topology", action="store_true", help="Setup Docker topology and assign IPs")
    parser.add_argument("--start-ospf", action="store_true", help="Start OSPF daemons in routers")
    parser.add_argument("--install-host-routes", action="store_true", help="Install routes on hosts")
    parser.add_argument("--switch-path", choices=["north", "south"], help="Switch traffic path")

    args = parser.parse_args()

    if args.setup_topology:
        setup_topology()

    if args.start_ospf:
        print("Starting OSPF daemons...")
        for router_name, cfg in routers.items():
            configure_router(router_name, cfg)

    if args.install_host_routes:
        install_host_routes()

    if args.switch_path:
        switch_path(args.switch_path)
