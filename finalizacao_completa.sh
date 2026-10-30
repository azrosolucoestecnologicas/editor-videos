#!/bin/bash
# Script completo: renderiza final + remove pausas + acelera 1.4x

echo "🎬 INICIANDO PIPELINE FINAL..."

VIDEO_ENTRADA="saida/Enter_x_OAB_v2_profissional.mp4"
VIDEO_SEM_PAUSAS="saida/Enter_x_OAB_v2_sem_pausas.mp4"
VIDEO_FINAL="saida/Enter_x_OAB_FINAL.mp4"

# 1. Remover pausas longas
echo "✂️  Removendo pausas longas..."
python3 remover_pausas.py "$VIDEO_ENTRADA" "$VIDEO_SEM_PAUSAS"

if [ ! -f "$VIDEO_SEM_PAUSAS" ]; then
    echo "❌ Erro ao remover pausas"
    exit 1
fi

# 2. Acelerar 1.4x
echo "⏱️  Acelerando para 1.4x..."
ffmpeg -y -v error \
    -i "$VIDEO_SEM_PAUSAS" \
    -vf "setpts=PTS/1.4" \
    -af "atempo=1.4" \
    -c:v libx264 -preset fast -crf 20 \
    -c:a aac -b:a 192k \
    -movflags +faststart \
    "$VIDEO_FINAL"

# 3. Verificar resultado
if [ -f "$VIDEO_FINAL" ]; then
    DURACAO=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FINAL")
    TAMANHO=$(ls -lh "$VIDEO_FINAL" | awk '{print $5}')

    echo ""
    echo "✅ VÍDEO FINAL PRONTO!"
    echo "📁 $VIDEO_FINAL"
    echo "📊 Tamanho: $TAMANHO"
    echo "⏱️  Duração: $(printf '%.0f' $DURACAO)s ($(printf '%02d:%02d' $((${DURACAO%.*}/60)) $((${DURACAO%.*}%60))))"
    echo ""
    echo "🚀 Pronto para publicar!"
else
    echo "❌ Erro na aceleração"
    exit 1
fi
