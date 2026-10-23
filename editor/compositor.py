"""Monta cada quadro final: vídeo da pessoa, tela dividida, animações, zoom e legendas."""

from PIL import Image, ImageDraw

from . import animacoes
from .legendas import Legendas
from .texto import FONTE_PADRAO, cor, ease_in_out, ease_out_cubic, gradiente_vertical, lerp, limitar, progresso

FADE_SAIDA = 0.25


class Compositor:
    def __init__(self, roteiro, largura, altura, fps):
        self.roteiro = roteiro
        self.W, self.H, self.fps = largura, altura, fps
        self.s = largura / 1080
        cfg = roteiro.cfg
        self.div = cfg["divisao"]
        self.tema = dict(cfg["tema"])
        self.tema["_fonte"] = roteiro.arquivo(self.tema["fonte"]) if self.tema.get("fonte") else FONTE_PADRAO

        self.eventos = roteiro.eventos()
        self.Hp = int(round(self.H * float(self.div["proporcao"]) / 2) * 2)  # altura do painel de animação
        self.em_cima = self.div.get("animacao_em", "cima") != "baixo"
        self.T = float(self.div.get("transicao", 0.35))
        self.intervalos_divididos = self._mesclar([(e.inicio, e.fim) for e in self.eventos if e.layout == "dividido"])
        self.intervalos_cheios = self._mesclar([(e.inicio, e.fim) for e in self.eventos if e.layout == "cheio"])
        self.zooms = [e for e in self.eventos if e.zoom is not None]
        self.com_animacao = [e for e in self.eventos if e.animacao]
        self.padrao_dividido = cfg["layout_padrao"] == "dividido"

        self.fundo = gradiente_vertical((self.W, self.Hp), *self._cores_fundo())
        self.sombra_overlay = self._sombra((self.W, self.Hp))
        self.cor_linha = cor(self.tema["destaque"])
        self._anims = {}

        self.legendas = None
        if cfg["legendas"].get("ativas") and roteiro.palavras:
            self.legendas = Legendas(roteiro.palavras, cfg["legendas"], self.tema, self.s, self.W, self.tema["_fonte"])

    # ------------------------------------------------------------ preparação
    def _cores_fundo(self):
        fundo = self.tema["fundo"]
        if isinstance(fundo, str):
            return fundo, fundo
        return fundo[0], fundo[-1]

    def _sombra(self, tamanho):
        w, h = tamanho
        mascara = Image.linear_gradient("L").resize((w, h)).point(lambda v: int((255 - v) * 0.65))
        if not self.em_cima:
            mascara = mascara.transpose(Image.FLIP_TOP_BOTTOM)
        img = Image.new("RGBA", tamanho, (0, 0, 0, 255))
        img.putalpha(mascara)
        return img

    def _mesclar(self, intervalos):
        res = []
        for a, b in sorted(intervalos):
            if res and a - res[-1][1] < 0.8:
                res[-1][1] = max(res[-1][1], b)
            else:
                res.append([a, b])
        return res

    # ------------------------------------------------------------ estados no tempo t
    def fator_divisao(self, t):
        if self.padrao_dividido:
            # Tela dividida o tempo todo, exceto em eventos com layout 'cheio'.
            return 1 - self._rampa(t, self.intervalos_cheios)
        return self._rampa(t, self.intervalos_divididos)

    def _rampa(self, t, intervalos):
        k = 0.0
        for a, b in intervalos:
            entrada = progresso(t, a - self.T / 2, self.T)
            saida = 1 - progresso(t, b - self.T / 2, self.T)
            k = max(k, min(entrada, saida))
        return ease_in_out(k)

    def fator_zoom(self, t):
        z = 1.0
        for e in self.zooms:
            fator = float(e.zoom.get("fator", 1.18))
            entrada = float(e.zoom.get("entrada", 0.12))
            saida = float(e.zoom.get("saida", 0.3))
            k = min(ease_out_cubic(progresso(t, e.inicio, entrada)), 1 - ease_in_out(progresso(t, e.fim - saida, saida)))
            z = max(z, 1 + (fator - 1) * k)
        return z

    def animacao_ativa(self, t):
        ativos = [e for e in self.com_animacao if e.inicio <= t < e.fim]
        for e in list(self._anims):
            if all(ev.indice != e or not (ev.inicio - 1 <= t < ev.fim + 1) for ev in self.com_animacao):
                self._anims.pop(e).fechar()
        if not ativos:
            return None, None
        evento = max(ativos, key=lambda e: e.inicio)  # o mais recente vence
        if evento.indice not in self._anims:
            params = dict(evento.animacao)
            params["_fps"] = self.fps
            self._anims[evento.indice] = animacoes.criar(params, self.tema, self.s, self.roteiro, (self.W, self.Hp))
        return evento, self._anims[evento.indice]

    # ------------------------------------------------------------ quadro
    def quadro(self, frame, t):
        W, H = self.W, self.H
        k = self.fator_divisao(t)
        z = self.fator_zoom(t)
        ph = int(round(self.Hp * k))  # altura visível do painel
        alt_pessoa = H - ph

        z_total = z * lerp(1.0, float(self.div.get("zoom_rosto", 1.0)), k)
        cw = W / z_total
        ch = alt_pessoa / z_total
        cy = lerp(H / 2, float(self.div.get("foco_rosto", 0.36)) * H, k)
        cy = limitar(cy, ch / 2, H - ch / 2)
        caixa = (W / 2 - cw / 2, cy - ch / 2, W / 2 + cw / 2, cy + ch / 2)
        if caixa == (0, 0, W, H):
            pessoa = frame
        else:
            pessoa = frame.resize((W, max(1, alt_pessoa)), Image.BILINEAR, box=caixa)

        tela = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        y_pessoa = ph if self.em_cima else 0
        tela.paste(pessoa, (0, y_pessoa))

        y_painel = ph - self.Hp if self.em_cima else H - ph
        if ph > 0:
            tela.paste(self.fundo, (0, y_painel))

        evento, anim = self.animacao_ativa(t)
        if anim is not None:
            camada = Image.new("RGBA", (W, self.Hp), (0, 0, 0, 0))
            anim.desenhar(camada, t - evento.inicio, evento.fim - evento.inicio)
            alfa = 1 - progresso(t, evento.fim - FADE_SAIDA, FADE_SAIDA)
            if evento.layout != "dividido" and k < 0.5:
                # Animação por cima do vídeo em tela cheia: escurece o fundo para dar leitura.
                sombra = self.sombra_overlay
                entrada = progresso(t, evento.inicio, 0.25)
                if entrada < 1:
                    sombra = sombra.copy()
                    sombra.putalpha(sombra.getchannel("A").point(lambda v: int(v * entrada)))
                camada = Image.alpha_composite(sombra, camada)
                y_painel = 0 if self.em_cima else H - self.Hp
            if alfa < 1:
                camada.putalpha(camada.getchannel("A").point(lambda v: int(v * alfa)))
            tela.alpha_composite(camada, (0, y_painel))

        if ph > 0 and self.tema.get("linha_divisoria", True):
            y_linha = ph if self.em_cima else H - ph
            espessura = max(2, int(6 * self.s))
            ImageDraw.Draw(tela).rectangle((0, y_linha - espessura // 2, W, y_linha + espessura // 2), fill=self.cor_linha)

        if self.legendas is not None:
            img, alfa = self.legendas.imagem(t)
            if img is not None:
                pos_div = self.roteiro.cfg["legendas"].get("posicao_dividido", "divisao")
                y_div = (ph if self.em_cima else H - ph) if pos_div == "divisao" else float(pos_div) * H
                y_cheio = float(self.roteiro.cfg["legendas"].get("posicao_cheio", 0.72))
                if anim is not None and evento.layout != "dividido" and not self.em_cima:
                    y_cheio = 1 - y_cheio  # animação sobreposta embaixo: legenda sobe
                y = lerp(y_cheio * H, y_div, k)
                if alfa < 1:
                    img = img.copy()
                    img.putalpha(img.getchannel("A").point(lambda v: int(v * alfa)))
                x0 = int((W - img.width) / 2)
                y0 = int(limitar(y - img.height / 2, 0, H - img.height))
                tela.alpha_composite(img, (x0, y0))

        return tela.convert("RGB")

    def fechar(self):
        for a in self._anims.values():
            a.fechar()
        self._anims.clear()
