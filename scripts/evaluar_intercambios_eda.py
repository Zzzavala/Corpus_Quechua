"""Audita un escenario léxico de seis intercambios, sin modificar el maestro.

El propósito es mostrar sus ganancias y pérdidas antes de tomar una decisión humana.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys
sys.dont_write_bytecode=True
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from heuristicas import tiempo_es

BASE=ROOT/'04_reportes/eda_postseleccion'
OUT=BASE/'evaluacion_intercambios'
PARES=[
    ('B04','GEN-0850','GEN-0264'),
    ('B04','GEN-0930','GEN-0499'),
    ('B04','GEN-0783','GEN-0454'),
    ('B05','GEN-0794','GEN-0629'),
    ('B05','GEN-1081','GEN-0642'),
    ('B05','GEN-1094','GEN-0493'),
]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def toks(s):return set(re.findall(r"[a-záéíóúüñ]+",str(s).lower()))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    master=ROOT/'02_maestro/corpus_maestro.xlsx'
    eda=BASE/'EDA_POSTSELECCION.xlsx'
    proposal=BASE/'propuesta_candidatos/PROPUESTA_CANDIDATOS.xlsx'
    before={str(p):sha(p) for p in [master,eda,proposal,BASE/'REVISION_HUMANA.xlsx']}
    h={k:v.fillna('') for k,v in pd.read_excel(master,sheet_name=None,dtype=str).items()}
    corpus=h['Corpus'].merge(h['Origen'],on='ID',validate='one_to_one')
    selected=corpus[corpus.Bloque.ne('')].copy()
    ref=pd.read_excel(eda,sheet_name='Referencias_todas',dtype=str).fillna('')
    target=set().union(*(toks(x) for x in ref.Español_ref))
    index=corpus.set_index('ID')
    details=[]
    simulated=selected.copy()
    for block,remove,add in PARES:
        old=index.loc[remove];new=index.loc[add]
        assert old.Bloque==block and not new.Bloque
        assert old.Dominio==new.Dominio=='General'
        assert old.Control=='No' and old.Test_sugerido=='No' and not old.Responde_a
        assert not new.Responde_a
        assert old.Fuente=='Redactado por Claude (F5)' and not old.Quechua_borrador
        assert new.Quechua_borrador
        slot=selected[selected.ID.eq(remove)].iloc[0]
        details.append({'Bloque':block,'Sale_ID':remove,'Sale_ES':old.Español,'Sale_tiempo':tiempo_es(old.Español),
            'Sale_fuente':old.Fuente,'Sale_QU_borrador':old.Quechua_borrador,
            'Entra_ID':add,'Entra_ES':new.Español,'Entra_tiempo':tiempo_es(new.Español),
            'Entra_fuente':new.Fuente,'Entra_QU_borrador':new.Quechua_borrador,
            'Bloque_destino':block,'Sublote_destino':slot.Sublote,'N_destino':slot.N_bloque,
            'Decision':'NO APLICAR TODAVÍA','Motivo':'Gana formas escritas, pero cambia el contraste temporal y ambos quechuas siguen sin validación humana.'})
        simulated=simulated[~simulated.ID.eq(remove)]
        row=new.copy()
        row['ID']=add
        for field,value in [('Bloque',block),('Sublote',slot.Sublote),('N_bloque',slot.N_bloque),
                            ('Prioridad',slot.Prioridad),('Control','No'),('Test_sugerido','No')]:
            row[field]=value
        simulated=pd.concat([simulated,pd.DataFrame([row])],ignore_index=True)
    swaps=pd.DataFrame(details)
    # Comprobaciones estructurales del escenario.
    assert len(simulated)==1000 and simulated.ID.is_unique
    counts=simulated.groupby(['Bloque','Dominio']).size().unstack(fill_value=0)
    assert all(counts['General'].eq(140)) and all(counts.drop(columns='General').sum(axis=1).eq(60))
    assert set(simulated.Responde_a)-{''} <= set(simulated.ID)
    for answer in simulated[simulated.Responde_a.ne('')].itertuples():
        question=simulated.set_index('ID').loc[answer.Responde_a]
        assert question.Bloque==answer.Bloque and question.Sublote==answer.Sublote
    assert selected.Control.value_counts().to_dict()==simulated.Control.value_counts().to_dict()
    assert selected.Test_sugerido.value_counts().to_dict()==simulated.Test_sugerido.value_counts().to_dict()
    def summary(df,label):
        voc=set().union(*(toks(x) for x in df.Español))
        return {'Escenario':label,'Filas':len(df),'Formas_objetivo_cubiertas':len(voc&target),
            'Con_borrador_QU':int(df.Quechua_borrador.ne('').sum()),
            'Redactado_Claude':int(df.Fuente.eq('Redactado por Claude (F5)').sum()),
            'Grupo2':int(df.Fuente.eq('Grupo 2 – Corpus Chanka').sum())}
    metrics=pd.DataFrame([summary(selected,'Actual'),summary(simulated,'Intercambio léxico hipotético')])
    # Tiempo sólo para la parte general, donde ocurren los cambios.
    times=[]
    for label,df in [('Actual',selected),('Intercambio léxico hipotético',simulated)]:
        counter=Counter(tiempo_es(x) for x in df[df.Dominio.eq('General')].Español)
        for k,v in counter.items():times.append({'Escenario':label,'Tiempo_ES_heuristico':k,'Filas':v})
    time_df=pd.DataFrame(times)
    time_pivot=time_df.pivot(index='Tiempo_ES_heuristico',columns='Escenario',values='Filas').fillna(0).astype(int).reset_index()
    time_pivot['Diferencia']=time_pivot['Intercambio léxico hipotético']-time_pivot['Actual']
    # Las alternativas generales no provenientes de ejercicios cubren otros tiempos, pero aún no tienen quechua.
    candidates=pd.read_excel(proposal,sheet_name='Candidatos_disponibles',dtype=str).fillna('')
    translation_first=candidates[(candidates.Dominio.eq('General'))&(~candidates.Tipo_borrador.eq('ejercicio generado'))].copy()
    translation_first['Tiempo_ES_heuristico']=translation_first.Español.map(tiempo_es)
    def alerta_tiempo(texto,etiqueta):
        s=texto.lower()
        if re.search(r'\b(?:iré|irás|irá|iremos|irán)\b',s) and etiqueta!='futuro':
            return 'La forma futura de «ir» no fue reconocida por la heurística.'
        if re.search(r'\b(?:ayer|anoche|la semana pasada|el año pasado)\b',s) and etiqueta=='futuro':
            return 'Hay un marcador pasado, pero la heurística asignó futuro.'
        return ''
    translation_first['Alerta_tiempo']=translation_first.apply(lambda r:alerta_tiempo(r.Español,r.Tiempo_ES_heuristico),axis=1)
    translation_first['Ruta_recomendada']='Revisar español → aprobar intención → enviar a traducción; no intercambiar todavía.'
    tiempos_audit=selected[['ID','Bloque','Dominio','Español']].copy()
    tiempos_audit['Tiempo_ES_heuristico']=tiempos_audit.Español.map(tiempo_es)
    tiempos_audit['Alerta_tiempo']=tiempos_audit.apply(lambda r:alerta_tiempo(r.Español,r.Tiempo_ES_heuristico),axis=1)
    tiempos_audit=tiempos_audit[tiempos_audit.Alerta_tiempo.ne('')]
    # Triage de las 30 filas basado en observaciones editoriales, sin evaluación lingüística humana.
    triage=pd.read_excel(proposal,sheet_name='Revision_editorial_IA',dtype=str).fillna('')
    def level(r):
        if 'Posponer' in r.Orientacion_editorial_IA:return 'C — resolver contexto antes de considerar'
        if 'Candidato' in r.Orientacion_editorial_IA:return 'A — revisar primero'
        return 'B — revisar sólo si aporta un contraste buscado'
    triage['Prioridad_revision_IA']=triage.apply(level,axis=1)
    with pd.ExcelWriter(OUT/'EVALUACION_INTERCAMBIOS.xlsx',engine='openpyxl') as w:
        for name,df in [('Dictamen_6',swaps),('Metricas',metrics),('Tiempos_general',time_pivot),
                        ('Alternativas_traducir',translation_first),('Alertas_tiempo',tiempos_audit),('Triaje_30',triage),
                        ('Conteos_simulados',counts.reset_index())]:
            df.to_excel(w,sheet_name=name,index=False)
            ws=w.sheets[name];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
            for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=min(58,max(14,len(str(col[0].value or ''))+2))
            for row in ws.iter_rows():
                for cell in row:
                    if cell.data_type=='f':cell.data_type='s'
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    m=metrics.set_index('Escenario')
    gains=[m.loc['Intercambio léxico hipotético',col]-m.loc['Actual',col]
           for col in ['Formas_objetivo_cubiertas','Con_borrador_QU']]
    axes[0].bar(['Formas objetivo\ncubiertas','Filas con\nborrador QU'],gains,color='#e6a24a')
    axes[0].set_ylabel('Ganancia neta en filas/formas')
    axes[0].set_title('Beneficio pequeño del escenario')
    for i,v in enumerate(gains):axes[0].text(i,v+.15,f'+{v}',ha='center',fontweight='bold')
    changed=time_pivot[time_pivot.Diferencia.ne(0)]
    axes[1].bar(changed.Tiempo_ES_heuristico,changed.Diferencia,color=['#ba4f4f' if x<0 else '#5f9e6e' for x in changed.Diferencia])
    axes[1].axhline(0,color='black',lw=.8);axes[1].set_ylabel('Cambio en frases')
    axes[1].set_title('Costo: cambia la distribución temporal general')
    fig.tight_layout();fig.savefig(OUT/'ganancia_vs_variedad.png',dpi=150,bbox_inches='tight');plt.close(fig)
    result={'escenario_aplicado_al_maestro':False,'intercambios_evaluados':len(swaps),
        'recomendacion':'No aplicar todavía: revisar español/quechua y conservar variedad temporal.',
        'filas_simuladas':len(simulated),'estructura_200_140_60':'OK','pares_dialogo':'OK',
        'control_y_test':'sin cambios','integridad_entradas':'pendiente'}
    assert all(sha(Path(p))==h for p,h in before.items())
    result['integridad_entradas']='OK'
    (OUT/'ejecucion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    report=['# Evaluación de posibles intercambios','',
        '**Dictamen: no aplicar todavía los seis intercambios léxicos simulados.** La estructura quedaría correcta, '
        'pero la ganancia de vocabulario se obtiene reemplazando frases de pasado, futuro, condicional u orden por ejercicios principalmente en presente.','',
        'La simulación mantiene 1 000 frases, cinco bloques de 200, 140 generales y 60 médicas por bloque, pares de diálogo, controles y test sugeridos. '
        'Eso demuestra consistencia estructural, no conveniencia lingüística. Ningún cambio fue escrito al maestro.','',
        '## Decisión recomendada','',
        '1. Revisar primero el triaje A del Excel con el traductor y, en medicina, con el revisor de dominio.',
        '2. Revisar las seis alternativas de español no procedentes de ejercicios. Cubren otros tiempos, pero carecen de quechua.',
        '3. Recalcular intercambios después de las decisiones humanas, exigiendo conservar dominio, función comunicativa, tiempo/modo, pares y diversidad de fuentes.',
        '4. Tratar las distintas flexiones de un mismo verbo como una familia para cobertura conceptual; conservarlas separadas sólo cuando el contraste gramatical sea intencional.','',
        '## Limitación adicional del EDA','',
        'La clasificación de tiempo verbal es heurística. Por ejemplo, «Esta tarde iré a recoger a los niños» fue etiquetada como pasado porque la expresión regular actual no reconoce bien el futuro del verbo «ir». '
        'La hoja `Alertas_tiempo` registra los casos detectados por esta auditoría; no es una lista exhaustiva. Las cifras temporales sirven para comparar y necesitan revisión antes de decidir.','',
        '## Archivos','',
        '- `EVALUACION_INTERCAMBIOS.xlsx`: seis intercambios, métricas, tiempos, alternativas y triaje.',
        '- `ganancia_vs_variedad.png`: beneficio léxico frente al cambio de distribución temporal.',
        '- `ejecucion.json`: comprobaciones e integridad.','',
        'Las categorías A/B/C son prioridades editoriales del asistente; no constituyen validación de quechua ni aprobación clínica.']
    (OUT/'DICTAMEN.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(swaps[['Bloque','Sale_ID','Sale_tiempo','Entra_ID','Entra_tiempo','Decision']].to_string(index=False))
    print('\n',metrics.to_string(index=False));print('\n',time_pivot.to_string(index=False));print('\n',json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
