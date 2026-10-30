/**
 * Ícones disponíveis para o tipo de cena `icone_destaque`.
 *
 * A skill `reels-estilo` manda usar um único estilo de ícone no vídeo
 * inteiro: linha, `strokeWidth` 2, do `lucide-react`. A lista é explícita em
 * vez de um `import *` para que o bundler carregue só o que é usado — a
 * biblioteca tem quase 2000 ícones.
 *
 * Para usar um ícone novo, acrescente-o aqui com o nome em minúsculas e
 * hífens; é esse nome que vai no `scene_plan.json`.
 */

import {
  AlertTriangle,
  BookOpen,
  Brain,
  CalendarDays,
  CheckCircle2,
  Clock,
  FileSearch,
  FileText,
  FileWarning,
  Gavel,
  Landmark,
  Lightbulb,
  Lock,
  MessageCircle,
  Scale,
  Search,
  ShieldCheck,
  Target,
  TrendingUp,
  Users,
  XCircle,
  Zap,
} from "lucide-react";

export const ICONES = {
  "alert-triangle": AlertTriangle,
  "book-open": BookOpen,
  brain: Brain,
  "calendar-days": CalendarDays,
  "check-circle": CheckCircle2,
  clock: Clock,
  "file-search": FileSearch,
  "file-text": FileText,
  "file-warning": FileWarning,
  gavel: Gavel,
  landmark: Landmark,
  lightbulb: Lightbulb,
  lock: Lock,
  "message-circle": MessageCircle,
  scale: Scale,
  search: Search,
  "shield-check": ShieldCheck,
  target: Target,
  "trending-up": TrendingUp,
  users: Users,
  "x-circle": XCircle,
  zap: Zap,
} as const;

export type NomeIcone = keyof typeof ICONES;

export const NOMES_DE_ICONE = Object.keys(ICONES) as NomeIcone[];

/**
 * Ícone pelo nome.
 *
 * Falha em vez de cair num ícone qualquer: antes, um nome errado no
 * scene_plan virava um triângulo de alerta publicado no reel, que ninguém
 * percebia até alguém assistir. O plano é escrito à mão, então um nome fora
 * do mapa é erro de digitação e tem que aparecer na hora do render.
 */
export const icone = (nome: string) => {
  const achado = ICONES[nome as NomeIcone];
  if (!achado) {
    throw new Error(
      `Ícone "${nome}" não existe. Os disponíveis são: ${NOMES_DE_ICONE.join(", ")}.`,
    );
  }
  return achado;
};
