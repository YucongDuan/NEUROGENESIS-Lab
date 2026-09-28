"""Command-line entry point with explicit input and output paths."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .core import ValidationError, canonical, load_json, write_json
from .experiments import run, catalog
from .capsule import save, verify, replay
from .calibration import fit_csv
from .reporting import report_html


def main(argv=None):
    p=argparse.ArgumentParser(description='NEUROGENESIS-Lab | Nervous-system research workbench')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('list',help='List executable experiments and book anchors')
    r=sub.add_parser('run',help='Run an experiment; optionally save a reproducible capsule')
    r.add_argument('experiment');r.add_argument('--params',type=Path);r.add_argument('--out',type=Path)
    for action in ['verify-run','replay']:
        a=sub.add_parser(action);a.add_argument('path',type=Path);a.add_argument('--trusted-digest')
    a=sub.add_parser('fit');a.add_argument('--data',type=Path,required=True);a.add_argument('--metadata',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('serve');a.add_argument('--port',type=int,default=8766)
    a=sub.add_parser('demo');a.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('bridge');a.add_argument('--input',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        if args.command=='list':
            print(canonical({k:{'title':v['title'],'book_sections':v['book_sections']} for k,v in catalog().items()}))
        elif args.command=='run':
            params=load_json(args.params) if args.params else {}
            result=save(args.experiment,params,args.out) if args.out else run(args.experiment,params)
            print(canonical(result))
        elif args.command=='verify-run':print(canonical(verify(args.path,args.trusted_digest)))
        elif args.command=='replay':
            report=replay(args.path,args.trusted_digest);print(canonical(report))
            if not report['numerically_equal']:return 1
        elif args.command=='fit':
            if args.data.is_symlink() or not args.data.is_file() or args.data.stat().st_size>500000:raise ValidationError('Expected a bounded regular CSV file')
            print(canonical(save('fit-passive',load_json(args.metadata),args.out,args.data.read_text(encoding='utf-8'))))
        elif args.command=='serve':
            if not 1<=args.port<=65535:raise ValidationError('Port must be between 1 and 65535')
            from .server import serve
            serve(args.port)
        elif args.command=='demo':
            if args.out.exists():raise ValidationError('Demo output directory must not already exist')
            args.out.mkdir(parents=True);results=[]
            for name in catalog():
                save(name,{},args.out/name);results.append(load_json(args.out/name/'result.json'))
            (args.out/'index.html').write_text(report_html(results),encoding='utf-8')
            write_json(args.out/'summary.json',[{'experiment':r['experiment'],'metrics':r['metrics']} for r in results])
            print(canonical({'experiments':len(results),'path':str(args.out)}))
        elif args.command=='bridge':
            from .bridge import import_nephrogenesis
            if args.out.exists():raise ValidationError('Bridge output must be a new path')
            write_json(args.out,import_nephrogenesis(args.input));print(canonical({'saved':str(args.out)}))
        return 0
    except (ValidationError,OSError,UnicodeError) as exc:
        print(f'Error: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
