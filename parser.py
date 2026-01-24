import subprocess
from datetime import datetime

result = subprocess.run(['ps','aux'], capture_output=True, text=True, check=True)
output = result.stdout
lines = output.splitlines()

user_processes = {}
total_cpu = 0.0
total_mem = 0.0
max_cpu = 0.0
max_cpu_process = ""
max_mem = 0.0
max_mem_process = ""

for line in lines[1:]:
    parts = line.split(None, 10)
    user = parts[0]
    cpu = float(parts[2])
    mem = float(parts[3])
    command = parts[10]

    user_processes[user] = user_processes.get(user, 0) + 1

    total_cpu += cpu
    total_mem += mem

    if cpu > max_cpu:
        max_cpu = cpu
        max_cpu_process = command[:20]
    if mem > max_mem:
        max_mem = mem
        max_mem_process = command[:20]

report_lines = []
report_lines.append("Отчёт о состоянии системы:")

user_list = ", ".join(user_processes.keys())
report_lines.append(f"Пользователи системы: {user_list}")
report_lines.append(f"Процессов запущено: {sum(user_processes.values())}\n")

report_lines.append("Пользовательских процессов:")
for user, count in user_processes.items():
    report_lines.append(f"{user}: {count}")

report_lines.append(f"\nВсего памяти используется: {total_mem:.1f}%")
report_lines.append(f"Всего CPU используется: {total_cpu:.1f}%")
report_lines.append(f"Больше всего памяти использует: {max_mem_process}")
report_lines.append(f"Больше всего CPU использует: {max_cpu_process}")

report_text = "\n".join(report_lines)
print(report_text)

filename = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
with open(filename, "w") as f:
    f.write(report_text)
