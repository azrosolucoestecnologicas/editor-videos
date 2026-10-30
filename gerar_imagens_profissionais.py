#!/usr/bin/env python3
"""Gera imagens profissionais com design metálico para o vídeo ENTER x OAB."""

from PIL import Image, ImageDraw, ImageFont
import os

def criar_imagem(largura, altura, cor_fundo, arquivo):
    """Cria base de imagem com fundo gradiente."""
    img = Image.new("RGB", (largura, altura), cor_fundo)
    return img

# Criar diretório
os.makedirs("assets", exist_ok=True)

# Cores profissionais metalizado
COR_ESCURO = "#0a0e27"
COR_OURO = "#d4af37"
COR_PRATA = "#c0c0c0"
COR_AZUL_ESCURO = "#1a3a52"

W, H = 1920, 1080

# 1. Hook inicial
img = Image.new("RGB", (W, H), COR_ESCURO)
d = ImageDraw.Draw(img)
# Texto principal
d.text((W//2, H//3), "UMA STARTUP DE IA PROCESSADA\nPELA ORDEM DOS ADVOGADOS", 
       fill=COR_OURO, anchor="mm", font=None)
# Subtítulo
d.text((W//2, 2*H//3), "A disputa que vai além da tecnologia", 
       fill=COR_PRATA, anchor="mm")
img.save("assets/hook_inicial.png")
print("✓ Hook inicial criado")

# 2. Separador - ENTER vs OAB
img = Image.new("RGB", (W, H), COR_ESCURO)
d = ImageDraw.Draw(img)
d.text((W//4, H//2), "ENTER", fill=COR_OURO, anchor="mm")
d.text((3*W//4, H//2), "OAB", fill=COR_OURO, anchor="mm")
d.line([(W//2, 100), (W//2, H-100)], fill=COR_PRATA, width=4)
img.save("assets/vs_separador.png")
print("✓ VS Separador criado")

# 3. Timeline de fases
img = Image.new("RGB", (W, H), COR_ESCURO)
d = ImageDraw.Draw(img)
fases = ["DIAGNÓSTICO", "ESTRATÉGIA", "POSTULAÇÃO"]
for i, fase in enumerate(fases):
    x = (i+1) * W // 4
    d.rectangle([(x-100, H//2-50), (x+100, H//2+50)], outline=COR_OURO, width=3)
    d.text((x, H//2), fase, fill=COR_OURO, anchor="mm")
img.save("assets/fases_timeline.png")
print("✓ Timeline de fases criado")

# 4. Destaque: "Quem assina vs Quem faz"
img = Image.new("RGB", (W, H), COR_ESCURO)
d = ImageDraw.Draw(img)
d.text((W//4, H//2-100), "QUEM\nASSINA?", fill=COR_PRATA, anchor="mm")
d.text((3*W//4, H//2+100), "QUEM\nFAZ?", fill=COR_OURO, anchor="mm")
img.save("assets/quem_assina_faz.png")
print("✓ Quem assina/faz criado")

print("\n✓ Todas as imagens profissionais criadas em assets/")
