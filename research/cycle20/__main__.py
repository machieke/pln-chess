import argparse
from pathlib import Path
from research.cycle19.records import output,external
from .meter import metered
from .demonstrations import compact

def main():
    parser=argparse.ArgumentParser(description='Bounded native belief-workspace research')
    parser.add_argument('mode',choices=('batch','combined','continuation','correction','history','residency','controls','refit','benchmark','comparison-A','comparison-BC','anchors'))
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--meter',type=Path,help='Shared research process ledger')
    args=parser.parse_args();dest=output(args.out);meter=external(args.meter) if args.meter else dest/'meter'
    with metered(meter,args.mode):
        if args.mode=='controls':
            from .controls import run
            run(dest)
        elif args.mode=='refit':
            from .demonstrations import refit
            refit(dest)
        elif args.mode=='comparison-A':
            from .compatibility import compare_all
            compare_all(dest)
        elif args.mode=='comparison-BC':
            from .panel import run_panel
            run_panel(dest)
        elif args.mode=='benchmark':
            from .benchmark import run
            run(dest,meter)
        elif args.mode=='anchors':
            from research.cycle19.anchors import run
            from pln_chess.common import ROOT
            run(ROOT,dest)
        else:compact(args.mode,dest,meter)
    print(args.mode,'completed',dest,flush=True)

if __name__=='__main__':main()
