"""Propuesta exploratoria de candidatos adicionales; no cambia la selección real.
La cuota 21 general/9 médico corresponde a una lista de revisión de 30 ejemplos.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import re
import unicodedata
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent.parent
EDA=ROOT/'04_reportes/eda_postseleccion'
OUT=EDA/'propuesta_candidatos'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(s): return re.findall(r"[a-záéíóúüñ]+(?:['’][a-záéíóúüñ]+)?|[0-9]+",unicodedata.normalize('NFC',str(s)).lower())
def lexicon(series): return set(t for s in series for t in tokens(s))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    master=ROOT/'02_maestro/corpus_maestro.xlsx'
    report=EDA/'EDA_POSTSELECCION.xlsx'
    before={str(p):sha(p) for p in [master,report,EDA/'REVISION_HUMANA.xlsx']}
    execution=json.loads((EDA/'ejecucion.json').read_text(encoding='utf-8'))
    assert execution['maestro_sha256']==sha(master),'Reejecutar EDA: cambió el maestro.'
    h={k:v.fillna('') for k,v in pd.read_excel(master,sheet_name=None,dtype=str).items()}
    c=h['Corpus'].merge(h['Origen'],on='ID',validate='one_to_one')
    refs=pd.read_excel(report,sheet_name='Referencias_todas',dtype=str).fillna('')
    selected=c[c.Bloque.ne('')].copy()
    covered=lexicon(selected['Español'])
    target=lexicon(refs['Español_ref'])
    missing=(target & lexicon(c['Español']))-covered
    vs={};dfreq={}
    for name,g in refs.groupby('Archivo'):
        g=g.drop_duplicates('Clave')
        vs[name]=lexicon(g['Español_ref'])
        dfreq[name]=Counter(t for s in g['Español_ref'] for t in set(tokens(s)))
    # Cada archivo aporta hasta el mismo peso: el tamaño de flashcards2 no domina.
    maxima={f:max((math.log1p(n) for n in d.values()),default=1) for f,d in dfreq.items()}
    weight={t:sum(math.log1p(d[t])/maxima[f] for f,d in dfreq.items()) for t in missing}
    # Sólo/solo no debe incentivar una frase adicional exclusivamente por esa grafía.
    orthographic={t for t in missing if t=='sólo' and 'solo' in covered}
    priority_missing=missing-orthographic
    qa=h['QA'].groupby('ID').agg(Numero_alertas=('Tipo','size'),
        Alertas=('Detalle',lambda x:' | '.join(x)),
        N_alta=('Severidad',lambda x:int(x.eq('ALTA').sum())))
    pool=c[c.Bloque.eq('')].merge(qa,on='ID',how='left').fillna({'Numero_alertas':0,'Alertas':'','N_alta':0})
    rows=[]
    for r in pool.to_dict('records'):
        words=set(tokens(r['Español']));gaps=words & priority_missing
        if not (words & missing): continue
        r['Formas_objetivo_nuevas']=' | '.join(sorted(words & missing))
        r['Formas_priorizables']=' | '.join(sorted(gaps))
        r['N_formas_priorizables']=len(gaps)
        r['N_palabras_ES']=len(tokens(r['Español']))
        r['Ganancia_lexica_base']=sum(weight[t] for t in gaps)
        r['Contexto_posible']=bool(re.search(r'(?i)^(?:y |entonces |eso |esa |ese |lo |acaso |esta persona)',r['Español']))
        r['Varias_preguntas']=r['Español'].count('?')>1
        r['En_rango_longitud']=2<=r['N_palabras_ES']<=20
        r['Revision_clinica_necesaria']=r['Dominio']=='Médico'
        # Penalty is workflow prioritization, never a confidence/quality estimate.
        r['Factor_revision']=1/(1+0.5*min(int(r['N_alta']),3)+0.25*int(r['Contexto_posible'])+0.25*int(r['Varias_preguntas']))
        rows.append(r)
    candidates=pd.DataFrame(rows).sort_values(['Ganancia_lexica_base','ID'],ascending=[False,True])
    choices=[];seen=set();chosen=set();quota={'General':21,'Médico':9}
    for step in range(sum(quota.values())):
        scored=[]
        for r in candidates.to_dict('records'):
            if r['ID'] in chosen or not quota.get(r['Dominio'],0) or not r['En_rango_longitud']:continue
            new=(set(tokens(r['Español'])) & priority_missing)-seen
            if not new:continue
            score=sum(weight[t] for t in new)*r['Factor_revision']
            scored.append((score,r['ID'],r,new))
        if not scored:break
        _,_,r,new=sorted(scored,key=lambda x:(-x[0],x[1]))[0]
        r=dict(r,Orden_revision=step+1,Formas_adicionales_en_propuesta=' | '.join(sorted(new)),
               N_adicionales_en_propuesta=len(new),Puntaje_revision=sum(weight[t] for t in new)*r['Factor_revision'],
               Estado_propuesta='Candidato; requiere revisión, no aprobado')
        choices.append(r);seen|=new;chosen.add(r['ID']);quota[r['Dominio']]-=1
    proposal=pd.DataFrame(choices)
    # Observaciones editoriales de esta revisión: no aprobación de un hablante.
    notes={
        'CLI-0242':('Si sigue el estreñimiento', 'Revisar español y contexto',
            'Hay discordancia de tratamiento entre «puede regresar» y «verte». Precisar quién vuelve y a quién se atiende; revisar la condición clínica antes de reformular.'),
        'CLI-0205':('Debe permanecer en casa por 14 días', 'Posponer hasta revisión del contexto',
            'Instrucción sanitaria con plazo concreto y redacción defectuosa («que tuvo en contacto»). Identificar documento, fecha y situación. No incorporarla solo para cubrir contacto/último.'),
        'CLI-0729':('¿Se siente seguro o segura', 'Candidato para revisión contextual',
            'Pregunta comprensible sobre seguridad en casa. Confirmar intención y trato adecuado en una entrevista sensible; validar ambos lados.'),
        'CLI-0306':('¿Es casado, soltero', 'Revisar formulación e inclusividad',
            'Revisar concordancia y si se necesita lista cerrada de estados civiles. La enumeración puede requerir contexto y otras opciones.'),
        'CLI-0680':('¿Quiere sentarse?', 'Candidato para revisión lingüística',
            'Pregunta breve y autónoma. Validar el trato y la traducción; no confundir el aporte de quiere con validación del quechua.'),
        'CLI-0960':('¿Conoces el condón femenino?', 'Candidato para revisión especializada',
            'Confirmar terminología, comprensión y contexto de educación sexual con revisor competente; mantener el tratamiento consistente.'),
        'CLI-0567':('¿Desde cuándo ha cambiado de carácter', 'Posponer hasta precisar referente',
            'No queda claro de quién se habla; combina inicio temporal y alternativas de comportamiento. Aclarar referente e intención y revisar términos antes de traducir.'),
        'CLI-0911':('Esto tenemos que coserlo.', 'Revisar autonomía',
            '«Esto» depende de señalar una lesión u objeto. Guardar contexto de la intervención o redactar una versión autónoma y retraducirla.'),
        'CLI-0152':('No fumar y evitar', 'Candidato para revisión especializada',
            'Forma de indicación impersonal. Confirmar registro comunicativo y contexto de uso con el revisor clínico y lingüístico.'),
        'GEN-0692':('Las niñas no ven el sol.', 'Revisar aporte léxico',
            'La forma «ven» es ambigua en la referencia: puede ser ver o el imperativo de venir. Coincidir en la escritura no implica cubrir el mismo significado.'),
        'GEN-0520':('Las niñas odian la oscuridad.', 'Revisar naturalidad y redundancia',
            'Aclarar si se desea expresar odio o miedo; son significados distintos. No sustituirlos automáticamente.'),
        'GEN-0527':('Yo no odio la tarea.', 'Revisar intención y redundancia',
            'La negación de odio no afirma agrado. Conservar solo si ese contraste es un objetivo útil.'),
        'GEN-0475':('Yo no leo una revista.', 'Revisar alcance de la negación',
            'Decidir si se niega una revista concreta o la actividad en general. No cambiar a plural sin revisar el significado y la traducción.'),
        'GEN-0633':('Ellas no recuerdan una canción.', 'Revisar alcance y contexto',
            'Puede referirse a una canción concreta o a ninguna. Precisar intención y contrastar con otros ejemplos de recordar.'),
        'GEN-1115':('Me gustaría aprender a manejar.', 'Candidato para traducción y revisión',
            'Precisar si manejar se refiere a conducir un vehículo; conservar significado local. Falta quechua: no grabar como par aprobado.'),
    }
    editorial=[]
    for r in proposal.to_dict('records'):
        item=notes.get(r['ID'])
        if item and r['Español'].startswith(item[0]):
            _,action,note=item
        else:
            action='Revisar diversidad y equivalencia'
            note='Ejemplo de ejercicio: contrastar persona, negación, verbo y situación con los ejemplos ya seleccionados. La nueva forma escrita puede aportar poca diversidad comunicativa.'
        editorial.append({'Orden_revision':r['Orden_revision'],'ID':r['ID'],'Dominio':r['Dominio'],
            'Español':r['Español'],'Quechua_borrador':r['Quechua_borrador'],
            'Formas_adicionales':r['Formas_adicionales_en_propuesta'],
            'Orientacion_editorial_IA':action,'Observacion_editorial_IA':note,
            'Estado_validacion':'Pendiente de revisión humana','Decision_humana':'','Revisor':'','Fecha':''})
    editorial=pd.DataFrame(editorial)
    after=covered | lexicon(proposal['Español'])
    impacts=[]
    for name,v in vs.items():
        impacts.append({'Referencia':name,'Formas_objetivo':len(v),'Cubiertas_actual':len(v&covered),
            'Cubiertas_si_se_anaden':len(v&after),'Formas_adicionales':len((v&after)-covered),
            'Cobertura_actual_pct':100*len(v&covered)/len(v),'Cobertura_hipotetica_pct':100*len(v&after)/len(v)})
    impact=pd.DataFrame(impacts)
    byword=[]
    for t in sorted(missing):
        available=candidates[candidates['Español'].map(lambda s:t in set(tokens(s)))]
        byword.append({'Forma':t,'Situacion':'variacion_solo_sólo_no_priorizada' if t in orthographic else 'brecha_literal',
            'En_flashcards_1':t in vs.get('flashcards.xlsx',set()),'En_flashcards_2':t in vs.get('flashcards2.xlsx',set()),
            'IDs_disponibles':' | '.join(available.ID),'En_propuesta':t in after,
            'Peso_lexico':weight[t]})
    # Exact preservation of both sides and uniqueness; no selected ID can enter proposal.
    original=c.set_index('ID')
    assert proposal.ID.is_unique and not (set(proposal.ID)&set(selected.ID))
    for field in ['Español','Quechua_borrador','Quechua_validado']:
        assert proposal[field].tolist()==original.loc[proposal.ID,field].tolist()
    assert proposal.Dominio.value_counts().to_dict()=={'General':21,'Médico':9}
    with pd.ExcelWriter(OUT/'PROPUESTA_CANDIDATOS.xlsx',engine='openpyxl') as w:
        for sheet,df in [('Revision_editorial_IA',editorial),('Propuesta_30',proposal),('Impacto_hipotetico',impact),('Brechas_285',pd.DataFrame(byword)),('Candidatos_disponibles',candidates)]:
            df.to_excel(w,sheet_name=sheet,index=False)
            ws=w.sheets[sheet];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width=min(55,max(14,len(str(col[0].value or ''))+2))
            for row in ws.iter_rows():
                for cell in row:
                    if cell.data_type=='f':cell.data_type='s'
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    xx=range(len(impact))
    axes[0].bar([x-.18 for x in xx],impact.Cobertura_actual_pct,width=.36,label='Actual',color='#4586a8')
    axes[0].bar([x+.18 for x in xx],impact.Cobertura_hipotetica_pct,width=.36,label='Si se añaden las 30',color='#e6a24a')
    axes[0].set_xticks(list(xx),impact.Referencia,rotation=15)
    axes[0].set_ylabel('Cobertura de formas escritas (%)');axes[0].set_title('Impacto léxico hipotético');axes[0].legend()
    sources=proposal.Fuente.value_counts()
    axes[1].barh(sources.index,sources.values,color='#5f9e6e')
    axes[1].set_xlabel('Candidatos');axes[1].set_title('Procedencia de la lista de revisión')
    for y,v in enumerate(sources.values):axes[1].text(v+.15,y,str(v),va='center')
    fig.tight_layout();fig.savefig(OUT/'impacto_y_procedencia.png',dpi=150,bbox_inches='tight');plt.close(fig)
    assert all(sha(Path(p))==h for p,h in before.items()),'Se alteró una entrada.'
    metadata={'entradas_sha256':before,'cuotas_revision':{'General':21,'Médico':9},
        'brechas_literales':len(missing),'candidatos_con_brechas':len(candidates),'propuestos':len(proposal),
        'formas_nuevas_priorizadas':len(seen),'seleccion_actual':len(selected),
        'tamano_hipotetico_si_se_anaden':len(selected)+len(proposal),
        'alcance':'Lista de revisión adicional. No sustituciones, ni validación, ni modificación del maestro.',
        'integridad_entradas':'OK'}
    (OUT/'ejecucion.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    ng=int(proposal.Tipo_borrador.eq('ejercicio generado').sum())
    negative=int(proposal['Español'].str.contains(r'(?i)\bno\b',regex=True).sum())
    text=['# Primera revisión de candidatos adicionales','',
        f'Se encontraron {len(candidates)} frases no seleccionadas que contienen alguna de las {len(missing)} formas objetivo disponibles. '
        'Se preparó una lista exploratoria de 30: 21 generales y 9 médicas. No se cambió ningún bloque.','',
        '## Qué revela la búsqueda','',
        f'- {ng} de las 30 proceden de ejercicios generados; {negative} incluyen la palabra «no». '
        'Estas cantidades se solapan y no deben sumarse.',
        '- La selección léxica recompensa formas como trabaja/trabajas/trabajamos, aunque sean de la misma familia. '
        'No se interpreta cada forma nueva como un concepto ni como un objetivo gramatical validado.',
        '- «Ven» puede tener sentidos diferentes. Coincidir por token no demuestra que se cubra el uso buscado.',
        '- Sólo/solo se mantiene en las cifras literales del EDA, pero no incentiva esta priorización cuando solo ya está cubierto.',
        '- Algunas frases médicas necesitan referente, contexto o revisión especializada. No se recomiendan para grabación por su puntaje.','',
        '## Cómo leer el Excel','',
        'Abrir primero Revision_editorial_IA. Cada uno de los 30 candidatos tiene una observación y un siguiente paso. '
        'Son observaciones del asistente, no evaluaciones de un hablante chanka. Las decisiones humanas están vacías.',
        'Propuesta_30 contiene la procedencia y los pares originales. Candidatos_disponibles permite buscar alternativas. '
        'Brechas_285 vincula cada forma con sus IDs disponibles.','',
        '## Impacto hipotético, no resultado de una nueva selección','']
    for r in impact.to_dict('records'):
        text.append(f'- {r["Referencia"]}: {r["Cobertura_actual_pct"]:.2f}% actual → {r["Cobertura_hipotetica_pct"]:.2f}% si se añadieran las 30 frases completas.')
    text += ['',f'Esta simulación tendría {len(selected)+len(proposal)} frases. No mantiene el límite de 1 000 ni calcula pérdidas por reemplazos. '
        'No ejecutar esas adiciones automáticamente: primero revisar y después evaluar intercambios dentro de las cuotas y pares de diálogo.','',
        '## Método reproducible','',
        'Peso de cada forma: suma, por archivo de referencia, de log(1+frecuencia por frase única) dividido por el máximo de ese archivo. '
        'Cada archivo aporta hasta el mismo peso; flashcards2 no domina solo por su tamaño. '
        'Se selecciona por ganancia de formas todavía no cubiertas, con factor 1/(1+0.5×min(alertas altas,3)+0.25×contexto posible+0.25×varias preguntas), '
        'longitud entre 2 y 20 tokens y cuota 21/9. Estos parámetros organizan una lista de revisión; no están calibrados como probabilidades de calidad.',
        'El puntaje usa alertas existentes: cero alertas no significa ausencia de errores. '
        'Ningún lado del par se modifica. Las huellas del maestro, EDA y revisión humana se verifican al terminar.','',
        '## Próximo paso','',
        'Revisar primero los candidatos breves y claros, resolver las observaciones contextuales y '
        'comparar las familias repetitivas con las frases ya seleccionadas. Si se cambia el español, revisar o rehacer su traducción. '
        'No buscar máxima cobertura a costa de naturalidad, variedad de situaciones o consistencia clínica.','',
        'Este Excel es una salida automática: guardar decisiones humanas en una copia antes de volver a ejecutar el script. '
        'La plantilla REVISION_HUMANA.xlsx anterior no se modificó.']
    (OUT/'REVISION_CANDIDATOS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(proposal[['Orden_revision','ID','Dominio','Español','Formas_adicionales_en_propuesta','N_alta']].to_string(index=False))
    print(impact.round(2).to_string(index=False))

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
