import configparser
from pathlib import Path
import requests

def read_config(config_path="config.txt"):
    path = Path(config_path)
    parser = configparser.ConfigParser()
    parser.read_string("[hub]\n" + path.read_text(encoding="utf-8"))
    cfg = parser["hub"]

    required = ["base_url", "basic_username", "basic_password", "bearer_token"]
    missing = [key for key in required if not cfg.get(key, "").strip()]
    if missing:
        raise ValueError("Missing settings: " + ", ".join(missing))

    return {
        "base_url": cfg["base_url"].rstrip("/"),
        "basic_username": cfg["basic_username"],
        "basic_password": cfg["basic_password"],
        "bearer_token": cfg["bearer_token"],
        "timeout": cfg.getfloat("timeout", fallback=3.0),
    }

def check_authentication(config, session=None):
    client = session or requests
    results = {}
    try:
        response = client.get(
            config["base_url"] + "/basic/sensors",
            auth=(config["basic_username"], config["basic_password"]),
            timeout=config["timeout"],
        )
        results["basic"] = response.status_code == 200
    except requests.RequestException:
        results["basic"] = False

    try:
        response = client.get(
            config["base_url"] + "/bearer/sensors",
            headers={"Authorization": "Bearer " + config["bearer_token"]},
            timeout=config["timeout"],
        )
        results["bearer"] = response.status_code == 200
    except requests.RequestException:
        results["bearer"] = False

    results["valid"] = results["basic"] and results["bearer"]
    return results

def main():
    try:
        result = check_authentication(read_config())
    except (OSError, ValueError, configparser.Error) as exc:
        print(f"Configuration error: {exc}")
        return 1

    print("Basic authentication:", "PASS" if result["basic"] else "FAIL")
    print("Bearer authentication:", "PASS" if result["bearer"] else "FAIL")
    print("Configuration valid:", "YES" if result["valid"] else "NO")
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
