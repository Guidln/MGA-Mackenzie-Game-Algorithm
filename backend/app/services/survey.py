"""Pesquisa com usuários: guarda TUDO (resposta bruta + tabelas normalizadas + rascunhos) e extrai agregados."""
import csv
import io
import json
import re
import sqlite3
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS respostas (
  id INTEGER PRIMARY KEY AUTOINCREMENT, criado_em TEXT NOT NULL, nome TEXT, faixa_etaria TEXT, horas_semana TEXT,
  plataformas TEXT, generos TEXT, referencia_id INTEGER, nota_geral INTEGER, comentario TEXT, payload TEXT, sid TEXT);
CREATE TABLE IF NOT EXISTS jogos_resp (resposta_id INTEGER NOT NULL, game_id INTEGER NOT NULL, nota INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS recs_resp (resposta_id INTEGER NOT NULL, referencia_id INTEGER, game_id INTEGER NOT NULL,
  posicao INTEGER, similaridade REAL, resposta TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS extras_resp (resposta_id INTEGER NOT NULL, titulo TEXT NOT NULL, chave TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS wishlist_resp (resposta_id INTEGER NOT NULL, game_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS rascunhos (sid TEXT PRIMARY KEY, atualizado_em TEXT NOT NULL, payload TEXT NOT NULL, concluido INTEGER NOT NULL DEFAULT 0);
"""
now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
avg = lambda v: round(sum(v) / len(v), 2) if v else None


class Survey:
    def __init__(self, path):
        self.path = str(path)
        with self._db() as c:
            c.executescript(SCHEMA)
            cols = {r["name"] for r in c.execute("PRAGMA table_info(respostas)")}
            for col in ("payload", "sid"):  # migra bancos criados na versão anterior
                if col not in cols:
                    c.execute(f"ALTER TABLE respostas ADD COLUMN {col} TEXT")

    @contextmanager
    def _db(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()

    @staticmethod
    def _norm(t):
        return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()

    # ---------- escrita ----------
    def save_draft(self, sid: str, payload: dict):
        """Autosave: guarda o que já foi preenchido, mesmo que a pessoa não conclua."""
        with self._db() as c:
            c.execute("INSERT INTO rascunhos(sid,atualizado_em,payload,concluido) VALUES(?,?,?,0) "
                      "ON CONFLICT(sid) DO UPDATE SET atualizado_em=excluded.atualizado_em, payload=excluded.payload WHERE concluido=0",
                      (sid, now(), json.dumps(payload, ensure_ascii=False)))

    def add(self, d: dict, n_games: int) -> int:
        """d: dict do SurveyIn. IDs fora do catálogo são descartados; duplicatas por jogo ficam com a última nota."""
        jogos = {j["game_id"]: j["nota"] for j in d["jogos"] if 0 <= j["game_id"] < n_games}
        recs = [r for r in d["avaliacoes"] if 0 <= r["game_id"] < n_games]
        wish = sorted({g for g in d.get("wishlist", []) if 0 <= g < n_games})
        extras = {}
        for t in d["extras"]:
            t = t.strip()[:80]
            if t and self._norm(t):
                extras.setdefault(self._norm(t), t)
        with self._db() as c:
            cur = c.execute(
                "INSERT INTO respostas(criado_em,nome,faixa_etaria,horas_semana,plataformas,generos,referencia_id,nota_geral,comentario,payload,sid)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (now(), (d.get("nome") or "").strip() or None, d.get("faixa_etaria"), d.get("horas_semana"),
                 json.dumps(d["plataformas"], ensure_ascii=False), json.dumps(d["generos"], ensure_ascii=False),
                 d.get("referencia_id"), d.get("nota_geral"), (d.get("comentario") or "").strip() or None,
                 json.dumps(d, ensure_ascii=False), d.get("sid")))
            rid = cur.lastrowid
            c.executemany("INSERT INTO jogos_resp VALUES(?,?,?)", [(rid, g, n) for g, n in jogos.items()])
            c.executemany("INSERT INTO recs_resp VALUES(?,?,?,?,?,?)",
                          [(rid, r.get("referencia_id", d.get("referencia_id")), r["game_id"], r["posicao"], r.get("similaridade"), r["resposta"]) for r in recs])
            c.executemany("INSERT INTO extras_resp VALUES(?,?,?)", [(rid, t, k) for k, t in extras.items()])
            c.executemany("INSERT INTO wishlist_resp VALUES(?,?)", [(rid, g) for g in wish])
            if d.get("sid"):
                c.execute("INSERT INTO rascunhos(sid,atualizado_em,payload,concluido) VALUES(?,?,?,1) "
                          "ON CONFLICT(sid) DO UPDATE SET concluido=1, atualizado_em=excluded.atualizado_em, payload=excluded.payload",
                          (d["sid"], now(), json.dumps(d, ensure_ascii=False)))
        return rid

    # ---------- leitura para o motor de recomendação ----------
    def community_data(self):
        """(n_respostas, [ {game_id: nota} por usuário ], {(ref, game): [aprovações, total]}, assinatura p/ cache)."""
        with self._db() as c:
            n = c.execute("SELECT COUNT(*) FROM respostas").fetchone()[0]
            last = c.execute("SELECT COALESCE(MAX(id),0) FROM respostas").fetchone()[0]
            users = defaultdict(dict)
            for r in c.execute("SELECT resposta_id, game_id, nota FROM jogos_resp"):
                users[r["resposta_id"]][r["game_id"]] = r["nota"]
            pairs = defaultdict(lambda: [0, 0])
            for r in c.execute("SELECT referencia_id, game_id, resposta FROM recs_resp WHERE referencia_id IS NOT NULL"):
                p = pairs[(r["referencia_id"], r["game_id"])]
                p[1] += 1
                p[0] += r["resposta"] in ("quero", "gostei")
        return n, list(users.values()), dict(pairs), (n, last)

    # ---------- agregados ----------
    def summary(self, names: list[str]) -> dict:
        nm = lambda i: names[i] if i is not None and 0 <= i < len(names) else f"#{i}"
        with self._db() as c:
            total = c.execute("SELECT COUNT(*) FROM respostas").fetchone()[0]
            resp = c.execute("SELECT * FROM respostas ORDER BY id DESC").fetchall()
            jogos = c.execute("SELECT * FROM jogos_resp").fetchall()
            recs = c.execute("SELECT * FROM recs_resp").fetchall()
            extras = c.execute("SELECT titulo, chave FROM extras_resp").fetchall()
            wish = c.execute("SELECT game_id FROM wishlist_resp").fetchall()
            dr = c.execute("SELECT COUNT(*), COALESCE(SUM(concluido),0) FROM rascunhos").fetchone()

        por_jogo = defaultdict(list)
        for j in jogos:
            por_jogo[j["game_id"]].append(j["nota"])
        titulos = [dict(game_id=g, jogo=nm(g), citacoes=len(n), nota_media=round(sum(n) / len(n), 2)) for g, n in por_jogo.items()]
        mais_jogados = sorted(titulos, key=lambda t: (-t["citacoes"], -t["nota_media"], t["jogo"]))[:15]
        melhor_avaliados = sorted([t for t in titulos if t["citacoes"] >= 2], key=lambda t: (-t["nota_media"], -t["citacoes"]))[:15]

        por_pos, pares = defaultdict(lambda: [0, 0]), defaultdict(Counter)
        for r in recs:
            ok = r["resposta"] in ("quero", "gostei")
            por_pos[r["posicao"]][0] += 1; por_pos[r["posicao"]][1] += ok
            pares[(r["referencia_id"], r["game_id"])][r["resposta"]] += 1
        n_rec = len(recs); n_ok = sum(v[1] for v in por_pos.values())
        pares_l = []
        for (ref, g), cnt in pares.items():
            t = sum(cnt.values()); a = cnt["quero"] + cnt["gostei"]
            pares_l.append(dict(referencia=nm(ref) if ref is not None else "—", recomendado=nm(g), avaliacoes=t,
                                aprovacao=round(a / t, 3), quero=cnt["quero"], gostei=cnt["gostei"], nao=cnt["nao"]))
        pares_l.sort(key=lambda p: (-p["aprovacao"], -p["avaliacoes"]))

        ex = Counter(); label = {}
        for e in extras:
            ex[e["chave"]] += 1; label.setdefault(e["chave"], e["titulo"])

        P = []  # payloads completos (campos novos)
        for r in resp:
            try:
                P.append(json.loads(r["payload"] or "{}"))
            except ValueError:
                P.append({})
        cnt = lambda key: [dict(nome=k, total=v) for k, v in Counter(x for p in P for x in (p.get(key) if isinstance(p.get(key), list) else [p.get(key)]) if x).most_common()]
        valores = defaultdict(list)
        for p in P:
            for k, v in (p.get("valores") or {}).items():
                valores[k].append(v)
        sis = [p.get("sistema") or {} for p in P]
        num = lambda k: [s[k] for s in sis if isinstance(s.get(k), (int, float))]
        nps = num("nps")
        prom, det = sum(v >= 9 for v in nps), sum(v <= 6 for v in nps)
        fav = Counter(p["favorito_id"] for p in P if p.get("favorito_id") is not None)
        notas = [r["nota_geral"] for r in resp if r["nota_geral"]]
        return dict(
            total_respostas=total, nota_geral_media=avg(notas),
            rascunhos=dict(total=dr[0], concluidos=dr[1], em_andamento=dr[0] - dr[1]),
            mais_jogados=mais_jogados, melhor_avaliados=melhor_avaliados,
            recomendacoes=dict(avaliadas=n_rec, aprovacao=round(n_ok / n_rec, 3) if n_rec else None,
                               por_posicao=[dict(posicao=p, avaliacoes=v[0], aprovacao=round(v[1] / v[0], 3)) for p, v in sorted(por_pos.items())],
                               pares=pares_l[:20]),
            sugeridos_pelos_usuarios=[dict(titulo=label[k], votos=n) for k, n in ex.most_common(20)],
            quero_jogar=[dict(jogo=nm(g), votos=n) for g, n in Counter(w["game_id"] for w in wish).most_common(10)],
            favoritos=[dict(jogo=nm(g), votos=n) for g, n in fav.most_common(10)],
            generos=cnt("generos"), plataformas=cnt("plataformas"), descoberta=cnt("descoberta"),
            regioes=cnt("regiao"), gasto=cnt("gasto_mensal"), anos_jogando=cnt("anos_jogando"), faixas=cnt("faixa_etaria"), horas=cnt("horas_semana"),
            estilos=cnt("estilo"), voltaria=[dict(nome=k, total=v) for k, v in Counter(s.get("voltaria") for s in sis if s.get("voltaria")).most_common()],
            valores_media=[dict(nome=k, media=avg(v), n=len(v)) for k, v in sorted(valores.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))],
            sistema=dict(nps=round(100 * (prom - det) / len(nps)) if nps else None, nps_n=len(nps),
                         clareza=avg(num("clareza")), facilidade=avg(num("facilidade")), surpresa=avg(num("surpresa"))),
            abertas=[dict(data=r["criado_em"][:10], gostou=(s.get("gostou") or "").strip(), faltou=(s.get("faltou") or "").strip())
                     for r, s in zip(resp, sis) if (s.get("gostou") or s.get("faltou"))][:20],
            comentarios=[dict(data=r["criado_em"][:10], nota=r["nota_geral"], texto=r["comentario"]) for r in resp if r["comentario"]][:20])

    def export_csv(self, names: list[str]) -> str:
        """Formato longo: uma linha por (resposta, tipo, item). Pronto para pandas/Excel. Para TUDO, use export_json()."""
        nm = lambda i: names[i] if i is not None and 0 <= i < len(names) else ""
        out = io.StringIO(); w = csv.writer(out)
        w.writerow(["resposta_id", "criado_em", "faixa_etaria", "horas_semana", "tipo", "referencia", "titulo", "nota_ou_resposta", "posicao", "similaridade"])
        with self._db() as c:
            for r in c.execute("SELECT * FROM respostas ORDER BY id"):
                base = [r["id"], r["criado_em"], r["faixa_etaria"] or "", r["horas_semana"] or ""]
                for j in c.execute("SELECT * FROM jogos_resp WHERE resposta_id=?", (r["id"],)):
                    w.writerow(base + ["jogo_jogado", "", nm(j["game_id"]), j["nota"], "", ""])
                for x in c.execute("SELECT * FROM recs_resp WHERE resposta_id=?", (r["id"],)):
                    w.writerow(base + ["recomendacao_mga", nm(x["referencia_id"]), nm(x["game_id"]), x["resposta"], x["posicao"], x["similaridade"] or ""])
                for e in c.execute("SELECT * FROM extras_resp WHERE resposta_id=?", (r["id"],)):
                    w.writerow(base + ["sugestao_usuario", "", e["titulo"], "", "", ""])
                for g in c.execute("SELECT * FROM wishlist_resp WHERE resposta_id=?", (r["id"],)):
                    w.writerow(base + ["quero_jogar", "", nm(g["game_id"]), "", "", ""])
        return out.getvalue()

    def export_json(self) -> str:
        """Dump completo: respostas concluídas (payload bruto) + rascunhos ainda em andamento."""
        with self._db() as c:
            resp = [dict(id=r["id"], criado_em=r["criado_em"], **json.loads(r["payload"] or "{}")) for r in c.execute("SELECT * FROM respostas ORDER BY id")]
            dr = [dict(sid=r["sid"], atualizado_em=r["atualizado_em"], concluido=bool(r["concluido"]), payload=json.loads(r["payload"]))
                  for r in c.execute("SELECT * FROM rascunhos ORDER BY atualizado_em")]
        return json.dumps(dict(respostas=resp, rascunhos=dr), ensure_ascii=False, indent=1)
