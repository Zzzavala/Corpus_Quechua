"""Ejecuta secuencialmente las celdas Python del notebook, conservando sus salidas.

No requiere nbclient. Este ejecutor usa Python (no un kernel Jupyter) y solo admite
las celdas Python ordinarias de este notebook, sin magics ni comandos de shell.
"""
from pathlib import Path
import base64
import contextlib
import io
import json
import os
import sys
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import IPython.display

ROOT=Path(__file__).resolve().parent.parent
PATH=ROOT/'EDA_Postseleccion_Corpus_Chanka.ipynb'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    os.chdir(ROOT)
    nb=json.loads(PATH.read_text(encoding='utf-8'))
    env={'__name__':'__main__'}
    count=0
    old_display,old_show=IPython.display.display,plt.show
    try:
        for cell in nb['cells']:
            if cell['cell_type']!='code':continue
            count+=1;cell['execution_count']=count;cell['outputs']=[]
            stream=io.StringIO()
            def flush():
                s=stream.getvalue()
                if s:cell['outputs'].append({'output_type':'stream','name':'stdout','text':s})
                stream.seek(0);stream.truncate(0)
            def display(*objects,**kwargs):
                flush()
                for obj in objects:
                    data={'text/plain':repr(obj)}
                    if hasattr(obj,'_repr_html_'):
                        html=obj._repr_html_()
                        if html:data['text/html']=html
                    cell['outputs'].append({'output_type':'display_data','metadata':{},'data':data})
            def show(*args,**kwargs):
                flush()
                for number in plt.get_fignums():
                    fig=plt.figure(number);buf=io.BytesIO();fig.savefig(buf,format='png',dpi=110,bbox_inches='tight')
                    cell['outputs'].append({'output_type':'display_data','metadata':{},'data':{
                        'image/png':base64.b64encode(buf.getvalue()).decode('ascii'),'text/plain':'Figura del EDA'}})
                    plt.close(fig)
            IPython.display.display=display;plt.show=show
            print(f'Ejecutando celda {count}...',flush=True)
            try:
                with contextlib.redirect_stdout(stream):
                    exec(compile(cell['source'],f'{PATH.name}:celda{count}','exec'),env)
                flush()
            except Exception as e:
                flush();cell['outputs'].append({'output_type':'error','ename':type(e).__name__,'evalue':str(e),
                                                'traceback':traceback.format_exc().splitlines()})
                PATH.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
                raise
        nb['metadata']['ejecucion']={'modo':'Python secuencial; no kernel Jupyter','celdas_ejecutadas':count}
        PATH.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
        print(f'OK: {count} celdas ejecutadas. {PATH}')
    finally:
        IPython.display.display=old_display;plt.show=old_show

if __name__=='__main__':main()
