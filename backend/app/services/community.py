"""Feedback loop: transforma as respostas da pesquisa em sinais que ajustam o ranking do MGA.

score_final = (1 - w) * conteúdo (cosseno mapeado para 0–1) + w * comunidade,  com  w = 0,6 * n / (n + 25)
  (sem respostas, w = 0 e o resultado é exatamente o MGA original; com muitas respostas, a comunidade chega a 60%).
comunidade = 0,45 * similaridade item-item (jogadores que avaliaram os dois jogos)
           + 0,35 * aprovação direta do par referência→recomendado (suavizada: (a+1)/(t+2))
           + 0,20 * qualidade média do jogo (notas, suavizada).
Valores sem evidência ficam neutros (0,5), de modo que poucos dados não distorcem o ranking."""
import numpy as np

W_CF, W_PAIR, W_Q, SHRINK, W_MAX, W_HALF = 0.45, 0.35, 0.20, 5.0, 0.6, 25.0


class Community:
    def __init__(self, n_games, n_resp, users, pairs):
        self.n, self.n_resp, self.pairs = n_games, n_resp, pairs
        R = np.zeros((max(len(users), 1), n_games)); M = np.zeros_like(R, dtype=bool)
        for u, d in enumerate(users):
            for g, v in d.items():
                if 0 <= g < n_games:
                    R[u, g] = v; M[u, g] = True
        cnt_u = np.maximum(M.sum(1), 1)
        C = np.where(M, R - (R.sum(1) / cnt_u)[:, None], 0.0)          # nota centrada na média de cada usuário
        num, norm = C.T @ C, np.sqrt((C ** 2).sum(0))
        den = np.outer(norm, norm)
        cos = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
        co = M.T.astype(float) @ M.astype(float)                        # usuários que avaliaram os dois
        self.cf, self.co = cos * co / (co + SHRINK), co
        self.count = M.sum(0)
        self.quality = (R.sum(0) + 3 * 2) / (self.count + 2) / 5        # prior: nota 3 com peso 2
        self.mean = np.where(self.count > 0, R.sum(0) / np.maximum(self.count, 1), np.nan)

    @property
    def weight(self):
        return W_MAX * self.n_resp / (self.n_resp + W_HALF) if self.n_resp else 0.0

    def pair(self, i, j):
        a, t = self.pairs.get((i, j), (0, 0))
        return a, t

    def score(self, i):
        """Vetor (n_games,) com o escore de comunidade de cada jogo para a referência i."""
        p = np.array([(self.pair(i, j)[0] + 1) / (self.pair(i, j)[1] + 2) for j in range(self.n)])
        return W_CF * (self.cf[i] + 1) / 2 + W_PAIR * p + W_Q * self.quality

    def detail(self, i, j):
        a, t = self.pair(i, j)
        return dict(aprovacao=round(a / t, 3) if t else None, avaliacoes_par=t,
                    nota_media=None if np.isnan(self.mean[j]) else round(float(self.mean[j]), 2),
                    n_notas=int(self.count[j]), jogadores_em_comum=int(self.co[i, j]))

    def rank(self, S_row, i, k):
        """Reordena os candidatos combinando conteúdo e comunidade. Retorna [(j, final, conteudo, comunidade)]."""
        idx = np.array([j for j in range(self.n) if j != i])
        c = S_row[idx]
        cn = (c + 1) / 2
        com = self.score(i)[idx]
        w = self.weight
        fin = (1 - w) * cn + w * com
        order = np.lexsort((-c, -fin))[:k]                               # desempate pelo cosseno
        return [(int(idx[o]), float(fin[o]), float(c[o]), float(com[o])) for o in order]
