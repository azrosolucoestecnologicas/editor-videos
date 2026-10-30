"""O que está esperando na pasta `entrada/`, e em que pé cada coisa está.

Um job é uma pasta dentro de `entrada/` com o vídeo e as imagens que vão
aparecer nele. O nome da pasta é o nome do job. Vídeo solto na raiz da
`entrada/` também vale como job, só sem imagens.

Serve para responder, numa olhada, à pergunta com que toda edição começa: o
que já foi feito neste vídeo e qual é o próximo passo.
"""

from dataclasses import dataclass, field
from pathlib import Path

from . import ffmpeg, plano as mod_plano, transcricao

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = RAIZ / "entrada"
PASTA_SAIDA = RAIZ / "output"

VIDEOS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
IMAGENS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}


@dataclass
class Job:
    nome: str
    pasta: Path
    bruto: Path | None = None
    cortado: Path | None = None
    imagens: list[Path] = field(default_factory=list)

    @property
    def video(self):
        """O arquivo em que o resto do pipeline trabalha."""
        return self.cortado or self.bruto

    @property
    def transcrito(self):
        v = self.video
        return v is not None and transcricao.caminho_transcricao(v).exists()

    @property
    def plano(self):
        if self.cortado is None:
            return None
        caminho = mod_plano.caminhos(self.cortado)[0]
        return caminho if caminho.exists() else None

    @property
    def render(self):
        if self.bruto is None:
            return None
        saida = PASTA_SAIDA / f"{self.bruto.stem}_final.mp4"
        return saida if saida.exists() else None

    @property
    def proximo_passo(self):
        """A única coisa que falta fazer agora — em português, para quem lê."""
        if self.bruto is None:
            return "nenhum vídeo nesta pasta"
        if self.cortado is None:
            return f'cortar: python editar.py reel "{_curto(self.bruto)}"'
        if self.plano is None:
            return f'planejar: python editar.py plano "{_curto(self.cortado)}"'
        dados = mod_plano.carregar(self.plano) or {}
        pendentes = [c["id"] for c in dados.get("cenas") or [] if c.get("tipo") is None]
        if pendentes:
            return f"escrever {len(pendentes)} cena(s) sem tipo: {', '.join(pendentes[:6])}"
        if self.render is None:
            return f'conferir os stills e renderizar: python editar.py reel "{_curto(self.bruto)}"'
        return "pronto"


def _curto(caminho):
    """O caminho como você o digitaria, relativo à raiz do projeto."""
    try:
        return Path(caminho).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(caminho)


def _video_do_job(arquivos):
    """Separa o bruto do cortado.

    `cortar` grava ao lado do original com o sufixo `_cortado`, então os dois
    convivem na mesma pasta e o bruto é simplesmente o que não tem o sufixo.
    """
    cortados = [a for a in arquivos if a.stem.endswith("_cortado")]
    brutos = [a for a in arquivos if not a.stem.endswith("_cortado")]
    cortado = max(cortados, key=lambda a: a.stat().st_mtime, default=None)
    if cortado is not None:
        # O bruto deste cortado, e não qualquer outro vídeo que esteja na pasta.
        esperado = cortado.stem[: -len("_cortado")]
        combina = [a for a in brutos if a.stem == esperado]
        if combina:
            return combina[0], cortado
    bruto = max(brutos, key=lambda a: a.stat().st_mtime, default=None)
    return bruto, cortado


def _montar(nome, pasta, arquivos):
    videos = sorted(a for a in arquivos if a.suffix.lower() in VIDEOS)
    bruto, cortado = _video_do_job(videos)
    imagens = sorted(a for a in arquivos if a.suffix.lower() in IMAGENS)
    return Job(nome=nome, pasta=pasta, bruto=bruto, cortado=cortado, imagens=imagens)


def listar(raiz=None):
    """Todos os jobs da `entrada/`, mais recente primeiro."""
    raiz = Path(raiz) if raiz else PASTA_ENTRADA
    if not raiz.exists():
        return []

    jobs = []
    for pasta in sorted(p for p in raiz.iterdir() if p.is_dir()):
        arquivos = [a for a in pasta.rglob("*") if a.is_file()]
        job = _montar(pasta.name, pasta, arquivos)
        if job.bruto is not None:
            jobs.append(job)

    soltos = [a for a in raiz.iterdir() if a.is_file() and a.suffix.lower() in VIDEOS]
    for bruto, cortado in ([_video_do_job(soltos)] if soltos else []):
        if bruto is not None:
            jobs.append(Job(nome=bruto.stem, pasta=raiz, bruto=bruto, cortado=cortado))

    return sorted(jobs, key=lambda j: j.bruto.stat().st_mtime, reverse=True)


def descrever(job):
    """As linhas que o comando `entrada` imprime para um job."""
    linhas = [f"{job.nome}"]
    if job.bruto is not None:
        duracao = ffmpeg.duracao(job.bruto, padrao=0.0)
        tempo = f"{int(duracao // 60)}:{int(duracao % 60):02d}" if duracao else "?"
        linhas.append(f"  vídeo      {_curto(job.bruto)} ({tempo})")
    if job.cortado is not None:
        cortado = ffmpeg.duracao(job.cortado, padrao=0.0)
        linhas.append(f"  cortado    {_curto(job.cortado)} ({int(cortado // 60)}:{int(cortado % 60):02d})")
    if job.imagens:
        nomes = ", ".join(a.name for a in job.imagens[:4])
        resto = f" (+{len(job.imagens) - 4})" if len(job.imagens) > 4 else ""
        linhas.append(f"  imagens    {len(job.imagens)}: {nomes}{resto}")
    if job.plano is not None:
        dados = mod_plano.carregar(job.plano) or {}
        cenas = dados.get("cenas") or []
        escritas = sum(1 for c in cenas if c.get("tipo"))
        linhas.append(f"  plano      {escritas}/{len(cenas)} cena(s) escrita(s)")
    if job.render is not None:
        linhas.append(f"  render     {_curto(job.render)}")
    linhas.append(f"  → {job.proximo_passo}")
    return linhas
