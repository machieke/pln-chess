"""Read-only observation of the running preservation tree; sampled lower bounds."""
import argparse
import os
from pathlib import Path
import time
from pln_chess.common import write_json


def run(pid, out):
    ticks = os.sysconf('SC_CLK_TCK'); out = Path(out)
    start = time.time(); samples = 0; peak = 0; cpu = 0; comparison_peak = 0; comparison_cpu = 0
    peak_process = None
    def process(number):
        path = Path('/proc')/str(number)
        try:
            fields = (path/'stat').read_text().rsplit(')', 1)[1].split()
            if fields[0] == 'Z':
                return None
            total = sum(int(fields[i]) for i in (11, 12, 13, 14))/ticks
            status = dict(line.split(':', 1) for line in (path/'status').read_text().splitlines())
            hwm = int(status.get('VmHWM', '0 kB').split()[0])
            children = set()
            for task in (path/'task').iterdir():
                try:
                    children.update(int(n) for n in (task/'children').read_text().split())
                except FileNotFoundError:
                    pass
            return total, hwm, children
        except (FileNotFoundError, ProcessLookupError):
            return None
    while True:
        root = process(pid)
        if root is None:
            break
        pending = [(pid, root)]; seen = set(); current_cpu = 0; child_cpu = 0
        comparison = len(list((out.parent/'preservation/commands').glob('*.json'))) == 209
        while pending:
            number, info = pending.pop()
            if number in seen or info is None:
                continue
            seen.add(number); current_cpu += info[0]
            if number != pid:
                child_cpu += info[0]
            if info[1] > peak:
                peak = info[1]; peak_process = number
            if comparison:
                comparison_peak = max(comparison_peak, info[1])
            pending.extend((child, process(child)) for child in info[2])
        samples += 1; cpu = max(cpu, current_cpu)
        if comparison:
            comparison_cpu = max(comparison_cpu, child_cpu)
        time.sleep(2)
    write_json(out, dict(passed=True, pid=pid, started_unix=start, completed_unix=time.time(), samples=samples,
        interval_seconds=2, observed_process_tree_cpu_seconds_lower_bound=cpu,
        observed_max_process_rss_kib=peak, peak_process=peak_process,
        comparison_observed_max_process_rss_kib=comparison_peak,
        comparison_observed_child_cpu_seconds_lower_bound=comparison_cpu,
        scope='Read-only /proc sampling begun during resumed run; peak values are observed lower bounds, not certified global maxima. Comparison phase starts after 209 completed command receipts. Early interrupted work is excluded.'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--pid', type=int, required=True); p.add_argument('--out', required=True)
    a = p.parse_args(); run(a.pid, a.out)
