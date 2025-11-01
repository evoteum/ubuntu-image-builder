#!/usr/bin/env python3
import os
import sys
import subprocess
import yaml
from jinja2 import Environment, FileSystemLoader
import argparse


ARGS = None
build_errors = False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build Ubuntu images or render templates only."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration YAML file (absolute or relative). Example: --config /workspace/config.yaml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render YAML templates only; skip image builds.",
    )
    parser.add_argument(
        "--id",
        nargs="+",
        type=int,
        metavar="HOST_ID",
        help="Build only specific host IDs (space-separated). Example: --id 10 12 15",
    )
    parser.add_argument(
        "--fleet",
        nargs="+",
        metavar="FLEET_NAME",
        help="Build all hosts belonging to one or more fleets. Example: --fleet lab prod",
    )
    return parser.parse_args()


def load_config(path):
    """Load YAML configuration from a given path."""
    if not os.path.isfile(path):
        print(f"Error: Config file not found at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dirs(*paths):
    """Create directories if they do not exist."""
    for path in paths:
        os.makedirs(path, exist_ok=True)


def render_template(env, template_name, context):
    """Render a Jinja2 template to string."""
    template = env.get_template(template_name)
    return template.render(context)


def build_image(image_yaml: str, output_img: str, dry_run: bool = False):
    """Run ubuntu-image and capture logs (Ubuntu only)."""
    if dry_run:
        print(f"Would build image {output_img}")
        return
    global build_errors
    log_file = f"{output_img}.log"
    with open(log_file, "w") as log:
        print(f"Building image {output_img} ...")
        result = subprocess.run(
            [
                "ubuntu-image",
                "classic",
                image_yaml,
                "--output-dir",
                os.path.dirname(output_img),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    if result.returncode == 0:
        print(f"Built {output_img}")
    else:
        print(f"Failed to build {output_img}, see {log_file}")
        build_errors = True


def main():
    global ARGS
    ARGS = parse_args()

    if ARGS.dry_run:
        print("Dry run mode! Rendering templates only.")

    config = load_config(ARGS.config)

    defaults = config.get("defaults", {})
    template_dir = defaults.get("template_dir", "templates")
    output_dir = defaults.get("output_dir", "output")

    env = Environment(loader=FileSystemLoader(template_dir))

    fleets = config["fleets"]
    models = config["hardware"]["models"]
    hosts = config["hardware"]["hosts"]
    users = config.get("users", [])

    ensure_dirs(output_dir)

    # --- Filter by fleet ---
    if ARGS.fleet:
        requested_fleets = set(ARGS.fleet)
        available_fleets = {h["fleet"] for h in hosts}
        valid_fleets = requested_fleets & available_fleets
        invalid_fleets = requested_fleets - available_fleets

        if invalid_fleets:
            print(f"Warning: Ignoring unknown fleet(s): {sorted(invalid_fleets)}")

        if not valid_fleets:
            print("No valid fleets provided. Nothing to do.")
            sys.exit(0)

        hosts = [h for h in hosts if h["fleet"] in valid_fleets]
        print(f"Building for fleet(s): {sorted(valid_fleets)}")
    else:
        print("No --fleet specified; building entire estate. Buckle in...")

    # --- Filter by host ID ---
    if ARGS.id:
        requested_ids = set(ARGS.id)
        available_ids = {h["id"] for h in hosts}
        valid_ids = requested_ids & available_ids
        invalid_ids = requested_ids - available_ids

        if invalid_ids:
            print(f"Warning: Ignoring unknown host ID(s): {sorted(invalid_ids)}")

        if not valid_ids:
            print("No valid host IDs provided. Nothing to do.")
            sys.exit(0)

        hosts = [h for h in hosts if h["id"] in valid_ids]
        print(f"Building for host ID(s): {sorted(valid_ids)}")

    # --- Build each host ---
    for host in hosts:
        fleet_name = host["fleet"]
        if fleet_name not in fleets:
            print(f"Error: fleet '{fleet_name}' not defined in {ARGS.config}.")
            sys.exit(1)

        model_name = host["model"]
        model_cfg = models[model_name]
        fleet_cfg = fleets[fleet_name]
        ip_base = fleet_cfg["ip_base"]
        shortname = model_cfg.get("shortname")
        host_id = host.get("id")

        if not all([fleet_name, shortname, host_id]):
            print(f"Error: Missing fleet, shortname, or host_id for host {host}. Skipping.")
            continue

        hostname = f"{fleet_name}-{shortname}-{host_id}"
        ip = f"{ip_base}{host_id}"

        context = {
            "hostname": hostname,
            "ip": ip,
            "model": model_cfg,
            "fleet": fleet_cfg,
            "users": users,
            "config": config.get("defaults", {}),
            "volume": model_cfg.get("volume"),
        }

        host_dir = os.path.join(output_dir, hostname)
        cloud_init_dir = os.path.join(host_dir, "cloud-init")
        ensure_dirs(host_dir, cloud_init_dir)

        user_data = render_template(env, "cloud-init/user-data.yaml.j2", context)
        network_config = render_template(
            env, "cloud-init/network-config.yaml.j2", context
        )
        meta_data = render_template(env, "cloud-init/meta-data.yaml.j2", context)

        with open(os.path.join(cloud_init_dir, "user-data.yaml"), "w") as f:
            f.write(user_data)
        with open(os.path.join(cloud_init_dir, "network-config.yaml"), "w") as f:
            f.write(network_config)
        with open(os.path.join(cloud_init_dir, "meta-data.yaml"), "w") as f:
            f.write(meta_data)

        context.update(
            {
                "user_data": user_data,
                "network_config": network_config,
                "meta_data": meta_data,
            }
        )

        image_yaml_path = os.path.join(host_dir, "image_definition.yaml")
        rendered_image = render_template(env, "image_definition.yaml.j2", context)
        with open(image_yaml_path, "w") as f:
            f.write(rendered_image)

        print(f"Rendered image definition for {hostname} ({ip})")

        output_img = os.path.join(host_dir, f"{hostname}.img")
        build_image(image_yaml_path, output_img, dry_run=ARGS.dry_run)

    if build_errors:
        print("Some build errors occurred.")
        sys.exit(1)

    print(f"\nJob done! Output is in '{output_dir}/'.")


if __name__ == "__main__":
    main()