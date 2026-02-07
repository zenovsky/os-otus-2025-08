import argparse
import json
import os
import re
from collections import Counter
from heapq import nlargest

LOG_PATTERN = re.compile(
    r"(?P<ip>\S+) - - "
    r"\[(?P<time>[^\]]+)] "
    r'"(?P<method>\S+) (?P<url>\S+) \S+" '
    r"(?P<status>\d{3}) "
    r"(?P<size>\S+) "
    r'"(?P<referer>[^"]*)" '
    r'"(?P<agent>[^"]*)" '
    r"(?P<duration>\d+)"
)


HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"}


def parse_log_file(filepath: str) -> dict:
    total_requests = 0
    methods_counter = Counter()
    ip_counter = Counter()
    longest_requests = []

    with open(filepath, encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()
            total_requests += 1

            ip = data["ip"]
            method = data["method"]
            url = data["url"]
            duration = int(data["duration"])
            time_raw = data["time"]

            ip_counter[ip] += 1
            if method in HTTP_METHODS:
                methods_counter[method] += 1

            longest_requests.append(
                {
                    "ip": ip,
                    "method": method,
                    "url": url,
                    "duration_ms": duration,
                    "datetime": time_raw,
                }
            )

    top_ips = ip_counter.most_common(3)
    top_longest = nlargest(3, longest_requests, key=lambda x: x["duration_ms"])

    return {
        "total_requests": total_requests,
        "total_stat": dict(methods_counter),
        "top_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
        "top_longest": top_longest,
    }


def save_json(data: dict, log_filename: str):
    os.makedirs("results", exist_ok=True)
    json_path = os.path.join("results", f"{log_filename}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return json_path


def print_stats(stats: dict, log_name: str):
    print(f"\n=== Анализ логов сервера по {log_name} ===")
    print(f"Общее количество выполненных запросов: {stats['total_requests']}")

    print("\nКоличество запросов по HTTP-методам:")
    for method, count in stats["total_stat"].items():
        print(f"  {method}: {count}")

    print("\nТоп 3 IP адресов, с которых было сделано наибольшее количество запросов")
    for item in stats["top_ips"]:
        print(f"  {item['ip']} — {item['count']} requests")

    print("\nТоп 3 самых долгих запросов")
    for req in stats["top_longest"]:
        print(f"  {req['duration_ms']} ms | {req['method']} {req['url']} | {req['ip']} | {req['datetime']}")


def collect_log_files(path: str) -> list:
    if os.path.isfile(path):
        return [path]

    if os.path.isdir(path):
        return [
            os.path.join(path, filename)
            for filename in os.listdir(path)
            if os.path.isfile(os.path.join(path, filename))
        ]

    raise ValueError("Provided path is neither file nor directory")


def main():
    parser = argparse.ArgumentParser(description="Web server access.log analyzer")
    parser.add_argument("path", help="Path to log file or directory with logs")
    args = parser.parse_args()

    log_files = collect_log_files(args.path)

    for log_file in log_files:
        stats = parse_log_file(log_file)
        log_name = os.path.basename(log_file)

        json_path = save_json(stats, log_name)
        print_stats(stats, log_name)

        print(f"\nJSON saved to: {json_path}")


if __name__ == "__main__":
    main()
