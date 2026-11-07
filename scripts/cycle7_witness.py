"""Replay one stored native transcript with this checkout's verified library."""
import argparse
from pln_chess.common import ROOT, read_json
from pln_chess.pln import Runtime

def main():
    p=argparse.ArgumentParser();p.add_argument('index',type=int);p.add_argument('--transcripts',default=str(ROOT/'artifacts/cycle7/native/transcripts.json'));a=p.parse_args()
    records=read_json(a.transcripts)
    if not 0<=a.index<len(records):p.error('Witness index is out of range')
    print(Runtime(timeout=120).execute(records[a.index]['body']),end='')

if __name__=='__main__':main()
