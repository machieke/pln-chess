"""Optional local-history source review plus an executed Boolean-helper check."""
import hashlib,subprocess
from pathlib import Path
from pln_chess.pln import Runtime
from pln_chess.common import write_json

def audit(output):
    rt=Runtime();expr='(Consistency_ImplicationImplicantConjunction 0.2 0.3 0.4 0.8 0.7)'
    raw=rt.execute(f'!(println! (CONSISTENCY {expr}))')
    result={'runtime':rt.manifest,'consistency_helper':{'source':'vendor/pln/lib_pln.metta','line':56,'expression':expr,'stdout':raw,
        'interpretation':'Boolean marginal consistency helper; no STV, And predicate, or conjunction inference rule is introduced.'},
        'local_experimental_upstream':{'status':'not available locally'},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    root=Path('/tmp/pln-experimental-audit')
    paths=['experimental/truth-value-formula/conjunction-introduction/README.md','experimental/truth-value-formula/conjunction-introduction/conjunction-xp.mac']
    if (root/'.git').exists() and all((root/p).exists() for p in paths):
        result['local_experimental_upstream']={'head':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
            'files':[{'path':p,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p in paths],'status':'source-inspected only',
            'interpretation':'Maxima formula/distribution experiments and explanatory notes; no executable MeTTa conjunction rule in the pinned PeTTa library. No port or activation performed.'}
    assert '(CONSISTENCY true)' in raw
    write_json(output,result);return result

if __name__=='__main__':
    import sys
    audit(sys.argv[1])
