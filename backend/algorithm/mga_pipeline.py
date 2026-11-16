"""MGA - Mackenzie Game Algorithm | Pipeline de recomendação baseada em conteúdo (Etapa 3)."""
import os
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

# Caminho da base: variável de ambiente MGA_DATA_PATH ou backend/data/ (relativo a este arquivo).
PATH = os.environ.get('MGA_DATA_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'the_game_awards_2014_2024_ofc.xlsx')

# Taxonomia documentada (apenas separa rótulos compostos e unifica sinônimos presentes na base)
GENRE_MAP = {
 'Action':['Action'],'RPG':['RPG'],'FPS':['Shooter'],'Shooter':['Shooter'],'Battle Royale':['Shooter'],
 'Platform':['Platform'],'Indie':['Indie'],'Action RPG':['Action','RPG'],'Horror':['Horror'],
 'Survival Horror':['Horror','Survival'],'Roguelike':['Roguelike'],'Card':['Card'],'Racing':['Racing'],
 'Narrative':['Narrative'],'Stealth':['Stealth'],'Open World':['Open World'],'Fighting':['Fighting'],
 'Simulation':['Simulation'],'Coop':['Coop'],'Adventure':['Adventure'],'Action-Adventure':['Action','Adventure']}
PLAT_MAP = {'PC':['PC'],'PS':['PlayStation'],'PS3':['PlayStation'],'PS4':['PlayStation'],'PS5':['PlayStation'],
 'Xbox':['Xbox'],'Wii U':['Nintendo'],'Switch':['Nintendo'],'Mobile':['Mobile'],
 'Consoles':['PlayStation','Xbox'],'Multi':['PC','PlayStation','Xbox','Nintendo']}

def load(path=None): return pd.read_excel(path or PATH, sheet_name='Base_Jogos')

def multi_hot(series, mapping, prefix, sep=None):
    rows=[]
    for v in series:
        toks=[t.strip() for t in v.split(sep)] if sep else [v]
        s=set()
        for t in toks: s.update(mapping[t])
        rows.append(s)
    cols=sorted(set().union(*rows))
    return pd.DataFrame([[int(c in r) for c in cols] for r in rows],columns=[f'{prefix}_{c}' for c in cols])

def build(df, genre='macro', platform='familia', logs=True, missing='mediana+indicador',
          use_ano=True, use_diretor=False, weights=None):
    """Retorna a matriz de atributos X (n_jogos x n_atributos) e o mapa bloco->colunas."""
    w={'genero':2.0,'plataforma':0.5,'numerico':1.0,'pais':0.5}
    if weights: w.update(weights)
    d=df.copy()
    num=['quantidade_premios','vendas_milhoes','jogadores_concluiram_hltb','nota_publico_metacritic','nota_critica_metacritic']
    if use_ano: num=['ano']+num
    blocks={}
    N=d[num].copy()
    ind={}
    if missing=='remover_hltb': N=N.drop(columns='jogadores_concluiram_hltb')
    for c in ['vendas_milhoes','jogadores_concluiram_hltb']:
        if c in N and N[c].isna().any():
            if missing=='mediana+indicador': ind[f'{c}_ausente']=N[c].isna().astype(int)
    if logs:
        for c in ['vendas_milhoes','jogadores_concluiram_hltb']:
            if c in N: N[c]=np.log1p(N[c])
    N=N.fillna(N.median())
    N=pd.DataFrame(StandardScaler().fit_transform(N),columns=N.columns)
    blocks['numerico']=N
    if ind: blocks['numerico']=pd.concat([N,pd.DataFrame(ind)],axis=1)
    if genre=='macro': G=multi_hot(d.genero,GENRE_MAP,'genero')
    else: G=pd.get_dummies(d.genero,prefix='genero').astype(int)
    blocks['genero']=G
    if platform=='familia': P=multi_hot(d.plataforma,PLAT_MAP,'plat',sep=' / ')
    else: P=d.plataforma.str.get_dummies(sep=' / ').add_prefix('plat_')
    blocks['plataforma']=P
    blocks['pais']=pd.get_dummies(d.pais_maior_vendas,prefix='pais').astype(int)
    if use_diretor: blocks['diretor']=pd.get_dummies(d.diretor,prefix='diretor').astype(int); w['diretor']=0.25
    parts=[]
    for b,M in blocks.items():
        # equaliza o peso total do bloco (1/sqrt(n_colunas)) e aplica o peso definido a priori
        parts.append(M*(w[b]/np.sqrt(M.shape[1])))
    X=pd.concat(parts,axis=1)
    return X,{b:list(M.columns) for b,M in blocks.items()}

def sim_matrix(X,metric='cosseno'):
    if metric=='cosseno': return cosine_similarity(X.values)
    D=euclidean_distances(X.values); return 1/(1+D)

def recommend(S,df,name,k=5):
    i=df.index[df.jogo==name][0]; o=[j for j in np.argsort(-S[i],kind='stable') if j!=i][:k]
    return [(df.jogo[j],float(S[i,j])) for j in o]

def explain(X,df,i,j,cat=3,num=2,tol=0.5):
    """Explicação: atributos categóricos efetivamente compartilhados (valor positivo em ambos; ordem gênero > plataforma > país)
    + atributos numéricos padronizados com mesmo sinal e menor diferença absoluta (< tol)."""
    xi,xj=X.iloc[i],X.iloc[j]; out=[]
    for pref in ('genero_','plat_','pais_'):
        out+=[c for c in X.columns if c.startswith(pref) and xi[c]>0 and xj[c]>0]
    out=out[:cat]
    nums=[c for c in X.columns if not c.startswith(('genero_','plat_','pais_')) and not c.endswith('_ausente')]
    cand=[(abs(xi[c]-xj[c]),c) for c in nums if xi[c]*xj[c]>0 and abs(xi[c]-xj[c])<tol]
    return out+[c for _,c in sorted(cand)[:num]]
