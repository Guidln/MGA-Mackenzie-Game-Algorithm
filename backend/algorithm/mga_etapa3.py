"""MGA - Etapa 3: reavaliação do baseline, ablação do pipeline ajustado, sensibilidade e figuras.
Execução: python mga_etapa3.py  (requer pandas, numpy, scikit-learn, matplotlib, openpyxl)"""
import itertools, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from mga_pipeline import *
RED,GOLD,DARK='#8B1A14','#D4A017','#262626'
df=load(); K=5; n=len(df)

def baseline_etapa2(d):
    """Pipeline da Etapa 2: 42 atributos (z-score + imputação pela mediana + OHE/multi-hot), sem pesos."""
    num=['ano','quantidade_premios','vendas_milhoes','jogadores_concluiram_hltb','nota_publico_metacritic','nota_critica_metacritic']
    nn=d[num].fillna(d[num].median()); nn=pd.DataFrame(StandardScaler().fit_transform(nn),columns=num)
    return pd.concat([nn,pd.get_dummies(d.genero,prefix='genero').astype(int),
        pd.get_dummies(d.pais_maior_vendas,prefix='pais').astype(int),
        d.plataforma.str.get_dummies(sep=' / ').add_prefix('plat_')],axis=1)

macro=[set(GENRE_MAP[g]) for g in df.genero]
plat=[set(c.split('_',1)[1] for c in multi_hot(pd.Series([p]),PLAT_MAP,'p',' / ').columns) for p in df.plataforma]
def topk(S): return [[j for j in np.argsort(-S[i],kind='stable') if j!=i][:K] for i in range(n)]
def gini(x):
    x=np.sort(np.array(x,float));c=np.cumsum(x);return (n+1-2*c.sum()/c[-1])/n
def metrics(S):
    T=topk(S); cnt=np.bincount(sum(T,[]),minlength=n)
    return dict(
      GC5=np.mean([len(macro[i]&macro[j])>0 for i in range(n) for j in T[i]]),
      PC5=np.mean([len(plat[i]&plat[j])>0 for i in range(n) for j in T[i]]),
      cobertura=(cnt>0).mean(), max_recs=int(cnt.max()), gini=gini(cnt),
      score_medio=np.mean([S[i,j] for i in range(n) for j in T[i]]),
      dif_ano=np.mean([abs(df.ano[i]-df.ano[j]) for i in range(n) for j in T[i]]),
      div_intralista=np.mean([1-np.mean([S[a,b] for a,b in itertools.combinations(T[i],2)]) for i in range(n)])),T
def jacc(A,B): return float(np.mean([len(set(a)&set(b))/len(set(a)|set(b)) for a,b in zip(A,B)]))
def shared_ok(X,i,j,a):
    if a.startswith(('genero_','pais_','plat_')): return X.iloc[i][a]>0 and X.iloc[j][a]>0
    return True
def expl_baseline(X,i,j,top=3): return list((X.iloc[i]-X.iloc[j]).abs().sort_values().index[:top])

R={}
Xb=baseline_etapa2(df); Sb=cosine_similarity(Xb.values); mb,Tb=metrics(Sb); mb['n_attr']=Xb.shape[1]; mb['J_vs_base']=1.0; R['B0 Etapa 2 (baseline)']=mb
W1=dict(genero=1,plataforma=1,numerico=1,pais=1)
def run(name,**kw):
    X,_=build(df,**kw); S=cosine_similarity(X.values); m,T=metrics(S); m['n_attr']=X.shape[1]; m['J_vs_base']=jacc(Tb,T); R[name]=m; return X,S,T
run('E1 Equalização dos blocos',genre='raw',platform='raw',logs=False,missing='mediana',weights=W1)
run('E2 + Taxonomia de gênero',genre='macro',platform='raw',logs=False,missing='mediana',weights=W1)
run('E3 + Famílias de plataforma',genre='macro',platform='familia',logs=False,missing='mediana',weights=W1)
run('E4 + log1p (vendas, HLTB)',genre='macro',platform='familia',logs=True,missing='mediana',weights=W1)
run('E5 + Indicadores de ausência',genre='macro',platform='familia',logs=True,missing='mediana+indicador',weights=W1)
Xf,Sf,Tf=run('F Pesos por bloco (modelo final)')
run('V1 Final sem HLTB',missing='remover_hltb')
run('V2 Final sem ano',use_ano=False)
run('V3 Final com diretor',use_diretor=True)
abl=pd.DataFrame(R).T; abl.to_csv('ablacao_etapa3.csv'); print(abl.round(3).to_string())

# sensibilidade de pesos
rows=[]
for g,p,nu,pa in itertools.product([1,2,3],[0.25,0.5,1],[0.5,1,1.5],[0.25,0.5]):
    X,_=build(df,weights=dict(genero=g,plataforma=p,numerico=nu,pais=pa)); S=cosine_similarity(X.values); m,T=metrics(S)
    rows.append(dict(w_genero=g,w_plat=p,w_num=nu,w_pais=pa,J_vs_final=jacc(Tf,T),GC5=m['GC5'],max_recs=m['max_recs'],cobertura=m['cobertura']))
G=pd.DataFrame(rows); G.to_csv('sensibilidade_pesos.csv',index=False)
# robustez: ruído, métrica alternativa
rng=np.random.default_rng(42); js=[jacc(Tf,topk(cosine_similarity((Xf+rng.normal(0,0.05,Xf.shape)).values))) for _ in range(50)]
Se=1/(1+np.linalg.norm(Xf.values[:,None]-Xf.values[None],axis=2)); Te=topk(Se)
# validade das explicações
def valid(Xm,T,fn):
    ok=tot=0
    for i in range(n):
        for j in T[i]:
            for a in fn(Xm,i,j): tot+=1; ok+=shared_ok(Xm,i,j,a)
    return ok/tot
ev_b=valid(Xb,Tb,expl_baseline); ev_f=valid(Xf,Tf,lambda X,i,j: explain(X,df,i,j)) if True else 0
# consistência técnica do modelo final
cons=dict(auto_excluido=all(i not in Tf[i] for i in range(n)),
  intervalo=bool(Sf.min()>=-1-1e-9 and Sf.max()<=1+1e-9), smin=float(Sf.min()),
  smax_fora_diag=float((Sf-np.eye(n)*9).max()),
  reproduzivel=Tf==topk(cosine_similarity(build(df)[0].values)))
ext=dict(J_ruido_media=float(np.mean(js)),J_ruido_dp=float(np.std(js)),J_euclid=jacc(Tf,Te),
  sens_J_media=float(G.J_vs_final.mean()),sens_J_min=float(G.J_vs_final.min()),sens_GC5_min=float(G.GC5.min()),sens_GC5_max=float(G.GC5.max()),
  sens_n=len(G),ev_base=ev_b,ev_final=ev_f,n_expl=n*K*3,cons=cons,matriz=list(Xf.shape),
  hubs_base=[(df.jogo[i],int(c)) for i,c in sorted(enumerate(np.bincount(sum(Tb,[]),minlength=n)),key=lambda t:-t[1])[:3]],
  hubs_final=[(df.jogo[i],int(c)) for i,c in sorted(enumerate(np.bincount(sum(Tf,[]),minlength=n)),key=lambda t:-t[1])[:3]])
print(json.dumps(ext,indent=1,default=str,ensure_ascii=False))

# consultas de teste
QS=['Elden Ring','The Last of Us Part II','Hades']; Q={}
for q in QS:
    i=df.index[df.jogo==q][0]
    Q[q]=dict(base=[(df.jogo[j],float(Sb[i,j])) for j in Tb[i]],
      final=[dict(jogo=df.jogo[j],score=float(Sf[i,j]),genero=df.genero[j],plat=df.plataforma[j],ano=int(df.ano[j]),expl=explain(Xf,df,i,j)) for j in Tf[i]])
json.dump(dict(abl=abl.to_dict('index'),ext=ext,Q=Q),open('resultados_etapa3.json','w'),default=str,ensure_ascii=False,indent=1)

# ---- figuras
plt.rcParams.update({'font.size':9})
fig,ax=plt.subplots(1,3,figsize=(11,3.4))
for a,q in zip(ax,QS):
    r=Q[q]['final'][::-1]; a.barh([x['jogo'][:24] for x in r],[x['score'] for x in r],color=RED)
    for y,x in enumerate(r): a.text(x['score']+.01,y,f"{x['score']:.3f}",va='center',fontsize=8)
    a.set_title(f'Ref.: {q}',fontsize=9,fontweight='bold'); a.set_xlim(0,1.1); a.set_xlabel('Similaridade de cosseno')
plt.tight_layout(); plt.savefig('fig_top5_final.png',dpi=200); plt.close()

names=['B0','E1','E2','E3','E4','E5','F']; lab=['Baseline\n(Etapa 2)','E1\nBlocos','E2\nGênero','E3\nPlataf.','E4\nlog1p','E5\nAusência','F\nPesos']
vals=[abl.iloc[k]['GC5'] for k in range(7)]
fig,ax=plt.subplots(figsize=(7,3.3)); b=ax.bar(lab,vals,color=[DARK]+[GOLD]*5+[RED])
for r_,v in zip(b,vals): ax.text(r_.get_x()+r_.get_width()/2,v+.01,f'{v:.3f}',ha='center',fontsize=8)
ax.set_ylabel('Coerência de gênero@5'); ax.set_ylim(0,.62); plt.tight_layout(); plt.savefig('fig_ablacao.png',dpi=200); plt.close()

fig,ax=plt.subplots(figsize=(6.2,3.2)); ax.hist(G.J_vs_final,bins=12,color=RED,edgecolor='white')
ax.axvline(G.J_vs_final.mean(),color=GOLD,ls='--',label=f'Média = {G.J_vs_final.mean():.2f}'); ax.set_xlabel('Jaccard@5 em relação ao modelo final'); ax.set_ylabel('Configurações de pesos'); ax.legend(); plt.tight_layout(); plt.savefig('fig_sensibilidade.png',dpi=200); plt.close()

# fluxograma da metodologia
fig,ax=plt.subplots(figsize=(7.4,8.4)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(3.2,19.6)
steps=[('1. Base de dados','Base_Jogos (66 jogos × 14 colunas, 2014–2024)'),
('2. Análise exploratória e qualidade','tipos, ausentes, duplicidades, cardinalidade, escalas'),
('3. Tratamento','unificação "EUA"; N/D → vazio; plataforma_mais_zerada_hltb e fontes removidas do vetor'),
('4. Engenharia de atributos','taxonomia de gênero (multi-hot) • famílias de plataforma (multi-hot) • país (one-hot)\nlog1p + z-score nas numéricas • imputação pela mediana + indicador de ausência'),
('5. Ponderação por bloco','cada bloco ÷ √(nº de colunas) × peso a priori (gênero 2; numérico 1; plataforma 0,5; país 0,5)'),
('6. Representação vetorial','matriz 66 × 34 (um vetor por jogo)'),
('7. Similaridade de cosseno','matriz 66 × 66 • remoção do item consultado • ranking Top-N'),
('8. Explicabilidade','atributos compartilhados com maior contribuição ao cosseno'),
('9. Avaliação','consistência técnica • coerência@5 • cobertura/concentração • estabilidade • análise qualitativa')]
h=1.65;y=19.2
for k,(t,s) in enumerate(steps):
    ax.add_patch(plt.Rectangle((0.6,y-h+0.25),8.8,h-0.55,fc='#F5E9E8' if k%2==0 else '#FBF3DC',ec=RED if k%2==0 else GOLD,lw=1.5))
    ax.text(5,y-0.68,t,ha='center',va='center',fontweight='bold',fontsize=10.5); ax.text(5,y-1.12,s,ha='center',va='center',fontsize=8.2)
    if k<len(steps)-1: ax.annotate('',xy=(5,y-h+0.05),xytext=(5,y-h+0.27),arrowprops=dict(arrowstyle='-|>',color=DARK))
    y-=h+0.1
plt.tight_layout(); plt.savefig('fig_fluxograma.png',dpi=200); plt.close()
