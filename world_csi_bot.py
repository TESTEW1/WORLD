import discord
from discord.ext import commands, tasks
import random
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
import json
import time
#
# ================= INTENTS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
DB_FILE = "world_csi.db"
CANAL_BETA = "🌎・mundo-csi"
ADMIN_ID = 769951556388257812

# ================= CLASSES =================
CLASSES = {
    "Guerreiro": {
        "emoji": "⚔️",
        "hp_bonus": 30,
        "atk_bonus": 15,
        "def_bonus": 10,
        "description": "Mestre do combate corpo a corpo, resistente e poderoso."
    },
    "Mago": {
        "emoji": "🔮",
        "hp_bonus": 10,
        "atk_bonus": 25,
        "def_bonus": 5,
        "description": "Manipulador de energias arcanas, devastador mas frágil."
    },
    "Arqueiro": {
        "emoji": "🏹",
        "hp_bonus": 15,
        "atk_bonus": 20,
        "def_bonus": 8,
        "description": "Atirador preciso, ágil e letal à distância."
    },
    "Paladino": {
        "emoji": "🛡️",
        "hp_bonus": 25,
        "atk_bonus": 12,
        "def_bonus": 15,
        "description": "Guerreiro sagrado, equilibrado entre ataque e defesa."
    },
    "Assassino": {
        "emoji": "🗡️",
        "hp_bonus": 12,
        "atk_bonus": 22,
        "def_bonus": 6,
        "description": "Mestre das sombras, golpes críticos devastadores."
    },
    "Necromante": {
        "emoji": "💀",
        "hp_bonus": 8,
        "atk_bonus": 23,
        "def_bonus": 7,
        "description": "Senhor dos mortos, drena vida dos inimigos."
    },
    "Berserker": {
        "emoji": "🪓",
        "hp_bonus": 35,
        "atk_bonus": 18,
        "def_bonus": 5,
        "description": "Fúria incontrolável, quanto menor o HP mais forte."
    },
    "Druida": {
        "emoji": "🌿",
        "hp_bonus": 20,
        "atk_bonus": 14,
        "def_bonus": 12,
        "description": "Guardião da natureza, se cura ao coletar recursos."
    },
    "Monge": {
        "emoji": "👊",
        "hp_bonus": 18,
        "atk_bonus": 16,
        "def_bonus": 14,
        "description": "Mestre das artes marciais, equilibrado e versátil."
    },
    "Bardo": {
        "emoji": "🎵",
        "hp_bonus": 15,
        "atk_bonus": 10,
        "def_bonus": 10,
        "mana_bonus": 20,
        "description": "Músico encantador, bônus de XP e sorte aumentada."
    }
}

# ================= RAÇAS =================
RACES = {
    "Humano": {
        "emoji": "👤",
        "hp_bonus": 20,
        "atk_bonus": 8,
        "def_bonus": 8,
        "xp_mult": 1.10,
        "description": "Adaptáveis e resilientes. Ganham 10% a mais de XP em todas as ações.",
        "passive": "Adaptabilidade: +10% XP ganho permanentemente.",
        "lore": "Os humanos são os mais jovens entre as raças, mas sua ambição supera qualquer limitação natural."
    },
    "Élfico": {
        "emoji": "🧝",
        "hp_bonus": 12,
        "atk_bonus": 18,
        "def_bonus": 6,
        "xp_mult": 1.05,
        "description": "Ágeis e precisos, com afinidade natural por magia e arco.",
        "passive": "Visão Élfica: +15% chance de crítico com ataques à distância.",
        "lore": "Os elfos habitam as florestas eternas, guardiões da memória do mundo antes dos humanos."
    },
    "Anão": {
        "emoji": "⚒️",
        "hp_bonus": 35,
        "atk_bonus": 12,
        "def_bonus": 20,
        "xp_mult": 1.0,
        "description": "Robustos e resistentes, mestres da forja e da batalha em espaços fechados.",
        "passive": "Pele de Pedra: Reduz o dano recebido em 10%.",
        "lore": "Os anões nasceram das rochas primordiais. Cada golpe deles ecoa como um martelo na bigorna."
    },
    "Orc": {
        "emoji": "🟢",
        "hp_bonus": 40,
        "atk_bonus": 22,
        "def_bonus": 5,
        "xp_mult": 0.95,
        "description": "Brutais e selvagens, força física incomparável mas baixa resistência mágica.",
        "passive": "Fúria Tribal: +20% ATK quando HP < 40%.",
        "lore": "Os orcs vieram das estepes vermelhas. Sua força é lendária — dizem que um orc raivoso vale dez guerreiros humanos."
    },
    "Anjo": {
        "emoji": "👼",
        "hp_bonus": 18,
        "atk_bonus": 14,
        "def_bonus": 16,
        "xp_mult": 1.05,
        "description": "Seres celestiais com cura poderosa e proteção divina.",
        "passive": "Graça Divina: Recupera 5% HP ao início de cada turno de batalha.",
        "lore": "Os anjos desceram do Trono Celestial. Poucos escolhem o caminho mortal — aqueles que o fazem carregam um propósito eterno."
    },
    "Demônio": {
        "emoji": "😈",
        "hp_bonus": 15,
        "atk_bonus": 25,
        "def_bonus": 8,
        "xp_mult": 1.0,
        "description": "Seres infernais com poder destrutivo e corrupção.",
        "passive": "Essência Corrompida: +25% dano de veneno e maldições.",
        "lore": "Os demônios emergem do Abismo Ardente. Sua presença corrói a realidade ao redor."
    },
    "Dragônico": {
        "emoji": "🐉",
        "hp_bonus": 30,
        "atk_bonus": 20,
        "def_bonus": 12,
        "xp_mult": 1.0,
        "description": "Descendentes de dragões com escamas resistentes e sopro de fogo.",
        "passive": "Sangue de Dragão: Imune a veneno; +15% dano de fogo.",
        "lore": "Os dragônicos são filhos da aliança proibida entre humanos e dragões. Carregam o fardo e a glória de dois mundos."
    },
    "Vampiro": {
        "emoji": "🧛",
        "hp_bonus": 10,
        "atk_bonus": 22,
        "def_bonus": 10,
        "xp_mult": 1.05,
        "description": "Imortais sedentes de sangue, drenam vida dos inimigos.",
        "passive": "Sede de Sangue: 15% de chance de drenar 10% do dano causado como HP.",
        "lore": "Os vampiros são os primeiros imortais criados pela Lua Negra. Eles lembram de tudo — inclusive do fim do mundo anterior."
    },
    "Lobisomem": {
        "emoji": "🐺",
        "hp_bonus": 28,
        "atk_bonus": 20,
        "def_bonus": 8,
        "xp_mult": 1.0,
        "description": "Metamorfos furiosos, mais fortes à noite e em batalhas prolongadas.",
        "passive": "Instinto Predatório: +10% ATK para cada turno passado em batalha.",
        "lore": "Os lobisomens nasceram da primeira lua cheia após a Queda. Vivem entre dois mundos sem pertencer a nenhum."
    },
    "Espectro": {
        "emoji": "👻",
        "hp_bonus": 5,
        "atk_bonus": 28,
        "def_bonus": 4,
        "xp_mult": 1.05,
        "description": "Seres etéreos, difíceis de acertar e com ataques que atravessam defesas.",
        "passive": "Forma Etérea: 20% de chance de esquivar completamente de um ataque.",
        "lore": "Os espectros são almas que recusaram morrer. Existem em ambos os planos — e não pertencem a nenhum."
    },
    "Golem": {
        "emoji": "🗿",
        "hp_bonus": 60,
        "atk_bonus": 10,
        "def_bonus": 30,
        "xp_mult": 0.90,
        "description": "Construções animadas com HP e DEF extremos mas baixo ATK.",
        "passive": "Corpo de Pedra: Reduz dano recebido em 20%, mas ganha 10% menos XP.",
        "lore": "Os golems foram criados para serem perfeitos. Alguns desenvolveram consciência — e nenhum de seus criadores sobreviveu para contar."
    },
    "Sereia": {
        "emoji": "🧜",
        "hp_bonus": 14,
        "atk_bonus": 16,
        "def_bonus": 10,
        "xp_mult": 1.08,
        "description": "Criaturas aquáticas com magias de encantamento e controle.",
        "passive": "Voz Encantada: 25% de chance de encantar o inimigo, fazendo-o perder um turno.",
        "lore": "As sereias governam os oceanos há mais tempo do que existem cidades. Sua voz é a coisa mais perigosa do mundo."
    },
    "Titã": {
        "emoji": "🏔️",
        "hp_bonus": 50,
        "atk_bonus": 25,
        "def_bonus": 15,
        "xp_mult": 0.92,
        "description": "Descendentes dos Titãs primordiais, força e tamanho colossal.",
        "passive": "Herança Titânica: +30% HP máximo ao evoluir de classe.",
        "lore": "Os titãs são os filhos dos primeiros seres criados pelo universo. Poucos existem — e cada um é uma força da natureza."
    },
    "Fada": {
        "emoji": "🧚",
        "hp_bonus": 8,
        "atk_bonus": 12,
        "def_bonus": 6,
        "xp_mult": 1.15,
        "description": "Seres mágicos minúsculos com sorte extrema e bônus de XP elevado.",
        "passive": "Benção da Fada: +15% XP e +1 ponto de sorte permanentemente.",
        "lore": "As fadas são os espíritos do primeiro jardim do mundo. Pequenas em tamanho, imensas em poder mágico."
    },
    "Elementário": {
        "emoji": "🌀",
        "hp_bonus": 20,
        "atk_bonus": 20,
        "def_bonus": 10,
        "xp_mult": 1.0,
        "description": "Seres compostos de elementos puros, mudam de forma em batalha.",
        "passive": "Mudança Elemental: Alterna entre bônus de fogo, gelo ou raio a cada batalha.",
        "lore": "Os elementários são os pensamentos dos elementos ganhos em forma. Não nasceram — simplesmente sempre existiram."
    },
    "Goblin": {
        "emoji": "👺",
        "hp_bonus": 10,
        "atk_bonus": 15,
        "def_bonus": 5,
        "xp_mult": 1.12,
        "description": "Pequenos e astutos, alta sorte e ganho de moedas aumentado.",
        "passive": "Ganância Goblin: +20% moedas de qualquer fonte.",
        "lore": "Os goblins são desprezados por todos — e ricos como poucos. Sua astúcia transforma sucata em ouro."
    },
    "Gnomo": {
        "emoji": "🔧",
        "hp_bonus": 12,
        "atk_bonus": 14,
        "def_bonus": 14,
        "xp_mult": 1.05,
        "description": "Inventores natos, equipamentos têm efeito dobrado.",
        "passive": "Engenharia: Bônus de arma e armadura aumentados em 25%.",
        "lore": "Os gnomos construíram a primeira máquina a vapor no Ano 1 da Nova Era. Ninguém sabe o que eles estão construindo agora."
    },
    "Ciclope": {
        "emoji": "👁️",
        "hp_bonus": 45,
        "atk_bonus": 30,
        "def_bonus": 5,
        "xp_mult": 0.95,
        "description": "Um olho que vê tudo — visão perfeita garante críticos mais frequentes.",
        "passive": "Olho Perfeito: +30% chance de crítico; críticos causam 2x dano.",
        "lore": "Os ciclopes vivem nas montanhas proibidas. Cada um guarda um segredo do universo em seu único olho."
    },
    "Sombra": {
        "emoji": "🌑",
        "hp_bonus": 8,
        "atk_bonus": 26,
        "def_bonus": 6,
        "xp_mult": 1.05,
        "description": "Seres das trevas, invisíveis e letais, especializados em ataques furtivos.",
        "passive": "Invisibilidade das Sombras: Primeiro ataque de cada batalha é sempre crítico.",
        "lore": "As sombras são o que sobrou das entidades do Vazio após a criação do mundo. Existem onde a luz não alcança."
    },
    "Ancião": {
        "emoji": "🧙",
        "hp_bonus": 15,
        "atk_bonus": 15,
        "def_bonus": 15,
        "xp_mult": 1.20,
        "description": "Seres de sabedoria suprema, ganham muito mais XP e têm acesso a magias proibidas.",
        "passive": "Sabedoria Eterna: +20% XP e desbloqueia habilidades com 5 níveis de antecedência.",
        "lore": "Os anciões existem desde antes da memória. Cada um passou por mil vidas — e ainda buscam respostas."
    },
}

# ================= EVOLUÇÃO DE RAÇA =================
# Cada raça tem 3 estágios de evolução com bônus em dobro
# Req: level 30 → Evo1, level 70 → Evo2, level 130 → Evo3
RACE_EVOLUTION_TREE = {
    "Humano": [
        {"level": 30,  "name": "Humano Desperto",     "emoji": "👤✨", "suffix": " Desperto",
         "lore": "Sua ambição ultrapassou os limites do comum. O potencial humano começa a se revelar.",
         "hp_bonus": 40, "atk_bonus": 16, "def_bonus": 16},
        {"level": 70,  "name": "Humano Transcendente","emoji": "👤🔥", "suffix": " Transcendente",
         "lore": "Você transcendeu a limitação humana. O seu corpo e mente operam em outro plano.",
         "hp_bonus": 80, "atk_bonus": 32, "def_bonus": 32},
        {"level": 130, "name": "Além-Humano",         "emoji": "👤💎", "suffix": " Além-Humano",
         "lore": "Você não é mais humano no sentido comum. Você é o passo seguinte da evolução.",
         "hp_bonus": 160, "atk_bonus": 64, "def_bonus": 64},
    ],
    "Élfico": [
        {"level": 30,  "name": "Alto Élfico",         "emoji": "🧝✨", "suffix": " Alto",
         "lore": "A magia élfica flui com mais pureza em suas veias. Seus olhos enxergam além do véu.",
         "hp_bonus": 24, "atk_bonus": 36, "def_bonus": 12},
        {"level": 70,  "name": "Élfico Estelar",      "emoji": "🧝⭐", "suffix": " Estelar",
         "lore": "As estrelas respondem ao seu chamado. Você se tornou um canal vivo da magia estelar.",
         "hp_bonus": 48, "atk_bonus": 72, "def_bonus": 24},
        {"level": 130, "name": "Élfico Primordial",   "emoji": "🧝👑", "suffix": " Primordial",
         "lore": "Você carrega a memória do primeiro elfos — e o poder que veio com ela.",
         "hp_bonus": 96, "atk_bonus": 144, "def_bonus": 48},
    ],
    "Anão": [
        {"level": 30,  "name": "Anão de Ferro",       "emoji": "⚒️🔩", "suffix": " de Ferro",
         "lore": "Seu corpo endureceu como o metal que forja. Cada golpe que você absorve te torna mais forte.",
         "hp_bonus": 70, "atk_bonus": 24, "def_bonus": 40},
        {"level": 70,  "name": "Anão de Adamantio",   "emoji": "⚒️💎", "suffix": " de Adamantio",
         "lore": "Sua pele rivaliza com o adamantio. Nada penetra sua defesa sem pagar um alto preço.",
         "hp_bonus": 140, "atk_bonus": 48, "def_bonus": 80},
        {"level": 130, "name": "Anão Primordial",     "emoji": "⚒️👑", "suffix": " Primordial",
         "lore": "Você é a rocha viva em forma de anão. Os próprios titãs curvam-se ante sua resistência.",
         "hp_bonus": 280, "atk_bonus": 96, "def_bonus": 160},
    ],
    "Orc": [
        {"level": 30,  "name": "Orc Warchief",        "emoji": "🟢⚔️", "suffix": " Warchief",
         "lore": "Sua fúria não é cega — é calculada. Os outros orcs te seguem sem questionar.",
         "hp_bonus": 80, "atk_bonus": 44, "def_bonus": 10},
        {"level": 70,  "name": "Orc Lendário",        "emoji": "🟢🔥", "suffix": " Lendário",
         "lore": "Lendas são contadas sobre sua fúria. Inimigos fogem apenas ao ouvir seu nome.",
         "hp_bonus": 160, "atk_bonus": 88, "def_bonus": 20},
        {"level": 130, "name": "Orc Primordial",      "emoji": "🟢👑", "suffix": " Primordial",
         "lore": "Você é a encarnação da fúria tribal. Uma força da natureza com forma de guerreiro.",
         "hp_bonus": 320, "atk_bonus": 176, "def_bonus": 40},
    ],
    "Anjo": [
        {"level": 30,  "name": "Anjo Guardião",       "emoji": "👼✨", "suffix": " Guardião",
         "lore": "Sua luz divina se intensificou. Você protege não apenas a si, mas todos ao redor.",
         "hp_bonus": 36, "atk_bonus": 28, "def_bonus": 32},
        {"level": 70,  "name": "Anjo Celestial",      "emoji": "👼⭐", "suffix": " Celestial",
         "lore": "Suas asas tocam os céus mais altos. O próprio divino reconhece seu poder.",
         "hp_bonus": 72, "atk_bonus": 56, "def_bonus": 64},
        {"level": 130, "name": "Arcanjo",             "emoji": "👼👑", "suffix": " Arcanjo",
         "lore": "Você ascendeu ao posto de Arcanjo. Poucos mortais chegaram tão alto — ou voltaram para contar.",
         "hp_bonus": 144, "atk_bonus": 112, "def_bonus": 128},
    ],
    "Demônio": [
        {"level": 30,  "name": "Demônio Maior",       "emoji": "😈🔥", "suffix": " Maior",
         "lore": "Sua essência corrompida se intensificou. Você não apenas destrói — você consome.",
         "hp_bonus": 30, "atk_bonus": 50, "def_bonus": 16},
        {"level": 70,  "name": "Arquidemônio",        "emoji": "😈💀", "suffix": " Arqui",
         "lore": "Você lidera legiões do abismo. Sua simples presença corrói a realidade.",
         "hp_bonus": 60, "atk_bonus": 100, "def_bonus": 32},
        {"level": 130, "name": "Demônio Primordial",  "emoji": "😈👑", "suffix": " Primordial",
         "lore": "Você é uma das primeiras forças do caos. Anterior ao próprio tempo.",
         "hp_bonus": 120, "atk_bonus": 200, "def_bonus": 64},
    ],
    "Dragônico": [
        {"level": 30,  "name": "Meio-Dragão",         "emoji": "🐉✨", "suffix": " Meio-Dragão",
         "lore": "O sangue dracônico queima mais forte em suas veias. Suas escamas brilham como metal.",
         "hp_bonus": 60, "atk_bonus": 40, "def_bonus": 24},
        {"level": 70,  "name": "Dragônico Puro",      "emoji": "🐉🔥", "suffix": " Puro",
         "lore": "A herança dracônica se revelou por completo. Você é mais dragão do que humano agora.",
         "hp_bonus": 120, "atk_bonus": 80, "def_bonus": 48},
        {"level": 130, "name": "Dragão Encarnado",    "emoji": "🐉👑", "suffix": " Encarnado",
         "lore": "Você é a reencarnação de um dragão ancião em forma humanoide. Lendas te tratam como divindade.",
         "hp_bonus": 240, "atk_bonus": 160, "def_bonus": 96},
    ],
    "Vampiro": [
        {"level": 30,  "name": "Vampiro Antigo",      "emoji": "🧛🌙", "suffix": " Antigo",
         "lore": "Séculos de existência te tornaram mais refinado. Seu toque drena mais do que sangue.",
         "hp_bonus": 20, "atk_bonus": 44, "def_bonus": 20},
        {"level": 70,  "name": "Vampiro Nobre",       "emoji": "🧛👑", "suffix": " Nobre",
         "lore": "Você lidera a nobreza vampírica. Sua sede transforma batalhas em banquetes.",
         "hp_bonus": 40, "atk_bonus": 88, "def_bonus": 40},
        {"level": 130, "name": "Vampiro Primordial",  "emoji": "🧛💎", "suffix": " Primordial",
         "lore": "Você existia antes da Lua Negra. Os outros vampiros são crianças perto de você.",
         "hp_bonus": 80, "atk_bonus": 176, "def_bonus": 80},
    ],
    "Lobisomem": [
        {"level": 30,  "name": "Lobisomem Alfa",      "emoji": "🐺⚡", "suffix": " Alfa",
         "lore": "Sua matilha te reconhece como líder. A lua cheia te obedece.",
         "hp_bonus": 56, "atk_bonus": 40, "def_bonus": 16},
        {"level": 70,  "name": "Lobisomem Lendário",  "emoji": "🐺🔥", "suffix": " Lendário",
         "lore": "Lendas de aldeias inteiras falam do lobo que nunca morre. Esse lobo é você.",
         "hp_bonus": 112, "atk_bonus": 80, "def_bonus": 32},
        {"level": 130, "name": "Lobisomem Primordial","emoji": "🐺👑", "suffix": " Primordial",
         "lore": "Você é o primeiro — o lobo antes de todos os lobos. A própria lua te teme.",
         "hp_bonus": 224, "atk_bonus": 160, "def_bonus": 64},
    ],
    "Espectro": [
        {"level": 30,  "name": "Espectro Sombrio",    "emoji": "👻🌑", "suffix": " Sombrio",
         "lore": "Você dominou a fronteira entre os planos. Seus ataques atravessam até armaduras mágicas.",
         "hp_bonus": 10, "atk_bonus": 56, "def_bonus": 8},
        {"level": 70,  "name": "Espectro Eterno",     "emoji": "👻💀", "suffix": " Eterno",
         "lore": "Nem o tempo nem a morte te alcançam mais. Você simplesmente existe — para sempre.",
         "hp_bonus": 20, "atk_bonus": 112, "def_bonus": 16},
        {"level": 130, "name": "Espectro Primordial", "emoji": "👻👑", "suffix": " Primordial",
         "lore": "Você é o eco de uma era anterior ao mundo. Sua existência dobra a realidade.",
         "hp_bonus": 40, "atk_bonus": 224, "def_bonus": 32},
    ],
    "Golem": [
        {"level": 30,  "name": "Golem de Aço",        "emoji": "🗿⚙️", "suffix": " de Aço",
         "lore": "Você absorveu metal puro em sua estrutura. Agora você é uma fortaleza ambulante.",
         "hp_bonus": 120, "atk_bonus": 20, "def_bonus": 60},
        {"level": 70,  "name": "Golem Arcano",        "emoji": "🗿🔮", "suffix": " Arcano",
         "lore": "Runa mágicas foram gravadas em sua pedra. Você conduz magia através de seu próprio corpo.",
         "hp_bonus": 240, "atk_bonus": 40, "def_bonus": 120},
        {"level": 130, "name": "Golem Primordial",    "emoji": "🗿👑", "suffix": " Primordial",
         "lore": "Você é a pedra mais antiga do mundo. Nem deuses conseguem arranhar sua superfície.",
         "hp_bonus": 480, "atk_bonus": 80, "def_bonus": 240},
    ],
    "Sereia": [
        {"level": 30,  "name": "Sereia das Profundezas","emoji": "🧜🌊", "suffix": " das Profundezas",
         "lore": "Você dominou as correntes abissais. Sua voz ressoa em todos os oceanos.",
         "hp_bonus": 28, "atk_bonus": 32, "def_bonus": 20},
        {"level": 70,  "name": "Rainha do Mar",       "emoji": "🧜👑", "suffix": " Rainha",
         "lore": "Os oceanos te obedecem. Criaturas marinhas caem de joelhos ante sua presença.",
         "hp_bonus": 56, "atk_bonus": 64, "def_bonus": 40},
        {"level": 130, "name": "Sereia Primordial",   "emoji": "🧜💎", "suffix": " Primordial",
         "lore": "Você é mais velha que os oceanos. O mar não te criou — você criou o mar.",
         "hp_bonus": 112, "atk_bonus": 128, "def_bonus": 80},
    ],
    "Titã": [
        {"level": 30,  "name": "Titã Guerreiro",      "emoji": "🏔️⚔️", "suffix": " Guerreiro",
         "lore": "Seu tamanho e força atingiram proporcoes míticas. Exércitos inteiros fogem.",
         "hp_bonus": 100, "atk_bonus": 50, "def_bonus": 30},
        {"level": 70,  "name": "Titã Ancião",         "emoji": "🏔️🌟", "suffix": " Ancião",
         "lore": "Você viveu mais do que civilizações. Sua sabedoria e força rivalizam com deuses.",
         "hp_bonus": 200, "atk_bonus": 100, "def_bonus": 60},
        {"level": 130, "name": "Titã Primordial",     "emoji": "🏔️👑", "suffix": " Primordial",
         "lore": "Você é um dos primeiros seres criados pelo universo. Sua existência move montanhas.",
         "hp_bonus": 400, "atk_bonus": 200, "def_bonus": 120},
    ],
    "Fada": [
        {"level": 30,  "name": "Fada Encantada",      "emoji": "🧚✨", "suffix": " Encantada",
         "lore": "Sua magia se tornou impossível de ignorar. Você distorce a sorte ao seu redor.",
         "hp_bonus": 16, "atk_bonus": 24, "def_bonus": 12},
        {"level": 70,  "name": "Fada Mística",        "emoji": "🧚🌟", "suffix": " Mística",
         "lore": "Você é uma anomalia da sorte. Coisas impossíveis acontecem ao seu favor.",
         "hp_bonus": 32, "atk_bonus": 48, "def_bonus": 24},
        {"level": 130, "name": "Rainha das Fadas",    "emoji": "🧚👑", "suffix": " Rainha",
         "lore": "Você governa o primeiro jardim do mundo. Toda a magia de sorte emana de você.",
         "hp_bonus": 64, "atk_bonus": 96, "def_bonus": 48},
    ],
    "Elementário": [
        {"level": 30,  "name": "Elementário Puro",    "emoji": "🌀🔥", "suffix": " Puro",
         "lore": "Você não alterna mais — você domina todos os elementos simultaneamente.",
         "hp_bonus": 40, "atk_bonus": 40, "def_bonus": 20},
        {"level": 70,  "name": "Elementário Mestre",  "emoji": "🌀⚡", "suffix": " Mestre",
         "lore": "Os elementos te obedecem. Fogo, gelo e raio respondem ao seu pensamento.",
         "hp_bonus": 80, "atk_bonus": 80, "def_bonus": 40},
        {"level": 130, "name": "Elementário Primordial","emoji": "🌀👑", "suffix": " Primordial",
         "lore": "Você É os elementos. Você não usa magia — você é a magia em sua forma mais pura.",
         "hp_bonus": 160, "atk_bonus": 160, "def_bonus": 80},
    ],
    "Goblin": [
        {"level": 30,  "name": "Goblin Mestre",       "emoji": "👺💰", "suffix": " Mestre",
         "lore": "Sua astúcia ultrapassou qualquer goblin comum. O ouro te encontra antes de você o procurar.",
         "hp_bonus": 20, "atk_bonus": 30, "def_bonus": 10},
        {"level": 70,  "name": "Goblin Lendário",     "emoji": "👺👑", "suffix": " Lendário",
         "lore": "Sua riqueza e influência tornaram-se lendárias. Reinos inteiros devem favores a você.",
         "hp_bonus": 40, "atk_bonus": 60, "def_bonus": 20},
        {"level": 130, "name": "Rei Goblin",          "emoji": "👺💎", "suffix": " Rei",
         "lore": "Você é o rei absoluto dos goblins. Sua ganância moldou impérios.",
         "hp_bonus": 80, "atk_bonus": 120, "def_bonus": 40},
    ],
    "Gnomo": [
        {"level": 30,  "name": "Gnomo Inventor",      "emoji": "🔧⚙️", "suffix": " Inventor",
         "lore": "Suas criações desafiam as leis da física. Engenharia virou arte em suas mãos.",
         "hp_bonus": 24, "atk_bonus": 28, "def_bonus": 28},
        {"level": 70,  "name": "Gnomo Arcano",        "emoji": "🔧🔮", "suffix": " Arcano",
         "lore": "Você fundiu magia e engenharia. Suas máquinas funcionam com energia pura do cosmos.",
         "hp_bonus": 48, "atk_bonus": 56, "def_bonus": 56},
        {"level": 130, "name": "Grande Gnomo",        "emoji": "🔧👑", "suffix": " Grande",
         "lore": "Você é a mente mais brilhante já criada. Suas invenções moldaram o curso da história.",
         "hp_bonus": 96, "atk_bonus": 112, "def_bonus": 112},
    ],
    "Ciclope": [
        {"level": 30,  "name": "Ciclope Guerreiro",   "emoji": "👁️⚔️", "suffix": " Guerreiro",
         "lore": "Seu olho único vê através de ilusões, armaduras e até o tempo. Nada escapa.",
         "hp_bonus": 90, "atk_bonus": 60, "def_bonus": 10},
        {"level": 70,  "name": "Ciclope Ancião",      "emoji": "👁️🌟", "suffix": " Ancião",
         "lore": "Você guarda dois segredos do universo agora. Seu olho vê coisas que não deveriam existir.",
         "hp_bonus": 180, "atk_bonus": 120, "def_bonus": 20},
        {"level": 130, "name": "Ciclope Primordial",  "emoji": "👁️👑", "suffix": " Primordial",
         "lore": "Você guarda o segredo da criação. Seu olho viu o nascimento do universo.",
         "hp_bonus": 360, "atk_bonus": 240, "def_bonus": 40},
    ],
    "Sombra": [
        {"level": 30,  "name": "Sombra Viva",         "emoji": "🌑⚡", "suffix": " Viva",
         "lore": "Você não habita as sombras — você é a sombra. Luz alguma te revela.",
         "hp_bonus": 16, "atk_bonus": 52, "def_bonus": 12},
        {"level": 70,  "name": "Sombra Eterna",       "emoji": "🌑💀", "suffix": " Eterna",
         "lore": "Você existirá enquanto houver ausência de luz. O vazio te alimenta.",
         "hp_bonus": 32, "atk_bonus": 104, "def_bonus": 24},
        {"level": 130, "name": "Sombra Primordial",   "emoji": "🌑👑", "suffix": " Primordial",
         "lore": "Você era a escuridão antes do primeiro raio de luz. Você viu o universo nascer — do seu interior.",
         "hp_bonus": 64, "atk_bonus": 208, "def_bonus": 48},
    ],
    "Ancião": [
        {"level": 30,  "name": "Ancião Sábio",        "emoji": "🧙📚", "suffix": " Sábio",
         "lore": "Sua sabedoria transcendeu o aprendizado. Você não busca conhecimento — ele te encontra.",
         "hp_bonus": 30, "atk_bonus": 30, "def_bonus": 30},
        {"level": 70,  "name": "Ancião Eterno",       "emoji": "🧙⭐", "suffix": " Eterno",
         "lore": "Você viveu mais vidas do que a maioria existiu. Cada ciclo te tornou mais poderoso.",
         "hp_bonus": 60, "atk_bonus": 60, "def_bonus": 60},
        {"level": 130, "name": "Ancião Primordial",   "emoji": "🧙👑", "suffix": " Primordial",
         "lore": "Você é mais velho que o próprio universo. Sua existência é a resposta que todos buscam.",
         "hp_bonus": 120, "atk_bonus": 120, "def_bonus": 120},
    ],
}

def get_race_evolution_stage(race_name, player_level):
    """Retorna o estágio de evolução atual da raça (0=base, 1/2/3=evoluída)"""
    evos = RACE_EVOLUTION_TREE.get(race_name, [])
    stage = 0
    for i, evo in enumerate(evos):
        if player_level >= evo["level"]:
            stage = i + 1
    return stage

def get_race_current_data(race_name, stage):
    """Retorna os dados da raça no estágio informado"""
    if stage == 0:
        return RACES.get(race_name)
    evos = RACE_EVOLUTION_TREE.get(race_name, [])
    if stage <= len(evos):
        evo = evos[stage - 1]
        base = RACES.get(race_name, {})
        return {
            **base,
            "name": evo["name"],
            "emoji": evo["emoji"],
            "hp_bonus": evo["hp_bonus"],
            "atk_bonus": evo["atk_bonus"],
            "def_bonus": evo["def_bonus"],
            "lore": evo["lore"],
        }
    return RACES.get(race_name)


# ================= 20 NOVAS CLASSES =================
NEW_CLASSES = {
    "Cavaleiro das Sombras": {
        "emoji": "🌑",
        "hp_bonus": 28,
        "atk_bonus": 20,
        "def_bonus": 12,
        "description": "Guerreiro das trevas que combina força bruta e magia sombria.",
        "race_affinity": ["Sombra", "Vampiro", "Demônio"],
    },
    "Invocador": {
        "emoji": "🌀",
        "hp_bonus": 12,
        "atk_bonus": 22,
        "def_bonus": 8,
        "description": "Conjura criaturas de outros planos para lutar em seu lugar.",
        "race_affinity": ["Elementário", "Anjo", "Espectro"],
    },
    "Runesmith": {
        "emoji": "🔣",
        "hp_bonus": 16,
        "atk_bonus": 18,
        "def_bonus": 16,
        "description": "Grava runas em armas e armaduras para potencializar seus efeitos.",
        "race_affinity": ["Gnomo", "Anão", "Humano"],
    },
    "Cazador de Recompensas": {
        "emoji": "🎯",
        "hp_bonus": 18,
        "atk_bonus": 24,
        "def_bonus": 8,
        "description": "Especialista em rastrear e eliminar alvos específicos.",
        "race_affinity": ["Humano", "Élfico", "Goblin"],
    },
    "Xamã": {
        "emoji": "🪶",
        "hp_bonus": 20,
        "atk_bonus": 14,
        "def_bonus": 14,
        "description": "Canaliza os espíritos ancestrais para curar, amaldiçoar e destruir.",
        "race_affinity": ["Lobisomem", "Orc", "Titã"],
    },
    "Tempesteiro": {
        "emoji": "⛈️",
        "hp_bonus": 12,
        "atk_bonus": 28,
        "def_bonus": 5,
        "description": "Controla raios e tempestades com poder devastador.",
        "race_affinity": ["Elementário", "Dragônico", "Titã"],
    },
    "Ilusionista": {
        "emoji": "🪄",
        "hp_bonus": 10,
        "atk_bonus": 20,
        "def_bonus": 10,
        "description": "Cria ilusões para confundir e destruir inimigos.",
        "race_affinity": ["Fada", "Espectro", "Sereia"],
    },
    "Alquimista": {
        "emoji": "⚗️",
        "hp_bonus": 14,
        "atk_bonus": 16,
        "def_bonus": 12,
        "description": "Transforma elementos em poderosas poções e bombas.",
        "race_affinity": ["Gnomo", "Goblin", "Humano"],
    },
    "Guardião do Abismo": {
        "emoji": "♾️",
        "hp_bonus": 22,
        "atk_bonus": 22,
        "def_bonus": 10,
        "description": "Canaliza o poder do Abismo Arcano para aniquilar inimigos.",
        "race_affinity": ["Espectro", "Demônio", "Sombra"],
    },
    "Dançarino da Morte": {
        "emoji": "💃",
        "hp_bonus": 10,
        "atk_bonus": 26,
        "def_bonus": 6,
        "description": "Combina dança e lâminas em movimentos letais e imprevisíveis.",
        "race_affinity": ["Vampiro", "Sombra", "Élfico"],
    },
    "Oráculo": {
        "emoji": "🔮",
        "hp_bonus": 8,
        "atk_bonus": 18,
        "def_bonus": 8,
        "description": "Vê o futuro e manipula o destino dos inimigos.",
        "race_affinity": ["Ancião", "Fada", "Anjo"],
    },
    "Colossus": {
        "emoji": "🗿",
        "hp_bonus": 55,
        "atk_bonus": 18,
        "def_bonus": 25,
        "description": "Corpo transformado em fortaleza viva — quase indestrutível.",
        "race_affinity": ["Golem", "Titã", "Orc"],
    },
    "Devorador de Almas": {
        "emoji": "💫",
        "hp_bonus": 14,
        "atk_bonus": 30,
        "def_bonus": 5,
        "description": "Consome as almas dos inimigos para ganhar poder crescente.",
        "race_affinity": ["Demônio", "Vampiro", "Lobisomem"],
    },
    "Arauto Celestial": {
        "emoji": "✨",
        "hp_bonus": 20,
        "atk_bonus": 16,
        "def_bonus": 18,
        "description": "Mensageiro dos deuses, combina cura divina e golpes sagrados.",
        "race_affinity": ["Anjo", "Humano", "Élfico"],
    },
    "Lançador de Venenos": {
        "emoji": "☠️",
        "hp_bonus": 12,
        "atk_bonus": 22,
        "def_bonus": 8,
        "description": "Especialista em venenos, doenças e debuffs devastadores.",
        "race_affinity": ["Goblin", "Vampiro", "Dragônico"],
    },
    "Gladiador": {
        "emoji": "🏟️",
        "hp_bonus": 32,
        "atk_bonus": 22,
        "def_bonus": 8,
        "description": "Combatente de arena, quanto mais mata mais forte fica.",
        "race_affinity": ["Orc", "Humano", "Ciclope"],
    },
    "Mestre das Correntes": {
        "emoji": "⛓️",
        "hp_bonus": 20,
        "atk_bonus": 20,
        "def_bonus": 12,
        "description": "Usa correntes de energia para prender e devastar inimigos.",
        "race_affinity": ["Golem", "Anão", "Titã"],
    },
    "Profeta da Destruição": {
        "emoji": "📯",
        "hp_bonus": 10,
        "atk_bonus": 25,
        "def_bonus": 8,
        "description": "Prediz e causa calamidades. Seus feitiços se tornam realidade.",
        "race_affinity": ["Ancião", "Demônio", "Espectro"],
    },
    "Ferreiro de Guerra": {
        "emoji": "🔨",
        "hp_bonus": 25,
        "atk_bonus": 20,
        "def_bonus": 20,
        "description": "Forja equipamentos durante batalha, melhorando armas e armaduras em tempo real.",
        "race_affinity": ["Anão", "Gnomo", "Golem"],
    },
    "Dragonlancer": {
        "emoji": "🐲",
        "hp_bonus": 24,
        "atk_bonus": 28,
        "def_bonus": 10,
        "description": "Cavaleiro dracônico que monta dragões e usa lança de fogo.",
        "race_affinity": ["Dragônico", "Humano", "Titã"],
    },
}

# Merge NEW_CLASSES into CLASSES
CLASSES.update(NEW_CLASSES)

# ================= SISTEMA DE RAÇAS =================
# Adicionado ao perfil do jogador como player["race"]

# ================= ÁRVORES DE EVOLUÇÃO DE CLASSE =================
# Cada classe pode evoluir nos níveis 40, 80, 120 e 160
# Ao evoluir, o jogador escolhe uma especialização
CLASS_EVOLUTION_TREE = {
    # ── CLASSES ORIGINAIS ──────────────────────────────────────────
    "Guerreiro": {
        40:  {"name": "Guerreiro Elite",     "spec_options": ["Campeão", "Guardião Inabalável"]},
        80:  {"name": "Lorde da Guerra",     "spec_options": ["Berserker Sagrado", "Comandante Tático"]},
        120: {"name": "Titan da Batalha",    "spec_options": ["Avatar da Guerra", "Senhor dos Exércitos"]},
        160: {"name": "Imperador Guerreiro", "spec_options": ["Deus da Guerra Mortal", "Lenda Imortal"]},
    },
    "Mago": {
        40:  {"name": "Arcano Iniciado",   "spec_options": ["Piromante", "Criomante"]},
        80:  {"name": "Arquimago",         "spec_options": ["Mago do Caos", "Conjurador Estelar"]},
        120: {"name": "Sábio Eterno",      "spec_options": ["Deus Arcano", "Tecedor da Realidade"]},
        160: {"name": "Transcendente",     "spec_options": ["Onisciente do Cosmos", "Destruidor de Planos"]},
    },
    "Arqueiro": {
        40:  {"name": "Atirador de Elite",   "spec_options": ["Caçador Sombrio", "Arqueiro da Tempestade"]},
        80:  {"name": "Mestre dos Arcos",    "spec_options": ["Atirador Fantasma", "Arqueiro Divino"]},
        120: {"name": "Lenda do Arco",       "spec_options": ["Caçador de Deuses", "Vendaval de Flechas"]},
        160: {"name": "Flecha Primordial",   "spec_options": ["Atirador do Fim dos Tempos", "Sombra Alada"]},
    },
    "Paladino": {
        40:  {"name": "Cavaleiro Sagrado",   "spec_options": ["Cruzado", "Sentinela Divina"]},
        80:  {"name": "Arauto da Luz",       "spec_options": ["Campeão Celestial", "Protetor Eterno"]},
        120: {"name": "Lorde Sagrado",       "spec_options": ["Avatar Divino", "Juiz dos Deuses"]},
        160: {"name": "Divindade Encarnada", "spec_options": ["Santo Guerreiro", "Escudo do Universo"]},
    },
    "Assassino": {
        40:  {"name": "Phantom Blade",     "spec_options": ["Mestre das Sombras", "Envenenador Letal"]},
        80:  {"name": "Sombra Absoluta",   "spec_options": ["Caçador Dimensional", "Executor Supremo"]},
        120: {"name": "Espectro Mortal",   "spec_options": ["Sombra do Abismo", "Dançarino da Morte Noir"]},
        160: {"name": "Void Walker",       "spec_options": ["Ceifador do Vazio", "Aniquilador Silencioso"]},
    },
    "Necromante": {
        40:  {"name": "Mestre dos Mortos",   "spec_options": ["Invocador Sombrio", "Lich Aprendiz"]},
        80:  {"name": "Lorde dos Não-Mortos","spec_options": ["Lich Verdadeiro", "Senhor das Almas"]},
        120: {"name": "Soberano Eterno",     "spec_options": ["Deus Morto-Vivo", "Destruidor de Almas"]},
        160: {"name": "Lich Primordial",     "spec_options": ["Rei da Morte Eterna", "Corrompedor do Cosmos"]},
    },
    "Berserker": {
        40:  {"name": "Bárbaro Sangrento",   "spec_options": ["Carnificina", "Orc-Sangue"]},
        80:  {"name": "Destruidor",          "spec_options": ["Avatar da Fúria", "Berserker Divino"]},
        120: {"name": "Flagelo Vivo",        "spec_options": ["Destruidor de Mundos", "Cataclismo Ambulante"]},
        160: {"name": "Fúria Primordial",    "spec_options": ["Ira dos Titãs", "Apocalipse em Forma"]},
    },
    "Druida": {
        40:  {"name": "Guardião da Floresta","spec_options": ["Metamorfo", "Druida Lunar"]},
        80:  {"name": "Ancião da Natureza",  "spec_options": ["Druida do Caos", "Guardião Primordial"]},
        120: {"name": "Espírito da Terra",   "spec_options": ["Avatar da Natureza", "Ent Vivente"]},
        160: {"name": "Gaia Encarnada",      "spec_options": ["A Própria Floresta", "Senhor das Bestas Eternas"]},
    },
    "Monge": {
        40:  {"name": "Mestre do Ki",         "spec_options": ["Punho de Aço", "Monge do Vento"]},
        80:  {"name": "Mestre Supremo",       "spec_options": ["Monge Celestial", "Fúria Controlada"]},
        120: {"name": "Iluminado",            "spec_options": ["Monge Transcendente", "Dançarino do Ki"]},
        160: {"name": "Além do Mortal",       "spec_options": ["Ki Primordial", "Vazio em Movimento"]},
    },
    "Bardo": {
        40:  {"name": "Maestro",            "spec_options": ["Bardo da Batalha", "Encantador Supremo"]},
        80:  {"name": "Lenda Viva",         "spec_options": ["Bardo do Destino", "Cantor dos Deuses"]},
        120: {"name": "Voz do Cosmos",      "spec_options": ["Sinfonia da Destruição", "Música do Universo"]},
        160: {"name": "A Canção Eterna",    "spec_options": ["Compositor do Fim", "Eco Primordial"]},
    },
    # ── NOVAS CLASSES ──────────────────────────────────────────────
    "Cavaleiro das Sombras": {
        40:  {"name": "Lorde das Sombras",     "spec_options": ["Cavaleiro do Vazio", "Sombra Armada"]},
        80:  {"name": "Guardião Sombrio",      "spec_options": ["Dragão das Trevas", "Fantasma de Aço"]},
        120: {"name": "Soberano das Trevas",   "spec_options": ["Lich Cavaleiro", "Sombra Imortal"]},
        160: {"name": "Abismo Encarnado",      "spec_options": ["Ceifeiro das Sombras", "Vazio Armado"]},
    },
    "Invocador": {
        40:  {"name": "Senhor das Criaturas",  "spec_options": ["Invocador Elemental", "Portão do Abismo"]},
        80:  {"name": "Mestre dos Planos",     "spec_options": ["Invocador Divino", "Abridor de Portais"]},
        120: {"name": "Soberano das Dimensões","spec_options": ["Senhor das Legiões", "Tecedor de Planos"]},
        160: {"name": "Criador de Mundos",     "spec_options": ["Pai das Criaturas", "Nexo Dimensional"]},
    },
    "Runesmith": {
        40:  {"name": "Gravador de Runas",     "spec_options": ["Runesmith de Batalha", "Arquiteto de Runas"]},
        80:  {"name": "Mestre das Runas",      "spec_options": ["Runas Proibidas", "Construtor Arcano"]},
        120: {"name": "Runa Viva",             "spec_options": ["Avatar das Runas", "Runas Primordiais"]},
        160: {"name": "A Primeira Runa",       "spec_options": ["Origem do Poder", "Runa do Fim"]},
    },
    "Cazador de Recompensas": {
        40:  {"name": "Caçador Lendário",      "spec_options": ["Sniper Arcano", "Caçador de Monstros"]},
        80:  {"name": "Caçador de Bosses",     "spec_options": ["Exterminador Elite", "Sombra Caçadora"]},
        120: {"name": "Lenda da Caça",         "spec_options": ["Caçador de Deuses", "Predador Supremo"]},
        160: {"name": "O Último Caçador",      "spec_options": ["Fim de Tudo", "Caçador Imortal"]},
    },
    "Xamã": {
        40:  {"name": "Guardião Espiritual",   "spec_options": ["Xamã de Guerra", "Curandeiro dos Espíritos"]},
        80:  {"name": "Ancestral Vivo",        "spec_options": ["Xamã do Caos", "Portador dos Ancestrais"]},
        120: {"name": "Espírito Encarnado",    "spec_options": ["Espírito da Destruição", "Ancião dos Espíritos"]},
        160: {"name": "Pai dos Espíritos",     "spec_options": ["Espírito Primordial", "Voz dos Mortos"]},
    },
    "Tempesteiro": {
        40:  {"name": "Senhor do Trovão",      "spec_options": ["Tempesteiro de Plasma", "Deus do Raio"]},
        80:  {"name": "Tempestade Viva",       "spec_options": ["Furacão Arcano", "Relâmpago Encarnado"]},
        120: {"name": "Olho da Tempestade",    "spec_options": ["Tempesteiro Divino", "Zeus Menor"]},
        160: {"name": "A Tempestade Eterna",   "spec_options": ["Armageddon Elétrico", "Tempestade Primordial"]},
    },
    "Ilusionista": {
        40:  {"name": "Mestre das Ilusões",    "spec_options": ["Ilusionista de Batalha", "Sonhador Arcano"]},
        80:  {"name": "Arquiteto de Sonhos",   "spec_options": ["Senhor dos Pesadelos", "Criador de Realidades"]},
        120: {"name": "Realidade Alternativa", "spec_options": ["Deus das Ilusões", "Espelho do Cosmos"]},
        160: {"name": "A Ilusão Suprema",      "spec_options": ["Realidade que Mente", "Ilusionista Primordial"]},
    },
    "Alquimista": {
        40:  {"name": "Alquimista de Elite",   "spec_options": ["Bombardeiro", "Alquimista Curador"]},
        80:  {"name": "Mestre Alquimista",     "spec_options": ["Transmutador", "Fabricante do Caos"]},
        120: {"name": "Grão-Alquimista",       "spec_options": ["Pedra Filosofal Viva", "Alquimista Divino"]},
        160: {"name": "Primeiro Alquimista",   "spec_options": ["Criador da Vida", "Destruidor da Matéria"]},
    },
    "Guardião do Abismo": {
        40:  {"name": "Sentinela do Vazio",    "spec_options": ["Guardião das Almas", "Soldado do Abismo"]},
        80:  {"name": "Lorde do Abismo",       "spec_options": ["Entidade do Vazio", "Comandante das Sombras"]},
        120: {"name": "Soberano do Nada",      "spec_options": ["Avatar do Abismo", "Guardião Eterno"]},
        160: {"name": "O Abismo em Pessoa",    "spec_options": ["Vazio Primordial", "O Nada que Destrói"]},
    },
    "Dançarino da Morte": {
        40:  {"name": "Executora da Sombra",   "spec_options": ["Lâminas do Vento", "Dança Mortal"]},
        80:  {"name": "Ceifadora Elegante",    "spec_options": ["Fantasma Dançante", "Morte Personificada"]},
        120: {"name": "Dança do Apocalipse",   "spec_options": ["Última Dança", "Ceifadora do Cosmos"]},
        160: {"name": "A Morte Dança",         "spec_options": ["Fim do Mundo Bailado", "Extinção Graciosa"]},
    },
    "Oráculo": {
        40:  {"name": "Vidente do Destino",    "spec_options": ["Oráculo de Batalha", "Manipulador do Tempo"]},
        80:  {"name": "Profeta dos Deuses",    "spec_options": ["Reescritor do Destino", "Senhor do Futuro"]},
        120: {"name": "Olho do Cosmos",        "spec_options": ["Onisciente", "Paradoxo Vivo"]},
        160: {"name": "O Destino em Pessoa",   "spec_options": ["Fim Predestinado", "Tecedor do Cosmos"]},
    },
    "Colossus": {
        40:  {"name": "Fortaleza Viva",        "spec_options": ["Titan da Defesa", "Colosso de Batalha"]},
        80:  {"name": "Muralha Inquebrável",   "spec_options": ["Monolito Eterno", "Colosso Sagrado"]},
        120: {"name": "Fundação do Mundo",     "spec_options": ["Rocha Primordial", "Colossus Divino"]},
        160: {"name": "A Montanha Que Caminha","spec_options": ["Continente Animado", "Titã Imortal"]},
    },
    "Devorador de Almas": {
        40:  {"name": "Colecionador de Almas", "spec_options": ["Devorador de Guerreiros", "Absorvedor Eterno"]},
        80:  {"name": "Ladrão de Essências",   "spec_options": ["Devorador de Deuses", "Vazio Faminto"]},
        120: {"name": "O Vazio Faminto",       "spec_options": ["Consumidor de Realidades", "Fome Eterna"]},
        160: {"name": "Devor. do Universo",    "spec_options": ["Fim de Toda Existência", "O Vácuo Primordial"]},
    },
    "Arauto Celestial": {
        40:  {"name": "Mensageiro dos Deuses", "spec_options": ["Arauto da Luz", "Protetor Divino"]},
        80:  {"name": "Voz do Trono",          "spec_options": ["Arauto da Destruição", "Escudo dos Céus"]},
        120: {"name": "Avatar Celestial",      "spec_options": ["Braço dos Deuses", "Sentença Divina"]},
        160: {"name": "Deus Mensageiro",       "spec_options": ["Vontade do Cosmos", "Portador do Fim"]},
    },
    "Lançador de Venenos": {
        40:  {"name": "Mestre das Toxinas",    "spec_options": ["Envenenador Supremo", "Corrosivo Letal"]},
        80:  {"name": "Senhor das Pragas",     "spec_options": ["Praga Viva", "Destruidor Silencioso"]},
        120: {"name": "Catalisador da Morte",  "spec_options": ["Pandemia Personificada", "Toxina Primordial"]},
        160: {"name": "A Praga Final",         "spec_options": ["Extintor de Mundos", "Veneno do Cosmos"]},
    },
    "Gladiador": {
        40:  {"name": "Campeão da Arena",      "spec_options": ["Gladiador Impiedoso", "Gladiador Protetor"]},
        80:  {"name": "Lenda da Arena",        "spec_options": ["Gladiador Divino", "Mestre do Espetáculo"]},
        120: {"name": "Senhor dos Combates",   "spec_options": ["Invicto Eterno", "Arena Personificada"]},
        160: {"name": "Gladiador Imortal",     "spec_options": ["O Último em Pé", "Combate Primordial"]},
    },
    "Mestre das Correntes": {
        40:  {"name": "Aprisionador",          "spec_options": ["Correntes de Fogo", "Correntes do Abismo"]},
        80:  {"name": "Controlador Supremo",   "spec_options": ["Correntes da Realidade", "Aprisionador Eterno"]},
        120: {"name": "Deus das Correntes",    "spec_options": ["Correntes Primordiais", "Ligação do Cosmos"]},
        160: {"name": "Corrente do Universo",  "spec_options": ["Tudo Acorrentado", "Fim da Liberdade"]},
    },
    "Profeta da Destruição": {
        40:  {"name": "Anunciador do Caos",    "spec_options": ["Profeta do Fogo", "Voz do Abismo"]},
        80:  {"name": "Catalisador do Fim",    "spec_options": ["Profeta Demoníaco", "Anunciador do Juízo"]},
        120: {"name": "A Profecia em Pessoa",  "spec_options": ["Destruição Inevitável", "Profeta do Cosmos"]},
        160: {"name": "O Fim Anunciado",       "spec_options": ["Apocalipse Ambulante", "Profecia Primordial"]},
    },
    "Ferreiro de Guerra": {
        40:  {"name": "Armeiro de Batalha",    "spec_options": ["Ferreiro Divino", "Construtor de Lendas"]},
        80:  {"name": "Forjador de Heróis",    "spec_options": ["Mestre da Forja Sagrada", "Armeiro Eterno"]},
        120: {"name": "Forjador de Deuses",    "spec_options": ["Criador de Armas Divinas", "Ferreiro Primordial"]},
        160: {"name": "A Primeira Forja",      "spec_options": ["Forja do Cosmos", "Armeiro do Universo"]},
    },
    "Dragonlancer": {
        40:  {"name": "Cavaleiro de Dragão",   "spec_options": ["Lançador de Chamas", "Cavaleiro do Gelo"]},
        80:  {"name": "Senhor dos Dragões",    "spec_options": ["Avatar Dracônico", "Dragonlord"]},
        120: {"name": "Dragão Encarnado",      "spec_options": ["Forma Final do Dragão", "Último Dragão"]},
        160: {"name": "Dragão Primordial",     "spec_options": ["Pai dos Dragões", "Chama da Criação"]},
    },
}

# ================= HABILIDADES POR TIER DE EVOLUÇÃO =================
# basic=nível 1-39, intermediate=40-79, advanced=80-119, supreme=desbloqueada por boss
CLASS_TIERED_SKILLS = {
    # ── GUERREIRO ──────────────────────────────────────────────────
    "Guerreiro": {
        "basic": [
            {"name": "🗡️ Golpe Devastador",  "mana_cost": 0,  "dmg_mult": 1.4, "desc": "Um golpe poderoso com toda a força!"},
            {"name": "🛡️ Ataque Protetor",   "mana_cost": 10, "dmg_mult": 1.2, "def_bonus": 10, "desc": "Ataca enquanto se defende."},
        ],
        "intermediate": [
            {"name": "⚔️ Fúria do Guerreiro", "mana_cost": 20, "dmg_mult": 1.8, "desc": "Rajada de golpes furiosos!"},
            {"name": "🔥 Grito de Batalha",   "mana_cost": 15, "dmg_mult": 1.5, "stun_chance": 0.2, "desc": "Paralisa o inimigo."},
            {"name": "💪 Postura do Titã",    "mana_cost": 25, "dmg_mult": 1.3, "def_bonus": 25, "self_heal": 20, "desc": "Postura defensiva que também cura."},
        ],
        "advanced": [
            {"name": "🌪️ Redemoinho de Aço", "mana_cost": 35, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Gira causando dano em área!"},
            {"name": "🩸 Golpe do Colosso",  "mana_cost": 45, "dmg_mult": 2.8, "ignore_def": True, "desc": "Força dos titãs em um golpe!"},
        ],
        "supreme": {
            "name": "☠️ Aniquilação Total", "mana_cost": 80, "dmg_mult": 5.0, "stun_chance": 0.5, "ignore_def": True,
            "desc": "O poder de um deus mortal. Destrói qualquer defesa!",
            "unlock_boss": "Yeti Colossal"
        },
    },
    # ── MAGO ───────────────────────────────────────────────────────
    "Mago": {
        "basic": [
            {"name": "🔥 Bola de Fogo",      "mana_cost": 25, "dmg_mult": 2.0, "desc": "Uma esfera flamejante!"},
            {"name": "❄️ Toque Gelado",      "mana_cost": 20, "dmg_mult": 1.6, "slow_chance": 0.4, "desc": "Congela o adversário."},
        ],
        "intermediate": [
            {"name": "⚡ Relâmpago Arcano",  "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Eletricidade arcana!"},
            {"name": "🌀 Explosão do Vazio", "mana_cost": 40, "dmg_mult": 2.8, "desc": "Poder do abismo!"},
            {"name": "🌌 Chuva de Meteoros", "mana_cost": 50, "dmg_mult": 2.5, "poison": True, "desc": "Meteoros arcanos caem!"},
        ],
        "advanced": [
            {"name": "⭐ Colapso Estelar",   "mana_cost": 60, "dmg_mult": 3.5, "stun_chance": 0.4, "desc": "Estrelas colapsam no alvo!"},
            {"name": "💥 Singularidade",     "mana_cost": 70, "dmg_mult": 3.8, "ignore_def": True, "desc": "Buraco negro arcano!"},
        ],
        "supreme": {
            "name": "🌠 Extinção Arcana", "mana_cost": 100, "dmg_mult": 6.5, "ignore_def": True, "stun_chance": 0.6,
            "desc": "Destrói a realidade ao redor do alvo. O poder mais destrutivo da magia arcana!",
            "unlock_boss": "Olho do Abismo"
        },
    },
    # ── ARQUEIRO ───────────────────────────────────────────────────
    "Arqueiro": {
        "basic": [
            {"name": "🏹 Flecha Certeira",   "mana_cost": 0,  "dmg_mult": 1.5, "desc": "Flecha com precisão mortal."},
            {"name": "🌿 Flecha Envenenada", "mana_cost": 10, "dmg_mult": 1.3, "poison": True, "desc": "Veneno corrosivo."},
        ],
        "intermediate": [
            {"name": "💨 Chuva de Flechas",  "mana_cost": 20, "dmg_mult": 1.7, "desc": "Múltiplas flechas!"},
            {"name": "🎯 Tiro Perfurante",   "mana_cost": 15, "dmg_mult": 2.0, "ignore_def": True, "desc": "Perfura qualquer defesa."},
            {"name": "⚡ Flecha do Trovão",  "mana_cost": 25, "dmg_mult": 2.2, "stun_chance": 0.35, "desc": "Paralisa com raio."},
        ],
        "advanced": [
            {"name": "🌌 Flecha Cósmica",    "mana_cost": 35, "dmg_mult": 2.8, "ignore_def": True, "desc": "Flecha imbuída de energia estelar!"},
            {"name": "🔥 Inferno Balístico", "mana_cost": 45, "dmg_mult": 3.2, "poison": True, "stun_chance": 0.2, "desc": "Flechas de fogo infernal!"},
        ],
        "supreme": {
            "name": "🌠 A Última Flecha", "mana_cost": 90, "dmg_mult": 5.5, "ignore_def": True, "crit_chance": 0.8,
            "desc": "Uma única flecha que atravessa dimensões. Não falha. Nunca.",
            "unlock_boss": "Arquimago Zephyr Corrompido"
        },
    },
    # ── PALADINO ───────────────────────────────────────────────────
    "Paladino": {
        "basic": [
            {"name": "✨ Golpe Sagrado",     "mana_cost": 15, "dmg_mult": 1.6, "desc": "Energia divina!"},
            {"name": "🛡️ Escudo da Fé",     "mana_cost": 20, "dmg_mult": 1.0, "self_heal": 30, "desc": "Cura ao defender."},
        ],
        "intermediate": [
            {"name": "☀️ Julgamento Divino", "mana_cost": 35, "dmg_mult": 2.0, "desc": "Julgamento dos céus!"},
            {"name": "🌟 Aura de Proteção",  "mana_cost": 25, "dmg_mult": 1.2, "def_bonus": 20, "desc": "Aura protetora."},
            {"name": "🕊️ Bênção dos Anjos", "mana_cost": 30, "dmg_mult": 1.5, "self_heal": 40, "desc": "Cura massiva divina."},
        ],
        "advanced": [
            {"name": "⚡ Espada do Juízo",   "mana_cost": 50, "dmg_mult": 2.8, "ignore_def": True, "desc": "Espada forjada no céu!"},
            {"name": "🌈 Nova Sagrada",      "mana_cost": 55, "dmg_mult": 2.5, "self_heal": 60, "stun_chance": 0.3, "desc": "Explosão de luz divina!"},
        ],
        "supreme": {
            "name": "👑 Juízo Final Divino", "mana_cost": 95, "dmg_mult": 5.0, "self_heal": 100, "ignore_def": True,
            "desc": "O poder do Trono Celestial canalizado. Cura completamente e destrói o inimigo!",
            "unlock_boss": "Imperador Astral"
        },
    },
    # ── ASSASSINO ──────────────────────────────────────────────────
    "Assassino": {
        "basic": [
            {"name": "🗡️ Golpe Sorrateiro",  "mana_cost": 0,  "dmg_mult": 1.8, "crit_chance": 0.4, "desc": "Das sombras, golpe mortal!"},
            {"name": "☠️ Veneno Assassino",  "mana_cost": 15, "dmg_mult": 1.3, "poison": True, "desc": "Veneno letal."},
        ],
        "intermediate": [
            {"name": "💨 Dança das Lâminas", "mana_cost": 20, "dmg_mult": 1.5, "desc": "Sequência vertiginosa."},
            {"name": "🌑 Golpe das Sombras", "mana_cost": 30, "dmg_mult": 2.5, "crit_chance": 0.5, "desc": "Alta chance crítica!"},
            {"name": "🎭 Ilusão Mortal",     "mana_cost": 25, "dmg_mult": 2.2, "stun_chance": 0.4, "desc": "Ilude e golpeia."},
        ],
        "advanced": [
            {"name": "⚡ Tempestade de Lâminas","mana_cost": 40, "dmg_mult": 3.0, "crit_chance": 0.6, "desc": "Cem lâminas em um segundo!"},
            {"name": "🌀 Portal Sombrio",    "mana_cost": 45, "dmg_mult": 3.3, "ignore_def": True, "desc": "Aparece atrás do inimigo."},
        ],
        "supreme": {
            "name": "💀 Morte Certa", "mana_cost": 85, "dmg_mult": 6.0, "crit_chance": 0.9, "ignore_def": True, "poison": True,
            "desc": "Um golpe que não pode ser evitado. Veneno, crítico e ignora toda defesa.",
            "unlock_boss": "Senhor das Sombras"
        },
    },
    # ── NECROMANTE ─────────────────────────────────────────────────
    "Necromante": {
        "basic": [
            {"name": "💀 Dreno de Vida",    "mana_cost": 20, "dmg_mult": 1.5, "self_heal": 20, "desc": "Rouba HP!"},
            {"name": "🌑 Maldição Sombria", "mana_cost": 25, "dmg_mult": 1.4, "weaken": True, "desc": "Enfraquece o inimigo."},
        ],
        "intermediate": [
            {"name": "🦴 Invocar Esqueleto", "mana_cost": 30, "dmg_mult": 1.7, "desc": "Esqueleto guerreiro!"},
            {"name": "☠️ Morte Instantânea", "mana_cost": 50, "dmg_mult": 3.0, "desc": "Toca a morte!"},
            {"name": "🩸 Praga dos Mortos",  "mana_cost": 35, "dmg_mult": 1.8, "poison": True, "weaken": True, "desc": "Praga que drena e enfraquece."},
        ],
        "advanced": [
            {"name": "🌒 Exército Espectral","mana_cost": 55, "dmg_mult": 2.8, "self_heal": 50, "desc": "Horda de espectros ataca!"},
            {"name": "💀 Apocalipse Morto",  "mana_cost": 65, "dmg_mult": 3.5, "weaken": True, "poison": True, "desc": "A morte vem em ondas."},
        ],
        "supreme": {
            "name": "♾️ Extinction Protocol", "mana_cost": 100, "dmg_mult": 5.8, "self_heal": 80, "ignore_def": True, "weaken": True,
            "desc": "Convoca todos os mortos do campo de batalha. A morte absoluta.",
            "unlock_boss": "Rei das Sombras Eternas"
        },
    },
    # ── BERSERKER ──────────────────────────────────────────────────
    "Berserker": {
        "basic": [
            {"name": "🪓 Frenesi",           "mana_cost": 0,  "dmg_mult": 2.0, "desc": "Ataque frenético!"},
            {"name": "💢 Ira Incontrolável", "mana_cost": 15, "dmg_mult": 2.2, "self_dmg": 10, "desc": "Sacrifica HP por poder."},
        ],
        "intermediate": [
            {"name": "🩸 Sede de Sangue",    "mana_cost": 10, "dmg_mult": 1.8, "hp_scale": True, "desc": "Quanto menos HP, mais forte!"},
            {"name": "💥 Explosão de Fúria", "mana_cost": 25, "dmg_mult": 2.8, "desc": "Toda raiva liberada!"},
            {"name": "🔥 Fúria Sanguinária", "mana_cost": 20, "dmg_mult": 2.5, "self_dmg": 15, "stun_chance": 0.3, "desc": "Corre sangrando e paralisa."},
        ],
        "advanced": [
            {"name": "🌋 Terremoto",         "mana_cost": 40, "dmg_mult": 3.2, "stun_chance": 0.45, "desc": "Soca o chão rachando tudo!"},
            {"name": "💀 Modo Deus da Fúria", "mana_cost": 50, "dmg_mult": 3.8, "ignore_def": True, "desc": "Além do limite humano."},
        ],
        "supreme": {
            "name": "🌪️ Ragnarök Pessoal", "mana_cost": 70, "dmg_mult": 6.2, "ignore_def": True, "stun_chance": 0.5, "self_dmg": 30,
            "desc": "O fim do mundo concentrado em um único ser. Devastação total.",
            "unlock_boss": "Primeiro Gigante Primordial"
        },
    },
    # ── DRUIDA ─────────────────────────────────────────────────────
    "Druida": {
        "basic": [
            {"name": "🌿 Golpe Natural",     "mana_cost": 0,  "dmg_mult": 1.3, "self_heal": 15, "desc": "Natureza cura ao atacar."},
            {"name": "🌪️ Tempestade de Folhas","mana_cost": 20,"dmg_mult": 1.6, "desc": "Tempestade de espinhos!"},
        ],
        "intermediate": [
            {"name": "🐺 Fúria Animal",      "mana_cost": 30, "dmg_mult": 2.0, "desc": "Transforma-se em besta!"},
            {"name": "⚡ Trovão da Terra",   "mana_cost": 35, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "Terra responde com trovão!"},
            {"name": "🌊 Maré da Floresta",  "mana_cost": 30, "dmg_mult": 1.9, "self_heal": 35, "desc": "A floresta cura e destrói."},
        ],
        "advanced": [
            {"name": "🌳 Abraço do Ent",     "mana_cost": 45, "dmg_mult": 2.6, "stun_chance": 0.5, "desc": "Raízes gigantes prendem e esmagam!"},
            {"name": "🌏 Pulso da Terra",    "mana_cost": 55, "dmg_mult": 3.0, "self_heal": 50, "desc": "A própria terra ataca!"},
        ],
        "supreme": {
            "name": "🌌 Gaia's Wrath", "mana_cost": 90, "dmg_mult": 5.3, "self_heal": 120, "stun_chance": 0.4,
            "desc": "A raiva do planeta em forma de ataque. A natureza em seu estado mais puro e destrutivo.",
            "unlock_boss": "Ent Ancião"
        },
    },
    # ── MONGE ──────────────────────────────────────────────────────
    "Monge": {
        "basic": [
            {"name": "👊 Soco do Dragão",    "mana_cost": 0,  "dmg_mult": 1.5, "desc": "Soco carregado de ki!"},
            {"name": "🌀 Cem Golpes",        "mana_cost": 20, "dmg_mult": 1.7, "desc": "Cem golpes em um segundo!"},
        ],
        "intermediate": [
            {"name": "⚡ Raio de Ki",        "mana_cost": 25, "dmg_mult": 2.0, "desc": "Energia vital projetada!"},
            {"name": "🧘 Golpe Transcendente","mana_cost": 40,"dmg_mult": 2.5, "desc": "Corpo e mente em harmonia."},
            {"name": "🌊 Onda de Ki",        "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Onda de energia pura."},
        ],
        "advanced": [
            {"name": "💫 Explosão de Ki",    "mana_cost": 50, "dmg_mult": 3.2, "ignore_def": True, "desc": "Ki explode em todas as direções!"},
            {"name": "🌟 Modo Ultra-Ki",     "mana_cost": 60, "dmg_mult": 3.5, "stun_chance": 0.4, "desc": "Além do limite do ki mortal."},
        ],
        "supreme": {
            "name": "☯️ Transcendência Absoluta", "mana_cost": 85, "dmg_mult": 5.8, "ignore_def": True, "self_heal": 80,
            "desc": "A alma e o universo se tornam um. O golpe que existe além da física.",
            "unlock_boss": "Loop Temporal"
        },
    },
    # ── BARDO ──────────────────────────────────────────────────────
    "Bardo": {
        "basic": [
            {"name": "🎵 Nota Dissonante",   "mana_cost": 10, "dmg_mult": 1.3, "stun_chance": 0.3, "desc": "Nota que atordoa!"},
            {"name": "🎸 Acorde do Caos",    "mana_cost": 20, "dmg_mult": 1.6, "desc": "Confunde os sentidos."},
        ],
        "intermediate": [
            {"name": "🎺 Fanfarra da Ruína", "mana_cost": 15, "dmg_mult": 1.5, "weaken": True, "desc": "Enfraquece com música."},
            {"name": "🎻 Sinfonia da Destruição","mana_cost": 35,"dmg_mult": 2.2, "desc": "Música torna-se força!"},
            {"name": "🎹 Requiem do Inimigo", "mana_cost": 30, "dmg_mult": 2.0, "weaken": True, "stun_chance": 0.25, "desc": "Canta a morte do inimigo."},
        ],
        "advanced": [
            {"name": "🎼 Apocalipse Sônico", "mana_cost": 50, "dmg_mult": 2.8, "stun_chance": 0.4, "weaken": True, "desc": "Som que racha o espaço!"},
            {"name": "🌌 Canto das Estrelas","mana_cost": 55, "dmg_mult": 3.0, "self_heal": 40, "desc": "Música das esferas cura e destrói."},
        ],
        "supreme": {
            "name": "🎵 A Canção Que Encerra o Mundo", "mana_cost": 90, "dmg_mult": 5.0, "weaken": True, "stun_chance": 0.7, "self_heal": 60,
            "desc": "Uma melodia tão perfeita que a realidade se recusa a continuar. O inimigo simplesmente para.",
            "unlock_boss": "Querubim Corrompido Makhael"
        },
    },
    # ── CAVALEIRO DAS SOMBRAS ───────────────────────────────────────
    "Cavaleiro das Sombras": {
        "basic": [
            {"name": "🌑 Estocada das Trevas","mana_cost": 0, "dmg_mult": 1.6, "desc": "Lança sombria perfura o inimigo."},
            {"name": "⛓️ Correntes Sombrias", "mana_cost": 15,"dmg_mult": 1.4, "stun_chance": 0.25, "desc": "Correntes de trevas prendem."},
        ],
        "intermediate": [
            {"name": "💀 Cavalgar nas Sombras","mana_cost": 25,"dmg_mult": 2.0, "desc": "Surge das sombras em alta velocidade."},
            {"name": "🐴 Corcel das Trevas",  "mana_cost": 30, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "Cavalo sombrio esmaga o inimigo."},
            {"name": "🌑 Aura Corrompida",    "mana_cost": 20, "dmg_mult": 1.5, "weaken": True, "def_bonus": 15, "desc": "Aura que enfraquece e protege."},
        ],
        "advanced": [
            {"name": "💫 Lance do Apocalipse","mana_cost": 50, "dmg_mult": 3.0, "ignore_def": True, "desc": "Lança atravessa qualquer coisa."},
            {"name": "🌪️ Vendaval Sombrio",  "mana_cost": 55, "dmg_mult": 3.4, "stun_chance": 0.4, "desc": "Tufão de energia sombria."},
        ],
        "supreme": {
            "name": "🏇 Cavaleiro do Apocalipse", "mana_cost": 90, "dmg_mult": 5.5, "ignore_def": True, "stun_chance": 0.5, "weaken": True,
            "desc": "Monta o corcel da morte e arrasa tudo em seu caminho.",
            "unlock_boss": "Senhor das Sombras"
        },
    },
    # ── INVOCADOR ──────────────────────────────────────────────────
    "Invocador": {
        "basic": [
            {"name": "🌀 Invocar Elemental", "mana_cost": 20, "dmg_mult": 1.5, "desc": "Elemental menor ataca."},
            {"name": "👁️ Olho Observador",   "mana_cost": 15, "dmg_mult": 1.3, "weaken": True, "desc": "Olho arcano debilita o inimigo."},
        ],
        "intermediate": [
            {"name": "🔥 Invocar Demônio",   "mana_cost": 35, "dmg_mult": 2.2, "desc": "Demônio menor combate junto."},
            {"name": "💀 Portão da Morte",   "mana_cost": 40, "dmg_mult": 2.5, "poison": True, "desc": "Portal libera criaturas mortais."},
            {"name": "🌌 Invocar Colossus",  "mana_cost": 45, "dmg_mult": 2.8, "stun_chance": 0.3, "desc": "Golem gigante esmaga."},
        ],
        "advanced": [
            {"name": "⭐ Invocar Lendário",  "mana_cost": 60, "dmg_mult": 3.5, "desc": "Uma criatura lendária entra em batalha!"},
            {"name": "🌠 Portão Celestial",  "mana_cost": 65, "dmg_mult": 3.8, "ignore_def": True, "desc": "Anjo de guerra desce à batalha."},
        ],
        "supreme": {
            "name": "♾️ Invocar a Extinção", "mana_cost": 100, "dmg_mult": 5.5, "ignore_def": True, "stun_chance": 0.4, "weaken": True,
            "desc": "Abre um portal para o fim dos tempos. Criaturas primordiais devoram o inimigo.",
            "unlock_boss": "Vácuo da Criação"
        },
    },
    # ── RUNESMITH ──────────────────────────────────────────────────
    "Runesmith": {
        "basic": [
            {"name": "🔣 Runa de Fogo",      "mana_cost": 15, "dmg_mult": 1.5, "desc": "Runa explode em chamas."},
            {"name": "❄️ Runa de Gelo",      "mana_cost": 15, "dmg_mult": 1.4, "stun_chance": 0.2, "desc": "Runa congela o inimigo."},
        ],
        "intermediate": [
            {"name": "⚡ Runa do Trovão",    "mana_cost": 25, "dmg_mult": 2.0, "stun_chance": 0.35, "desc": "Runa elétrica paralisa."},
            {"name": "💀 Runa da Morte",     "mana_cost": 30, "dmg_mult": 2.2, "weaken": True, "desc": "Runa que drena a vida."},
            {"name": "🛡️ Runa Protetora",   "mana_cost": 20, "dmg_mult": 1.2, "def_bonus": 30, "self_heal": 25, "desc": "Runa escuda e cura."},
        ],
        "advanced": [
            {"name": "🌟 Runa Suprema",      "mana_cost": 50, "dmg_mult": 3.0, "ignore_def": True, "desc": "Runa inscrita na realidade."},
            {"name": "♾️ Runa do Abismo",    "mana_cost": 60, "dmg_mult": 3.5, "poison": True, "weaken": True, "desc": "Runa do vazio corrompido."},
        ],
        "supreme": {
            "name": "🌌 Runa Primordial", "mana_cost": 95, "dmg_mult": 5.8, "ignore_def": True, "stun_chance": 0.5,
            "desc": "A primeira runa gravada no universo. Poder irresistível.",
            "unlock_boss": "O Caos em Pessoa"
        },
    },
    # ── CAZADOR DE RECOMPENSAS ─────────────────────────────────────
    "Cazador de Recompensas": {
        "basic": [
            {"name": "🎯 Disparo Preciso",   "mana_cost": 0,  "dmg_mult": 1.5, "desc": "Tiro certeiro na fraqueza."},
            {"name": "🔍 Marcar Alvo",       "mana_cost": 10, "dmg_mult": 1.3, "weaken": True, "desc": "Marca o alvo para mais dano."},
        ],
        "intermediate": [
            {"name": "💣 Bomba de Fragmentos","mana_cost": 25,"dmg_mult": 2.0, "stun_chance": 0.3, "desc": "Explosão de estilhaços."},
            {"name": "☠️ Disparo Envenenado","mana_cost": 20, "dmg_mult": 1.8, "poison": True, "desc": "Bala com veneno mortal."},
            {"name": "🌪️ Rajada Rápida",    "mana_cost": 30, "dmg_mult": 2.2, "desc": "Cinco tiros em um segundo."},
        ],
        "advanced": [
            {"name": "🔫 Tiro Fatal",        "mana_cost": 45, "dmg_mult": 3.0, "crit_chance": 0.5, "desc": "Tiro com 50% de crítico."},
            {"name": "💥 Explosão Suprema",  "mana_cost": 55, "dmg_mult": 3.5, "ignore_def": True, "desc": "Projétil que ignora armaduras."},
        ],
        "supreme": {
            "name": "👁️ O Tiro Impossível", "mana_cost": 80, "dmg_mult": 5.8, "crit_chance": 0.85, "ignore_def": True,
            "desc": "Um tiro que viaja através do tempo para acertar o alvo. Impossível de desviar.",
            "unlock_boss": "♾️ Loop Temporal"
        },
    },
    # ── XAMÃ ───────────────────────────────────────────────────────
    "Xamã": {
        "basic": [
            {"name": "🪶 Espírito Guerreiro", "mana_cost": 15,"dmg_mult": 1.5, "desc": "Espírito ancestral ataca."},
            {"name": "🌊 Maldição Tribal",    "mana_cost": 20, "dmg_mult": 1.3, "weaken": True, "desc": "Maldição dos ancestrais."},
        ],
        "intermediate": [
            {"name": "🐺 Espírito do Lobo",  "mana_cost": 30, "dmg_mult": 2.0, "desc": "Lobo espiritual desmembra."},
            {"name": "⚡ Trovão dos Ancestrais","mana_cost": 35,"dmg_mult": 2.3, "stun_chance": 0.35, "desc": "Raio convocado pelos mortos."},
            {"name": "💚 Cura dos Espíritos", "mana_cost": 25, "dmg_mult": 1.2, "self_heal": 60, "desc": "Espíritos curam ferimentos."},
        ],
        "advanced": [
            {"name": "🌋 Fúria dos Totens",  "mana_cost": 50, "dmg_mult": 2.8, "poison": True, "stun_chance": 0.3, "desc": "Totens ancestrais despertam furiosos."},
            {"name": "💀 Possessão Espiritual","mana_cost": 55,"dmg_mult": 3.2, "weaken": True, "ignore_def": True, "desc": "Espírito penetra o inimigo por dentro."},
        ],
        "supreme": {
            "name": "🌌 Convocação Primordial", "mana_cost": 90, "dmg_mult": 5.2, "self_heal": 100, "stun_chance": 0.5,
            "desc": "Chama todos os ancestrais de todas as eras. O maior poder espiritual do mundo.",
            "unlock_boss": "Yeti Colossal"
        },
    },
    # ── TEMPESTEIRO ────────────────────────────────────────────────
    "Tempesteiro": {
        "basic": [
            {"name": "⚡ Raio Simples",      "mana_cost": 10, "dmg_mult": 1.5, "stun_chance": 0.2, "desc": "Raio básico."},
            {"name": "💨 Rajada de Vento",   "mana_cost": 15, "dmg_mult": 1.4, "desc": "Vento cortante."},
        ],
        "intermediate": [
            {"name": "⛈️ Tempestade Local",  "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Tempestade concentrada."},
            {"name": "🌊 Ciclone Elétrico",  "mana_cost": 35, "dmg_mult": 2.5, "stun_chance": 0.4, "desc": "Furacão elétrico devasta."},
            {"name": "🌩️ Cadeia de Raios",  "mana_cost": 40, "dmg_mult": 2.0, "poison": True, "desc": "Raios encadeados que queimam."},
        ],
        "advanced": [
            {"name": "🌪️ Furacão Arcano",   "mana_cost": 55, "dmg_mult": 3.2, "stun_chance": 0.45, "desc": "Furacão que leva o inimigo."},
            {"name": "⚡ Plasma Absoluto",   "mana_cost": 60, "dmg_mult": 3.6, "ignore_def": True, "desc": "Plasma que dissolve matéria."},
        ],
        "supreme": {
            "name": "🌩️ Zeus Menor II — A Tempestade Eterna", "mana_cost": 100, "dmg_mult": 6.0, "stun_chance": 0.7, "ignore_def": True,
            "desc": "Invoca o poder de Zeus Menor. Relâmpagos sem fim que nunca param.",
            "unlock_boss": "Zeus Menor, o Trovejante"
        },
    },
    # ── ILUSIONISTA ────────────────────────────────────────────────
    "Ilusionista": {
        "basic": [
            {"name": "🪄 Ilusão Básica",     "mana_cost": 10, "dmg_mult": 1.3, "stun_chance": 0.2, "desc": "Ilusão confunde o inimigo."},
            {"name": "🌀 Espelho Falso",      "mana_cost": 15, "dmg_mult": 1.2, "def_bonus": 15, "desc": "Cria cópia para desviar ataques."},
        ],
        "intermediate": [
            {"name": "🎭 Pesadelo Vívido",   "mana_cost": 30, "dmg_mult": 2.0, "stun_chance": 0.4, "weaken": True, "desc": "Faz o inimigo ver seus medos."},
            {"name": "💫 Doppelgänger",       "mana_cost": 35, "dmg_mult": 2.2, "desc": "Clone que ataca o inimigo."},
            {"name": "🌑 Realidade Alternativa","mana_cost": 40,"dmg_mult": 2.4, "ignore_def": True, "desc": "Move o ataque para uma realidade sem defesas."},
        ],
        "advanced": [
            {"name": "👁️ Labirinto Mental",  "mana_cost": 50, "dmg_mult": 2.8, "stun_chance": 0.6, "desc": "Prende a mente do inimigo."},
            {"name": "🌌 Grande Ilusão",      "mana_cost": 60, "dmg_mult": 3.2, "weaken": True, "stun_chance": 0.4, "desc": "Ilusão tão real que causa dano físico."},
        ],
        "supreme": {
            "name": "♾️ Fim da Realidade", "mana_cost": 90, "dmg_mult": 5.0, "stun_chance": 0.8, "weaken": True,
            "desc": "Faz o inimigo acreditar que já morreu. Tão poderoso que pode se tornar realidade.",
            "unlock_boss": "Olho do Abismo"
        },
    },
    # ── ALQUIMISTA ─────────────────────────────────────────────────
    "Alquimista": {
        "basic": [
            {"name": "⚗️ Bomba Ácida",       "mana_cost": 10, "dmg_mult": 1.4, "poison": True, "desc": "Ácido corroi o inimigo."},
            {"name": "🧪 Poção Explosiva",    "mana_cost": 15, "dmg_mult": 1.5, "desc": "Poção que explode no contato."},
        ],
        "intermediate": [
            {"name": "☠️ Gás Tóxico",        "mana_cost": 25, "dmg_mult": 1.8, "poison": True, "weaken": True, "desc": "Nuvem de gás envenena e debilita."},
            {"name": "🔥 Napalm Arcano",     "mana_cost": 30, "dmg_mult": 2.2, "poison": True, "desc": "Líquido flamejante grudento."},
            {"name": "💊 Elixir de Combate", "mana_cost": 20, "dmg_mult": 1.3, "self_heal": 50, "def_bonus": 20, "desc": "Elixir que potencializa capacidades."},
        ],
        "advanced": [
            {"name": "💥 Bomba de Fragmentos Arcanos","mana_cost": 50,"dmg_mult": 3.0, "stun_chance": 0.35, "poison": True, "desc": "Estilhaços envenenados!"},
            {"name": "⚗️ Transmutação Letal", "mana_cost": 55, "dmg_mult": 3.4, "ignore_def": True, "desc": "Transmuta a armadura do inimigo em pó."},
        ],
        "supreme": {
            "name": "☢️ Grande Transmutação", "mana_cost": 85, "dmg_mult": 5.5, "ignore_def": True, "poison": True, "weaken": True,
            "desc": "Transmuta toda matéria do inimigo em elemento instável. A pedra filosofal da destruição.",
            "unlock_boss": "O Caos em Pessoa"
        },
    },
    # ── GUARDIÃO DO ABISMO ─────────────────────────────────────────
    "Guardião do Abismo": {
        "basic": [
            {"name": "♾️ Toque do Vazio",    "mana_cost": 15, "dmg_mult": 1.5, "weaken": True, "desc": "O vazio corrói o inimigo."},
            {"name": "🌑 Barreira do Abismo","mana_cost": 20, "dmg_mult": 1.2, "def_bonus": 25, "desc": "Barreira de energia do vazio."},
        ],
        "intermediate": [
            {"name": "💀 Fissura do Vazio",  "mana_cost": 30, "dmg_mult": 2.2, "ignore_def": True, "desc": "Fenda dimensional ataca."},
            {"name": "🌀 Espiral do Nada",   "mana_cost": 35, "dmg_mult": 2.4, "stun_chance": 0.35, "desc": "Espiral suga e destrói."},
            {"name": "👁️ Olhar do Abismo",  "mana_cost": 25, "dmg_mult": 1.8, "weaken": True, "poison": True, "desc": "Olhar que corrói alma e corpo."},
        ],
        "advanced": [
            {"name": "♾️ Colapso Dimensional","mana_cost": 55,"dmg_mult": 3.3, "stun_chance": 0.4, "desc": "Dimensão colapsa sobre o inimigo!"},
            {"name": "🌌 Pureza do Vazio",   "mana_cost": 65, "dmg_mult": 3.8, "ignore_def": True, "weaken": True, "desc": "Poder puro do nada absoluto."},
        ],
        "supreme": {
            "name": "☯️ O Nada Que Devora", "mana_cost": 100, "dmg_mult": 6.0, "ignore_def": True, "weaken": True, "stun_chance": 0.5,
            "desc": "O abismo engole o inimigo completamente. Não existe defesa contra o nada.",
            "unlock_boss": "O Senhor das Sombras"
        },
    },
    # ── DANÇARINO DA MORTE ─────────────────────────────────────────
    "Dançarino da Morte": {
        "basic": [
            {"name": "💃 Passo Letal",        "mana_cost": 0,  "dmg_mult": 1.5, "crit_chance": 0.3, "desc": "Dança e golpeia sem parar."},
            {"name": "🗡️ Lâminas Dançantes", "mana_cost": 15, "dmg_mult": 1.6, "desc": "Lâminas giram em dança."},
        ],
        "intermediate": [
            {"name": "💀 Valsa da Morte",     "mana_cost": 25, "dmg_mult": 2.2, "crit_chance": 0.4, "desc": "Dança mortal e hipnótica."},
            {"name": "🩸 Sangue na Pista",    "mana_cost": 20, "dmg_mult": 2.0, "poison": True, "desc": "Deixa rastro de veneno na dança."},
            {"name": "🌀 Girar do Caos",      "mana_cost": 30, "dmg_mult": 2.3, "stun_chance": 0.35, "desc": "Gira causando tontura no inimigo."},
        ],
        "advanced": [
            {"name": "🌪️ Turbilhão de Lâminas","mana_cost": 45,"dmg_mult": 3.0, "crit_chance": 0.5, "desc": "Tufão de lâminas afiadas!"},
            {"name": "💫 Último Passo",       "mana_cost": 55, "dmg_mult": 3.5, "ignore_def": True, "crit_chance": 0.4, "desc": "O golpe final da dança."},
        ],
        "supreme": {
            "name": "☠️ Dança do Apocalipse", "mana_cost": 85, "dmg_mult": 5.8, "crit_chance": 0.9, "ignore_def": True, "poison": True,
            "desc": "Uma dança tão rápida que cria réplicas. Cortes em cada dimensão do espaço.",
            "unlock_boss": "Dançarino da Morte"
        },
    },
    # ── ORÁCULO ────────────────────────────────────────────────────
    "Oráculo": {
        "basic": [
            {"name": "🔮 Visão do Futuro",   "mana_cost": 15, "dmg_mult": 1.4, "weaken": True, "desc": "Vê o próximo ataque e debilita."},
            {"name": "⭐ Maldição do Destino","mana_cost": 20, "dmg_mult": 1.5, "desc": "Predestina dano ao inimigo."},
        ],
        "intermediate": [
            {"name": "⏱️ Distorção Temporal", "mana_cost": 30, "dmg_mult": 2.0, "stun_chance": 0.45, "desc": "Temporariamente paralisa o tempo do inimigo."},
            {"name": "💫 Fio do Destino",     "mana_cost": 25, "dmg_mult": 2.2, "ignore_def": True, "desc": "Ataca através do destino predestinado."},
            {"name": "🌌 Paradoxo",           "mana_cost": 35, "dmg_mult": 2.4, "weaken": True, "stun_chance": 0.3, "desc": "Cria paradoxo que confunde e debilita."},
        ],
        "advanced": [
            {"name": "♾️ Reescrever o Passado","mana_cost": 55,"dmg_mult": 3.2, "ignore_def": True, "desc": "Reescreve a batalha a seu favor."},
            {"name": "🌠 Visão do Fim",       "mana_cost": 60, "dmg_mult": 3.5, "weaken": True, "stun_chance": 0.4, "desc": "Mostra ao inimigo sua própria morte."},
        ],
        "supreme": {
            "name": "⏳ O Destino Era Este", "mana_cost": 95, "dmg_mult": 5.5, "stun_chance": 0.7, "ignore_def": True, "weaken": True,
            "desc": "Desde o início do universo, estava escrito que este golpe acertaria. Irresistível.",
            "unlock_boss": "Loop Temporal"
        },
    },
    # ── COLOSSUS ───────────────────────────────────────────────────
    "Colossus": {
        "basic": [
            {"name": "🗿 Soco de Pedra",     "mana_cost": 0,  "dmg_mult": 1.6, "stun_chance": 0.2, "desc": "Punho do tamanho de uma rocha."},
            {"name": "🏔️ Postura de Granito","mana_cost": 10, "dmg_mult": 0.8, "def_bonus": 35, "desc": "Postura impenetrável."},
        ],
        "intermediate": [
            {"name": "🌋 Pisar do Colossus", "mana_cost": 25, "dmg_mult": 2.0, "stun_chance": 0.4, "desc": "Pisada que racha o chão."},
            {"name": "💪 Golpe Monolítico",  "mana_cost": 30, "dmg_mult": 2.3, "ignore_def": True, "desc": "Força de uma montanha."},
            {"name": "🛡️ Fortaleza Viva",   "mana_cost": 20, "dmg_mult": 1.0, "def_bonus": 50, "self_heal": 40, "desc": "Torna-se uma fortaleza."},
        ],
        "advanced": [
            {"name": "🌍 Terremoto",         "mana_cost": 50, "dmg_mult": 3.0, "stun_chance": 0.5, "desc": "Abala a terra causando tremores."},
            {"name": "💥 Colapso Gravitacional","mana_cost": 55,"dmg_mult": 3.4, "ignore_def": True, "desc": "Gravidade aumentada esmaga."},
        ],
        "supreme": {
            "name": "🏔️ A Montanha Desperta", "mana_cost": 80, "dmg_mult": 5.2, "stun_chance": 0.6, "ignore_def": True, "def_bonus": 40,
            "desc": "A força de uma cordilheira inteira. Nada sobrevive a este golpe.",
            "unlock_boss": "Primeiro Gigante Primordial"
        },
    },
    # ── DEVORADOR DE ALMAS ──────────────────────────────────────────
    "Devorador de Almas": {
        "basic": [
            {"name": "💫 Devorar Fragmento", "mana_cost": 15, "dmg_mult": 1.5, "self_heal": 15, "desc": "Consume fragmento da alma do inimigo."},
            {"name": "🌑 Fome das Sombras",  "mana_cost": 20, "dmg_mult": 1.4, "weaken": True, "desc": "Fome que drena energia."},
        ],
        "intermediate": [
            {"name": "💀 Ingestão da Força", "mana_cost": 30, "dmg_mult": 2.0, "self_heal": 30, "desc": "Devora a força do inimigo."},
            {"name": "🌀 Vórtice da Fome",   "mana_cost": 35, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "Vórtice que suga energia."},
            {"name": "☠️ Roubo de Essência", "mana_cost": 25, "dmg_mult": 1.8, "self_heal": 40, "weaken": True, "desc": "Rouba essência vital."},
        ],
        "advanced": [
            {"name": "💫 Devorar a Alma",    "mana_cost": 55, "dmg_mult": 3.2, "self_heal": 60, "ignore_def": True, "desc": "Consome a alma diretamente."},
            {"name": "🌌 Fome Infinita",     "mana_cost": 60, "dmg_mult": 3.5, "self_heal": 80, "desc": "Fome sem fim que cresce com cada golpe."},
        ],
        "supreme": {
            "name": "♾️ Consumir a Existência", "mana_cost": 100, "dmg_mult": 5.8, "self_heal": 150, "ignore_def": True, "weaken": True,
            "desc": "Devora a própria existência do inimigo. Cada partícula consumida restaura o Devorador.",
            "unlock_boss": "Vácuo da Criação"
        },
    },
    # ── ARAUTO CELESTIAL ───────────────────────────────────────────
    "Arauto Celestial": {
        "basic": [
            {"name": "✨ Mensagem Divina",   "mana_cost": 10, "dmg_mult": 1.4, "desc": "Mensagem dos deuses como força."},
            {"name": "🕊️ Escudo da Graça",  "mana_cost": 15, "dmg_mult": 0.9, "def_bonus": 20, "self_heal": 20, "desc": "Graça divina protege e cura."},
        ],
        "intermediate": [
            {"name": "☀️ Proclama Sagrada",  "mana_cost": 25, "dmg_mult": 2.0, "stun_chance": 0.3, "desc": "Proclama santa atordoa."},
            {"name": "👼 Chamado dos Anjos", "mana_cost": 30, "dmg_mult": 2.2, "self_heal": 40, "desc": "Anjos respondem ao chamado."},
            {"name": "🌟 Luz Celestial",     "mana_cost": 35, "dmg_mult": 2.4, "weaken": True, "desc": "Luz que queima seres das trevas."},
        ],
        "advanced": [
            {"name": "⚡ Lança dos Céus",    "mana_cost": 50, "dmg_mult": 3.0, "ignore_def": True, "desc": "Lança forjada no Trono Celestial."},
            {"name": "🌈 Julgamento Celestial","mana_cost": 55,"dmg_mult": 3.3, "stun_chance": 0.4, "self_heal": 60, "desc": "Julgamento dos céus cai."},
        ],
        "supreme": {
            "name": "👑 Vontade dos Deuses", "mana_cost": 90, "dmg_mult": 5.2, "ignore_def": True, "self_heal": 120, "stun_chance": 0.4,
            "desc": "Os próprios deuses falam através do Arauto. O golpe e a cura máxima simultaneamente.",
            "unlock_boss": "Imperador Astral"
        },
    },
    # ── LANÇADOR DE VENENOS ────────────────────────────────────────
    "Lançador de Venenos": {
        "basic": [
            {"name": "☠️ Inoculação Básica", "mana_cost": 0,  "dmg_mult": 1.3, "poison": True, "desc": "Veneno básico inoculado."},
            {"name": "🧪 Spray Tóxico",      "mana_cost": 10, "dmg_mult": 1.2, "poison": True, "weaken": True, "desc": "Spray que envenena e debilita."},
        ],
        "intermediate": [
            {"name": "💀 Veneno Paralisante","mana_cost": 25, "dmg_mult": 1.8, "poison": True, "stun_chance": 0.35, "desc": "Veneno que paralisa os nervos."},
            {"name": "🌑 Praga Sombria",     "mana_cost": 30, "dmg_mult": 2.0, "poison": True, "weaken": True, "desc": "Praga que se espalha."},
            {"name": "⚗️ Toxina Corrosiva",  "mana_cost": 20, "dmg_mult": 1.6, "poison": True, "ignore_def": True, "desc": "Corrói armaduras e carne."},
        ],
        "advanced": [
            {"name": "☢️ Veneno Arcano",     "mana_cost": 45, "dmg_mult": 2.8, "poison": True, "ignore_def": True, "desc": "Veneno que ignora proteções mágicas."},
            {"name": "💫 Morte Lenta Total", "mana_cost": 55, "dmg_mult": 3.2, "poison": True, "weaken": True, "stun_chance": 0.3, "desc": "Veneno que destrói todos os sistemas."},
        ],
        "supreme": {
            "name": "☠️ O Veneno de Todos os Venenos", "mana_cost": 80, "dmg_mult": 4.8, "poison": True, "weaken": True, "ignore_def": True, "stun_chance": 0.5,
            "desc": "Combina todo veneno existente. Paralisa, corrói, enfraquece e mata simultaneamente.",
            "unlock_boss": "Dragão de Magma"
        },
    },
    # ── GLADIADOR ──────────────────────────────────────────────────
    "Gladiador": {
        "basic": [
            {"name": "🏟️ Golpe da Arena",    "mana_cost": 0,  "dmg_mult": 1.5, "desc": "Golpe calibrado para matar."},
            {"name": "🛡️ Bloquear e Golpear","mana_cost": 10, "dmg_mult": 1.3, "def_bonus": 15, "desc": "Defende e contra-ataca."},
        ],
        "intermediate": [
            {"name": "⚔️ Combo da Vitória",  "mana_cost": 25, "dmg_mult": 2.0, "desc": "Sequência treinada para matar."},
            {"name": "💥 Golpe do Campeão",  "mana_cost": 30, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "Golpe de campeão invicto."},
            {"name": "🩸 Sede de Glória",    "mana_cost": 20, "dmg_mult": 2.2, "self_heal": 30, "desc": "A glória cura ferimentos."},
        ],
        "advanced": [
            {"name": "🏆 Execução Lendária", "mana_cost": 50, "dmg_mult": 3.2, "ignore_def": True, "desc": "Execução digna de lendas."},
            {"name": "🌟 Aura do Invicto",   "mana_cost": 45, "dmg_mult": 2.8, "def_bonus": 30, "self_heal": 50, "desc": "Aura de um guerreiro sem derrota."},
        ],
        "supreme": {
            "name": "🏟️ O Último Combate", "mana_cost": 85, "dmg_mult": 5.5, "ignore_def": True, "stun_chance": 0.45, "self_heal": 80,
            "desc": "O golpe final de uma carreira de mil batalhas. Tudo aprendido, tudo liberado.",
            "unlock_boss": "Imperador Astral"
        },
    },
    # ── MESTRE DAS CORRENTES ────────────────────────────────────────
    "Mestre das Correntes": {
        "basic": [
            {"name": "⛓️ Corrente Básica",   "mana_cost": 10, "dmg_mult": 1.3, "stun_chance": 0.2, "desc": "Corrente prende brevemente."},
            {"name": "💪 Açoite de Ferro",   "mana_cost": 0,  "dmg_mult": 1.4, "desc": "Açoite metálico poderoso."},
        ],
        "intermediate": [
            {"name": "⛓️ Aprisionamento",    "mana_cost": 25, "dmg_mult": 1.8, "stun_chance": 0.45, "desc": "Correntes prendem o inimigo."},
            {"name": "🔥 Correntes Flamejantes","mana_cost": 30,"dmg_mult": 2.2, "poison": True, "desc": "Correntes de fogo queimam."},
            {"name": "💫 Dança das Correntes","mana_cost": 20, "dmg_mult": 2.0, "desc": "Múltiplas correntes giram e golpeiam."},
        ],
        "advanced": [
            {"name": "🌑 Correntes do Abismo","mana_cost": 50, "dmg_mult": 3.0, "weaken": True, "stun_chance": 0.4, "desc": "Correntes do vazio prendem a alma."},
            {"name": "♾️ Laço da Realidade", "mana_cost": 55, "dmg_mult": 3.3, "ignore_def": True, "desc": "Corrente prende na própria realidade."},
        ],
        "supreme": {
            "name": "⛓️ Acorrentar o Universo", "mana_cost": 90, "dmg_mult": 5.3, "stun_chance": 0.7, "ignore_def": True, "weaken": True,
            "desc": "Correntes que aprisionam até a alma. Nada pode se mover.",
            "unlock_boss": "Caos em Pessoa"
        },
    },
    # ── PROFETA DA DESTRUIÇÃO ───────────────────────────────────────
    "Profeta da Destruição": {
        "basic": [
            {"name": "📯 Anúncio do Caos",   "mana_cost": 10, "dmg_mult": 1.4, "weaken": True, "desc": "Profecia que enfraquece."},
            {"name": "🌑 Sombra da Profecia", "mana_cost": 15, "dmg_mult": 1.5, "desc": "Sombra da destruição futura."},
        ],
        "intermediate": [
            {"name": "🔥 Profecias em Chamas","mana_cost": 25, "dmg_mult": 2.0, "poison": True, "desc": "Profecia se manifesta em fogo."},
            {"name": "💀 Decreto do Fim",     "mana_cost": 30, "dmg_mult": 2.3, "weaken": True, "stun_chance": 0.3, "desc": "Decreta a destruição do inimigo."},
            {"name": "🌪️ Tempestade Profética","mana_cost": 35,"dmg_mult": 2.5, "desc": "Tempestade do futuro atinge agora."},
        ],
        "advanced": [
            {"name": "🌋 Armageddon Menor",  "mana_cost": 55, "dmg_mult": 3.2, "stun_chance": 0.4, "ignore_def": True, "desc": "Versão menor do fim do mundo."},
            {"name": "💫 A Profecia Se Cumpre","mana_cost": 60,"dmg_mult": 3.6, "weaken": True, "poison": True, "desc": "O inevitável ocorre agora."},
        ],
        "supreme": {
            "name": "🌌 O Fim Que Profetizei", "mana_cost": 100, "dmg_mult": 6.0, "ignore_def": True, "stun_chance": 0.5, "weaken": True, "poison": True,
            "desc": "A profecia que sempre foi. O universo colapsa em torno do inimigo.",
            "unlock_boss": "O Caos em Pessoa"
        },
    },
    # ── FERREIRO DE GUERRA ──────────────────────────────────────────
    "Ferreiro de Guerra": {
        "basic": [
            {"name": "🔨 Martelada Brutal",  "mana_cost": 0,  "dmg_mult": 1.5, "desc": "Martelo de guerra esmaga."},
            {"name": "⚒️ Forjar na Batalha", "mana_cost": 15, "dmg_mult": 1.2, "def_bonus": 20, "desc": "Forja armadura adicional no campo."},
        ],
        "intermediate": [
            {"name": "🔥 Golpe da Forja",    "mana_cost": 25, "dmg_mult": 2.0, "stun_chance": 0.3, "desc": "Golpe com metal incandescente."},
            {"name": "⚙️ Bomba da Engrenagem","mana_cost": 30, "dmg_mult": 2.2, "desc": "Engrenagem explosiva arremessada."},
            {"name": "🛡️ Armadura de Batalha","mana_cost": 20, "dmg_mult": 1.0, "def_bonus": 40, "self_heal": 35, "desc": "Forja armadura sagrada em segundos."},
        ],
        "advanced": [
            {"name": "💫 Arma Perfeita",     "mana_cost": 50, "dmg_mult": 3.0, "ignore_def": True, "desc": "Forja a arma perfeita para este momento."},
            {"name": "🌟 Lenda da Forja",    "mana_cost": 55, "dmg_mult": 3.4, "def_bonus": 30, "stun_chance": 0.3, "desc": "Arma forjada com memórias de batalha."},
        ],
        "supreme": {
            "name": "⚒️ A Forja Sagrada Desperta", "mana_cost": 90, "dmg_mult": 5.5, "ignore_def": True, "def_bonus": 50, "self_heal": 80,
            "desc": "A Forja Sagrada dos Anões primordiais. A arma e a armadura definitivas.",
            "unlock_boss": "Golem da Forja Corrompida"
        },
    },
    # ── DRAGONLANCER ───────────────────────────────────────────────
    "Dragonlancer": {
        "basic": [
            {"name": "🐲 Lança de Fogo",     "mana_cost": 15, "dmg_mult": 1.6, "desc": "Lança imbuída de fogo dracônico."},
            {"name": "🔥 Sopro do Dragão",   "mana_cost": 20, "dmg_mult": 1.5, "poison": True, "desc": "Sopro de fogo queima o inimigo."},
        ],
        "intermediate": [
            {"name": "🐉 Carga Dracônica",   "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Monta dragão e carrega o inimigo."},
            {"name": "💥 Golpe de Cauda",    "mana_cost": 25, "dmg_mult": 2.0, "stun_chance": 0.4, "desc": "Cauda de dragão golpeia brutalmente."},
            {"name": "🌋 Chuva de Lava",     "mana_cost": 35, "dmg_mult": 2.4, "poison": True, "desc": "Lava cai do céu."},
        ],
        "advanced": [
            {"name": "🌌 Voo Dracônico",     "mana_cost": 50, "dmg_mult": 3.0, "ignore_def": True, "desc": "Ataca em alta velocidade do céu."},
            {"name": "⭐ Lança das Estrelas", "mana_cost": 55, "dmg_mult": 3.4, "crit_chance": 0.4, "desc": "Lança de energia estelar."},
        ],
        "supreme": {
            "name": "🐉 O Último Dragão Desperta", "mana_cost": 95, "dmg_mult": 5.8, "ignore_def": True, "stun_chance": 0.4, "poison": True,
            "desc": "O primeiro e último dragão primordial emerge. Fogo que não tem temperatura — apenas destruição.",
            "unlock_boss": "Dragão de Magma"
        },
    },
}

# ================= ESPECIALIZAÇÕES (desbloqueadas ao evoluir de classe) =================
CLASS_SPECIALIZATIONS = {
    # ── GUERREIRO ──────────────────────────────────────────────────
    "Campeão": {
        "emoji": "🏆",
        "desc": "Especializado em golpes críticos e combate ofensivo.",
        "passive": "+20% chance de crítico. Críticos causam 2.5x dano.",
        "bonus_atk": 15, "bonus_hp": 10, "bonus_def": 0,
        "special_skill": {"name": "🏆 Golpe do Campeão", "mana_cost": 35, "dmg_mult": 2.8, "crit_chance": 0.6, "desc": "Golpe do verdadeiro campeão!"}
    },
    "Guardião Inabalável": {
        "emoji": "🛡️",
        "desc": "Especializado em defesa extrema e proteção de aliados.",
        "passive": "+30 DEF permanente. Reflete 10% do dano recebido.",
        "bonus_atk": 0, "bonus_hp": 25, "bonus_def": 30,
        "special_skill": {"name": "🛡️ Bastião", "mana_cost": 25, "dmg_mult": 1.0, "def_bonus": 60, "self_heal": 50, "desc": "Nada atravessa este escudo!"}
    },
    # ── MAGO ───────────────────────────────────────────────────────
    "Piromante": {
        "emoji": "🔥",
        "desc": "Controla o fogo com poder sem igual.",
        "passive": "+30% dano de fogo. Todos ataques têm chance de queimar.",
        "bonus_atk": 20, "bonus_hp": 0, "bonus_def": 0,
        "special_skill": {"name": "🌋 Inferno Absoluto", "mana_cost": 60, "dmg_mult": 3.8, "poison": True, "desc": "Fogo que queima até as almas!"}
    },
    "Criomante": {
        "emoji": "❄️",
        "desc": "Mestre do gelo e do congelamento.",
        "passive": "+35% chance de congelar. Inimigos congelados recebem +20% dano.",
        "bonus_atk": 15, "bonus_hp": 5, "bonus_def": 5,
        "special_skill": {"name": "❄️ Blizzard Eterno", "mana_cost": 55, "dmg_mult": 3.5, "stun_chance": 0.7, "desc": "Tempestade de gelo que imobiliza tudo!"}
    },
    # ── ARQUEIRO ───────────────────────────────────────────────────
    "Caçador Sombrio": {
        "emoji": "🌑",
        "desc": "Usa as sombras para golpes letais.",
        "passive": "Primeiro ataque de cada combate é sempre crítico. +15% crit.",
        "bonus_atk": 18, "bonus_hp": 5, "bonus_def": 0,
        "special_skill": {"name": "🌑 Flecha Sombria", "mana_cost": 40, "dmg_mult": 3.5, "crit_chance": 0.7, "desc": "Flecha que surge das sombras!"}
    },
    "Arqueiro da Tempestade": {
        "emoji": "⚡",
        "desc": "Flechas carregadas com energia elétrica.",
        "passive": "+30% chance de paralisar com flechas. Cada flecha causa dano em área.",
        "bonus_atk": 20, "bonus_hp": 0, "bonus_def": 0,
        "special_skill": {"name": "⚡ Tempestade de Raios", "mana_cost": 45, "dmg_mult": 3.2, "stun_chance": 0.6, "desc": "Raios disparam em todas as direções!"}
    },
    # ── GENÉRICO (demais especializações seguem o mesmo padrão) ────
    "Berserker Sagrado": {
        "emoji": "🔥",
        "desc": "Fúria abençoada pelos deuses da guerra.",
        "passive": "+25% ATK quando HP < 50%. Regenera HP ao matar.",
        "bonus_atk": 25, "bonus_hp": 15, "bonus_def": 0,
        "special_skill": {"name": "🔥 Fúria Sagrada", "mana_cost": 40, "dmg_mult": 3.5, "ignore_def": True, "desc": "Fúria abençoada que ignora defesas!"}
    },
    "Mestre das Sombras": {
        "emoji": "🌑",
        "desc": "Invísivel aos olhos mortais.",
        "passive": "30% de esquiva. Ataques furtivos causam 2x dano.",
        "bonus_atk": 20, "bonus_hp": 0, "bonus_def": 5,
        "special_skill": {"name": "🌑 Extinção Furtiva", "mana_cost": 45, "dmg_mult": 3.8, "crit_chance": 0.65, "desc": "Ataque do invisível — impossível de desviar!"}
    },
    "Lich Aprendiz": {
        "emoji": "💀",
        "desc": "Primeiro passo para a imortalidade dos lich.",
        "passive": "Revive com 25% HP uma vez por batalha.",
        "bonus_atk": 15, "bonus_hp": 10, "bonus_def": 5,
        "special_skill": {"name": "💀 Ressurreição Negra", "mana_cost": 50, "dmg_mult": 2.5, "self_heal": 60, "desc": "Morre e renasce com o poder dos mortos!"}
    },
    "Carnificina": {
        "emoji": "🩸",
        "desc": "Cada kill aumenta o dano do próximo ataque.",
        "passive": "Acumula stacks de fúria a cada dano recebido. +5% ATK por stack.",
        "bonus_atk": 30, "bonus_hp": 0, "bonus_def": 0,
        "special_skill": {"name": "🩸 Modo Carnificina", "mana_cost": 35, "dmg_mult": 4.0, "self_dmg": 20, "desc": "Dano máximo com sacrifício de HP!"}
    },
    "Metamorfo": {
        "emoji": "🐺",
        "desc": "Transforma-se em diferentes bestas para diferentes situações.",
        "passive": "Pode alternar entre forma de ataque (+20% ATK) e forma de cura (+30 HP regen).",
        "bonus_atk": 12, "bonus_hp": 20, "bonus_def": 8,
        "special_skill": {"name": "🐺 Forma Primordial", "mana_cost": 45, "dmg_mult": 3.2, "self_heal": 60, "desc": "Transforma-se na besta mais antiga!"}
    },
    "Punho de Aço": {
        "emoji": "👊",
        "desc": "Mãos tornam-se armas sagradas.",
        "passive": "+25% dano de golpes sem armas. Cada crítico cura 15 HP.",
        "bonus_atk": 22, "bonus_hp": 12, "bonus_def": 5,
        "special_skill": {"name": "👊 Punho Divino", "mana_cost": 40, "dmg_mult": 3.5, "ignore_def": True, "desc": "Punho sagrado que atravessa qualquer coisa!"}
    },
    "Bardo da Batalha": {
        "emoji": "🎸",
        "desc": "Música inspira e destrói em igual medida.",
        "passive": "+15% ATK para cada aliado na batalha. Música causa dano em área.",
        "bonus_atk": 18, "bonus_hp": 10, "bonus_def": 5,
        "special_skill": {"name": "🎸 Solo da Morte", "mana_cost": 40, "dmg_mult": 3.2, "stun_chance": 0.5, "desc": "Solo tão poderoso que desintegra!"}
    },
}

# ================= MANA POR CLASSE (novas classes incluídas) =================
CLASS_MANA = {
    "Guerreiro":  {"base_mana": 30,  "mana_per_level": 2},
    "Mago":       {"base_mana": 100, "mana_per_level": 8},
    "Arqueiro":   {"base_mana": 40,  "mana_per_level": 3},
    "Paladino":   {"base_mana": 60,  "mana_per_level": 4},
    "Assassino":  {"base_mana": 50,  "mana_per_level": 3},
    "Necromante": {"base_mana": 80,  "mana_per_level": 6},
    "Berserker":  {"base_mana": 20,  "mana_per_level": 1},
    "Druida":     {"base_mana": 70,  "mana_per_level": 5},
    "Monge":      {"base_mana": 55,  "mana_per_level": 4},
    "Bardo":      {"base_mana": 65,  "mana_per_level": 5},
    # Novas classes
    "Cavaleiro das Sombras": {"base_mana": 55, "mana_per_level": 4},
    "Invocador":             {"base_mana": 90, "mana_per_level": 7},
    "Runesmith":             {"base_mana": 60, "mana_per_level": 4},
    "Cazador de Recompensas":{"base_mana": 45, "mana_per_level": 3},
    "Xamã":                  {"base_mana": 75, "mana_per_level": 5},
    "Tempesteiro":           {"base_mana": 85, "mana_per_level": 7},
    "Ilusionista":           {"base_mana": 80, "mana_per_level": 6},
    "Alquimista":            {"base_mana": 55, "mana_per_level": 4},
    "Guardião do Abismo":    {"base_mana": 75, "mana_per_level": 6},
    "Dançarino da Morte":    {"base_mana": 50, "mana_per_level": 3},
    "Oráculo":               {"base_mana": 95, "mana_per_level": 7},
    "Colossus":              {"base_mana": 25, "mana_per_level": 2},
    "Devorador de Almas":    {"base_mana": 70, "mana_per_level": 5},
    "Arauto Celestial":      {"base_mana": 65, "mana_per_level": 5},
    "Lançador de Venenos":   {"base_mana": 45, "mana_per_level": 3},
    "Gladiador":             {"base_mana": 35, "mana_per_level": 2},
    "Mestre das Correntes":  {"base_mana": 60, "mana_per_level": 4},
    "Profeta da Destruição": {"base_mana": 80, "mana_per_level": 6},
    "Ferreiro de Guerra":    {"base_mana": 40, "mana_per_level": 3},
    "Dragonlancer":          {"base_mana": 55, "mana_per_level": 4},
}

# ================= HABILIDADES POR CLASSE (PvP) =================
CLASS_SKILLS = {
    "Guerreiro": [
        {"name": "🗡️ Golpe Devastador", "mana_cost": 0, "dmg_mult": 1.4, "desc": "Um golpe poderoso com toda a força!"},
        {"name": "🛡️ Ataque Protetor", "mana_cost": 10, "dmg_mult": 1.2, "def_bonus": 10, "desc": "Ataca enquanto se defende."},
        {"name": "⚔️ Fúria do Guerreiro", "mana_cost": 20, "dmg_mult": 1.8, "desc": "Desencadeia uma rajada de golpes furiosos!"},
        {"name": "🔥 Grito de Batalha", "mana_cost": 15, "dmg_mult": 1.5, "stun_chance": 0.2, "desc": "Grita aterrorizante que pode paralisar."},
    ],
    "Mago": [
        {"name": "🔥 Bola de Fogo", "mana_cost": 25, "dmg_mult": 2.0, "desc": "Uma esfera flamejante de destruição!"},
        {"name": "⚡ Relâmpago Arcano", "mana_cost": 30, "dmg_mult": 2.2, "stun_chance": 0.3, "desc": "Eletricidade arcana que pode paralisar."},
        {"name": "❄️ Toque Gelado", "mana_cost": 20, "dmg_mult": 1.6, "slow_chance": 0.4, "desc": "Congela o adversário reduzindo sua ação."},
        {"name": "🌀 Explosão do Vazio", "mana_cost": 40, "dmg_mult": 2.8, "desc": "Poder do abismo canalizado em destruição!"},
    ],
    "Arqueiro": [
        {"name": "🏹 Flecha Certeira", "mana_cost": 0, "dmg_mult": 1.5, "desc": "Uma flecha lançada com precisão mortal."},
        {"name": "💨 Chuva de Flechas", "mana_cost": 20, "dmg_mult": 1.7, "desc": "Múltiplas flechas caem como chuva!"},
        {"name": "🎯 Tiro Perfurante", "mana_cost": 15, "dmg_mult": 2.0, "ignore_def": True, "desc": "Flecha que penetra qualquer defesa."},
        {"name": "🌿 Flecha Envenenada", "mana_cost": 10, "dmg_mult": 1.3, "poison": True, "desc": "Veneno que corrói lentamente."},
    ],
    "Paladino": [
        {"name": "✨ Golpe Sagrado", "mana_cost": 15, "dmg_mult": 1.6, "desc": "Energia divina concentrada em um golpe!"},
        {"name": "🛡️ Escudo da Fé", "mana_cost": 20, "dmg_mult": 1.0, "self_heal": 30, "desc": "Cura a si mesmo enquanto defende."},
        {"name": "☀️ Julgamento Divino", "mana_cost": 35, "dmg_mult": 2.0, "desc": "O julgamento dos céus cai sobre o inimigo!"},
        {"name": "🌟 Aura de Proteção", "mana_cost": 25, "dmg_mult": 1.2, "def_bonus": 20, "desc": "Aura que reduz o dano recebido."},
    ],
    "Assassino": [
        {"name": "🗡️ Golpe Sorrateiro", "mana_cost": 0, "dmg_mult": 1.8, "crit_chance": 0.4, "desc": "Das sombras, um golpe mortal!"},
        {"name": "💨 Dança das Lâminas", "mana_cost": 20, "dmg_mult": 1.5, "desc": "Uma sequência vertiginosa de ataques."},
        {"name": "☠️ Veneno Assassino", "mana_cost": 15, "dmg_mult": 1.3, "poison": True, "desc": "Aplica veneno letal no adversário."},
        {"name": "🌑 Golpe das Sombras", "mana_cost": 30, "dmg_mult": 2.5, "crit_chance": 0.5, "desc": "Ataque das trevas com alta chance crítica!"},
    ],
    "Necromante": [
        {"name": "💀 Dreno de Vida", "mana_cost": 20, "dmg_mult": 1.5, "self_heal": 20, "desc": "Rouba HP do adversário!"},
        {"name": "🦴 Invocar Esqueleto", "mana_cost": 30, "dmg_mult": 1.7, "desc": "Um esqueleto guerreiro ataca!"},
        {"name": "🌑 Maldição Sombria", "mana_cost": 25, "dmg_mult": 1.4, "weaken": True, "desc": "Maldição que enfraquece o inimigo."},
        {"name": "☠️ Morte Instantânea", "mana_cost": 50, "dmg_mult": 3.0, "desc": "Toca o véu entre vida e morte!"},
    ],
    "Berserker": [
        {"name": "🪓 Frenesi", "mana_cost": 0, "dmg_mult": 2.0, "desc": "Ataque frenético sem controle!"},
        {"name": "💢 Ira Incontrolável", "mana_cost": 15, "dmg_mult": 2.2, "self_dmg": 10, "desc": "Sacrifica HP próprio por poder devastador."},
        {"name": "🩸 Sede de Sangue", "mana_cost": 10, "dmg_mult": 1.8, "hp_scale": True, "desc": "Quanto menos HP, mais forte o golpe!"},
        {"name": "💥 Explosão de Fúria", "mana_cost": 25, "dmg_mult": 2.8, "desc": "Toda a raiva liberada em um instante!"},
    ],
    "Druida": [
        {"name": "🌿 Golpe Natural", "mana_cost": 0, "dmg_mult": 1.3, "self_heal": 15, "desc": "A natureza cura ao atacar."},
        {"name": "🌪️ Tempestade de Folhas", "mana_cost": 20, "dmg_mult": 1.6, "desc": "Uma tempestade de espinhos e folhas!"},
        {"name": "🐺 Fúria Animal", "mana_cost": 30, "dmg_mult": 2.0, "desc": "Transforma-se em besta selvagem!"},
        {"name": "⚡ Trovão da Terra", "mana_cost": 35, "dmg_mult": 2.3, "stun_chance": 0.3, "desc": "A terra responde com trovão!"},
    ],
    "Monge": [
        {"name": "👊 Soco do Dragão", "mana_cost": 0, "dmg_mult": 1.5, "desc": "Um soco carregado de ki!"},
        {"name": "🌀 Cem Golpes", "mana_cost": 20, "dmg_mult": 1.7, "desc": "Cem golpes em menos de um segundo!"},
        {"name": "⚡ Raio de Ki", "mana_cost": 25, "dmg_mult": 2.0, "desc": "Energia vital lançada como projétil!"},
        {"name": "🧘 Golpe Transcendente", "mana_cost": 40, "dmg_mult": 2.5, "desc": "O corpo e a mente em perfeita harmonia."},
    ],
    "Bardo": [
        {"name": "🎵 Nota Dissonante", "mana_cost": 10, "dmg_mult": 1.3, "stun_chance": 0.3, "desc": "Uma nota que atordoa o adversário!"},
        {"name": "🎸 Acorde do Caos", "mana_cost": 20, "dmg_mult": 1.6, "desc": "Um acorde que confunde os sentidos."},
        {"name": "🎺 Fanfarra da Ruína", "mana_cost": 15, "dmg_mult": 1.5, "weaken": True, "desc": "Enfraquece o inimigo com música mágica."},
        {"name": "🎻 Sinfonia da Destruição", "mana_cost": 35, "dmg_mult": 2.2, "desc": "A música se torna força destrutiva pura!"},
    ],
}

# ================= BOSS SKILLS =================
BOSS_SKILLS = {
    "default": [
        {"name": "⚔️ Golpe Brutal", "dmg_mult": 1.5, "desc": "Um golpe poderoso!"},
        {"name": "🌀 Rajada de Energia", "dmg_mult": 1.8, "desc": "Energia sombria liberada!", "weaken": True},
        {"name": "💥 Impacto Sísmico", "dmg_mult": 2.0, "desc": "Tremor que abala a terra!", "stun_chance": 0.25},
        {"name": "🔥 Chama Infernal", "dmg_mult": 1.6, "desc": "Fogo que corrói a alma!", "poison": True},
        {"name": "💀 Golpe Devastador", "dmg_mult": 2.5, "desc": "Ataque com toda a força bestial!"},
    ],
    "Slime Rei": [
        {"name": "🟢 Divisão Slime", "dmg_mult": 1.2, "desc": "Se divide em múltiplos ataques!", "poison": True},
        {"name": "💧 Ácido Corrosivo", "dmg_mult": 1.8, "desc": "Ácido que corrói armaduras!", "weaken": True},
        {"name": "🌊 Onda Viscosa", "dmg_mult": 2.0, "desc": "Uma onda de gosma envolve tudo!", "stun_chance": 0.3},
    ],
    "Ent Ancião": [
        {"name": "🌿 Chicote de Raiz", "dmg_mult": 1.6, "desc": "Raízes presas nos tornozelos!"},
        {"name": "🌪️ Tempestade de Espinhos", "dmg_mult": 1.9, "desc": "Espinhos cortam por todos os lados!", "poison": True},
        {"name": "🌳 Esmagamento Arbóreo", "dmg_mult": 2.3, "desc": "Galhos gigantes esmagam!", "stun_chance": 0.35},
    ],
    "Faraó Amaldiçoado": [
        {"name": "🔮 Maldição Antiga", "dmg_mult": 1.7, "desc": "Maldição que drena a vida!", "weaken": True},
        {"name": "💀 Exército dos Mortos", "dmg_mult": 2.0, "desc": "Múmias surgem para atacar!"},
        {"name": "⚡ Raio do Deserto", "dmg_mult": 2.4, "desc": "A energia do deserto em forma de raio!", "stun_chance": 0.2},
    ],
    "Yeti Colossal": [
        {"name": "❄️ Sopro Ártico", "dmg_mult": 1.8, "desc": "Vento gelado que congela tudo!", "stun_chance": 0.4},
        {"name": "🏔️ Avalanche", "dmg_mult": 2.1, "desc": "Uma avalanche de neve e pedra!"},
        {"name": "💪 Soco Colossal", "dmg_mult": 2.6, "desc": "Punho do tamanho de uma rocha!"},
    ],
    "Dragão de Magma": [
        {"name": "🔥 Chama Draconiana", "dmg_mult": 2.0, "desc": "Fogo que derrete aço!", "poison": True},
        {"name": "💨 Rugido de Magma", "dmg_mult": 1.7, "desc": "O rugido causa ondas de calor!", "stun_chance": 0.2},
        {"name": "🌋 Erupção Dracônica", "dmg_mult": 2.8, "desc": "O corpo do dragão explode em lava!"},
    ],
    "Senhor das Sombras": [
        {"name": "🌑 Trevas Absolutas", "dmg_mult": 2.2, "desc": "A escuridão consome tudo!", "weaken": True},
        {"name": "👁️ Olhar Paralisante", "dmg_mult": 1.5, "desc": "Um olhar que paralisa a alma!", "stun_chance": 0.5},
        {"name": "💀 Ceifada da Morte", "dmg_mult": 3.0, "desc": "A foice da morte avança!", "poison": True},
    ],
}

# ================= ACHIEVEMENTS =================
ACHIEVEMENTS = [
    # === COMBATE (30) ===
    {"id": "first_kill", "cat": "⚔️ Combate", "name": "Primeiro Sangue", "desc": "Derrote seu primeiro monstro", "xp": 100, "stat": "monsters_killed", "threshold": 1},
    {"id": "kills_10", "cat": "⚔️ Combate", "name": "Caçador Iniciante", "desc": "Derrote 10 monstros", "xp": 100, "stat": "monsters_killed", "threshold": 10},
    {"id": "kills_50", "cat": "⚔️ Combate", "name": "Caçador Experiente", "desc": "Derrote 50 monstros", "xp": 200, "stat": "monsters_killed", "threshold": 50},
    {"id": "kills_100", "cat": "⚔️ Combate", "name": "Caçador Veterano", "desc": "Derrote 100 monstros", "xp": 400, "stat": "monsters_killed", "threshold": 100},
    {"id": "kills_250", "cat": "⚔️ Combate", "name": "Exterminador", "desc": "Derrote 250 monstros", "xp": 600, "stat": "monsters_killed", "threshold": 250},
    {"id": "kills_500", "cat": "⚔️ Combate", "name": "Anjo da Morte", "desc": "Derrote 500 monstros", "xp": 900, "stat": "monsters_killed", "threshold": 500},
    {"id": "kills_1000", "cat": "⚔️ Combate", "name": "Lenda das Batalhas", "desc": "Derrote 1000 monstros", "xp": 1500, "stat": "monsters_killed", "threshold": 1000},
    {"id": "boss_1", "cat": "⚔️ Combate", "name": "Caçador de Bosses", "desc": "Derrote seu primeiro boss", "xp": 150, "stat": "bosses_defeated", "threshold": 1},
    {"id": "boss_3", "cat": "⚔️ Combate", "name": "Domador de Colossais", "desc": "Derrote 3 bosses", "xp": 300, "stat": "bosses_defeated", "threshold": 3},
    {"id": "boss_5", "cat": "⚔️ Combate", "name": "Terror dos Bosses", "desc": "Derrote 5 bosses", "xp": 500, "stat": "bosses_defeated", "threshold": 5},
    {"id": "boss_10", "cat": "⚔️ Combate", "name": "Matador de Deuses", "desc": "Derrote 10 bosses", "xp": 900, "stat": "bosses_defeated", "threshold": 10},
    {"id": "boss_20", "cat": "⚔️ Combate", "name": "Lenda Imortal", "desc": "Derrote 20 bosses", "xp": 1500, "stat": "bosses_defeated", "threshold": 20},
    {"id": "first_boss_unique", "cat": "⚔️ Combate", "name": "Primeiro Colossus", "desc": "Derrote o primeiro boss de level", "xp": 300, "special": "level_boss_1"},
    {"id": "all_level_bosses", "cat": "⚔️ Combate", "name": "Conquistador dos Reinos", "desc": "Derrote todos os 20 bosses de level (um por reino)", "xp": 10000, "special": "all_level_bosses"},
    {"id": "slime_rei", "cat": "⚔️ Combate", "name": "Massacrador de Slimes", "desc": "Derrote o Slime Rei", "xp": 300, "special": "boss_slime_rei"},
    {"id": "dragon", "cat": "⚔️ Combate", "name": "Dragoneante", "desc": "Derrote o Dragão de Magma", "xp": 600, "special": "boss_dragao"},
    {"id": "shadow_lord", "cat": "⚔️ Combate", "name": "Derrotando as Sombras", "desc": "Derrote o Senhor das Sombras", "xp": 750, "special": "boss_sombras"},
    {"id": "pvp_win_1", "cat": "⚔️ Combate", "name": "Guerreiro PvP", "desc": "Vença seu primeiro duelo PvP", "xp": 150, "special": "pvp_win_1"},
    {"id": "pvp_win_10", "cat": "⚔️ Combate", "name": "Campeão de Duelos", "desc": "Vença 10 duelos PvP", "xp": 450, "special": "pvp_win_10"},
    {"id": "no_damage", "cat": "⚔️ Combate", "name": "Intocável", "desc": "Derrote um boss com HP acima de 80%", "xp": 450, "special": "boss_no_damage"},
    {"id": "crit_master", "cat": "⚔️ Combate", "name": "Mestre dos Críticos", "desc": "Acerte 50 golpes críticos", "xp": 400, "special": "crit_50"},
    {"id": "poison_master", "cat": "⚔️ Combate", "name": "Mestre dos Venenos", "desc": "Envenene 20 inimigos", "xp": 200, "special": "poison_20"},
    {"id": "stun_master", "cat": "⚔️ Combate", "name": "Mestre dos Atordoamentos", "desc": "Atordoe 15 inimigos", "xp": 200, "special": "stun_15"},
    {"id": "class_master", "cat": "⚔️ Combate", "name": "Mestre da Classe", "desc": "Use todas as habilidades da sua classe em batalha", "xp": 300, "special": "all_skills_used"},
    {"id": "dungeon_10", "cat": "⚔️ Combate", "name": "Explorador de Masmorras", "desc": "Complete 10 masmorras", "xp": 300, "special": "dungeons_10"},
    {"id": "dungeon_50", "cat": "⚔️ Combate", "name": "Mestre das Masmorras", "desc": "Complete 50 masmorras", "xp": 750, "special": "dungeons_50"},
    {"id": "legendary_drop", "cat": "⚔️ Combate", "name": "Agraciado pelos Deuses", "desc": "Receba um item Lendário de drop de boss", "xp": 450, "special": "legendary_drop"},
    {"id": "divine_drop", "cat": "⚔️ Combate", "name": "Toque Divino", "desc": "Receba um item Divino de drop de boss", "xp": 1200, "special": "divine_drop"},
    {"id": "comeback_win", "cat": "⚔️ Combate", "name": "Vingança Épica", "desc": "Derrote um boss após usar o botão Vingança", "xp": 450, "special": "comeback_win"},
    {"id": "training_champion", "cat": "⚔️ Combate", "name": "Dedicação Suprema", "desc": "Use o sistema de treinamento 10 vezes", "xp": 300, "special": "training_10"},
    # === EXPLORAÇÃO (20) ===
    {"id": "explore_1", "cat": "🗺️ Exploração", "name": "Aventureiro", "desc": "Explore pela primeira vez", "xp": 50, "stat": "areas_explored", "threshold": 1},
    {"id": "explore_10", "cat": "🗺️ Exploração", "name": "Explorador", "desc": "Explore 10 áreas", "xp": 100, "stat": "areas_explored", "threshold": 10},
    {"id": "explore_50", "cat": "🗺️ Exploração", "name": "Desbravador", "desc": "Explore 50 áreas", "xp": 300, "stat": "areas_explored", "threshold": 50},
    {"id": "explore_100", "cat": "🗺️ Exploração", "name": "Cartógrafo", "desc": "Explore 100 áreas", "xp": 600, "stat": "areas_explored", "threshold": 100},
    {"id": "explore_250", "cat": "🗺️ Exploração", "name": "Lenda dos Mapas", "desc": "Explore 250 áreas", "xp": 1200, "stat": "areas_explored", "threshold": 250},
    {"id": "world_2", "cat": "🗺️ Exploração", "name": "Além das Fronteiras", "desc": "Desbloqueie o segundo mundo", "xp": 200, "special": "world_2"},
    {"id": "world_3", "cat": "🗺️ Exploração", "name": "Viajante dos Reinos", "desc": "Desbloqueie o terceiro mundo", "xp": 400, "special": "world_3"},
    {"id": "world_4", "cat": "🗺️ Exploração", "name": "Mestre dos Portais", "desc": "Desbloqueie o quarto mundo", "xp": 600, "special": "world_4"},
    {"id": "world_5", "cat": "🗺️ Exploração", "name": "Conquistador Dimensional", "desc": "Desbloqueie o quinto mundo", "xp": 900, "special": "world_5"},
    {"id": "all_worlds", "cat": "🗺️ Exploração", "name": "Senhor de Todos os Mundos", "desc": "Desbloqueie todos os mundos", "xp": 1800, "special": "all_worlds"},
    {"id": "secret_dungeon", "cat": "🗺️ Exploração", "name": "Descobridor do Abismo", "desc": "Encontre uma masmorra secreta", "xp": 300, "special": "secret_dungeon"},
    {"id": "mimic_survive", "cat": "🗺️ Exploração", "name": "Sobrevivente do Mímico", "desc": "Sobreviva a um ataque de Mímico", "xp": 200, "special": "mimic_survive"},
    {"id": "hunt_10", "cat": "🗺️ Exploração", "name": "Caçador do Reino", "desc": "Cace 10 vezes no mesmo reino", "xp": 150, "special": "hunt_10_same"},
    {"id": "full_map", "cat": "🗺️ Exploração", "name": "Cartógrafo Completo", "desc": "Descubra todas as localizações de um mundo", "xp": 450, "special": "full_map_world"},
    {"id": "night_explorer", "cat": "🗺️ Exploração", "name": "Criatura da Noite", "desc": "Explore às 3 da manhã (horário do servidor)", "xp": 100, "special": "night_explore"},
    {"id": "fast_explore", "cat": "🗺️ Exploração", "name": "Relâmpago", "desc": "Explore 5 áreas em uma hora", "xp": 150, "special": "fast_5_explore"},
    {"id": "dungeon_first_time", "cat": "🗺️ Exploração", "name": "Primeiro nas Sombras", "desc": "Entre em uma masmorra pela primeira vez", "xp": 100, "special": "first_dungeon"},
    {"id": "loot_100", "cat": "🗺️ Exploração", "name": "Saqueador", "desc": "Colete 100 itens no total", "xp": 300, "special": "loot_100"},
    {"id": "survive_trap", "cat": "🗺️ Exploração", "name": "Sortudo", "desc": "Sobreviva a 5 armadilhas em masmorras", "xp": 150, "special": "survive_5_traps"},
    {"id": "no_fail_explore", "cat": "🗺️ Exploração", "name": "Explorador Invicto", "desc": "Explore 10 vezes seguidas sem falhar", "xp": 400, "special": "explore_10_streak"},
    # === ECONOMIA (20) ===
    {"id": "coins_1k", "cat": "💰 Economia", "name": "Primeiras Moedas", "desc": "Ganhe 1.000 CSI no total", "xp": 100, "stat": "total_coins_earned", "threshold": 1000},
    {"id": "coins_10k", "cat": "💰 Economia", "name": "Comerciante", "desc": "Ganhe 10.000 CSI no total", "xp": 200, "stat": "total_coins_earned", "threshold": 10000},
    {"id": "coins_50k", "cat": "💰 Economia", "name": "Mercador Rico", "desc": "Ganhe 50.000 CSI no total", "xp": 450, "stat": "total_coins_earned", "threshold": 50000},
    {"id": "coins_100k", "cat": "💰 Economia", "name": "Milionário", "desc": "Ganhe 100.000 CSI no total", "xp": 900, "stat": "total_coins_earned", "threshold": 100000},
    {"id": "coins_500k", "cat": "💰 Economia", "name": "Magnata", "desc": "Ganhe 500.000 CSI no total", "xp": 1800, "stat": "total_coins_earned", "threshold": 500000},
    {"id": "buy_first_item", "cat": "💰 Economia", "name": "Primeira Compra", "desc": "Compre seu primeiro item na loja", "xp": 50, "special": "buy_first"},
    {"id": "buy_legendary", "cat": "💰 Economia", "name": "Comprador de Sonhos", "desc": "Compre um item Lendário", "xp": 300, "special": "buy_legendary"},
    {"id": "sell_items", "cat": "💰 Economia", "name": "Comerciante Nato", "desc": "Venda 20 itens", "xp": 150, "special": "sell_20"},
    {"id": "equip_epic", "cat": "💰 Economia", "name": "Equipado para a Guerra", "desc": "Equipe um item Épico ou melhor", "xp": 150, "special": "equip_epic"},
    {"id": "equip_legendary", "cat": "💰 Economia", "name": "Escolhido pelos Deuses", "desc": "Equipe um item Lendário", "xp": 450, "special": "equip_legendary"},
    {"id": "equip_divine", "cat": "💰 Economia", "name": "Avatar Divino", "desc": "Equipe um item Divino", "xp": 1200, "special": "equip_divine"},
    {"id": "full_set", "cat": "💰 Economia", "name": "Arsenal Completo", "desc": "Equipe arma e armadura ao mesmo tempo", "xp": 100, "special": "full_equip"},
    {"id": "inv_20", "cat": "💰 Economia", "name": "Colecionador", "desc": "Tenha 20 itens no inventário", "xp": 100, "special": "inv_20"},
    {"id": "inv_50", "cat": "💰 Economia", "name": "Acumulador", "desc": "Tenha 50 itens no inventário", "xp": 200, "special": "inv_50"},
    {"id": "potion_10", "cat": "💰 Economia", "name": "Alquimista", "desc": "Beba 10 poções", "xp": 100, "special": "potion_10"},
    {"id": "broke", "cat": "💰 Economia", "name": "Falido", "desc": "Fique com 0 moedas CSI", "xp": 50, "special": "broke"},
    {"id": "xp_10k", "cat": "💰 Economia", "name": "Veterano", "desc": "Acumule 10.000 XP no total", "xp": 150, "stat": "total_xp_earned", "threshold": 10000},
    {"id": "xp_100k", "cat": "💰 Economia", "name": "Lendário do XP", "desc": "Acumule 100.000 XP no total", "xp": 750, "stat": "total_xp_earned", "threshold": 100000},
    {"id": "xp_500k", "cat": "💰 Economia", "name": "Transcendente", "desc": "Acumule 500.000 XP no total", "xp": 1800, "stat": "total_xp_earned", "threshold": 500000},
    {"id": "work_first", "cat": "💰 Economia", "name": "Trabalhador Honesto", "desc": "Trabalhe pela primeira vez", "xp": 50, "special": "work_first"},
    # === PROGRESSÃO (20) ===
    {"id": "level_5", "cat": "🌟 Progressão", "name": "Primeiros Passos", "desc": "Alcance o nível 5", "xp": 100, "stat": "level", "threshold": 5},
    {"id": "level_10", "cat": "🌟 Progressão", "name": "Guerreiro dos Campos", "desc": "Alcance o nível 10", "xp": 150, "stat": "level", "threshold": 10},
    {"id": "level_20", "cat": "🌟 Progressão", "name": "Cavaleiro do Reino", "desc": "Alcance o nível 20", "xp": 300, "stat": "level", "threshold": 20},
    {"id": "level_30", "cat": "🌟 Progressão", "name": "Herói Consagrado", "desc": "Alcance o nível 30", "xp": 500, "stat": "level", "threshold": 30},
    {"id": "level_40", "cat": "🌟 Progressão", "name": "Campeão dos Reinos", "desc": "Alcance o nível 40", "xp": 750, "stat": "level", "threshold": 40},
    {"id": "level_50", "cat": "🌟 Progressão", "name": "Lenda Viva", "desc": "Alcance o nível 50", "xp": 1200, "stat": "level", "threshold": 50},
    {"id": "level_60", "cat": "🌟 Progressão", "name": "Deus Mortal", "desc": "Alcance o nível 60", "xp": 2250, "stat": "level", "threshold": 60},
    {"id": "class_chosen", "cat": "🌟 Progressão", "name": "O Chamado", "desc": "Escolha sua classe", "xp": 100, "special": "class_chosen"},
    {"id": "pet_first", "cat": "🌟 Progressão", "name": "Tamer", "desc": "Tenha seu primeiro pet", "xp": 100, "special": "pet_first"},
    {"id": "pet_rare", "cat": "🌟 Progressão", "name": "Dono de Raridades", "desc": "Capture um pet Raro ou melhor", "xp": 300, "special": "pet_rare"},
    {"id": "guild_join", "cat": "🌟 Progressão", "name": "Companheiro de Guilda", "desc": "Entre em uma guilda", "xp": 150, "special": "guild_join"},
    {"id": "guild_master", "cat": "🌟 Progressão", "name": "Líder Supremo", "desc": "Crie ou lidere uma guilda", "xp": 450, "special": "guild_master"},
    {"id": "quest_1", "cat": "🌟 Progressão", "name": "Missão Aceita", "desc": "Complete sua primeira quest", "xp": 100, "special": "quest_1"},
    {"id": "quest_10", "cat": "🌟 Progressão", "name": "Herói das Missões", "desc": "Complete 10 quests", "xp": 300, "special": "quest_10"},
    {"id": "quest_25", "cat": "🌟 Progressão", "name": "Lenda das Quests", "desc": "Complete 25 quests", "xp": 750, "special": "quest_25"},
    {"id": "alignment_hero", "cat": "🌟 Progressão", "name": "Coração de Herói", "desc": "Alcance o alinhamento Herói", "xp": 300, "special": "alignment_hero"},
    {"id": "alignment_villain", "cat": "🌟 Progressão", "name": "Sombra do Caos", "desc": "Alcance o alinhamento Vilão", "xp": 300, "special": "alignment_villain"},
    {"id": "job_first", "cat": "🌟 Progressão", "name": "Trabalhador da Cidade", "desc": "Aceite seu primeiro emprego", "xp": 100, "special": "job_first"},
    {"id": "defend_city", "cat": "🌟 Progressão", "name": "Guardião das Muralhas", "desc": "Defenda a cidade pela primeira vez", "xp": 150, "special": "defend_city"},
    {"id": "farm_first_harvest", "cat": "🌟 Progressão", "name": "Fazendeiro", "desc": "Faça sua primeira colheita na fazenda", "xp": 100, "special": "farm_harvest"},
    # === SECRETAS (10) ===
    {"id": "death_cheat", "cat": "🔮 Secreta", "name": "Frágil Imortalidade", "desc": "Sobreviva com 1 HP em batalha", "xp": 750, "special": "zero_hp_survive"},
    {"id": "max_mana", "cat": "🔮 Secreta", "name": "Reservatório Arcano", "desc": "Use mana máxima em uma única batalha", "xp": 450, "special": "max_mana_battle"},
    {"id": "all_classes", "cat": "🔮 Secreta", "name": "O Polivalente", "desc": "Mude de classe 3 vezes", "xp": 1200, "special": "all_classes_tried"},
    {"id": "midnight_boss", "cat": "🔮 Secreta", "name": "Criatura da Meia-Noite", "desc": "Derrote um boss à meia-noite", "xp": 600, "special": "boss_midnight"},
    {"id": "rich_broke", "cat": "🔮 Secreta", "name": "Ciclo da Fortuna", "desc": "Acumule 10k CSI e depois fique com 0", "xp": 450, "special": "rich_then_broke"},
    {"id": "solo_all_bosses", "cat": "🔮 Secreta", "name": "Solitário Lendário", "desc": "Derrote todos os bosses de level sozinho", "xp": 1500, "special": "solo_all_bosses"},
    {"id": "perfect_boss", "cat": "🔮 Secreta", "name": "Combate Perfeito", "desc": "Derrote um boss sem ser envenenado/atordoado", "xp": 900, "special": "perfect_boss_fight"},
    {"id": "first_message", "cat": "🔮 Secreta", "name": "O Começo", "desc": "Seja o primeiro jogador do servidor", "xp": 150, "special": "first_player"},
    {"id": "born_survivor", "cat": "🔮 Secreta", "name": "Nascido para Sobreviver", "desc": "Sobreviva a 100 batalhas", "xp": 750, "special": "survived_100_battles"},
    {"id": "max_training", "cat": "🔮 Secreta", "name": "Além dos Limites", "desc": "Maximize todos os boosts de treinamento", "xp": 1200, "special": "max_all_training"},
]

TRAINING_OPTIONS = {
    "forca":      {"cost": 50,  "atk_boost": 5,  "emoji": "⚔️", "desc": "Aumenta ATK em +5 permanentemente"},
    "defesa":     {"cost": 50,  "def_boost": 5,  "emoji": "🛡️", "desc": "Aumenta DEF em +5 permanentemente"},
    "vitalidade": {"cost": 50,  "hp_boost": 20,  "emoji": "❤️", "desc": "Aumenta HP Máximo em +20 permanentemente"},
    "intensivo":  {"cost": 200, "atk_boost": 10, "def_boost": 10, "hp_boost": 35, "emoji": "🔥", "desc": "Treino intensivo: +10 ATK, +10 DEF, +35 HP Max"},
    "mana":       {"cost": 50,  "mana_boost": 15, "emoji": "💎", "desc": "Aumenta Mana Máxima em +15 (requer Livro de Feitiços)"},
}

# ================= MONSTER EQUIPMENT DROPS =================
# Cada monstro pode dropar itens comuns ou incomuns específicos
MONSTER_DROPS = {
    # Campos Iniciais
    "Slime": [
        {"name": "Gel de Slime", "type": "resource"},
        {"name": "Espada Enferrujada", "type": "weapon", "rarity": "Comum"},
    ],
    "Goblin": [
        {"name": "Faca de Goblin", "type": "weapon", "rarity": "Comum"},
        {"name": "Escudo de Madeira", "type": "armor", "rarity": "Comum"},
        {"name": "Espada Pequena", "type": "weapon", "rarity": "Incomum"},
    ],
    "Lobo": [
        {"name": "Pele de Lobo", "type": "resource"},
        {"name": "Garra de Lobo", "type": "resource"},
        {"name": "Colete de Couro", "type": "armor", "rarity": "Incomum"},
    ],
    "Esqueleto": [
        {"name": "Osso Afiado", "type": "weapon", "rarity": "Comum"},
        {"name": "Armadura Óssea", "type": "armor", "rarity": "Incomum"},
        {"name": "Espada de Ferro", "type": "weapon", "rarity": "Incomum"},
    ],
    "Rato Selvagem": [
        {"name": "Pelo de Rato", "type": "resource"},
        {"name": "Adaga de Pedra", "type": "weapon", "rarity": "Comum"},
    ],
    # Floresta Élfica
    "Ent Menor": [
        {"name": "Galho Mágico", "type": "resource"},
        {"name": "Cajado de Madeira Viva", "type": "weapon", "rarity": "Incomum"},
        {"name": "Vestes de Batalha", "type": "armor", "rarity": "Incomum"},
    ],
    "Aranha Gigante": [
        {"name": "Seda Venenosa", "type": "resource"},
        {"name": "Adaga Venenosa", "type": "weapon", "rarity": "Raro"},
        {"name": "Capa de Sombras", "type": "armor", "rarity": "Raro"},
    ],
    "Elfo Renegado": [
        {"name": "Arco Élfic", "type": "weapon", "rarity": "Raro"},
        {"name": "Capa de Sombras", "type": "armor", "rarity": "Raro"},
        {"name": "Armadura Élfica", "type": "armor", "rarity": "Raro"},
    ],
    "Espírito Florestal": [
        {"name": "Essência Etérea", "type": "resource"},
        {"name": "Vestes Arcanas", "type": "armor", "rarity": "Raro"},
    ],
    # Deserto
    "Múmia": [
        {"name": "Ataduras Mágicas", "type": "resource"},
        {"name": "Cetro Antigo", "type": "weapon", "rarity": "Raro"},
        {"name": "Armadura de Ouro", "type": "armor", "rarity": "Épico"},
    ],
    "Escorpião": [
        {"name": "Veneno de Escorpião", "type": "resource"},
        {"name": "Garras de Escorpião", "type": "weapon", "rarity": "Incomum"},
        {"name": "Lança do Caçador", "type": "weapon", "rarity": "Raro"},
    ],
    "Escorpião Gigante": [
        {"name": "Veneno Concentrado", "type": "resource"},
        {"name": "Lança do Caçador", "type": "weapon", "rarity": "Raro"},
        {"name": "Armadura de Escamas", "type": "armor", "rarity": "Incomum"},
    ],
    # Tundra
    "Urso Glacial": [
        {"name": "Pele Ártica", "type": "resource"},
        {"name": "Machado de Gelo", "type": "weapon", "rarity": "Raro"},
        {"name": "Cota Encantada", "type": "armor", "rarity": "Raro"},
    ],
    "Troll de Gelo": [
        {"name": "Cristal de Gelo", "type": "resource"},
        {"name": "Armadura de Permafrost", "type": "armor", "rarity": "Épico"},
        {"name": "Clava Titânica", "type": "weapon", "rarity": "Raro"},
    ],
    "Lobo Glacial": [
        {"name": "Pele de Gelo", "type": "resource"},
        {"name": "Machado Rúnico", "type": "weapon", "rarity": "Raro"},
    ],
    # Vulcão
    "Salamandra": [
        {"name": "Escama de Fogo", "type": "resource"},
        {"name": "Lâmina Flamejante", "type": "weapon", "rarity": "Épico"},
        {"name": "Armadura Flamejante", "type": "armor", "rarity": "Épico"},
    ],
    "Demônio Menor": [
        {"name": "Fragmento Infernal", "type": "resource"},
        {"name": "Espada Demoníaca", "type": "weapon", "rarity": "Épico"},
        {"name": "Armadura do Inferno", "type": "armor", "rarity": "Épico"},
        {"name": "Katana Demoníaca", "type": "weapon", "rarity": "Épico"},
    ],
    "Elemental de Fogo": [
        {"name": "Núcleo de Magma", "type": "resource"},
        {"name": "Cajado Arcano", "type": "weapon", "rarity": "Épico"},
    ],
    # Clima especial
    "Vampiro": [
        {"name": "Sangue de Vampiro", "type": "resource"},
        {"name": "Foice Maldita", "type": "weapon", "rarity": "Raro"},
        {"name": "Armadura das Sombras", "type": "armor", "rarity": "Épico"},
    ],
    "Lobo Lunático": [
        {"name": "Pele Lunar", "type": "resource"},
        {"name": "Garras da Lua", "type": "weapon", "rarity": "Raro"},
    ],
    "Espectro Noturno": [
        {"name": "Essência Sombria", "type": "resource"},
        {"name": "Vestes do Sábio", "type": "armor", "rarity": "Raro"},
    ],
    "Elemental do Trovão": [
        {"name": "Núcleo Elétrico", "type": "resource"},
        {"name": "Katana Relâmpago", "type": "weapon", "rarity": "Raro"},
        {"name": "Armadura da Tempestade", "type": "armor", "rarity": "Épico"},
    ],
    "Fantasma": [
        {"name": "Ectoplasma", "type": "resource"},
        {"name": "Vestes Arcanas", "type": "armor", "rarity": "Raro"},
    ],
    # default fallback
    "default": [
        {"name": "Couro Bruto", "type": "resource"},
        {"name": "Dente de Monstro", "type": "resource"},
    ]
}

# ================= SISTEMA DE CHAVES DE DUNGEON SECRETA =================
# Chaves são dropadas de baús nas dungeons comuns e desbloqueiam dungeons secretas
DUNGEON_KEY_DROP_CHANCE = 0.08  # 8% de sorte — chave também cai a cada 5 dungeons completadas

def get_world_secret_dungeon_keys(world_data):
    """Retorna lista de chaves de dungeons secretas do mundo atual."""
    keys = []
    for sd in world_data.get("secret_dungeons", []):
        if "key_name" in sd:
            keys.append(sd["key_name"])
    return keys

def player_has_key(player, key_name):
    """Verifica se o jogador tem a chave especificada."""
    return key_name in player.get("inventory", [])

def consume_key(player, key_name):
    """Remove a chave do inventário do jogador."""
    if key_name in player.get("inventory", []):
        player["inventory"].remove(key_name)
        return True
    return False

# Raridade de drop por tipo de monstro por dado
HUNT_DROP_CHANCE = {
    "resource": 0.40,           # 40% recurso
    "weapon_common": 0.15,      # 15% arma comum/incomum
    "weapon_rare": 0.05,        # 5% arma rara (do monstro)
    "weapon_epic": 0.02,        # 2% épico (só monstros fortes)
    "weapon_legendary": 0.005,  # 0.5% lendário (monstros de elite em reinos altos)
    "weapon_mythic": 0.0005,    # 0.05% Mítico (monstros de elite nos 13 novos reinos)
    # Ancestral/Divino/Primordial: apenas via boss especial de dungeon secreta
}

# Reinos avançados (novas áreas) permitem drops mais raros de monstros
HIGH_LEVEL_WORLDS = {62, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180}
HIGH_LEVEL_DROP_BONUS = {
    "legendary": 0.008,   # 0.8% lendário em reinos avançados
    "mythic": 0.001,      # 0.1% Mítico em reinos avançados
    "ancestral": 0.0002   # 0.02% Ancestral nos reinos mais altos (100+)
}

# ================= SISTEMA DE CLIMA =================
WEATHER_TYPES = {
    "sol": {
        "emoji": "☀️", "name": "Sol Abrasador",
        "monster_boost": 1.0, "drop_boost": 1.0,
        "special_monsters": [],
        "desc": "O sol brilha forte — criaturas normais habitam a região."
    },
    "chuva": {
        "emoji": "🌧️", "name": "Chuva Torrencial",
        "monster_boost": 1.2, "drop_boost": 1.1,
        "special_monsters": ["Elemental da Água", "Sapo Gigante", "Serpente Lodosa"],
        "desc": "A chuva atrai criaturas aquáticas e torna os monstros mais agressivos!"
    },
    "noite": {
        "emoji": "🌙", "name": "Noite Profunda",
        "monster_boost": 1.4, "drop_boost": 1.2,
        "special_monsters": ["Vampiro", "Lobo Lunático", "Espectro Noturno"],
        "desc": "A escuridão acorda as criaturas mais perigosas..."
    },
    "tempestade": {
        "emoji": "⛈️", "name": "Tempestade Elétrica",
        "monster_boost": 1.5, "drop_boost": 1.3,
        "special_monsters": ["Elemental do Trovão", "Grifo Tempestuoso"],
        "desc": "Raios caem ao redor — criaturas elétricas surgem das nuvens!"
    },
    "neblina": {
        "emoji": "🌫️", "name": "Neblina Arcana",
        "monster_boost": 1.3, "drop_boost": 1.4,
        "special_monsters": ["Fantasma", "Banshee", "Wisp Errante"],
        "desc": "A neblina mágica esconde criaturas espectrais e segredos antigos..."
    },
    "lua_sangue": {
        "emoji": "🩸🌕", "name": "LUA DE SANGUE",
        "monster_boost": 2.5, "drop_boost": 2.0,
        "special_monsters": ["Lobo Colossal", "Vampiro Ancião", "Demônio de Sangue", "Boss da Lua de Sangue"],
        "desc": "⚠️ LUA DE SANGUE! Monstros extremamente poderosos surgem — mas as recompensas são extraordinárias!"
    }
}

# Clima atual (global, muda a cada X tempo)
CURRENT_WEATHER = {"type": "sol", "changed_at": 0}

# ================= SISTEMA DE PERÍODO (DIA/NOITE) =================
TIME_PERIODS = {
    "amanhecer": {
        "emoji": "🌅", "name": "Amanhecer",
        "desc": "O sol nasce no horizonte. A névoa da noite se dissipa lentamente.",
        "xp_mult": 1.0, "coin_mult": 1.0, "special": "Monstros noturnos enfraquecem."
    },
    "dia": {
        "emoji": "☀️", "name": "Dia",
        "desc": "Plena luz do dia. Criaturas da floresta se movem livremente.",
        "xp_mult": 1.1, "coin_mult": 1.1, "special": "Exploração mais segura."
    },
    "entardecer": {
        "emoji": "🌇", "name": "Entardecer",
        "desc": "O sol se põe. Criaturas crepusculares surgem nos arredores.",
        "xp_mult": 1.2, "coin_mult": 1.15, "special": "Chance maior de drops raros."
    },
    "noite": {
        "emoji": "🌙", "name": "Noite",
        "desc": "A escuridão domina. Monstros mais fortes rondam os caminhos.",
        "xp_mult": 1.3, "coin_mult": 1.2, "special": "Monstros mais perigosos, recompensas maiores."
    },
    "meia_noite": {
        "emoji": "🕛", "name": "Meia-Noite",
        "desc": "O silêncio total... apenas os mais corajosos ousam agir agora.",
        "xp_mult": 1.5, "coin_mult": 1.4, "special": "Hora dos lendários! Drops especiais possíveis."
    },
}
PERIOD_ORDER = ["amanhecer", "dia", "entardecer", "noite", "meia_noite"]
CURRENT_PERIOD = {"type": "dia", "changed_at": 0}

# ================= PET EVOLUTION SYSTEM =================
PET_EVOLUTIONS = {
    "Slime Bebê": {
        "level_required": 5, "next": "Slime Adolescente",
        "next_data": {"name": "Slime Adolescente", "emoji": "💧", "rarity": "Incomum", "bonus_hp": 25, "bonus_atk": 8}
    },
    "Slime Adolescente": {
        "level_required": 15, "next": "Slime Mestre",
        "next_data": {"name": "Slime Mestre", "emoji": "💠", "rarity": "Raro", "bonus_hp": 50, "bonus_atk": 18}
    },
    "Coelho Mágico": {
        "level_required": 8, "next": "Coelho Arcano",
        "next_data": {"name": "Coelho Arcano", "emoji": "🐰", "rarity": "Raro", "bonus_hp": 35, "bonus_atk": 12}
    },
    "Coelho Arcano": {
        "level_required": 20, "next": "Lebre Celestial",
        "next_data": {"name": "Lebre Celestial", "emoji": "✨", "rarity": "Épico", "bonus_hp": 65, "bonus_atk": 22}
    },
    "Fada da Floresta": {
        "level_required": 10, "next": "Fada Élfica",
        "next_data": {"name": "Fada Élfica", "emoji": "🧚", "rarity": "Épico", "bonus_hp": 45, "bonus_atk": 18}
    },
    "Fada Élfica": {
        "level_required": 25, "next": "Fada Primordial",
        "next_data": {"name": "Fada Primordial", "emoji": "🌟", "rarity": "Mítico", "bonus_hp": 90, "bonus_atk": 40}
    },
    "Lobo Cinzento": {
        "level_required": 15, "next": "Lobo das Sombras",
        "next_data": {"name": "Lobo das Sombras", "emoji": "🐺", "rarity": "Raro", "bonus_hp": 50, "bonus_atk": 25}
    },
    "Lobo das Sombras": {
        "level_required": 28, "next": "Lobo Alpha Lendário",
        "next_data": {"name": "Lobo Alpha Lendário", "emoji": "🐺", "rarity": "Lendário", "bonus_hp": 100, "bonus_atk": 55}
    },
    "Coruja Espectral": {
        "level_required": 18, "next": "Coruja do Destino",
        "next_data": {"name": "Coruja do Destino", "emoji": "🦉", "rarity": "Épico", "bonus_hp": 65, "bonus_atk": 30}
    },
    "Coruja do Destino": {
        "level_required": 32, "next": "Coruja Divina",
        "next_data": {"name": "Coruja Divina", "emoji": "🦉", "rarity": "Mítico", "bonus_hp": 120, "bonus_atk": 60}
    },
    "Dragão de Gelo Bebê": {
        "level_required": 25, "next": "Dragão de Gelo Jovem",
        "next_data": {"name": "Dragão de Gelo Jovem", "emoji": "🐉", "rarity": "Mítico", "bonus_hp": 140, "bonus_atk": 70}
    },
    "Dragão de Gelo Jovem": {
        "level_required": 40, "next": "Dragão de Gelo Ancião",
        "next_data": {"name": "Dragão de Gelo Ancião", "emoji": "❄️", "rarity": "Divino", "bonus_hp": 250, "bonus_atk": 120}
    },

    # ── Mundo 10 ──────────────────────────────────────────────────────
    "Espírito da Floresta": {
        "level_required": 16, "next": "Espírito Ancião",
        "next_data": {"name": "Espírito Ancião", "emoji": "🌲", "rarity": "Lendário", "bonus_hp": 75, "bonus_atk": 35}
    },
    "Espírito Ancião": {
        "level_required": 30, "next": "Espírito Primordial",
        "next_data": {"name": "Espírito Primordial", "emoji": "🌳", "rarity": "Mítico", "bonus_hp": 140, "bonus_atk": 65}
    },

    # ── Mundo 20 ──────────────────────────────────────────────────────
    "Escorpião Dourado": {
        "level_required": 22, "next": "Escorpião Carmesim",
        "next_data": {"name": "Escorpião Carmesim", "emoji": "🦂", "rarity": "Épico", "bonus_hp": 65, "bonus_atk": 32}
    },
    "Escorpião Carmesim": {
        "level_required": 35, "next": "Escorpião Lendário",
        "next_data": {"name": "Escorpião Lendário", "emoji": "🦂", "rarity": "Lendário", "bonus_hp": 120, "bonus_atk": 58}
    },
    "Escaravelho Místico": {
        "level_required": 25, "next": "Escaravelho Sagrado",
        "next_data": {"name": "Escaravelho Sagrado", "emoji": "🪲", "rarity": "Lendário", "bonus_hp": 85, "bonus_atk": 42}
    },
    "Escaravelho Sagrado": {
        "level_required": 38, "next": "Escaravelho Divino",
        "next_data": {"name": "Escaravelho Divino", "emoji": "🪲", "rarity": "Mítico", "bonus_hp": 160, "bonus_atk": 80}
    },
    "Esfinge Menor": {
        "level_required": 28, "next": "Esfinge Guardiã",
        "next_data": {"name": "Esfinge Guardiã", "emoji": "🦁", "rarity": "Mítico", "bonus_hp": 110, "bonus_atk": 55}
    },
    "Esfinge Guardiã": {
        "level_required": 42, "next": "Esfinge Imortal",
        "next_data": {"name": "Esfinge Imortal", "emoji": "🦁", "rarity": "Divino", "bonus_hp": 210, "bonus_atk": 105}
    },

    # ── Mundo 30 ──────────────────────────────────────────────────────
    "Raposa Ártica": {
        "level_required": 30, "next": "Raposa das Tempestades",
        "next_data": {"name": "Raposa das Tempestades", "emoji": "🦊", "rarity": "Lendário", "bonus_hp": 95, "bonus_atk": 48}
    },
    "Raposa das Tempestades": {
        "level_required": 44, "next": "Raposa Celestial",
        "next_data": {"name": "Raposa Celestial", "emoji": "🦊", "rarity": "Mítico", "bonus_hp": 175, "bonus_atk": 88}
    },
    "Fênix de Gelo": {
        "level_required": 32, "next": "Fênix de Cristal",
        "next_data": {"name": "Fênix de Cristal", "emoji": "🦅", "rarity": "Divino", "bonus_hp": 180, "bonus_atk": 90}
    },
    "Fênix de Cristal": {
        "level_required": 46, "next": "Fênix Primordial",
        "next_data": {"name": "Fênix Primordial", "emoji": "🕊️", "rarity": "Primordial", "bonus_hp": 320, "bonus_atk": 160}
    },

    # ── Mundo 40 ──────────────────────────────────────────────────────
    "Salamandra de Fogo": {
        "level_required": 34, "next": "Salamandra Dracônica",
        "next_data": {"name": "Salamandra Dracônica", "emoji": "🦎", "rarity": "Lendário", "bonus_hp": 110, "bonus_atk": 55}
    },
    "Salamandra Dracônica": {
        "level_required": 47, "next": "Salamandra Divina",
        "next_data": {"name": "Salamandra Divina", "emoji": "🦎", "rarity": "Mítico", "bonus_hp": 200, "bonus_atk": 100}
    },
    "Fênix Carmesim": {
        "level_required": 36, "next": "Fênix Solar",
        "next_data": {"name": "Fênix Solar", "emoji": "🔥", "rarity": "Mítico", "bonus_hp": 150, "bonus_atk": 75}
    },
    "Fênix Solar": {
        "level_required": 49, "next": "Fênix Eterna",
        "next_data": {"name": "Fênix Eterna", "emoji": "☀️", "rarity": "Divino", "bonus_hp": 270, "bonus_atk": 135}
    },
    "Dragão de Magma": {
        "level_required": 38, "next": "Dragão Vulcânico",
        "next_data": {"name": "Dragão Vulcânico", "emoji": "🐲", "rarity": "Divino", "bonus_hp": 200, "bonus_atk": 100}
    },
    "Dragão Vulcânico": {
        "level_required": 52, "next": "Dragão Primordial do Caos",
        "next_data": {"name": "Dragão Primordial do Caos", "emoji": "🐉", "rarity": "Primordial", "bonus_hp": 380, "bonus_atk": 190}
    },

    # ── Mundo 50 ──────────────────────────────────────────────────────
    "Espectro Sombrio": {
        "level_required": 42, "next": "Espectro do Abismo",
        "next_data": {"name": "Espectro do Abismo", "emoji": "👤", "rarity": "Mítico", "bonus_hp": 170, "bonus_atk": 85}
    },
    "Espectro do Abismo": {
        "level_required": 54, "next": "Espectro Eterno",
        "next_data": {"name": "Espectro Eterno", "emoji": "🌑", "rarity": "Divino", "bonus_hp": 290, "bonus_atk": 145}
    },
    "Elemental do Vazio": {
        "level_required": 44, "next": "Elemental Cósmico",
        "next_data": {"name": "Elemental Cósmico", "emoji": "🌀", "rarity": "Divino", "bonus_hp": 220, "bonus_atk": 110}
    },
    "Elemental Cósmico": {
        "level_required": 56, "next": "Elemental Primordial",
        "next_data": {"name": "Elemental Primordial", "emoji": "⚫", "rarity": "Primordial", "bonus_hp": 400, "bonus_atk": 200}
    },
    "Entidade Cósmica": {
        "level_required": 46, "next": "Entidade Astral",
        "next_data": {"name": "Entidade Astral", "emoji": "🌟", "rarity": "Divino", "bonus_hp": 300, "bonus_atk": 150}
    },
    "Entidade Astral": {
        "level_required": 58, "next": "Deus Primordial",
        "next_data": {"name": "Deus Primordial", "emoji": "✨", "rarity": "Primordial", "bonus_hp": 500, "bonus_atk": 250}
    },

    # ── Mundo 60 (já são top, mas ganham 1 evolução final cada) ──────
    "Anjo Guardião": {
        "level_required": 50, "next": "Arcanjo Guardião",
        "next_data": {"name": "Arcanjo Guardião", "emoji": "👼", "rarity": "Primordial", "bonus_hp": 380, "bonus_atk": 190}
    },
    "Querubim Guerreiro": {
        "level_required": 52, "next": "Serafim Guerreiro",
        "next_data": {"name": "Serafim Guerreiro", "emoji": "😇", "rarity": "Primordial", "bonus_hp": 450, "bonus_atk": 225}
    },
    "Arcanjo Primordial": {
        "level_required": 55, "next": "Deus da Guerra Celestial",
        "next_data": {"name": "Deus da Guerra Celestial", "emoji": "⚔️", "rarity": "Primordial", "bonus_hp": 700, "bonus_atk": 350}
    },
}

# ================= SPELL BOOK / LIVRO DE FEITIÇOS =================
MANA_CATEGORIES = [
    {"id": "goblin",     "name": "🟤 Goblin",       "level_req": 12, "mana_mult": 1.0, "desc": "Iniciante das artes mágicas"},
    {"id": "aprendiz",   "name": "⚪ Aprendiz",     "level_req": 16, "mana_mult": 1.1, "desc": "Começa a entender os fundamentos"},
    {"id": "estudante",  "name": "🟢 Estudante",    "level_req": 20, "mana_mult": 1.2, "desc": "Progresso notável no estudo"},
    {"id": "praticante", "name": "🔵 Praticante",   "level_req": 25, "mana_mult": 1.35,"desc": "Domínio básico das magias"},
    {"id": "adepto",     "name": "🟣 Adepto",       "level_req": 30, "mana_mult": 1.5, "desc": "Feitiços fluem naturalmente"},
    {"id": "veterano",   "name": "🟡 Veterano",     "level_req": 35, "mana_mult": 1.7, "desc": "Veterano das artes arcanas"},
    {"id": "mestre",     "name": "🟠 Mestre",       "level_req": 40, "mana_mult": 2.0, "desc": "Mestre indiscutível da magia"},
    {"id": "arcano",     "name": "🔴 Arcano",       "level_req": 45, "mana_mult": 2.3, "desc": "Acessa planos superiores de poder"},
    {"id": "lendario",   "name": "⭐ Lendário",     "level_req": 52, "mana_mult": 2.7, "desc": "Lenda das artes mágicas"},
    {"id": "supremo",    "name": "💎 Supremo",      "level_req": 58, "mana_mult": 3.5, "desc": "O pico absoluto do poder arcano"},
]

SPELL_BOOK_SKILLS = {
    "Mago": [
        {"cat": "goblin",     "name": "🔥 Chispa Arcana",      "mana_cost": 5,  "dmg_mult": 1.2, "desc": "Uma centelha mágica básica."},
        {"cat": "aprendiz",   "name": "❄️ Flecha de Gelo",     "mana_cost": 12, "dmg_mult": 1.5, "slow": True, "desc": "Desacelera o inimigo."},
        {"cat": "estudante",  "name": "⚡ Tempestade Arcana",  "mana_cost": 20, "dmg_mult": 1.8, "desc": "Múltiplos raios arcanos."},
        {"cat": "praticante", "name": "🌪️ Tufão de Magia",    "mana_cost": 30, "dmg_mult": 2.2, "desc": "Vento mágico devasta."},
        {"cat": "adepto",     "name": "🔮 Singularidade",      "mana_cost": 40, "dmg_mult": 2.6, "ignore_def": True, "desc": "Destrói defesas."},
        {"cat": "veterano",   "name": "🌌 Portal do Caos",     "mana_cost": 50, "dmg_mult": 3.0, "desc": "Abre uma fenda dimensional."},
        {"cat": "mestre",     "name": "☄️ Meteoro Arcano",    "mana_cost": 60, "dmg_mult": 3.5, "desc": "Um meteoro mágico devastador!"},
        {"cat": "arcano",     "name": "🌠 Colapso Estelar",   "mana_cost": 75, "dmg_mult": 4.0, "stun_chance": 0.4, "desc": "O poder das estrelas."},
        {"cat": "lendario",   "name": "💥 Explosão Cósmica",  "mana_cost": 90, "dmg_mult": 4.8, "desc": "O universo colapsa no alvo."},
        {"cat": "supremo",    "name": "⚗️ Aniquilação Total", "mana_cost": 120,"dmg_mult": 6.0, "ignore_def": True, "desc": "Poder absoluto e irresistível!"},
    ],
    "Necromante": [
        {"cat": "goblin",     "name": "💀 Toque da Morte",     "mana_cost": 5,  "dmg_mult": 1.2, "desc": "A morte roça o inimigo."},
        {"cat": "aprendiz",   "name": "🦴 Esqueleto Básico",   "mana_cost": 12, "dmg_mult": 1.4, "desc": "Invoca um guerreiro ósseo."},
        {"cat": "estudante",  "name": "☠️ Praga",              "mana_cost": 20, "dmg_mult": 1.6, "poison": True, "desc": "Praga que corrói a alma."},
        {"cat": "praticante", "name": "🌑 Escudo da Morte",    "mana_cost": 30, "dmg_mult": 1.2, "self_heal": 40, "desc": "Cura drenando o inimigo."},
        {"cat": "adepto",     "name": "💀 Exército dos Mortos","mana_cost": 45, "dmg_mult": 2.5, "desc": "Horda de não-mortos ataca!"},
        {"cat": "veterano",   "name": "🌒 Eclipse Sombrio",    "mana_cost": 55, "dmg_mult": 3.0, "weaken": True, "desc": "Escuridão que enfraquece."},
        {"cat": "mestre",     "name": "⚰️ Ressurreição Caótica","mana_cost": 65, "dmg_mult": 3.5, "self_heal": 60, "desc": "Drena vida em massa."},
        {"cat": "arcano",     "name": "🩸 Maré de Sangue",     "mana_cost": 80, "dmg_mult": 4.2, "poison": True, "desc": "Sangue que envenena a área."},
        {"cat": "lendario",   "name": "🌚 Véu da Morte",       "mana_cost": 95, "dmg_mult": 5.0, "desc": "A morte se materializa."},
        {"cat": "supremo",    "name": "💀 Exterminação",       "mana_cost": 130,"dmg_mult": 6.5, "ignore_def": True, "desc": "Nada escapa à morte absoluta!"},
    ],
    "Paladino": [
        {"cat": "goblin",     "name": "✨ Bênção Menor",       "mana_cost": 5,  "dmg_mult": 1.1, "self_heal": 10, "desc": "A luz cura levemente."},
        {"cat": "aprendiz",   "name": "☀️ Raio Sagrado",       "mana_cost": 12, "dmg_mult": 1.5, "desc": "Um raio de luz divina."},
        {"cat": "estudante",  "name": "🛡️ Barreira Sagrada",   "mana_cost": 20, "dmg_mult": 1.0, "self_heal": 35, "def_bonus": 15, "desc": "Barreira protetora."},
        {"cat": "praticante", "name": "⚔️ Espada da Justiça",  "mana_cost": 30, "dmg_mult": 2.0, "desc": "Justiça divina corporificada."},
        {"cat": "adepto",     "name": "🌟 Nova de Luz",        "mana_cost": 40, "dmg_mult": 2.4, "stun_chance": 0.3, "desc": "Explosão de luz sagrada."},
        {"cat": "veterano",   "name": "👼 Proteção Angélica",  "mana_cost": 50, "dmg_mult": 1.5, "self_heal": 60, "desc": "Anjos protegem o paladino."},
        {"cat": "mestre",     "name": "⭐ Purificação Divina", "mana_cost": 65, "dmg_mult": 3.0, "desc": "Purifica toda maldade."},
        {"cat": "arcano",     "name": "☀️ Arma Celestial",    "mana_cost": 80, "dmg_mult": 3.8, "ignore_def": True, "desc": "Arma forjada pelos céus."},
        {"cat": "lendario",   "name": "🕊️ Intervenção Divina", "mana_cost": 100,"dmg_mult": 4.5, "self_heal": 80, "desc": "Os deuses intervêm pessoalmente."},
        {"cat": "supremo",    "name": "🌈 Juízo Final",        "mana_cost": 140,"dmg_mult": 6.0, "stun_chance": 0.5, "desc": "O julgamento eterno cai!"},
    ],
    "Druida": [
        {"cat": "goblin",     "name": "🌿 Cura Menor",         "mana_cost": 5,  "dmg_mult": 1.0, "self_heal": 20, "desc": "A natureza cura."},
        {"cat": "aprendiz",   "name": "🌱 Espinhos Vivos",     "mana_cost": 12, "dmg_mult": 1.4, "poison": True, "desc": "Espinhos que envenenam."},
        {"cat": "estudante",  "name": "🐺 Forma Animal",       "mana_cost": 20, "dmg_mult": 1.8, "desc": "Se transforma em besta."},
        {"cat": "praticante", "name": "🌪️ Tempestade Natural", "mana_cost": 30, "dmg_mult": 2.2, "desc": "A natureza se rebela."},
        {"cat": "adepto",     "name": "🌳 Raízes Antigas",     "mana_cost": 40, "dmg_mult": 1.8, "stun_chance": 0.4, "desc": "Raízes antigas imobilizam."},
        {"cat": "veterano",   "name": "⚡ Relâmpago Natural",  "mana_cost": 50, "dmg_mult": 2.8, "desc": "Raio convocado da natureza."},
        {"cat": "mestre",     "name": "🌊 Tsunami Arcano",     "mana_cost": 65, "dmg_mult": 3.2, "desc": "Onda massiva de energia natural."},
        {"cat": "arcano",     "name": "🦅 Forma Celestial",    "mana_cost": 80, "dmg_mult": 3.8, "self_heal": 50, "desc": "Transforma-se em ser celestial."},
        {"cat": "lendario",   "name": "🌍 Terremoto",          "mana_cost": 100,"dmg_mult": 4.6, "stun_chance": 0.5, "desc": "A terra se parte ao meio."},
        {"cat": "supremo",    "name": "🌳 Árvore do Mundo",   "mana_cost": 150,"dmg_mult": 6.0, "self_heal": 100, "desc": "O poder da criação inteira!"},
    ],
}

# Classes de suporte que podem curar aliados em grupo
SUPPORT_CLASSES = {"Paladino", "Druida", "Mago", "Bardo", "Necromante"}

# ================= KINGDOM SYSTEM (para Reis) =================
KINGDOM_DEFAULTS = {
    "name": None,  # Nome do reino do jogador
    "population": 100,
    "economy": "Neutra",  # Ruim / Neutra / Boa / Excelente
    "army": "Neutra",
    "resources": [],
    "bio": "",
    "wars_won": 0,
    "trades": 0,
}


# ================= RARITY DICE BONUS =================
RARITY_DICE_BONUS = {
    "Comum": 0,
    "Incomum": 0,
    "Raro": 1,
    "Épico": 1,
    "Lendário": 2,
    "Mítico": 2,
    "Divino": 3,
    "Primordial": 4,
}

# ================= RARIDADES (expandidas) =================
RARITIES = {
    "Comum": {"color": 0xAAAAAA, "emoji": "⚪"},
    "Incomum": {"color": 0x00FF00, "emoji": "🟢"},
    "Raro": {"color": 0x0000FF, "emoji": "🔵"},
    "Épico": {"color": 0x800080, "emoji": "🟣"},
    "Lendário": {"color": 0xFFD700, "emoji": "🟡"},
    "Mítico": {"color": 0xFF4400, "emoji": "🔴"},
    "Ancestral": {"color": 0xFF8C00, "emoji": "🟠"},
    "Divino": {"color": 0x00FFFF, "emoji": "💎"},
    "Primordial": {"color": 0xFF00FF, "emoji": "🌈"}
}

# ================= PETS POR MUNDO =================
PETS = {
    1: [
        {"name": "Slime Bebê", "emoji": "💧", "rarity": "Comum", "bonus_hp": 10, "bonus_atk": 3},
        {"name": "Rato Selvagem Domesticado", "emoji": "🐀", "rarity": "Comum", "bonus_hp": 8, "bonus_atk": 4},
        {"name": "Lagarta Arcana", "emoji": "🐛", "rarity": "Comum", "bonus_hp": 9, "bonus_atk": 3},
        {"name": "Fungo Espiritual", "emoji": "🍄", "rarity": "Comum", "bonus_hp": 12, "bonus_atk": 2},
        {"name": "Coelho Mágico", "emoji": "🐰", "rarity": "Incomum", "bonus_hp": 15, "bonus_atk": 5},
        {"name": "Fada da Floresta", "emoji": "🧚", "rarity": "Raro", "bonus_hp": 20, "bonus_atk": 8}
    ],
    10: [
        {"name": "Toupeira das Sombras", "emoji": "🦡", "rarity": "Comum", "bonus_hp": 18, "bonus_atk": 6},
        {"name": "Cogumelo Sombrio", "emoji": "🍄", "rarity": "Comum", "bonus_hp": 16, "bonus_atk": 7},
        {"name": "Lobo Cinzento", "emoji": "🐺", "rarity": "Incomum", "bonus_hp": 25, "bonus_atk": 12},
        {"name": "Coruja Espectral", "emoji": "🦉", "rarity": "Raro", "bonus_hp": 30, "bonus_atk": 15},
        {"name": "Espírito da Floresta", "emoji": "👻", "rarity": "Épico", "bonus_hp": 40, "bonus_atk": 20}
    ],
    20: [
        {"name": "Besouro do Deserto", "emoji": "🪲", "rarity": "Comum", "bonus_hp": 22, "bonus_atk": 9},
        {"name": "Cobra das Areias", "emoji": "🐍", "rarity": "Comum", "bonus_hp": 20, "bonus_atk": 11},
        {"name": "Escorpião Dourado", "emoji": "🦂", "rarity": "Raro", "bonus_hp": 35, "bonus_atk": 18},
        {"name": "Escaravelho Místico", "emoji": "🪲", "rarity": "Épico", "bonus_hp": 45, "bonus_atk": 23},
        {"name": "Esfinge Menor", "emoji": "🦁", "rarity": "Lendário", "bonus_hp": 60, "bonus_atk": 30}
    ],
    30: [
        {"name": "Raposa Ártica", "emoji": "🦊", "rarity": "Épico", "bonus_hp": 50, "bonus_atk": 25},
        {"name": "Dragão de Gelo Bebê", "emoji": "🐉", "rarity": "Lendário", "bonus_hp": 70, "bonus_atk": 35},
        {"name": "Fênix de Gelo", "emoji": "🦅", "rarity": "Mítico", "bonus_hp": 100, "bonus_atk": 50}
    ],
    40: [
        {"name": "Salamandra de Fogo", "emoji": "🦎", "rarity": "Épico", "bonus_hp": 55, "bonus_atk": 28},
        {"name": "Fênix Carmesim", "emoji": "🔥", "rarity": "Lendário", "bonus_hp": 80, "bonus_atk": 40},
        {"name": "Dragão de Magma", "emoji": "🐲", "rarity": "Mítico", "bonus_hp": 120, "bonus_atk": 60}
    ],
    50: [
        {"name": "Espectro Sombrio", "emoji": "👤", "rarity": "Lendário", "bonus_hp": 90, "bonus_atk": 45},
        {"name": "Elemental do Vazio", "emoji": "🌀", "rarity": "Mítico", "bonus_hp": 130, "bonus_atk": 65},
        {"name": "Entidade Cósmica", "emoji": "✨", "rarity": "Divino", "bonus_hp": 180, "bonus_atk": 90}
    ],
    60: [
        {"name": "Anjo Guardião", "emoji": "👼", "rarity": "Divino", "bonus_hp": 200, "bonus_atk": 100},
        {"name": "Querubim Guerreiro", "emoji": "😇", "rarity": "Divino", "bonus_hp": 250, "bonus_atk": 120},
        {"name": "Arcanjo Primordial", "emoji": "🕊️", "rarity": "Primordial", "bonus_hp": 400, "bonus_atk": 200}
    ]
}

# ================= PETS NOVOS (EXPANSÃO) =================
PETS_EXTRA = {
    1: [
        {"name": "Girino Mágico",     "emoji": "🐸", "rarity": "Comum",    "bonus_hp": 8,  "bonus_atk": 3,  "can_mount": False},
        {"name": "Borboleta de Cristal","emoji":"🦋","rarity": "Comum",    "bonus_hp": 9,  "bonus_atk": 2,  "can_mount": False},
        {"name": "Filhote de Urso",   "emoji": "🐻", "rarity": "Incomum",  "bonus_hp": 18, "bonus_atk": 6,  "can_mount": True,  "mount_bonus_def": 5,  "mount_bonus_spd": 2},
        {"name": "Raposa das Ruínas", "emoji": "🦊", "rarity": "Raro",     "bonus_hp": 22, "bonus_atk": 9,  "can_mount": True,  "mount_bonus_def": 8,  "mount_bonus_spd": 5},
        {"name": "Unicórnio Bebê",    "emoji": "🦄", "rarity": "Épico",    "bonus_hp": 40, "bonus_atk": 18, "can_mount": True,  "mount_bonus_def": 15, "mount_bonus_spd": 10},
    ],
    10: [
        {"name": "Morcego das Cavernas","emoji":"🦇","rarity": "Comum",    "bonus_hp": 14, "bonus_atk": 6,  "can_mount": False},
        {"name": "Tritão Sombrio",    "emoji": "🦎", "rarity": "Incomum",  "bonus_hp": 22, "bonus_atk": 9,  "can_mount": False},
        {"name": "Cavalo Negro Élfico","emoji":"🐴", "rarity": "Raro",     "bonus_hp": 30, "bonus_atk": 10, "can_mount": True,  "mount_bonus_def": 12, "mount_bonus_spd": 8},
        {"name": "Grifo Menor",       "emoji": "🦅", "rarity": "Épico",    "bonus_hp": 45, "bonus_atk": 22, "can_mount": True,  "mount_bonus_def": 18, "mount_bonus_spd": 14},
    ],
    20: [
        {"name": "Escorpião das Areias","emoji":"🦂","rarity": "Incomum",  "bonus_hp": 20, "bonus_atk": 10, "can_mount": False},
        {"name": "Camelo Místico",    "emoji": "🐪", "rarity": "Raro",     "bonus_hp": 32, "bonus_atk": 12, "can_mount": True,  "mount_bonus_def": 10, "mount_bonus_spd": 6},
        {"name": "Serpente Faraônica","emoji": "🐍", "rarity": "Épico",    "bonus_hp": 48, "bonus_atk": 24, "can_mount": True,  "mount_bonus_def": 20, "mount_bonus_spd": 12},
        {"name": "Roc das Dunas",     "emoji": "🦅", "rarity": "Lendário", "bonus_hp": 65, "bonus_atk": 33, "can_mount": True,  "mount_bonus_def": 30, "mount_bonus_spd": 20},
    ],
    30: [
        {"name": "Lobo do Ártico",    "emoji": "🐺", "rarity": "Raro",     "bonus_hp": 30, "bonus_atk": 15, "can_mount": True,  "mount_bonus_def": 12, "mount_bonus_spd": 9},
        {"name": "Urso Polar Místico","emoji": "🐻", "rarity": "Épico",    "bonus_hp": 55, "bonus_atk": 27, "can_mount": True,  "mount_bonus_def": 22, "mount_bonus_spd": 10},
        {"name": "Cão do Permafrost", "emoji": "❄️", "rarity": "Lendário", "bonus_hp": 75, "bonus_atk": 38, "can_mount": True,  "mount_bonus_def": 35, "mount_bonus_spd": 18},
    ],
    40: [
        {"name": "Lagartixa de Magma","emoji": "🦎", "rarity": "Raro",     "bonus_hp": 35, "bonus_atk": 17, "can_mount": False},
        {"name": "Touro de Fogo",     "emoji": "🐂", "rarity": "Épico",    "bonus_hp": 58, "bonus_atk": 29, "can_mount": True,  "mount_bonus_def": 24, "mount_bonus_spd": 8},
        {"name": "Dragão de Cinzas",  "emoji": "🐲", "rarity": "Lendário", "bonus_hp": 88, "bonus_atk": 44, "can_mount": True,  "mount_bonus_def": 40, "mount_bonus_spd": 22},
        {"name": "Fênix Ancestral",   "emoji": "🔥", "rarity": "Mítico",   "bonus_hp": 130,"bonus_atk": 65, "can_mount": True,  "mount_bonus_def": 60, "mount_bonus_spd": 35},
    ],
    50: [
        {"name": "Sombra Equina",     "emoji": "🌑", "rarity": "Épico",    "bonus_hp": 55, "bonus_atk": 27, "can_mount": True,  "mount_bonus_def": 20, "mount_bonus_spd": 16},
        {"name": "Leviathan Menor",   "emoji": "🐋", "rarity": "Lendário", "bonus_hp": 92, "bonus_atk": 46, "can_mount": True,  "mount_bonus_def": 42, "mount_bonus_spd": 18},
        {"name": "Cavalo do Vazio",   "emoji": "🌀", "rarity": "Mítico",   "bonus_hp": 140,"bonus_atk": 70, "can_mount": True,  "mount_bonus_def": 65, "mount_bonus_spd": 38},
    ],
    60: [
        {"name": "Cervo Celestial",   "emoji": "🦌", "rarity": "Divino",   "bonus_hp": 210,"bonus_atk": 105,"can_mount": True,  "mount_bonus_def": 90, "mount_bonus_spd": 50},
        {"name": "Dragão Primordial", "emoji": "🐉", "rarity": "Primordial","bonus_hp":420,"bonus_atk": 210,"can_mount": True,  "mount_bonus_def": 180,"mount_bonus_spd": 90},
    ],
}

# Pets que já existiam no PETS original que também podem virar montaria
EXISTING_PETS_MOUNT = {
    "Lobo Cinzento":       {"can_mount": True,  "mount_bonus_def": 8,  "mount_bonus_spd": 5},
    "Raposa Ártica":       {"can_mount": True,  "mount_bonus_def": 14, "mount_bonus_spd": 9},
    "Dragão de Gelo Bebê": {"can_mount": True,  "mount_bonus_def": 20, "mount_bonus_spd": 12},
    "Fênix de Gelo":       {"can_mount": True,  "mount_bonus_def": 30, "mount_bonus_spd": 18},
    "Salamandra de Fogo":  {"can_mount": True,  "mount_bonus_def": 16, "mount_bonus_spd": 10},
    "Fênix Carmesim":      {"can_mount": True,  "mount_bonus_def": 25, "mount_bonus_spd": 16},
    "Dragão de Magma":     {"can_mount": True,  "mount_bonus_def": 35, "mount_bonus_spd": 22},
    "Esfinge Menor":       {"can_mount": True,  "mount_bonus_def": 18, "mount_bonus_spd": 12},
    "Arcanjo Primordial":  {"can_mount": True,  "mount_bonus_def": 120,"mount_bonus_spd": 60},
    "Entidade Cósmica":    {"can_mount": True,  "mount_bonus_def": 55, "mount_bonus_spd": 30},
    "Anjo Guardião":       {"can_mount": True,  "mount_bonus_def": 65, "mount_bonus_spd": 35},
    "Querubim Guerreiro":  {"can_mount": True,  "mount_bonus_def": 80, "mount_bonus_spd": 42},
}

def get_all_pets():
    """Retorna todos os pets (originais + extras) como lista flat por mundo"""
    all_pets = {}
    for world, pets in PETS.items():
        all_pets[world] = list(pets)
    for world, pets in PETS_EXTRA.items():
        if world not in all_pets:
            all_pets[world] = []
        all_pets[world].extend(pets)
    return all_pets

def get_pet_mount_data(pet_name):
    """Retorna dados de montaria de um pet, ou None se não pode ser montaria"""
    # Checar pets extras
    for pets in PETS_EXTRA.values():
        for p in pets:
            if p["name"] == pet_name:
                if p.get("can_mount"):
                    return {"mount_bonus_def": p.get("mount_bonus_def", 0), "mount_bonus_spd": p.get("mount_bonus_spd", 0)}
                return None
    # Checar pets originais com montaria
    if pet_name in EXISTING_PETS_MOUNT:
        return EXISTING_PETS_MOUNT[pet_name]
    return None
POTIONS = {
    "Poção de Vida Menor": {"rarity": "Comum", "hp_restore": 30, "emoji": "🧪"},
    "Poção de Vida": {"rarity": "Incomum", "hp_restore": 60, "emoji": "🧪"},
    "Poção de Vida Maior": {"rarity": "Raro", "hp_restore": 100, "emoji": "💊"},
    "Poção de Vida Superior": {"rarity": "Épico", "hp_restore": 150, "emoji": "💊"},
    "Elixir da Vida": {"rarity": "Lendário", "hp_restore": 250, "emoji": "⚗️"},
    "Elixir Divino": {"rarity": "Divino", "hp_restore": 500, "emoji": "✨"},
    "Poção de XP Menor": {"rarity": "Incomum", "xp_gain": 50, "emoji": "✨"},
    "Poção de XP": {"rarity": "Raro", "xp_gain": 100, "emoji": "✨"},
    "Poção de XP Maior": {"rarity": "Épico", "xp_gain": 200, "emoji": "💫"},
    "Elixir de XP": {"rarity": "Lendário", "xp_gain": 500, "emoji": "🌟"},
    "Poção de Força": {"rarity": "Raro", "temp_atk": 20, "duration": 5, "emoji": "💪"},
    "Poção de Defesa": {"rarity": "Raro", "temp_def": 15, "duration": 5, "emoji": "🛡️"},
    "Poção de Sorte": {"rarity": "Épico", "luck_bonus": 2, "duration": 3, "emoji": "🍀"},
    "Antídoto": {"rarity": "Comum", "cure_poison": True, "emoji": "💉"},
    "Poção de Ressurreição": {"rarity": "Mítico", "revive": True, "emoji": "💀"}
}

# ================= SISTEMA DE QUESTS =================
QUESTS = {
    1: [  # Campos Iniciais
        {
            "id": "campos_001",
            "name": "🐀 A Praga dos Ratos",
            "description": "Os aldeões estão desesperados. Ratos selvagens invadiram os campos e destroem as colheitas. Elimine 5 Ratos Selvagens e traga paz à região.",
            "type": "individual",
            "objective": "hunt",
            "target": "Rato Selvagem",
            "count": 5,
            "reward_xp": 150,
            "reward_coins": 30,
            "reward_item": "Poção de Vida",
            "lore": "Os aldeões sussurram sobre uma criatura maior controlando os ratos... O Rato Rei.",
            "npc": "Aldeão Theron",
            "difficulty": "Fácil"
        },
        {
            "id": "campos_002",
            "name": "🌿 Ervas do Curandeiro",
            "description": "O curandeiro da aldeia precisa de recursos para preparar remédios. Colete 8 recursos diferentes dos Campos Iniciais.",
            "type": "individual",
            "objective": "collect",
            "count": 8,
            "reward_xp": 100,
            "reward_coins": 20,
            "reward_item": "Poção de XP Menor",
            "lore": "O curandeiro menciona que as ervas desta região têm propriedades mágicas únicas desde a queda do primeiro meteoro.",
            "npc": "Curandeira Elara",
            "difficulty": "Fácil"
        },
        {
            "id": "campos_003",
            "name": "👑 A Caça ao Slime Rei",
            "description": "Uma equipe de aventureiros deve unir forças para derrotar o Slime Rei que aterroriza a região. Missão para 2-3 jogadores.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Slime Rei",
            "reward_xp": 400,
            "reward_coins": 80,
            "reward_item": "Espada de Ferro",
            "lore": "O Slime Rei absorveu a magia de um cristal antigo e agora é imune a ataques solitários. Apenas a força combinada pode pará-lo.",
            "npc": "Capitão Aldric",
            "difficulty": "Médio"
        },
        {
            "id": "campos_004",
            "name": "📚 O Diário Perdido",
            "description": "Um explorador perdeu seu diário precioso nos campos. Explore a região e encontre o artefato perdido.",
            "type": "individual",
            "objective": "explore",
            "count": 3,
            "reward_xp": 80,
            "reward_coins": 15,
            "reward_item": None,
            "lore": "O diário menciona uma rota secreta para as Montanhas Geladas... algo que nenhum mapa oficial mostra.",
            "npc": "Explorador Miko",
            "difficulty": "Fácil"
        }
    ],
    10: [  # Floresta Sombria
        {
            "id": "floresta_001",
            "name": "🕷️ O Ninho Maldito",
            "description": "Aranhas Gigantes bloqueiam a passagem principal da floresta. Elimine-as para reabrir o caminho dos mercadores.",
            "type": "individual",
            "objective": "hunt",
            "target": "Aranha Gigante",
            "count": 6,
            "reward_xp": 350,
            "reward_coins": 50,
            "reward_item": "Poção de Vida Maior",
            "lore": "As aranhas foram atraídas por um artefato élfico enterrado nas profundezas da floresta.",
            "npc": "Mercador Brynn",
            "difficulty": "Médio"
        },
        {
            "id": "floresta_002",
            "name": "🌲 O Ent Adormecido",
            "description": "Uma equipe deve despertar e pacificar o Ent Ancião antes que sua fúria destrua a floresta inteira.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Ent Ancião",
            "reward_xp": 900,
            "reward_coins": 150,
            "reward_item": "Armadura Élfica",
            "lore": "O Ent Ancião tem 3.000 anos. Ele guarda em sua memória o segredo da origem da floresta.",
            "npc": "Druida Sylvara",
            "difficulty": "Difícil"
        },
        {
            "id": "floresta_003",
            "name": "👻 Sussurros Espectrais",
            "description": "Espíritos Florestais perturbam a paz. Explore a floresta e descubra o que os inquieta.",
            "type": "individual",
            "objective": "explore",
            "count": 5,
            "reward_xp": 280,
            "reward_coins": 40,
            "reward_item": "Poção de XP",
            "lore": "Os espíritos mencionam uma 'Chave de Ébano' escondida nas raízes da árvore mais antiga.",
            "npc": "Espírito Ancião Vel",
            "difficulty": "Médio"
        }
    ],
    20: [  # Deserto das Almas
        {
            "id": "deserto_001",
            "name": "⚰️ A Maldição do Faraó",
            "description": "Múmias emergem das tumbas atacando viajantes. Três guerreiros devem adentrar a pirâmide e quebrar a maldição.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Faraó Amaldiçoado",
            "reward_xp": 1200,
            "reward_coins": 200,
            "reward_item": "Lâmina Flamejante",
            "lore": "O Faraó Kha-Mentu foi traído por seus sacerdotes e amaldiçoado para guardar seus próprios tesouros por toda a eternidade.",
            "npc": "Arqueólogo Ramses",
            "difficulty": "Difícil"
        },
        {
            "id": "deserto_002",
            "name": "🏺 Artefatos da Dinastia",
            "description": "Colete recursos únicos do deserto para reconstituir um artefato sagrado da civilização perdida.",
            "type": "individual",
            "objective": "collect",
            "count": 10,
            "reward_xp": 500,
            "reward_coins": 70,
            "reward_item": "Poção de Vida Superior",
            "lore": "Os artefatos da Dinastia de Ouro revelam que os humanos não foram os primeiros a habitar este mundo.",
            "npc": "Sábia Nefertiri",
            "difficulty": "Médio"
        },
        {
            "id": "deserto_003",
            "name": "🦂 Caçador de Escorpiões",
            "description": "Elimine Escorpiões Gigantes que envenenaram o único oásis da região.",
            "type": "individual",
            "objective": "hunt",
            "target": "Escorpião Gigante",
            "count": 8,
            "reward_xp": 600,
            "reward_coins": 90,
            "reward_item": "Antídoto",
            "lore": "O veneno dos escorpiões, se processado corretamente, pode curar qualquer doença conhecida.",
            "npc": "Nômade Hassan",
            "difficulty": "Médio"
        }
    ],
    30: [  # Montanhas Geladas
        {
            "id": "gelo_001",
            "name": "❄️ O Coração Congelado",
            "description": "O Yeti Colossal capturou três aldeões. Uma equipe deve resgatá-los e derrotar a besta.",
            "type": "team",
            "min_players": 2,
            "max_players": 3,
            "objective": "boss",
            "target": "Yeti Colossal",
            "reward_xp": 1800,
            "reward_coins": 280,
            "reward_item": "Armadura Rúnica",
            "lore": "O Yeti Colossal é na verdade um guardião criado pelos Titãs do Gelo para proteger um segredo nas profundezas da montanha.",
            "npc": "Ancião da Montanha Bjorn",
            "difficulty": "Muito Difícil"
        },
        {
            "id": "gelo_002",
            "name": "💎 Cristais da Profundidade",
            "description": "Minere cristais de gelo raros das cavernas mais profundas para o ferreiro da fortaleza.",
            "type": "individual",
            "objective": "collect",
            "count": 12,
            "reward_xp": 700,
            "reward_coins": 100,
            "reward_item": "Poção de XP Maior",
            "lore": "Os cristais de gelo desta região têm memória. Ao tocá-los, você vê fragmentos do passado.",
            "npc": "Ferreiro Helga",
            "difficulty": "Médio"
        }
    ],
    40: [  # Reino Vulcânico
        {
            "id": "vulcao_001",
            "name": "🐲 O Dragão de Magma",
            "description": "O Dragão de Magma desperta após séculos de sono. Três heróis devem uni-lo ou derrotá-lo.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Dragão de Magma",
            "reward_xp": 2500,
            "reward_coins": 400,
            "reward_item": "Excalibur",
            "lore": "O Dragão de Magma Ignarius foi o primeiro ser criado quando o mundo era apenas fogo e pedra. Ele guarda a Chama Original.",
            "npc": "Profeta Ignar",
            "difficulty": "Lendário"
        },
        {
            "id": "vulcao_002",
            "name": "🌋 A Forja Sagrada",
            "description": "Colete núcleos de fogo da lava ativa para reacender a Forja Sagrada dos anões.",
            "type": "individual",
            "objective": "collect",
            "count": 15,
            "reward_xp": 900,
            "reward_coins": 130,
            "reward_item": "Martelo do Trovão",
            "lore": "A Forja Sagrada foi usada para criar as primeiras armas dos deuses. Está apagada há 1.000 anos.",
            "npc": "Anão-Mestre Doran",
            "difficulty": "Difícil"
        }
    ],
    50: [  # Abismo Arcano
        {
            "id": "abismo_001",
            "name": "🌀 O Senhor das Sombras",
            "description": "O Senhor das Sombras ameaça consumir toda a realidade. Três campeões devem confrontá-lo no coração do abismo.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Senhor das Sombras",
            "reward_xp": 4000,
            "reward_coins": 600,
            "reward_item": "Cetro da Eternidade",
            "lore": "O Senhor das Sombras é um ser que existia antes do universo. Ele não deseja destruição — deseja retornar ao vazio primordial.",
            "npc": "Arquimago Zephyr",
            "difficulty": "Mítico"
        },
        {
            "id": "abismo_002",
            "name": "📖 Tomos Proibidos",
            "description": "Recupere tomos de conhecimento proibido espalhados pelo Abismo Arcano antes que se corrompam.",
            "type": "individual",
            "objective": "explore",
            "count": 7,
            "reward_xp": 1200,
            "reward_coins": 160,
            "reward_item": "Poção de XP Maior",
            "lore": "Os tomos foram escritos por entidades que existiram antes dos deuses. Seu conteúdo pode enlouquecer mortais despreparados.",
            "npc": "Bibliotecária Spectra",
            "difficulty": "Muito Difícil"
        }
    ],
    60: [  # Trono Celestial
        {
            "id": "celestial_001",
            "name": "👑 O Imperador Astral",
            "description": "A batalha final. Três lendas vivas devem enfrentar o Imperador Astral pelo destino de todos os mundos.",
            "type": "team",
            "min_players": 3,
            "max_players": 3,
            "objective": "boss",
            "target": "Imperador Astral",
            "reward_xp": 10000,
            "reward_coins": 1000,
            "reward_item": "Armadura do Primeiro Deus",
            "lore": "O Imperador Astral não é um inimigo — é um teste. Aqueles dignos de passar herdarão o trono do universo.",
            "npc": "Voz do Cosmos",
            "difficulty": "Primordial"
        },
        {
            "id": "celestial_002",
            "name": "🌟 Fragmentos da Criação",
            "description": "Reúna os Fragmentos Estelares espalhados pelo Trono Celestial para reconstruir o Cristal da Origem.",
            "type": "individual",
            "objective": "collect",
            "count": 20,
            "reward_xp": 3000,
            "reward_coins": 500,
            "reward_item": "Elixir Divino",
            "lore": "O Cristal da Origem foi destruído durante a Primeira Guerra Celestial. Sua reconstrução poderia criar — ou destruir — um novo universo.",
            "npc": "Guardião Estelar Auron",
            "difficulty": "Lendário"
        }
    ]
}

# ================= EMPREGOS DO REINO =================
JOBS = {
    "Ferreiro": {
        "emoji": "⚒️",
        "min_level": 5,
        "description": "Mestre das forjas. Cria e melhora equipamentos com materiais coletados.",
        "salary_coins": (8, 18),
        "salary_xp": (50, 120),
        "perks": [
            "Pode craftar armas únicas com `forjar arma`",
            "20% desconto ao comprar equipamentos na loja",
            "+2 bônus em dados ao coletar recursos de metal",
            "Pode identificar qualidade de itens com `inspecionar item`",
        ],
        "work_action": "Você martela o ferro com maestria. Faíscas voam enquanto uma lâmina toma forma.",
        "work_msgs": [
            "🔨 Você forja uma espada encomendada por um guarda. Trabalho limpo!",
            "⚒️ Um anão visita sua forja e aprova sua técnica — raro elogio!",
            "🔥 O fogo da forja revela um inchaço no aço. Você o reforja melhor ainda.",
            "⚙️ Você repara a armadura de um cavaleiro. Ele parte em silêncio, mas com respeito.",
            "⛏️ Uma lâmina perfeita sai da forja. Você a guarda — ninguém ainda merece.",
        ]
    },
    "Arcano": {
        "emoji": "🔮",
        "min_level": 5,
        "description": "Estudioso dos mistérios mágicos. Pesquisa feitiços e fenômenos sobrenaturais.",
        "salary_coins": (5, 12),
        "salary_xp": (80, 180),
        "perks": [
            "+15 de mana máxima permanente",
            "Pode usar `estudar magia` para ganhar XP extra",
            "50% de chance de identificar itens mágicos automaticamente",
            "Acesso à `biblioteca arcana` com lore exclusivo",
        ],
        "work_action": "Você mergulha em pergaminhos proibidos, decifrando runas antigas com os olhos vibrando.",
        "work_msgs": [
            "📚 Você decifra um pergaminho que ninguém leu por 300 anos. Revelação inquietante.",
            "✨ Uma fórmula mágica que você criou funciona pela primeira vez. Que satisfação!",
            "🌀 Uma anomalia arcana surge no laboratório. Você a contém por um fio.",
            "🔮 Você cataloga uma criatura mágica nunca documentada. A academia vai amar isso.",
            "💫 Seus estudos sobre o Abismo revelam uma verdade que deveria permanecer escondida.",
        ]
    },
    "Curandeiro": {
        "emoji": "💚",
        "min_level": 5,
        "description": "Guardião da vida. Cura ferimentos e doenças usando ervas e magia de cura.",
        "salary_coins": (6, 14),
        "salary_xp": (40, 100),
        "perks": [
            "Regenera +10 HP ao usar `trabalhar` além do salário",
            "Poções custam 30% menos na loja",
            "`curar` tem 25% de chance de curar completamente",
            "Pode usar `curar aliado @user` para curar outros jogadores",
        ],
        "work_action": "Suas mãos brilham com energia de cura enquanto você atende os feridos.",
        "work_msgs": [
            "💚 Você salva um mercador picado por uma aranha venenosa. Ele chora de alívio.",
            "🌿 Suas ervas curam uma criança com febre arcana. A mãe te abraça com força.",
            "⚕️ Um guerreiro chega quase morto. Você trabalha a noite toda. Ele sobrevive.",
            "🍃 Você descobre uma combinação de ervas que alivia veneno de drago. Anotado.",
            "💊 Você trata 12 aldeões com gripe mágica num só dia. Exausto, mas feliz.",
        ]
    },
    "Mercador": {
        "emoji": "💰",
        "min_level": 5,
        "description": "Comerciante astuto. Compra e vende itens obtendo lucro em cada transação.",
        "salary_coins": (15, 30),
        "salary_xp": (20, 60),
        "perks": [
            "Vende itens por 25% a mais de valor",
            "Acesso a `mercado negro` com itens raros",
            "Pode `negociar` para reduzir custo de compras",
            "+5 coins extras ao concluir qualquer quest",
        ],
        "work_action": "Você negocia com viajantes, comprando barato e vendendo caro com um sorriso encantador.",
        "work_msgs": [
            "💰 Você compra uma gema por 3 moedas e vende por 30. Que dia excelente!",
            "🤝 Um nobre paga o triplo por um item comum — ele nem sabia que era comum.",
            "📊 Sua rota comercial entre dois reinos rende 50% a mais este mês.",
            "🏪 Um rival tenta te sabotar. Você sorri e leva o cliente dele embora.",
            "💎 Você fareja um item raro num lote de bugigangas. Fortuna bem merecida.",
        ]
    },
    "Escriba": {
        "emoji": "📜",
        "min_level": 5,
        "description": "Guardião do conhecimento. Registra histórias, cria mapas e decifra textos antigos.",
        "salary_coins": (4, 10),
        "salary_xp": (100, 220),
        "perks": [
            "Descobre locais no mapa 2x mais rápido ao explorar",
            "Pode escrever `crônica` para ganhar XP bônus registrando aventuras",
            "Acesso a livros de lore exclusivos com `ler arquivo`",
            "Pode `mapear` áreas para revelar locais secretos",
        ],
        "work_action": "Sua pena raspa o pergaminho enquanto você registra histórias que outros esquecem.",
        "work_msgs": [
            "📜 Você traduz um mapa antigo e revela uma rota perdida há séculos.",
            "✍️ Um herói lendário te pede para escrever sua biografia. Honra inesperada.",
            "🗺️ Você completa o mapa de uma região inteira em uma semana. Perfeição.",
            "📖 Seu arquivo sobre criaturas mágicas se torna referência para todo o reino.",
            "🔍 Você encontra uma inconsistência em crônicas antigas. A história foi alterada.",
        ]
    },
    "Cavaleiro": {
        "emoji": "⚔️",
        "min_level": 10,
        "description": "Protetor jurado das cidades e do povo. Defende contra invasões, patrulha e mantém a ordem.",
        "salary_coins": (10, 22),
        "salary_xp": (60, 140),
        "perks": [
            "+20 HP máximos permanentes",
            "Pode usar `patrulhar` para ganhar XP e defender a cidade",
            "Pode convocar até 2 jogadores em defesa com `convocar cavaleiros`",
            "Resistência a dano aumentada em 15% durante batalhas",
        ],
        "work_action": "Você patrulha as ruas de armadura brilhante, a mão na espada, os olhos vigilantes.",
        "work_msgs": [
            "⚔️ Você intercepta ladrões no mercado. Eles fogem ao ver sua armadura.",
            "🛡️ Uma criança perdida chora no beco escuro. Você a leva em segurança para casa.",
            "🗡️ Um bêbado começa uma briga na taverna. Você a encerra com uma palavra firme.",
            "🏰 Você escolta uma caravana real por 3 dias. Sem incidentes. Exatamente como deve ser.",
            "⚡ Um bandido saca a espada. Você a desarma em um movimento. Sem derramamento de sangue.",
        ],
        "city_defense_cooldown": 3600  # 1 hora
    },
    "Guarda_Real": {
        "emoji": "🛡️",
        "min_level": 15,
        "description": "Elite da proteção real. Defende o reino com força e lealdade absolutas.",
        "salary_coins": (15, 30),
        "salary_xp": (80, 180),
        "perks": [
            "+35 HP máximos permanentes",
            "Pode usar `defender reino` em invasões de monstros",
            "Acesso a equipamentos da guarda real na loja",
            "Pode recrutar jogadores para a guarda com `recrutar guarda`",
        ],
        "work_action": "Você fica em posição de guarda nas portas do palácio, imóvel como uma estátua de aço.",
        "work_msgs": [
            "🛡️ Uma espiã tenta se infiltrar. Seu instinto a detecta antes de qualquer dano.",
            "👑 O rei te agradece pessoalmente por salvar sua filha de um sequestro.",
            "⚔️ Você treina recrutas por uma semana. Um deles tem talento genuíno.",
            "🏰 Um ataque surpresa na madrugada é repelido sob seu comando.",
            "🗡️ Você desarma um assassino dentro do salão do trono. Silenciosamente.",
        ]
    },
    "Rei": {
        "emoji": "👑",
        "min_level": 30,
        "description": "Soberano de uma cidade. Governa, toma decisões que afetam o povo e defende o reino.",
        "salary_coins": (0, 0),
        "salary_xp": (0, 0),
        "perks": [
            "Recebe tributo diário de coins baseado no nível da cidade",
            "Pode `governar` para tomar decisões que afetam eventos futuros",
            "Pode `decretar lei` com efeitos especiais no servidor",
            "Pode `convocar guerra` para batalhas massivas com outros jogadores",
            "Pode `nomear cavaleiro @user` para promover jogadores",
            "Recebe alertas de invasão antes de outros jogadores",
        ],
        "work_action": "Você assina decretos, ouve petições e toma decisões que afetam milhares de vidas.",
        "work_msgs": [
            "👑 Você media uma disputa de terras entre dois nobres. Decisão salomônica.",
            "⚖️ Uma petição popular chega: o povo quer menos impostos. Você considera.",
            "🏰 Um embaixador de outro reino chega. Diplomacia delicada se inicia.",
            "📜 Você assina um tratado de paz com os elfos. Trégua de 50 anos.",
            "👥 O povo celebra nas ruas ao ouvir sua decisão de perdoar uma dívida coletiva.",
        ]
    }
}

# ================= EVENTOS DE INVASÃO DE CIDADE =================
CITY_INVASION_EVENTS = {
    1: [
        {
            "id": "inv_campos_001",
            "title": "🐗 Horda de Javalis Raivosos",
            "description": "Uma horda de javalis gigantes avança pela estrada principal! O mercado está sendo destruído!",
            "enemy": "Javali Enraivecido",
            "enemy_count": 8,
            "hp": 180,
            "atk": 18,
            "xp_reward": 800,
            "coins_reward": 40,
            "min_defenders": 1,
            "dialogue_options": [
                {"text": "🌾 Espalhar feno para distrair os javalis para longe", "success_chance": 0.65, "align": +5},
                {"text": "⚔️ Atacar a liderança da horda diretamente", "success_chance": 0.55, "align": +3},
                {"text": "📯 Tocar o alarme e evacuar os moradores", "success_chance": 0.80, "align": +8},
            ]
        },
        {
            "id": "inv_campos_002",
            "title": "🐀 Praga de Ratos Mágicos",
            "description": "Ratos do tamanho de gatos estão invadindo os celeiros! As reservas de comida do inverno estão em risco!",
            "enemy": "Rato Mágico Gigante",
            "enemy_count": 15,
            "hp": 80,
            "atk": 10,
            "xp_reward": 600,
            "coins_reward": 30,
            "min_defenders": 1,
            "dialogue_options": [
                {"text": "🧀 Preparar iscas envenenadas nos celeiros", "success_chance": 0.75, "align": +3},
                {"text": "🔥 Acender tochas para afugentar a praga", "success_chance": 0.60, "align": +5},
                {"text": "🐱 Recrutar gatos mágicos da floresta", "success_chance": 0.85, "align": +7},
            ]
        },
    ],
    10: [
        {
            "id": "inv_floresta_001",
            "title": "👺 Ataque Goblin Organizado",
            "description": "Uma tribo de goblins com táticas militares invade a aldeia florestal! Eles têm catapultas improvisadas!",
            "enemy": "Guerreiro Goblin",
            "enemy_count": 12,
            "hp": 350,
            "atk": 28,
            "xp_reward": 1800,
            "coins_reward": 80,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🤝 Tentar negociar — por que os goblins atacam?", "success_chance": 0.45, "align": +12},
                {"text": "🏹 Emboscada nas árvores antes que avancem", "success_chance": 0.65, "align": +4},
                {"text": "🔥 Destruir as catapultas primeiro", "success_chance": 0.70, "align": +2},
                {"text": "💀 Ataque total sem misericórdia", "success_chance": 0.80, "align": -5},
            ]
        },
        {
            "id": "inv_floresta_002",
            "title": "🕷️ Ninho de Aranhas Colossais",
            "description": "Um ninho de aranhas colossais foi perturbado e as criaturas invadem o acampamento!",
            "enemy": "Aranha Colossal",
            "enemy_count": 6,
            "hp": 500,
            "atk": 35,
            "xp_reward": 2000,
            "coins_reward": 90,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🔥 Fogo destrói a teia e afasta as aranhas", "success_chance": 0.75, "align": +3},
                {"text": "🧪 Usar antídoto para atrair as aranhas para longe", "success_chance": 0.60, "align": +6},
                {"text": "⚔️ Combate direto com as criaturas", "success_chance": 0.55, "align": +2},
            ]
        },
    ],
    20: [
        {
            "id": "inv_deserto_001",
            "title": "💀 Exército de Mumificados",
            "description": "O selo de Kha-Mentu foi quebrado! Um exército de guerreiros mumificados marcha pelo deserto em direção ao Oásis!",
            "enemy": "Guerreiro Mumificado",
            "enemy_count": 20,
            "hp": 600,
            "atk": 42,
            "xp_reward": 3500,
            "coins_reward": 120,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "📜 Recitar a prece de descanso dos mortos", "success_chance": 0.55, "align": +10},
                {"text": "🏺 Quebrar o artefato que os controla", "success_chance": 0.65, "align": +5},
                {"text": "⚔️ Confronto direto — são mortos, sem negociação", "success_chance": 0.70, "align": 0},
                {"text": "🚪 Evacuar o oásis e deixá-los ir", "success_chance": 0.90, "align": +3},
            ]
        },
    ],
    30: [
        {
            "id": "inv_gelo_001",
            "title": "🦣 Ataque dos Yetis Furiosos",
            "description": "Uma tempestade de neve trouxe Yetis famintos até a Fortaleza Permafrost! Eles arranham as portas!",
            "enemy": "Yeti Furioso",
            "enemy_count": 5,
            "hp": 900,
            "atk": 60,
            "xp_reward": 4500,
            "coins_reward": 150,
            "min_defenders": 2,
            "dialogue_options": [
                {"text": "🥩 Jogar comida para além dos muros para atraí-los", "success_chance": 0.70, "align": +8},
                {"text": "🔥 Acender fogueiras nas paredes para afastá-los", "success_chance": 0.65, "align": +3},
                {"text": "⚔️ Sair e enfrentar os Yetis um a um", "success_chance": 0.50, "align": +5},
                {"text": "❄️ Usar magia para criar uma barreira de gelo maior", "success_chance": 0.75, "align": +4},
            ]
        },
    ],
    40: [
        {
            "id": "inv_vulcao_001",
            "title": "🐲 Dragões de Lava Jovens",
            "description": "A erupção acordou ninhadas de dragões de lava! Três criaturas atacam a Cidadela Cinzenta!",
            "enemy": "Dragão de Lava Jovem",
            "enemy_count": 3,
            "hp": 1500,
            "atk": 90,
            "xp_reward": 7000,
            "coins_reward": 200,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "🧊 Usar magia de gelo para acalmar as criaturas", "success_chance": 0.50, "align": +12},
                {"text": "🥚 Encontrar e proteger os ovos para negociar", "success_chance": 0.60, "align": +10},
                {"text": "⚔️ Batalha total — dragões ou cidadela", "success_chance": 0.65, "align": -2},
                {"text": "💎 Oferecer gemas como pagamento para recuo", "success_chance": 0.45, "align": +5},
            ]
        },
    ],
    50: [
        {
            "id": "inv_abismo_001",
            "title": "👁️ Invasão de Entidades do Vazio",
            "description": "Uma fenda no Abismo Arcano se abre! Entidades insanas emergem com fome de realidade!",
            "enemy": "Entidade do Vazio",
            "enemy_count": 4,
            "hp": 2000,
            "atk": 120,
            "xp_reward": 10000,
            "coins_reward": 300,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "🔮 Ritual de fechamento da fenda (arriscado)", "success_chance": 0.45, "align": +15},
                {"text": "📚 Usar conhecimento arcano para comunicar com elas", "success_chance": 0.35, "align": +10},
                {"text": "⚔️ Combate dimensional com tudo que tem", "success_chance": 0.60, "align": 0},
                {"text": "💥 Explodir a fenda com magia destrutiva", "success_chance": 0.70, "align": -5},
            ]
        },
    ],
    60: [
        {
            "id": "inv_celestial_001",
            "title": "😈 Queda de Anjos Corrompidos",
            "description": "Anjos caídos atacam o Trono Celestial! Seres de luz corrompida descem em chamas!",
            "enemy": "Anjo Caído",
            "enemy_count": 5,
            "hp": 3000,
            "atk": 160,
            "xp_reward": 20000,
            "coins_reward": 500,
            "min_defenders": 3,
            "dialogue_options": [
                {"text": "✨ Tentar purificar a corrupção com luz celestial", "success_chance": 0.40, "align": +20},
                {"text": "🕊️ Preces de redenção para os seres caídos", "success_chance": 0.35, "align": +15},
                {"text": "⚔️ Batalha épica — eles escolheram a queda", "success_chance": 0.65, "align": +3},
                {"text": "🌌 Usar o poder do Trono para bani-los de volta", "success_chance": 0.55, "align": +8},
            ]
        },
    ]
}

# ================= BOSSES VARIADOS POR REINO =================
WORLD_BOSSES_VARIANTS = {
    1: [
        {"name": "👑 Slime Rei Corrompido", "hp": 200, "atk": 18, "xp": 350, "coins": (20, 45),
         "desc": "O Slime Rei foi infectado por magia negra. Seu corpo negro borbulha com veneno arcano.",
         "intro": "Uma massa negra e pulsante bloqueia seu caminho. Olhos vermelhos piscam do interior do lodo."},
        {"name": "🐀 Rato dos Esgotos Ancestral", "hp": 170, "atk": 22, "xp": 300, "coins": (15, 35),
         "desc": "Um rato que viveu nos esgotos por 500 anos. Carrega doenças de cinco civilizações.",
         "intro": "Um rato do tamanho de um cavalo emerge das profundezas. Sua pele está coberta de runas."},
        {"name": "🌪️ Espírito do Campo", "hp": 250, "atk": 15, "xp": 400, "coins": (25, 50),
         "desc": "O espírito protetor dos campos foi corrompido. Antes guardava a terra. Agora a devora.",
         "intro": "O vento para subitamente. Uma forma etérea verde e dourada materializa com olhos vazios."},
        {"name": "🌱 Ent Jovem Enraivecido", "hp": 300, "atk": 12, "xp": 380, "coins": (18, 40),
         "desc": "Um ent jovem cujas raízes foram contaminadas por poluição arcana. Ele sofre e ataca.",
         "intro": "Um conjunto de árvores se levanta e toma forma humanoide colossal. Ele geme ao se mover."},
    ],
    10: [
        {"name": "🌲 Ent Ancião das Profundezas", "hp": 450, "atk": 30, "xp": 600, "coins": (30, 70),
         "desc": "O mais antigo dos ents. Viu o mundo nascer e quer ver morrer.",
         "intro": "A floresta inteira treme. Um ent de 400 anos se ergue, sua face entalhada em sofrimento."},
        {"name": "🕷️ Mãe das Aranhas", "hp": 380, "atk": 35, "xp": 550, "coins": (25, 60),
         "desc": "A aranha original. Todas as aranhas desta floresta desceram dela.",
         "intro": "Oito olhos vermelhos brilham na escuridão. Uma aranha colossal desce do teto da caverna."},
        {"name": "👺 Rei Goblin Estrategista", "hp": 400, "atk": 28, "xp": 580, "coins": (28, 65),
         "desc": "Não é apenas bruto — ele é inteligente. E isso o torna o goblin mais perigoso já visto.",
         "intro": "Um goblin de armadura élfica roubada senta num trono de ossos. Ele te olha com interesse."},
        {"name": "🌫️ Espectro do Herói Caído", "hp": 350, "atk": 40, "xp": 620, "coins": (20, 55),
         "desc": "Um herói que morreu sem completar sua missão. Preso entre vivos e mortos pela raiva.",
         "intro": "Uma figura translúcida em armadura enferrujada empunha uma espada de luz mortiça."},
    ],
    20: [
        {"name": "🔺 Faraó Kha-Mentu Ressurgido", "hp": 600, "atk": 45, "xp": 900, "coins": (40, 90),
         "desc": "O faraó da primeira civilização. Morreu traído por seus sacerdotes. Voltou com sede de vingança.",
         "intro": "A pirâmide treme. Bandagens douradas flutuam pelo ar. O faraó abre os olhos dourados."},
        {"name": "🦂 Grande Escorpião do Deserto", "hp": 550, "atk": 50, "xp": 850, "coins": (35, 80),
         "desc": "Escorpião com veneno capaz de matar um elefante. Protege ruínas por séculos.",
         "intro": "As dunas explodem. Um escorpião colossal surge do subsolo, pinças do tamanho de árvores."},
        {"name": "🌪️ Djinn do Vento de Areia", "hp": 500, "atk": 55, "xp": 880, "coins": (30, 75),
         "desc": "Gênio aprisionado há milênios. A raiva do cativeiro o transformou em algo incontrolável.",
         "intro": "Uma tempestade de areia para e toma forma humana. Olhos como tempestades te encarram."},
        {"name": "🏺 Golem da Argila Sagrada", "hp": 700, "atk": 38, "xp": 920, "coins": (45, 95),
         "desc": "Criado para proteger o templo. Agora que o templo caiu, ele não sabe o que proteger.",
         "intro": "Uma estátua de argila de 5 metros pisca. Runas sagradas brilham em seu peito. Ele avança."},
    ],
    30: [
        {"name": "❄️ Titã do Gelo Eterno", "hp": 800, "atk": 60, "xp": 1200, "coins": (50, 110),
         "desc": "Um titã de gelo que dormia no coração da montanha. Despertou com a invasão de aventureiros.",
         "intro": "Uma avalanche para no ar. Blocos de gelo se reorganizam numa forma colossal de 10 metros."},
        {"name": "🐉 Dragão de Cristal", "hp": 750, "atk": 70, "xp": 1300, "coins": (55, 120),
         "desc": "Um dragão cujas escamas viraram cristal por uma maldição. Belo e letal.",
         "intro": "Luz se refrata por toda a caverna. Um dragão translúcido de cristal azul te olha com curiosidade."},
        {"name": "🦣 Rei dos Yetis", "hp": 900, "atk": 55, "xp": 1100, "coins": (45, 100),
         "desc": "O patriarca de toda a tribo Yeti. Tão antigo que sua pelagem virou neve permanente.",
         "intro": "A temperatura cai 20 graus de repente. O maior ser que você já viu emerge da nevasca."},
        {"name": "🌊 Elemental de Gelo Primordial", "hp": 680, "atk": 75, "xp": 1350, "coins": (60, 130),
         "desc": "Um elemental que existia antes de qualquer montanha ser formada. Ele é a própria neve.",
         "intro": "Flocos de neve flutuam em padrão impossível. Eles se fundem numa entidade translúcida e feroz."},
    ],
    40: [
        {"name": "🌋 Ignarius, Dragão de Magma Ancião", "hp": 1100, "atk": 85, "xp": 1800, "coins": (70, 150),
         "desc": "O primeiro ser criado quando o mundo era fogo. Guarda a Chama Original com ciúme eterno.",
         "intro": "O vulcão erupciona de dentro pra fora. Magma toma forma. Ignarius abre os olhos de brasa."},
        {"name": "⚒️ Golem da Forja Corrompida", "hp": 950, "atk": 95, "xp": 1700, "coins": (65, 140),
         "desc": "A Forja Sagrada criou este golem para se defender. Mas a forja ficou louca.",
         "intro": "Ferramentas flutuam em espiral. O metal derretido toma forma de um guerreiro monstruoso."},
        {"name": "💀 Espírito do Forjador Traído", "hp": 880, "atk": 100, "xp": 1900, "coins": (75, 160),
         "desc": "Um forjador anão que foi assassinado pela coroa. Sua raiva o manteve vivo em forma etérea.",
         "intro": "O ar cheira a metal e ranço. Uma figura translúcida com martelo de fogo surge do nada."},
        {"name": "🔥 Salamandra Primordial", "hp": 1000, "atk": 90, "xp": 1750, "coins": (68, 145),
         "desc": "A salamandra que nasceu do primeiro fogo do universo. Criatura mais antiga do Reino.",
         "intro": "O chão de lava explode. Uma salamandra do tamanho de uma casa emerge, cantando em chamas."},
    ],
    50: [
        {"name": "🌀 O Senhor das Sombras", "hp": 1500, "atk": 120, "xp": 2800, "coins": (90, 200),
         "desc": "Entidade que existia antes do universo. Quer apagar a realidade e retornar ao silêncio primordial.",
         "intro": "A luz some. Não há escuridão — há ausência de tudo. Então ele fala: 'Você também cansou de existir?'"},
        {"name": "👁️ Olho do Abismo", "hp": 1200, "atk": 140, "xp": 3000, "coins": (100, 220),
         "desc": "Um olho do tamanho de uma casa que observa desde o início dos tempos. Enlouquece quem o encontra.",
         "intro": "Uma pupila vertical de 3 metros se abre no teto do Abismo. Você sente ser estudado até o DNA."},
        {"name": "🌌 Arquimago Zephyr Corrompido", "hp": 1350, "atk": 110, "xp": 2600, "coins": (85, 190),
         "desc": "O maior mago do mundo se corrompeu estudando o Abismo. Agora é parte dele.",
         "intro": "Uma silhueta familiar usa magias impossíveis. Você reconhece o rosto: Zephyr, com olhos vazios."},
        {"name": "♾️ Loop Temporal", "hp": 1100, "atk": 130, "xp": 2900, "coins": (95, 210),
         "desc": "Uma entidade que é o próprio tempo se loopando. Cada vez que você ataca, ela volta um segundo.",
         "intro": "Você sente déjà vu. E de novo. E de novo. Uma entidade surge com múltiplas versões de si mesma."},
    ],
    60: [
        {"name": "👑 Imperador Astral", "hp": 2500, "atk": 180, "xp": 5000, "coins": (150, 350),
         "desc": "O governante do Trono Celestial. Não é mau — é o teste final. Aqueles dignos passarão.",
         "intro": "O Trono brilha com luz insuportável. Uma figura de luz pura desce. 'Você chegou. Curioso.'"},
        {"name": "😈 Querubim Corrompido Makhael", "hp": 2000, "atk": 200, "xp": 5500, "coins": (160, 370),
         "desc": "O anjo mais belo que existiu, corrompido pela inveja. Sua queda criou um buraco no céu.",
         "intro": "Asas negras preenchem o horizonte. Um ser de beleza aterrorizante pousa, com espada de trevas."},
        {"name": "🌌 Vácuo da Criação", "hp": 3000, "atk": 150, "xp": 4500, "coins": (140, 320),
         "desc": "O espaço vazio onde a criação começa e termina. É o nada que deseja ser algo.",
         "intro": "O Trono implode em silêncio. No centro do vácuo, algo toma forma — ou talvez seja o vazio mesmo."},
        {"name": "⭐ O Primeiro Herói (Corrompido)", "hp": 2200, "atk": 190, "xp": 5200, "coins": (155, 360),
         "desc": "O primeiro aventureiro que passou por todos os reinos. Corrompido pelo poder do Trono.",
         "intro": "Você reconhece os equipamentos: os mesmos de todas as lendas antigas. Mas os olhos são do Vazio."},
    ]
}

# ================= SISTEMA DE ALINHAMENTO MORAL =================
ALIGNMENT_TITLES = {
    "Heroi":      {"emoji": "✨", "color": 0xFFD700, "desc": "Protetor dos inocentes, luz nas trevas."},
    "Anti-Heroi": {"emoji": "⚖️", "color": 0x888888, "desc": "Nem bom, nem mau. Apenas pragmático."},
    "Vilao":      {"emoji": "💀", "color": 0xFF0000, "desc": "O medo é sua arma. O poder é seu deus."},
    "Neutro":     {"emoji": "🌑", "color": 0x444444, "desc": "Ainda sem definição. O destino aguarda."},
}

# Pontos: +10 = herói, -10 = vilão, zona neutra = anti-herói
ALIGNMENT_SCENARIOS = {
    1: [  # Campos
        {
            "id": "esc_campos_001",
            "emoji": "🏘️",
            "title": "O Aldeão Desesperado",
            "description": "Um aldeão idoso se ajoelha diante de você, com lágrimas nos olhos. Seus filhos foram capturados pelo Slime Rei. Ele oferece suas últimas 3 moedas em pagamento.",
            "choices": [
                {"text": "✨ Aceitar a missão gratuitamente e ir resgatar os filhos",      "align": +10, "xp": 300, "coins": 0,   "result": "Você salva os filhos sem pedir nada em troca. A aldeia inteira celebra seu nome."},
                {"text": "⚖️ Aceitar as 3 moedas e completar a missão",                    "align": 0,   "xp": 200, "coins": 3,   "result": "Uma transação justa. Os filhos são salvos. O aldeão agradece com o que pôde."},
                {"text": "💀 Exigir todo o tesouro da aldeia para ajudar",                  "align": -10, "xp": 150, "coins": 15,  "result": "Você extorque o aldeão. Os filhos são salvos, mas você é amaldiçoado pelo sofrimento causado."},
                {"text": "🏃 Ignorar o pedido e seguir em frente",                         "align": -5,  "xp": 0,   "coins": 0,   "result": "Você passa direto. Os gritos do aldeão ecoam em sua mente por dias."},
            ]
        },
        {
            "id": "esc_campos_002",
            "emoji": "🐺",
            "title": "A Matilha Faminta",
            "description": "Uma matilha de lobos faminta bloqueia a estrada. Eles não são monstros — apenas animais com fome depois de uma seca prolongada. Aldeões assustados assistem de longe.",
            "choices": [
                {"text": "✨ Caçar comida e alimentar os lobos para liberarem a estrada",   "align": +8,  "xp": 250, "coins": 0,   "result": "Os lobos comem e se dispersam. Os aldeões nunca esquecerão o gesto."},
                {"text": "⚖️ Assustar a matilha para longe sem ferir nenhum",               "align": +3,  "xp": 180, "coins": 0,   "result": "Com ruído e fogo, você afasta os lobos. Eficiente e sem sangue."},
                {"text": "💀 Matar todos os lobos para garantir a estrada livre",            "align": -5,  "xp": 200, "coins": 5,   "result": "A estrada fica livre... e coberta de sangue. Os aldeões ficam em silêncio."},
                {"text": "⚖️ Cobrar dos aldeões para abrir a passagem",                     "align": -2,  "xp": 100, "coins": 8,   "result": "Negócio é negócio. Você dispersa os lobos, os aldeões pagam contrariados."},
            ]
        },
        {
            "id": "esc_campos_003",
            "emoji": "💰",
            "title": "O Tesouro do Ladrão",
            "description": "Você encontra um ladrão inconsciente após uma queda. Ao seu lado, uma bolsa com moedas roubadas de aldeões. Uma nota diz para quem pertence cada moeda.",
            "choices": [
                {"text": "✨ Devolver cada moeda ao dono certo usando a lista",              "align": +12, "xp": 200, "coins": 0,   "result": "Cada aldeão recebe de volta o que era seu. Sua honra cresce."},
                {"text": "⚖️ Guardar metade e devolver metade anonimamente",                "align": -2,  "xp": 100, "coins": 12,  "result": "Alguns aldeões recebem de volta algo. Você fica com o resto."},
                {"text": "💀 Ficar com tudo — o ladrão não merecia mesmo",                   "align": -8,  "xp": 50,  "coins": 25,  "result": "Você rouba do ladrão. O dinheiro é seu agora, mas o karma não esquece."},
                {"text": "🏥 Chamar um curandeiro para o ladrão e reportar à guarda",       "align": +10, "xp": 180, "coins": 0,   "result": "Justiça é feita. O ladrão recebe ajuda e responderá pelo que fez."},
            ]
        },
        {
            "id": "esc_campos_004",
            "emoji": "🔥",
            "title": "Celeiro em Chamas",
            "description": "Um celeiro pega fogo! Uma criança está presa dentro. O dono tenta entrar mas é segurado por outros. Você pode agir.",
            "choices": [
                {"text": "✨ Entrar correndo e salvar a criança (perde 30 HP)",              "align": +15, "xp": 400, "coins": 0,   "result": "Você entra pelas chamas. A criança está viva. Você sai queimado, mas vivo. Herói."},
                {"text": "⚖️ Organizar um balde de água com os aldeões antes",              "align": +5,  "xp": 200, "coins": 0,   "result": "Trabalho em equipe. A criança é salva com risco menor para todos."},
                {"text": "💀 Observar sem agir — não é problema seu",                       "align": -12, "xp": 0,   "coins": 0,   "result": "Você assiste. A criança sobrevive por sorte. Os aldeões nunca te perdoarão."},
                {"text": "⚖️ Entrar SE receberem uma boa recompensa primeiro",              "align": -6,  "xp": 200, "coins": 20,  "result": "Você negocia enquanto a criança grita. Ela sobrevive. A aldeia fica dividida sobre você."},
            ]
        },
    ],
    10: [  # Floresta
        {
            "id": "esc_floresta_001",
            "emoji": "🌲",
            "title": "O Acampamento Goblin",
            "description": "Você descobre um acampamento goblin. Mas ao se aproximar, vê que são goblins jovens — praticamente crianças — aprendendo a sobreviver sem adultos. Eles ficam com medo de você.",
            "choices": [
                {"text": "✨ Ensinar as crianças a pescar e coletar alimentos",               "align": +12, "xp": 350, "coins": 0,   "result": "Os jovens goblins aprendem. Décadas depois, eles serão pacifistas que lembram do herói."},
                {"text": "⚖️ Ignorar e passar sem interagir",                               "align": 0,   "xp": 0,   "coins": 0,   "result": "Você não ajuda, mas também não prejudica. Eles continuam sua vida."},
                {"text": "💀 Atacar o acampamento para 'eliminar uma ameaça futura'",        "align": -15, "xp": 300, "coins": 8,   "result": "Você ataca crianças indefesas. XP fácil, mas uma mancha irreparável na alma."},
                {"text": "⚖️ Roubar os alimentos deles discretamente",                      "align": -8,  "xp": 50,  "coins": 10,  "result": "Você rouba de crianças. Elas ficam com fome. O karma lembra."},
            ]
        },
        {
            "id": "esc_floresta_002",
            "emoji": "👁️",
            "title": "A Espiã da Floresta",
            "description": "Uma elfa te intercepta. Ela é uma espiã da resistência contra um tirano que governa um vilarejo próximo. Ela pede sua ajuda para entregar uma mensagem secreta.",
            "choices": [
                {"text": "✨ Ajudar a entrega da mensagem pro bem da resistência",           "align": +10, "xp": 400, "coins": 0,   "result": "A mensagem chega. A resistência se fortalece. Você fez parte da história."},
                {"text": "💀 Trair a espiã ao tirano em troca de ouro",                     "align": -15, "xp": 100, "coins": 30,  "result": "A espiã é capturada. O tirano te paga. A resistência cai por ora."},
                {"text": "⚖️ Pedir pagamento para a entrega",                               "align": -3,  "xp": 250, "coins": 15,  "result": "Serviço prestado por moedas. A elfa suspira, mas aceita."},
                {"text": "⚖️ Recusar — muito perigoso envolver-se em política",             "align": 0,   "xp": 0,   "coins": 0,   "result": "Você recusa e segue. A resistência encontra outro mensageiro."},
            ]
        },
    ],
    20: [  # Deserto
        {
            "id": "esc_deserto_001",
            "emoji": "🏺",
            "title": "A Tumba Profanada",
            "description": "Um grupo de saqueadores está violando uma tumba sagrada, levando artefatos dos ancestrais. Um ancião nomade te pede para intervir.",
            "choices": [
                {"text": "✨ Expulsar os saqueadores e devolver os artefatos ao ancião",    "align": +12, "xp": 500, "coins": 0,   "result": "Os artefatos voltam ao seu lugar. O ancião te abençoa com conhecimento antigo."},
                {"text": "⚖️ Expulsar os saqueadores e ficar com metade",                   "align": -3,  "xp": 300, "coins": 25,  "result": "Meio certo, meio errado. O ancião fica com o suficiente para o ritual."},
                {"text": "💀 Juntar-se aos saqueadores — mais dividido entre mais gente",   "align": -10, "xp": 200, "coins": 40,  "result": "Você saqueia junto. Riqueza fácil. A maldição do faraó observa em silêncio."},
                {"text": "⚖️ Negociar com os saqueadores para eles pararem",               "align": +5,  "xp": 200, "coins": 0,   "result": "Palavras no lugar de violência. Eles recuam. Alguns artefatos foram perdidos."},
            ]
        },
    ],
    30: [  # Montanhas
        {
            "id": "esc_gelo_001",
            "emoji": "🏔️",
            "title": "A Aldeia Sitiada",
            "description": "Uma aldeia nas montanhas está sitiada por bandidos que exigem tributo mensal. Os moradores estão famintos e com frio. Os bandidos são 5, todos armados.",
            "choices": [
                {"text": "✨ Enfrentar os 5 bandidos sozinho para libertar a aldeia",       "align": +15, "xp": 600, "coins": 0,   "result": "Batalha épica. Você vence. A aldeia é livre. Eles te constroem uma estátua."},
                {"text": "⚖️ Treinar os aldeões para se defenderem sozinhos",               "align": +10, "xp": 500, "coins": 0,   "result": "Você ensina a pescar. A aldeia aprende a se proteger para sempre."},
                {"text": "💀 Fazer um acordo com os bandidos — eles te pagam para manter controle", "align": -12, "xp": 150, "coins": 35, "result": "Você lucra com o sofrimento. Os aldeões continuam pagando. Agora para você também."},
                {"text": "⚖️ Negociar a saída dos bandidos com seu espólio de batalha",    "align": +3,  "xp": 300, "coins": 10,  "result": "Dinheiro muda mentes. Os bandidos partem. A aldeia respira aliviada."},
            ]
        },
    ],
    40: [  # Vulcão
        {
            "id": "esc_vulcao_001",
            "emoji": "🌋",
            "title": "A Última Criança Anã",
            "description": "Você encontra a única criança sobrevivente de uma civilização anã destruída pelo vulcão. Ela segura um mapa para um tesouro lendário de sua nação.",
            "choices": [
                {"text": "✨ Adotar a criança e protegê-la, esquecendo o tesouro",          "align": +15, "xp": 700, "coins": 0,   "result": "Você escolhe uma vida acima do ouro. A criança cresce para se tornar uma lenda."},
                {"text": "⚖️ Ajudar a criança a recuperar o tesouro de sua nação",          "align": +10, "xp": 600, "coins": 50,  "result": "Justo. O tesouro pertence a ela. Você recebe uma parte como herança da civilização."},
                {"text": "💀 Roubar o mapa e deixar a criança para trás",                   "align": -15, "xp": 200, "coins": 80,  "result": "Você rouba de uma órfã. O tesouro é seu. Mas o peso disso nunca sai."},
                {"text": "⚖️ Levar ao acampamento mais próximo e seguir adiante",           "align": +3,  "xp": 200, "coins": 0,   "result": "Você a coloca em segurança. Não ficou com o tesouro, mas também não abandonou."},
            ]
        },
    ],
    50: [  # Abismo
        {
            "id": "esc_abismo_001",
            "emoji": "👁️",
            "title": "O Pacto das Sombras",
            "description": "Uma entidade do Abismo te oferece poder imenso. Tudo que precisa é assinar um pacto — sacrificando a felicidade de três pessoas que não te conhecem.",
            "choices": [
                {"text": "✨ Recusar o pacto com firmeza e atacar a entidade",               "align": +15, "xp": 800, "coins": 0,   "result": "A entidade recua. Você resiste à tentação. Raro. Muito raro."},
                {"text": "💀 Assinar o pacto — poder acima de tudo",                        "align": -20, "xp": 1000, "coins": 100, "result": "O poder chega. Em algum lugar, três estranhos acordam com pesadelos eternos."},
                {"text": "⚖️ Fingir aceitar e depois quebrar o pacto",                     "align": -5,  "xp": 500, "coins": 50,  "result": "Você engana a entidade. Ela não esquece facilmente."},
                {"text": "⚖️ Negociar termos — sacrifício menor, poder menor",             "align": -8,  "xp": 600, "coins": 60,  "result": "Um acordo menor. Poder moderado. Culpa moderada. Tudo moderado."},
            ]
        },
    ],
    60: [  # Trono
        {
            "id": "esc_celestial_001",
            "emoji": "👑",
            "title": "O Julgamento Final",
            "description": "O Imperador Astral oferece a você o poder de reescrever a história de UMA pessoa — alguém que sofreu imerecidamente. Mas para isso, outra pessoa terá que sofrer no lugar.",
            "choices": [
                {"text": "✨ Recusar — o sofrimento não deve ser transferido, deve ser curado", "align": +20, "xp": 2000, "coins": 0,  "result": "O Imperador sorri. 'Finalmente alguém entendeu.' Você recebe a bênção do Trono."},
                {"text": "💀 Escolher quem sofre — transferir para um vilão conhecido",      "align": -5,  "xp": 1200, "coins": 200, "result": "Julgamento humano de sofrimento. A lógica parece boa... mas quem decide quem merece?"},
                {"text": "⚖️ Perguntar se há uma terceira opção antes de decidir",          "align": +8,  "xp": 1500, "coins": 0,   "result": "Existe sempre. O Imperador abre um caminho alternativo de cura sem custo."},
                {"text": "💀 Usar o poder em si mesmo — apagar seu próprio sofrimento",     "align": -10, "xp": 1000, "coins": 100, "result": "Egoísta. Funciona. Mas você perdeu a chance de ser verdadeiramente grande."},
            ]
        },
    ],
}

# ================= QUESTS ALINHAMENTO MORAL =================
ALIGNMENT_QUESTS = {
    "heroi": [
        {
            "id": "heroi_001",
            "name": "🛡️ Protetor das Crianças Perdidas",
            "description": "Crianças órfãs estão sendo escravizadas por um mercador corrupto. Resgate 8 crianças das grades.",
            "type": "individual", "objective": "hunt", "target": "Mercador Corrupto",
            "count": 1, "reward_xp": 2000, "reward_coins": 50, "reward_item": "Poção de Vida Superior",
            "align_required": "Heroi", "align_gain": +10,
            "lore": "O mercador tem conexões perigosas. Seja cuidadoso.",
            "npc": "Madre Celeste", "difficulty": "Difícil"
        },
        {
            "id": "heroi_002",
            "name": "✨ A Cura da Aldeia Amaldiçoada",
            "description": "Uma maldição arcana infecta uma aldeia inteira. Colete 12 ingredientes para o ritual de cura.",
            "type": "individual", "objective": "collect", "count": 12,
            "reward_xp": 1800, "reward_coins": 30, "reward_item": "Elixir da Vida",
            "align_required": "Heroi", "align_gain": +8,
            "lore": "A maldição foi lançada por um mago que perdeu a família nesta aldeia. Tragédia se alimenta de tragédia.",
            "npc": "Padre Elian", "difficulty": "Médio"
        },
    ],
    "anti_heroi": [
        {
            "id": "anti_001",
            "name": "⚖️ O Trabalho Sujo",
            "description": "O prefeito precisa de alguém para 'resolver' um problema sem fazer perguntas. Explore a área e descubra.",
            "type": "individual", "objective": "explore", "count": 5,
            "reward_xp": 1500, "reward_coins": 100, "reward_item": None,
            "align_required": None, "align_gain": -2,
            "lore": "O prefeito não diz o que quer. Você não pergunta. Esse é o acordo.",
            "npc": "Prefeito Sombra", "difficulty": "Médio"
        },
        {
            "id": "anti_002",
            "name": "⚖️ Informações Valiosas",
            "description": "Colete 10 artefatos de locais proibidos. Ninguém precisa saber de onde vieram.",
            "type": "individual", "objective": "collect", "count": 10,
            "reward_xp": 2000, "reward_coins": 80, "reward_item": "Poção de Sorte",
            "align_required": None, "align_gain": -3,
            "lore": "Informação é poder. E você está se tornando muito poderoso.",
            "npc": "Informante Xan", "difficulty": "Difícil"
        },
    ],
    "vilao": [
        {
            "id": "vilao_001",
            "name": "💀 A Purga dos Campos",
            "description": "Um lorde sombrio quer os campos 'limpos' de aldeões. Cace 10 monstros que 'protegem' as aldeias.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 10, "reward_xp": 2500, "reward_coins": 200, "reward_item": "Foice Maldita",
            "align_required": "Vilao", "align_gain": -10,
            "lore": "O Lorde Sombrio promete poder em troca de serviço. O preço é a sua humanidade.",
            "npc": "Lorde Maldito Vorn", "difficulty": "Médio"
        },
        {
            "id": "vilao_002",
            "name": "🌑 Sabotar a Resistência",
            "description": "Explore acampamentos da resistência e plante informações falsas. Visite 7 locais.",
            "type": "individual", "objective": "explore", "count": 7,
            "reward_xp": 3000, "reward_coins": 150, "reward_item": "Poção de Sorte",
            "align_required": "Vilao", "align_gain": -8,
            "lore": "A resistência luta pelo povo. Você luta pelo poder. Apenas um pode vencer.",
            "npc": "Chanceler das Sombras", "difficulty": "Difícil"
        },
    ]
}

# ================= BAÚS MIMIC =================
MIMIC_TIERS = [
    {
        "name": "Baú Comum",
        "emoji": "📦",
        "mimic_chance": 0.20,
        "loot_xp": (200, 400),
        "loot_coins": (5, 15),
        "loot_items": ["Comum", "Incomum"],
        "mimic_dmg": (20, 40),
        "mimic_xp_loss": (50, 100),
        "mimic_desc": "💥 O baú se abre e dentes enormes aparecem! O MIMIC te ataca!",
    },
    {
        "name": "Baú Élfico",
        "emoji": "🗝️",
        "mimic_chance": 0.30,
        "loot_xp": (500, 900),
        "loot_coins": (10, 25),
        "loot_items": ["Incomum", "Raro"],
        "mimic_dmg": (35, 65),
        "mimic_xp_loss": (120, 200),
        "mimic_desc": "🦷 O ornamento élfico era falso! Garras surgem das dobradiças! MIMIC ÉLFICO!",
    },
    {
        "name": "Baú Rúnico",
        "emoji": "🔮",
        "mimic_chance": 0.35,
        "loot_xp": (1000, 2000),
        "loot_coins": (15, 40),
        "loot_items": ["Raro", "Épico"],
        "mimic_dmg": (50, 90),
        "mimic_xp_loss": (200, 350),
        "mimic_desc": "🌑 As runas pulsam com vida própria! Um MIMIC RÚNICO emerge com poder arcano!",
    },
    {
        "name": "Baú Lendário",
        "emoji": "⚜️",
        "mimic_chance": 0.40,
        "loot_xp": (2000, 4000),
        "loot_coins": (20, 60),
        "loot_items": ["Épico", "Lendário"],
        "mimic_dmg": (80, 130),
        "mimic_xp_loss": (400, 600),
        "mimic_desc": "👁️ Os olhos do baú se abrem. Um MIMIC LENDÁRIO! A criatura mais antiga desta dungeon!",
    },
]

# ================= SISTEMA DE MAPA =================
MAP_LOCATIONS = {
    # Cada mundo tem uma lista de locais descobríveis
    1: {
        "world_name": "🌱 Campos Iniciais",
        "locations": [
            {"id": "campos_vila", "name": "🏘️ Vila dos Primeiros Passos", "type": "cidade", "discovered": True},
            {"id": "campos_pedreira", "name": "⛏️ Pedreira dos Iniciantes", "type": "recurso", "discovered": False},
            {"id": "campos_gruta", "name": "🕳️ Gruta do Slime Ancião", "type": "dungeon", "discovered": False},
            {"id": "campos_floresta_borda", "name": "🌿 Borda da Floresta Proibida", "type": "portal", "discovered": False},
            {"id": "campos_torre", "name": "🗼 Torre do Observador", "type": "npc_especial", "discovered": False},
        ]
    },
    10: {
        "world_name": "🌲 Floresta Sombria",
        "locations": [
            {"id": "floresta_acampamento", "name": "⛺ Acampamento das Sombras", "type": "cidade", "discovered": True},
            {"id": "floresta_arvore_milenar", "name": "🌳 Árvore Milenar do Ent", "type": "boss_local", "discovered": False},
            {"id": "floresta_rio_negro", "name": "🖤 Rio das Águas Negras", "type": "recurso", "discovered": False},
            {"id": "floresta_ruinas", "name": "🏚️ Ruínas do Reino Élfico", "type": "dungeon", "discovered": False},
            {"id": "floresta_claro", "name": "🌙 Clareira da Lua", "type": "evento_especial", "discovered": False},
        ]
    },
    20: {
        "world_name": "🏜️ Deserto das Almas",
        "locations": [
            {"id": "deserto_oasis", "name": "🌴 Oásis de Amun", "type": "cidade", "discovered": True},
            {"id": "deserto_piramide", "name": "🔺 Grande Pirâmide de Kha-Mentu", "type": "boss_local", "discovered": False},
            {"id": "deserto_mercado", "name": "🏪 Mercado das Almas", "type": "loja", "discovered": False},
            {"id": "deserto_oasis_secreto", "name": "💧 Oásis do Tempo", "type": "dungeon_secreta", "discovered": False},
            {"id": "deserto_ruinas_antigas", "name": "🏛️ Ruínas da Primeira Civilização", "type": "lore", "discovered": False},
        ]
    },
    30: {
        "world_name": "❄️ Montanhas Geladas",
        "locations": [
            {"id": "gelo_fortaleza", "name": "🏰 Fortaleza Permafrost", "type": "cidade", "discovered": True},
            {"id": "gelo_pico", "name": "🏔️ Pico dos Titãs", "type": "boss_local", "discovered": False},
            {"id": "gelo_mina", "name": "⛏️ Mina dos Cristais Eternos", "type": "recurso", "discovered": False},
            {"id": "gelo_palacio", "name": "❄️ Palácio de Cristal Perdido", "type": "dungeon_secreta", "discovered": False},
            {"id": "gelo_portal", "name": "🌌 Portal para o Vulcão", "type": "portal", "discovered": False},
        ]
    },
    40: {
        "world_name": "🌋 Reino Vulcânico",
        "locations": [
            {"id": "vulcao_cidadela", "name": "🔥 Cidadela Cinzenta", "type": "cidade", "discovered": True},
            {"id": "vulcao_cratera", "name": "🌋 Cratera Principal", "type": "boss_local", "discovered": False},
            {"id": "vulcao_forja", "name": "⚒️ A Forja Sagrada dos Anões", "type": "crafting", "discovered": False},
            {"id": "vulcao_camara", "name": "🔥 Câmara da Chama Original", "type": "dungeon_secreta", "discovered": False},
            {"id": "vulcao_rio_lava", "name": "🌊 Rio de Lava Eterna", "type": "recurso", "discovered": False},
        ]
    },
    50: {
        "world_name": "🌌 Abismo Arcano",
        "locations": [
            {"id": "abismo_torre", "name": "🗼 Torre do Conhecimento Perdido", "type": "cidade", "discovered": True},
            {"id": "abismo_vortex", "name": "🌀 Vórtice Central do Abismo", "type": "boss_local", "discovered": False},
            {"id": "abismo_biblioteca", "name": "📚 Biblioteca dos Tomos Proibidos", "type": "lore", "discovered": False},
            {"id": "abismo_loop", "name": "♾️ Loop Temporal", "type": "dungeon_secreta", "discovered": False},
            {"id": "abismo_portal", "name": "✨ Portal para o Trono", "type": "portal", "discovered": False},
        ]
    },
    60: {
        "world_name": "👑 Trono Celestial",
        "locations": [
            {"id": "celestial_antecamara", "name": "🏛️ Antecâmara do Trono", "type": "cidade", "discovered": True},
            {"id": "celestial_trono", "name": "👑 O Trono em Si", "type": "boss_local", "discovered": False},
            {"id": "celestial_alem", "name": "🌌 Além do Trono", "type": "dungeon_secreta", "discovered": False},
            {"id": "celestial_raiz", "name": "✨ Raiz da Criação", "type": "dungeon_secreta", "discovered": False},
            {"id": "celestial_arquivo", "name": "📜 Arquivo do Destino", "type": "lore", "discovered": False},
        ]
    },
}

# ================= NOVOS NPCs COM LORE =================
WORLD_NPCS_EXTRA = {
    1: [
        {
            "name": "Sábio Pell",
            "role": "Historiador dos Campos",
            "emoji": "📜",
            "dialogues": [
                "Estudei os Campos por 40 anos. Cada pedra aqui é uma página de história.",
                "Sabia que o primeiro herói que passou por aqui era uma cozinheira? Ela matou o Slime Rei com uma frigideira.",
                "Os slimes têm memória coletiva. Quando você mata um, os outros sentem. Por isso ficam mais agressivos.",
                "Encontrei inscrições de 3.000 anos atrás naquelas pedras. Dizem que 'o herói verdadeiro virá dos campos'. Poderia ser você.",
                "Minha teoria: este campo foi um campo de batalha divino. Os slimes são cicatrizes da guerra.",
            ]
        },
        {
            "name": "Criança Miko",
            "role": "Garoto Curioso",
            "emoji": "👦",
            "dialogues": [
                "Você é um aventureiro de verdade?! Isso é incrível! Quando crescer, vou ser como você!",
                "Vi um slime comer uma pedra inteira ontem. Por que eles comem pedra?",
                "Minha mãe diz para não falar com estranhos. Mas você não parece estranho... parece ÉPICO!",
                "Encontrei uma moeda dourada no campo. Papai disse que pertencia a um herói antigo. Posso te mostrar?",
                "Às vezes ouço o campo sussurrar à noite. Papai diz que é o vento. Mas eu sei que não é.",
            ]
        },
    ],
    10: [
        {
            "name": "Espírito Ancião Vel",
            "role": "Guardião Espectral",
            "emoji": "👻",
            "dialogues": [
                "Morri aqui há 800 anos. A floresta me manteve aqui para guardar um segredo.",
                "O Ent e eu somos velhos amigos. Ele estava aqui antes de mim. E estará depois.",
                "Há uma chave enterrada sob a árvore maior. Não a procure ainda. Você ainda não está pronto.",
                "Na vida, fui guerreiro. Na morte, aprendi que a paz verdadeira não vem da vitória, mas da compreensão.",
                "Se você ouvir a floresta cantar à meia-noite, não responda. Nunca responda.",
            ]
        },
        {
            "name": "Bruxo das Raízes",
            "role": "Místico da Floresta",
            "emoji": "🧙",
            "dialogues": [
                "Cada árvore desta floresta é uma palavra num livro que nenhum humano escreveu.",
                "Posso ler seu destino nas raízes expostas. Quer ouvir? Cuidado — a verdade pesa.",
                "Os goblins não são maus por natureza. São o reflexo de como os humanos os trataram.",
                "Há 300 anos, esta floresta era um jardim celestial. O que aconteceu? Os deuses discordaram.",
                "Vejo em você algo que não via há gerações. Uma chama que não se apaga com facilidade.",
            ]
        },
    ],
    20: [
        {
            "name": "Fantasma do General",
            "role": "Espírito Guerreiro",
            "emoji": "⚔️",
            "dialogues": [
                "Lutei na última guerra do Deserto. Mil anos atrás. Ainda não sei quem venceu.",
                "A areia guarda os mortos melhor que qualquer túmulo. Cada duna é um cemitério.",
                "O Faraó Kha-Mentu era meu general. Ele não merecia o que fizeram com ele.",
                "Há uma espada enterrada a 30 metros de profundidade aqui perto. Ela espera por alguém digno.",
                "No calor mais forte, quando a miragem aparece, olhe nos olhos dela. Ela mostra o futuro.",
            ]
        },
        {
            "name": "Mercante Ib",
            "role": "Comerciante Nômade",
            "emoji": "🐪",
            "dialogues": [
                "Viajei por todos os sete reinos. Este deserto é o mais honesto — ele mata com calor, sem subterfúgios.",
                "Já vendi uma estrela embalsamada uma vez. O cliente nunca descobriu que era falsa. Ou descobriu e não se importou.",
                "O mercado das almas está três dunas ao norte. Não compre nada lá que você não possa pagar com algo além de ouro.",
                "Ouvi que o Faraó Kha-Mentu tem uma câmara com mapas de reinos que ainda não existem.",
                "O escorpião que te pica hoje pode salvar sua vida amanhã. Aprendi isso do jeito difícil.",
            ]
        },
    ],
    30: [
        {
            "name": "Vidente das Neves",
            "role": "Oráculo das Montanhas",
            "emoji": "🔮",
            "dialogues": [
                "Vejo três futuros possíveis para você. Todos difíceis. Um deles é glorioso.",
                "O Yeti chorou uma vez. Eu vi. As lágrimas congelaram antes de chegar ao chão.",
                "Os Titãs do Gelo me ensinaram que o frio não mata — a resistência a ele sim.",
                "Há uma criança que vai mudar este mundo. Ela já nasceu. Você pode ter passado por ela.",
                "Quando a montanha cantar, três vezes, em noite sem lua — é hora do próximo ciclo começar.",
            ]
        },
    ],
    40: [
        {
            "name": "Anão Sobrevivente Krug",
            "role": "Último dos Forjadores",
            "emoji": "⚒️",
            "dialogues": [
                "Sou o último da minha linhagem. Os outros se fundiram com Ignarius voluntariamente. Fui covarde. Sobrevivi.",
                "A Forja Sagrada não está apagada — está esperando. Ela reconhece quem é digno.",
                "Aprendi 12 segredos de forja que nenhum humano conhece. Morrerei com eles... a menos que prove ser digno.",
                "O Dragão de Magma guarda as memórias da minha civilização. Quando você o derrotar... escute o rugido. Há palavras lá.",
                "Fiz a espada mais perfeita do mundo uma vez. Então a destruí. Não havia ninguém digno de empunhá-la.",
            ]
        },
    ],
    50: [
        {
            "name": "Ex-Entidade do Vazio",
            "role": "Ser Primordial Aposentado",
            "emoji": "🌌",
            "dialogues": [
                "Existia antes do universo. Decidi me tornar mortal para entender o que é ser frágil. Arrependo? Às vezes.",
                "O Senhor das Sombras é meu irmão mais novo. Ele nunca entendeu que o vazio não é casa — é solidão.",
                "Cada pensamento que você tem ecoa no Abismo por eternidades. Pense com cuidado.",
                "Vi o fim do universo em uma visão. Não era trágico. Era... tranquilo. Como dormir.",
                "Se quiser falar com os mortos, o Abismo tem um bairro deles. Mas eles cobram memórias como entrada.",
            ]
        },
    ],
    60: [
        {
            "name": "Alma de Herói",
            "role": "Espírito de Aventureiro Lendário",
            "emoji": "⭐",
            "dialogues": [
                "Cheguei onde você está. Passei pelo teste. O Imperador me perguntou o que eu mais queria. Disse 'nada'. E recebi tudo.",
                "O Trono não é um lugar. É um estado de ser. Você não SOBE ao Trono. Você SE TORNA o Trono.",
                "Meu maior erro foi achar que chegaria aqui mais forte. Na verdade, cheguei mais humano.",
                "Há segredos além do Trono que nem eu conheço. E estou aqui há 1.000 anos.",
                "O Imperador não quer ser derrotado. Quer ser compreendido. Há diferença.",
            ]
        },
        {
            "name": "Arquiteto do Cosmos",
            "role": "Construtor do Universo",
            "emoji": "🌌",
            "dialogues": [
                "Construí este universo peça por peça. Não é perfeito. Nenhuma criação é.",
                "Coloquei propositalmente as imperfeições. Sem elas, não haveria heróis — não haveria história.",
                "Você chegou ao fim do mapa. Mas o mapa é menor que o território.",
                "Vejo tudo que foi, é e será. E ainda assim, você me surpreende.",
                "Quando terminar aqui, se quiser, posso mostrar o que existe além deste universo. A escolha é sua.",
            ]
        },
    ]
}

# ================= NOVOS EVENTS EXPANDIDOS POR REINO =================
WORLD_EVENTS_EXTRA = {
    1: [
        "Um mercador suspeito oferece uma 'maçã encantada' de graça. Você aceita?",
        "Uma borboleta gigante te guia até um baú escondido no campo.",
        "Você escorrega em um slime invisível e cai no chão. Constrangedor.",
        "Uma velha anuncia que você é 'o escolhido'. Mas ela diz isso para todos.",
        "Um slime se apega à sua bota e não larga. Parece estar te adotando.",
        "Você encontra um mapa antigo rasgado pela metade.",
        "Uma fada minúscula te cutuca insistentemente apontando para uma direção.",
        "O vento traz o cheiro de uma batalha recente. Sangue e magia.",
        "Você tropeça em uma pedra que ressoa como um sino ao ser tocada.",
        "Um corvo negro te segue por uma hora e depois desaparece.",
        "Uma criança te pede para desenhar um mapa. Você descobre um local novo.",
        "O chão balança levemente — algo grande se move sob a terra.",
        "Você encontra as cinzas de uma fogueira recente com símbolos ao redor.",
        "Uma voz na sua cabeça diz 'olhe para cima'. No céu, forma de dragão nas nuvens.",
        "Um aventureiro mais experiente te dá um conselho vago mas profundo.",
        "Você acha um espelho partido. Reflete algo diferente do que está na sua frente.",
        "Uma erva rara brilha ao seu pé. Parece útil para poções.",
        "Uma estátua quebrada aponta na direção de uma dungeon desconhecida.",
        "Uma criança corre até você com uma mensagem: 'Não confie em ninguém de capuz hoje'.",
        "O céu fica vermelho por um instante. O narrador não explica por quê.",
    ],
    10: [
        "A floresta para completamente. Nenhum som. Por 30 segundos. Então retorna.",
        "Você ouve uma melodia linda vindo de lugar nenhum. Faz você sentir saudade de algo que nunca teve.",
        "Musgo cresce visivelmente enquanto você observa. A floresta está respondendo a você.",
        "Uma aranha do tamanho da sua cabeça te olha fixamente. Depois vai embora. Sem atacar.",
        "Você encontra uma árvore com nomes gravados. O último nome é o seu.",
        "Folhas caem em padrão perfeitamente geométrico ao seu redor.",
        "Um ent jovem te estuda de longe com curiosidade antes de recuar.",
        "Você descobre uma cabana abandonada com comida ainda fresca.",
        "Bioluminescência ilumina seu caminho na escuridão da floresta.",
        "Um espírito triste te pede para entregar uma mensagem a alguém já morto.",
        "A floresta parece menor do que deveria. Como se algo a comprimisse.",
        "Você encontra penas negras formando uma seta no chão.",
        "Um riacho subterrâneo burburinha com algo que parece palavras.",
        "Uma formação de cogumelos forma um círculo perfeito. Centro parece mais escuro.",
        "Você acha armadilha de caçador humano. Para que tipo de criatura?",
        "Frutos estranhos caem de uma árvore ao seu passar. Cheiram bem demais.",
        "Uma névoa roxa surge do chão e desaparece em segundos.",
        "Você ouve risadas de crianças mas não há ninguém.",
        "Uma serpente enorme cruza seu caminho sem te atacar. Ela carrega algo na boca.",
        "O sol entra pela copa das árvores formando a silhueta de uma espada no chão.",
    ],
}

# ================= QUESTS EXTRAS COM MUITO XP =================
QUESTS_EXTRA = {
    1: [
        {
            "id": "campos_bonus_001",
            "name": "⭐ O Grande Teste dos Campos",
            "description": "O Sábio Pell te desafia: cace 10 monstros diferentes, colete 10 recursos e explore 5 vezes — tudo para provar que é um aventureiro completo.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 10, "reward_xp": 3000, "reward_coins": 100, "reward_item": "Poção de XP Maior",
            "lore": "Pell registra cada herói que passa pelos campos. Poucos completam o teste. Você vai tentar?",
            "npc": "Sábio Pell", "difficulty": "Épico"
        },
    ],
    10: [
        {
            "id": "floresta_bonus_001",
            "name": "🌲 Pacificador da Floresta",
            "description": "Derrote 15 monstros da floresta para reduzir a agressividade das criaturas e restaurar o equilíbrio.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 15, "reward_xp": 5000, "reward_coins": 80, "reward_item": "Armadura Élfica",
            "lore": "A floresta está em desequilíbrio. Cada monstro que cai restaura um pouco da paz perdida.",
            "npc": "Espírito Ancião Vel", "difficulty": "Muito Difícil"
        },
    ],
    20: [
        {
            "id": "deserto_bonus_001",
            "name": "🏺 Historiador do Deserto",
            "description": "Colete 20 recursos únicos do deserto para o museu ambulante do mercante Ib.",
            "type": "individual", "objective": "collect", "count": 20,
            "reward_xp": 6000, "reward_coins": 60, "reward_item": "Poção de XP Maior",
            "lore": "Ib coleta a história do deserto. Cada artefato é uma memória de civilizações perdidas.",
            "npc": "Mercante Ib", "difficulty": "Épico"
        },
    ],
    30: [
        {
            "id": "gelo_bonus_001",
            "name": "❄️ Conquistador das Alturas",
            "description": "Explore 10 vezes as Montanhas Geladas e descubra todos os segredos que elas escondem.",
            "type": "individual", "objective": "explore", "count": 10,
            "reward_xp": 7000, "reward_coins": 50, "reward_item": "Elixir de XP",
            "lore": "As montanhas revelam seus segredos apenas aos mais persistentes.",
            "npc": "Vidente das Neves", "difficulty": "Muito Difícil"
        },
    ],
    40: [
        {
            "id": "vulcao_bonus_001",
            "name": "🔥 Herdeiro dos Forjadores",
            "description": "Colete 25 recursos do Reino Vulcânico para reconstruir a Forja Sagrada dos anões.",
            "type": "individual", "objective": "collect", "count": 25,
            "reward_xp": 9000, "reward_coins": 40, "reward_item": "Martelo do Trovão",
            "lore": "Krug acredita que você pode restaurar o legado dos forjadores. Prove a ele.",
            "npc": "Anão Sobrevivente Krug", "difficulty": "Lendário"
        },
    ],
    50: [
        {
            "id": "abismo_bonus_001",
            "name": "🌀 Sobrevivente do Vazio",
            "description": "Explore o Abismo Arcano 15 vezes e retorne sempre. A maioria não consegue.",
            "type": "individual", "objective": "explore", "count": 15,
            "reward_xp": 12000, "reward_coins": 30, "reward_item": "Cetro da Eternidade",
            "lore": "A Ex-Entidade do Vazio diz: 'Voltar do Abismo vivo 15 vezes significa que o universo ainda precisa de você.'",
            "npc": "Ex-Entidade do Vazio", "difficulty": "Mítico"
        },
    ],
    60: [
        {
            "id": "celestial_bonus_001",
            "name": "👑 A Saga Completa",
            "description": "Cace 20 guardiões celestiais para provar que chegou ao Trono como lenda viva.",
            "type": "individual", "objective": "hunt", "target": None,
            "count": 20, "reward_xp": 25000, "reward_coins": 20, "reward_item": "Armadura do Primeiro Deus",
            "lore": "A Alma de Herói diz: 'A saga completa de um herói não se mede em batalhas. Se mede em escolhas.'",
            "npc": "Alma de Herói", "difficulty": "Primordial"
        },
    ],
}

# ================= LIVROS DE LORE =================
LORE_BOOKS = {
    1: [
        {
            "title": "📖 Crônicas dos Campos — Vol. I",
            "content": """*Páginas amareladas, mas legíveis...*

**'A Origem dos Sete Reinos'**

No princípio, havia apenas o Vazio — um silêncio perfeito e eterno.
Então, a Primeira Chama surgiu do nada, e com ela nasceu o Mundo.

Os Campos Iniciais foram o primeiro solo a se solidificar das cinzas da criação.
Aqui, os primeiros seres vivos deram seus primeiros passos trêmulos.

Os antigos chamavam este lugar de 'Berço' — pois todo herói, 
independente de sua grandeza futura, começa aqui.

*'O guerreiro mais poderoso que existiu começou matando um slime,'* 
dizia o Sábio Aldren. *'Não se envergonhe do seu começo.'*

— Crônicas dos Campos, escrito pelo Historiador Pell, Ano 1 da Nova Era"""
        },
        {
            "title": "📖 Diário de um Aventureiro",
            "content": """*Rabiscado às pressas em tinta quase seca...*

**Dia 1:**
Cheguei aos Campos. Parece simples demais para ser perigoso.
Estava errado. Um coelho me mordeu.

**Dia 7:**
Encontrei outros aventureiros. Formamos um grupo.
Derrotamos o Slime Rei juntos. Nunca me senti tão vivo.

**Dia 15:**
A Floresta Sombria chama. Dizem que os que entram mudam para sempre.
Vou descobrir por quê.

*— Assinado: 'O Herói Sem Nome', encontrado nos Campos Iniciais*"""
        }
    ],
    10: [
        {
            "title": "📖 Sussurros da Floresta — Tomo Antigo",
            "content": """*Escrito em folhas de árvore, palavras que parecem vivas...*

**'A Floresta que Respira'**

A Floresta Sombria não é apenas uma floresta.
Ela é um ser vivo, consciente, e muito, muito antiga.

O Ent Ancião que habita seu coração tem 3.000 anos de memória.
Ele viu o mundo mudar, viu reinos nascer e morrer.

*Dizem os druidas que quem escuta a floresta com o coração aberto 
pode ouvir ela contar histórias do tempo em que os dragões ainda 
voavam livres sobre todos os reinos.*

Mas cuidado — a floresta também ouve você.
E ela lembra de tudo.

— Coletado pelo Druida Sylvara, Guardiã da Floresta"""
        }
    ],
    20: [
        {
            "title": "📖 Hieróglifos Traduzidos — Fragmento VII",
            "content": """*Tradução de hieróglifos encontrados em uma pirâmide semi-enterrada...*

**'O Testamento do Faraó Kha-Mentu'**

Eu, Kha-Mentu, Faraó da Décima Dinastia, escrevo isto em minha última hora.

Meus sacerdotes me traíram. Eles queriam o Olho de Ra para si mesmos.
Lançaram sobre mim uma maldição: guardar meus próprios tesouros por toda eternidade.

Mas há uma saída. O Olho de Ra ainda pulsa no centro da Grande Pirâmide.
Aquele que o recuperar pode quebrar qualquer maldição.

*Procure o herói que vier depois de mim. Diga-lhe: o segredo está 
onde o sol nunca brilha — mas a verdade sempre ilumina.*

— Kha-Mentu, Faraó Eterno, condenado a aguardar"""
        }
    ],
    30: [
        {
            "title": "📖 Canções do Gelo — Manuscrito",
            "content": """*Escrito em pergaminho congelado, as palavras tremem...*

**'A Balada do Yeti'**

Nem sempre o Yeti foi uma besta selvagem.

Há mil anos, Krom era um guardião gentil das montanhas,
criado pelos Titãs do Gelo para proteger o Cristal do Inverno Eterno.

Então vieram os primeiros humanos, gananciosos e ignorantes.
Eles tentaram roubar o Cristal para vender seu poder.

Krom os deteve — mas algo quebrou dentro dele naquele dia.
O guardião gentil tornou-se a besta que todos temem agora.

*O Cristal do Inverno Eterno ainda está lá, no coração da montanha.
Ainda aguarda um guardião digno.*

— Cantado pelos Bardos das Montanhas, transmitido oralmente por gerações"""
        }
    ],
    40: [
        {
            "title": "📖 Tábuas de Pedra Vulcânica — Transcrição",
            "content": """*Gravado em pedra por mãos que suportaram o calor das chamas...*

**'A Origem do Fogo'**

No segundo dia após a criação do mundo, a Primeira Chama se dividiu.

Uma parte tornou-se o sol.
Outra parte afundou nas profundezas e tornou-se o magma.
A terceira parte... tomou forma. Tornou-se Ignarius.

O Dragão de Magma não é uma criatura — é um elemento.
Tão fundamental quanto água, terra e ar.

*Matar Ignarius não destrói o fogo. Apenas o libera de sua forma.
Mas poucos compreendem isto antes de ser tarde demais.*

— Profeta Ignar, Guardião da Chama Primordial"""
        }
    ],
    50: [
        {
            "title": "📖 Fragmentos do Vazio — Texto Corrompido",
            "content": """*As palavras parecem se mover enquanto você lê...*

**'O Que Existe Antes do Começo'**

[TEXTO PARCIALMENTE ILEGÍVEL]

...antes dos deuses, havia o Vazio...
...o Senhor das Sombras não é o vilão desta história...
...ele apenas quer voltar para casa...
...o 'lar' dele é o nada absoluto...
...e se ele conseguir, tudo que existe...

[TEXTO RASGADO]

...a única forma de detê-lo é mostrar-lhe que a existência...
...vale mais que o silêncio do vazio...

[FIM DO FRAGMENTO]

*Nota da Bibliotecária Spectra: 'Leiam com cuidado. Este texto muda quem o lê.'*"""
        }
    ],
    60: [
        {
            "title": "📖 O Livro do Destino — Página Final",
            "content": """*Este livro parece ter sido escrito para você especificamente...*

**'A Profecia do Herói Final'**

Haverá um dia em que o Trono Celestial receberá um mortal.

Não um deus. Não um anjo. Um ser que começou nos Campos,
que sangrou na Floresta, que queimou no Vulcão,
que sobreviveu ao Abismo — e que chegou aqui.

O Imperador Astral não é um inimigo.
Ele é o último teste antes da ascensão.

*'O verdadeiro poder não é destruir os outros.
É ter o poder de destruir e escolher não fazê-lo.'*

O Trono aguarda.
A história foi escrita.
Apenas você pode decidir como ela termina.

— O Livro do Destino, autor desconhecido, data desconhecida"""
        },
        {
            "title": "📖 Memórias dos Deuses — Tomo Proibido",
            "content": """*As páginas brilham com luz sobrenatural...*

**'O Que os Deuses Temem'**

Os deuses não são imortais. São apenas muito, muito velhos.

O Imperador Astral sabe disso. Por isso ele testa os mortais —
buscando aquele que possa um dia carregá-lo
quando ele mesmo estiver pronto para descansar.

Há segredos que os deuses escondem:
— O Primeiro Deus não criou o universo. Ele *encontrou* ele.
— A morte não é o fim. É uma porta. Mas nem todos sabem abri-la.
— O verdadeiro nome do Vazio é amor. Um amor que consumiu tudo.

*'Se você leu até aqui, você já não é mais o mesmo.'*

— Arquivos da Biblioteca Celestial, acesso nível Divino"""
        },
        {
            "title": "📖 Crônicas da Guerra Primordial",
            "content": """*Escrito em luz solidificada, impossível de destruir...*

**'A Batalha Antes do Tempo'**

Antes que o universo existisse, houve uma guerra.

De um lado: a Luz Primordial, que queria existência, forma, vida.
Do outro: o Vazio Eterno, que queria silêncio, paz, nada.

Eles lutaram por uma eternidade que não tinha nome ainda.

A batalha terminou sem vencedor — ambos exaustos,
fizeram um acordo: criariam algo novo.
Algo que contivesse os dois.

Chamaram isso de *Universo*.

E plantaram dentro de cada ser vivo uma centelha de cada lado.
É por isso que todo ser carrega tanto amor quanto destruição.

*A guerra não terminou. Apenas mudou de palco.*

— Fragmento encontrado no 'Além do Trono'"""
        }
    ]
}

# ================= LIVROS DE LORE EXTRAS (por mundo) =================
LORE_BOOKS_EXTRA = {
    1: [
        {
            "title": "📖 O Bestiário dos Campos — Capítulo I",
            "content": """*Ilustrações detalhadas e notas à margem...*

**'Sobre os Slimes'**

Os slimes são os seres mais mal compreendidos dos Campos.

Eles não são criaturas — são memórias.
Cada slime é formado quando uma emoção humana intensa é derramada no solo:
lágrimas, sangue, esperança, desespero.

O Slime Rei é formado das memórias de centenas de heróis que falharam.
Ele não é mal. Ele é *acumulado*.

*'Olhe nos olhos de um slime. Você pode ver algo familiar?'*

Por isso matar um slime é sempre um pouco triste.
Você está apagando uma memória do mundo.

— Naturalista Pell, Campos Iniciais, Ano 23"""
        },
        {
            "title": "📖 Cartas Para Ninguém — Vol. 1",
            "content": """*Cartas sem destinatário, amarradas com fita vermelha...*

**Carta #1:**
*'Para quem vier depois de mim,'*

Eu estava onde você está agora. Com medo, sem saber nada.
Matei meu primeiro slime e quase chorei. Parece ridículo agora.

Saiba: cada derrota é um professor rigoroso.
Cada cicatriz é um capítulo da sua história.

Quando você chegar ao Trono Celestial
(e você chegará, se persistir),
olhe para trás e lembre do primeiro slime.

*'Quem ri do começo humilde não entende de grandeza.'*

Com amor,
— Um aventureiro que passou por aqui antes"""
        }
    ],
    10: [
        {
            "title": "📖 O Grimório da Floresta — Página Arrancada",
            "content": """*Manchas de seiva verde nas bordas rasgadas...*

**'Os Segredos das Trevas Verdes'**

A Floresta Sombria tem três camadas.

**A Primeira:** onde os aventureiros entram. Com goblins, aranhas, perigos visíveis.
**A Segunda:** onde apenas os experientes chegam. Os espíritos moram aqui.
**A Terceira:** onde ninguém volta. Lá fica o coração da floresta.

No coração existe uma árvore tão antiga que seus galhos tocam outros mundos.
Seus frutos concedem visões do passado e do futuro.

*Um fruto faz você ver tudo que já foi.*
*O outro, tudo que ainda será.*
*O terceiro... ninguém sabe. Ninguém comeu e se lembrou.*

— Druida Vel, desaparecido"""
        },
        {
            "title": "📖 Diário da Druida Sylvara — Entradas Escolhidas",
            "content": """*Escrito com tinta feita de seiva e terra...*

**Entrada 47:**
O Ent Ancião falou comigo hoje. Em 30 anos, é a segunda vez.

Ele disse: *'A floresta sangra.'*

Perguntei por quê. Ele disse: *'Porque os humanos esqueceram como ouvir.'*

Fiquei em silêncio por um longo tempo.

Depois ele disse algo que não consigo parar de pensar:
*'Não temo o fogo, nem o machado. Temo o esquecimento.
Porque uma árvore que ninguém lembra jamais existiu.'*

**Entrada 89:**
Hoje um aventureiro perguntou se a floresta é perigosa.
Respondi: *'A floresta é justa. Ela trata você como você a trata.'*
Ele não entendeu. Talvez entenda quando sair.

— Sylvara, Guardiã"""
        }
    ],
    20: [
        {
            "title": "📖 O Papiro da Eternidade — Tradução Incompleta",
            "content": """*Caracteres dourados sobre papiro preservado por magia...*

**'O Ciclo das Eras'**

O Deserto das Almas não é um deserto natural.

Há 5.000 anos, era um jardim. O mais belo do mundo.
Havia rios, florestas, cidades de ouro e cristal.

Então veio a Maldição do Faraó Kha-Mentu —
mas não como punição. Como *proteção*.

Kha-Mentu transformou o paraíso em deserto
para que os invasores não desejassem mais conquistá-lo.
Sacrificou a beleza para salvar os segredos.

*'O maior ato de amor pode parecer destruição para quem não entende.'*

Sob as areias ainda dormem as maravilhas do jardim original.
Esperando por alguém digno de acordá-las.

— Fragmento da Biblioteca do Faraó, Nível -7"""
        },
        {
            "title": "📖 O Livro dos Espíritos — Capítulo das Múmias",
            "content": """*Páginas que parecem sugar o calor das suas mãos...*

**'Por Que os Mortos Caminham'**

As múmias não são monstros. São guardas.

Cada múmia foi uma pessoa real que, em vida,
jurou proteger algo até o fim dos tempos.
Quando morreram, o juramento continuou.

O problema é que elas esqueceram o quê estão protegendo.
Lembram apenas do juramento.

*'Uma múmia que lembra o que protege se ajoelha diante do digno.
Uma múmia que esqueceu ataca tudo que se move.'*

Se você encontrar uma múmia que para e te olha sem atacar —
ela está lembrando. Não a interrompa.

Talvez ela encontre o que procura em você.

— Nefertiri, Guardiã dos Conhecimentos"""
        }
    ],
    30: [
        {
            "title": "📖 Sagas do Gelo — Volume III",
            "content": """*Pergaminho enrijecido pelo frio, mas legível...*

**'Os Titãs do Gelo'**

Antes dos humanos existirem, os Titãs do Gelo governavam estas montanhas.

Eram seres de 30 metros de altura, feitos de cristal e vento,
com memórias que se estendiam por eras geológicas.

Eles não lutavam. Criavam.
Cada Titã era responsável por uma lei da natureza:
— Boreas: o frio
— Glacius: o tempo (no sentido meteorológico)
— Permafrost: a permanência das coisas

Os humanos os confundiram com inimigos e atacaram.
Os Titãs, confusos com tamanha agressividade em seres tão pequenos,
*recuaram*.

Eles ainda estão aqui. Apenas menores. Esperando ser compreendidos.
O Yeti Colossal é um eco da memória deles.

— Bjorn, Anciãos das Montanhas"""
        },
        {
            "title": "📖 O Cristal do Inverno — Lenda Completa",
            "content": """*Glifos rúnicos que parecem pulsar com frio azul...*

**'O Segredo nas Profundezas'**

O Cristal do Inverno Eterno não é apenas uma joia.

É um arquivo. Um registro de tudo que já existiu e morreu no frio.
Cada criatura que morreu nestas montanhas tem sua memória guardada ali.

Por isso os Titãs do Gelo o protegiam com tanto cuidado.
Era a *biblioteca da morte* deles.

O Yeti Colossal, Krom, sente cada memória armazenada
como se fossem suas próprias. Sente a dor de cada ser.
É por isso que está sempre em sofrimento.

*'Quem derrotar Krom com compaixão, não com ódio,
pode ouvir ele sussurrar o nome do ser que mais sente falta.'*

Dizem que é sempre o mesmo nome.
Mas ninguém que ouviu jamais revelou qual é.

— Fragmento, Fortaleza Permafrost"""
        }
    ],
    40: [
        {
            "title": "📖 O Códice do Fogo — Primeira Revelação",
            "content": """*Gravado em obsidiana, legível apenas à luz do fogo...*

**'A Profecia de Ignarius'**

No dia em que o último vulcão se apagar,
o dragão retornará ao fogo primordial.

Mas antes disso, ele testará os guerreiros:
*'Apenas quem sobreviver ao fogo sem se tornar cinza
merece carregar a Chama Original em seu coração.'*

A Chama Original não é uma arma. É uma responsabilidade.
Quem a carrega sente o peso de tudo que foi criado com fogo:
cada estrela, cada vida, cada sonho que aqueceu alguém na noite fria.

Os Anões que forjaram as primeiras armas dos deuses carregavam essa chama.
Por isso suas criações eram imortais.

*'Forja com fogo do coração, não das mãos.'*

— Profeta Ignar, última visão antes de se tornar cinzas"""
        },
        {
            "title": "📖 Memórias de Lava — Registro Vulcânico",
            "content": """*Palavras que parecem ainda quentes ao toque...*

**'Civilização Antes do Fogo'**

Poucos sabem que o Reino Vulcânico foi habitado por uma civilização avançada.

Os Forjadores — assim eram chamados — dominavam a metalurgia mágica.
Criavam objetos que tinham *alma*: que sentiam, que pensavam, que escolhiam seus donos.

Quando Ignarius despertou pela última vez, eles não fugiram.
Fizeram uma escolha coletiva: fundir-se com o dragão.
Voluntariamente.

Agora Ignarius carrega dentro de si as memórias de toda uma civilização.
Cada rugido é uma canção em idioma extinto.
Cada chama é um nome que não existe mais.

*'Quando você derrota Ignarius, você libera as almas presas nele.
Não é uma batalha. É um funeral que durou 1.000 anos.'*

— Doran, Mestre-Ferreiro, herdeiro da tradição"""
        }
    ],
    50: [
        {
            "title": "📖 O Tratado do Vazio — Tradução Proibida",
            "content": """*As palavras se movem enquanto você as lê. Literalmente.*

**'O Que Existe Antes do Nada'**

Filósofos debatem há milênios sobre o que existe após a morte.
Poucos perguntam o que existia antes do nascimento.

A resposta é o Abismo Arcano.

Cada alma que nasce vem do Abismo.
Cada alma que morre retorna ao Abismo.
O Senhor das Sombras não é um vilão — é um *administrador*.

Ele cuida das almas em trânsito.
Ordena o caos entre o antes e o depois.

O problema é que há almas que não querem ir embora.
Que querem ficar no Abismo para sempre.
E o Senhor das Sombras não tem autoridade para forçá-las.

*'Todo monstro que você enfrenta no Abismo
era uma vez uma alma que tinha medo de seguir em frente.'*

— Spectra, Bibliotecária do Abismo"""
        },
        {
            "title": "📖 Cartas do Arquimago Zephyr — Correspondência Final",
            "content": """*Letras que brilham e se apagam alternadamente...*

**Para meu sucessor, seja você quem for:**

Passei 200 anos estudando o Abismo Arcano.
Aprendi uma coisa: quanto mais você sabe, mais você entende que não sabe nada.

As entidades do Vazio não são más.
São *antigas*. E antigas demais para entender coisas novas como você.

Quando encontrares o Senhor das Sombras,
não o trate como inimigo.
Trate-o como um ser que está aqui há muito mais tempo que você
e está muito, muito cansado.

Às vezes o maior ato de compaixão é dar descanso a quem não pode morrer.

*'O verdadeiro poder do Abismo não é destruição. É transformação.'*

Com esperança no futuro,
Arquimago Zephyr
P.S.: Meu livro de magias está escondido na Dimensão Invertida. Você vai precisar."""
        }
    ]
}

# ================= NPCs POR CIDADE =================
CITY_NPCS = {
    1: {
        "city_name": "🏘️ Vila dos Primeiros Passos",
        "npcs": [
            {
                "name": "Aldeão Theron",
                "role": "Fazendeiro",
                "emoji": "👨‍🌾",
                "dialogues": [
                    "Bem-vindo, viajante! Estes campos parecem simples, mas escondem mais segredos do que imaginamos.",
                    "Meu avô dizia que o primeiro Slime a aparecer nestes campos nasceu de uma lágrima do céu.",
                    "Você parece forte. Talvez pudesse ajudar com a praga dos ratos? Os Campos precisam de heróis como você.",
                    "Dizem que nas noites de lua cheia, o Slime Rei aparece no centro do campo. Ninguém voltou para confirmar... ainda."
                ]
            },
            {
                "name": "Curandeira Elara",
                "role": "Curandeira da Vila",
                "emoji": "👩‍⚕️",
                "dialogues": [
                    "As ervas destes campos têm propriedades mágicas. Cada planta guarda uma história.",
                    "Aprendi a curar com minha mãe, que aprendeu com a sua. A arte de curar é tão antiga quanto a dor.",
                    "Cuidado com as vespas gigantes ao norte. Seu veneno não mata rapidamente, mas faz você desejar que matasse.",
                    "Se precisar de uma poção, posso preparar algo... mas os ingredientes são raros por aqui."
                ]
            },
            {
                "name": "Capitão Aldric",
                "role": "Guarda da Vila",
                "emoji": "💂",
                "dialogues": [
                    "Fui aventureiro antes de ser guarda. Aprendi que trabalho em equipe salva mais vidas do que força individual.",
                    "O Slime Rei foi derrotado uma vez, há 50 anos. Mas os slimes absorvem a magia da terra e renascem.",
                    "Recrute companheiros se quiser enfrentar os grandes perigos. Nenhum herói conquista o mundo sozinho.",
                    "Minha espada está enferrujada agora. Mas já matei um boss com ela. Os tempos bons..."
                ]
            }
        ]
    },
    10: {
        "city_name": "🌲 Acampamento das Sombras",
        "npcs": [
            {
                "name": "Druida Sylvara",
                "role": "Guardiã da Floresta",
                "emoji": "🧙‍♀️",
                "dialogues": [
                    "A floresta fala para aqueles que sabem ouvir. Você consegue ouvi-la?",
                    "O Ent Ancião está inquieto. Algo perturba seu sono milenar. Temo o que pode acontecer se ele despertar com raiva.",
                    "Cada árvore aqui tem um nome. Eu os conheço todos. São minha família.",
                    "Os goblins desta floresta não são naturalmente maus. Algo os corrompeu. Descubra o que é e talvez encontre paz."
                ]
            },
            {
                "name": "Mercador Brynn",
                "role": "Comerciante Errante",
                "emoji": "🧔",
                "dialogues": [
                    "Comércio é a única linguagem universal. Até monstros têm preço.",
                    "Passei por aqui há um mês. A floresta estava diferente. Mais... viva. Não da forma boa.",
                    "Procuro a Teia Mágica das Aranhas Gigantes. Pago bem. Muito bem.",
                    "Ei, você não parece daqui. De onde veio? Dos Campos? Ah, a nostalgia..."
                ]
            }
        ]
    },
    20: {
        "city_name": "🏜️ Oásis de Amun",
        "npcs": [
            {
                "name": "Sábia Nefertiri",
                "role": "Guardiã dos Conhecimentos Antigos",
                "emoji": "👑",
                "dialogues": [
                    "Os hieróglifos nas pirâmides não são decoração. São advertências. Poucos tomam o cuidado de lê-las.",
                    "O Faraó Kha-Mentu não era um vilão. Era um rei traído. Há diferença.",
                    "Esta areia foi mar profundo uma vez. Tudo muda. Tudo passa. Até o deserto.",
                    "Você busca riquezas? As maiores riquezas deste deserto são os conhecimentos enterrados junto com os mortos."
                ]
            },
            {
                "name": "Nômade Hassan",
                "role": "Guia do Deserto",
                "emoji": "🧕",
                "dialogues": [
                    "O deserto testa cada viajante de forma diferente. Ele sabe o que você mais teme.",
                    "Minha família guia viajantes nestas areias há sete gerações. Perdemos apenas três. Não foi culpa nossa.",
                    "Há uma tempestade chegando. De areia ou de destino, não sei dizer. Mas algo está por vir.",
                    "O escorpião que te pica é o mesmo que te salva do veneno de outro. A vida no deserto é assim."
                ]
            }
        ]
    },
    30: {
        "city_name": "❄️ Fortaleza Permafrost",
        "npcs": [
            {
                "name": "Ancião da Montanha Bjorn",
                "role": "Líder Tribal",
                "emoji": "🧓",
                "dialogues": [
                    "Vivi 80 invernos nestas montanhas. O frio não é inimigo — é professor.",
                    "O Yeti não é um monstro. É um guardião mal compreendido. Mas compreender não significa que ele não vai te matar.",
                    "Há uma passagem secreta através das montanhas. Apenas os dignos a encontram. Você tem o que é necessário?",
                    "Meu pai viu os Titãs do Gelo uma vez. Disse que eram lindos e aterrorizantes ao mesmo tempo."
                ]
            },
            {
                "name": "Ferreiro Helga",
                "role": "Ferreria das Montanhas",
                "emoji": "⚒️",
                "dialogues": [
                    "Armas feitas com cristal de gelo nunca enferrujam. Nunca quebram. Nunca esquecem o sangue que derramaram.",
                    "Trabalhei para reis. Trabalhei para heróis. Nenhum deles agradeceu como você agradece com moedas.",
                    "O segredo de uma boa armadura não é a dureza. É a flexibilidade. Como a vida.",
                    "Preciso de mais cristais de gelo. Os das profundezas. Os outros não têm poder suficiente."
                ]
            }
        ]
    },
    40: {
        "city_name": "🌋 Cidadela Cinzenta",
        "npcs": [
            {
                "name": "Profeta Ignar",
                "role": "Profeta do Fogo",
                "emoji": "🔥",
                "dialogues": [
                    "O fogo não destrói. Transforma. Há diferença fundamental entre os dois.",
                    "Ignarius desperta a cada geração para testar se a humanidade evoluiu. Ela nunca evolui.",
                    "Vejo em suas chamas um destino extraordinário. Ou uma morte extraordinária. Difícil distinguir.",
                    "A Forja Sagrada é real. Eu a vi. Uma vez. Durou um segundo que pareceu uma eternidade."
                ]
            },
            {
                "name": "Anão-Mestre Doran",
                "role": "Mestre Ferreiro Divino",
                "emoji": "⚙️",
                "dialogues": [
                    "Em 300 anos de forja, nunca criei algo que não pudesse ser melhorado. Incluindo eu mesmo.",
                    "As melhores armas têm nomes. Você saberia como nomear a sua?",
                    "A Forja Sagrada foi criada pelos próprios deuses. Reacendê-la... bem. Que coisa seria essa.",
                    "Anões não temem a morte. Tememos morrer antes de terminar nossa obra-prima."
                ]
            }
        ]
    },
    50: {
        "city_name": "🌌 Torre do Conhecimento Perdido",
        "npcs": [
            {
                "name": "Arquimago Zephyr",
                "role": "Arquimago do Abismo",
                "emoji": "🧙",
                "dialogues": [
                    "A magia não é poder. É responsabilidade. O poder vem da sabedoria de quando não usar a magia.",
                    "Estudei o Senhor das Sombras por 200 anos. Quanto mais entendo, mais temo. E mais o compreendo.",
                    "O Abismo Arcano distorce a realidade, mas também revela verdades que a realidade normal esconde.",
                    "Você chegou até aqui. Isso significa que está pronto — ou é inconsciente demais para saber que não está."
                ]
            },
            {
                "name": "Bibliotecária Spectra",
                "role": "Guardiã dos Tomos Proibidos",
                "emoji": "📚",
                "dialogues": [
                    "Cada livro proibido foi proibido por uma razão. Geralmente por pessoas que queriam o conhecimento só para si.",
                    "Li um texto que descrevia o fim do universo. Depois disso, o chá nunca mais teve o mesmo gosto.",
                    "Conhecimento não é perigoso. O que fazemos com ele é que pode ser.",
                    "Procura algum livro em especial? Tenho... categorias especiais. Para visitantes especiais."
                ]
            }
        ]
    },
    60: {
        "city_name": "👑 Antecâmara do Trono",
        "npcs": [
            {
                "name": "Guardião Estelar Auron",
                "role": "Guardião do Trono Celestial",
                "emoji": "⚜️",
                "dialogues": [
                    "Poucos chegam até aqui. Menos ainda estão prontos para o que vem a seguir.",
                    "O Imperador Astral conhece seu nome desde o dia em que você nasceu. Ele esteve esperando.",
                    "Não venho aqui para dissuadi-lo. Venho para honrar sua jornada. O que você fez foi extraordinário.",
                    "O Trono Celestial não é um lugar. É um estado de ser. Você está se tornando algo além de mortal."
                ]
            },
            {
                "name": "Alma de Herói Lendário",
                "role": "Espírito dos Que Vieram Antes",
                "emoji": "👻",
                "dialogues": [
                    "Cheguei aqui antes de você. Falhei. Mas minha falha abriu o caminho para o seu sucesso.",
                    "Não tenho arrependimentos. Cada escolha que fiz me trouxe até aqui — mesmo depois da morte.",
                    "O Imperador... não é o que parece. Esteja preparado para a surpresa de sua vida.",
                    "Lute bem. Lute com honra. E quando terminar — não esqueça de onde veio."
                ]
            }
        ]
    }
}

# ================= MUNDOS E EVENTOS =================
WORLDS = {
    1: {
        "name": "🌱 Campos Iniciais",
        "emoji": "🌱",
        "xp_loss_multiplier": 0.3,
        "monsters": {
            "Slime": {"xp": (10, 20), "hp": 30, "atk": 5, "coins": (1, 3)},
            "Rato Selvagem": {"xp": (12, 22), "hp": 25, "atk": 7, "coins": (1, 4)},
            "Coelho Raivoso": {"xp": (11, 21), "hp": 20, "atk": 6, "coins": (1, 3)},
            "Javali Jovem": {"xp": (13, 23), "hp": 35, "atk": 8, "coins": (2, 5)},
            "Vespa Gigante": {"xp": (12, 22), "hp": 22, "atk": 7, "coins": (1, 4)}
        },
        "boss": {"name": "Slime Rei", "hp": 420, "atk": 38, "xp": 500, "level": 9, "coins": (50, 100)},
        "resources": ["Pedra fraca", "Grama mágica", "Couro de rato", "Flor silvestre", "Mel selvagem"],
        "dungeons": [
            {"name": "Caverna dos Slimes", "level": 1, "boss": "Slime Ancião"},
            {"name": "Toca dos Ratos", "level": 2, "boss": "Rato Rei"},
            {"name": "Ninho de Vespas", "level": 3, "boss": "Vespa Rainha"}
        ],
        "secret_dungeons": [
            {"name": "🕳️ Gruta Esquecida", "level": 1, "boss": "Guardião Primordial dos Campos", "secret": True},
            {"name": "🌀 Buraco no Tecido da Realidade", "level": 2, "boss": "Anomalia Viva", "secret": True}
        ],
        "events": [
            "Você encontra um riacho cristalino. A água brilha sob o sol.",
            "Um bando de pássaros voa sobre você, cantando melodias antigas.",
            "Você tropeça em uma pedra e cai de cara no chão.",
            "Uma borboleta dourada pousa em seu ombro por um instante.",
            "O vento carrega o aroma de flores silvestres.",
            "Você ouve risadas ao longe, mas não vê ninguém.",
            "Pegadas estranhas marcam o solo à sua frente.",
            "Uma névoa suave cobre o campo por alguns momentos.",
            "Você encontra um velho cajado abandonado no caminho.",
            "Um arco-íris surge após uma chuva rápida.",
            "Você pisa em um espinho e sente uma dor aguda.",
            "Uma placa enferrujada aponta para direções desconhecidas.",
            "Você encontra moedas espalhadas pelo chão.",
            "Um esquilo rouba sua comida e foge para uma árvore.",
            "Você sente uma presença te observando entre a grama alta.",
            "Uma criança perdida pede ajuda para encontrar o caminho.",
            "Você encontra um diário rasgado com histórias antigas.",
            "O sol se põe, pintando o céu de laranja e roxo.",
            "Você encontra uma fonte antiga com água mágica.",
            "Um mercador errante oferece itens misteriosos.",
            "Você ouve o som de uma batalha ao longe.",
            "Pegadas de sangue levam a uma caverna escura."
        ]
    },
    10: {
        "name": "🌲 Floresta Sombria",
        "emoji": "🌲",
        "xp_loss_multiplier": 0.5,
        "monsters": {
            "Goblin": {"xp": (25, 40), "hp": 60, "atk": 12, "coins": (3, 8)},
            "Lobo Negro": {"xp": (28, 45), "hp": 70, "atk": 15, "coins": (4, 9)},
            "Aranha Gigante": {"xp": (30, 43), "hp": 65, "atk": 14, "coins": (3, 8)},
            "Ogro Menor": {"xp": (32, 47), "hp": 80, "atk": 16, "coins": (5, 10)},
            "Espectro Florestal": {"xp": (29, 44), "hp": 55, "atk": 13, "coins": (4, 9)}
        },
        "boss": {"name": "Ent Ancião", "hp": 840, "atk": 63, "xp": 900, "level": 19, "coins": (100, 200)},
        "resources": ["Madeira escura", "Ervas raras", "Pele de lobo", "Teia mágica", "Musgo brilhante"],
        "dungeons": [
            {"name": "Covil dos Goblins", "level": 4, "boss": "Chefe Goblin"},
            {"name": "Ninho de Aranhas", "level": 5, "boss": "Aranha Rainha"},
            {"name": "Caverna do Ogro", "level": 6, "boss": "Ogro Cruel"}
        ],
        "secret_dungeons": [
            {"name": "🌑 Floresta Invertida", "level": 4, "boss": "Reflexo Sombrio", "secret": True},
            {"name": "🍄 Reino dos Cogumelos", "level": 5, "boss": "Rei Fúngico", "secret": True}
        ],
        "events": [
            "Galhos se movem sozinhos ao seu redor, como se estivessem vivos.",
            "Você ouve sussurros entre as árvores, mas não entende as palavras.",
            "Uma coruja de olhos vermelhos te observa de um galho alto.",
            "Raízes tentam prender seus pés enquanto você caminha.",
            "Você encontra um círculo de cogumelos brilhantes.",
            "Neblina densa obscurece sua visão por alguns minutos.",
            "Um veado fantasmagórico atravessa seu caminho e desaparece.",
            "Você tropeça e cai em um buraco coberto de folhas.",
            "Luzes misteriosas dançam entre as árvores.",
            "Você encontra um altar antigo coberto de musgo.",
            "Corvos negros grasnam alto, como se estivessem te alertando.",
            "Uma árvore cai perto de você com um estrondo.",
            "Você encontra marcas de garras profundas em um tronco.",
            "Um caminho de pétalas negras aparece misteriosamente.",
            "Você ouve o choro de uma criança, mas não encontra ninguém.",
            "Aranhas gigantes tecem teias bloqueando seu caminho.",
            "Você encontra um esqueleto segurando um mapa antigo.",
            "A lua cheia ilumina clareiras entre as árvores.",
            "Você encontra uma casa abandonada com a porta entreaberta.",
            "Olhos brilhantes te observam da escuridão.",
            "Você sente algo te seguindo, mas ao olhar não vê nada.",
            "Um portal de energia aparece brevemente e desaparece."
        ]
    },
    20: {
        "name": "🏜️ Deserto das Almas",
        "emoji": "🏜️",
        "xp_loss_multiplier": 0.7,
        "monsters": {
            "Escorpião Gigante": {"xp": (40, 60), "hp": 100, "atk": 20, "coins": (5, 12)},
            "Múmia": {"xp": (45, 65), "hp": 120, "atk": 22, "coins": (6, 13)},
            "Serpente de Areia": {"xp": (43, 63), "hp": 110, "atk": 21, "coins": (5, 12)},
            "Guardião de Tumba": {"xp": (47, 67), "hp": 130, "atk": 24, "coins": (7, 14)},
            "Espírito do Deserto": {"xp": (44, 64), "hp": 105, "atk": 20, "coins": (5, 12)}
        },
        "boss": {"name": "Faraó Amaldiçoado", "hp": 1400, "atk": 98, "xp": 1400, "level": 29, "coins": (180, 350)},
        "resources": ["Areia mágica", "Ossos antigos", "Vendas místicas", "Escaravelho dourado", "Papiro antigo"],
        "dungeons": [
            {"name": "Pirâmide Perdida", "level": 7, "boss": "Faraó Esquecido"},
            {"name": "Tumba dos Reis", "level": 8, "boss": "Anúbis Menor"},
            {"name": "Templo Subterrâneo", "level": 9, "boss": "Esfinge Guardiã"}
        ],
        "secret_dungeons": [
            {"name": "⭐ Oásis do Tempo Invertido", "level": 7, "boss": "Guardião do Paradoxo", "secret": True},
            {"name": "🏺 Catacumba dos Faraós Esquecidos", "level": 8, "boss": "Faraó Primordial", "secret": True}
        ],
        "events": [
            "Uma tempestade de areia surge do nada, cegando você temporariamente.",
            "Você afunda na areia movediça e luta para sair.",
            "Miragens de oásis aparecem ao longe, tentando te enganar.",
            "Você encontra uma pirâmide semi-enterrada na areia.",
            "Hieróglifos brilhantes aparecem nas dunas ao seu redor.",
            "Um escorpião gigante emerge da areia perto de você.",
            "Você encontra um sarcófago aberto e vazio.",
            "O sol escaldante te deixa exausto e sedento.",
            "Você ouve cânticos ancestrais vindos das dunas.",
            "Uma caravana de espíritos passa por você sem te notar.",
            "Você encontra joias espalhadas entre ossos antigos.",
            "Um redemoinho de areia forma uma figura humanóide.",
            "Você cai em uma armadilha antiga cheia de flechas.",
            "Marcas de antigas batalhas cobrem as ruínas ao redor.",
            "A lua ilumina hieróglifos que contam histórias perdidas.",
            "Você encontra um oásis real com água fresca.",
            "Serpentes de areia deslizam rapidamente ao seu redor.",
            "Você vê vultos de múmias caminhando ao longe.",
            "Uma maldição antiga faz você sentir fraqueza.",
            "Você encontra um amuleto enterrado na areia.",
            "Templos subterrâneos são revelados por ventos fortes.",
            "Você ouve o rugido de algo gigantesco sob a areia."
        ]
    },
    30: {
        "name": "❄️ Montanhas Geladas",
        "emoji": "❄️",
        "xp_loss_multiplier": 0.9,
        "monsters": {
            "Lobo de Gelo": {"xp": (60, 80), "hp": 150, "atk": 28, "coins": (7, 15)},
            "Golem de Neve": {"xp": (65, 85), "hp": 180, "atk": 30, "coins": (8, 16)},
            "Ogro Glacial": {"xp": (63, 83), "hp": 160, "atk": 29, "coins": (7, 15)},
            "Dragão de Gelo Jovem": {"xp": (70, 90), "hp": 200, "atk": 32, "coins": (10, 18)},
            "Elemental de Gelo": {"xp": (67, 87), "hp": 170, "atk": 31, "coins": (8, 16)}
        },
        "boss": {"name": "Yeti Colossal", "hp": 2100, "atk": 133, "xp": 2000, "level": 39, "coins": (280, 500)},
        "resources": ["Cristal de gelo", "Minério frio", "Pele de yeti", "Neve eterna", "Gema congelada"],
        "dungeons": [
            {"name": "Caverna Congelada", "level": 10, "boss": "Guardião do Gelo"},
            {"name": "Fortaleza de Gelo", "level": 11, "boss": "Rei do Inverno"},
            {"name": "Abismo Glacial", "level": 12, "boss": "Dragão Ancestral"}
        ],
        "secret_dungeons": [
            {"name": "🌨️ Núcleo do Inverno Eterno", "level": 10, "boss": "Titã do Gelo", "secret": True},
            {"name": "❄️ Palácio de Cristal Perdido", "level": 11, "boss": "Rainha das Neves", "secret": True}
        ],
        "events": [
            "Uma avalanche desce pela montanha em sua direção.",
            "Você escorrega em gelo fino e cai em uma fenda.",
            "O frio intenso congela suas roupas e músculos.",
            "Você encontra um viajante congelado segurando um mapa.",
            "Cristais de gelo cantam melodias com o vento.",
            "Uma tempestade de neve bloqueia completamente sua visão.",
            "Você encontra uma caverna quente com fontes termais.",
            "Pegadas gigantescas estão impressas na neve.",
            "Você ouve rugidos ecoando entre os picos.",
            "Estalactites de gelo caem perigosamente perto de você.",
            "Você encontra um monastério abandonado no topo.",
            "Espíritos congelados aparecem brevemente na nevasca.",
            "Você cai através de neve falsa em uma caverna.",
            "Lobos uivam ao longe sob a lua cheia.",
            "Você encontra equipamentos de expedições antigas.",
            "O vento forma figuras assustadoras com a neve.",
            "Você sente a montanha tremer levemente.",
            "Cristais gigantes emergem do gelo à sua frente.",
            "Você encontra marcas de batalha antigas no gelo.",
            "Uma ponte de gelo quebra sob seus pés.",
            "Você vê uma silhueta gigantesca no topo da montanha.",
            "A temperatura cai drasticamente de repente."
        ]
    },
    40: {
        "name": "🌋 Reino Vulcânico",
        "emoji": "🌋",
        "xp_loss_multiplier": 1.2,
        "monsters": {
            "Salamandra": {"xp": (80, 100), "hp": 200, "atk": 38, "coins": (10, 20)},
            "Demônio de Lava": {"xp": (85, 105), "hp": 230, "atk": 42, "coins": (12, 22)},
            "Elemental de Fogo": {"xp": (83, 103), "hp": 210, "atk": 40, "coins": (11, 21)},
            "Hidra de Magma": {"xp": (90, 110), "hp": 250, "atk": 45, "coins": (13, 23)},
            "Fênix Negra": {"xp": (87, 107), "hp": 220, "atk": 43, "coins": (12, 22)}
        },
        "boss": {"name": "Dragão de Magma", "hp": 3150, "atk": 182, "xp": 2800, "level": 49, "coins": (400, 700)},
        "resources": ["Pedra vulcânica", "Núcleo de fogo", "Escamas de dragão", "Obsidiana pura", "Cinza sagrada"],
        "dungeons": [
            {"name": "Caldeirão de Lava", "level": 13, "boss": "Senhor do Fogo"},
            {"name": "Forja Infernal", "level": 14, "boss": "Titã Flamejante"},
            {"name": "Coração do Vulcão", "level": 15, "boss": "Ifrit Primordial"}
        ],
        "secret_dungeons": [
            {"name": "🔥 Câmara da Chama Original", "level": 13, "boss": "Aspecto do Fogo Primordial", "secret": True},
            {"name": "🌋 Ventre do Vulcão Vivo", "level": 14, "boss": "Espírito do Vulcão", "secret": True}
        ],
        "events": [
            "Lava jorra de uma fissura bem ao seu lado.",
            "O chão racha e revela rios de magma abaixo.",
            "Gases tóxicos sobem de buracos fumegantes.",
            "Você tropeça e quase cai em um poço de lava.",
            "Um gêiser de lava explode próximo a você.",
            "Pedras incandescentes chovem do céu.",
            "Você encontra ruínas de uma civilização antiga queimada.",
            "O calor derrete parcialmente seu equipamento.",
            "Salamandras gigantes nadam livremente na lava.",
            "Você ouve rugidos vindos de cavernas profundas.",
            "Um vulcão ao longe entra em erupção.",
            "Você encontra cristais de fogo pulsantes.",
            "Demônios observam você das sombras flamejantes.",
            "Pontes de pedra desmoronam sob seus pés.",
            "Você vê esqueletos de aventureiros anteriores.",
            "Chamas azuis dançam misteriosamente ao redor.",
            "Você encontra um altar dedicado ao deus do fogo.",
            "A fumaça densa te faz tossir e perder a direção.",
            "Você sente tremores constantes sob seus pés.",
            "Criaturas de magma emergem das profundezas.",
            "Você encontra um ovo de dragão rachado e vazio.",
            "Asas gigantescas bloqueiam brevemente o sol vermelho."
        ]
    },
    50: {
        "name": "🌌 Abismo Arcano",
        "emoji": "🌌",
        "xp_loss_multiplier": 1.5,
        "monsters": {
            "Espectro": {"xp": (100, 130), "hp": 280, "atk": 48, "coins": (12, 22)},
            "Mago Sombrio": {"xp": (105, 135), "hp": 300, "atk": 52, "coins": (14, 24)},
            "Devorador de Almas": {"xp": (103, 133), "hp": 290, "atk": 50, "coins": (13, 23)},
            "Lich": {"xp": (110, 140), "hp": 320, "atk": 55, "coins": (15, 25)},
            "Golem Arcano": {"xp": (107, 137), "hp": 310, "atk": 53, "coins": (14, 24)}
        },
        "boss": {"name": "Senhor das Sombras", "hp": 4900, "atk": 245, "xp": 4000, "level": 59, "coins": (600, 1000)},
        "resources": ["Essência arcana", "Fragmento sombrio", "Cristal do vazio", "Poeira estelar", "Runa mística"],
        "dungeons": [
            {"name": "Torre Arcana", "level": 16, "boss": "Arquimago Corrupto"},
            {"name": "Dimensão Sombria", "level": 17, "boss": "Entidade do Vazio"},
            {"name": "Biblioteca Proibida", "level": 18, "boss": "Guardião do Conhecimento"}
        ],
        "secret_dungeons": [
            {"name": "♾️ Loop Temporal Permanente", "level": 16, "boss": "Eco de Si Mesmo", "secret": True},
            {"name": "🌀 Dimensão Invertida", "level": 17, "boss": "Anti-Matéria Viva", "secret": True}
        ],
        "events": [
            "A gravidade inverte e você flutua sem controle.",
            "Portais dimensionais abrem e fecham ao seu redor.",
            "Você vê versões alternativas de si mesmo passando.",
            "O tempo parece congelar por alguns segundos.",
            "Sussurros de milhares de vozes ecoam em sua mente.",
            "Você atravessa uma cortina de energia e sente dor.",
            "Estrelas cadentes atravessam o vazio infinito.",
            "Você encontra fragmentos de realidades destruídas.",
            "Sombras ganham vida e tentam te tocar.",
            "Você vê memórias de pessoas desconhecidas.",
            "A realidade se distorce formando figuras impossíveis.",
            "Você sente sua essência sendo puxada do corpo.",
            "Criaturas do vazio te observam da escuridão.",
            "Você encontra um livro que escreve sozinho.",
            "Pontes de energia aparecem e desaparecem.",
            "Você ouve profecias sobre seu futuro.",
            "Magos mortos oferecem conhecimento proibido.",
            "Você cai em um loop temporal por instantes.",
            "Olhos gigantes se abrem no céu escuro.",
            "Você encontra artefatos de eras esquecidas.",
            "A linha entre sonho e realidade desaparece.",
            "Uma entidade cósmica nota sua presença."
        ]
    },
    60: {
        "name": "👑 Trono Celestial",
        "emoji": "👑",
        "xp_loss_multiplier": 2.0,
        "monsters": {
            "Guardião Celestial": {"xp": (140, 180), "hp": 400, "atk": 65, "coins": (15, 28)},
            "Anjo Caído": {"xp": (145, 185), "hp": 420, "atk": 68, "coins": (16, 30)},
            "Serafim Corrompido": {"xp": (150, 190), "hp": 450, "atk": 70, "coins": (18, 32)},
            "Querubim Guerreiro": {"xp": (155, 195), "hp": 480, "atk": 73, "coins": (19, 34)},
            "Arcanjo Negro": {"xp": (160, 200), "hp": 500, "atk": 75, "coins": (20, 35)}
        },
        "boss": {"name": "Imperador Astral", "hp": 2500, "atk": 100, "xp": 2500, "level": 60, "coins": (80, 160)},
        "resources": ["Essência celestial", "Fragmento estelar", "Coroa divina", "Lágrima de deus", "Pluma sagrada"],
        "dungeons": [
            {"name": "Santuário Celestial", "level": 19, "boss": "Avatar Divino"},
            {"name": "Palácio Estelar", "level": 20, "boss": "Deus Menor"},
            {"name": "Portal da Eternidade", "level": 21, "boss": "Guardião Final"}
        ],
        "secret_dungeons": [
            {"name": "🌌 Além do Trono", "level": 19, "boss": "O Que Não Tem Nome", "secret": True},
            {"name": "✨ Raiz da Criação", "level": 20, "boss": "Deus Esquecido", "secret": True}
        ],
        "events": [
            "Raios divinos atravessam as nuvens douradas.",
            "Você caminha sobre um chão de estrelas solidificadas.",
            "Anjos cantam hinos em línguas antigas.",
            "Você sente o peso de mil olhares celestiais.",
            "Portões gigantescos se abrem revelando o infinito.",
            "Suas feridas curam instantaneamente por luz divina.",
            "Você vê deuses antigos esculpidos em ouro.",
            "Colunas de mármore sustentam o próprio céu.",
            "Você encontra armas que mataram divindades.",
            "O trono vazio pulsa com poder incompreensível.",
            "Guardiões imortais testam sua dignidade.",
            "Você ouve profecias sobre o fim de todas as coisas.",
            "Asas de luz brotam temporariamente de suas costas.",
            "Você vê a criação e destruição de mundos.",
            "Energias primordiais fluem através de você.",
            "Você encontra o livro do destino aberto.",
            "Almas de heróis lendários te cumprimentam.",
            "Você sente o conhecimento de tudo por um instante.",
            "O Imperador te observa do trono distante.",
            "Você encontra a espada que cortou a primeira estrela.",
            "Sua mortalidade é questionada pela própria existência.",
            "Você está a um passo de se tornar uma lenda eterna."
        ]
    },
    # ─── REINO 8: PÂNTANO DAS ALMAS PERDIDAS (desbloqueado no nível 62) ───
    62: {
        "name": "🌿 Pântano das Almas Perdidas",
        "emoji": "🌿",
        "xp_loss_multiplier": 2.1,
        "monsters": {
            "Criatura do Pântano": {"xp": (170, 210), "hp": 520, "atk": 78, "coins": (22, 38)},
            "Espírito Lamacento": {"xp": (175, 215), "hp": 540, "atk": 80, "coins": (23, 40)},
            "Serpente das Profundezas": {"xp": (180, 220), "hp": 560, "atk": 83, "coins": (24, 42)},
            "Bruxo das Trevas Úmidas": {"xp": (185, 225), "hp": 580, "atk": 85, "coins": (25, 44)},
            "Jacaré Arcano": {"xp": (190, 230), "hp": 600, "atk": 88, "coins": (26, 46)}
        },
        "boss": {"name": "Hidra das Almas", "hp": 8500, "atk": 320, "xp": 6000, "level": 69, "coins": (900, 1600)},
        "resources": ["Lama mágica", "Essência pantanosa", "Pele de serpente ancestral", "Cogumelo sombrio", "Raiz corrompida"],
        "dungeons": [
            {"name": "Covil da Hidra Menor", "level": 22, "boss": "Hidra Jovem"},
            {"name": "Ruínas Submersas", "level": 23, "boss": "Guardião Submerso"},
            {"name": "Câmara das Almas Presas", "level": 24, "boss": "Necromante do Pântano"}
        ],
        "secret_dungeons": [
            {"name": "🌑 Coração do Pântano Eterno", "level": 22, "boss": "Entidade das Águas Negras", "secret": True,
             "special_boss_drop": "Ancestral", "key_name": "🗝️ Chave do Pântano Eterno"},
            {"name": "💀 Templo Afundado de Morthak", "level": 23, "boss": "Morthak, o Imortal Pantanoso", "secret": True,
             "special_boss_drop": "Ancestral", "key_name": "🗝️ Chave de Morthak"}
        ],
        "events": [
            "Bolhas negras sobem à superfície lamacenta.", "Você sente seus pés afundando na lama.",
            "Fogos-fátuos guiam você para um caminho perigoso.", "Um espírito perdido pede que você entregue uma mensagem.",
            "A lama parece ter consciência própria.", "Criaturas invisíveis se movem sob as águas escuras.",
            "Você encontra um barco afundado com tesouro dentro.", "O ar fétido envenena seus pulmões.",
            "Uma caravana de mortos-vivos marcha em silêncio.", "Raízes gigantes tentam te prender."
        ],
        "exclusive_drops": {
            "weapons": ["Cajado das Almas Perdidas", "Lâmina Pantanosa"],
            "armor": ["Manto das Almas", "Couraça do Pântano"]
        }
    },
    # ─── REINO 9: FLORESTA CRISTALINA (desbloqueado no nível 70) ───
    70: {
        "name": "💎 Floresta Cristalina",
        "emoji": "💎",
        "xp_loss_multiplier": 2.3,
        "monsters": {
            "Golem de Cristal": {"xp": (200, 250), "hp": 650, "atk": 92, "coins": (28, 50)},
            "Fada de Diamante": {"xp": (205, 255), "hp": 620, "atk": 90, "coins": (27, 48)},
            "Elemental Cristalino": {"xp": (210, 260), "hp": 670, "atk": 95, "coins": (29, 52)},
            "Dragão de Quartzo": {"xp": (220, 270), "hp": 700, "atk": 98, "coins": (31, 55)},
            "Guardião de Safira": {"xp": (215, 265), "hp": 680, "atk": 96, "coins": (30, 53)}
        },
        "boss": {"name": "Senhor dos Cristais", "hp": 12000, "atk": 380, "xp": 8000, "level": 79, "coins": (1100, 2000)},
        "resources": ["Cristal puro", "Fragmento de diamante", "Essência cristalina", "Pó de safira", "Núcleo de quartzo"],
        "dungeons": [
            {"name": "Caverna das Gemas Vivas", "level": 25, "boss": "Guardião das Gemas"},
            {"name": "Palácio de Diamante", "level": 26, "boss": "Rei Cristalino"},
            {"name": "Labirinto de Esmeralda", "level": 27, "boss": "Araña de Rubi"}
        ],
        "secret_dungeons": [
            {"name": "🌟 Núcleo Cristalino Primordial", "level": 25, "boss": "Entidade do Cristal Vivo", "secret": True,
             "special_boss_drop": "Ancestral", "key_name": "🗝️ Chave do Cristal Primordial"},
            {"name": "💠 Câmara do Diamante Negro", "level": 26, "boss": "Sombra Cristalizada", "secret": True,
             "special_boss_drop": "Mítico", "key_name": "🗝️ Chave do Diamante Negro"}
        ],
        "events": [
            "Árvores de cristal cantam com o vento.", "Seu reflexo se move sozinho nos cristais.",
            "Um cristal explode liberando energia pura.", "Você encontra uma floresta de estalactites coloridas.",
            "Luz se refrata criando arco-íris em todas as direções.", "Um elemental cristalino te oferece um fragmento.",
            "Você vê o futuro refletido em um cristal gigante.", "Cristais pulsam com batimentos cardíacos."
        ],
        "exclusive_drops": {
            "weapons": ["Espada de Diamante Negro", "Cajado Cristalino"],
            "armor": ["Armadura de Cristal Vivo", "Manto de Safira"]
        }
    },
    # ─── REINO 10: REINO DAS SOMBRAS ETERNAS (desbloqueado no nível 80) ───
    80: {
        "name": "🌑 Reino das Sombras Eternas",
        "emoji": "🌑",
        "xp_loss_multiplier": 2.5,
        "monsters": {
            "Sombra Viva": {"xp": (240, 290), "hp": 720, "atk": 105, "coins": (32, 58)},
            "Espectro Eterno": {"xp": (245, 295), "hp": 740, "atk": 108, "coins": (33, 60)},
            "Lich Ancestral": {"xp": (250, 300), "hp": 760, "atk": 112, "coins": (35, 63)},
            "Demônio das Trevas": {"xp": (255, 305), "hp": 780, "atk": 115, "coins": (36, 65)},
            "Senhor das Sombras Menor": {"xp": (260, 310), "hp": 800, "atk": 118, "coins": (38, 68)}
        },
        "boss": {"name": "Rei das Sombras Eternas", "hp": 16000, "atk": 450, "xp": 10000, "level": 89, "coins": (1400, 2500)},
        "resources": ["Essência das trevas", "Cristal da sombra", "Núcleo espectral", "Poeira negra", "Lágrima de espectro"],
        "dungeons": [
            {"name": "Torre do Vazio", "level": 28, "boss": "Arquimago das Trevas"},
            {"name": "Catacumba Eterna", "level": 29, "boss": "Lich Supremo"},
            {"name": "Portal das Sombras", "level": 30, "boss": "Guardião do Vazio"}
        ],
        "secret_dungeons": [
            {"name": "♾️ Coração das Trevas Infinitas", "level": 28, "boss": "Entidade Sem Forma", "secret": True,
             "special_boss_drop": "Ancestral", "key_name": "🗝️ Chave das Trevas Infinitas"},
            {"name": "💀 Trono do Lich Eterno", "level": 29, "boss": "Lich da Eternidade", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Lich Eterno"}
        ],
        "events": [
            "A escuridão aqui é diferente — ela te observa.", "Suas próprias sombras tentam te prender.",
            "Vozes dos mortos sussurram seus maiores medos.", "Luz não existe aqui — apenas graus de escuridão.",
            "Um portal para o vazio se abre brevemente.", "Espectros de aventureiros mortos vagam perdidos.",
            "Você sente sua essência sendo drenada.", "O tempo aqui se move de forma diferente."
        ],
        "exclusive_drops": {
            "weapons": ["Foice das Sombras Eternas", "Cajado do Vazio Profundo"],
            "armor": ["Manto da Escuridão Absoluta", "Armadura Espectral"]
        }
    },
    # ─── REINO 11: PLANÍCIES DO TROVÃO (desbloqueado no nível 90) ───
    90: {
        "name": "⚡ Planícies do Trovão",
        "emoji": "⚡",
        "xp_loss_multiplier": 2.7,
        "monsters": {
            "Elemental do Trovão": {"xp": (270, 320), "hp": 820, "atk": 122, "coins": (40, 70)},
            "Gigante da Tempestade": {"xp": (275, 325), "hp": 850, "atk": 125, "coins": (42, 73)},
            "Grifo da Relâmpago": {"xp": (280, 330), "hp": 870, "atk": 128, "coins": (43, 75)},
            "Titã do Vento": {"xp": (285, 335), "hp": 900, "atk": 132, "coins": (45, 78)},
            "Dragão do Trovão": {"xp": (290, 340), "hp": 920, "atk": 135, "coins": (46, 80)}
        },
        "boss": {"name": "Zeus Menor, o Trovejante", "hp": 20000, "atk": 520, "xp": 12000, "level": 99, "coins": (1700, 3000)},
        "resources": ["Essência do trovão", "Cristal elétrico", "Pena de grifo", "Núcleo da tempestade", "Relâmpago engarrafado"],
        "dungeons": [
            {"name": "Fortaleza da Tempestade", "level": 31, "boss": "Lorde da Tempestade"},
            {"name": "Caverna do Raio", "level": 32, "boss": "Elemental de Plasma"},
            {"name": "Pico do Trovão", "level": 33, "boss": "Grifo Ancião"}
        ],
        "secret_dungeons": [
            {"name": "⚡ Olho da Tempestade Eterna", "level": 31, "boss": "A Tempestade Consciente", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave da Tempestade Eterna"},
            {"name": "🌩️ Câmara do Primeiro Relâmpago", "level": 32, "boss": "Relâmpago Primordial Vivo", "secret": True,
             "special_boss_drop": "Ancestral", "key_name": "🗝️ Chave do Primeiro Relâmpago"}
        ],
        "events": [
            "Relâmpagos caem ao seu redor sem parar.", "O chão conduz eletricidade — cada passo doi.",
            "Uma tempestade eterna bloqueia a visão.", "Você vê figuras de trovão no céu.",
            "Grifos gigantes duelam acima de você.", "O ar cheira a ozônio e morte.",
            "Um raio atinge o chão perto de você criando uma cratera.", "Titãs da tempestade marcham ao longe."
        ],
        "exclusive_drops": {
            "weapons": ["Lança do Trovão Divino", "Martelo de Zeus"],
            "armor": ["Armadura da Tempestade", "Manto do Relâmpago"]
        }
    },
    # ─── REINO 12: TERRA DOS GIGANTES (desbloqueado no nível 100) ───
    100: {
        "name": "🗿 Terra dos Gigantes",
        "emoji": "🗿",
        "xp_loss_multiplier": 3.0,
        "monsters": {
            "Gigante de Pedra": {"xp": (300, 360), "hp": 1000, "atk": 145, "coins": (50, 88)},
            "Titã da Terra": {"xp": (310, 370), "hp": 1050, "atk": 150, "coins": (53, 92)},
            "Golias das Ruínas": {"xp": (320, 380), "hp": 1100, "atk": 155, "coins": (56, 96)},
            "Colosso Antigo": {"xp": (330, 390), "hp": 1150, "atk": 160, "coins": (58, 100)},
            "Gigante de Gelo e Fogo": {"xp": (340, 400), "hp": 1200, "atk": 165, "coins": (60, 105)}
        },
        "boss": {"name": "Primeiro Gigante Primordial", "hp": 25000, "atk": 600, "xp": 15000, "level": 109, "coins": (2000, 3500)},
        "resources": ["Osso de gigante", "Pedra colossal", "Couro de titã", "Essência primordial", "Cinza de colossus"],
        "dungeons": [
            {"name": "Fortaleza Colossal", "level": 34, "boss": "Guardião Colossus"},
            {"name": "Sepultura dos Gigantes", "level": 35, "boss": "Espírito Gigante"},
            {"name": "Palácio do Titã", "level": 36, "boss": "Titã Guerreiro"}
        ],
        "secret_dungeons": [
            {"name": "🗿 Coração da Terra Antiga", "level": 34, "boss": "Titã da Criação", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave da Terra Antiga"},
            {"name": "💀 Mausoléu do Primeiro Gigante", "level": 35, "boss": "Alma do Primeiro Gigante", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Primeiro Gigante"}
        ],
        "events": [
            "Pegadas do tamanho de lagos marcam o solo.", "Um gigante dorme e sua respiração causa ventos.",
            "Montanhas são na verdade gigantes adormecidos.", "Você é pequeno demais para ser notado.",
            "Uma batalha de gigantes sacode o chão.", "Os ossos dos gigantes caídos formam colinas.",
            "Um gigante jovem te confunde com um inseto.", "A terra treme com cada passo dos colossos."
        ],
        "exclusive_drops": {
            "weapons": ["Clava do Titã Primordial", "Lança Colossal"],
            "armor": ["Placas do Primeiro Gigante", "Couraça Colossal"]
        }
    },
    # ─── REINO 13: MAR DAS ALMAS (desbloqueado no nível 110) ───
    110: {
        "name": "🌊 Mar das Almas",
        "emoji": "🌊",
        "xp_loss_multiplier": 3.2,
        "monsters": {
            "Kraken Jovem": {"xp": (350, 420), "hp": 1250, "atk": 170, "coins": (62, 110)},
            "Sereia Maldita": {"xp": (355, 425), "hp": 1200, "atk": 168, "coins": (60, 108)},
            "Leviatã Menor": {"xp": (360, 430), "hp": 1300, "atk": 175, "coins": (65, 115)},
            "Fantasma Marinho": {"xp": (365, 435), "hp": 1250, "atk": 172, "coins": (63, 112)},
            "Guardião das Profundezas": {"xp": (370, 440), "hp": 1350, "atk": 178, "coins": (67, 118)}
        },
        "boss": {"name": "Leviatã das Almas", "hp": 30000, "atk": 680, "xp": 18000, "level": 119, "coins": (2300, 4000)},
        "resources": ["Escama de leviatã", "Pérola das profundezas", "Essência oceânica", "Coral mágico", "Água das almas"],
        "dungeons": [
            {"name": "Navio Fantasma", "level": 37, "boss": "Capitão Espectral"},
            {"name": "Templo Submerso", "level": 38, "boss": "Sacerdote do Mar"},
            {"name": "Abismo Oceânico", "level": 39, "boss": "Kraken Ancião"}
        ],
        "secret_dungeons": [
            {"name": "🌊 Coração do Oceano Eterno", "level": 37, "boss": "O Mar Consciente", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Oceano Eterno"},
            {"name": "🐙 Câmara do Leviatã Primordial", "level": 38, "boss": "Leviatã Primordial", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Leviatã Primordial"}
        ],
        "events": [
            "Ondas gigantescas surgem do nada.", "Você vê cidades afundadas nas profundezas.",
            "Sereias cantam tentando te hipnotizar.", "Um kraken emerge brevemente.",
            "O mar muda de cor para vermelho sangue.", "Almas de marinheiros mortos pedem ajuda.",
            "Um vórtice gigante se forma ao longe.", "Criaturas abissais sobem à superfície."
        ],
        "exclusive_drops": {
            "weapons": ["Tridente do Leviatã", "Lança das Profundezas"],
            "armor": ["Armadura das Almas Marinhas", "Manto do Oceano Eterno"]
        }
    },
    # ─── REINO 14: REINO DO CAOS (desbloqueado no nível 120) ───
    120: {
        "name": "🌀 Reino do Caos",
        "emoji": "🌀",
        "xp_loss_multiplier": 3.5,
        "monsters": {
            "Entidade do Caos": {"xp": (400, 480), "hp": 1400, "atk": 190, "coins": (70, 125)},
            "Fragmento de Realidade": {"xp": (410, 490), "hp": 1350, "atk": 185, "coins": (68, 122)},
            "Demônio do Vazio Caótico": {"xp": (420, 500), "hp": 1450, "atk": 195, "coins": (72, 128)},
            "Paradoxo Vivo": {"xp": (430, 510), "hp": 1500, "atk": 200, "coins": (75, 132)},
            "Contradição Manifesta": {"xp": (440, 520), "hp": 1550, "atk": 205, "coins": (78, 136)}
        },
        "boss": {"name": "O Caos em Pessoa", "hp": 38000, "atk": 780, "xp": 22000, "level": 129, "coins": (2800, 4800)},
        "resources": ["Essência caótica", "Fragmento de paradoxo", "Cristal do vazio caótico", "Pó dimensional", "Runa do caos"],
        "dungeons": [
            {"name": "Nexo Caótico", "level": 40, "boss": "Guardião do Nexo"},
            {"name": "Dimensão Fragmentada", "level": 41, "boss": "Entidade Fragmentada"},
            {"name": "Câmara do Paradoxo", "level": 42, "boss": "O Paradoxo Absoluto"}
        ],
        "secret_dungeons": [
            {"name": "🌀 Epicentro do Caos Primordial", "level": 40, "boss": "Caos Puro Manifestado", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Caos Primordial"},
            {"name": "♾️ Loop do Caos Eterno", "level": 41, "boss": "O Infinito Consciente", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Caos Eterno"}
        ],
        "events": [
            "A realidade se dobra ao seu redor.", "Você existe em dois lugares ao mesmo tempo.",
            "O passado e o futuro se misturam.", "Criaturas impossíveis vagam livres.",
            "Você vê sua própria morte — mas em outra linha temporal.", "A gravidade muda de direção.",
            "Cores impossíveis preenchem o horizonte.", "Tudo aqui viola as leis da física."
        ],
        "exclusive_drops": {
            "weapons": ["Lâmina do Caos Absoluto", "Cetro da Entropia"],
            "armor": ["Vestes do Caos Vivente", "Armadura do Paradoxo"]
        }
    },
    # ─── REINO 15: JARDIM DOS DEUSES (desbloqueado no nível 130) ───
    130: {
        "name": "🌸 Jardim dos Deuses",
        "emoji": "🌸",
        "xp_loss_multiplier": 3.8,
        "monsters": {
            "Guardião Divino Menor": {"xp": (460, 550), "hp": 1600, "atk": 215, "coins": (82, 145)},
            "Criatura do Paraíso": {"xp": (470, 560), "hp": 1650, "atk": 220, "coins": (85, 150)},
            "Anjo Renegado": {"xp": (480, 570), "hp": 1700, "atk": 225, "coins": (88, 155)},
            "Serafim Caído": {"xp": (490, 580), "hp": 1750, "atk": 230, "coins": (90, 160)},
            "Querubim Corrompido": {"xp": (500, 590), "hp": 1800, "atk": 235, "coins": (93, 165)}
        },
        "boss": {"name": "Jardineiro Divino", "hp": 46000, "atk": 880, "xp": 26000, "level": 139, "coins": (3300, 5600)},
        "resources": ["Pétala divina", "Semente celestial", "Néctar dos deuses", "Espinho sagrado", "Raiz do paraíso"],
        "dungeons": [
            {"name": "Labirinto do Paraíso", "level": 43, "boss": "Guardião do Labirinto"},
            {"name": "Templo da Deusa Floral", "level": 44, "boss": "Avatar da Deusa"},
            {"name": "Câmara das Sementes Proibidas", "level": 45, "boss": "Espírito da Natureza Divina"}
        ],
        "secret_dungeons": [
            {"name": "🌸 Câmara da Primeira Flor", "level": 43, "boss": "A Primeira Flor Consciente", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave da Primeira Flor"},
            {"name": "✨ Núcleo do Jardim Proibido", "level": 44, "boss": "Deus Jardineiro Oculto", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Jardim Proibido"}
        ],
        "events": [
            "Flores que cantam te rodeiam.", "Frutos proibidos brilham convidativamente.",
            "Anjos fazem rondas pelo jardim.", "Uma fonte de água da vida surge no caminho.",
            "O perfume de mil flores te envolve.", "Um deus menor passeia distraído.",
            "Árvores da vida crescem até o céu.", "Você sente paz absoluta — e perigo absoluto."
        ],
        "exclusive_drops": {
            "weapons": ["Espada da Primeira Flor", "Arco do Paraíso"],
            "armor": ["Vestes do Jardim Divino", "Armadura de Pétalas Sagradas"]
        }
    },
    # ─── REINO 16: REINO DO GELO ETERNO (desbloqueado no nível 140) ───
    140: {
        "name": "🧊 Reino do Gelo Eterno",
        "emoji": "🧊",
        "xp_loss_multiplier": 4.0,
        "monsters": {
            "Dragão de Gelo Ancião": {"xp": (520, 620), "hp": 1900, "atk": 248, "coins": (96, 170)},
            "Titã do Gelo": {"xp": (530, 630), "hp": 1950, "atk": 252, "coins": (98, 174)},
            "Colosso Glacial": {"xp": (540, 640), "hp": 2000, "atk": 256, "coins": (100, 178)},
            "Elemental do Gelo Eterno": {"xp": (550, 650), "hp": 2050, "atk": 260, "coins": (102, 182)},
            "Rainha das Banshees": {"xp": (560, 660), "hp": 2100, "atk": 265, "coins": (105, 186)}
        },
        "boss": {"name": "Imperadora do Gelo Eterno", "hp": 55000, "atk": 980, "xp": 30000, "level": 149, "coins": (3800, 6500)},
        "resources": ["Gelo eterno", "Cristal do frio absoluto", "Fragmento glacial divino", "Alma congelada", "Núcleo do inverno eterno"],
        "dungeons": [
            {"name": "Fortaleza do Gelo Eterno", "level": 46, "boss": "General Glacial"},
            {"name": "Câmara da Rainha das Neves", "level": 47, "boss": "Rainha das Neves"},
            {"name": "Núcleo do Inverno Absoluto", "level": 48, "boss": "Espírito do Inverno Eterno"}
        ],
        "secret_dungeons": [
            {"name": "🧊 Coração do Gelo Primordial", "level": 46, "boss": "Gelo Primordial Consciente", "secret": True,
             "special_boss_drop": "Divino", "key_name": "🗝️ Chave do Gelo Primordial"},
            {"name": "❄️ Câmara da Extinção Gelada", "level": 47, "boss": "O Frio Absoluto", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave da Extinção Gelada"}
        ],
        "events": [
            "O frio aqui congela os próprios pensamentos.", "Dragões de gelo dormem em torno de você.",
            "Tudo que você toca vira gelo.", "A temperatura é impossível para mortais suportarem.",
            "Cristais de gelo formam figuras de antigas batalhas.", "Você encontra heróis congelados no tempo.",
            "Uma tempestade de gelo absoluto surge.", "O reino inteiro parece respirar frio."
        ],
        "exclusive_drops": {
            "weapons": ["Lança do Gelo Eterno", "Espada da Extinção Glacial"],
            "armor": ["Armadura do Inverno Absoluto", "Vestes da Imperadora Glacial"]
        }
    },
    # ─── REINO 17: RUÍNAS DA CIVILIZAÇÃO PERDIDA (desbloqueado no nível 150) ───
    150: {
        "name": "🏛️ Ruínas da Civilização Perdida",
        "emoji": "🏛️",
        "xp_loss_multiplier": 4.3,
        "monsters": {
            "Guardião Autômato": {"xp": (580, 690), "hp": 2200, "atk": 275, "coins": (108, 192)},
            "Construto Arcano": {"xp": (590, 700), "hp": 2250, "atk": 280, "coins": (110, 196)},
            "Seninela Antiga": {"xp": (600, 710), "hp": 2300, "atk": 285, "coins": (112, 200)},
            "Arma Viva Abandonada": {"xp": (610, 720), "hp": 2350, "atk": 290, "coins": (115, 205)},
            "Espírito do Inventor": {"xp": (620, 730), "hp": 2400, "atk": 295, "coins": (118, 210)}
        },
        "boss": {"name": "Rei-Autômato da Civilização Perdida", "hp": 65000, "atk": 1100, "xp": 35000, "level": 159, "coins": (4400, 7500)},
        "resources": ["Engrenagem arcana", "Metal da era perdida", "Cristal de memória", "Runa esquecida", "Núcleo de construto"],
        "dungeons": [
            {"name": "Fábrica de Golens Arcanos", "level": 49, "boss": "Mestre Construtor"},
            {"name": "Biblioteca da Civilização Perdida", "level": 50, "boss": "Guardião do Conhecimento Perdido"},
            {"name": "Câmara do Último Rei", "level": 51, "boss": "Fantasma do Último Rei"}
        ],
        "secret_dungeons": [
            {"name": "🏛️ Coração da Civilização Proibida", "level": 49, "boss": "O Criador Esquecido", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave da Civilização Proibida"},
            {"name": "⚙️ Câmara da Arma Final", "level": 50, "boss": "A Arma que Destruiu Tudo", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave da Arma Final"}
        ],
        "events": [
            "Máquinas antigas ainda funcionam sem operadores.", "Hologramas de uma civilização florescente.",
            "Registros de uma civilização mais avançada que a atual.", "Autômatos te saúdam como se você fosse seu mestre.",
            "Você encontra a memória coletiva de uma civilização.", "Armas proibidas estão guardadas aqui.",
            "A tecnologia aqui é incompreensível para os atuais.", "Você lê profecias que já se realizaram."
        ],
        "exclusive_drops": {
            "weapons": ["Arma da Civilização Perdida", "Cajado do Último Mago"],
            "armor": ["Armadura do Rei-Autômato", "Vestes do Inventor Supremo"]
        }
    },
    # ─── REINO 18: PLANO ASTRAL (desbloqueado no nível 160) ───
    160: {
        "name": "✨ Plano Astral",
        "emoji": "✨",
        "xp_loss_multiplier": 4.6,
        "monsters": {
            "Ser Astral": {"xp": (650, 770), "hp": 2500, "atk": 310, "coins": (122, 218)},
            "Entidade Cósmica Menor": {"xp": (660, 780), "hp": 2550, "atk": 315, "coins": (125, 222)},
            "Guardião da Realidade": {"xp": (670, 790), "hp": 2600, "atk": 320, "coins": (128, 226)},
            "Viajante entre Mundos": {"xp": (680, 800), "hp": 2650, "atk": 325, "coins": (130, 230)},
            "Avatar Astral": {"xp": (690, 810), "hp": 2700, "atk": 330, "coins": (133, 235)}
        },
        "boss": {"name": "Senhor do Plano Astral", "hp": 78000, "atk": 1250, "xp": 42000, "level": 169, "coins": (5200, 9000)},
        "resources": ["Essência astral pura", "Cristal da consciência", "Fragmento cósmico", "Luz das estrelas mortas", "Núcleo astral"],
        "dungeons": [
            {"name": "Nexo das Consciências", "level": 52, "boss": "Mente Coletiva"},
            {"name": "Portal das Estrelas Mortas", "level": 53, "boss": "Guardião das Estrelas"},
            {"name": "Câmara da Existência", "level": 54, "boss": "Entidade da Existência"}
        ],
        "secret_dungeons": [
            {"name": "✨ Coração do Cosmos", "level": 52, "boss": "O Cosmos em Pessoa", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Coração do Cosmos"},
            {"name": "🌌 Câmara Além da Existência", "level": 53, "boss": "O Que Existe Além", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Além da Existência"}
        ],
        "events": [
            "Você flutua entre estrelas e galáxias.", "Seu corpo astral se separa do físico.",
            "Você vê todos os mundos simultaneamente.", "Entidades cósmicas conversam sobre você.",
            "O tempo não existe aqui — tudo é eterno.", "Você encontra sua própria alma.",
            "Galáxias nascem e morrem ao seu redor.", "O universo inteiro parece ser um ser vivo."
        ],
        "exclusive_drops": {
            "weapons": ["Espada do Cosmos", "Cajado da Consciência Universal"],
            "armor": ["Armadura do Plano Astral", "Vestes da Entidade Cósmica"]
        }
    },
    # ─── REINO 19: ALÉM DA EXISTÊNCIA (desbloqueado no nível 170) ───
    170: {
        "name": "🌌 Além da Existência",
        "emoji": "🌌",
        "xp_loss_multiplier": 5.0,
        "monsters": {
            "Conceito Vivo": {"xp": (720, 860), "hp": 2900, "atk": 350, "coins": (138, 248)},
            "Ideia Manifestada": {"xp": (730, 870), "hp": 2950, "atk": 355, "coins": (140, 252)},
            "Possibilidade Mortal": {"xp": (740, 880), "hp": 3000, "atk": 360, "coins": (142, 256)},
            "Destino em Forma": {"xp": (750, 890), "hp": 3050, "atk": 365, "coins": (145, 260)},
            "O Fim Personificado": {"xp": (760, 900), "hp": 3100, "atk": 370, "coins": (148, 265)}
        },
        "boss": {"name": "O Que Existe Além de Tudo", "hp": 95000, "atk": 1450, "xp": 52000, "level": 179, "coins": (6200, 10800)},
        "resources": ["Essência do nada", "Fragmento do além", "Cristal da não-existência", "Pó do antes do começo", "Núcleo da possibilidade"],
        "dungeons": [
            {"name": "Câmara do Nada Absoluto", "level": 55, "boss": "Guardião do Nada"},
            {"name": "Portal para o Além", "level": 56, "boss": "Aquele que Guarda a Porta"},
            {"name": "O Fim de Tudo", "level": 57, "boss": "A Morte em Pessoa"}
        ],
        "secret_dungeons": [
            {"name": "🌌 O Verdadeiro Fim", "level": 55, "boss": "A Última Coisa que Existe", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Verdadeiro Fim"},
            {"name": "♾️ Câmara do Começo e do Fim", "level": 56, "boss": "O Alpha e o Omega", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Alpha e Omega"}
        ],
        "events": [
            "Você existe mas não deveria.", "Suas memórias começam a desaparecer.",
            "O nada te chama pelo nome.", "Você vê o fim de todas as coisas.",
            "Conceitos se materializam e te atacam.", "A linguagem não consegue descrever o que você vê.",
            "Você encontra coisas que ainda não foram criadas.", "O próprio universo parece terminar aqui."
        ],
        "exclusive_drops": {
            "weapons": ["Espada do Além", "Cetro da Não-Existência"],
            "armor": ["Armadura do Nada Absoluto", "Vestes do Conceito de Poder"]
        }
    },
    # ─── REINO 20: O TRONO PRIMORDIAL (desbloqueado no nível 180) ───
    180: {
        "name": "⭐ O Trono Primordial",
        "emoji": "⭐",
        "xp_loss_multiplier": 6.0,
        "monsters": {
            "Guardião Primordial": {"xp": (800, 960), "hp": 3500, "atk": 420, "coins": (160, 285)},
            "Entidade Anterior à Criação": {"xp": (820, 980), "hp": 3600, "atk": 430, "coins": (165, 292)},
            "Ser do Antes do Tempo": {"xp": (840, 1000), "hp": 3700, "atk": 440, "coins": (170, 300)},
            "Conceito de Divindade": {"xp": (860, 1020), "hp": 3800, "atk": 450, "coins": (175, 308)},
            "A Própria Criação": {"xp": (880, 1040), "hp": 3900, "atk": 460, "coins": (180, 316)}
        },
        "boss": {"name": "O Criador Primordial", "hp": 150000, "atk": 2000, "xp": 80000, "level": 200, "coins": (10000, 18000)},
        "resources": ["Essência da criação", "Fragmento primordial puro", "Cristal do antes do começo", "Luz da primeira estrela", "Semente de universo"],
        "dungeons": [
            {"name": "Câmara do Primeiro Ser", "level": 58, "boss": "O Primeiro Ser"},
            {"name": "Trono da Criação", "level": 59, "boss": "Guardião do Trono"},
            {"name": "O Centro de Tudo", "level": 60, "boss": "A Fonte de Todo Poder"}
        ],
        "secret_dungeons": [
            {"name": "⭐ O Verdadeiro Trono Primordial", "level": 58, "boss": "O Criador Oculto", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Trono Primordial"},
            {"name": "🌌 Câmara do Criador Esquecido", "level": 59, "boss": "Aquele que Criou os Criadores", "secret": True,
             "special_boss_drop": "Primordial", "key_name": "🗝️ Chave do Criador Esquecido"}
        ],
        "events": [
            "Você está no centro de toda existência.", "O Criador te testa silenciosamente.",
            "Universos nascem ao seu redor como bolhas.", "Você ouve a voz que disse 'que haja luz'.",
            "Tudo que você tocou foi criado por uma vontade superior.", "O trono está vazio — esperando.",
            "Você vê o plano de toda a existência.", "A própria realidade te reverencia.",
            "Você encontra o sentido de tudo.", "Sua chegada aqui era esperada desde o início.",
            "O Criador sorri. Você chegou até aqui.", "A última aventura começa agora."
        ],
        "exclusive_drops": {
            "weapons": ["Espada do Criador Primordial", "O Cetro que Criou Tudo"],
            "armor": ["Armadura da Criação Absoluta", "Vestes do Guardião do Trono"]
        }
    }
}

# ================= ITENS EXPANDIDOS (com Divino e Primordial) =================
ITEMS = {
    "weapons": [
        # Comum
        {"name": "Espada Enferrujada", "rarity": "Comum", "atk": 5},
        {"name": "Adaga de Pedra", "rarity": "Comum", "atk": 6},
        {"name": "Cajado de Madeira", "rarity": "Comum", "atk": 5},
        {"name": "Machado Quebrado", "rarity": "Comum", "atk": 6},
        {"name": "Lança de Bambu", "rarity": "Comum", "atk": 5},
        {"name": "Faca Cega", "rarity": "Comum", "atk": 4},
        {"name": "Porrete de Madeira", "rarity": "Comum", "atk": 5},
        {"name": "Foice Velha", "rarity": "Comum", "atk": 6},
        # Incomum
        {"name": "Espada de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Machado de Batalha", "rarity": "Incomum", "atk": 14},
        {"name": "Arco Composto", "rarity": "Incomum", "atk": 13},
        {"name": "Martelo de Guerra", "rarity": "Incomum", "atk": 15},
        {"name": "Katana Básica", "rarity": "Incomum", "atk": 13},
        {"name": "Mangual de Ferro", "rarity": "Incomum", "atk": 14},
        {"name": "Espada Larga", "rarity": "Incomum", "atk": 13},
        {"name": "Lança de Ferro", "rarity": "Incomum", "atk": 12},
        {"name": "Claymore", "rarity": "Incomum", "atk": 15},
        {"name": "Arco Longo", "rarity": "Incomum", "atk": 14},
        {"name": "Alabarda", "rarity": "Incomum", "atk": 14},
        {"name": "Machado Duplo", "rarity": "Incomum", "atk": 15},
        # Raro
        {"name": "Espada de Madeira Negra", "rarity": "Raro", "atk": 25},
        {"name": "Lança Mística", "rarity": "Raro", "atk": 27},
        {"name": "Arco Élfico", "rarity": "Raro", "atk": 26},
        {"name": "Machado Rúnico", "rarity": "Raro", "atk": 28},
        {"name": "Cimitarra de Prata", "rarity": "Raro", "atk": 26},
        {"name": "Alabarda Encantada", "rarity": "Raro", "atk": 27},
        {"name": "Tridente de Aço", "rarity": "Raro", "atk": 25},
        {"name": "Katana Relâmpago", "rarity": "Raro", "atk": 28},
        {"name": "Arco das Sombras", "rarity": "Raro", "atk": 27},
        {"name": "Espada Lunar", "rarity": "Raro", "atk": 26},
        {"name": "Martelo Rúnico", "rarity": "Raro", "atk": 28},
        {"name": "Lança do Caçador", "rarity": "Raro", "atk": 27},
        {"name": "Foice Maldita", "rarity": "Raro", "atk": 26},
        {"name": "Adaga Venenosa", "rarity": "Raro", "atk": 25},
        {"name": "Clava Titânica", "rarity": "Raro", "atk": 28},
        # Épico
        {"name": "Lâmina Flamejante", "rarity": "Épico", "atk": 45},
        {"name": "Cajado Arcano", "rarity": "Épico", "atk": 48},
        {"name": "Espada do Vento", "rarity": "Épico", "atk": 46},
        {"name": "Machado Titânico", "rarity": "Épico", "atk": 50},
        {"name": "Arco das Estrelas", "rarity": "Épico", "atk": 47},
        {"name": "Lança do Dragão", "rarity": "Épico", "atk": 49},
        {"name": "Foice Sombria", "rarity": "Épico", "atk": 48},
        {"name": "Martelo do Trovão", "rarity": "Épico", "atk": 51},
        {"name": "Katana Demoníaca", "rarity": "Épico", "atk": 49},
        {"name": "Espada da Tempestade", "rarity": "Épico", "atk": 47},
        {"name": "Arco Celestial", "rarity": "Épico", "atk": 48},
        {"name": "Tridente de Poseidon", "rarity": "Épico", "atk": 50},
        {"name": "Lança da Fênix", "rarity": "Épico", "atk": 49},
        {"name": "Machado Infernal", "rarity": "Épico", "atk": 51},
        {"name": "Adaga da Morte", "rarity": "Épico", "atk": 46},
        {"name": "Espada do Eclipse", "rarity": "Épico", "atk": 48},
        {"name": "Cajado do Caos", "rarity": "Épico", "atk": 50},
        # Lendário
        {"name": "Excalibur", "rarity": "Lendário", "atk": 100},
        {"name": "Mjolnir", "rarity": "Lendário", "atk": 105},
        {"name": "Gungnir", "rarity": "Lendário", "atk": 103},
        {"name": "Kusanagi", "rarity": "Lendário", "atk": 102},
        {"name": "Durandal", "rarity": "Lendário", "atk": 104},
        {"name": "Gram", "rarity": "Lendário", "atk": 103},
        {"name": "Tyrfing", "rarity": "Lendário", "atk": 102},
        {"name": "Caladbolg", "rarity": "Lendário", "atk": 104},
        {"name": "Gáe Bolg", "rarity": "Lendário", "atk": 105},
        {"name": "Rhongomyniad", "rarity": "Lendário", "atk": 103},
        # Mítico
        {"name": "Espada do Criador", "rarity": "Mítico", "atk": 200},
        {"name": "Cetro da Eternidade", "rarity": "Mítico", "atk": 210},
        {"name": "Lâmina do Destino", "rarity": "Mítico", "atk": 205},
        {"name": "Arco do Apocalipse", "rarity": "Mítico", "atk": 208},
        # Ancestral
        {"name": "Espada dos Antepassados", "rarity": "Ancestral", "atk": 280},
        {"name": "Cajado do Primeiro Mago", "rarity": "Ancestral", "atk": 295},
        {"name": "Lança da Era Perdida", "rarity": "Ancestral", "atk": 285},
        {"name": "Arco dos Antigos Caçadores", "rarity": "Ancestral", "atk": 290},
        {"name": "Machado da Raça Extinta", "rarity": "Ancestral", "atk": 288},
        # Divino (NOVO)
        {"name": "Espada da Ascensão", "rarity": "Divino", "atk": 380},
        {"name": "Cajado da Criação Divina", "rarity": "Divino", "atk": 400},
        {"name": "Lança do Juízo Final", "rarity": "Divino", "atk": 390},
        {"name": "Arco da Extinção", "rarity": "Divino", "atk": 395},
        {"name": "Foice do Ceifador Divino", "rarity": "Divino", "atk": 385},
        # Primordial (NOVO)
        {"name": "Fragmento da Primeira Arma", "rarity": "Primordial", "atk": 750},
        {"name": "Vontade Feita Lâmina", "rarity": "Primordial", "atk": 800},
        {"name": "O Começo e o Fim", "rarity": "Primordial", "atk": 780},
        {"name": "Peso da Existência", "rarity": "Primordial", "atk": 760}
    ],
    "armor": [
        # Comum
        {"name": "Armadura de Couro", "rarity": "Comum", "def": 3},
        {"name": "Robes Simples", "rarity": "Comum", "def": 4},
        {"name": "Túnica de Linho", "rarity": "Comum", "def": 3},
        {"name": "Peitoral de Bronze", "rarity": "Comum", "def": 4},
        {"name": "Capa Rasgada", "rarity": "Comum", "def": 3},
        {"name": "Colete de Couro", "rarity": "Comum", "def": 4},
        {"name": "Vestes Gastas", "rarity": "Comum", "def": 3},
        {"name": "Armadura Rachada", "rarity": "Comum", "def": 4},
        # Incomum
        {"name": "Armadura de Ferro", "rarity": "Incomum", "def": 8},
        {"name": "Cota de Malha", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Escamas", "rarity": "Incomum", "def": 9},
        {"name": "Robes Reforçados", "rarity": "Incomum", "def": 8},
        {"name": "Brigandina", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Couro Batido", "rarity": "Incomum", "def": 9},
        {"name": "Peitoral de Aço", "rarity": "Incomum", "def": 10},
        {"name": "Armadura de Anéis", "rarity": "Incomum", "def": 9},
        {"name": "Vestes de Batalha", "rarity": "Incomum", "def": 8},
        {"name": "Couraça Leve", "rarity": "Incomum", "def": 9},
        {"name": "Armadura Laminada", "rarity": "Incomum", "def": 10},
        {"name": "Gibão de Armas", "rarity": "Incomum", "def": 9},
        # Raro
        {"name": "Armadura Mística", "rarity": "Raro", "def": 18},
        {"name": "Armadura Élfica", "rarity": "Raro", "def": 20},
        {"name": "Placas de Aço", "rarity": "Raro", "def": 19},
        {"name": "Armadura Rúnica", "rarity": "Raro", "def": 21},
        {"name": "Cota Encantada", "rarity": "Raro", "def": 19},
        {"name": "Armadura de Mithril", "rarity": "Raro", "def": 20},
        {"name": "Vestes Arcanas", "rarity": "Raro", "def": 18},
        {"name": "Armadura Lunar", "rarity": "Raro", "def": 20},
        {"name": "Placas Reforçadas", "rarity": "Raro", "def": 21},
        {"name": "Armadura Cristalina", "rarity": "Raro", "def": 19},
        {"name": "Vestes do Sábio", "rarity": "Raro", "def": 18},
        {"name": "Armadura do Cavaleiro", "rarity": "Raro", "def": 21},
        {"name": "Couraça Élfica", "rarity": "Raro", "def": 20},
        {"name": "Armadura Sombria", "rarity": "Raro", "def": 19},
        {"name": "Placas de Dragão", "rarity": "Raro", "def": 21},
        # Épico
        {"name": "Armadura Dracônica", "rarity": "Épico", "def": 35},
        {"name": "Armadura das Sombras", "rarity": "Épico", "def": 38},
        {"name": "Placas do Titã", "rarity": "Épico", "def": 37},
        {"name": "Armadura Flamejante", "rarity": "Épico", "def": 36},
        {"name": "Vestes Estelares", "rarity": "Épico", "def": 35},
        {"name": "Armadura do Vazio", "rarity": "Épico", "def": 39},
        {"name": "Couraça Angelical", "rarity": "Épico", "def": 38},
        {"name": "Armadura Demoníaca", "rarity": "Épico", "def": 40},
        {"name": "Placas do Dragão Negro", "rarity": "Épico", "def": 39},
        {"name": "Armadura da Tempestade", "rarity": "Épico", "def": 37},
        {"name": "Vestes do Arcano Maior", "rarity": "Épico", "def": 36},
        {"name": "Armadura de Obsidiana", "rarity": "Épico", "def": 38},
        {"name": "Placas Celestiais", "rarity": "Épico", "def": 40},
        {"name": "Armadura do Fênix", "rarity": "Épico", "def": 37},
        {"name": "Couraça Infernal", "rarity": "Épico", "def": 39},
        {"name": "Armadura do Eclipse", "rarity": "Épico", "def": 38},
        {"name": "Vestes do Caos", "rarity": "Épico", "def": 36},
        # Lendário
        {"name": "Armadura Celestial", "rarity": "Lendário", "def": 80},
        {"name": "Égide Divina", "rarity": "Lendário", "def": 85},
        {"name": "Armadura de Odin", "rarity": "Lendário", "def": 83},
        {"name": "Placas de Adaman", "rarity": "Lendário", "def": 82},
        {"name": "Vestes do Arcano Supremo", "rarity": "Lendário", "def": 84},
        {"name": "Armadura de Zeus", "rarity": "Lendário", "def": 85},
        {"name": "Placas de Poseidon", "rarity": "Lendário", "def": 83},
        {"name": "Armadura de Ares", "rarity": "Lendário", "def": 84},
        {"name": "Vestes de Atena", "rarity": "Lendário", "def": 82},
        {"name": "Couraça de Thor", "rarity": "Lendário", "def": 85},
        # Mítico
        {"name": "Armadura do Primeiro Deus", "rarity": "Mítico", "def": 180},
        {"name": "Vestes da Criação", "rarity": "Mítico", "def": 190},
        {"name": "Placas da Eternidade", "rarity": "Mítico", "def": 185},
        {"name": "Armadura do Destino", "rarity": "Mítico", "def": 188},
        # Ancestral
        {"name": "Armadura dos Guardiões Ancestrais", "rarity": "Ancestral", "def": 260},
        {"name": "Vestes do Elo Perdido", "rarity": "Ancestral", "def": 275},
        {"name": "Placas da Civilização Extinta", "rarity": "Ancestral", "def": 268},
        {"name": "Manto do Tempo Esquecido", "rarity": "Ancestral", "def": 272},
        # Divino (NOVO)
        {"name": "Manto da Ascensão", "rarity": "Divino", "def": 350},
        {"name": "Armadura do Serafim", "rarity": "Divino", "def": 370},
        {"name": "Vestes do Julgamento", "rarity": "Divino", "def": 360},
        {"name": "Placas do Arcanjo Supremo", "rarity": "Divino", "def": 365},
        # Primordial (NOVO)
        {"name": "Pele da Primeira Criatura", "rarity": "Primordial", "def": 700},
        {"name": "Armadura do Antes do Começo", "rarity": "Primordial", "def": 750},
        {"name": "Vestes do Silêncio Eterno", "rarity": "Primordial", "def": 720},
        {"name": "Proteção do Vazio Consciente", "rarity": "Primordial", "def": 730}
    ]
}

# ================= NOVOS EQUIPAMENTOS (EXPANSÃO — DOBRO) =================
ITEMS_EXTRA = {
    "weapons": [
        # Comum
        {"name": "Faca Lascada",          "rarity": "Comum",    "atk": 4},
        {"name": "Vara de Madeira",        "rarity": "Comum",    "atk": 5},
        {"name": "Pedra Afiada",           "rarity": "Comum",    "atk": 4},
        {"name": "Osso Endurecido",        "rarity": "Comum",    "atk": 5},
        {"name": "Garfo de Ferro Velho",   "rarity": "Comum",    "atk": 4},
        {"name": "Bordão Rachado",         "rarity": "Comum",    "atk": 5},
        {"name": "Espeto de Caçador",      "rarity": "Comum",    "atk": 6},
        {"name": "Clava de Pedra",         "rarity": "Comum",    "atk": 5},
        # Incomum
        {"name": "Espada de Cobre",        "rarity": "Incomum",  "atk": 12},
        {"name": "Arco Curto Élfico",      "rarity": "Incomum",  "atk": 13},
        {"name": "Lança de Bronze",        "rarity": "Incomum",  "atk": 12},
        {"name": "Bastão de Ferro",        "rarity": "Incomum",  "atk": 14},
        {"name": "Adaga de Ferro Dupla",   "rarity": "Incomum",  "atk": 13},
        {"name": "Machado Leve",           "rarity": "Incomum",  "atk": 13},
        {"name": "Florete de Aço",         "rarity": "Incomum",  "atk": 14},
        {"name": "Estrela de Arremesso",   "rarity": "Incomum",  "atk": 13},
        {"name": "Espada Curta de Ferro",  "rarity": "Incomum",  "atk": 12},
        {"name": "Bastão de Batalha",      "rarity": "Incomum",  "atk": 14},
        {"name": "Kunai de Ferro",         "rarity": "Incomum",  "atk": 13},
        {"name": "Maça de Ferro",          "rarity": "Incomum",  "atk": 14},
        # Raro
        {"name": "Katana de Vento",        "rarity": "Raro",     "atk": 26},
        {"name": "Arco de Osso de Dragão", "rarity": "Raro",     "atk": 27},
        {"name": "Espada das Marés",       "rarity": "Raro",     "atk": 25},
        {"name": "Lança do Trovejante",    "rarity": "Raro",     "atk": 28},
        {"name": "Machado das Trevas",     "rarity": "Raro",     "atk": 26},
        {"name": "Florete da Névoa",       "rarity": "Raro",     "atk": 27},
        {"name": "Cajado das Raízes",      "rarity": "Raro",     "atk": 25},
        {"name": "Alabarda do Caçador",    "rarity": "Raro",     "atk": 28},
        {"name": "Espada de Cristal",      "rarity": "Raro",     "atk": 26},
        {"name": "Tridente Sombrio",       "rarity": "Raro",     "atk": 27},
        {"name": "Adaga do Espectro",      "rarity": "Raro",     "atk": 25},
        {"name": "Mangual Rúnico",         "rarity": "Raro",     "atk": 28},
        {"name": "Lança de Coral",         "rarity": "Raro",     "atk": 26},
        {"name": "Cimitarra Lunar",        "rarity": "Raro",     "atk": 27},
        {"name": "Machado da Lua",         "rarity": "Raro",     "atk": 26},
        # Épico
        {"name": "Espada do Caos Menor",   "rarity": "Épico",    "atk": 46},
        {"name": "Lança do Dilúvio",       "rarity": "Épico",    "atk": 48},
        {"name": "Arco do Crepúsculo",     "rarity": "Épico",    "atk": 47},
        {"name": "Machado do Abismo",      "rarity": "Épico",    "atk": 50},
        {"name": "Cajado da Tempestade",   "rarity": "Épico",    "atk": 49},
        {"name": "Foice do Pesadelo",      "rarity": "Épico",    "atk": 48},
        {"name": "Florete do Vazio",       "rarity": "Épico",    "atk": 46},
        {"name": "Tridente Celestial",     "rarity": "Épico",    "atk": 49},
        {"name": "Espada da Aurora",       "rarity": "Épico",    "atk": 47},
        {"name": "Alabarda Demoníaca",     "rarity": "Épico",    "atk": 50},
        {"name": "Katana das Estrelas",    "rarity": "Épico",    "atk": 48},
        {"name": "Lança do Dragão Negro",  "rarity": "Épico",    "atk": 51},
        {"name": "Arco do Destino",        "rarity": "Épico",    "atk": 47},
        {"name": "Machado do Titã Sombrio","rarity": "Épico",    "atk": 50},
        {"name": "Cajado do Necromante",   "rarity": "Épico",    "atk": 49},
        {"name": "Adaga Gêmea das Sombras","rarity": "Épico",    "atk": 48},
        {"name": "Espada do Crepúsculo",   "rarity": "Épico",    "atk": 46},
        # Lendário
        {"name": "Fragarach",              "rarity": "Lendário", "atk": 101},
        {"name": "Hauteclaire",            "rarity": "Lendário", "atk": 103},
        {"name": "Joyeuse",                "rarity": "Lendário", "atk": 102},
        {"name": "Skofnung",               "rarity": "Lendário", "atk": 104},
        {"name": "Curtana",                "rarity": "Lendário", "atk": 101},
        {"name": "Claiomh Solais",         "rarity": "Lendário", "atk": 105},
        {"name": "Harpe",                  "rarity": "Lendário", "atk": 102},
        {"name": "Shamshir-e Zomorrodnegar","rarity":"Lendário", "atk": 103},
        {"name": "Dáinsleif",              "rarity": "Lendário", "atk": 104},
        {"name": "Chandrahas",             "rarity": "Lendário", "atk": 102},
        # Mítico
        {"name": "Lâmina do Caos Absoluto","rarity": "Mítico",   "atk": 205},
        {"name": "Foice da Eternidade",    "rarity": "Mítico",   "atk": 215},
        {"name": "Espada do Juízo",        "rarity": "Mítico",   "atk": 208},
        {"name": "Martelo dos Deuses",     "rarity": "Mítico",   "atk": 212},
        # Ancestral
        {"name": "Lança da Aurora Primeva","rarity": "Ancestral","atk": 285},
        {"name": "Espada do Primeiro Rei", "rarity": "Ancestral","atk": 292},
        {"name": "Cajado do Cosmos Antigo","rarity": "Ancestral","atk": 288},
        {"name": "Arco dos Profetas Extintos","rarity":"Ancestral","atk":291},
        {"name": "Machado do Titã Primordial","rarity":"Ancestral","atk":286},
        # Divino
        {"name": "Lança da Redenção Divina","rarity": "Divino",  "atk": 388},
        {"name": "Espada do Sol Negro",    "rarity": "Divino",   "atk": 395},
        {"name": "Cajado da Aniquilação",  "rarity": "Divino",   "atk": 392},
        {"name": "Foice do Arcanjo Caído", "rarity": "Divino",   "atk": 385},
        {"name": "Tridente do Poseidon Divino","rarity":"Divino","atk": 398},
        # Primordial
        {"name": "Silêncio Feito Arma",    "rarity": "Primordial","atk": 755},
        {"name": "A Última Vontade",       "rarity": "Primordial","atk": 810},
        {"name": "Ecos do Não-Ser",        "rarity": "Primordial","atk": 775},
        {"name": "Raiz da Criação",        "rarity": "Primordial","atk": 790},
    ],
    "armor": [
        # Comum
        {"name": "Tapa de Couro",          "rarity": "Comum",    "def": 3},
        {"name": "Vestes de Palha",        "rarity": "Comum",    "def": 4},
        {"name": "Escudo de Madeira Leve", "rarity": "Comum",    "def": 3},
        {"name": "Manto Rasgado",          "rarity": "Comum",    "def": 4},
        {"name": "Colete de Osso",         "rarity": "Comum",    "def": 3},
        {"name": "Vestes do Aldeão",       "rarity": "Comum",    "def": 4},
        {"name": "Peitoral de Madeira",    "rarity": "Comum",    "def": 3},
        {"name": "Gibão Velho",            "rarity": "Comum",    "def": 4},
        # Incomum
        {"name": "Armadura de Bronze",     "rarity": "Incomum",  "def": 8},
        {"name": "Vestes de Couro Duplo",  "rarity": "Incomum",  "def": 9},
        {"name": "Peitoral de Madeira Reforçada","rarity":"Incomum","def":8},
        {"name": "Armadura de Escamas de Peixe","rarity":"Incomum","def":9},
        {"name": "Capa Encantada",         "rarity": "Incomum",  "def": 10},
        {"name": "Vestes do Monge",        "rarity": "Incomum",  "def": 9},
        {"name": "Armadura de Placas Leve","rarity": "Incomum",  "def": 10},
        {"name": "Manto de Viagem",        "rarity": "Incomum",  "def": 8},
        {"name": "Colete Reforçado",       "rarity": "Incomum",  "def": 9},
        {"name": "Armadura de Tiras",      "rarity": "Incomum",  "def": 10},
        {"name": "Casaco de Ferro",        "rarity": "Incomum",  "def": 9},
        {"name": "Vestes de Batalha Leve", "rarity": "Incomum",  "def": 8},
        # Raro
        {"name": "Armadura de Mithril Leve","rarity":"Raro",     "def": 19},
        {"name": "Placas do Druida",       "rarity": "Raro",     "def": 20},
        {"name": "Vestes do Necromante",   "rarity": "Raro",     "def": 18},
        {"name": "Couraça das Florestas",  "rarity": "Raro",     "def": 21},
        {"name": "Armadura do Mercenário", "rarity": "Raro",     "def": 19},
        {"name": "Manto das Estrelas",     "rarity": "Raro",     "def": 20},
        {"name": "Vestes do Paladino",     "rarity": "Raro",     "def": 18},
        {"name": "Armadura Vulcânica",     "rarity": "Raro",     "def": 21},
        {"name": "Peitoral do Cavaleiro Negro","rarity":"Raro",  "def": 20},
        {"name": "Cota de Malha Rúnica",   "rarity": "Raro",     "def": 21},
        {"name": "Vestes do Arauto",       "rarity": "Raro",     "def": 19},
        {"name": "Armadura das Marés",     "rarity": "Raro",     "def": 20},
        {"name": "Placas do Druida Solar", "rarity": "Raro",     "def": 21},
        {"name": "Manto das Ruínas",       "rarity": "Raro",     "def": 19},
        {"name": "Armadura do Caçador",    "rarity": "Raro",     "def": 20},
        # Épico
        {"name": "Armadura do Pântano",    "rarity": "Épico",    "def": 36},
        {"name": "Vestes do Arcanista",    "rarity": "Épico",    "def": 38},
        {"name": "Placas do Leviathan",    "rarity": "Épico",    "def": 37},
        {"name": "Armadura do Trovão",     "rarity": "Épico",    "def": 39},
        {"name": "Manto da Penumbra",      "rarity": "Épico",    "def": 35},
        {"name": "Couraça de Obsidiana Polida","rarity":"Épico", "def": 38},
        {"name": "Armadura das Profundezas","rarity":"Épico",    "def": 40},
        {"name": "Vestes do Vazio Menor",  "rarity": "Épico",    "def": 36},
        {"name": "Placas do Guerreiro Eterno","rarity":"Épico",  "def": 39},
        {"name": "Armadura do Berserker",  "rarity": "Épico",    "def": 37},
        {"name": "Manto da Ascensão Menor","rarity": "Épico",    "def": 38},
        {"name": "Couraça de Dragão Menor","rarity": "Épico",    "def": 40},
        {"name": "Armadura do Espectro",   "rarity": "Épico",    "def": 36},
        {"name": "Placas do Caos",         "rarity": "Épico",    "def": 37},
        {"name": "Vestes do Feiticeiro",   "rarity": "Épico",    "def": 35},
        {"name": "Armadura do Inquisidor", "rarity": "Épico",    "def": 39},
        # Lendário
        {"name": "Armadura de Odim",       "rarity": "Lendário", "def": 83},
        {"name": "Vestes de Hécate",       "rarity": "Lendário", "def": 84},
        {"name": "Placas do Guardião Eterno","rarity":"Lendário","def": 85},
        {"name": "Égide do Herói Lendário","rarity": "Lendário", "def": 82},
        {"name": "Armadura do Semideus",   "rarity": "Lendário", "def": 84},
        {"name": "Vestes do Dragão Sagrado","rarity":"Lendário", "def": 85},
        {"name": "Couraça do Arcanjo",     "rarity": "Lendário", "def": 83},
        {"name": "Armadura da Eternidade", "rarity": "Lendário", "def": 84},
        {"name": "Placas do Caçador Divino","rarity":"Lendário", "def": 82},
        {"name": "Manto do Profeta",       "rarity": "Lendário", "def": 85},
        # Mítico
        {"name": "Armadura do Ser Primevo","rarity": "Mítico",   "def": 185},
        {"name": "Vestes do Cosmos",       "rarity": "Mítico",   "def": 192},
        {"name": "Placas do Abismo Final", "rarity": "Mítico",   "def": 188},
        {"name": "Couraça da Criação",     "rarity": "Mítico",   "def": 191},
        # Ancestral
        {"name": "Vestes do Tempo Esquecido","rarity":"Ancestral","def":270},
        {"name": "Armadura dos Primeiros Heróis","rarity":"Ancestral","def":278},
        {"name": "Placas da Era das Lendas","rarity":"Ancestral","def":265},
        {"name": "Manto do Arauto Perdido","rarity": "Ancestral","def": 273},
        {"name": "Couraça dos Antepassados","rarity":"Ancestral","def":268},
        # Divino
        {"name": "Armadura do Serafim Caído","rarity":"Divino",  "def": 355},
        {"name": "Vestes do Julgamento Final","rarity":"Divino", "def": 368},
        {"name": "Placas da Divindade Menor","rarity":"Divino",  "def": 362},
        {"name": "Manto da Criação Divina","rarity": "Divino",   "def": 358},
        {"name": "Couraça do Arcanjo Supremo","rarity":"Divino", "def": 372},
        # Primordial
        {"name": "Essência do Antes do Tempo","rarity":"Primordial","def":710},
        {"name": "Armadura do Último Deus","rarity": "Primordial","def":755},
        {"name": "Manto do Vazio Absoluto","rarity": "Primordial","def":730},
        {"name": "Vestes da Não-Existência","rarity":"Primordial","def":740},
    ]
}

# Mescla ITEMS_EXTRA no ITEMS para que todo o sistema use automaticamente
ITEMS["weapons"].extend(ITEMS_EXTRA["weapons"])
ITEMS["armor"].extend(ITEMS_EXTRA["armor"])
STRUCTURES = [
    {
        "name": "🏛️ Cidade Mercante",
        "description": "Uma cidade movimentada onde comerciantes de todos os reinos se reúnem.",
        "narrator": "As ruas estão repletas de mercadores gritando seus produtos...",
        "worlds": [1, 10, 20, 30]
    },
    {
        "name": "⛪ Templo Abandonado",
        "description": "Um templo antigo que guarda segredos esquecidos.",
        "narrator": "O ar aqui é pesado... Algo sagrado já habitou este lugar.",
        "worlds": [10, 20, 30, 40]
    },
    {
        "name": "🏰 Fortaleza em Ruínas",
        "description": "Restos de uma fortaleza que já foi gloriosa.",
        "narrator": "Ecos de batalhas antigas ainda reverberam entre as pedras...",
        "worlds": [20, 30, 40, 50]
    },
    {
        "name": "🌉 Ponte Mística",
        "description": "Uma ponte que conecta dimensões.",
        "narrator": "Você sente a realidade se distorcendo ao cruzar...",
        "worlds": [40, 50, 60]
    },
    {
        "name": "🗿 Monumento dos Heróis",
        "description": "Estátuas de heróis lendários do passado.",
        "narrator": "Seus feitos estão gravados em pedra eterna...",
        "worlds": [30, 40, 50, 60]
    }
]

# ================= FALAS DO NARRADOR =================
NARRATOR_WARNINGS = [
    "Logo ele enfrentará seu maior pesadelo...",
    "O destino está prestes a testar sua verdadeira força...",
    "Algo terrível se aproxima nas sombras...",
    "Os dados do destino estão prestes a rolar...",
    "Uma presença maligna observa cada passo seu...",
    "A morte espreita além do próximo horizonte...",
    "Seu nome será lembrado... ou esquecido para sempre.",
    "As estrelas tremem com o que está por vir...",
    "Nem todos os heróis sobrevivem às suas jornadas...",
    "O fim de uma era se aproxima..."
]

# ================= SISTEMA DE SORTE =================
LUCK_SYSTEM = {
    1: {"emoji": "💀", "name": "Azar extremo"},
    2: {"emoji": "☠️", "name": "Muito azar"},
    3: {"emoji": "😵", "name": "Azar"},
    4: {"emoji": "😐", "name": "Ruim"},
    5: {"emoji": "😶", "name": "Neutro"},
    6: {"emoji": "🙂", "name": "Bom"},
    7: {"emoji": "😄", "name": "Sorte"},
    8: {"emoji": "🍀", "name": "Muita sorte"},
    9: {"emoji": "✨", "name": "Sorte extrema"},
    10: {"emoji": "🌟", "name": "Lenda"}
}

# ================= BANCO DE DADOS =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        hp INTEGER DEFAULT 100,
        max_hp INTEGER DEFAULT 100,
        coins INTEGER DEFAULT 0,
        inventory TEXT DEFAULT '[]',
        weapon TEXT DEFAULT NULL,
        armor TEXT DEFAULT NULL,
        worlds TEXT DEFAULT '[1]',
        bosses TEXT DEFAULT '[]',
        class TEXT DEFAULT NULL,
        pet TEXT DEFAULT NULL,
        guild_id INTEGER DEFAULT NULL,
        active_effects TEXT DEFAULT '{}',
        active_quest TEXT DEFAULT NULL,
        completed_quests TEXT DEFAULT '[]',
        mana INTEGER DEFAULT 50,
        max_mana INTEGER DEFAULT 50,
        pvp_battles TEXT DEFAULT '{}',
        alignment_points INTEGER DEFAULT 0,
        pet_farm TEXT DEFAULT '[]',
        discovered_map TEXT DEFAULT '{}'
    )''')

    # Migração segura de colunas novas
    for col_def in [
        "ALTER TABLE players ADD COLUMN mana INTEGER DEFAULT 50",
        "ALTER TABLE players ADD COLUMN max_mana INTEGER DEFAULT 50",
        "ALTER TABLE players ADD COLUMN pvp_battles TEXT DEFAULT '{}'",
        "ALTER TABLE players ADD COLUMN alignment_points INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN pet_farm TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN mana_category TEXT DEFAULT 'none'",
        "ALTER TABLE players ADD COLUMN spell_book_unlocked INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN afk_farming INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN afk_start INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN kingdom_data TEXT DEFAULT 'null'",
        "ALTER TABLE players ADD COLUMN pets_list TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN discovered_map TEXT DEFAULT '{}'",
        "ALTER TABLE players ADD COLUMN job TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN job_since INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN city_title TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN knights TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN last_work INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN last_defend INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN achievements TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN training_points INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN temp_atk_boost INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN temp_def_boost INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN temp_hp_boost INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN level_boss_attempts TEXT DEFAULT '{}'",
        "ALTER TABLE players ADD COLUMN monsters_killed INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN bosses_defeated INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN total_coins_earned INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN total_xp_earned INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN areas_explored INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN dungeons_completed INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN race TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN specialization TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN class_tier INTEGER DEFAULT 0",
        "ALTER TABLE players ADD COLUMN supreme_skills TEXT DEFAULT '[]'",
        "ALTER TABLE players ADD COLUMN mount TEXT DEFAULT NULL",
        "ALTER TABLE players ADD COLUMN race_stage INTEGER DEFAULT 0",
    ]:
        try:
            c.execute(col_def)
        except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS pvp_battles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenger_id TEXT,
        target_id TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS coin_exchange_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        csi_coins INTEGER,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS guilds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        total_xp INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS trade_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user TEXT,
        to_user TEXT,
        from_items TEXT,
        to_items TEXT,
        status TEXT DEFAULT 'pending',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS team_quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quest_id TEXT,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        status TEXT DEFAULT 'recruiting',
        progress INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS boss_battles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boss_name TEXT,
        leader_id TEXT,
        members TEXT DEFAULT '[]',
        world_level INTEGER,
        status TEXT DEFAULT 'recruiting',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_player_db(user_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (str(user_id),))
    result = c.fetchone()
    conn.close()

    if result:
        r = dict(result)
        return {
            "level": r.get("level", 1),
            "xp": r.get("xp", 0),
            "hp": r.get("hp", 100),
            "max_hp": r.get("max_hp", 100),
            "coins": r.get("coins", 0),
            "inventory": json.loads(r["inventory"]) if r.get("inventory") else [],
            "weapon": r.get("weapon"),
            "armor": r.get("armor"),
            "worlds": json.loads(r["worlds"]) if r.get("worlds") else [1],
            "bosses": json.loads(r["bosses"]) if r.get("bosses") else [],
            "class": r.get("class"),
            "pet": r.get("pet"),
            "guild_id": r.get("guild_id"),
            "active_effects": json.loads(r["active_effects"]) if r.get("active_effects") else {},
            "active_quest": json.loads(r["active_quest"]) if r.get("active_quest") else None,
            "completed_quests": json.loads(r["completed_quests"]) if r.get("completed_quests") else [],
            "mana": r.get("mana", 50),
            "max_mana": r.get("max_mana", 50),
            "pvp_battles": json.loads(r["pvp_battles"]) if r.get("pvp_battles") else {},
            "alignment_points": r.get("alignment_points", 0),
            "pet_farm": json.loads(r["pet_farm"]) if r.get("pet_farm") else [],
            "discovered_map": json.loads(r["discovered_map"]) if r.get("discovered_map") else {},
            "job": r.get("job"),
            "job_since": r.get("job_since", 0),
            "city_title": r.get("city_title"),
            "knights": json.loads(r["knights"]) if r.get("knights") else [],
            "last_work": r.get("last_work", 0),
            "last_defend": r.get("last_defend", 0),
            "achievements": json.loads(r["achievements"]) if r.get("achievements") else [],
            "training_points": r.get("training_points", 0),
            "temp_atk_boost": r.get("temp_atk_boost", 0),
            "temp_def_boost": r.get("temp_def_boost", 0),
            "temp_hp_boost": r.get("temp_hp_boost", 0),
            "level_boss_attempts": json.loads(r["level_boss_attempts"]) if r.get("level_boss_attempts") else {},
            "monsters_killed": r.get("monsters_killed", 0),
            "bosses_defeated": r.get("bosses_defeated", 0),
            "total_coins_earned": r.get("total_coins_earned", 0),
            "total_xp_earned": r.get("total_xp_earned", 0),
            "areas_explored": r.get("areas_explored", 0),
            "dungeons_completed": r.get("dungeons_completed", 0),
            "mana_category": r.get("mana_category", "none"),
            "spell_book_unlocked": r.get("spell_book_unlocked", 0),
            "afk_farming": r.get("afk_farming", 0),
            "afk_start": r.get("afk_start", 0),
            "kingdom_data": json.loads(r["kingdom_data"]) if r.get("kingdom_data") and r["kingdom_data"] != "null" else None,
            "pets_list": json.loads(r["pets_list"]) if r.get("pets_list") else [],
            "race": r.get("race"),
            "specialization": r.get("specialization"),
            "class_tier": r.get("class_tier", 0),
            "supreme_skills": json.loads(r["supreme_skills"]) if r.get("supreme_skills") else [],
            "race_stage": r.get("race_stage", 0),
            "mount": r.get("mount"),
        }
    return None

def save_player_db(user_id, player):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''INSERT OR REPLACE INTO players
                 (user_id, level, xp, hp, max_hp, coins, inventory, weapon, armor,
                  worlds, bosses, class, pet, guild_id, active_effects, active_quest, completed_quests,
                  mana, max_mana, pvp_battles, alignment_points, pet_farm, discovered_map,
                  job, job_since, city_title, knights, last_work, last_defend,
                  achievements, training_points, temp_atk_boost, temp_def_boost, temp_hp_boost,
                  level_boss_attempts, monsters_killed, bosses_defeated, total_coins_earned,
                  total_xp_earned, areas_explored, dungeons_completed, mana_category, spell_book_unlocked,
                  afk_farming, afk_start, kingdom_data, pets_list,
                  race, specialization, class_tier, supreme_skills, race_stage, mount)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(user_id), player["level"], player["xp"], player["hp"], player["max_hp"],
               player["coins"], json.dumps(player["inventory"]), player["weapon"], player["armor"],
               json.dumps(player["worlds"]), json.dumps(player["bosses"]), player.get("class"),
               player.get("pet"), player.get("guild_id"),
               json.dumps(player.get("active_effects", {})),
               json.dumps(player.get("active_quest")) if player.get("active_quest") else None,
               json.dumps(player.get("completed_quests", [])),
               player.get("mana", 50), player.get("max_mana", 50),
               json.dumps(player.get("pvp_battles", {})),
               player.get("alignment_points", 0),
               json.dumps(player.get("pet_farm", [])),
               json.dumps(player.get("discovered_map", {})),
               player.get("job"), player.get("job_since", 0),
               player.get("city_title"),
               json.dumps(player.get("knights", [])),
               player.get("last_work", 0), player.get("last_defend", 0),
               json.dumps(player.get("achievements", [])),
               player.get("training_points", 0),
               player.get("temp_atk_boost", 0),
               player.get("temp_def_boost", 0),
               player.get("temp_hp_boost", 0),
               json.dumps(player.get("level_boss_attempts", {})),
               player.get("monsters_killed", 0),
               player.get("bosses_defeated", 0),
               player.get("total_coins_earned", 0),
               player.get("total_xp_earned", 0),
               player.get("areas_explored", 0),
               player.get("dungeons_completed", 0),
               player.get("mana_category", "none"),
               player.get("spell_book_unlocked", 0),
               player.get("afk_farming", 0),
               player.get("afk_start", 0),
               json.dumps(player.get("kingdom_data")) if player.get("kingdom_data") else None,
               json.dumps(player.get("pets_list", [])),
               player.get("race"),
               player.get("specialization"),
               player.get("class_tier", 0),
               json.dumps(player.get("supreme_skills", [])),
               player.get("race_stage", 0),
               player.get("mount")))

    conn.commit()
    conn.close()


# ================= CONQUISTAS =================

async def check_achievements(channel, user_id, trigger_special=None):
    """Verifica e concede conquistas desbloqueadas ao jogador."""
    player = get_player(user_id)
    if not player:
        return
    earned = player.get("achievements", [])
    new_earned = []

    for ach in ACHIEVEMENTS:
        if ach["id"] in earned:
            continue  # Já tem
        unlocked = False

        if "stat" in ach:
            val = player.get(ach["stat"], 0)
            if val >= ach["threshold"]:
                unlocked = True

        if "special" in ach and trigger_special == ach["special"]:
            unlocked = True

        if unlocked:
            new_earned.append(ach)
            earned.append(ach["id"])

    if new_earned:
        player["achievements"] = earned
        total_xp = sum(a["xp"] for a in new_earned)
        save_player_db(user_id, player)
        add_xp(user_id, total_xp)

        for ach in new_earned:
            is_secret = ach["cat"] == "🔮 Secreta"
            secret_note = "\n🔮 *Uma conquista secreta foi revelada!*" if is_secret else ""
            embed = discord.Embed(
                title="🏆 CONQUISTA DESBLOQUEADA!",
                description=f"*'O narrador anuncia com voz trovejante!'*{secret_note}",
                color=discord.Color.gold()
            )
            embed.add_field(name=f"{ach['cat']} — {ach['name']}", value=f"_{ach['desc']}_\n\n⭐ **+{ach['xp']:,} XP** de recompensa!", inline=False)
            embed.set_footer(text=f"Conquistas desbloqueadas: {len(earned)}/{len(ACHIEVEMENTS)}")
            await channel.send(embed=embed)


# ================= FUNÇÕES BASE =================

def roll_dice():
    return random.randint(1, 10)

def roll_with_bonus(player):
    """Rola dado com bônus de raridade de itens e classe"""
    roll = roll_dice()
    item_bonus = get_item_dice_bonus(player)
    if player.get("class") == "Bardo":
        roll = min(10, roll + 1)
    roll = min(10, roll + item_bonus)
    return roll

def get_luck(roll):
    return LUCK_SYSTEM.get(roll, LUCK_SYSTEM[5])

def calc_xp(level):
    return (level ** 2) * 20

def get_world(level, player=None):
    """Retorna o mundo atual do jogador. Se player fornecido, respeita travas de boss."""
    if player:
        # Mundos desbloqueados = apenas os que estão na lista player["worlds"]
        available = sorted([k for k in WORLDS.keys() if k in player["worlds"]], reverse=True)
    else:
        levels = sorted([k for k in WORLDS.keys() if k <= level], reverse=True)
        available = levels
    return WORLDS[available[0]] if available else WORLDS[1]

def create_player(user_id):
    player = {
        "level": 1,
        "xp": 0,
        "hp": 100,
        "max_hp": 100,
        "coins": 0,
        "inventory": [],
        "weapon": None,
        "armor": None,
        "worlds": [1],
        "bosses": [],
        "class": None,
        "pet": None,
        "guild_id": None,
        "active_effects": {},
        "active_quest": None,
        "completed_quests": [],
        "mana": 50,
        "max_mana": 50,
        "pvp_battles": {},
        "alignment_points": 0,
        "pet_farm": [],
        "mana_category": "none",
        "spell_book_unlocked": 0,
        "afk_farming": 0,
        "afk_start": 0,
        "kingdom_data": None,
        "pets_list": [],
        "discovered_map": {},
        "job": None,
        "job_since": 0,
        "city_title": None,
        "knights": [],
        "last_work": 0,
        "last_defend": 0,
    }
    save_player_db(user_id, player)
    return player

def get_player(user_id):
    player = get_player_db(user_id)
    if not player:
        player = create_player(user_id)
    return player

def calc_max_mana(player):
    """Calcula mana máxima baseada na classe e nível"""
    cls = player.get("class")
    if not cls or cls not in CLASS_MANA:
        return 50 + player["level"] * 2
    base = CLASS_MANA[cls]["base_mana"]
    per_level = CLASS_MANA[cls]["mana_per_level"]
    return base + (player["level"] - 1) * per_level

def get_item_dice_bonus(player):
    """Retorna bônus no dado baseado na raridade dos equipamentos"""
    bonus = 0
    if player.get("weapon"):
        for w in ITEMS["weapons"]:
            if w["name"] == player["weapon"]:
                bonus += RARITY_DICE_BONUS.get(w["rarity"], 0)
                break
    if player.get("armor"):
        for a in ITEMS["armor"]:
            if a["name"] == player["armor"]:
                bonus += RARITY_DICE_BONUS.get(a["rarity"], 0)
                break
    return bonus

def get_item_sell_price(item_name):
    for weapon in ITEMS["weapons"]:
        if weapon["name"] == item_name:
            rarity_prices = {
                "Comum": 2, "Incomum": 8, "Raro": 20,
                "Épico": 60, "Lendário": 200, "Mítico": 600,
                "Divino": 1500, "Primordial": 4000
            }
            return rarity_prices.get(weapon["rarity"], 5)

    for armor in ITEMS["armor"]:
        if armor["name"] == item_name:
            rarity_prices = {
                "Comum": 2, "Incomum": 8, "Raro": 20,
                "Épico": 60, "Lendário": 200, "Mítico": 600,
                "Divino": 1500, "Primordial": 4000
            }
            return rarity_prices.get(armor["rarity"], 5)

    if item_name in POTIONS:
        rarity_prices = {
            "Comum": 3, "Incomum": 10, "Raro": 30,
            "Épico": 80, "Lendário": 250, "Mítico": 800,
            "Divino": 2000
        }
        return rarity_prices.get(POTIONS[item_name]["rarity"], 5)

    return 3  # recursos

def add_xp(user_id, amount, bypass_boss_gate=False):
    player = get_player(user_id)

    # XP aumentado significativamente
    amount = int(amount * 2.5)

    if player.get("class") == "Bardo":
        amount = int(amount * 1.2)

    # Race XP multiplier
    race_name = player.get("race")
    if race_name and race_name in RACES:
        amount = int(amount * RACES[race_name].get("xp_mult", 1.0))

    # Multiplicador de período
    period_data = TIME_PERIODS.get(CURRENT_PERIOD.get("type", "dia"), TIME_PERIODS["dia"])
    amount = int(amount * period_data.get("xp_mult", 1.0))

    # BLOQUEIO DE BOSS: Se o jogador está no nível de boss e não derrotou ele, XP vai para
    # um "balde" de XP pendente que é liberado ao vencer o boss
    boss_gate_levels = {9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 189, 199}
    if not bypass_boss_gate and player["level"] in boss_gate_levels:
        boss_data = get_level_boss(player["level"])
        if boss_data and boss_data["name"] not in player.get("bosses", []):
            # Acumula XP pendente — será liberado ao vencer o boss
            effects = player.get("active_effects", {})
            pending = effects.get("pending_xp", 0) + amount
            effects["pending_xp"] = pending
            player["active_effects"] = effects
            save_player_db(user_id, player)
            return False  # retorna False — nível não mudou

    player["xp"] += amount
    player["total_xp_earned"] = player.get("total_xp_earned", 0) + amount
    leveled = False

    # Bloqueia level-up nos níveis de boss se o boss não foi derrotado
    while player["xp"] >= calc_xp(player["level"]):
        next_level = player["level"] + 1
        # Verifica se o próximo nível é de boss gate — bloqueia progressão além dele
        if player["level"] in boss_gate_levels and not bypass_boss_gate:
            boss_data = get_level_boss(player["level"])
            if boss_data and boss_data["name"] not in player.get("bosses", []):
                # Mantém XP no teto sem ultrapassar
                player["xp"] = calc_xp(player["level"]) - 1
                break
        player["xp"] -= calc_xp(player["level"])
        player["level"] += 1

        class_bonus = 0
        if player.get("class") and player["class"] in CLASSES:
            class_bonus = CLASSES[player["class"]]["hp_bonus"] // 10

        player["max_hp"] += (10 + class_bonus)
        player["hp"] = player["max_hp"]

        # Atualiza mana ao subir de nível
        new_max_mana = calc_max_mana(player)
        player["max_mana"] = new_max_mana
        player["mana"] = new_max_mana  # Recupera toda a mana ao subir de nível

        # Verificar desbloqueio livro de feitiços no nível 12
        if player["level"] == 12 and not player.get("spell_book_unlocked"):
            player["spell_book_unlocked"] = 1
            effects = player.get("active_effects", {})
            effects["notify_spellbook"] = True
            player["active_effects"] = effects

        leveled = True
        # Mark that evolution should be checked after level-up
        evol_levels = {40, 80, 120, 160}
        if player["level"] in evol_levels and player.get("class"):
            effects = player.get("active_effects", {})
            effects["check_evolution"] = True
            player["active_effects"] = effects

    save_player_db(user_id, player)

    if player.get("guild_id"):
        distribute_guild_xp(player["guild_id"], amount)

    return leveled


def release_pending_xp(user_id):
    """Libera o XP pendente acumulado durante bloqueio de boss. Chame após derrotar o boss."""
    player = get_player(user_id)
    effects = player.get("active_effects", {})
    pending = effects.pop("pending_xp", 0)
    player["active_effects"] = effects
    save_player_db(user_id, player)
    if pending > 0:
        # Chama add_xp com bypass para liberar tudo de uma vez
        add_xp(user_id, pending // 3, bypass_boss_gate=True)  # divide por 3 pois add_xp multiplica por 2.5
        return pending
    return 0

def distribute_guild_xp(guild_id, amount):
    """Distribui apenas 5% do XP ganho para os demais membros da guilda (nerf)."""
    shared = max(1, int(amount * 0.05))  # 5% do XP original, mínimo 1
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT members FROM guilds WHERE id = ?", (guild_id,))
    result = c.fetchone()

    if result:
        members = json.loads(result[0])
        for member_id in members:
            member = get_player(member_id)
            if member:
                member["xp"] += shared
                while member["xp"] >= calc_xp(member["level"]):
                    member["xp"] -= calc_xp(member["level"])
                    member["level"] += 1
                    class_bonus = 0
                    if member.get("class") and member["class"] in CLASSES:
                        class_bonus = CLASSES[member["class"]]["hp_bonus"] // 10
                    member["max_hp"] += (10 + class_bonus)
                    member["hp"] = member["max_hp"]
                    for wl in WORLDS.keys():
                        if member["level"] >= wl and wl not in member["worlds"]:
                            member["worlds"].append(wl)
                save_player_db(member_id, member)

    conn.close()

def remove_xp(user_id, amount):
    player = get_player(user_id)
    world = get_world(player["level"], player)

    adjusted_loss = int(amount * world.get("xp_loss_multiplier", 1.0))
    player["xp"] -= adjusted_loss

    while player["xp"] < 0 and player["level"] > 1:
        player["level"] -= 1
        player["xp"] += calc_xp(player["level"])

    if player["xp"] < 0:
        player["xp"] = 0

    if player["level"] == 1 and player["xp"] == 0:
        player["inventory"] = []
        player["weapon"] = None
        player["armor"] = None
        player["worlds"] = [1]
        player["bosses"] = []
        player["hp"] = 100
        player["max_hp"] = 100
        player["coins"] = 0
        player["class"] = None
        player["pet"] = None
        player["active_quest"] = None
        save_player_db(user_id, player)
        return "reset", adjusted_loss

    save_player_db(user_id, player)
    return "ok", adjusted_loss

def add_coins(user_id, amount):
    player = get_player(user_id)
    player["coins"] += amount
    if amount > 0:
        player["total_coins_earned"] = player.get("total_coins_earned", 0) + amount
    save_player_db(user_id, player)

def remove_coins(user_id, amount):
    player = get_player(user_id)
    if player["coins"] >= amount:
        player["coins"] -= amount
        save_player_db(user_id, player)
        return True
    return False

def get_level_boss(level):
    """Retorna boss de level correspondente ao nível do jogador"""
    boss_levels = {
        9: 1, 19: 10, 29: 20, 39: 30, 49: 40, 59: 50,
        69: 60, 79: 70, 89: 80, 99: 90, 109: 100,
        119: 110, 129: 120, 139: 130, 149: 140, 159: 150,
        169: 160, 179: 170, 189: 180, 199: 190
    }
    world_key = boss_levels.get(level)
    if world_key and world_key in WORLDS:
        return WORLDS[world_key]["boss"]
    # Fallback: usar o mundo mais próximo disponível
    if world_key:
        nearest = max((k for k in WORLDS.keys() if k <= world_key), default=1)
        return WORLDS[nearest]["boss"]
    return None

# ================= VIEWS / BOTÕES =================

# ─────────────────────────────────────────────────────────────
# HELPER: apply race bonuses to player
# ─────────────────────────────────────────────────────────────
def apply_race_bonuses(player, race_name):
    race = RACES[race_name]
    player["max_hp"]  += race["hp_bonus"]
    player["hp"]       = player["max_hp"]
    player["race"]     = race_name
    return player


# ─────────────────────────────────────────────────────────────
# HELPER: get current skills for player (tiered system)
# ─────────────────────────────────────────────────────────────
def get_player_skills(player):
    cls = player.get("class", "Guerreiro") or "Guerreiro"
    lvl = player.get("level", 1)
    tier_data = CLASS_TIERED_SKILLS.get(cls)
    if not tier_data:
        # fallback to old CLASS_SKILLS
        return CLASS_SKILLS.get(cls, CLASS_SKILLS["Guerreiro"])

    skills = list(tier_data["basic"])
    if lvl >= 40:
        skills += tier_data.get("intermediate", [])
    if lvl >= 80:
        skills += tier_data.get("advanced", [])
    # Supreme skill
    supreme = tier_data.get("supreme")
    if supreme and supreme["name"] in player.get("supreme_skills", []):
        skills.append(supreme)
    # Specialization special skill
    spec = player.get("specialization")
    if spec and spec in CLASS_SPECIALIZATIONS:
        spec_skill = CLASS_SPECIALIZATIONS[spec].get("special_skill")
        if spec_skill:
            skills.append(spec_skill)
    return skills


# ─────────────────────────────────────────────────────────────
# HELPER: check and trigger class evolution prompt
# ─────────────────────────────────────────────────────────────
async def check_class_evolution(channel, user_id):
    player = get_player(user_id)
    if not player or not player.get("class"):
        return
    cls = player["class"]
    lvl = player["level"]
    tree = CLASS_EVOLUTION_TREE.get(cls)
    if not tree:
        return
    current_tier = player.get("class_tier", 0)
    evolution_levels = sorted(tree.keys())
    # Which tiers haven't been taken yet
    for evo_lvl in evolution_levels:
        tier_index = evolution_levels.index(evo_lvl) + 1
        if lvl >= evo_lvl and current_tier < tier_index:
            evo_data = tree[evo_lvl]
            specs = evo_data["spec_options"]
            embed = discord.Embed(
                title=f"🌟 Evolução de Classe Disponível!",
                description=(
                    f"**{cls}** pode evoluir para **{evo_data['name']}**!\n\n"
                    f"Escolha sua especialização abaixo.\n"
                    f"*A escolha altera suas habilidades, passivas e estilo de combate.*"
                ),
                color=discord.Color.gold()
            )
            for s in specs:
                spec_data = CLASS_SPECIALIZATIONS.get(s)
                if spec_data:
                    embed.add_field(
                        name=f"{spec_data['emoji']} {s}",
                        value=f"{spec_data['desc']}\n**Passiva:** {spec_data['passive']}",
                        inline=False
                    )
            view = ClassEvolutionView(user_id, cls, evo_data["name"], specs, tier_index)
            await channel.send(embed=embed, view=view)
            return  # show one at a time


# ─────────────────────────────────────────────────────────────
# VIEW: Race selection (page 1 of 4)
# ─────────────────────────────────────────────────────────────
class RaceSelectView(discord.ui.View):
    def __init__(self, user_id, page=0, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.page = page
        self.answered = False
        all_races = list(RACES.keys())
        # 5 per page
        chunk = all_races[page*5:(page+1)*5]
        colors = [
            discord.ButtonStyle.primary, discord.ButtonStyle.success,
            discord.ButtonStyle.danger, discord.ButtonStyle.secondary,
            discord.ButtonStyle.primary
        ]
        for i, race_name in enumerate(chunk):
            race_data = RACES[race_name]
            btn = discord.ui.Button(
                label=race_name,
                style=colors[i % len(colors)],
                emoji=race_data["emoji"],
                row=0
            )
            btn.callback = self.make_cb(race_name)
            self.add_item(btn)
        # Nav buttons
        total_pages = (len(all_races) + 4) // 5
        if page > 0:
            prev_btn = discord.ui.Button(label="◀ Anterior", style=discord.ButtonStyle.secondary, row=1)
            prev_btn.callback = self.make_nav(page - 1)
            self.add_item(prev_btn)
        if page < total_pages - 1:
            next_btn = discord.ui.Button(label="Próxima ▶", style=discord.ButtonStyle.secondary, row=1)
            next_btn.callback = self.make_nav(page + 1)
            self.add_item(next_btn)

    def make_cb(self, race_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            if player.get("race"):
                return await interaction.response.send_message(f"❌ Você já é um(a) **{player['race']}**!", ephemeral=True)
            apply_race_bonuses(player, race_name)
            save_player_db(self.user_id, player)
            race_data = RACES[race_name]
            embed = discord.Embed(
                title=f"{race_data['emoji']} Raça Escolhida: {race_name}!",
                description=f"*{race_data['lore']}*\n\n{race_data['description']}",
                color=discord.Color.purple()
            )
            embed.add_field(name="❤️ Bônus HP",  value=f"+{race_data['hp_bonus']}",  inline=True)
            embed.add_field(name="⚔️ Bônus ATK", value=f"+{race_data['atk_bonus']}", inline=True)
            embed.add_field(name="🛡️ Bônus DEF", value=f"+{race_data['def_bonus']}", inline=True)
            embed.add_field(name="✨ Passiva",    value=race_data["passive"],          inline=False)
            embed.set_footer(text="Agora use 'escolher classe' para completar seu personagem!")
            await interaction.response.edit_message(embed=embed, view=None)
        return callback

    def make_nav(self, new_page):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta não é sua seleção!", ephemeral=True)
            all_races = list(RACES.keys())
            chunk = all_races[new_page*5:(new_page+1)*5]
            embed = discord.Embed(
                title=f"🧬 Escolha sua Raça (Página {new_page+1})",
                description="Sua raça define bônus permanentes e passivas únicas.",
                color=discord.Color.purple()
            )
            for rn in chunk:
                rd = RACES[rn]
                embed.add_field(
                    name=f"{rd['emoji']} {rn}",
                    value=f"{rd['description']}\n**Passiva:** {rd['passive']}\n**HP:** +{rd['hp_bonus']} | **ATK:** +{rd['atk_bonus']} | **DEF:** +{rd['def_bonus']}",
                    inline=False
                )
            new_view = RaceSelectView(self.user_id, page=new_page)
            await interaction.response.edit_message(embed=embed, view=new_view)
        return callback


# ─────────────────────────────────────────────────────────────
# VIEW: Class selection (paginated, 5 per page across 6 pages)
# ─────────────────────────────────────────────────────────────
class ClassSelectView(discord.ui.View):
    def __init__(self, user_id, page=0, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.page = page
        self.answered = False
        all_classes = list(CLASSES.keys())
        chunk = all_classes[page*5:(page+1)*5]
        colors = [
            discord.ButtonStyle.primary, discord.ButtonStyle.success,
            discord.ButtonStyle.danger, discord.ButtonStyle.secondary,
            discord.ButtonStyle.primary
        ]
        for i, class_name in enumerate(chunk):
            class_data = CLASSES[class_name]
            btn = discord.ui.Button(
                label=class_name[:25],
                style=colors[i % len(colors)],
                emoji=class_data["emoji"],
                row=0
            )
            btn.callback = self.make_cb(class_name)
            self.add_item(btn)
        total_pages = (len(all_classes) + 4) // 5
        if page > 0:
            prev_btn = discord.ui.Button(label="◀ Anterior", style=discord.ButtonStyle.secondary, row=1)
            prev_btn.callback = self.make_nav(page - 1)
            self.add_item(prev_btn)
        if page < total_pages - 1:
            next_btn = discord.ui.Button(label="Próxima ▶", style=discord.ButtonStyle.secondary, row=1)
            next_btn.callback = self.make_nav(page + 1)
            self.add_item(next_btn)

    def make_cb(self, class_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            if player.get("class"):
                return await interaction.response.send_message(f"❌ Você já é um(a) **{player['class']}**!", ephemeral=True)
            player["class"] = class_name
            class_data = CLASSES[class_name]
            player["max_hp"] += class_data["hp_bonus"]
            player["hp"] = player["max_hp"]
            # Apply race affinity bonus if player has a race
            race = player.get("race")
            affinity_bonus = ""
            if race and race in class_data.get("race_affinity", []):
                player["max_hp"] += 15
                player["hp"] = player["max_hp"]
                affinity_bonus = f"\n\n🌟 **Bônus de Afinidade!** Sua raça **{race}** tem afinidade com esta classe!\n+15 HP bônus adicional."
            save_player_db(self.user_id, player)
            embed = discord.Embed(
                title=f"{class_data['emoji']} Classe Escolhida: {class_name}!",
                description=f"{class_data['description']}{affinity_bonus}",
                color=discord.Color.gold()
            )
            embed.add_field(name="💪 Bônus ATK", value=f"+{class_data['atk_bonus']}", inline=True)
            embed.add_field(name="🛡️ Bônus DEF", value=f"+{class_data['def_bonus']}", inline=True)
            embed.add_field(name="❤️ Bônus HP",  value=f"+{class_data['hp_bonus']}", inline=True)
            tree = CLASS_EVOLUTION_TREE.get(class_name)
            if tree:
                evo_levels = sorted(tree.keys())
                evo_text = " → ".join([f"Nv.{lvl} ({tree[lvl]['name']})" for lvl in evo_levels])
                embed.add_field(name="🌟 Árvore de Evolução", value=evo_text, inline=False)
            embed.set_footer(text="Use 'habilidades' para ver suas skills. Evolua nos níveis 40, 80, 120 e 160!")
            await interaction.response.edit_message(embed=embed, view=None)
        return callback

    def make_nav(self, new_page):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta não é sua seleção!", ephemeral=True)
            all_classes = list(CLASSES.keys())
            chunk = all_classes[new_page*5:(new_page+1)*5]
            total_pages = (len(all_classes) + 4) // 5
            embed = discord.Embed(
                title=f"🎭 Escolha sua Classe (Página {new_page+1}/{total_pages})",
                description="Cada classe tem árvore de evolução e especializações únicas.",
                color=discord.Color.blue()
            )
            for cn in chunk:
                cd = CLASSES[cn]
                tree = CLASS_EVOLUTION_TREE.get(cn)
                evo_hint = ""
                if tree:
                    evo_hint = f"\n🌟 Evolui nos níveis: {', '.join(str(k) for k in sorted(tree.keys()))}"
                embed.add_field(
                    name=f"{cd['emoji']} {cn}",
                    value=f"{cd['description']}\n**ATK:** +{cd['atk_bonus']} | **DEF:** +{cd['def_bonus']} | **HP:** +{cd['hp_bonus']}{evo_hint}",
                    inline=False
                )
            new_view = ClassSelectView(self.user_id, page=new_page)
            await interaction.response.edit_message(embed=embed, view=new_view)
        return callback


# Keep old aliases for backward compat
ClassSelectButton  = ClassSelectView
ClassSelectButton2 = ClassSelectView


# ─────────────────────────────────────────────────────────────
# VIEW: Class Evolution / Specialization choice
# ─────────────────────────────────────────────────────────────
class ClassEvolutionView(discord.ui.View):
    def __init__(self, user_id, base_class, evolved_name, spec_options, new_tier, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.base_class = base_class
        self.evolved_name = evolved_name
        self.answered = False
        colors = [discord.ButtonStyle.success, discord.ButtonStyle.danger]
        for i, spec in enumerate(spec_options):
            spec_data = CLASS_SPECIALIZATIONS.get(spec, {})
            btn = discord.ui.Button(
                label=spec[:25],
                style=colors[i % len(colors)],
                emoji=spec_data.get("emoji", "⭐"),
                row=0
            )
            btn.callback = self.make_cb(spec, new_tier)
            self.add_item(btn)

    def make_cb(self, spec_name, new_tier):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta evolução não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            spec_data = CLASS_SPECIALIZATIONS.get(spec_name, {})
            player["class"] = self.base_class
            player["specialization"] = spec_name
            player["class_tier"] = new_tier

            # ── Status escalonados por tier ─────────────────────────────
            # Tier 1 (nível 40):  1× base
            # Tier 2 (nível 80):  2.5× base + bônus extra
            # Tier 3 (nível 120): 5× base + bônus extra grande
            # Tier 4 (nível 160): 10× base + bônus máximo (poder divino)
            BASE_HP  = spec_data.get("bonus_hp",  0)
            BASE_ATK = spec_data.get("bonus_atk", 0)
            BASE_DEF = spec_data.get("bonus_def", 0)

            TIER_MULTIPLIERS = {
                1: {"hp": 1.0,  "atk": 1.0,  "def": 1.0,  "extra_hp":   0, "extra_atk":  0, "extra_def":  0},
                2: {"hp": 2.5,  "atk": 2.5,  "def": 2.5,  "extra_hp":  50, "extra_atk": 20, "extra_def": 15},
                3: {"hp": 5.0,  "atk": 5.0,  "def": 5.0,  "extra_hp": 150, "extra_atk": 60, "extra_def": 45},
                4: {"hp": 10.0, "atk": 10.0, "def": 10.0, "extra_hp": 400, "extra_atk":150, "extra_def":120},
            }
            mult = TIER_MULTIPLIERS.get(new_tier, TIER_MULTIPLIERS[1])

            bonus_hp  = int(BASE_HP  * mult["hp"])  + mult["extra_hp"]
            bonus_atk = int(BASE_ATK * mult["atk"]) + mult["extra_atk"]
            bonus_def = int(BASE_DEF * mult["def"]) + mult["extra_def"]

            # Garantir mínimos por tier (mesmo specs sem bônus base ganham algo)
            MIN_HP  = {1: 10, 2: 80,  3: 200, 4: 500}
            MIN_ATK = {1:  5, 2: 30,  3:  80, 4: 200}
            MIN_DEF = {1:  0, 2: 20,  3:  55, 4: 130}
            bonus_hp  = max(bonus_hp,  MIN_HP[new_tier])
            bonus_atk = max(bonus_atk, MIN_ATK[new_tier])
            bonus_def = max(bonus_def, MIN_DEF[new_tier])

            # Aplicar bônus ao jogador
            player["max_hp"] += bonus_hp
            player["hp"] = min(player["hp"] + bonus_hp, player["max_hp"])
            save_player_db(self.user_id, player)

            # Nomes dos tiers para exibição
            TIER_NAMES = {1: "Tier I — Elite", 2: "Tier II — Mestre", 3: "Tier III — Lendário", 4: "Tier IV — Divino"}
            TIER_COLORS = {1: discord.Color.blue(), 2: discord.Color.gold(), 3: discord.Color.from_rgb(255, 60, 0), 4: discord.Color.from_rgb(200, 0, 255)}
            TIER_EMOJIS = {1: "🔵", 2: "🌟", 3: "🔥", 4: "👑"}

            embed = discord.Embed(
                title=f"{TIER_EMOJIS[new_tier]} EVOLUÇÃO {TIER_NAMES[new_tier].upper()}!",
                description=(
                    f"Você evoluiu para **{self.evolved_name}**!\n"
                    f"Especialização: **{spec_name}** {spec_data.get('emoji','')}\n\n"
                    f"*{spec_data.get('desc', '')}*\n\n"
                    f"**Passiva:** {spec_data.get('passive', '')}"
                ),
                color=TIER_COLORS[new_tier]
            )
            if spec_data.get("special_skill"):
                sk = spec_data["special_skill"]
                embed.add_field(name="⚡ Habilidade Especial", value=f"{sk['name']} — {sk['desc']}", inline=False)
            embed.add_field(name="❤️ HP Ganho",  value=f"**+{bonus_hp}**",  inline=True)
            embed.add_field(name="⚔️ ATK Ganho", value=f"**+{bonus_atk}**", inline=True)
            embed.add_field(name="🛡️ DEF Ganho", value=f"**+{bonus_def}**", inline=True)
            if new_tier >= 2:
                embed.add_field(
                    name=f"📈 Por que tão forte?",
                    value=(
                        f"*Cada tier de evolução multiplica os bônus da especialização.*\n"
                        f"Tier I: ×1 | Tier II: ×2.5 | Tier III: ×5 | Tier IV: ×10"
                    ),
                    inline=False
                )
            embed.set_footer(text=f"Tier {new_tier}/4 — Use 'habilidades' para ver suas skills!")
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


class PetTameButton(discord.ui.View):
    def __init__(self, user_id, pet, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.pet = pet
        self.answered = False

    @discord.ui.button(label="Tentar Domesticar", style=discord.ButtonStyle.green, emoji="🤝")
    async def tame(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Este pet não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True

        roll = roll_dice()
        luck = get_luck(roll)
        embed = discord.Embed(title="🎲 Tentativa de Domesticação", color=discord.Color.blue())
        embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            player = get_player(self.user_id)
            dmg = random.randint(20, 40)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = 1
            save_player_db(self.user_id, player)
            embed.add_field(name="💥 O Pet Ataca!", value=f"*'{self.pet['name']} se assusta e ataca você!'*\n\n💔 **−{dmg} HP**", inline=False)
            embed.color = discord.Color.red()
        elif roll <= 6:
            embed.add_field(name="🏃 Fuga!", value=f"*'{self.pet['name']} não confia em você e foge...'*", inline=False)
            embed.color = discord.Color.orange()
        else:
            player = get_player(self.user_id)
            pet_entry = {**self.pet, "evo_stage": 1, "pet_xp": 0}
            if not player.get("pet"):
                # Sem pet ativo → torna-se pet ativo
                player["pet"] = self.pet["name"]
                save_player_db(self.user_id, player)
                embed.add_field(
                    name="✨ Domesticado! (Pet Ativo)",
                    value=f"*'{self.pet['emoji']} **{self.pet['name']}** agora é seu companheiro ativo!'*\n\n"
                          f"💪 **+{self.pet['bonus_atk']} ATK** | ❤️ **+{self.pet['bonus_hp']} HP**\n"
                          f"*Use `ver fazenda` para ver todos seus pets.*",
                    inline=False
                )
            else:
                # Já tem pet ativo → vai pra fazenda automaticamente
                pets_list = player.get("pets_list", [])
                if len(pets_list) >= 15:
                    embed.add_field(name="❌ Fazenda Cheia!", value="Sua fazenda já tem 15 pets! Use `ver fazenda` para gerenciar.", inline=False)
                    embed.color = discord.Color.red()
                else:
                    pets_list.append(pet_entry)
                    player["pets_list"] = pets_list
                    save_player_db(self.user_id, player)
                    embed.add_field(
                        name=f"🐾 Domesticado! → Fazenda",
                        value=f"*'{self.pet['emoji']} **{self.pet['name']}** foi para sua fazenda!'*\n\n"
                              f"💪 **+{self.pet['bonus_atk']} ATK** | ❤️ **+{self.pet['bonus_hp']} HP**\n"
                              f"Pet ativo atual: **{player['pet']}**\n"
                              f"*Use `trocar pet [nome]` para definir como ativo, ou `ver fazenda`.*",
                        inline=False
                    )
            embed.color = discord.Color.gold()

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Deixar Ir", style=discord.ButtonStyle.gray, emoji="👋")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esta escolha não é sua!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"*'Você decide não arriscar e deixa {self.pet['name']} em paz...'*", view=None
        )


class EquipButton(discord.ui.View):
    def __init__(self, user_id, item_name, item_type, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.item_name = item_name
        self.item_type = item_type
        self.answered = False

    @discord.ui.button(label="Equipar", style=discord.ButtonStyle.green, emoji="⚔️")
    async def equip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse item não é seu!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)
        old_item = player[self.item_type]
        player[self.item_type] = self.item_name
        save_player_db(self.user_id, player)

        if old_item:
            response = f"✅ **Equipado!**\n\n🔄 Você substituiu **{old_item}** por **{self.item_name}**!\n\n*'Seu poder aumenta...'*"
        else:
            response = f"✅ **Equipado!**\n\n⚔️ Você equipou **{self.item_name}**!\n\n*'Você está mais forte agora.'*"

        await interaction.response.edit_message(content=response, view=None)

    @discord.ui.button(label="Guardar", style=discord.ButtonStyle.gray, emoji="🎒")
    async def keep(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse item não é seu!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)
        player["inventory"].append(self.item_name)
        save_player_db(self.user_id, player)
        await interaction.response.edit_message(
            content=f"🎒 **Guardado!**\n\nVocê guarda **{self.item_name}** no inventário.\n\n*'Pode ser útil depois...'*",
            view=None
        )


class BossButton(discord.ui.View):
    def __init__(self, user_id, boss_name, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.boss_name = boss_name
        self.answered = False

    @discord.ui.button(label="Enfrentar Sozinho", style=discord.ButtonStyle.red, emoji="⚔️")
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"⚔️ **Você avança em direção ao {self.boss_name}!**\n\n*A batalha épica começa...*", view=None
        )
        await asyncio.sleep(2)
        await fight_boss(interaction.channel, self.user_id)

    @discord.ui.button(label="Chamar Aliados", style=discord.ButtonStyle.blurple, emoji="👥")
    async def call_allies(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"📣 **{interaction.user.mention} está convocando aliados para enfrentar o {self.boss_name}!**\n\nUse `juntar boss` para participar desta batalha! (até 5 jogadores)\n\nO líder deverá usar `iniciar batalha boss` quando estiver pronto.",
            view=None
        )
        # Registra na DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        player = get_player(self.user_id)
        world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
        c.execute("INSERT INTO boss_battles (boss_name, leader_id, members, world_level) VALUES (?, ?, ?, ?)",
                  (self.boss_name, str(self.user_id), json.dumps([str(self.user_id)]), world_level))
        conn.commit()
        conn.close()

    @discord.ui.button(label="Recuar", style=discord.ButtonStyle.gray, emoji="🏃")
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esse não é seu boss!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"🏃 **Você recua estrategicamente.**\n\n*'A prudência também é sabedoria.'*", view=None
        )


class RevengeTrainingView(discord.ui.View):
    """Mostrado ao jogador após derrota em boss de level — opções de Vingança ou Treinamento"""
    def __init__(self, user_id, boss_data, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.boss_data = boss_data
        self.answered = False

    @discord.ui.button(label="⚔️ Vingança!", style=discord.ButtonStyle.red, emoji="🔥")
    async def revenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Essa escolha não é sua!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        # Store revenge flag and boss for the next fight
        player = get_player(self.user_id)
        effects = player.get("active_effects", {})
        effects["pending_boss"] = self.boss_data
        effects["used_revenge"] = True
        player["active_effects"] = effects
        save_player_db(self.user_id, player)
        await interaction.response.edit_message(
            content=f"🔥 **A raiva te toma! Você avança novamente contra {self.boss_data['name']}!**\n\n*'O ódio pode ser a maior das forças!'*",
            view=None
        )
        await asyncio.sleep(2)
        await fight_boss(interaction.channel, self.user_id)

    @discord.ui.button(label="🏋️ Treinamento", style=discord.ButtonStyle.green, emoji="💪")
    async def training(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Essa escolha não é sua!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)
        effects = player.get("active_effects", {})
        effects["pending_boss"] = self.boss_data
        player["active_effects"] = effects
        save_player_db(self.user_id, player)
        embed = discord.Embed(
            title="🏋️ CENTRO DE TREINAMENTO",
            description=f"*'Um sábio ancião te guia: Seu corpo precisa de mais força para enfrentar {self.boss_data['name']}...'*\n\nEscolha o tipo de treino abaixo. Após treinar, use `desafiar boss` para renfrentar o boss!",
            color=discord.Color.green()
        )
        for name, data in TRAINING_OPTIONS.items():
            boosts = []
            if data.get("atk_boost"):
                boosts.append(f"+{data['atk_boost']} ATK")
            if data.get("def_boost"):
                boosts.append(f"+{data['def_boost']} DEF")
            if data.get("hp_boost"):
                boosts.append(f"+{data['hp_boost']} HP Max")
            embed.add_field(
                name=f"{data['emoji']} Treino de {name.capitalize()}",
                value=f"**{data['desc']}**\n💰 Custo: `{data['cost']:,}` CSI\n📈 Bônus: {', '.join(boosts)}",
                inline=True
            )
        embed.set_footer(text="Use: treinar força | treinar defesa | treinar vitalidade | treinar intensivo")
        view = TrainingView(self.user_id, self.boss_data)
        await interaction.response.edit_message(content=None, embed=embed, view=view)

    @discord.ui.button(label="🏃 Recuar", style=discord.ButtonStyle.gray)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Essa escolha não é sua!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content="🏃 *Você recua para recuperar suas forças. Às vezes, a prudência é a maior virtude.*",
            view=None
        )


class TrainingView(discord.ui.View):
    """Botões de treinamento após derrota em boss"""
    def __init__(self, user_id, boss_data=None, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.boss_data = boss_data
        self.answered = False
        for key, data in TRAINING_OPTIONS.items():
            label = f"{data['emoji']} {key.capitalize()} ({data['cost']} CSI)"
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
            btn.callback = self._make_callback(key)
            self.add_item(btn)

    def _make_callback(self, training_key):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Essa escolha não é sua!", ephemeral=True)
            if self.answered:
                return
            self.answered = True
            player = get_player(self.user_id)
            opt = TRAINING_OPTIONS[training_key]
            cost = opt["cost"]
            if player["coins"] < cost:
                self.answered = False
                return await interaction.response.send_message(
                    f"❌ Você não tem CSI suficiente! Precisa de `{cost:,}` mas tem `{player['coins']:,}`.", ephemeral=True
                )
            player["coins"] -= cost
            boosts = []
            if opt.get("atk_boost"):
                player["temp_atk_boost"] = player.get("temp_atk_boost", 0) + opt["atk_boost"]
                boosts.append(f"+{opt['atk_boost']} ATK")
            if opt.get("def_boost"):
                player["temp_def_boost"] = player.get("temp_def_boost", 0) + opt["def_boost"]
                boosts.append(f"+{opt['def_boost']} DEF")
            if opt.get("hp_boost"):
                player["temp_hp_boost"] = player.get("temp_hp_boost", 0) + opt["hp_boost"]
                player["max_hp"] = player.get("max_hp", 100) + opt["hp_boost"]
                player["hp"] = min(player["hp"] + opt["hp_boost"], player["max_hp"])
                boosts.append(f"+{opt['hp_boost']} HP Max")

            # Training counter for achievement
            training_count = player.get("training_points", 0) + 1
            player["training_points"] = training_count
            save_player_db(self.user_id, player)

            embed = discord.Embed(
                title=f"💪 Treino Completo!",
                description=f"*'O ancião sorri: Você ficou mais forte!'*\n\n{opt['emoji']} **Treino de {training_key.capitalize()}** concluído!\n\n📈 **Melhorias:** {', '.join(boosts)}\n💰 **Custo:** −{cost:,} CSI",
                color=discord.Color.green()
            )
            if self.boss_data:
                embed.set_footer(text=f"Use 'desafiar boss' para enfrentar {self.boss_data['name']} novamente!")

            await interaction.response.edit_message(embed=embed, view=None)
            await check_achievements(interaction.channel, self.user_id, "training_10" if training_count >= 10 else None)
            if training_count >= 10:
                await check_achievements(interaction.channel, self.user_id, "training_10")
        return callback


class TradeButton(discord.ui.View):
    def __init__(self, from_user, to_user, from_items, to_items, timeout=300):
        super().__init__(timeout=timeout)
        self.from_user = from_user
        self.to_user = to_user
        self.from_items = from_items
        self.to_items = to_items
        self.answered = False

    @discord.ui.button(label="Aceitar Troca", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.to_user):
            return await interaction.response.send_message("❌ Esta troca não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True

        from_player = get_player(self.from_user)
        to_player = get_player(self.to_user)

        def _is_weapon(item_name):
            return any(w["name"].lower() == item_name.lower() for w in ITEMS["weapons"])

        def _is_armor(item_name):
            return any(a["name"].lower() == item_name.lower() for a in ITEMS["armor"])

        def _get_item_name_exact(item_name):
            """Retorna o nome exato do item (case-insensitive) ou None"""
            for w in ITEMS["weapons"]:
                if w["name"].lower() == item_name.strip().lower():
                    return w["name"]
            for a in ITEMS["armor"]:
                if a["name"].lower() == item_name.strip().lower():
                    return a["name"]
            return item_name.strip()

        # Remove itens do from_player (inventário ou slot equipado)
        for item in self.from_items:
            exact = _get_item_name_exact(item)
            if exact in from_player["inventory"]:
                from_player["inventory"].remove(exact)
            elif from_player.get("weapon") and from_player["weapon"].lower() == item.strip().lower():
                from_player["weapon"] = None
            elif from_player.get("armor") and from_player["armor"].lower() == item.strip().lower():
                from_player["armor"] = None

        # Remove itens do to_player (inventário ou slot equipado)
        for item in self.to_items:
            exact = _get_item_name_exact(item)
            if exact in to_player["inventory"]:
                to_player["inventory"].remove(exact)
            elif to_player.get("weapon") and to_player["weapon"].lower() == item.strip().lower():
                to_player["weapon"] = None
            elif to_player.get("armor") and to_player["armor"].lower() == item.strip().lower():
                to_player["armor"] = None

        # Adiciona itens de to_player para from_player (garantindo nome exato)
        for item in self.to_items:
            exact = _get_item_name_exact(item)
            from_player["inventory"].append(exact)

        # Adiciona itens de from_player para to_player (garantindo nome exato)
        for item in self.from_items:
            exact = _get_item_name_exact(item)
            to_player["inventory"].append(exact)

        save_player_db(self.from_user, from_player)
        save_player_db(self.to_user, to_player)

        # Monta resumo da troca com tipo correto
        def _item_type_label(item_name):
            if _is_weapon(item_name): return "⚔️ Arma"
            if _is_armor(item_name): return "🛡️ Armadura"
            return "🎒 Item"

        from_labels = ", ".join(f"{_item_type_label(i)} **{_get_item_name_exact(i)}**" for i in self.from_items)
        to_labels = ", ".join(f"{_item_type_label(i)} **{_get_item_name_exact(i)}**" for i in self.to_items)

        await interaction.response.edit_message(
            content=(
                f"✅ **Troca Realizada!**\n\n"
                f"*'Os itens mudam de mãos...'*\n\n"
                f"📤 Você recebeu: {to_labels}\n"
                f"📥 Outro jogador recebeu: {from_labels}\n\n"
                f"💡 Use `equipar [nome do item]` para equipar armas ou armaduras recebidas!"
            ),
            view=None
        )

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.to_user):
            return await interaction.response.send_message("❌ Esta troca não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(content=f"❌ **Troca Recusada**\n\n*'Talvez em outra ocasião...'*", view=None)


class ShopButton(discord.ui.View):
    def __init__(self, user_id, items, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.items = items

    @discord.ui.button(label="Comprar Item 1", style=discord.ButtonStyle.green, emoji="💰")
    async def buy1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 0)

    @discord.ui.button(label="Comprar Item 2", style=discord.ButtonStyle.green, emoji="💰")
    async def buy2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 1)

    @discord.ui.button(label="Comprar Item 3", style=discord.ButtonStyle.green, emoji="💰")
    async def buy3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_item(interaction, 2)

    @discord.ui.button(label="Sair", style=discord.ButtonStyle.gray, emoji="🚪")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🚪 **Você sai da loja.**\n\n*'Até a próxima, viajante...'*", view=None)

    async def buy_item(self, interaction, index):
        if index >= len(self.items):
            return await interaction.response.send_message("❌ Item inválido!", ephemeral=True)
        item = self.items[index]
        player = get_player(interaction.user.id)

        if player["coins"] < item["price"]:
            return await interaction.response.send_message(
                f"❌ **Moedas insuficientes!**\n\nVocê precisa de **{item['price']} CSI** mas tem apenas **{player['coins']} CSI**.",
                ephemeral=True
            )

        remove_coins(interaction.user.id, item["price"])
        if item["type"] in ["weapon", "armor"]:
            player = get_player(interaction.user.id)
            player["inventory"].append(item["name"])
            save_player_db(interaction.user.id, player)
        elif item["type"] == "potion":
            player = get_player(interaction.user.id)
            player["inventory"].append(item["name"])
            save_player_db(interaction.user.id, player)

        await interaction.response.send_message(
            f"✅ **Compra realizada!**\n\nVocê comprou **{item['name']}** por **{item['price']} CSI**!\n\n*'Uma boa escolha!'*",
            ephemeral=True
        )


class DungeonSelectButton(discord.ui.View):
    def __init__(self, user_id, dungeons, world, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.dungeons = dungeons
        self.world = world
        self.answered = False

        for i, dungeon in enumerate(dungeons[:3]):
            button = discord.ui.Button(
                label=dungeon["name"], style=discord.ButtonStyle.primary,
                emoji="🏛️", custom_id=f"dungeon_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Esta dungeon não é para você!", ephemeral=True)
            if self.answered:
                return
            dungeon = self.dungeons[index]
            is_secret = dungeon.get("secret", False)
            is_locked = dungeon.get("locked", False)

            # ─── Verificação de chave para dungeon secreta ──────────────
            if is_secret and is_locked:
                key_name = dungeon.get("key_name", "")
                return await interaction.response.send_message(
                    f"🔒 **Dungeon Bloqueada!**\n\n"
                    f"Você descobriu **{dungeon['name']}** mas não possui a chave.\n"
                    f"Necessário: **{key_name}**\n"
                    f"*Explore dungeons comuns desta região para encontrar a chave em baús!*",
                    ephemeral=True
                )
            if is_secret and not is_locked:
                key_name = dungeon.get("key_name", "")
                if key_name:
                    player = get_player(self.user_id)
                    if not player_has_key(player, key_name):
                        return await interaction.response.send_message(
                            f"🔒 **Dungeon Secreta Bloqueada!**\n\nNecessário: **{key_name}**\n"
                            f"*Explore dungeons comuns desta região para encontrar a chave em baús!*",
                            ephemeral=True
                        )
                    # Consome a chave ao entrar
                    consume_key(player, key_name)
                    save_player_db(self.user_id, player)

            self.answered = True
            if is_secret:
                await interaction.response.edit_message(
                    content=f"🔮 **ENTRANDO NA DUNGEON SECRETA: {dungeon['name']}!**\n\n*'A chave brilha e a porta se abre... Que os deuses te protejam!'*",
                    view=None
                )
            else:
                await interaction.response.edit_message(
                    content=f"🏛️ **Você entra na {dungeon['name']}!**\n\n*'Que a sorte esteja com você...'*",
                    view=None
                )
            await asyncio.sleep(2)
            await explore_dungeon(interaction.channel, self.user_id, dungeon, self.world)
        return callback


class QuestAcceptButton(discord.ui.View):
    def __init__(self, user_id, quest, timeout=120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.quest = quest
        self.answered = False

    @discord.ui.button(label="Aceitar Quest", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Esta quest não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        player = get_player(self.user_id)

        if player.get("active_quest"):
            return await interaction.response.edit_message(
                content="❌ Você já tem uma quest ativa! Abandone-a primeiro com `abandonar quest`.", view=None
            )
        if self.quest["id"] in player.get("completed_quests", []):
            return await interaction.response.edit_message(
                content="❌ Você já completou esta quest!", view=None
            )

        quest_data = dict(self.quest)
        quest_data["progress"] = 0
        quest_data["started_at"] = datetime.now().isoformat()
        player["active_quest"] = quest_data
        save_player_db(self.user_id, player)

        embed = discord.Embed(
            title=f"📜 Quest Aceita: {self.quest['name']}",
            description=f"*{self.quest['npc']} sorri e diz:*\n\n*'{self.quest['lore']}'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎯 Objetivo", value=self.quest["description"], inline=False)
        embed.add_field(name="⭐ Recompensa XP", value=str(self.quest["reward_xp"]), inline=True)
        embed.add_field(name="💰 Recompensa Coins", value=str(self.quest["reward_coins"]), inline=True)
        if self.quest.get("reward_item"):
            embed.add_field(name="🎁 Item Recompensa", value=self.quest["reward_item"], inline=True)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.gray, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(content="*Você declina a quest e segue em frente.*", view=None)


class PvPChallengeButton(discord.ui.View):
    def __init__(self, challenger_id, target_id, challenger_name, target_name, timeout=120):
        super().__init__(timeout=timeout)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.challenger_name = challenger_name
        self.target_name = target_name
        self.answered = False

    @discord.ui.button(label="⚔️ Aceitar Duelo!", style=discord.ButtonStyle.red, emoji="⚔️")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_id):
            return await interaction.response.send_message("❌ Esse desafio não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"⚔️ **{self.target_name}** aceita o desafio! A batalha começa!",
            view=None
        )
        await asyncio.sleep(1)
        await fight_pvp(interaction.channel, self.challenger_id, self.target_id)

    @discord.ui.button(label="🏃 Recusar", style=discord.ButtonStyle.gray)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_id):
            return await interaction.response.send_message("❌ Esse desafio não é para você!", ephemeral=True)
        if self.answered:
            return
        self.answered = True
        await interaction.response.edit_message(
            content=f"🏃 **{self.target_name}** recusou o desafio de **{self.challenger_name}**...\n\n*'A coragem é necessária para um duelo.'*",
            view=None
        )


async def fight_pvp(channel, challenger_id, target_id):
    """Batalha PvP estilo Pokémon entre dois jogadores"""
    challenger = get_player(challenger_id)
    target = get_player(target_id)

    try:
        challenger_user = await bot.fetch_user(int(challenger_id))
        target_user = await bot.fetch_user(int(target_id))
        ch_name = challenger_user.display_name
        tg_name = target_user.display_name
    except:
        ch_name = "Desafiante"
        tg_name = "Alvo"

    ch_cls = challenger.get("class", "Guerreiro")
    tg_cls = target.get("class", "Guerreiro")
    ch_skills = get_player_skills(challenger)
    tg_skills = get_player_skills(target)

    # Stats de batalha (baseados nos stats reais + nível)
    ch_hp = challenger["max_hp"]
    tg_hp = target["max_hp"]
    ch_mana = calc_max_mana(challenger)
    tg_mana = calc_max_mana(target)
    ch_atk_base = CLASSES[ch_cls]["atk_bonus"] + challenger["level"] * 2
    tg_atk_base = CLASSES[tg_cls]["atk_bonus"] + target["level"] * 2
    ch_def = CLASSES[ch_cls]["def_bonus"] + challenger["level"]
    tg_def = CLASSES[tg_cls]["def_bonus"] + target["level"]

    # Bônus de item
    def get_item_atk_bonus(player):
        bonus = 0
        if player.get("weapon"):
            for w in ITEMS["weapons"]:
                if w["name"] == player["weapon"]:
                    bonus += w.get("atk", 0) // 5
                    break
        return bonus

    def get_item_def_bonus(player):
        bonus = 0
        if player.get("armor"):
            for a in ITEMS["armor"]:
                if a["name"] == player["armor"]:
                    bonus += a.get("def", 0) // 5
                    break
        return bonus

    ch_atk_base += get_item_atk_bonus(challenger)
    tg_atk_base += get_item_atk_bonus(target)
    ch_def += get_item_def_bonus(challenger)
    tg_def += get_item_def_bonus(target)

    ch_cur_hp = ch_hp
    tg_cur_hp = tg_hp
    ch_cur_mana = ch_mana
    tg_cur_mana = tg_mana

    ch_icon = CLASSES[ch_cls]["emoji"]
    tg_icon = CLASSES[tg_cls]["emoji"]

    # Intro épica
    intro = discord.Embed(
        title="⚔️ DUELO INICIADO! ⚔️",
        description=f"*O narrador anuncia com voz trovejante:*\n\n**'{ch_name} vs {tg_name}!'**\n\n*'Que o mais digno prevaleça!'*",
        color=discord.Color.dark_red()
    )
    intro.add_field(
        name=f"{ch_icon} {ch_name} ({ch_cls})",
        value=f"❤️ HP: `{ch_cur_hp}` | ✨ Mana: `{ch_cur_mana}`\n⚔️ ATK: `{ch_atk_base}` | 🛡️ DEF: `{ch_def}`\nArma: {challenger.get('weapon') or 'Nenhuma'}",
        inline=True
    )
    intro.add_field(
        name=f"{tg_icon} {tg_name} ({tg_cls})",
        value=f"❤️ HP: `{tg_cur_hp}` | ✨ Mana: `{tg_cur_mana}`\n⚔️ ATK: `{tg_atk_base}` | 🛡️ DEF: `{tg_def}`\nArma: {target.get('weapon') or 'Nenhuma'}",
        inline=True
    )
    await channel.send(embed=intro)
    await asyncio.sleep(2)

    # Sistema de batalha em turnos (max 6 turnos)
    battle_log = []
    turn = 1
    ch_poison = False
    tg_poison = False
    ch_weakened = False
    tg_weakened = False

    while ch_cur_hp > 0 and tg_cur_hp > 0 and turn <= 6:
        turn_embed = discord.Embed(
            title=f"⚔️ TURNO {turn}",
            color=discord.Color.red()
        )

        # === Ação do Desafiante ===
        # Escolhe habilidade (prioriza com mana disponível)
        available_ch = [s for s in ch_skills if s["mana_cost"] <= ch_cur_mana]
        if not available_ch:
            available_ch = [ch_skills[0]]  # fallback: ataque básico
        ch_skill = random.choice(available_ch)
        ch_cur_mana = max(0, ch_cur_mana - ch_skill["mana_cost"])

        # Calcula dano
        ch_dmg_raw = int(ch_atk_base * ch_skill["dmg_mult"])
        if ch_weakened:
            ch_dmg_raw = int(ch_dmg_raw * 0.7)
        # Chance de crítico
        if random.random() < ch_skill.get("crit_chance", 0.1):
            ch_dmg_raw = int(ch_dmg_raw * 1.8)
            ch_skill_name = f"💥 CRÍTICO! {ch_skill['name']}"
        else:
            ch_skill_name = ch_skill["name"]
        # Ignora defesa se skill especifica
        if ch_skill.get("ignore_def"):
            ch_dmg = max(1, ch_dmg_raw)
        else:
            ch_dmg = max(1, ch_dmg_raw - tg_def)

        # Aplica dano alvo
        tg_cur_hp -= ch_dmg

        # Efeitos especiais do atacante
        if ch_skill.get("self_heal"):
            heal = ch_skill["self_heal"]
            ch_cur_hp = min(ch_hp, ch_cur_hp + heal)

        # Efeitos no alvo
        stun_tg = False
        if random.random() < ch_skill.get("stun_chance", 0):
            stun_tg = True
        if ch_skill.get("poison"):
            tg_poison = True
        if ch_skill.get("weaken"):
            tg_weakened = True

        # Log do ataque
        ch_hp_bar = "❤️" * max(1, int(ch_cur_hp / ch_hp * 5)) + "🖤" * (5 - max(1, int(ch_cur_hp / ch_hp * 5)))
        tg_hp_bar = "❤️" * max(1, int(max(0, tg_cur_hp) / tg_hp * 5)) + "🖤" * (5 - max(1, int(max(0, tg_cur_hp) / tg_hp * 5)))

        ch_action = f"{ch_icon} **{ch_name}** usa {ch_skill_name}!\n💥 `−{ch_dmg} HP` para {tg_name}\n{ch_skill['desc']}"
        if stun_tg:
            ch_action += f"\n⚡ **{tg_name} foi paralisado!**"
        if ch_skill.get("poison") and tg_poison:
            ch_action += f"\n☠️ **{tg_name} foi envenenado!**"
        if ch_skill.get("self_heal"):
            ch_action += f"\n💚 **{ch_name} se curou em {ch_skill['self_heal']} HP!**"

        turn_embed.add_field(name=f"🔴 Ação de {ch_name}", value=ch_action, inline=False)

        if tg_cur_hp <= 0:
            turn_embed.add_field(
                name="💀 BATALHA ENCERRADA!",
                value=f"**{tg_name}** não aguenta mais!",
                inline=False
            )
            await channel.send(embed=turn_embed)
            break

        # Veneno do alvo
        if tg_poison:
            poison_dmg = max(5, int(tg_hp * 0.05))
            tg_cur_hp -= poison_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{tg_name}** sofre `{poison_dmg}` de veneno!", inline=False)
            if tg_cur_hp <= 0:
                await channel.send(embed=turn_embed)
                break

        # === Ação do Alvo (se não stunado) ===
        if not stun_tg:
            available_tg = [s for s in tg_skills if s["mana_cost"] <= tg_cur_mana]
            if not available_tg:
                available_tg = [tg_skills[0]]
            tg_skill = random.choice(available_tg)
            tg_cur_mana = max(0, tg_cur_mana - tg_skill["mana_cost"])

            tg_dmg_raw = int(tg_atk_base * tg_skill["dmg_mult"])
            if tg_weakened:
                tg_dmg_raw = int(tg_dmg_raw * 0.7)
            if random.random() < tg_skill.get("crit_chance", 0.1):
                tg_dmg_raw = int(tg_dmg_raw * 1.8)
                tg_skill_name = f"💥 CRÍTICO! {tg_skill['name']}"
            else:
                tg_skill_name = tg_skill["name"]

            if tg_skill.get("ignore_def"):
                tg_dmg = max(1, tg_dmg_raw)
            else:
                tg_dmg = max(1, tg_dmg_raw - ch_def)

            ch_cur_hp -= tg_dmg

            if tg_skill.get("self_heal"):
                tg_cur_hp = min(tg_hp, tg_cur_hp + tg_skill["self_heal"])
            if tg_skill.get("poison"):
                ch_poison = True
            if tg_skill.get("weaken"):
                ch_weakened = True
            stun_ch = random.random() < tg_skill.get("stun_chance", 0)

            tg_action = f"{tg_icon} **{tg_name}** usa {tg_skill_name}!\n💥 `−{tg_dmg} HP` para {ch_name}\n{tg_skill['desc']}"
            if stun_ch:
                tg_action += f"\n⚡ **{ch_name} foi paralisado!**"
            if tg_skill.get("poison") and ch_poison:
                tg_action += f"\n☠️ **{ch_name} foi envenenado!**"
            if tg_skill.get("self_heal"):
                tg_action += f"\n💚 **{tg_name} se curou em {tg_skill['self_heal']} HP!**"

            turn_embed.add_field(name=f"🔵 Ação de {tg_name}", value=tg_action, inline=False)
        else:
            turn_embed.add_field(name=f"⚡ {tg_name} estava paralisado!", value="Perdeu o turno!", inline=False)

        # Veneno do challenger
        if ch_poison:
            p_dmg = max(5, int(ch_hp * 0.05))
            ch_cur_hp -= p_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{ch_name}** sofre `{p_dmg}` de veneno!", inline=False)

        # HP bars no final do turno
        ch_pct = max(0, int(ch_cur_hp / ch_hp * 100))
        tg_pct = max(0, int(tg_cur_hp / tg_hp * 100))
        ch_bar = "🟥" * (ch_pct // 20) + "⬛" * (5 - ch_pct // 20)
        tg_bar = "🟦" * (tg_pct // 20) + "⬛" * (5 - tg_pct // 20)

        turn_embed.add_field(
            name="📊 Status",
            value=f"{ch_icon} **{ch_name}**: {ch_bar} `{max(0, ch_cur_hp)}/{ch_hp} HP` | 💙 `{ch_cur_mana}` mana\n"
                  f"{tg_icon} **{tg_name}**: {tg_bar} `{max(0, tg_cur_hp)}/{tg_hp} HP` | 💙 `{tg_cur_mana}` mana",
            inline=False
        )

        await channel.send(embed=turn_embed)
        await asyncio.sleep(2)
        turn += 1

    # Determina vencedor
    await asyncio.sleep(1)
    result_embed = discord.Embed(
        title="🏆 RESULTADO DO DUELO!",
        color=discord.Color.gold()
    )

    if ch_cur_hp <= 0 and tg_cur_hp <= 0:
        winner_id = None
        result_embed.description = f"*'Ambos caem simultaneamente!'*\n\n**EMPATE ÉPICO!**"
        result_embed.color = discord.Color.orange()
    elif ch_cur_hp <= 0:
        winner_id = target_id
        loser_id = challenger_id
        result_embed.description = f"*O narrador anuncia:*\n\n'**{tg_name}** vence o duelo com maestria!'"
        result_embed.color = discord.Color.blue()
        xp_win = 150 + target["level"] * 5
        add_xp(target_id, xp_win)
        result_embed.add_field(name=f"🏆 {tg_name} (Vencedor)", value=f"+{xp_win} XP | +1 Vitória PvP", inline=True)
        result_embed.add_field(name=f"💀 {ch_name} (Derrotado)", value="Melhor sorte na próxima!", inline=True)
    elif tg_cur_hp <= 0:
        winner_id = challenger_id
        loser_id = target_id
        result_embed.description = f"*O narrador anuncia:*\n\n'**{ch_name}** vence o duelo gloriosamente!'"
        result_embed.color = discord.Color.red()
        xp_win = 150 + challenger["level"] * 5
        add_xp(challenger_id, xp_win)
        result_embed.add_field(name=f"🏆 {ch_name} (Vencedor)", value=f"+{xp_win} XP | +1 Vitória PvP", inline=True)
        result_embed.add_field(name=f"💀 {tg_name} (Derrotado)", value="Melhor sorte na próxima!", inline=True)
    else:
        # Decidido por HP restante
        if ch_cur_hp >= tg_cur_hp:
            winner_id = challenger_id
            result_embed.description = f"*'Tempo esgotado! **{ch_name}** tinha mais HP!'*\n\n**{ch_name} vence por resistência!**"
            xp_win = 80 + challenger["level"] * 3
            add_xp(challenger_id, xp_win)
            result_embed.add_field(name=f"🏆 {ch_name}", value=f"+{xp_win} XP", inline=True)
            result_embed.add_field(name=f"⚔️ {tg_name}", value=f"HP restante: {max(0, tg_cur_hp)}", inline=True)
        else:
            winner_id = target_id
            result_embed.description = f"*'Tempo esgotado! **{tg_name}** tinha mais HP!'*\n\n**{tg_name} vence por resistência!**"
            xp_win = 80 + target["level"] * 3
            add_xp(target_id, xp_win)
            result_embed.add_field(name=f"🏆 {tg_name}", value=f"+{xp_win} XP", inline=True)
            result_embed.add_field(name=f"⚔️ {ch_name}", value=f"HP restante: {max(0, ch_cur_hp)}", inline=True)

    result_embed.add_field(
        name="📜 Narrador Final",
        value=random.choice([
            "*'Uma batalha que será lembrada por gerações!'*",
            "*'O sangue de guerreiros corre nessas veias!'*",
            "*'Que honra testemunhar tamanha bravura!'*",
            "*'Os deuses assistiram esta batalha com interesse!'*",
            "*'Lendas nacem de combates como este!'*",
        ]),
        inline=False
    )
    await channel.send(embed=result_embed)


# ================= FUNÇÕES DE BATALHA E EXPLORAÇÃO =================

async def fight_boss(channel, user_id, is_dungeon=False, dungeon_boss=None, allies=None):
    """Batalha de boss estilo Pokémon — turno a turno usando habilidades de classe"""
    player = get_player(user_id)

    if is_dungeon and dungeon_boss:
        boss_data = dungeon_boss
    else:
        effects = player.get("active_effects", {})
        pending_boss = effects.pop("pending_boss", None)
        player["active_effects"] = effects
        save_player_db(user_id, player)

        boss_gate_levels = {9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 199}

        if pending_boss:
            boss_data = pending_boss
        elif player["level"] in boss_gate_levels:
            # Segurança: força o boss de level correto mesmo sem pending_boss
            boss_data = get_level_boss(player["level"])
            if not boss_data or boss_data["name"] in player.get("bosses", []):
                world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
                boss_pool = WORLD_BOSSES_VARIANTS.get(world_level, [])
                boss_data = random.choice(boss_pool) if boss_pool else WORLDS[world_level]["boss"]
        else:
            world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
            boss_pool = WORLD_BOSSES_VARIANTS.get(world_level, [])
            boss_data = random.choice(boss_pool) if boss_pool else WORLDS[world_level]["boss"]

    # ---- Player stats ----
    p_cls = player.get("class", "Guerreiro")
    p_skills = get_player_skills(player)
    p_icon = CLASSES.get(p_cls, {}).get("emoji", "⚔️")

    p_max_hp = player["max_hp"] + player.get("temp_hp_boost", 0)
    p_hp = min(player["hp"], p_max_hp)
    p_mana = calc_max_mana(player)
    p_cur_mana = p_mana

    p_atk = CLASSES.get(p_cls, {}).get("atk_bonus", 5) + player["level"] * 2 + player.get("temp_atk_boost", 0)
    p_def = CLASSES.get(p_cls, {}).get("def_bonus", 3) + player["level"] + player.get("temp_def_boost", 0)

    # Item bonuses
    if player.get("weapon"):
        for w in ITEMS["weapons"]:
            if w["name"] == player["weapon"]:
                p_atk += w.get("atk", 0) // 4
                break
    if player.get("armor"):
        for a in ITEMS["armor"]:
            if a["name"] == player["armor"]:
                p_def += a.get("def", 0) // 4
                break
    if player.get("pet"):
        try:
            pet_name = player["pet"] if isinstance(player["pet"], str) else player["pet"].get("name", "")
            # Find pet in PETS and PETS_EXTRA data
            all_pet_worlds = list(PETS.values()) + list(PETS_EXTRA.values())
            for world_pets in all_pet_worlds:
                for p in world_pets:
                    if p["name"] == pet_name:
                        p_atk += p.get("bonus_atk", 0)
                        break
        except:
            pass
    # Also add small bonus from farm pets (max 3 farm pets contribute)
    pets_list = player.get("pets_list", [])
    farm_bonus = sum(p.get("bonus_atk", 0) // 3 for p in pets_list[:3])
    p_atk += farm_bonus

    # Ally bonus
    ally_bonus_atk = 0
    ally_names = []
    if allies:
        num_allies = len([a for a in allies if str(a) != str(user_id)])
        for ally_id in allies:
            if str(ally_id) != str(user_id):
                ally_p = get_player(ally_id)
                if ally_p:
                    ally_bonus_atk += ally_p["level"]
                    try:
                        au = await bot.fetch_user(int(ally_id))
                        ally_names.append(au.display_name)
                    except:
                        pass
        # Boss escala com o número de aliados (cada aliado adiciona 20% ao HP e ATK do boss)
        if num_allies > 0:
            scale_factor = 1.0 + (num_allies * 0.20)
            boss_data = dict(boss_data)  # cópia para não modificar o original
            boss_data["hp"] = int(boss_data["hp"] * scale_factor)
            boss_data["atk"] = int(boss_data["atk"] * scale_factor)
    p_atk += ally_bonus_atk // 2

    # ---- Exército do reino participa automaticamente do boss ----
    army_bonus_atk = 0
    army_bonus_desc = None
    kingdom_data = player.get("kingdom_data")
    if kingdom_data:
        army_level = kingdom_data.get("army", "Neutra")
        army_buffs = {
            "Ruim":     {"bonus": 5,   "desc": "⚔️ Recrutas mal-treinados ajudam como podem (+5 ATK)"},
            "Neutra":   {"bonus": 15,  "desc": "⚔️ Soldados do seu reino entram na batalha! (+15 ATK)"},
            "Boa":      {"bonus": 35,  "desc": "⚔️ Tropas de elite marcham ao seu lado! (+35 ATK)"},
            "Excelente":{"bonus": 70,  "desc": "⚔️ Exército lendário ataca com fúria devastadora! (+70 ATK)"},
        }
        buff = army_buffs.get(army_level)
        if buff:
            army_bonus_atk = buff["bonus"]
            army_bonus_desc = buff["desc"]
            p_atk += army_bonus_atk
    # ---- Pet combat bonus (pet entra automaticamente junto) ----
    pet_combat_name = None
    pet_combat_emoji = "🐾"
    pet_combat_hp = 0
    pet_combat_atk = 0
    if player.get("pet"):
        try:
            pet_name = player["pet"] if isinstance(player["pet"], str) else player["pet"].get("name", "")
            all_pet_worlds = list(PETS.values()) + list(PETS_EXTRA.values())
            for world_pets in all_pet_worlds:
                for p in world_pets:
                    if p["name"] == pet_name:
                        pet_combat_name = pet_name
                        pet_combat_emoji = p.get("emoji", "🐾")
                        pet_combat_hp = p.get("bonus_hp", 10)
                        pet_combat_atk = p.get("bonus_atk", 3)
                        break
        except:
            pass

    # ---- Montaria bonus (se tiver montaria ativa, adiciona DEF) ----
    mount_bonus_def = 0
    mount_name = player.get("mount")
    if mount_name:
        mount_data = get_pet_mount_data(mount_name)
        if mount_data:
            mount_bonus_def = mount_data.get("mount_bonus_def", 0)
            p_def += mount_bonus_def
    boss_hp = boss_data["hp"]
    boss_atk = boss_data["atk"]

    # Bosses de level são MUITO mais difíceis
    # Todos os bosses de level (níveis 9, 19, 29... 199)
    level_boss_names = set()
    boss_level_map = {9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
                      109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190}
    for wk in boss_level_map.values():
        if wk in WORLDS:
            level_boss_names.add(WORLDS[wk]["boss"]["name"])
        else:
            nearest = max((k for k in WORLDS.keys() if k <= wk), default=1)
            level_boss_names.add(WORLDS[nearest]["boss"]["name"])
    is_level_boss = boss_data["name"] in level_boss_names
    if is_level_boss:
        pass  # stats ja ajustados diretamente nos dados do boss

    boss_skills = BOSS_SKILLS.get(boss_data["name"], BOSS_SKILLS["default"])
    boss_cur_hp = boss_hp
    boss_poison = False
    boss_weakened = False

    try:
        player_user = await bot.fetch_user(int(user_id))
        p_name = player_user.display_name
    except:
        p_name = "Herói"

    # ---- Intro embed ----
    intro = discord.Embed(
        title=f"👹 BATALHA ÉPICA — {p_name} vs {boss_data['name']}",
        description=f"*'O narrador anuncia com voz trovejante: A batalha começa agora!'*",
        color=discord.Color.dark_red()
    )
    if is_level_boss:
        intro.add_field(name="🚨 BOSS DE NÍVEL", value="*Este boss é o guardião da passagem — mais forte e resistente!*", inline=False)
    if ally_names:
        intro.add_field(name="👥 Aliados", value=", ".join(ally_names), inline=False)
    if army_bonus_desc:
        intro.add_field(name="🏰 Exército do Reino", value=army_bonus_desc, inline=False)
    intro.add_field(
        name=f"{p_icon} {p_name} ({p_cls})",
        value=f"❤️ HP: `{p_hp}/{p_max_hp}` | ✨ Mana: `{p_cur_mana}`\n⚔️ ATK: `{p_atk}` | 🛡️ DEF: `{p_def}`",
        inline=True
    )
    if pet_combat_name:
        intro.add_field(
            name=f"{pet_combat_emoji} {pet_combat_name} (Pet)",
            value=f"❤️ HP: `{pet_combat_hp}` | ⚔️ ATK: `{pet_combat_atk}`\n*Seu fiel companheiro entra na batalha!*",
            inline=True
        )
    if mount_name and mount_bonus_def > 0:
        intro.add_field(
            name=f"🐎 Montaria: {mount_name}",
            value=f"🛡️ DEF Bônus: `+{mount_bonus_def}`\n*Sua montaria te protege na batalha!*",
            inline=True
        )
    intro.add_field(
        name=f"👹 {boss_data['name']}",
        value=f"❤️ HP: `{boss_cur_hp:,}` | ⚔️ ATK: `{boss_atk}`\n_{boss_data.get('desc','')[:60]}_",
        inline=True
    )
    await channel.send(embed=intro)
    await asyncio.sleep(2)

    # ---- Turn-based combat ----
    p_cur_hp = p_hp
    p_poison = False
    p_weakened = False
    p_stunned = False
    crits_done = 0
    poisons_done = 0
    stuns_done = 0
    skills_used = set()
    was_poisoned = False
    was_stunned = False
    pet_cur_hp = pet_combat_hp  # pet HP tracking

    for turn in range(1, 9):
        if p_cur_hp <= 0 or boss_cur_hp <= 0:
            break

        turn_embed = discord.Embed(title=f"⚔️ TURNO {turn}", color=discord.Color.red())

        # === Player action ===
        available = [s for s in p_skills if s["mana_cost"] <= p_cur_mana]
        if not available:
            available = [p_skills[0]]
        p_skill = random.choice(available)
        p_cur_mana = max(0, p_cur_mana - p_skill["mana_cost"])
        skills_used.add(p_skill["name"])

        dmg_raw = int(p_atk * p_skill["dmg_mult"])
        if p_weakened:
            dmg_raw = int(dmg_raw * 0.7)

        is_crit = random.random() < p_skill.get("crit_chance", 0.1)
        if is_crit:
            dmg_raw = int(dmg_raw * 1.8)
            crits_done += 1
            skill_display = f"💥 CRÍTICO! {p_skill['name']}"
        else:
            skill_display = p_skill["name"]

        if p_skill.get("ignore_def"):
            p_dmg = max(1, dmg_raw)
        else:
            boss_def = max(0, boss_atk // 4)  # boss tem alguma defesa
            p_dmg = max(1, dmg_raw - boss_def)

        boss_cur_hp -= p_dmg

        if p_skill.get("self_heal"):
            p_cur_hp = min(p_max_hp, p_cur_hp + p_skill["self_heal"])

        boss_stun = random.random() < p_skill.get("stun_chance", 0)
        if p_skill.get("poison"):
            boss_poison = True
            poisons_done += 1
        if p_skill.get("weaken"):
            boss_weakened = True

        p_action = f"{p_icon} **{p_name}** usa **{skill_display}**!\n💥 `−{p_dmg:,} HP` para {boss_data['name']}\n_{p_skill['desc']}_"
        if boss_stun:
            p_action += "\n⚡ **O boss foi paralisado!**"
            stuns_done += 1
        if p_skill.get("self_heal"):
            p_action += f"\n💚 **{p_name} recuperou {p_skill['self_heal']} HP!**"
        turn_embed.add_field(name=f"🔴 Você ataca!", value=p_action, inline=False)

        # === Pet attack ===
        if pet_combat_name and pet_cur_hp > 0:
            pet_dmg = max(1, pet_combat_atk + random.randint(0, pet_combat_atk // 2))
            boss_cur_hp -= pet_dmg
            # Pet de suporte (Fada) pode curar
            pet_heal = 0
            if "Fada" in pet_combat_name or "Coelho" in pet_combat_name:
                pet_heal = random.randint(5, 15)
                p_cur_hp = min(p_max_hp, p_cur_hp + pet_heal)
            pet_msg = f"{pet_combat_emoji} **{pet_combat_name}** ataca! `−{pet_dmg}` HP"
            if pet_heal:
                pet_msg += f" | 💚 Cura `+{pet_heal}` HP"
            turn_embed.add_field(name="🐾 Pet ataca!", value=pet_msg, inline=False)

        if boss_cur_hp <= 0:
            turn_embed.add_field(name="💥 BOSS DESTRUÍDO!", value=f"**{boss_data['name']}** foi derrotado!", inline=False)
            await channel.send(embed=turn_embed)
            break

        # Boss poison
        if boss_poison:
            boss_poison_dmg = max(10, int(boss_hp * 0.04))
            boss_cur_hp -= boss_poison_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{boss_data['name']}** sofre `{boss_poison_dmg}` de veneno!", inline=False)
            if boss_cur_hp <= 0:
                await channel.send(embed=turn_embed)
                break

        # === Boss action (if not stunned) ===
        if not boss_stun:
            b_skill = random.choice(boss_skills)
            b_dmg_raw = int(boss_atk * b_skill["dmg_mult"])
            if boss_weakened:
                b_dmg_raw = int(b_dmg_raw * 0.6)

            if random.random() < 0.1:
                b_dmg_raw = int(b_dmg_raw * 1.5)
                b_skill_name = f"💥 CRÍTICO! {b_skill['name']}"
            else:
                b_skill_name = b_skill["name"]

            b_dmg = max(1, b_dmg_raw - p_def)
            p_cur_hp -= b_dmg

            if b_skill.get("poison"):
                p_poison = True
                was_poisoned = True
            if b_skill.get("weaken"):
                p_weakened = True
            b_stun = random.random() < b_skill.get("stun_chance", 0)
            if b_stun:
                p_stunned = True
                was_stunned = True

            b_action = f"👹 **{boss_data['name']}** usa **{b_skill_name}**!\n💥 `−{b_dmg}` de dano!\n_{b_skill['desc']}_"
            if b_stun:
                b_action += f"\n⚡ **{p_name} foi paralisado no próximo turno!**"
            if b_skill.get("poison"):
                b_action += f"\n☠️ **{p_name} foi envenenado!**"
            turn_embed.add_field(name=f"🔵 Boss ataca!", value=b_action, inline=False)
        else:
            turn_embed.add_field(name=f"⚡ Boss paralisado!", value="O boss perdeu o turno!", inline=False)

        # Player poison
        if p_poison:
            p_poison_dmg = max(5, int(p_max_hp * 0.04))
            p_cur_hp -= p_poison_dmg
            turn_embed.add_field(name="☠️ Veneno!", value=f"**{p_name}** sofre `{p_poison_dmg}` de veneno!", inline=False)

        # HP bars
        p_pct = max(0, int(p_cur_hp / p_max_hp * 100))
        b_pct = max(0, int(boss_cur_hp / boss_hp * 100))
        p_bar = "🟥" * (p_pct // 20) + "⬛" * (5 - p_pct // 20)
        b_bar = "🟦" * (b_pct // 20) + "⬛" * (5 - b_pct // 20)

        turn_embed.add_field(
            name="📊 Status",
            value=f"{p_icon} **{p_name}**: {p_bar} `{max(0,p_cur_hp)}/{p_max_hp}` ❤️ | 💙 `{p_cur_mana}` mana\n"
                  f"👹 **{boss_data['name']}**: {b_bar} `{max(0,boss_cur_hp):,}/{boss_hp:,}` ❤️",
            inline=False
        )
        await channel.send(embed=turn_embed)
        await asyncio.sleep(2)

    # ---- Battle result ----
    await asyncio.sleep(1)

    if p_cur_hp <= 0 or (boss_cur_hp > 0 and p_cur_hp <= 0):
        # === DERROTA ===
        result, xp_loss = remove_xp(user_id, random.randint(80, 150))
        defeat_embed = discord.Embed(
            title="💀 DERROTA...",
            description=f"*'{boss_data['name']} permanece de pé enquanto você cai...'*\n\n❌ **−{xp_loss} XP**",
            color=discord.Color.dark_red()
        )
        defeat_embed.add_field(
            name="💡 O que fazer agora?",
            value="• **Vingança** — Enfrente o mesmo boss imediatamente\n• **Treinamento** — Fortaleça seus stats antes da revanche\n• **Recuar** — Recolha suas forças",
            inline=False
        )
        await channel.send(embed=defeat_embed)
        # Show revenge/training buttons for level bosses
        boss_levels_set = {"Slime Rei", "Ent Ancião", "Faraó Amaldiçoado", "Yeti Colossal", "Dragão de Magma", "Senhor das Sombras"}
        if boss_data["name"] in boss_levels_set or player.get("level") in [9,19,29,39,49,59]:
            view = RevengeTrainingView(user_id, boss_data)
            await channel.send("**O que você deseja fazer?**", view=view)
        return

    # === VITÓRIA ===
    xp = boss_data["xp"] + (player["level"] * 10)
    coins = random.randint(boss_data["coins"][0], boss_data["coins"][1])

    player2 = get_player(user_id)
    if boss_data["name"] not in player2["bosses"]:
        player2["bosses"].append(boss_data["name"])
    player2["bosses_defeated"] = player2.get("bosses_defeated", 0) + 1
    player2["total_coins_earned"] = player2.get("total_coins_earned", 0) + coins
    player2["total_xp_earned"] = player2.get("total_xp_earned", 0) + xp
    # Check for revenge achievement
    effects2 = player2.get("active_effects", {})
    was_revenge = effects2.pop("used_revenge", False)
    player2["active_effects"] = effects2
    save_player_db(user_id, player2)

    leveled = add_xp(user_id, xp, bypass_boss_gate=True)

    # Libera XP acumulado durante o bloqueio do boss
    pending_released = release_pending_xp(user_id)

    # === RECOMPENSA PARA ALIADOS (boss de nível) ===
    if is_level_boss and allies:
        boss_to_world_ally = {}
        boss_level_map_ally = {9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
                               109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190}
        for gate_lvl, wk in boss_level_map_ally.items():
            nearest = wk if wk in WORLDS else max((k for k in WORLDS.keys() if k <= wk), default=1)
            boss_to_world_ally[WORLDS[nearest]["boss"]["name"]] = nearest
        next_world_ally = boss_to_world_ally.get(boss_data["name"])
        ally_xp = boss_data["xp"] // 2  # aliados recebem metade do XP
        ally_coins = coins // 2

        for ally_id in allies:
            if str(ally_id) == str(user_id):
                continue
            ap = get_player(ally_id)
            if not ap:
                continue

            # Registra o boss como derrotado para o aliado
            if boss_data["name"] not in ap.get("bosses", []):
                ap["bosses"].append(boss_data["name"])
            ap["bosses_defeated"] = ap.get("bosses_defeated", 0) + 1
            ap["total_coins_earned"] = ap.get("total_coins_earned", 0) + ally_coins
            ap["total_xp_earned"] = ap.get("total_xp_earned", 0) + ally_xp

            # Desbloqueia o próximo mundo para o aliado
            if next_world_ally and next_world_ally in WORLDS:
                if next_world_ally not in ap.get("worlds", [1]):
                    ap["worlds"].append(next_world_ally)
                    ap["worlds"] = sorted(list(set(ap["worlds"])))

            save_player_db(ally_id, ap)

            # Libera XP bloqueado do aliado e dá XP + coins da batalha
            add_xp(ally_id, ally_xp, bypass_boss_gate=True)
            release_pending_xp(ally_id)
            add_coins(ally_id, ally_coins)

            # Drop próprio para cada aliado
            ally_drop_rand = random.random()
            ally_drop_rarity = None
            if ally_drop_rand < 0.002:
                ally_drop_rarity = random.choice(["Divino", "Primordial"])
            elif ally_drop_rand < 0.015:
                ally_drop_rarity = "Mítico"
            elif ally_drop_rand < 0.05:
                ally_drop_rarity = "Lendário"
            elif ally_drop_rand < 0.14:
                ally_drop_rarity = "Épico"
            elif ally_drop_rand < 0.28:
                ally_drop_rarity = "Raro"

            # Notifica o aliado
            try:
                ally_user = await bot.fetch_user(int(ally_id))
                ally_after = get_player(ally_id)
                ally_embed = discord.Embed(
                    title="🤝 ALIADO — BOSS DERROTADO!",
                    description=f"Você ajudou a derrotar **{boss_data['name']}**!\n*'Sua participação na batalha foi decisiva!'*",
                    color=discord.Color.gold()
                )
                ally_embed.add_field(name="⭐ XP Ganho", value=f"`+{ally_xp:,}`", inline=True)
                ally_embed.add_field(name="💰 Coins Ganhos", value=f"`+{ally_coins:,}`", inline=True)
                if next_world_ally and next_world_ally in WORLDS:
                    nw = WORLDS[next_world_ally]
                    ally_embed.add_field(
                        name=f"🌍 Reino Desbloqueado!",
                        value=f"{nw['emoji']} **{nw['name']}** agora está acessível!\nUse `abrir mapa` para viajar.",
                        inline=False
                    )
                if ally_drop_rarity:
                    item_type_ally = random.choice(["weapon", "armor"])
                    item_list_ally = "weapons" if item_type_ally == "weapon" else "armor"
                    items_of_rarity_ally = [i for i in ITEMS[item_list_ally] if i["rarity"] == ally_drop_rarity]
                    if items_of_rarity_ally:
                        item_ally = random.choice(items_of_rarity_ally)
                        ap2 = get_player(ally_id)
                        ap2["inventory"].append(item_ally["name"])
                        save_player_db(ally_id, ap2)
                        ally_embed.add_field(
                            name=f"✨ Drop Especial para você!",
                            value=f"{RARITIES[ally_drop_rarity]['emoji']} **{item_ally['name']}** ({ally_drop_rarity})",
                            inline=False
                        )
                ally_embed.set_footer(text=f"Aliado de {p_name} na batalha contra {boss_data['name']}")
                await channel.send(f"{ally_user.mention}", embed=ally_embed)
            except:
                pass

    add_coins(user_id, coins)

    victory_embed = discord.Embed(
        title="🏆 VITÓRIA GLORIOSA!",
        description=f"*'{boss_data['name']} cai derrotado! A lenda de {p_name} cresce!'*\n\n⭐ **+{xp:,} XP** | 💰 **+{coins:,} CSI**",
        color=discord.Color.gold()
    )
    if pending_released > 0:
        victory_embed.add_field(
            name="🔓 XP Bloqueado Liberado!",
            value=f"*O XP acumulado durante o bloqueio foi liberado!*\n⭐ **+{pending_released:,} XP bônus**",
            inline=False
        )

    if leveled:
        p_after = get_player(user_id)
        victory_embed.add_field(name="🆙 Level Up!", value=f"*Você chegou ao **Nível {p_after['level']}**!*", inline=False)

    # Unlock next world for level bosses + AUTO-TRAVEL
    boss_to_world = {}
    _boss_level_map = {9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
                       109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190}
    for _gate_lvl, _wk in _boss_level_map.items():
        _nearest = _wk if _wk in WORLDS else max((k for k in WORLDS.keys() if k <= _wk), default=1)
        _boss_name = WORLDS[_nearest]["boss"]["name"]
        # Map this boss to the NEXT world (one tier up)
        _all_world_keys = sorted(WORLDS.keys())
        _idx = _all_world_keys.index(_nearest) if _nearest in _all_world_keys else -1
        if _idx >= 0 and _idx + 1 < len(_all_world_keys):
            boss_to_world[_boss_name] = _all_world_keys[_idx + 1]
    next_world = boss_to_world.get(boss_data["name"])
    # Segurança: se boss_data tinha nome errado, checar pelos bosses derrotados
    if not next_world:
        p_check = get_player(user_id)
        for b_name, w_key in boss_to_world.items():
            if b_name in p_check.get("bosses", []) and w_key not in p_check.get("worlds", [1]) and w_key in WORLDS:
                next_world = w_key
                break
    if next_world and next_world in WORLDS:
        p3 = get_player(user_id)
        if next_world not in p3["worlds"]:
            p3["worlds"].append(next_world)
            # AUTO-TRAVEL: move player to new world (muda mundo atual)
            # Garante que o novo mundo está na lista e marca como mundo atual
            p3["worlds"] = sorted(list(set(p3["worlds"])))
            save_player_db(user_id, p3)
            new_world_data = WORLDS[next_world]
            victory_embed.add_field(
                name=f"🌍 REINO DESBLOQUEADO & VIAGEM AUTOMÁTICA!",
                value=f"{new_world_data['emoji']} **{new_world_data['name']}** agora está acessível!\n\n"
                      f"*'As correntes se rompem! As névoas se dissipam!'*\n"
                      f"**Você foi automaticamente transportado para o novo reino!**\n"
                      f"*Para voltar, use `abrir mapa` e viaje manualmente.*",
                inline=False
            )
            await channel.send(embed=victory_embed)
            await asyncio.sleep(2)
            # Enviar embed de chegada ao novo mundo
            arrival_embed = discord.Embed(
                title=f"{new_world_data['emoji']} BEM-VINDO: {new_world_data['name']}!",
                description=f"*'{random.choice(new_world_data.get('events', ['Você chega a um novo reino...']))}'*\n\n"
                            f"Um novo horizonte se abre diante de você! Este reino trará novos desafios, criaturas e segredos.\n\n"
                            f"Use `explorar` para começar sua aventura aqui.\nUse `abrir mapa` para voltar ao reino anterior.",
                color=discord.Color.gold()
            )
            arrival_embed.set_footer(text=f"Reino: {new_world_data['name']} | Use 'abrir mapa' para navegar entre reinos")
            await channel.send(embed=arrival_embed)
            # Drop + achievements after this return
            return

    # Item drop — boss é a ÚNICA fonte de Mítico+
    # Bosses de level têm chance maior de drops raros
    drop_rarity = None
    # Boss especial de dungeon secreta GARANTE drop da raridade definida
    if boss_data.get("is_secret_boss") and boss_data.get("special_drop_rarity"):
        _min_rarity = boss_data["special_drop_rarity"]
        _rarity_order = ["Mítico", "Ancestral", "Divino", "Primordial"]
        _min_idx = _rarity_order.index(_min_rarity) if _min_rarity in _rarity_order else 0
        _rarity_pool = _rarity_order[_min_idx:]
        _weights = [50, 30, 20, 10][:len(_rarity_pool)]
        drop_rarity = random.choices(_rarity_pool, weights=_weights)[0]
    else:
        rand = random.random()
        if is_level_boss:
            # Boss de level: chances maiores
            if rand < 0.002:    # 0.2% Divino/Primordial
                drop_rarity = random.choice(["Divino", "Primordial"])
            elif rand < 0.015:  # 1.5% Mítico
                drop_rarity = "Mítico"
            elif rand < 0.05:   # 5% Lendário
                drop_rarity = "Lendário"
            elif rand < 0.14:   # 9% Épico
                drop_rarity = "Épico"
            elif rand < 0.28:   # 14% Raro
                drop_rarity = "Raro"
        else:
            # Boss comum: chances menores em Mítico+
            if rand < 0.0003:   # 0.03% Divino/Primordial
                drop_rarity = random.choice(["Divino", "Primordial"])
            elif rand < 0.002:  # 0.2% Mítico
                drop_rarity = "Mítico"
            elif rand < 0.015:  # 1.5% Lendário
                drop_rarity = "Lendário"
            elif rand < 0.05:   # 5% Épico
                drop_rarity = "Épico"
            elif rand < 0.11:   # 6% Raro
                drop_rarity = "Raro"

    if drop_rarity:
        item_type = random.choice(["weapon", "armor"])
        item_list = "weapons" if item_type == "weapon" else "armor"
        items_of_rarity = [i for i in ITEMS[item_list] if i["rarity"] == drop_rarity]
        if items_of_rarity:
            item = random.choice(items_of_rarity)
            victory_embed.add_field(
                name=f"{'🌟' if drop_rarity in ['Divino','Primordial'] else '✨'} Drop Especial!",
                value=f"{RARITIES[drop_rarity]['emoji']} **{item['name']}** ({drop_rarity}) caiu do boss!\n*'Os deuses sorriem para você!'*",
                inline=False
            )
            await channel.send(embed=victory_embed)
            view = EquipButton(user_id, item["name"], item_type)
            await channel.send(f"⚔️ **{item['name']}** brilha em suas mãos! Deseja equipar?", view=view)

            # Achievements for drops
            if drop_rarity in ["Divino", "Primordial"]:
                await check_achievements(channel, user_id, "divine_drop")
            elif drop_rarity == "Lendário":
                await check_achievements(channel, user_id, "legendary_drop")

            p4 = get_player(user_id)
            p4["inventory"].append(item["name"])
            save_player_db(user_id, p4)
        else:
            await channel.send(embed=victory_embed)
    else:
        # Potion drop
        if random.random() < 0.15:
            pot_rarities = ["Raro", "Épico"]
            pot_weights = [70, 30]
            chosen_rarity = random.choices(pot_rarities, weights=pot_weights)[0]
            pots = [name for name, data in POTIONS.items() if data["rarity"] == chosen_rarity]
            if pots:
                dropped_pot = random.choice(pots)
                p4 = get_player(user_id)
                p4["inventory"].append(dropped_pot)
                save_player_db(user_id, p4)
                victory_embed.add_field(name="🧪 Poção Encontrada!", value=f"{RARITIES[chosen_rarity]['emoji']} **{dropped_pot}** adicionado ao inventário!", inline=False)
        await channel.send(embed=victory_embed)

    # Check achievements
    await check_achievements(channel, user_id)
    if was_revenge:
        await check_achievements(channel, user_id, "comeback_win")
    if p_cur_hp >= int(p_max_hp * 0.8):
        await check_achievements(channel, user_id, "boss_no_damage")
    if not was_poisoned and not was_stunned:
        await check_achievements(channel, user_id, "perfect_boss_fight")
    if boss_data["name"] == "Slime Rei":
        await check_achievements(channel, user_id, "boss_slime_rei")
    if boss_data["name"] == "Dragão de Magma":
        await check_achievements(channel, user_id, "boss_dragao")
    if boss_data["name"] == "Senhor das Sombras":
        await check_achievements(channel, user_id, "boss_sombras")
    # Check level boss
    p_bosses_beaten = player2.get("bosses", [])
    if len(p_bosses_beaten) >= 1:
        await check_achievements(channel, user_id, "level_boss_1")
    level_bosses_names = {"Slime Rei", "Ent Ancião", "Faraó Amaldiçoado", "Yeti Colossal", "Dragão de Magma", "Senhor das Sombras"}
    p3_final = get_player(user_id)
    if all(b in p3_final.get("bosses", []) for b in level_bosses_names):
        await check_achievements(channel, user_id, "all_level_bosses")
    # World unlocks
    worlds_count = len(p3_final.get("worlds", [1]))
    if worlds_count >= 2:
        await check_achievements(channel, user_id, "world_2")
    if worlds_count >= 3:
        await check_achievements(channel, user_id, "world_3")
    if worlds_count >= 4:
        await check_achievements(channel, user_id, "world_4")
    if worlds_count >= 5:
        await check_achievements(channel, user_id, "world_5")
    if len(WORLDS) <= worlds_count:
        await check_achievements(channel, user_id, "all_worlds")

    # ── Check class evolution after boss fight (levels 40/80/120/160) ──
    p_evo = get_player(user_id)
    effects_evo = p_evo.get("active_effects", {})
    if effects_evo.pop("check_evolution", False):
        p_evo["active_effects"] = effects_evo
        save_player_db(user_id, p_evo)
        await check_class_evolution(channel, user_id)

    # ── Check supreme skill unlock (boss-specific) ──
    cls = p_evo.get("class")
    if cls and cls in CLASS_TIERED_SKILLS:
        supreme = CLASS_TIERED_SKILLS[cls].get("supreme")
        if supreme:
            unlock_boss = supreme.get("unlock_boss", "")
            if boss_data["name"] == unlock_boss:
                supreme_skills = p_evo.get("supreme_skills", [])
                if supreme["name"] not in supreme_skills:
                    supreme_skills.append(supreme["name"])
                    p_evo["supreme_skills"] = supreme_skills
                    save_player_db(user_id, p_evo)
                    unlock_embed = discord.Embed(
                        title="👑 HABILIDADE SUPREMA DESBLOQUEADA!",
                        description=(
                            f"**{supreme['name']}**\n\n"
                            f"*{supreme['desc']}*\n\n"
                            f"Derrotou **{unlock_boss}** e dominou o poder supremo da sua classe!"
                        ),
                        color=discord.Color.from_rgb(255, 215, 0)
                    )
                    unlock_embed.add_field(name="💥 Dano", value=f"{supreme['dmg_mult']}x", inline=True)
                    unlock_embed.add_field(name="🔵 Mana", value=f"{supreme['mana_cost']}", inline=True)
                    await channel.send(embed=unlock_embed)


async def explore_dungeon(channel, user_id, dungeon, world):
    player = get_player(user_id)
    roll = roll_with_bonus(player)
    luck = get_luck(roll)
    is_secret = dungeon.get("secret", False)
    level_mult = get_dungeon_difficulty_multiplier(player)  # mais difícil por nível

    SECRET_EVENTS = [
        "🌑 *As paredes sangram símbolos antigos...*",
        "👁️ *Mil olhos te observam das trevas...*",
        "🌀 *A realidade distorce ao seu redor...*",
        "⚡ *Energia arcana pulsa sob seus pés...*",
        "🔮 *Vozes sussurram segredos proibidos...*",
    ]

    flavor = random.choice(SECRET_EVENTS) if is_secret else "*A dungeon é escura e úmida... Você sente perigo em cada sombra.*"

    embed = discord.Embed(
        title=f"{'🔮 MASMORRA SECRETA:' if is_secret else '🏛️'} {dungeon['name']}",
        description=flavor,
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="🎲 Dado da Exploração", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

    if is_secret:
        embed.set_footer(text=f"⚔️ Masmorra Secreta — Dificuldade ×{level_mult:.1f} | Recompensas ×{level_mult:.1f}")

    if roll == 1:
        dmg = int(random.randint(40, 70) * (level_mult if is_secret else 1))
        player["hp"] -= dmg
        if player["hp"] <= 0:
            player["hp"] = player["max_hp"] // 3
        save_player_db(user_id, player)
        xp_loss_base = random.randint(150, 250) if is_secret else random.randint(100, 150)
        xp_loss_total = int(xp_loss_base * level_mult)
        result, xp_loss = remove_xp(user_id, xp_loss_total)

        trap_msgs = [
            "Uma armadilha de cristal explode ao seu toque! Fragmentos cortam por todo lado!",
            "Garras gigantes surgem do chão! Você é lançado contra a parede!",
            "O teto desaba em blocos de pedra mágica! Esmagamento inevitável!",
            "Um campo arcano eletrifica tudo ao redor! Você convulsiona de dor!",
        ] if is_secret else ["Uma armadilha antiga é ativada! Lâminas surgem de todas as direções!"]

        embed.add_field(
            name="💀 ARMADILHA MORTAL!",
            value=f"*'{random.choice(trap_msgs)}'*\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
            inline=False
        )
        embed.color = discord.Color.dark_red()

    elif roll <= 3:
        xp_loss_base = random.randint(80, 120) if is_secret else random.randint(50, 80)
        xp_loss_total = int(xp_loss_base * (level_mult if is_secret else 1))
        result, xp_loss = remove_xp(user_id, xp_loss_total)
        if is_secret:
            msgs = [
                "Entidades do vazio bloqueiam seu caminho e drenam sua energia!",
                "Um labirinto dimensional te faz andar em círculos por horas!",
                "A masmorra te estuda. Você sai mais fraco do que entrou.",
            ]
            embed.add_field(
                name="☠️ Pesadelo Dimensional",
                value=f"*'{random.choice(msgs)}'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
        else:
            embed.add_field(
                name="☠️ Exploração Perigosa",
                value=f"*'Você se perde nos corredores sombrios...'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
        embed.color = discord.Color.red()

    elif roll <= 5:
        resources = random.sample(world["resources"], min(3 if is_secret else 2, len(world["resources"])))
        for r in resources:
            player["inventory"].append(r)
        save_player_db(user_id, player)
        items_text = "\n".join([f"• **{r}**" for r in resources])
        xp_bonus = int(random.randint(100, 200) * (level_mult if is_secret else 1))
        add_xp(user_id, xp_bonus)
        embed.add_field(
            name="📦 Câmara de Recursos",
            value=f"*'Uma câmara intocada há séculos...'*\n\n{items_text}\n⭐ **+{xp_bonus} XP**", inline=False
        )
        embed.color = discord.Color.blue()

    elif roll <= 7:
        xp_base = random.randint(500, 900) if is_secret else random.randint(80, 150)
        coins_base = random.randint(20, 50) if is_secret else random.randint(10, 25)
        xp = int(xp_base * level_mult)
        coins = int(coins_base * level_mult)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        key_dropped = None
        potion_dropped = None

        if random.random() < (0.50 if is_secret else 0.25):
            potion_list = list(POTIONS.keys())
            potion_dropped = random.choice(potion_list[-5:] if is_secret else potion_list)
            player = get_player(user_id)
            player["inventory"].append(potion_dropped)
            save_player_db(user_id, player)

        # ─── DROP DE CHAVE EM DUNGEON COMUM (1 a cada 5 dungeons ou 8% de sorte) ──
        if not is_secret:
            player_for_key = get_player(user_id)
            dungeons_done = player_for_key.get("dungeons_completed", 0) + 1
            player_for_key["dungeons_completed"] = dungeons_done
            save_player_db(user_id, player_for_key)
            key_by_count = (dungeons_done % 5 == 0)   # garantido a cada 5 dungeons
            key_by_luck  = random.random() < DUNGEON_KEY_DROP_CHANCE  # 8%
            if key_by_count or key_by_luck:
                # Tenta pegar secret_dungeons do mundo atual; se não tiver, busca qualquer mundo
                secret_dungeons = world.get("secret_dungeons", [])
                if not secret_dungeons:
                    for w_data in WORLDS.values():
                        sds = w_data.get("secret_dungeons", [])
                        if sds:
                            secret_dungeons = sds
                            break
                if secret_dungeons:
                    chosen_sd = random.choice(secret_dungeons)
                    key_name = chosen_sd.get("key_name", "")
                    if not key_name:
                        key_name = chosen_sd.get("name", "Chave Misteriosa") + " — Chave"
                    if key_name:
                        player = get_player(user_id)
                        player["inventory"].append(key_name)
                        save_player_db(user_id, player)
                        key_dropped = key_name
                else:
                    # Fallback: drop de chave genérica se nenhum mundo tiver secret_dungeons
                    key_name = "Chave da Dungeon Secreta"
                    player = get_player(user_id)
                    player["inventory"].append(key_name)
                    save_player_db(user_id, player)
                    key_dropped = key_name

        chest_bonus = ""
        if potion_dropped:
            chest_bonus += f"\n🧪 **{potion_dropped}** dropada!"
        if key_dropped:
            chest_bonus += f"\n🗝️ **{key_dropped}** encontrada no baú! *(Use para entrar na dungeon secreta!)*"
            # Mensagem dramática de chave
            key_msgs = [
                f"*'Um brilho estranho emana do corpo caído do boss... Uma chave cai ao chão com um tinido!'*",
                f"*'Nas entranhas do monstro, algo metálico brilha. Uma chave... mas para onde ela abre?'*",
                f"*'O boss se dissolve em sombras, deixando para trás uma chave enferrujada de origem desconhecida...'*",
                f"*'Uau, achou uma chave! Sla pra que serve isso... mas parece importante. Muito importante.'*",
                f"*'Uma chave surge do nada entre os escombros. Alguém claramente não queria que você a encontrasse.'*",
            ]
            await asyncio.sleep(1)
            key_embed = discord.Embed(
                title="🗝️ CHAVE ENCONTRADA!",
                description=random.choice(key_msgs) + f"\n\n🔑 Você obteve: **{key_dropped}**\n\n*Esta chave abre uma dungeon secreta desta região! Use `ver chaves` para gerenciar suas chaves.*",
                color=discord.Color.from_rgb(255, 200, 0)
            )
            key_embed.set_footer(text="Use 'dungeon' e encontre a dungeon secreta para usar esta chave!")
            await channel.send(embed=key_embed)

        embed.add_field(
            name="💎 Câmara do Tesouro!",
            value=f"*'{'Um tesouro ancestral brilha com luz própria!' if is_secret else 'Você encontra um baú antigo cheio de riquezas!'}'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{chest_bonus}",
            inline=False
        )
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        embed.color = discord.Color.green()

    elif roll <= 9:
        item_type = random.choice(["weapon", "armor"])
        item_list = "weapons" if item_type == "weapon" else "armor"
        if is_secret:
            # Usa raridade mínima definida na dungeon, ou Mítico por padrão
            min_rarity = dungeon.get("special_boss_drop", "Mítico")
            rarity_order = ["Mítico", "Ancestral", "Divino", "Primordial"]
            min_idx = rarity_order.index(min_rarity) if min_rarity in rarity_order else 0
            rarity_pool = rarity_order[min_idx:]
            # Pesos decrescentes
            all_weights = [50, 30, 25, 15]
            weights = all_weights[min_idx:min_idx + len(rarity_pool)]
            if not weights:
                rarity_pool = ["Mítico", "Ancestral", "Divino", "Primordial"]
                weights = [50, 30, 25, 15]
        else:
            rarity_pool = ["Raro", "Épico", "Lendário"]
            weights = [40, 40, 20]
        rarity = random.choices(rarity_pool, weights=weights)[0]
        items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
        item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])

        xp_base = random.randint(800, 1500) if is_secret else random.randint(120, 200)
        coins_base = random.randint(30, 80) if is_secret else random.randint(15, 35)
        xp = int(xp_base * level_mult)
        coins = int(coins_base * level_mult)
        leveled = add_xp(user_id, xp)
        add_coins(user_id, coins)

        rarity_info = RARITIES[item["rarity"]]
        embed.add_field(
            name=f"{'🌟 ITEM LENDÁRIO DA MASMORRA!' if is_secret else '✨ Equipamento Raro!'}",
            value=f"*'{'Um artefato que não deveria existir...' if is_secret else 'Em uma sala secreta, você encontra um equipamento magnífico!'}'*\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**",
            inline=False
        )
        if leveled:
            player = get_player(user_id)
            embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
        embed.color = rarity_info["color"]

        await channel.send(embed=embed)
        await asyncio.sleep(1)
        view = EquipButton(user_id, item["name"], item_type)
        await channel.send(f"✨ **{item['name']}** aguarda por você!\n\n*'Deseja equipar?'*", view=view)
        return

    else:  # roll == 10
        if is_secret:
            boss_power_msgs = [
                "👁️ *Uma entidade primordial abre os olhos. Ela existia antes do tempo.*",
                "🌑 *O guardião final da masmorra desperta. Você sentiu isso vindo.*",
                "💀 *Morte personificada bloqueia a câmara central. Não há fuga.*",
            ]
            embed.add_field(
                name="👹 GUARDIÃO FINAL DA MASMORRA SECRETA!",
                value=f"{random.choice(boss_power_msgs)}\n\n**{dungeon['boss']}** surge das sombras com poder incompreensível!",
                inline=False
            )
        else:
            embed.add_field(
                name="👹 O BOSS APARECE!",
                value=f"*'No fim da dungeon, uma presença maligna surge!\n\n**{dungeon['boss']}** bloqueia seu caminho!'*",
                inline=False
            )
        embed.color = discord.Color.dark_red()
        await channel.send(embed=embed)
        await asyncio.sleep(2)

        # Boss de dungeon secreta é MUITO mais forte
        if is_secret:
            special_drop_rarity = dungeon.get("special_boss_drop", "Mítico")
            boss_data = {
                "name": dungeon["boss"],
                "hp": int((800 + dungeon["level"] * 150) * level_mult),
                "atk": int((60 + dungeon["level"] * 10) * level_mult),
                "xp": int((2000 + dungeon["level"] * 300) * level_mult),
                "coins": (int((60 + dungeon["level"] * 8) * level_mult), int((150 + dungeon["level"] * 15) * level_mult)),
                "special_drop_rarity": special_drop_rarity,  # Boss especial garante drop desta raridade
                "is_secret_boss": True
            }
        else:
            boss_data = {
                "name": dungeon["boss"],
                "hp": 200 + (dungeon["level"] * 50),
                "atk": 20 + (dungeon["level"] * 3),
                "xp": 150 + (dungeon["level"] * 40),
                "coins": (10 + dungeon["level"] * 2, 25 + dungeon["level"] * 4)
            }
        await fight_boss(channel, user_id, is_dungeon=True, dungeon_boss=boss_data)
        return

    await channel.send(embed=embed)

# ================= TAREFAS PERIÓDICAS =================

@tasks.loop(minutes=20)
async def random_world_events():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CANAL_BETA)
        if not channel:
            continue

        event_type = random.choice(["structure", "narrator", "merchant", "pet", "book"])

        if event_type == "structure":
            structure = random.choice(STRUCTURES)
            embed = discord.Embed(
                title=f"{structure['name']} Avistada!",
                description=f"*'{structure['narrator']}'*",
                color=discord.Color.purple()
            )
            embed.add_field(name="📍 Descrição", value=structure["description"], inline=False)
            await channel.send(embed=embed)

        elif event_type == "narrator":
            warning = random.choice(NARRATOR_WARNINGS)
            try:
                members = [m for m in guild.members if not m.bot]
                if members:
                    random_member = random.choice(members)
                    embed = discord.Embed(
                        title="📖 O Narrador Fala",
                        description=f"*Uma voz ecoa direcionada a {random_member.mention}...*\n\n**\"{warning}\"**",
                        color=discord.Color.dark_gold()
                    )
                    await channel.send(embed=embed)
            except:
                pass

        elif event_type == "merchant":
            items_for_sale = []
            weapon = random.choice([i for i in ITEMS["weapons"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            weapon_price = {"Incomum": 300, "Raro": 900, "Épico": 2000}[weapon["rarity"]]
            items_for_sale.append({"name": weapon["name"], "type": "weapon", "price": weapon_price})

            armor = random.choice([i for i in ITEMS["armor"] if i["rarity"] in ["Incomum", "Raro", "Épico"]])
            armor_price = {"Incomum": 300, "Raro": 900, "Épico": 2000}[armor["rarity"]]
            items_for_sale.append({"name": armor["name"], "type": "armor", "price": armor_price})

            items_for_sale.append({"name": "Poção de Vida", "type": "potion", "price": 150})

            embed = discord.Embed(
                title="🏪 Mercador Errante Apareceu!",
                description="*'Um mercador misterioso surge do nada oferecendo seus produtos...'*",
                color=discord.Color.gold()
            )
            for i, item in enumerate(items_for_sale, 1):
                embed.add_field(name=f"Item {i}: {item['name']}", value=f"💰 **Preço: {item['price']} CSI**", inline=False)

            await channel.send(embed=embed, view=ShopButton(None, items_for_sale))

        elif event_type == "pet":
            world_levels = list(PETS.keys())
            chosen_world = random.choice(world_levels)
            pet = random.choice(PETS[chosen_world])
            embed = discord.Embed(
                title=f"{pet['emoji']} Criatura Selvagem Apareceu!",
                description=f"*'Um **{pet['name']}** selvagem aparece no horizonte!'*",
                color=RARITIES[pet["rarity"]]["color"]
            )
            embed.add_field(name="✨ Raridade", value=f"{RARITIES[pet['rarity']]['emoji']} {pet['rarity']}", inline=True)
            embed.add_field(name="💪 Bônus ATK", value=f"+{pet['bonus_atk']}", inline=True)
            embed.add_field(name="❤️ Bônus HP", value=f"+{pet['bonus_hp']}", inline=True)
            embed.set_footer(text="Use 'domesticar' para tentar capturá-lo!")
            await channel.send(embed=embed)

        elif event_type == "book":
            # Livro de lore aleatório aparece
            world_key = random.choice(list(LORE_BOOKS.keys()))
            book = random.choice(LORE_BOOKS[world_key])
            embed = discord.Embed(
                title=f"📚 Um Livro Antigo Foi Encontrado!",
                description=f"*'As páginas se abrem sozinhas...'*",
                color=discord.Color.dark_gold()
            )
            embed.add_field(name=book["title"], value=book["content"][:1024], inline=False)
            await channel.send(embed=embed)


# ================= PRÓLOGO =================
async def send_prologue(guild):
    channel = discord.utils.get(guild.text_channels, name=CANAL_BETA)
    if not channel:
        return

    await asyncio.sleep(1)

    # ══════════════════════════════════════════
    # EMBED 1 — Abertura épica do narrador
    # ══════════════════════════════════════════
    embed1 = discord.Embed(
        title="📖  W O R L D   C S I  📖",
        description=(
            "```\n"
            "╔══════════════════════════════════════╗\n"
            "║   O Narrador Desperta...             ║\n"
            "║   Uma Nova Saga Começa Aqui.         ║\n"
            "╚══════════════════════════════════════╝\n"
            "```\n"
            "*Uma voz grave ecoa por todo o servidor...*\n\n"
            "**\"No princípio, havia apenas o Vazio — um silêncio perfeito e eterno.**\n"
            "Então, a Primeira Chama surgiu do nada, e com ela nasceu o Mundo.\n\n"
            "Vinte reinos se formaram das cinzas da criação.\n"
            "Cada um guarda segredos que poucos ousam descobrir.\n"
            "Cada um testa aqueles que o atravessam de formas diferentes.\n\n"
            "**Você... é o próximo herói desta história.**\n"
            "Ou talvez o próximo vilão. O destino é seu para escrever.\"\n\n"
            "*— O Narrador, antes que a história comece*"
        ),
        color=0x2C2F33
    )
    embed1.set_footer(text="🎭 O Narrador observa cada passo seu...")
    await channel.send(embed=embed1)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 2 — Os Sete Reinos (lore)
    # ══════════════════════════════════════════
    embed2 = discord.Embed(
        title="🗺️ Os Vinte Reinos do Mundo",
        description="*O pergaminho se desenrola revelando terras que poucos mortais conhecem...*",
        color=0x8B4513
    )
    embed2.add_field(
        name="🌱 Campos Iniciais — O Berço",
        value=(
            "*\"Todo herói começa aqui. Não existe vergonha no começo humilde.\n"
            "O guerreiro mais poderoso que existiu começou matando um slime.\"*\n"
            "— Historiador Pell\n\n"
            "Terras abertas onde os primeiros seres vivos deram seus primeiros passos.\n"
            "O Slime Rei reina sobre estas planícies... por enquanto."
        ),
        inline=False
    )
    embed2.add_field(
        name="🌲 Floresta Sombria — A Que Respira",
        value=(
            "*\"A floresta não é apenas árvores. Ela é um ser vivo, consciente,\n"
            "e muito, muito antiga. Ela ouve você. E lembra de tudo.\"*\n"
            "— Druida Sylvara\n\n"
            "O Ent Ancião de 3.000 anos guarda segredos que nenhum livro registrou.\n"
            "Os sussurros entre os galhos contam histórias do tempo dos dragões."
        ),
        inline=False
    )
    embed2.add_field(
        name="🏜️ Deserto das Almas — O Jardim Perdido",
        value=(
            "*\"Esta areia foi mar profundo uma vez. Sob ela ainda dormem\n"
            "as maravilhas do jardim original — esperando um digno.\"*\n"
            "— Sábia Nefertiri\n\n"
            "O Faraó Kha-Mentu foi traído por seus sacerdotes e amaldiçoado\n"
            "para guardar seus próprios tesouros por toda a eternidade."
        ),
        inline=False
    )
    await channel.send(embed=embed2)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 3 — Os Reinos Clássicos (além dos 3 iniciais)
    # ══════════════════════════════════════════
    embed3 = discord.Embed(
        title="🗺️ Os Reinos Além",
        description="*...o pergaminho continua se desenrolando...*",
        color=0x4B0082
    )
    embed3.add_field(
        name="❄️ Montanhas Geladas — O Grito dos Titãs",
        value=(
            "*\"Vivi 80 invernos nestas montanhas. O frio não é inimigo — é professor.\n"
            "O Yeti não é um monstro. É um guardião mal compreendido.\"*\n"
            "— Ancião Bjorn\n\n"
            "Os Titãs do Gelo criaram o Cristal do Inverno Eterno — um arquivo\n"
            "de tudo que já morreu no frio. O Yeti Colossal sente cada memória."
        ),
        inline=False
    )
    embed3.add_field(
        name="🌋 Reino Vulcânico — Onde o Fogo Pensa",
        value=(
            "*\"O fogo não destrói. Transforma. Os Forjadores sabiam disso —\n"
            "por isso criaram armas que tinham alma.\"*\n"
            "— Profeta Ignar\n\n"
            "Ignarius, o Dragão de Magma, é o segundo elemento.\n"
            "Dentro dele vivem as memórias de uma civilização inteira."
        ),
        inline=False
    )
    embed3.add_field(
        name="🌌 Abismo Arcano — O Antes e o Depois",
        value=(
            "*\"Quanto mais você sabe, mais entende que não sabe nada.\n"
            "As entidades do Vazio não são más. São antigas demais.\"*\n"
            "— Arquimago Zephyr\n\n"
            "Cada alma que nasce vem do Abismo. Cada alma que morre, retorna.\n"
            "O Senhor das Sombras administra esse trânsito eterno."
        ),
        inline=False
    )
    embed3.add_field(
        name="👑 Trono Celestial — O Teste Final",
        value=(
            "*\"O Imperador Astral não é um inimigo — é o último teste.\n"
            "O Trono não é um lugar. É um estado de ser.\"*\n"
            "— Guardião Estelar Auron\n\n"
            "Aquele que chegar aqui não será mais mortal.\n"
            "A história foi escrita. Apenas você decide como ela termina."
        ),
        inline=False
    )
    await channel.send(embed=embed3)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 3B — Os 13 Novos Reinos (Expansão)
    # ══════════════════════════════════════════
    embed3b = discord.Embed(
        title="🌌 A Expansão — Treze Reinos Ocultos",
        description=(
            "*O pergaminho se rasga revelando um segundo mapa, costurado por trás do primeiro...*\n\n"
            "*\"Acreditávamos que o Trono Celestial era o fim. Estávamos errados.\n"
            "Havia mais. Havia sempre mais.\"*\n"
            "— Última anotação do Explorador Maren, desaparecido após o Trono"
        ),
        color=0x0a0a2e
    )
    embed3b.add_field(
        name="🌿 Pântano das Almas Perdidas — O Limbo Vivo",
        value=(
            "*\"Neste pântano as almas não vão embora. Ficam presas na lama,\n"
            "ainda tentando lembrar quem foram. A Hidra se alimenta dessas memórias.\"*\n"
            "— Xamã Morrek\n\n"
            "Um reino entre a vida e a morte, onde a lama guarda segredos de civilizações submersas."
        ),
        inline=False
    )
    embed3b.add_field(
        name="💎 Floresta Cristalina — O Espelho do Mundo",
        value=(
            "*\"Cada cristal aqui reflete uma versão diferente de você. A maioria\n"
            "das versões não sobreviveu. Aprenda com elas.\"*\n"
            "— Guardião Vitreo\n\n"
            "Árvores de quartzo e diamante que guardam reflexos do passado e do futuro."
        ),
        inline=False
    )
    embed3b.add_field(
        name="🌑 Reino das Sombras Eternas — A Noite que Pensa",
        value=(
            "*\"A escuridão aqui não é ausência de luz. É uma presença.\n"
            "E ela sabe seu nome desde antes de você nascer.\"*\n"
            "— Espectro do Explorador Anônimo\n\n"
            "Onde os Lichs ancestrais governam e toda sombra tem consciência própria."
        ),
        inline=False
    )
    embed3b.add_field(
        name="⚡ Planícies do Trovão — A Ira do Céu",
        value=(
            "*\"Zeus Menor não é um deus caído. É um deus em treinamento.\n"
            "E ele treina em cima de você.\"*\n"
            "— Sobrevivente das Planícies (único registrado)\n\n"
            "Planícies eternas onde relâmpagos são criaturas vivas e o céu nunca para de gritar."
        ),
        inline=False
    )
    await channel.send(embed=embed3b)
    await asyncio.sleep(2)

    embed3c = discord.Embed(
        title="🌌 A Expansão — Os Reinos do Abismo",
        description="*...a escrita no segundo pergaminho fica cada vez mais perturbadora...*",
        color=0x0d0d0d
    )
    embed3c.add_field(
        name="🗿 Terra dos Gigantes — Onde o Chão Respira",
        value=(
            "*\"As montanhas que você escala são costas de gigantes dormindo.\n"
            "Se eles acordarem ao mesmo tempo, não haverá terra suficiente.\"*\n"
            "— Anão Geólogo Durgin\n\n"
            "O Primeiro Gigante Primordial ainda carrega no corpo cicatrizes de batalhas\n"
            "que antecederam o universo atual."
        ),
        inline=False
    )
    embed3c.add_field(
        name="🌊 Mar das Almas — O Oceano que Devora o Tempo",
        value=(
            "*\"Cada onda neste mar carrega o último pensamento de alguém que se afogou.\n"
            "O Leviatã não ataca. Ele coleciona.\"*\n"
            "— Capitão Spectros, navegando há 400 anos sem envelhecer\n\n"
            "Um oceano onde o tempo não flui normalmente e cidades afundadas ainda têm habitantes."
        ),
        inline=False
    )
    embed3c.add_field(
        name="🌀 Reino do Caos — A Antítese da Existência",
        value=(
            "*\"Aqui as leis da física são sugestões. A gravidade é uma opinião.\n"
            "Paradoxos caminham como pessoas. E O Caos em Pessoa te observa.\"*\n"
            "— Registro ilegível de um explorador sem nome\n\n"
            "O único reino onde a realidade em si é o inimigo."
        ),
        inline=False
    )
    embed3c.add_field(
        name="🌸 Jardim dos Deuses — O Paraíso Armado",
        value=(
            "*\"Bonito demais para ser seguro. Cada flor é uma armadilha.\n"
            "Cada fruto é um teste. E o Jardineiro Divino não perdoa os que colhem sem permissão.\"*\n"
            "— Anjo Desertor\n\n"
            "Um paraíso literal — mas os deuses não deixaram portão destrancado."
        ),
        inline=False
    )
    await channel.send(embed=embed3c)
    await asyncio.sleep(2)

    embed3d = discord.Embed(
        title="🌌 A Expansão — Os Reinos Além da Compreensão",
        description="*...as últimas páginas do segundo pergaminho parecem escritas com algo que não é tinta...*",
        color=0x000011
    )
    embed3d.add_field(
        name="🧊 Reino do Gelo Eterno — O Inverno que Sempre Foi",
        value=(
            "*\"Não é frio. É a temperatura da ausência. É como seria o universo\n"
            "se nenhuma estrela tivesse nascido. A Imperadora lembra disso.\"*\n"
            "— Dragão de Gelo Ancião, em sonho\n\n"
            "O frio aqui antecede o próprio universo. A Imperadora do Gelo Eterno existia antes da luz."
        ),
        inline=False
    )
    embed3d.add_field(
        name="🏛️ Ruínas da Civilização Perdida — O Que Viemos Depois",
        value=(
            "*\"Eles tinham tecnologia que nós chamamos de magia.\n"
            "Tinham magia que nós chamamos de impossível.\n"
            "E ainda assim morreram. Algo os matou.\"*\n"
            "— Construto Arcano, em loop de memória\n\n"
            "Uma civilização tão avançada que criou autômatos que sobreviveram ao fim deles mesmos."
        ),
        inline=False
    )
    embed3d.add_field(
        name="✨ Plano Astral — O Espaço Entre os Pensamentos",
        value=(
            "*\"Você não viaja para o Plano Astral. Você percebe que já estava nele,\n"
            "o tempo todo, e só agora abriu os olhos.\"*\n"
            "— Ser Astral Sem Nome\n\n"
            "Onde o cosmos tem consciência e cada estrela é uma memória de um deus morto."
        ),
        inline=False
    )
    embed3d.add_field(
        name="🌌 Além da Existência — O Fim da Pergunta",
        value=(
            "*\"Não existe descrição. A linguagem não alcança.\n"
            "Tudo que posso dizer é: você vai entender quando chegar.\n"
            "E vai querer não ter chegado. E vai querer não ter voltado.\"*\n"
            "— Único explorador que retornou, incapaz de falar desde então\n\n"
            "O penúltimo reino. Aqui a existência questiona a si mesma."
        ),
        inline=False
    )
    embed3d.add_field(
        name="⭐ O Trono Primordial — O Começo do Fim",
        value=(
            "*\"O Criador Primordial não é um boss. É uma resposta.\n"
            "A pergunta é: você merece saber?\"*\n"
            "— Inscrição gravada na entrada do Trono Primordial\n\n"
            "O vigésimo e último reino. Chegar aqui significa ter atravessado tudo.\n"
            "O Criador Primordial espera. Ele sempre esperou. Ele sabia que você viria."
        ),
        inline=False
    )
    embed3d.set_footer(text="⚠️ Os 13 novos reinos são desbloqueados ao derrotar o Boss do Trono Celestial.")
    await channel.send(embed=embed3d)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 4 — Lore: A Guerra Primordial
    # ══════════════════════════════════════════
    embed4 = discord.Embed(
        title="📜 Crônicas da Guerra Primordial",
        description=(
            "*Um livro antigo se abre sozinho nas páginas proibidas...*\n\n"
            "**'O Que Existia Antes do Tempo'**\n\n"
            "Antes que o universo existisse, houve uma guerra.\n\n"
            "De um lado: a **Luz Primordial**, que queria existência, forma, vida.\n"
            "Do outro: o **Vazio Eterno**, que queria silêncio, paz, nada.\n\n"
            "Eles lutaram por uma eternidade que não tinha nome ainda.\n"
            "A batalha terminou sem vencedor — ambos exaustos, fizeram um acordo:\n"
            "criariam algo novo. Algo que contivesse os dois.\n\n"
            "Chamaram isso de ***Universo***.\n\n"
            "E plantaram dentro de cada ser vivo uma centelha de cada lado.\n"
            "*É por isso que todo ser carrega tanto amor quanto destruição.*\n\n"
            "**A guerra não terminou. Apenas mudou de palco.**\n\n"
            "*— Fragmento encontrado no 'Além do Trono', autor desconhecido*"
        ),
        color=0x1a0033
    )
    embed4.set_footer(text="📚 Lore desbloqueável: explore o mundo para encontrar mais fragmentos.")
    await channel.send(embed=embed4)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 5 — Sistema de Alinhamento
    # ══════════════════════════════════════════
    embed5 = discord.Embed(
        title="⚖️ O Peso das Escolhas",
        description=(
            "*O Narrador observa você com olhos que viram mil histórias...*\n\n"
            "**Neste mundo, suas ações têm consequências morais.**\n\n"
            "Salvar uma cidade ou saqueá-la.\n"
            "Ajudar um viajante ou roubá-lo.\n"
            "Proteger os inocentes ou usá-los como escudo.\n\n"
            "Cada escolha molda quem você é:"
        ),
        color=0x9B59B6
    )
    embed5.add_field(
        name="✨ Herói (+30 pontos ou mais)",
        value="*'Sua luz guia aqueles que estão perdidos.'*\nAcesso a missões de proteção, recompensas divinas e respeito do povo.",
        inline=False
    )
    embed5.add_field(
        name="⚖️ Anti-Herói (-5 a -29 pontos)",
        value="*'Você faz o bem pelos motivos errados... ou o errado pelos motivos certos.'*\nMissões de moral cinza com recompensas únicas.",
        inline=False
    )
    embed5.add_field(
        name="💀 Vilão (-30 pontos ou menos)",
        value="*'O poder não se pede. Se toma.'*\nMissões de conquista e destruição com XP massivo — e consequências.",
        inline=False
    )
    embed5.add_field(
        name="🎭 Como funciona",
        value="Use `cenário` para enfrentar dilemas morais!\nUse `alinhamento` para ver seu estado atual.",
        inline=False
    )
    await channel.send(embed=embed5)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 6 — Empregos e Títulos
    # ══════════════════════════════════════════
    embed6 = discord.Embed(
        title="💼 Empregos & Títulos do Reino",
        description=(
            "*O taberneiro pregou uma lista de oportunidades na parede...*\n\n"
            "**A partir do nível 5**, você pode trabalhar e ganhar salário!\n"
            "Cada emprego tem benefícios únicos que afetam sua jornada."
        ),
        color=0xE67E22
    )
    embed6.add_field(name="⚒️ Ferreiro (Nv.5)", value="Forja armas únicas, 20% desc. em lojas", inline=True)
    embed6.add_field(name="🔮 Arcano (Nv.5)", value="+15 mana máx, acesso a grimórios", inline=True)
    embed6.add_field(name="💚 Curandeiro (Nv.5)", value="Cura aliados, poções 30% mais baratas", inline=True)
    embed6.add_field(name="💰 Mercador (Nv.5)", value="Vende 25% a mais, mercado negro", inline=True)
    embed6.add_field(name="📜 Escriba (Nv.5)", value="Descobre locais 2× mais rápido", inline=True)
    embed6.add_field(name="⚔️ Cavaleiro (Nv.10)", value="+20 HP, defende cidades de invasões", inline=True)
    embed6.add_field(name="🛡️ Guarda Real (Nv.15)", value="+35 HP, comanda a guarda do reino", inline=True)
    embed6.add_field(name="👑 Rei (Nv.30)", value="Governa, nomeia cavaleiros, recebe tributo", inline=True)
    embed6.add_field(
        name="📣 Como começar",
        value="`procurar emprego` → escolha sua profissão → `trabalhar` a cada 30 min!",
        inline=False
    )
    await channel.send(embed=embed6)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # EMBED 7 — Comandos completos
    # ══════════════════════════════════════════
    embed7 = discord.Embed(
        title="⚔️ Guia Completo de Comandos",
        description="*Tudo que você precisa para conquistar o mundo:*",
        color=0x3498DB
    )
    embed7.add_field(
        name="🌍 Exploração & Caça",
        value="`explorar` | `caçar` | `coletar` | `minerar` | `dungeon`",
        inline=False
    )
    embed7.add_field(
        name="👹 Boss & Combate",
        value="`encontrar boss` — boss do reino atual\n`desafiar boss` — enfrente o boss (level boss se nível 9/19/29/39/49/59)\n`juntar boss` | `iniciar batalha boss` | `desafiar @jogador`",
        inline=False
    )
    embed7.add_field(
        name="💪 Treinamento (após derrota em boss)",
        value="`treinar força` — +ATK\n`treinar defesa` — +DEF\n`treinar vitalidade` — +HP Máx\n`treinar intensivo` — +ATK+DEF+HP",
        inline=False
    )
    embed7.add_field(
        name="🏆 Conquistas",
        value="`ver conquistas` — veja todas as 100 conquistas e seu progresso",
        inline=False
    )
    embed7.add_field(
        name="📋 Quests & Moral",
        value="`ver quests` | `realizar quest` | `finalizar quest` | `cenário` | `missão moral` | `alinhamento`",
        inline=False
    )
    embed7.add_field(
        name="👤 Personagem",
        value="`ver perfil` | `inventário` | `escolher raça` | `evoluir raça` | `escolher classe` | `habilidades` | `evolução classe` | `ver mana`",
        inline=False
    )
    embed7.add_field(
        name="🐾 Pets & Fazenda",
        value="`fazenda` | `trocar pet` | `guardar pet` | `procurar pet` | `domesticar`",
        inline=False
    )
    embed7.add_field(
        name="💼 Empregos & Títulos",
        value="`procurar emprego` | `trabalhar` | `largar emprego` | `me tornar rei` | `defender cidade`",
        inline=False
    )
    embed7.add_field(
        name="🗺️ Mapa & Viagem",
        value="`abrir mapa` | `viajar <local>` | `procurar cidade`",
        inline=False
    )
    embed7.add_field(
        name="🏰 Social & Guilda",
        value="`criar guilda` | `entrar guilda` | `ver guilda` | `trocar [item] com @user`",
        inline=False
    )
    embed7.add_field(
        name="🛒 Itens & Economia",
        value="`usar [poção]` | `vender [item]` | `equipar [item]` | `trocar coins <valor>` | `minerar baú`",
        inline=False
    )
    embed7.add_field(
        name="📚 Info & Lore",
        value="`comandos` — ver esta lista | `falar npc especial` | `abrir livro`",
        inline=False
    )
    embed7.set_footer(text="🌟 \"E assim, uma nova história começa...\" — O Narrador | Use 'comandos' para ver esta lista a qualquer momento!")
    await channel.send(embed=embed7)
    await asyncio.sleep(1)

    # ══════════════════════════════════════════
    # EMBED NOTA DE ATUALIZAÇÃO — O que há de novo
    # ══════════════════════════════════════════
    embed_update = discord.Embed(
        title="📋 Nota de Atualização — Expansão dos Reinos",
        description=(
            "*O Narrador desdobra um pergaminho oficial com o selo do Conselho do Mundo...*\n\n"
            "**\"Uma era de descobertas começou. O mundo é maior do que pensávamos.\"**"
        ),
        color=0x2ECC71
    )
    embed_update.add_field(
        name="🗺️ 13 Novos Reinos Desbloqueados",
        value=(
            "O mundo expandiu de **7 para 20 reinos**!\n"
            "Cada reino tem cidade, NPCs, lore, monstros, dungeons e boss únicos.\n"
            "Desbloqueie novos reinos derrotando o Boss do reino atual."
        ),
        inline=False
    )
    embed_update.add_field(
        name="🗝️ Sistema de Chaves — Dungeons Secretas",
        value=(
            "Dungeons secretas agora exigem uma **Chave específica** para entrar.\n"
            "• Explore **dungeons comuns** → encontre **baús** → chance de dropar chaves\n"
            "• Use `dungeon` para ver a dungeon comum e a **Dungeon Misteriosa** do seu reino\n"
            "• Use `chaves` para ver suas chaves atuais\n"
            "• Dungeons secretas têm inimigos muito mais fortes e drops **Míticos ou superiores**"
        ),
        inline=False
    )
    embed_update.add_field(
        name="🟠 Nova Raridade: Ancestral",
        value=(
            "Uma nova raridade foi adicionada entre Mítico 🔴 e Divino 💎:\n"
            "**🟠 Ancestral** — Armas e armaduras de eras esquecidas.\n"
            "Obtenível via bosses especiais de dungeons secretas nos novos reinos."
        ),
        inline=False
    )
    embed_update.add_field(
        name="👹 Bosses Especiais de Dungeon Secreta",
        value=(
            "Cada dungeon secreta tem um **Boss Especial Exclusivo** muito mais poderoso.\n"
            "Derrotar esse boss é a **única forma** de obter recompensas Míticas ou superiores.\n"
            "A raridade garantida varia por dungeon — quanto mais fundo, melhor o loot."
        ),
        inline=False
    )
    embed_update.add_field(
        name="⚔️ Drops Expandidos por Reino",
        value=(
            "Monstros dos 13 novos reinos têm tabela de drop própria.\n"
            "Monstros de elite nos reinos avançados podem dropar **Lendário** (0.8%) e **Mítico** (0.1%).\n"
            "Cada reino tem **itens exclusivos** que só podem ser obtidos lá."
        ),
        inline=False
    )
    embed_update.add_field(
        name="📊 Hierarquia de Raridades (atualizada)",
        value=(
            "⚪ Comum → 🟢 Incomum → 🔵 Raro → 🟣 Épico → 🟡 Lendário\n"
            "🔴 Mítico → 🟠 **Ancestral** *(NOVO)* → 💎 Divino → 🌈 Primordial"
        ),
        inline=False
    )
    embed_update.add_field(
        name="🏆 Conquista Atualizada",
        value=(
            "**Conquistador dos Reinos** agora exige derrotar os **20 bosses de level** (antes: 6).\n"
            "Recompensa aumentada para **10.000 XP**."
        ),
        inline=False
    )
    embed_update.set_footer(text="📅 Expansão dos Reinos | Use 'dungeon' para começar a explorar as novas masmorras!")
    await channel.send(embed=embed_update)
    await asyncio.sleep(2)

    # ══════════════════════════════════════════
    # MENSAGEM FINAL — Chamada para ação
    # ══════════════════════════════════════════
    embed8 = discord.Embed(
        title="🌟 Sua Jornada Começa Agora",
        description=(
            "*O Narrador fecha o livro e te olha diretamente...*\n\n"
            "**\"Você está pronto? Ou acha que está?\"**\n\n"
            "Os Campos Iniciais aguardam seus primeiros passos.\n"
            "Um Slime está por aí, inocente demais para saber o que está prestes a acontecer.\n\n"
            "Use `explorar` para começar.\n"
            "Use `ver perfil` para ver seu estado.\n"
            "Use `escolher classe` quando chegar ao nível 2.\n\n"
            "*Lembre-se: toda lenda começa com um único passo.*\n\n"
            "**Boa sorte, aventureiro. Você vai precisar.** 🎭"
        ),
        color=0xF1C40F
    )
    embed8.set_footer(text="⚠️ O boss de cada reino aparece nos níveis 9, 19, 29... até 179 e 199 — derrote-o para desbloquear o próximo reino! | 20 reinos • 20 bosses • raridades até Primordial")
    await channel.send(embed=embed8)


# ================= EVENTOS DO BOT =================

@bot.event
async def on_ready():
    init_db()
    print(f"🎮 {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")

    if not random_world_events.is_running():
        random_world_events.start()
    if not weather_change_loop.is_running():
        weather_change_loop.start()

    for guild in bot.guilds:
        await send_prologue(guild)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return

    content = message.content.lower().strip()
    user_id = message.author.id

    # ======================================================
    # ================= USAR POÇÃO (novo formato) ==========
    # ======================================================
    # Formato: "poção de vida, usar" ou "elixir de xp, usar" etc.
    if ", usar" in content or ",usar" in content:
        clean = content.replace(",usar", ", usar")
        item_part = clean.split(", usar")[0].strip()

        player = get_player(user_id)

        # Tenta encontrar a poção
        found_potion = None
        for potion_name in POTIONS.keys():
            if item_part in potion_name.lower():
                found_potion = potion_name
                break

        # Tenta encontrar equipamento a equipar
        if not found_potion:
            found_weapon = None
            found_armor = None
            for w in ITEMS["weapons"]:
                if item_part in w["name"].lower() and w["name"] in player["inventory"]:
                    found_weapon = w
                    break
            for a in ITEMS["armor"]:
                if item_part in a["name"].lower() and a["name"] in player["inventory"]:
                    found_armor = a
                    break

            if found_weapon:
                player["weapon"] = found_weapon["name"]
                save_player_db(user_id, player)
                await message.channel.send(f"⚔️ **{found_weapon['name']}** equipado!")
                return
            elif found_armor:
                player["armor"] = found_armor["name"]
                save_player_db(user_id, player)
                await message.channel.send(f"🛡️ **{found_armor['name']}** equipado!")
                return
            else:
                await message.channel.send(f"❌ Item **{item_part}** não encontrado no inventário!")
                return

        if found_potion not in player["inventory"]:
            await message.channel.send(f"❌ Você não tem **{found_potion}**!")
            return

        potion = POTIONS[found_potion]
        player["inventory"].remove(found_potion)

        embed = discord.Embed(
            title=f"{potion['emoji']} Poção Consumida!",
            description=f"*'Você bebe **{found_potion}**...'*",
            color=RARITIES.get(potion["rarity"], {"color": 0xFFFFFF})["color"]
        )

        if "hp_restore" in potion:
            old_hp = player["hp"]
            player["hp"] = min(player["hp"] + potion["hp_restore"], player["max_hp"])
            healed = player["hp"] - old_hp
            embed.add_field(name="💚 HP Restaurado", value=f"+{healed} HP", inline=False)

        if "xp_gain" in potion:
            add_xp(user_id, potion["xp_gain"])
            embed.add_field(name="⭐ XP Ganho", value=f"+{potion['xp_gain']} XP", inline=False)

        if "revive" in potion and potion["revive"]:
            player["hp"] = player["max_hp"]
            embed.add_field(name="💀 Ressurreição", value="HP completamente restaurado!", inline=False)

        save_player_db(user_id, player)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= EQUIPAR ITEM =======================
    # ======================================================
    if content.startswith("equipar "):
        item_name_search = content[8:].strip()
        player = get_player(user_id)

        found_item = None
        item_type = None
        for w in ITEMS["weapons"]:
            if item_name_search in w["name"].lower() and w["name"] in player["inventory"]:
                found_item = w["name"]
                item_type = "weapon"
                break
        if not found_item:
            for a in ITEMS["armor"]:
                if item_name_search in a["name"].lower() and a["name"] in player["inventory"]:
                    found_item = a["name"]
                    item_type = "armor"
                    break

        if not found_item:
            await message.channel.send(f"❌ Item não encontrado no inventário. Verifique com `inventário`.")
            return

        view = EquipButton(user_id, found_item, item_type)
        await message.channel.send(f"⚔️ **{found_item}** encontrado!\n\n*Deseja equipar?*", view=view)
        return

    # ======================================================
    # ================= ESCOLHER CLASSE ====================
    # ======================================================
    if any(word in content for word in ["escolher classe", "ver classes", "classes"]):
        player = get_player(user_id)

        if player.get("class"):
            await message.channel.send(f"❌ Você já é um **{player['class']}**! Use `evolução classe` para ver sua árvore de evolução.")
            return
        if player["level"] < 2:
            await message.channel.send("❌ Você precisa ser **nível 2** para escolher uma classe!")
            return

        all_classes = list(CLASSES.keys())
        total_pages = (len(all_classes) + 4) // 5
        page = 0
        chunk = all_classes[:5]

        embed = discord.Embed(
            title=f"🎭 Escolha sua Classe (Página 1/{total_pages})",
            description="*'Qual caminho você deseja seguir?'*\nCada classe tem árvore de evolução única com especializações nos níveis 40, 80, 120 e 160!",
            color=discord.Color.blue()
        )
        for cn in chunk:
            cd = CLASSES[cn]
            tree = CLASS_EVOLUTION_TREE.get(cn)
            evo_hint = f"\n🌟 Evolui: {', '.join(str(k) for k in sorted(tree.keys()))}" if tree else ""
            embed.add_field(
                name=f"{cd['emoji']} {cn}",
                value=f"{cd['description']}\n**ATK:** +{cd['atk_bonus']} | **DEF:** +{cd['def_bonus']} | **HP:** +{cd['hp_bonus']}{evo_hint}",
                inline=False
            )
        view = ClassSelectView(user_id, page=0)
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= ESCOLHER RAÇA ======================
    # ======================================================
    elif any(word in content for word in ["evoluir raça", "evoluir raca", "evolução raça", "evolucao raca", "evo raça", "evo raca", "ver evolução raça", "evoluções de raça"]):
        player = get_player(user_id)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return

        race_name = player.get("race")
        if not race_name:
            await message.channel.send("❌ Você ainda não escolheu uma raça! Use `escolher raça` primeiro.")
            return

        player_level = player.get("level", 1)
        evos = RACE_EVOLUTION_TREE.get(race_name, [])
        current_stage = player.get("race_stage", 0)

        if not evos:
            await message.channel.send(f"❌ A raça **{race_name}** não possui evoluções registradas.")
            return

        base_race = RACES.get(race_name, {})

        # Montar embed de status de evolução
        embed = discord.Embed(
            title=f"🧬 Evolução de Raça — {base_race.get('emoji','')} {race_name}",
            description=(
                f"*'Cada ciclo de vida forja um ser mais poderoso. Sua linhagem está evoluindo...'*\n\n"
                f"**Estágio atual:** `{current_stage}/3`\n"
                f"**Nível:** `{player_level}`"
            ),
            color=discord.Color.from_rgb(100, 0, 200)
        )

        # Mostrar todos os 3 estágios
        stage_emojis = ["1️⃣", "2️⃣", "3️⃣"]
        for i, evo in enumerate(evos):
            stage_num = i + 1
            unlocked = current_stage >= stage_num
            available = player_level >= evo["level"] and current_stage == stage_num - 1
            if unlocked:
                status = "✅ **DESBLOQUEADO**"
            elif available:
                status = "🔓 **DISPONÍVEL — Use `evoluir raça` para evoluir!**"
            else:
                status = f"🔒 Requer Nível **{evo['level']}**"
            embed.add_field(
                name=f"{stage_emojis[i]} {evo['emoji']} {evo['name']}",
                value=(
                    f"{status}\n"
                    f"*{evo['lore']}*\n"
                    f"❤️ HP: **+{evo['hp_bonus']}** | ⚔️ ATK: **+{evo['atk_bonus']}** | 🛡️ DEF: **+{evo['def_bonus']}**"
                ),
                inline=False
            )

        # Verificar se pode evoluir agora
        next_stage = current_stage + 1
        if next_stage > 3:
            embed.set_footer(text="🏆 Você atingiu a evolução máxima da sua raça!")
            await message.channel.send(embed=embed)
            return

        next_evo = evos[next_stage - 1]
        if player_level < next_evo["level"]:
            embed.set_footer(text=f"Próxima evolução disponível no Nível {next_evo['level']}")
            await message.channel.send(embed=embed)
            return

        # Pode evoluir! Aplicar evolução
        old_hp  = player.get("max_hp",  100)
        old_atk = player.get("atk",     10)
        old_def = player.get("def",     5)

        player["max_hp"] = old_hp  + next_evo["hp_bonus"]
        player["hp"]     = player["max_hp"]
        player["atk"]    = old_atk + next_evo["atk_bonus"]
        player["def"]    = old_def + next_evo["def_bonus"]
        player["race_stage"] = next_stage
        save_player_db(user_id, player)

        evo_embed = discord.Embed(
            title=f"🌟 EVOLUÇÃO DE RAÇA — ESTÁGIO {next_stage}!",
            description=(
                f"*'{next_evo['lore']}'*\n\n"
                f"{base_race.get('emoji','')} **{race_name}** → {next_evo['emoji']} **{next_evo['name']}**\n\n"
                f"✨ *Seu poder racial atingiu um novo patamar!*"
            ),
            color=discord.Color.gold()
        )
        evo_embed.add_field(name="❤️ HP Ganho",  value=f"+{next_evo['hp_bonus']}  → `{player['max_hp']}`", inline=True)
        evo_embed.add_field(name="⚔️ ATK Ganho", value=f"+{next_evo['atk_bonus']} → `{player['atk']}`",    inline=True)
        evo_embed.add_field(name="🛡️ DEF Ganho", value=f"+{next_evo['def_bonus']} → `{player['def']}`",    inline=True)
        if next_stage == 3:
            evo_embed.add_field(
                name="👑 EVOLUÇÃO MÁXIMA ATINGIDA!",
                value="*Você chegou ao ápice da sua linhagem racial. Nenhum ser da sua raça é mais poderoso.*",
                inline=False
            )
        evo_embed.set_footer(text=f"Estágio {next_stage}/3 | Use 'ver perfil' para ver seus atributos atualizados")
        await message.channel.send(embed=evo_embed)
        return

    elif any(word in content for word in ["escolher raça", "escolher raca", "ver raças", "ver racas", "raças", "racas"]):
        player = get_player(user_id)

        if player.get("race"):
            race_data = RACES[player["race"]]
            await message.channel.send(
                f"❌ Você já é um(a) **{race_data['emoji']} {player['race']}**!\n"
                f"**Passiva:** {race_data['passive']}"
            )
            return
        if player["level"] < 1:
            await message.channel.send("❌ Você precisa estar registrado para escolher uma raça!")
            return

        all_races = list(RACES.keys())
        total_pages = (len(all_races) + 4) // 5
        chunk = all_races[:5]

        embed = discord.Embed(
            title=f"🧬 Escolha sua Raça (Página 1/{total_pages})",
            description="*'De onde você vem? Sua origem define seu destino.'*\nSua raça concede bônus permanentes e uma passiva única!",
            color=discord.Color.purple()
        )
        for rn in chunk:
            rd = RACES[rn]
            embed.add_field(
                name=f"{rd['emoji']} {rn}",
                value=f"{rd['description']}\n**Passiva:** {rd['passive']}\n**HP:** +{rd['hp_bonus']} | **ATK:** +{rd['atk_bonus']} | **DEF:** +{rd['def_bonus']}",
                inline=False
            )
        view = RaceSelectView(user_id, page=0)
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= HABILIDADES ========================
    # ======================================================
    elif any(word in content for word in ["habilidades", "ver habilidades", "skills", "magias"]):
        player = get_player(user_id)
        cls = player.get("class")
        if not cls:
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        skills = get_player_skills(player)
        tier_data = CLASS_TIERED_SKILLS.get(cls)

        embed = discord.Embed(
            title=f"⚔️ Habilidades de {message.author.display_name}",
            description=f"**Classe:** {CLASSES[cls]['emoji']} {cls}{(' • **Spec:** ' + player['specialization']) if player.get('specialization') else ''}",
            color=discord.Color.red()
        )

        lvl = player["level"]
        tiers_shown = {"🟢 Básicas": [], "🔵 Intermediárias": [], "🟣 Avançadas": [], "⭐ Especial": [], "👑 Suprema": []}

        if tier_data:
            for sk in tier_data["basic"]:
                tiers_shown["🟢 Básicas"].append(sk)
            if lvl >= 40:
                for sk in tier_data.get("intermediate", []):
                    tiers_shown["🔵 Intermediárias"].append(sk)
            else:
                embed.add_field(name="🔵 Intermediárias", value=f"*Desbloqueiam no nível 40*", inline=False)
            if lvl >= 80:
                for sk in tier_data.get("advanced", []):
                    tiers_shown["🟣 Avançadas"].append(sk)
            else:
                embed.add_field(name="🟣 Avançadas", value=f"*Desbloqueiam no nível 80*", inline=False)
            supreme = tier_data.get("supreme")
            if supreme:
                if supreme["name"] in player.get("supreme_skills", []):
                    tiers_shown["👑 Suprema"].append(supreme)
                else:
                    embed.add_field(name="👑 Suprema", value=f"*Desbloqueie derrotando: **{supreme['unlock_boss']}***", inline=False)
        else:
            for sk in CLASS_SKILLS.get(cls, []):
                tiers_shown["🟢 Básicas"].append(sk)

        spec = player.get("specialization")
        if spec and spec in CLASS_SPECIALIZATIONS:
            sk = CLASS_SPECIALIZATIONS[spec].get("special_skill")
            if sk:
                tiers_shown["⭐ Especial"].append(sk)

        for tier_label, sk_list in tiers_shown.items():
            if sk_list:
                val = "\n".join([f"**{sk['name']}** — {sk['mana_cost']} mana | {sk['desc']}" for sk in sk_list])
                embed.add_field(name=tier_label, value=val, inline=False)

        # Show evolution tree
        tree = CLASS_EVOLUTION_TREE.get(cls)
        if tree:
            current_tier = player.get("class_tier", 0)
            evo_lines = []
            for evo_lvl in sorted(tree.keys()):
                tier_idx = sorted(tree.keys()).index(evo_lvl) + 1
                status = "✅" if current_tier >= tier_idx else ("🔓" if lvl >= evo_lvl else "🔒")
                evo_lines.append(f"{status} **Nv.{evo_lvl}** → {tree[evo_lvl]['name']}")
            embed.add_field(name="🌳 Árvore de Evolução", value="\n".join(evo_lines), inline=False)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= EVOLUÇÃO CLASSE ====================
    # ======================================================
    elif any(word in content for word in ["evolução classe", "evoluir classe", "evolucao classe", "evoluir minha classe"]):
        player = get_player(user_id)
        cls = player.get("class")
        if not cls:
            await message.channel.send("⚠️ Escolha uma classe primeiro!")
            return
        await check_class_evolution(message.channel, user_id)
        return

    # ======================================================
    # ================= PROCURAR PET =======================
    # ======================================================
    elif any(word in content for word in ["procurar pet", "procurar criatura", "buscar pet"]):
        player = get_player(user_id)
        # Permite procurar novos pets mesmo com pet ativo — extras vão pra fazenda

        world = get_world(player["level"], player)
        roll = roll_dice()
        luck = get_luck(roll)

        embed = discord.Embed(
            title="🔍 Procurando Criaturas...",
            description="*'Você vasculha o ambiente em busca de criaturas selvagens...'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado da Busca", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 2:
            # Encontra inimigo em vez de pet
            monster_name = random.choice(list(world["monsters"].keys()))
            monster = world["monsters"][monster_name]
            dmg = random.randint(15, 35)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = 1
            save_player_db(user_id, player)
            result, xp_loss = remove_xp(user_id, random.randint(20, 40))

            embed.add_field(
                name="⚠️ Emboscada!",
                value=f"*'Em vez de um pet, você encontra um **{monster_name}** furioso que te ataca!'*\n\n💔 **−{dmg} HP**\n❌ **−{xp_loss} XP**",
                inline=False
            )
            embed.color = discord.Color.red()
            await message.channel.send(embed=embed)
            return

        elif roll <= 4:
            embed.add_field(
                name="😔 Nada Encontrado",
                value="*'Você vasculha por horas, mas só encontra rastros. As criaturas parecem evitar você.'*",
                inline=False
            )
            embed.color = discord.Color.light_grey()
            await message.channel.send(embed=embed)
            return

        elif roll <= 6:
            # Pet comum do mundo
            world_level = max([k for k in PETS.keys() if k <= player["level"]])
            available = PETS[world_level]
            pet = random.choice([p for p in available if p["rarity"] in ["Comum", "Incomum"]] or available)

            embed.add_field(
                name=f"{pet['emoji']} Criatura Avistada!",
                value=f"*'Você encontra um **{pet['name']}** ({pet['rarity']}) nas proximidades!'*",
                inline=False
            )
            embed.color = RARITIES[pet["rarity"]]["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = PetTameButton(user_id, pet)
            await message.channel.send(f"{pet['emoji']} **{pet['name']}** está próximo!", view=view)

        else:  # 7-10: maior chance de pet raro
            world_level = max([k for k in PETS.keys() if k <= player["level"]])
            available = PETS[world_level]
            if roll >= 9:
                pets_filtered = [p for p in available if p["rarity"] in ["Raro", "Épico", "Lendário", "Mítico", "Divino", "Primordial"]]
            else:
                pets_filtered = [p for p in available if p["rarity"] in ["Incomum", "Raro", "Épico"]]
            pet = random.choice(pets_filtered or available)

            embed.add_field(
                name=f"{pet['emoji']} Criatura Rara Avistada!",
                value=f"*'Incrível! Você detecta um **{pet['name']}** ({RARITIES[pet['rarity']]['emoji']} {pet['rarity']}) escondido!'*",
                inline=False
            )
            embed.color = RARITIES[pet["rarity"]]["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = PetTameButton(user_id, pet)
            await message.channel.send(f"{pet['emoji']} **{pet['name']}** apareceu!", view=view)
        return

    # ======================================================
    # ================= DOMESTICAR PET =====================
    # ======================================================
    elif any(word in content for word in ["domesticar", "tentar domesticar", "domar"]):
        player = get_player(user_id)
        # Permite múltiplos pets — o ativo fica em player["pet"], os outros na fazenda
        # Não bloqueia mais domesticação!

        world_level = player["level"] - (player["level"] % 10)
        if world_level == 0:
            world_level = 1
        if world_level not in PETS:
            world_level = max([w for w in PETS.keys() if w <= player["level"]])

        available_pets = PETS[world_level]
        pet = random.choice(available_pets)

        embed = discord.Embed(
            title=f"{pet['emoji']} {pet['name']} Apareceu!",
            description=f"*'Um **{pet['name']}** selvagem aparece diante de você!'*",
            color=RARITIES[pet["rarity"]]["color"]
        )
        embed.add_field(name="✨ Raridade", value=f"{RARITIES[pet['rarity']]['emoji']} {pet['rarity']}", inline=True)
        embed.add_field(name="💪 Bônus ATK", value=f"+{pet['bonus_atk']}", inline=True)
        embed.add_field(name="❤️ Bônus HP", value=f"+{pet['bonus_hp']}", inline=True)

        view = PetTameButton(user_id, pet)
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= DESAFIAR / IR ATRÁS DO BOSS ========
    # ======================================================
    elif any(word in content for word in ["desafiar boss", "ir atrás do boss", "ir atras do boss", "chamar boss", "invocar boss", "enfrentar boss"]):
        player = get_player(user_id)

        # ── REDIRECIONAR: desafiar boss do level X ──────────────────────
        import re as _re
        _m = _re.match(r"desafiar boss (?:do )?level (\d+)", content)
        if _m:
            target_level = int(_m.group(1))
            boss_gate_levels = [9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 189, 199]
            if target_level not in boss_gate_levels:
                niveis_str = ", ".join(str(x) for x in boss_gate_levels[:10]) + "..."
                await message.channel.send(
                    f"❌ **Level {target_level}** não tem boss de nível!\n\n"
                    f"Bosses de nível existem apenas nos níveis: **{niveis_str}**\n"
                    f"Exemplo: `desafiar boss do level 9`, `desafiar boss do level 19`"
                )
                return
            player_level = player.get("level", 1)
            if player_level < target_level:
                await message.channel.send(
                    f"🔒 **Boss do Level {target_level}** bloqueado!\n\n"
                    f"Você está no nível **{player_level}**. Alcance o nível **{target_level}** para desafiar este boss.\n"
                    f"*\'O guardião desta passagem não reconhece sua presença... ainda.\'*"
                )
                return
            boss_data_lv = get_level_boss(target_level)
            if not boss_data_lv:
                await message.channel.send(f"❌ Não foi possível encontrar o boss do level {target_level}.")
                return
            already_defeated = boss_data_lv["name"] in player.get("bosses", [])
            effects = player.get("active_effects", {})
            effects["pending_boss"] = boss_data_lv
            player["active_effects"] = effects
            save_player_db(user_id, player)
            if already_defeated:
                boss_level_to_world = {9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
                                       109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190}
                world_key = boss_level_to_world.get(target_level, 1)
                world_data_lv = WORLDS.get(world_key, {})
                world_name_lv = world_data_lv.get("name", "Reino " + str(target_level))
                world_emoji_lv = world_data_lv.get("emoji", "🌍")
                boss_nm = boss_data_lv["name"]
                embed_lv = discord.Embed(
                    title=f"⚔️ REVANCHE — BOSS DO LEVEL {target_level}!",
                    description=(
                        f"*\'As névoas do tempo se desfazem... O guardião ressurge das sombras para um novo duelo!\'*\n\n"
                        f"👹 **{boss_nm}** retorna para uma batalha épica!\n\n"
                        f"{world_emoji_lv} **{world_name_lv}** — Este foi o guardião que desbloqueou este reino para você.\n\n"
                        f"*A lenda diz que reviver grandes batalhas fortalece a alma do guerreiro...*"
                    ),
                    color=discord.Color.from_rgb(150, 0, 200)
                )
            else:
                boss_nm = boss_data_lv["name"]
                embed_lv = discord.Embed(
                    title=f"🚨 BOSS DE NÍVEL {target_level} — PASSAGEM BLOQUEADA!",
                    description=(
                        f"*\'O ar fica pesado... Uma sombra colossal bloqueia seu caminho!\'*\n\n"
                        f"👹 **{boss_nm}** surge diante de você!\n\n"
                        f"⚠️ **Derrote-o para desbloquear o próximo reino e desbloquear o XP!**"
                    ),
                    color=discord.Color.dark_red()
                )
            embed_lv.add_field(name="❤️ HP", value=f"`{boss_data_lv['hp']:,}`", inline=True)
            embed_lv.add_field(name="⚔️ ATK", value=f"`{boss_data_lv['atk']}`", inline=True)
            embed_lv.add_field(name="⭐ XP", value=f"`{boss_data_lv['xp']:,}`", inline=True)
            embed_lv.add_field(name="🎯 Level do Boss", value=f"`{target_level}`", inline=True)
            if already_defeated:
                embed_lv.add_field(name="🏆 Status", value="*Revanche — Boss já derrotado anteriormente*", inline=False)
            embed_lv.add_field(name="💡 Dica", value="Use os botões abaixo para lutar ou chamar aliados!", inline=False)
            view_lv = BossButton(user_id, boss_data_lv["name"])
            await message.channel.send(embed=embed_lv, view=view_lv)
            return
        # ── FIM REDIRECT DESAFIAR BOSS DO LEVEL ─────────────────────────

        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        # PRIORIDADE: Boss de level (se nível 9/19/29/39/49/59 e ainda não derrotou)
        boss_gate_levels = {9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 189, 199}
        boss_data = None
        is_level_boss = False

        if player["level"] in boss_gate_levels:
            boss_data = get_level_boss(player["level"])
            if boss_data and boss_data["name"] not in player.get("bosses", []):
                is_level_boss = True
            else:
                boss_data = None  # Já derrotou, vai pegar boss do mundo

        if not boss_data:
            # Verifica se tem boss pendente (de encontrar boss)
            effects = player.get("active_effects", {})
            pending = effects.get("pending_boss")
            if pending:
                boss_data = pending
            else:
                # Boss do mundo atual
                world_level = max([k for k in WORLDS.keys() if k <= player["level"]])
                boss_pool = WORLD_BOSSES_VARIANTS.get(world_level, [])
                boss_data = random.choice(boss_pool) if boss_pool else WORLDS[world_level]["boss"]

        # *** CORREÇÃO: Salva SEMPRE o boss correto como pending_boss antes dos botões ***
        effects = player.get("active_effects", {})
        effects["pending_boss"] = boss_data
        player["active_effects"] = effects
        save_player_db(user_id, player)

        color = discord.Color.dark_red() if is_level_boss else discord.Color.red()
        title = "🚨 BOSS DE NÍVEL — PASSAGEM BLOQUEADA!" if is_level_boss else "⚔️ BOSS ENCONTRADO!"
        desc_extra = "\n\n⚠️ **Derrote-o para desbloquear o próximo reino e desbloquear o XP!**" if is_level_boss else ""

        embed = discord.Embed(
            title=title,
            description=f"*'O ar fica pesado... Uma sombra colossal se ergue!'*\n\n👹 **{boss_data['name']}** surge!{desc_extra}",
            color=color
        )
        embed.add_field(name="❤️ HP", value=f"`{boss_data['hp']:,}`", inline=True)
        embed.add_field(name="⚔️ ATK", value=f"`{boss_data['atk']}`", inline=True)
        embed.add_field(name="⭐ XP", value=f"`{boss_data['xp']:,}`", inline=True)
        if is_level_boss:
            embed.add_field(name="🚫 XP Bloqueado", value="Ganhe XP novamente derrotando este boss!", inline=False)
        embed.add_field(name="💡 Dica", value="Use os botões abaixo para lutar ou chamar aliados!", inline=False)

        view = BossButton(user_id, boss_data["name"])
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ======= DESAFIAR BOSS DO LEVEL X (revanche) ==========
    # ======================================================
    elif content.startswith("desafiar boss do level ") or content.startswith("desafiar boss level "):
        player = get_player(user_id)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return

        # Extrair o número do level do comando
        try:
            parts = content.split()
            target_level = int(parts[-1])
        except (ValueError, IndexError):
            await message.channel.send("❌ Use: `desafiar boss do level 9` (ou 19, 29, 39...)")
            return

        # Bosses disponíveis nos níveis: 9, 19, 29, 39...
        boss_gate_levels = [9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 189, 199]
        if target_level not in boss_gate_levels:
            niveis_str = ", ".join(str(x) for x in boss_gate_levels[:10]) + "..."
            await message.channel.send(
                f"❌ **Level {target_level}** não tem boss de nível!\n\n"
                f"Os bosses de nível existem apenas nos níveis: **{niveis_str}**\n\n"
                f"Use: `desafiar boss do level 9`, `desafiar boss do level 19`, etc."
            )
            return

        # Verificar se o jogador já passou desse level (desbloqueou o boss)
        player_level = player.get("level", 1)
        if player_level < target_level:
            await message.channel.send(
                f"🔒 **Boss do Level {target_level}** ainda está bloqueado!\n\n"
                f"Você está no nível **{player_level}**. Alcance o nível **{target_level}** para desafiar este boss.\n\n"
                f"*\'O guardião desta passagem não reconhece sua presença... ainda.\'*"
            )
            return

        # Pegar dados do boss
        boss_data = get_level_boss(target_level)
        if not boss_data:
            await message.channel.send(f"❌ Não foi possível encontrar o boss do level {target_level}.")
            return

        already_defeated = boss_data["name"] in player.get("bosses", [])

        # Salvar como pending boss
        effects = player.get("active_effects", {})
        effects["pending_boss"] = boss_data
        player["active_effects"] = effects
        save_player_db(user_id, player)

        if already_defeated:
            # Revanche — mesma vibe de desbloqueio de reino
            boss_level_to_world = {9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
                                   109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190}
            world_key = boss_level_to_world.get(target_level, 1)
            world_data = WORLDS.get(world_key, {})
            world_name = world_data.get("name", "Reino " + str(target_level))
            world_emoji = world_data.get("emoji", "🌍")
            boss_name_val = boss_data["name"]
            embed = discord.Embed(
                title=f"⚔️ REVANCHE — BOSS DO LEVEL {target_level}!",
                description=(
                    f"*'As névoas do tempo se desfazem... O guardião ressurge das sombras para um novo duelo!'*\n\n"
                    f"👹 **{boss_name_val}** retorna para uma batalha épica!\n\n"
                    f"{world_emoji} **{world_name}** — Este foi o guardião que desbloqueou este reino para você.\n\n"
                    f"*A lenda diz que reviver grandes batalhas fortalece a alma do guerreiro...*"
                ),
                color=discord.Color.from_rgb(150, 0, 200)
            )
        else:
            boss_name_val = boss_data["name"]
            embed = discord.Embed(
                title=f"🚨 BOSS DE NÍVEL {target_level} — PASSAGEM BLOQUEADA!",
                description=(
                    f"*'O ar fica pesado... Uma sombra colossal bloqueia seu caminho!'*\n\n"
                    f"👹 **{boss_name_val}** surge diante de você!\n\n"
                    f"⚠️ **Derrote-o para desbloquear o próximo reino e desbloquear o XP!**"
                ),
                color=discord.Color.dark_red()
            )

        embed.add_field(name="❤️ HP", value=f"`{boss_data['hp']:,}`", inline=True)
        embed.add_field(name="⚔️ ATK", value=f"`{boss_data['atk']}`", inline=True)
        embed.add_field(name="⭐ XP", value=f"`{boss_data['xp']:,}`", inline=True)
        embed.add_field(name="🎯 Level do Boss", value=f"`{target_level}`", inline=True)
        if already_defeated:
            embed.add_field(name="🏆 Status", value="*Revanche — Boss já derrotado anteriormente*", inline=False)
        embed.add_field(name="💡 Dica", value="Use os botões abaixo para lutar ou chamar aliados!", inline=False)

        view = BossButton(user_id, boss_data["name"])
        await message.channel.send(embed=embed, view=view)
        return

    # ======================================================
    # ================= JUNTAR BOSS (co-op) ================
    # ======================================================
    elif any(word in content for word in ["juntar boss", "ajudar boss", "participar boss"]):
        player = get_player(user_id)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, boss_name, leader_id, members FROM boss_battles WHERE status = 'recruiting' ORDER BY created_at DESC LIMIT 1")
        result = c.fetchone()
        conn.close()

        if not result:
            await message.channel.send("❌ Não há batalhas de boss abertas no momento!")
            return

        battle_id, boss_name, leader_id, members_json = result
        members = json.loads(members_json)

        if str(user_id) in members:
            await message.channel.send("❌ Você já está nesta batalha!")
            return

        if len(members) >= 5:
            await message.channel.send("❌ Esta batalha já está cheia (máximo 5 jogadores)!")
            return

        members.append(str(user_id))
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE boss_battles SET members = ? WHERE id = ?", (json.dumps(members), battle_id))
        conn.commit()
        conn.close()

        await message.channel.send(
            f"✅ **{message.author.mention}** entrou na batalha contra **{boss_name}**!\n\n👥 Jogadores: {len(members)}/5\n\nO líder pode usar `iniciar batalha boss` quando estiver pronto!"
        )
        return

    # ======================================================
    # ================= INICIAR BATALHA BOSS (co-op) =======
    # ======================================================
    elif any(word in content for word in ["iniciar batalha boss", "começar batalha boss", "start boss"]):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, boss_name, leader_id, members, world_level FROM boss_battles WHERE leader_id = ? AND status = 'recruiting'", (str(user_id),))
        result = c.fetchone()

        if not result:
            await message.channel.send("❌ Você não tem uma batalha de boss ativa. Use `desafiar boss` e escolha 'Chamar Aliados'.")
            conn.close()
            return

        battle_id, boss_name, leader_id, members_json, world_level = result
        members = json.loads(members_json)

        c.execute("UPDATE boss_battles SET status = 'active' WHERE id = ?", (battle_id,))
        conn.commit()
        conn.close()

        boss_data = WORLDS.get(world_level, WORLDS[1])["boss"]

        member_names = []
        for mid in members:
            try:
                u = await bot.fetch_user(int(mid))
                member_names.append(u.mention)
            except:
                pass

        embed = discord.Embed(
            title=f"⚔️ BATALHA ÉPICA INICIADA!",
            description=f"**{'  |  '.join(member_names)}** vs **{boss_name}**!\n\n*'Que os deuses guiem suas espadas!'*",
            color=discord.Color.dark_red()
        )
        await message.channel.send(embed=embed)
        await asyncio.sleep(2)
        await fight_boss(message.channel, user_id, allies=members)
        return


    # ======================================================
    # ================= CRIAR GUILDA =======================
    # ======================================================
    elif "criar guilda" in content or "criar guild" in content:
        player = get_player(user_id)
        if player.get("guild_id"):
            await message.channel.send("❌ Você já está em uma guilda!")
            return

        guild_name = content.replace("criar guilda", "").replace("criar guild", "").strip()
        if not guild_name:
            await message.channel.send("❌ Use: `criar guilda [nome]`")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO guilds (name, leader_id, members) VALUES (?, ?, ?)",
                      (guild_name, str(user_id), json.dumps([str(user_id)])))
            guild_id = c.lastrowid
            conn.commit()
            player["guild_id"] = guild_id
            save_player_db(user_id, player)

            embed = discord.Embed(
                title="🏰 Guilda Criada!",
                description=f"*'A guilda **{guild_name}** foi fundada!'*",
                color=discord.Color.gold()
            )
            embed.add_field(name="👑 Líder", value=message.author.mention, inline=True)
            embed.set_footer(text="Outros podem usar 'entrar guilda' para se juntar!")
            await message.channel.send(embed=embed)
        except sqlite3.IntegrityError:
            await message.channel.send("❌ Já existe uma guilda com esse nome!")
        finally:
            conn.close()
        return

    # ======================================================
    # ================= ENTRAR GUILDA ======================
    # ======================================================
    elif "entrar guilda" in content or "entrar na guilda" in content:
        player = get_player(user_id)
        if player.get("guild_id"):
            await message.channel.send("❌ Você já está em uma guilda!")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, leader_id, members FROM guilds")
        guilds = c.fetchall()
        conn.close()

        if not guilds:
            await message.channel.send("❌ Não há guildas! Crie uma com `criar guilda [nome]`")
            return

        embed = discord.Embed(title="🏰 Guildas Disponíveis", color=discord.Color.blue())
        for guild_row in guilds:
            guild_id, name, leader_id, members_json = guild_row
            members = json.loads(members_json)
            embed.add_field(name=f"{guild_id}. {name}", value=f"👥 Membros: {len(members)}", inline=False)
        await message.channel.send(embed=embed)

        def check(m):
            return m.author.id == user_id and m.content.isdigit()

        try:
            response = await bot.wait_for('message', check=check, timeout=30.0)
            guild_id_choice = int(response.content)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT name, members FROM guilds WHERE id = ?", (guild_id_choice,))
            result = c.fetchone()
            if not result:
                await message.channel.send("❌ Guilda não encontrada!")
                conn.close()
                return
            guild_name, members_json = result
            members = json.loads(members_json)
            members.append(str(user_id))
            c.execute("UPDATE guilds SET members = ? WHERE id = ?", (json.dumps(members), guild_id_choice))
            conn.commit()
            conn.close()
            player["guild_id"] = guild_id_choice
            save_player_db(user_id, player)
            await message.channel.send(f"✅ **Você entrou na guilda {guild_name}!**")
        except asyncio.TimeoutError:
            await message.channel.send("⏰ Tempo esgotado!")
        return

    # ======================================================
    # ================= VER GUILDA =========================
    # ======================================================
    elif any(word in content for word in ["ver guilda", "minha guilda"]):
        player = get_player(user_id)
        if not player.get("guild_id"):
            await message.channel.send("❌ Você não está em nenhuma guilda!")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name, leader_id, members, total_xp FROM guilds WHERE id = ?", (player["guild_id"],))
        result = c.fetchone()
        conn.close()

        if not result:
            await message.channel.send("❌ Guilda não encontrada!")
            return

        guild_name, leader_id, members_json, total_xp = result
        members = json.loads(members_json)
        embed = discord.Embed(title=f"🏰 {guild_name}", color=discord.Color.gold())
        embed.add_field(name="👥 Membros", value=len(members), inline=True)
        embed.add_field(name="⭐ XP Total", value=total_xp, inline=True)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= BEBER POÇÃO (formato antigo) =======
    # ======================================================
    elif any(word in content for word in ["beber", "usar poção", "tomar"]):
        player = get_player(user_id)
        potion_name = None
        for potion in POTIONS.keys():
            if potion.lower() in content:
                potion_name = potion
                break

        if not potion_name:
            await message.channel.send("❌ Especifique qual poção! Formato: `[nome da poção], usar`")
            return

        if potion_name not in player["inventory"]:
            await message.channel.send(f"❌ Você não tem **{potion_name}**!")
            return

        potion = POTIONS[potion_name]
        player["inventory"].remove(potion_name)
        embed = discord.Embed(
            title=f"{potion['emoji']} Poção Consumida!",
            description=f"*'Você bebe **{potion_name}**...'*",
            color=RARITIES.get(potion["rarity"], {"color": 0xFFFFFF})["color"]
        )
        if "hp_restore" in potion:
            old_hp = player["hp"]
            player["hp"] = min(player["hp"] + potion["hp_restore"], player["max_hp"])
            embed.add_field(name="💚 HP Restaurado", value=f"+{player['hp'] - old_hp} HP", inline=False)
        if "xp_gain" in potion:
            add_xp(user_id, potion["xp_gain"])
            embed.add_field(name="⭐ XP Ganho", value=f"+{potion['xp_gain']} XP", inline=False)
        if "revive" in potion and potion["revive"]:
            player["hp"] = player["max_hp"]
            embed.add_field(name="💀 Ressurreição", value="HP completamente restaurado!", inline=False)
        save_player_db(user_id, player)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VENDER ITEM ========================
    # ======================================================
    elif content.startswith("vender"):
        player = get_player(user_id)
        item_name = content.replace("vender", "").strip()
        if not item_name:
            await message.channel.send("❌ Use: `vender [nome do item]`")
            return

        found_item = None
        for item in player["inventory"]:
            if item_name in item.lower():
                found_item = item
                break

        if not found_item:
            await message.channel.send(f"❌ Você não tem **{item_name}** no inventário!")
            return

        price = get_item_sell_price(found_item)
        player["inventory"].remove(found_item)
        player["coins"] += price
        save_player_db(user_id, player)

        embed = discord.Embed(
            title="💰 Item Vendido!",
            description=f"*'Você vendeu **{found_item}** por **{price} CSI**!'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Moedas Atuais", value=f"{player['coins']} CSI", inline=False)
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= TROCAR ITEMS =======================
    # ======================================================
    if "trocar" in content and "@" in message.content and "csi" not in content:
        parts = message.content.split("com")
        if len(parts) < 2:
            return

        from_items_text = parts[0].replace("trocar", "").strip()
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione um usuário válido!")
            return

        to_user = mentions[0]
        to_user_id = to_user.id

        if to_user_id == user_id:
            await message.channel.send("❌ Você não pode trocar com você mesmo!")
            return

        await message.channel.send(f"{to_user.mention}, que item você oferece em troca de **{from_items_text}**?\n\nResponda com: `ofereço [nome do item]`")

        def check(m):
            return m.author.id == to_user_id and "ofereço" in m.content.lower()

        try:
            response = await bot.wait_for('message', check=check, timeout=60.0)
            to_items_text = response.content.replace("ofereço", "").strip()

            embed = discord.Embed(title="🔄 Proposta de Troca", color=discord.Color.blue())
            embed.add_field(name=f"📤 {message.author.name} oferece", value=f"**{from_items_text}**", inline=True)
            embed.add_field(name=f"📥 {to_user.name} oferece", value=f"**{to_items_text}**", inline=True)

            view = TradeButton(user_id, to_user_id, [from_items_text], [to_items_text])
            await message.channel.send(embed=embed, view=view)
        except asyncio.TimeoutError:
            await message.channel.send("⏰ Tempo esgotado! Proposta expirou.")
        return

    # ======================================================
    # ================= TROCAR COINS CSI ===================
    # ======================================================
    elif "trocar" in content and "csi" in content:
        player = get_player(user_id)
        embed = discord.Embed(
            title="💱 Solicitação de Conversão",
            description=f"{message.author.mention} deseja converter moedas CSI.",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}` CSI", inline=False)
        await message.channel.send(embed=embed)
        try:
            admin = await bot.fetch_user(int(BOT_OWNER_ID))
            dm_embed = discord.Embed(title="🔔 Solicitação de Conversão", color=discord.Color.gold())
            dm_embed.add_field(name="Jogador", value=f"{message.author.name} ({message.author.id})", inline=False)
            dm_embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}` CSI", inline=False)
            await admin.send(embed=dm_embed)
        except:
            pass
        return

    # ======================================================
    # ================= EXPLORAR ===========================
    # ======================================================
    if content in ["comandos", "ver comandos", "lista de comandos", "ajuda", "help", "/comandos"]:
        # ── Página 1: Início & Personagem ──────────────────────────────
        e1 = discord.Embed(
            title="📋 COMANDOS — World CSI  [1/5]",
            description="*Guia completo de todos os comandos disponíveis no bot!*\n`comandos 2` `comandos 3` `comandos 4` `comandos 5` para mais páginas",
            color=0x3498DB
        )
        e1.add_field(
            name="🆕 Início",
            value=(
                "O personagem é criado automaticamente na primeira ação!\n"
                "Use `escolher raça` e `escolher classe` para configurar.\n"
                "**Raças:** Humano, Elfo, Anão, Orc, Vampiro, Fada, Dragônio e mais!\n"
                "**Classes:** Guerreiro, Mago, Arqueiro, Paladino, Assassino, Necromante,\n"
                "Berserker, Druida, Monge, Bardo, e mais 20 classes!"
            ),
            inline=False
        )
        e1.add_field(
            name="👤 Personagem",
            value=(
                "`ver perfil` — Ver seus stats, nível, classe e raça\n"
                "`inventário` — Ver todos seus itens e equipamentos\n"
                "`escolher raça` — Escolher raça (só uma vez, permanente!)\n"
                "`escolher classe` — Escolher classe base\n"
                "`habilidades` — Ver habilidades e skills disponíveis\n"
                "`evolução classe` — Ver seu caminho de evolução atual\n"
                "`ver mana` — Ver mana atual e máxima"
            ),
            inline=False
        )
        e1.add_field(
            name="🌟 Evolução de Classe (Níveis 40 / 80 / 120 / 160)",
            value=(
                "Ao atingir nível 40, 80, 120 e 160 sua classe evolui automaticamente!\n"
                "Você escolhe uma **especialização** que dá bônus escalonados:\n"
                "• **Tier I (nível 40):** ×1 — introdução à especialização\n"
                "• **Tier II (nível 80):** ×2.5 + bônus extra — poder crescendo\n"
                "• **Tier III (nível 120):** ×5 + bônus grande — força lendária\n"
                "• **Tier IV (nível 160):** ×10 + poder divino — o topo absoluto\n"
                "`evolução classe` para ver as opções disponíveis"
            ),
            inline=False
        )
        e1.add_field(
            name="💪 Treinamento",
            value=(
                "`treinar força` — +ATK permanente\n"
                "`treinar defesa` — +DEF permanente\n"
                "`treinar vitalidade` — +HP Máximo permanente\n"
                "`treinar intensivo` — +ATK, +DEF e +HP de uma vez (mais caro)"
            ),
            inline=False
        )
        e1.add_field(
            name="🏆 Conquistas & XP",
            value=(
                "`ver conquistas` — 100 conquistas com recompensas de XP\n"
                "`alinhamento` — Ver seu alinhamento moral (Bem/Neutro/Mal)\n"
                "`ver títulos` — Ver títulos desbloqueados pelo alinhamento"
            ),
            inline=False
        )
        e1.set_footer(text="Página 1/5 — Use 'comandos 2' para continuar")

        # ── Página 2: Exploração, Caça & Combate ───────────────────────
        e2 = discord.Embed(
            title="📋 COMANDOS — World CSI  [2/5]",
            description="*Exploração, caça, dungeons e combate*",
            color=0x2ECC71
        )
        e2.add_field(
            name="🌍 Exploração",
            value=(
                "`explorar` — Explora a região atual. Resultado baseado no dado (1-10):\n"
                "• 1-2: Perde XP | 3-4: Nada | 5: Recurso | 6-7: Recurso+XP\n"
                "• 8: 2 recursos+XP+chance dungeon secreta | 9-10: Item raro!"
            ),
            inline=False
        )
        e2.add_field(
            name="⚔️ Caça",
            value=(
                "`caçar` — Ataca monstros da região. Drops escalam por raridade:\n"
                "• Monstros normais: drops até **Épico**\n"
                "• Bosses de nível: drops **Mítico** e acima\n"
                "• Monstros também dropam armas e armaduras!"
            ),
            inline=False
        )
        e2.add_field(
            name="🗺️ Coletar & Minerar",
            value=(
                "`coletar` — Coleta recursos naturais da região\n"
                "`minerar` — Mineração profunda, mais recursos de uma vez\n"
                "`minerar baú` — Tenta abrir um baú secreto (precisa de chave!)"
            ),
            inline=False
        )
        e2.add_field(
            name="🏰 Dungeons",
            value=(
                "`dungeon` — Procura uma dungeon na região atual\n"
                "`achar dungeon` / `procurar dungeon` — Mesma função\n"
                "Dungeons têm recompensas melhores que exploração normal!\n"
                "Dungeons secretas aparecem com 15% de chance ao explorar (dado 8)"
            ),
            inline=False
        )
        e2.add_field(
            name="👹 Boss do Reino",
            value=(
                "`encontrar boss` — Procura o boss do reino atual *(NÃO é boss de nível)*\n"
                "`desafiar boss` — Enfrenta o boss encontrado / boss de nível pendente\n"
                "`juntar boss` — Entra na batalha de boss de outro jogador\n"
                "`iniciar batalha boss` — Inicia a batalha após juntar jogadores\n"
                "`defender cidade` — Modo defesa cooperativo contra invasão"
            ),
            inline=False
        )
        e2.add_field(
            name="⚠️ Boss de Nível (9 / 19 / 29 / ... / 189 / 199)",
            value=(
                "Ao atingir esses níveis, um **boss bloqueia seu XP!**\n"
                "🔒 XP continua acumulando em segundo plano durante o bloqueio\n"
                "🏆 Ao vencer, o XP acumulado é liberado de uma vez!\n"
                "`desafiar boss` para enfrentar | `treinar *` para se preparar"
            ),
            inline=False
        )
        e2.add_field(
            name="⚔️ PvP",
            value=(
                "`desafiar @jogador` — Desafia outro jogador para duelo PvP\n"
                "Vencedor ganha XP e coins do perdedor!"
            ),
            inline=False
        )
        e2.set_footer(text="Página 2/5 — Use 'comandos 3' para continuar")

        # ── Página 3: Pets, Empregos, Quests, Mapa ─────────────────────
        e3 = discord.Embed(
            title="📋 COMANDOS — World CSI  [3/5]",
            description="*Pets, fazenda, empregos, quests e mapa*",
            color=0xF39C12
        )
        e3.add_field(
            name="🐾 Pets & Fazenda",
            value=(
                "`procurar pet` — Procura pets disponíveis na região\n"
                "`domesticar` — Tenta domesticar o pet encontrado\n"
                "`evoluir pet` — Evolui seu pet ativo (requer nível do jogador)\n"
                "`fazenda` / `ver fazenda` — Ver todos os seus pets armazenados\n"
                "`trocar pet [nome]` — Define um pet da fazenda como ativo\n"
                "`guardar pet` — Envia o pet ativo para a fazenda\n"
                "`stats pet` — Ver stats detalhados do pet ativo\n"
                "*Pets participam automaticamente das batalhas de boss!*"
            ),
            inline=False
        )
        e3.add_field(
            name="🐾 Formas Especiais de Pets",
            value=(
                "`quarta forma pet` — Exclusivo de pets **Comuns**! (Nível 3+)\n"
                "  *Uma 4ª forma que nenhum pet raro jamais alcançará*\n"
                "`forma bestial pet` — Exclusivo de pets **Lendário+**! (Nível 80+)\n"
                "  *Transformação permanente — não tem volta!*\n"
                "`ajuda formas pet` — Explicação completa das formas especiais"
            ),
            inline=False
        )
        e3.add_field(
            name="💼 Empregos",
            value=(
                "`procurar emprego` — Lista empregos disponíveis\n"
                "`ver emprego` — Ver emprego atual e progresso\n"
                "`trabalhar` — Trabalha no emprego atual (ganha coins e XP)\n"
                "`largar emprego` — Larga o emprego atual\n"
                "`defender cidade` — Trabalho especial do emprego de guarda\n"
                "🔨 **Ferreiro (nível 5+):** `forjar armas` e `fundir [raridade]`\n"
                "  *Funde 5 itens da mesma raridade para tentar subir a raridade!*"
            ),
            inline=False
        )
        e3.add_field(
            name="📋 Quests",
            value=(
                "`ver quests` — Lista de quests disponíveis na região atual\n"
                "`realizar quest` — Inicia / ver status da quest ativa\n"
                "`finalizar quest` — Entrega a quest concluída por recompensas\n"
                "`abandonar quest` — Abandona a quest ativa\n"
                "`cenário` — Evento moral aleatório (escolhas afetam alinhamento)\n"
                "`missão moral` — Quest especial baseada no alinhamento atual"
            ),
            inline=False
        )
        e3.add_field(
            name="🗺️ Mapa & Viagem",
            value=(
                "`abrir mapa` — Ver o mapa com todos os reinos disponíveis\n"
                "`procurar cidade` — Procura cidades próximas para viajar\n"
                "`viajar [local]` — Viaja para outro reino (precisa ter desbloqueado)\n"
                "*Ao vencer boss de nível, você viaja automaticamente ao próximo reino!*"
            ),
            inline=False
        )
        e3.set_footer(text="Página 3/5 — Use 'comandos 4' para continuar")

        # ── Página 4: Itens, Magia, Guilda, Reino ──────────────────────
        e4 = discord.Embed(
            title="📋 COMANDOS — World CSI  [4/5]",
            description="*Itens, magias, guildas, reinos e mundo próprio*",
            color=0x9B59B6
        )
        e4.add_field(
            name="🛒 Itens & Equipamentos",
            value=(
                "`equipar [nome do item]` — Equipa arma ou armadura do inventário\n"
                "`[item], usar` — Usa uma poção (ex: `poção de vida, usar`)\n"
                "`usar poção` / `beber [poção]` — Usa poção pelo nome\n"
                "`vender [item]` — Vende um item por coins\n"
                "`trocar [item] com @user` — Troca itens com outro jogador\n"
                "`trocar coins` / `converter coins` — Converte coins para CSI"
            ),
            inline=False
        )
        e4.add_field(
            name="✨ Magias & Livro de Feitiços",
            value=(
                "`livro de feitiços` — Abre o livro (desbloqueia no **Nível 12**)\n"
                "`feitiços` / `ver feitiços` — Ver feitiços disponíveis\n"
                "`avançar categoria mana` — Sobe de categoria no livro de feitiços\n"
                "`treinar mana` — Treina a mana para desbloquear novas categorias\n"
                "`curar @aliado` — Cura um aliado (Paladino / Druida / Mago / Bardo)"
            ),
            inline=False
        )
        e4.add_field(
            name="🏰 Guilda",
            value=(
                "`criar guilda [nome]` — Cria uma guilda\n"
                "`entrar guilda [nome]` — Entra em uma guilda existente\n"
                "`ver guilda` — Ver membros e stats da guilda\n"
                "*Guildas compartilham XP e têm rankings próprios!*"
            ),
            inline=False
        )
        e4.add_field(
            name="👑 Sistema de Reino",
            value=(
                "`me tornar rei` — Proclama-se rei (requer nível alto)\n"
                "`meu reino` — Ver status do seu reino\n"
                "`personalizar reino [nome]` — Renomeia o reino\n"
                "`melhorar economia` — Investe na economia do reino\n"
                "`reforçar exercito` — Reforça o exército\n"
                "`atacar reino @rei` — Declara guerra ao reino de outro jogador\n"
                "`trocar recursos @rei [valor]` — Troca recursos com outro reino\n"
                "`nomear cavaleiro @user` — Nomeia um jogador cavaleiro do seu reino"
            ),
            inline=False
        )
        e4.add_field(
            name="🌍 Mundo Próprio",
            value=(
                "`criar mundo próprio` — Cria um canal privado só seu no servidor!\n"
                "  *Pode ser usado em qualquer canal — cria na categoria Monstrinho*\n"
                "`adicionar jogador @user` — No seu canal, dá permissão a outro jogador\n"
                "  *Use dentro do seu canal mundo próprio*\n"
                "*Todos os comandos do bot funcionam no mundo próprio!*"
            ),
            inline=False
        )
        e4.add_field(
            name="🌙 Período, Clima & AFK",
            value=(
                "`período` — Ver período atual (dia/entardecer/noite/madrugada)\n"
                "`descansar` — Avança o período e restaura HP e Mana\n"
                "`clima` — Ver clima atual (afeta drops e XP)\n"
                "`farm afk` — Ativa/desativa farm AFK (+XP por minuto)\n"
                "  *Use novamente ao voltar para coletar o XP acumulado!*"
            ),
            inline=False
        )
        e4.set_footer(text="Página 4/5 — Use 'comandos 5' para continuar")

        # ── Página 5: NPCs, Fusão, Sistemas Especiais ──────────────────
        e5 = discord.Embed(
            title="📋 COMANDOS — World CSI  [5/5]",
            description="*NPCs, fusão de itens, sistemas especiais e dicas*",
            color=0xE74C3C
        )
        e5.add_field(
            name="🗣️ Dialogar com NPCs",
            value=(
                "`dialogar com npc [nome]` — Conversa com um NPC do mundo\n"
                "  *NPCs disponíveis:* Theron, Elara, Sylvara, Bjorn, Ramses,\n"
                "  Spectra, Imperador Astral, Mercador Brynn, Capitão Aldric\n"
                "**Tipos de resposta (aleatório):**\n"
                "• 50% → **Lore** — história do mundo e backstory do NPC\n"
                "• 25% → **Segredo** — dicas ocultas e mecânicas escondidas\n"
                "• 25% → **Quest Oculta** — quests exclusivas com ótimas recompensas!"
            ),
            inline=False
        )
        e5.add_field(
            name="🔨 Fusão de Itens (Ferreiro nível 5+)",
            value=(
                "`forjar armas` — Abre o menu de fusão de itens\n"
                "`fundir [raridade]` — Funde 5 itens da raridade indicada\n"
                "  *Ex:* `fundir comum` | `fundir raro` | `fundir épico`\n"
                "**Resultados possíveis:**\n"
                "• 60% → Sobe para próxima raridade *(Comum→Incomum→Raro→...)*\n"
                "• 25% → Fica na mesma raridade (reduzido para 2 itens)\n"
                "• 15% → Todos os 5 itens são destruídos!\n"
                "*Cadeia:* Comum → Incomum → Raro → Épico → Lendário → Mítico → Ancestral → Divino → Primordial"
            ),
            inline=False
        )
        e5.add_field(
            name="💬 NPC Lore (Legado)",
            value=(
                "`falar npc especial` — Conversa aleatória com NPC de lore\n"
                "`npc lore` — Mesma função"
            ),
            inline=False
        )
        e5.add_field(
            name="💡 Dicas Importantes",
            value=(
                "• **Drops:** Monstros dropam até **Épico** | Bosses dropam **Mítico+**\n"
                "• **Pets:** Participam automaticamente de batalhas de boss!\n"
                "• **Boss de Nível:** XP acumula durante o bloqueio e é liberado ao vencer\n"
                "• **Raça:** Só pode ser escolhida uma vez — escolha com cuidado!\n"
                "• **Classe:** Pode ser trocada, mas perde bônus da antiga\n"
                "• **Mundo Próprio:** Canal privado funciona com TODOS os comandos\n"
                "• Use `atualização` para ver o que foi adicionado recentemente!"
            ),
            inline=False
        )
        e5.set_footer(text="World CSI Bot — Use 'atualização' para ver novidades | 'comandos' para esta lista")

        # Enviar todos os 5 embeds
        await message.channel.send(embed=e1)
        await message.channel.send(embed=e2)
        await message.channel.send(embed=e3)
        await message.channel.send(embed=e4)
        await message.channel.send(embed=e5)
        return

    # ── PÁGINAS INDIVIDUAIS DE COMANDOS ────────────────────────────────
    if content in ["comandos 1"]:
        e1 = discord.Embed(title="📋 COMANDOS [1/5] — Personagem & Início", color=0x3498DB)
        e1.add_field(name="👤 Personagem", value="`ver perfil` | `inventário` | `escolher raça` | `evoluir raça` | `escolher classe` | `habilidades` | `evolução classe` | `ver mana`", inline=False)
        e1.add_field(name="💪 Treinamento", value="`treinar força` | `treinar defesa` | `treinar vitalidade` | `treinar intensivo`", inline=False)
        e1.add_field(name="🏆 Conquistas", value="`ver conquistas` | `alinhamento` | `ver títulos`", inline=False)
        e1.add_field(name="🌟 Evoluções", value="Nível 40/80/120/160 — evolução automática com bônus escalonados!\nTier I ×1 → Tier II ×2.5 → Tier III ×5 → Tier IV ×10", inline=False)
        await message.channel.send(embed=e1)
        return
    if content in ["comandos 2"]:
        e2 = discord.Embed(title="📋 COMANDOS [2/5] — Exploração & Combate", color=0x2ECC71)
        e2.add_field(name="🌍 Exploração", value="`explorar` | `coletar` | `minerar` | `dungeon` | `procurar dungeon`", inline=False)
        e2.add_field(name="👹 Boss", value="`encontrar boss` | `desafiar boss` | `juntar boss` | `iniciar batalha boss`", inline=False)
        e2.add_field(name="⚠️ Boss de Nível", value="Nos níveis 9/19/29/.../199 o XP é bloqueado até vencer o boss!", inline=False)
        e2.add_field(name="⚔️ PvP", value="`desafiar @jogador`", inline=False)
        await message.channel.send(embed=e2)
        return
    if content in ["comandos 3"]:
        e3 = discord.Embed(title="📋 COMANDOS [3/5] — Pets, Empregos & Quests", color=0xF39C12)
        e3.add_field(name="🐾 Pets", value="`procurar pet` | `domesticar` | `evoluir pet` | `fazenda` | `ver fazenda` | `trocar pet` | `guardar pet` | `stats pet`", inline=False)
        e3.add_field(name="🐾 Formas Especiais", value="`quarta forma pet` (Comuns, nível 3+) | `forma bestial pet` (Lendário+, nível 80+)", inline=False)
        e3.add_field(name="💼 Empregos", value="`procurar emprego` | `ver emprego` | `trabalhar` | `largar emprego` | `forjar armas` | `fundir [raridade]`", inline=False)
        e3.add_field(name="📋 Quests", value="`ver quests` | `realizar quest` | `finalizar quest` | `abandonar quest` | `cenário` | `missão moral`", inline=False)
        e3.add_field(name="🗺️ Mapa", value="`abrir mapa` | `procurar cidade` | `viajar [local]`", inline=False)
        await message.channel.send(embed=e3)
        return
    if content in ["comandos 4"]:
        e4 = discord.Embed(title="📋 COMANDOS [4/5] — Itens, Magia, Guilda & Reino", color=0x9B59B6)
        e4.add_field(name="🛒 Itens", value="`equipar [item]` | `[item], usar` | `usar poção` | `vender [item]` | `trocar [item] com @user`", inline=False)
        e4.add_field(name="✨ Magias", value="`livro de feitiços` | `avançar categoria mana` | `treinar mana` | `curar @aliado`", inline=False)
        e4.add_field(name="🏰 Guilda", value="`criar guilda [nome]` | `entrar guilda [nome]` | `ver guilda`", inline=False)
        e4.add_field(name="👑 Reino", value="`me tornar rei` | `meu reino` | `personalizar reino [nome]` | `melhorar economia` | `reforçar exercito` | `atacar reino @rei`", inline=False)
        e4.add_field(name="🌍 Mundo Próprio", value="`criar mundo próprio` | `adicionar jogador @user` (dentro do canal)", inline=False)
        e4.add_field(name="🌙 AFK & Clima", value="`farm afk` | `período` | `descansar` | `clima`", inline=False)
        await message.channel.send(embed=e4)
        return
    if content in ["comandos 5"]:
        e5 = discord.Embed(title="📋 COMANDOS [5/5] — NPCs, Fusão & Dicas", color=0xE74C3C)
        e5.add_field(name="🗣️ NPCs", value="`dialogar com npc [nome]` — Lore, segredos e quests ocultas!\nNPCs: Theron, Elara, Sylvara, Bjorn, Ramses, Spectra, Imperador Astral...", inline=False)
        e5.add_field(name="🔨 Fusão", value="`forjar armas` | `fundir [raridade]` — Ferreiro nível 5+\n60% sobe raridade | 25% fica igual | 15% tudo destruído!", inline=False)
        e5.add_field(name="💡 Dicas", value="Drops Épico+ só em bosses | Pets participam de boss | `atualização` para novidades", inline=False)
        await message.channel.send(embed=e5)
        return

    # ── ATUALIZAÇÃO / NOVIDADES / CHANGELOG ────────────────────────────
    if content in ["atualização", "atualizacao", "novidades", "update", "changelog", "o que é novo", "o que foi adicionado", "novidades do bot", "patch notes"]:
        e_atu = discord.Embed(
            title="📰 ATUALIZAÇÃO — World CSI",
            description=(
                "**Última atualização:** Fevereiro 2026\n"
                "*Confira tudo que foi adicionado ao bot recentemente!*"
            ),
            color=0xFF6B00
        )
        e_atu.add_field(
            name="🌍 Mundo Próprio",
            value=(
                "**Comando:** `criar mundo próprio`\n"
                "Cria um canal de texto privado só seu no servidor!\n"
                "• Pode ser usado em **qualquer canal** do servidor\n"
                "• Canal criado na categoria **╭━━━━━✦Monstrinho**\n"
                "• Todos podem **ver** mas só você pode **escrever**\n"
                "• **Todos os comandos do bot funcionam** dentro do canal\n"
                "• Use `adicionar jogador @user` (dentro do canal) para convidar alguém"
            ),
            inline=False
        )
        e_atu.add_field(
            name="🔨 Sistema de Fusão de Itens",
            value=(
                "**Requer:** Emprego de Ferreiro (nível 5+)\n"
                "**Comando:** `forjar armas` para menu | `fundir [raridade]` para fundir\n"
                "• Funde **5 itens** da mesma raridade em 1\n"
                "• **60%** chance de subir para a próxima raridade\n"
                "• **25%** fica na mesma raridade (mas você recebe só 2 itens)\n"
                "• **15%** todos os itens são destruídos — cuidado!\n"
                "• Cadeia completa: Comum→Incomum→Raro→Épico→Lendário→Mítico→Ancestral→Divino→Primordial"
            ),
            inline=False
        )
        e_atu.add_field(
            name="🐾 Quarta Forma — Pets Comuns (NOVO)",
            value=(
                "**Comando:** `quarta forma pet`\n"
                "Pets de raridade **Comum** têm uma quarta forma exclusiva!\n"
                "• Requer **Nível 3+** do jogador\n"
                "• **Pets comuns disponíveis** nos mundos 1, 10 e 20:\n"
                "  Slime Bebê, Rato Selvagem Domesticado, Lagarta Arcana,\n"
                "  Fungo Espiritual, Toupeira das Sombras, Cogumelo Sombrio,\n"
                "  Besouro do Deserto, Cobra das Areias\n"
                "• Pets sem forma registrada ganham a forma **[Nome] Desperto**\n"
                "*Uma forma que NENHUM pet raro jamais alcançará!*"
            ),
            inline=False
        )
        e_atu.add_field(
            name="🐺 Forma Bestial — Pets Lendário+",
            value=(
                "**Comando:** `forma bestial pet`\n"
                "Pets **Lendário ou superior** podem despertar a Forma Bestial!\n"
                "• Requer **Nível 80** do jogador\n"
                "• Transformação **permanente** — não tem volta!\n"
                "• Bônus massivos de HP e ATK\n"
                "• Pets suportados: Lobo Alpha, Esfinge, Fênix, Dragão de Gelo,\n"
                "  Arcanjo Primordial, Deus Primordial e mais!\n"
                "• Use `ajuda formas pet` para ver todos os detalhes"
            ),
            inline=False
        )
        e_atu.add_field(
            name="🌟 Status Escalonados na Evolução de Classe",
            value=(
                "As evoluções de classe agora dão **bônus crescentes por tier!**\n"
                "• **Tier I (nível 40):** ×1 base — primeira especialização\n"
                "• **Tier II (nível 80):** ×2.5 + bônus extra (+50 HP mín, +30 ATK mín)\n"
                "• **Tier III (nível 120):** ×5 + bônus grande (+200 HP mín, +80 ATK mín)\n"
                "• **Tier IV (nível 160):** ×10 + poder divino (+500 HP mín, +200 ATK mín)\n"
                "*Cada tier tem visual diferente: 🔵 → 🌟 → 🔥 → 👑*"
            ),
            inline=False
        )
        e_atu.add_field(
            name="🗣️ Sistema de Diálogo com NPCs",
            value=(
                "**Comando:** `dialogar com npc [nome]`\n"
                "• **50%** chance de ouvir **lore** do mundo e do NPC\n"
                "• **25%** chance de revelar um **segredo** oculto do jogo\n"
                "• **25%** chance de desbloquear uma **quest oculta** exclusiva!\n"
                "NPCs disponíveis: Theron, Elara, Sylvara, Bjorn, Ramses,\n"
                "Spectra, Imperador Astral, Mercador Brynn, Capitão Aldric"
            ),
            inline=False
        )
        e_atu.add_field(
            name="📋 Lista de Comandos Renovada",
            value=(
                "O comando `comandos` foi completamente refeito!\n"
                "Agora envia **5 embeds separados** com TODOS os comandos explicados:\n"
                "`comandos` — todos de uma vez | `comandos 1` a `comandos 5` — página individual\n"
                "Use `atualização` a qualquer hora para rever este changelog."
            ),
            inline=False
        )
        e_atu.set_footer(text="World CSI Bot — Use 'comandos' para ver todos os comandos disponíveis")
        await message.channel.send(embed=e_atu)
        return

    # ======================================================
    # ================= EXPLORAR ===========================
    # ======================================================
    if any(word in content for word in ["explorar", "vou explorar", "andar", "caminhar", "vou para"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        roll = roll_with_bonus(player)
        luck = get_luck(roll)
        event = random.choice(world["events"])

        embed = discord.Embed(
            title=f"{world['emoji']} {world['name']}",
            description=f"*'{event}'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado do Destino", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll == 1:
            result, xp_loss = remove_xp(user_id, random.randint(30, 50))
            embed.add_field(
                name="💀 Desastre!",
                value=f"*'Seus passos tropeçam no destino cruel!'*\n\n❌ **−{xp_loss} XP**",
                inline=False
            )
            if result == "reset":
                embed.add_field(name="🌑 Fim da Jornada", value="*'Sua história encontra um fim abrupto...'*\n\n**Você desperta nos Campos Iniciais.**", inline=False)
                embed.color = discord.Color.dark_red()

        elif roll == 2:
            result, xp_loss = remove_xp(user_id, random.randint(15, 30))
            embed.add_field(name="☠️ Infortúnio", value=f"*'Nem sempre o caminho é gentil...'*\n\n❌ **−{xp_loss} XP**", inline=False)
            embed.color = discord.Color.red()

        elif roll in [3, 4]:
            embed.add_field(name="😐 Nada de Especial", value="*'Você continua sua jornada sem nada digno de nota.'*", inline=False)
            embed.color = discord.Color.light_grey()

        elif roll == 5:
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(5, 15), player["max_hp"])
            save_player_db(user_id, player)
            embed.add_field(name="😶 Descoberta Modesta", value=f"*'Você encontra algo que pode ser útil...'*\n\n📦 **{res}**", inline=False)

            # Progresso de quest
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await complete_quest(message.channel, user_id, player)
                else:
                    save_player_db(user_id, player)

        elif roll in [6, 7]:
            xp = random.randint(20, 40)
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(10, 20), player["max_hp"])
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)

            embed.add_field(name="🙂 Boa Descoberta!", value=f"*'A sorte está ao seu lado hoje!'*\n\n📦 **{res}**\n⭐ **+{xp} XP**", inline=False)
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Evolução!", value=f"*'Um novo capítulo se abre!'*\n\n**Nível {player['level']}**", inline=False)
                embed.color = discord.Color.gold()
            else:
                embed.color = discord.Color.green()

            # Progresso de quest explore
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "explore":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await complete_quest(message.channel, user_id, player)
                else:
                    save_player_db(user_id, player)

        elif roll == 8:
            xp = random.randint(40, 70)
            resources = random.sample(world["resources"], min(2, len(world["resources"])))
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(15, 30), player["max_hp"])

            # Chance de dungeon secreta ao explorar
            secret_found = False
            if "secret_dungeons" in world and random.random() < 0.15:
                secret_dungeon = random.choice(world["secret_dungeons"])
                secret_found = True
                embed.add_field(
                    name="🔮 Dungeon Secreta Encontrada!",
                    value=f"*'Explorando os arredores, você descobre uma entrada oculta...'*\n\n**{secret_dungeon['name']}**",
                    inline=False
                )

            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="🍀 Tesouro Escondido!", value=f"*'Seus olhos captam o que outros perderiam!'*\n\n{items_text}\n⭐ **+{xp} XP**", inline=False)
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.green()

            if secret_found:
                await message.channel.send(embed=embed)
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 **Dungeon Secreta!** Deseja explorar?", view=view)
                return

        elif roll == 9:
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            rarity = random.choices(["Incomum", "Raro", "Épico"], weights=[55, 35, 10])[0]
            items_filtered = [i for i in ITEMS[item_list] if i["rarity"] == rarity]
            item = random.choice(items_filtered) if items_filtered else random.choice(ITEMS[item_list])
            xp = random.randint(60, 100)
            leveled = add_xp(user_id, xp)
            rarity_info = RARITIES[item["rarity"]]
            embed.add_field(
                name="✨ Descoberta Rara!",
                value=f"*'Seus olhos brilham ao ver algo extraordinário!'*\n\n{rarity_info['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = rarity_info["color"]
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(f"✨ **{item['name']}** aguarda!\n\n*'Deseja equipar?'*", view=view)
            await check_level_boss(message.channel, user_id)
            return

        else:  # roll == 10
            item_type = random.choice(["weapon", "armor"])
            item_list = "weapons" if item_type == "weapon" else "armor"
            epic_pool = [i for i in ITEMS[item_list] if i["rarity"] in ["Raro", "Épico", "Lendário"]]
            item = random.choice(epic_pool) if epic_pool else random.choice(ITEMS[item_list])
            xp = random.randint(120, 200)
            leveled = add_xp(user_id, xp)
            embed.add_field(
                name="🌟 EVENTO LENDÁRIO!",
                value=f"*'OS DEUSES SORRIEM PARA VOCÊ!'*\n\n{RARITIES[item['rarity']]['emoji']} **{item['name']}**\n⭐ **+{xp} XP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Ascensão!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.gold()
            await message.channel.send(embed=embed)
            await asyncio.sleep(1)
            view = EquipButton(user_id, item["name"], item_type)
            await message.channel.send(f"🌟 **{item['name']}** pulsa com poder divino!\n\n*'Deseja equipar?'*", view=view)
            await check_level_boss(message.channel, user_id)
            return

        await message.channel.send(embed=embed)
        # Track exploration
        p_explore = get_player(user_id)
        if roll >= 5:  # Count successful explorations
            p_explore["areas_explored"] = p_explore.get("areas_explored", 0) + 1
            save_player_db(user_id, p_explore)
        await check_achievements(message.channel, user_id)
        await check_level_boss(message.channel, user_id)
        return

    # ======================================================
    # ================= CAÇAR ==============================
    # ======================================================
    elif any(word in content for word in ["caçar", "cacar", "lutar", "atacar", "batalhar"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        monster_name = random.choice(list(world["monsters"].keys()))
        monster = world["monsters"][monster_name]
        roll = roll_with_bonus(player)
        luck = get_luck(roll)

        embed = discord.Embed(
            title=f"⚔️ Encontro de Batalha",
            description=f"*'Um **{monster_name}** surge diante de você!'*",
            color=discord.Color.red()
        )
        embed.add_field(name="🎲 Dado da Batalha", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            dmg = random.randint(10, 30)
            player = get_player(user_id)
            player["hp"] -= dmg
            if player["hp"] <= 0:
                player["hp"] = player["max_hp"] // 2
            save_player_db(user_id, player)
            result, xp_loss = remove_xp(user_id, random.randint(20, 40))
            embed.add_field(
                name="💀 Derrota Dolorosa",
                value=f"*'O {monster_name} te supera!'*\n\n❌ **−{xp_loss} XP**\n💔 **−{dmg} HP**",
                inline=False
            )
            embed.color = discord.Color.dark_red()

        elif roll <= 5:
            xp = random.randint(monster["xp"][0], monster["xp"][0] + 5)
            coins = random.randint(monster["coins"][0], monster["coins"][1])
            dmg = random.randint(5, 15)
            player = get_player(user_id)
            player["hp"] -= dmg
            save_player_db(user_id, player)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            embed.add_field(
                name="😓 Vitória Suada",
                value=f"*'A batalha foi feroz, mas você prevalece!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**\n💔 **−{dmg} HP**",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Crescimento!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.orange()

        elif roll <= 7:
            xp = random.randint(monster["xp"][0], monster["xp"][1])
            coins = random.randint(monster["coins"][0], monster["coins"][1])
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)
            # Chance de drop de poção (baixa)
            drop_potion = None
            if random.random() < 0.05:
                potion_list = [name for name, data in POTIONS.items() if data["rarity"] in ["Comum", "Incomum"]]
                drop_potion = random.choice(potion_list)
                p2 = get_player(user_id)
                p2["inventory"].append(drop_potion)
                save_player_db(user_id, p2)

            potion_text = f"\n🧪 Drop: **{drop_potion}**" if drop_potion else ""
            embed.add_field(
                name="⚔️ Vitória!",
                value=f"*'Cada golpe seu é preciso!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{potion_text}",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.green()

            # Track monster kill
            p_kill2 = get_player(user_id)
            p_kill2["monsters_killed"] = p_kill2.get("monsters_killed", 0) + 1
            save_player_db(user_id, p_kill2)

            # Progresso de quest de caça
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "hunt":
                if player["active_quest"].get("target", "") in monster_name or monster_name in player["active_quest"].get("target", ""):
                    player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                    if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                        await message.channel.send(embed=embed)
                        await complete_quest(message.channel, user_id, player)
                        return
                    else:
                        save_player_db(user_id, player)

        else:  # 8-10
            xp = random.randint(monster["xp"][1], monster["xp"][1] + 15)
            coins = random.randint(monster["coins"][1], monster["coins"][1] + 5)
            leveled = add_xp(user_id, xp)
            add_coins(user_id, coins)

            drop_item = None
            drop_item = None
            drop_potion = None

            # Caçar: dropa armas/armaduras dos monstros (máx Épico — Mítico+ APENAS de boss)
            monster_drops_pool = MONSTER_DROPS.get(monster_name, MONSTER_DROPS.get("default", []))
            allowed_rarities = ("Comum", "Incomum", "Raro", "Épico")
            equip_drops = [d for d in monster_drops_pool if d.get("type") in ("weapon", "armor")
                           and d.get("rarity") in allowed_rarities]
            # Chance de drop de equipamento baseada no dado (roll 8-10 já é alto)
            drop_chance = 0.25 if roll >= 9 else 0.15
            if equip_drops and random.random() < drop_chance:
                drop_def = random.choice(equip_drops)
                rarity = drop_def["rarity"]
                itype = drop_def["type"]
                ilist = "weapons" if itype == "weapon" else "armor"
                items_filtered = [i for i in ITEMS[ilist] if i["rarity"] == rarity]
                if items_filtered:
                    drop_item = random.choice(items_filtered)
                    p2 = get_player(user_id)
                    p2["inventory"].append(drop_item["name"])
                    save_player_db(user_id, p2)

            # 8% chance poção Comum/Incomum
            if random.random() < 0.08:
                potion_rarities = ["Comum", "Incomum"]
                drop_potion = random.choice([name for name, data in POTIONS.items() if data["rarity"] in potion_rarities])
                p2 = get_player(user_id)
                p2["inventory"].append(drop_potion)
                save_player_db(user_id, p2)

            drop_text = ""
            if drop_item:
                drop_text += f"\n{RARITIES[drop_item['rarity']]['emoji']} **{drop_item['name']}** ({drop_item['rarity']}) — drop do monstro!"
            if drop_potion:
                drop_text += f"\n🧪 **{drop_potion}**!"

            embed.add_field(
                name="✨ Domínio Total!",
                value=f"*'Vitória absoluta!'*\n\n⭐ **+{xp} XP**\n💰 **+{coins} CSI**{drop_text}",
                inline=False
            )
            if leveled:
                player = get_player(user_id)
                embed.add_field(name="🆙 Evolução!", value=f"**Nível {player['level']}**", inline=False)
            embed.color = discord.Color.gold()

            # Track monster kill
            p_kill = get_player(user_id)
            p_kill["monsters_killed"] = p_kill.get("monsters_killed", 0) + 1
            save_player_db(user_id, p_kill)

            await message.channel.send(embed=embed)

            # Progresso de quest de caça
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "hunt":
                if player["active_quest"].get("target", "") in monster_name or monster_name in player["active_quest"].get("target", ""):
                    player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                    if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                        await complete_quest(message.channel, user_id, player)
                        return
                    else:
                        save_player_db(user_id, player)

            await check_achievements(message.channel, user_id)
            await check_level_boss(message.channel, user_id)
            return

        await message.channel.send(embed=embed)
        await check_level_boss(message.channel, user_id)
        return

    # ======================================================
    # ================= COLETAR ============================
    # ======================================================
    elif any(word in content for word in ["coletar", "minerar", "colher", "pegar recursos"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        roll = roll_with_bonus(player)
        luck = get_luck(roll)

        embed = discord.Embed(
            title=f"⛏️ Coleta de Recursos",
            description=f"*'Você procura cuidadosamente por recursos valiosos...'*",
            color=discord.Color.blue()
        )
        embed.add_field(name="🎲 Dado da Sorte", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            embed.add_field(name="😔 Busca Infrutífera", value="*'Suas mãos voltam vazias...'*", inline=False)
            embed.color = discord.Color.light_grey()

            # Chance de dungeon secreta ao minerar (baixa)
            if "secret_dungeons" in world and random.random() < 0.08:
                secret_dungeon = random.choice(world["secret_dungeons"])
                embed.add_field(
                    name="🔮 Mas você encontra algo...",
                    value=f"*'Enquanto minerava, você descobre uma entrada oculta: **{secret_dungeon['name']}**!'*",
                    inline=False
                )
                await message.channel.send(embed=embed)
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
                return

        elif roll <= 6:
            res = random.choice(world["resources"])
            player = get_player(user_id)
            player["inventory"].append(res)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(10, 20), player["max_hp"])
            save_player_db(user_id, player)
            embed.add_field(name="📦 Recurso Encontrado", value=f"*'Você encontra algo útil!'*\n\n**{res}**", inline=False)
            embed.color = discord.Color.green()

            # Progresso quest coleta
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 1
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

        elif roll <= 8:
            resources = [random.choice(world["resources"]) for _ in range(2)]
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(15, 30), player["max_hp"])
            save_player_db(user_id, player)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="🍀 Coleta Proveitosa!", value=f"*'Múltiplos recursos encontrados!'*\n\n{items_text}", inline=False)
            embed.color = discord.Color.green()

            # Progresso quest
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + 2
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

        else:  # 9-10
            count = 3 if roll == 9 else 4
            resources = [random.choice(world["resources"]) for _ in range(count)]
            player = get_player(user_id)
            for r in resources:
                player["inventory"].append(r)
            if player.get("class") == "Druida":
                player["hp"] = min(player["hp"] + random.randint(20, 40), player["max_hp"])

            # Dungeon secreta ao minerar (chance maior em 9-10)
            secret_found = False
            if "secret_dungeons" in world and random.random() < 0.2:
                secret_dungeon = random.choice(world["secret_dungeons"])
                secret_found = True
                embed.add_field(
                    name="🔮 Dungeon Secreta Revelada!",
                    value=f"*'Sua ferramenta perfura uma parede falsa e revela: **{secret_dungeon['name']}**!'*",
                    inline=False
                )

            save_player_db(user_id, player)
            items_text = "\n".join([f"• **{r}**" for r in resources])
            embed.add_field(name="✨ Coleta Abundante!", value=f"*'Uma descoberta magnífica!'*\n\n{items_text}", inline=False)
            embed.color = discord.Color.gold()

            # Progresso quest
            player = get_player(user_id)
            if player.get("active_quest") and player["active_quest"].get("objective") == "collect":
                player["active_quest"]["progress"] = player["active_quest"].get("progress", 0) + count
                if player["active_quest"]["progress"] >= player["active_quest"].get("count", 1):
                    await message.channel.send(embed=embed)
                    if secret_found:
                        view = DungeonSelectButton(user_id, [secret_dungeon], world)
                        await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
                    await complete_quest(message.channel, user_id, player)
                    return
                else:
                    save_player_db(user_id, player)

            await message.channel.send(embed=embed)
            if secret_found:
                await asyncio.sleep(1)
                view = DungeonSelectButton(user_id, [secret_dungeon], world)
                await message.channel.send("🔮 Explorar a dungeon secreta?", view=view)
            return

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= DUNGEON ============================
    # ======================================================
    elif any(word in content for word in ["achar dungeon", "procurar dungeon", "buscar dungeon", "dungeon"]):
        player = get_player(user_id)
        if player["level"] >= 2 and not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return

        world = get_world(player["level"], player)
        if "dungeons" not in world or not world["dungeons"]:
            await message.channel.send("*'Não há dungeons conhecidas nesta região...'*")
            return

        roll = roll_dice()
        luck = get_luck(roll)

        embed = discord.Embed(
            title="🗺️ Mapa de Dungeons da Região",
            description="*'Você consulta seu mapa e identifica as masmorras desta região...'*",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎲 Dado da Exploração", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=False)

        if roll <= 3:
            embed.add_field(name="❌ Exploração Fracassada", value="*'Você vaga por horas mas não encontra nenhuma entrada...'*", inline=False)
            embed.color = discord.Color.red()
            await message.channel.send(embed=embed)
            return

        # ─── DUNGEONS COMUNS (sempre visíveis) ─────────────────
        dungeons_comuns = list(world["dungeons"])
        embed.add_field(
            name="🏛️ ─── DUNGEONS COMUNS ───",
            value="*'Masmorras conhecidas da região. Explore para encontrar baús com recompensas e chaves!'*",
            inline=False
        )
        for i, dungeon in enumerate(dungeons_comuns, 1):
            embed.add_field(
                name=f"  {i}. {dungeon['name']} (Nível {dungeon['level']})",
                value=f"  ⚔️ Boss: **{dungeon['boss']}**\n  🎁 Baús podem conter: ouro, equipamentos, materiais raros e **chaves de dungeon secreta**",
                inline=False
            )

        # ─── DUNGEONS MISTERIOSAS / SECRETAS ─────────────────
        secret_dungeons_all = world.get("secret_dungeons", [])
        embed.add_field(
            name="🔮 ─── DUNGEON MISTERIOSA (SECRETA) ───",
            value="*'Masmorras ocultas e perigosas. Requerem uma Chave específica para entrar. Inimigos muito mais fortes — recompensas de raridade Mítica ou superior!'*",
            inline=False
        )

        if secret_dungeons_all:
            for sd in secret_dungeons_all:
                key_name = sd.get("key_name", "🗝️ Chave Desconhecida")
                has_key = player_has_key(player, key_name)
                key_status = f"✅ **Você TEM a chave!**" if has_key else f"🔒 Necessita: **{key_name}**\n  *(Encontre esta chave em baús de dungeons comuns desta região)*"
                drop_rarity = sd.get("special_boss_drop", "Mítico")
                rarity_info = RARITIES.get(drop_rarity, RARITIES["Mítico"])
                embed.add_field(
                    name=f"  🔮 {sd['name']} (Nível {sd['level']})",
                    value=(
                        f"  👹 Boss Especial: **{sd['boss']}**\n"
                        f"  {rarity_info['emoji']} Recompensa máxima: **{drop_rarity}**\n"
                        f"  {key_status}"
                    ),
                    inline=False
                )
        else:
            embed.add_field(name="  🔒 Sem dungeons secretas", value="  *'Nenhuma dungeon secreta foi descoberta nesta região.'*", inline=False)

        embed.color = discord.Color.gold()
        embed.set_footer(text="💡 Complete dungeons comuns para obter chaves | Chaves desbloqueiam dungeons secretas com drops Míticos ou superiores!")
        await message.channel.send(embed=embed)
        await asyncio.sleep(1)

        # Monta lista para seleção: comuns primeiro, depois secretas (com verificação de chave)
        dungeons_para_selecao = list(dungeons_comuns)
        if secret_dungeons_all and roll >= 6:
            for sd in secret_dungeons_all:
                key_name = sd.get("key_name", "")
                if player_has_key(player, key_name):
                    dungeons_para_selecao.append(sd)
                elif roll >= 9:  # Alta sorte: mostra secretas mesmo sem chave (mas não deixa entrar)
                    dungeons_para_selecao.append(dict(sd, **{"locked": True}))

        view = DungeonSelectButton(user_id, dungeons_para_selecao, world)
        await message.channel.send("*'Qual dungeon deseja explorar?'*", view=view)
        return

    # ======================================================
    # ================= VER PERFIL =========================
    # ======================================================
    elif any(word in content for word in ["ver perfil", "meu perfil", "perfil", "status"]):
        player = get_player(user_id)
        world = get_world(player["level"], player)
        xp_need = calc_xp(player["level"])

        embed = discord.Embed(
            title=f"👤 {message.author.display_name}",
            description=f"*'O narrador revela sua história até agora...'*",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="⭐ Nível", value=f"`{player['level']}`", inline=True)
        embed.add_field(name="✨ XP", value=f"`{player['xp']}/{xp_need}`", inline=True)
        embed.add_field(name="💰 Moedas CSI", value=f"`{player['coins']}`", inline=True)
        embed.add_field(name="❤️ HP", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)

        if player.get("class"):
            max_mana = calc_max_mana(player)
            cur_mana = player.get("mana", max_mana)
            embed.add_field(name="💙 Mana", value=f"`{cur_mana}/{max_mana}`", inline=True)

        if player.get("class"):
            class_data = CLASSES[player["class"]]
            spec = player.get("specialization")
            class_display = f"{player['class']}"
            if spec:
                spec_emoji = CLASS_SPECIALIZATIONS.get(spec, {}).get("emoji", "⭐")
                class_display += f" › {spec_emoji} {spec}"
            embed.add_field(name=f"{class_data['emoji']} Classe", value=class_display, inline=True)
        if player.get("race"):
            race_data = RACES.get(player["race"], {})
            race_stage = player.get("race_stage", 0)
            evos = RACE_EVOLUTION_TREE.get(player["race"], [])
            if race_stage > 0 and race_stage <= len(evos):
                evo_data = evos[race_stage - 1]
                race_display = f"{evo_data['name']} *(Estágio {race_stage}/3)*"
                race_emoji = evo_data['emoji']
            else:
                race_display = player["race"]
                race_emoji = race_data.get('emoji', '🧬')
                if evos:
                    next_req = evos[0]["level"]
                    if player.get("level", 1) >= next_req:
                        race_display += " ⚡ *(evolução disponível!)*"
            embed.add_field(name=f"{race_emoji} Raça", value=race_display, inline=True)
        if player.get("pet"):
            embed.add_field(name="🐉 Pet", value=player["pet"], inline=True)
        embed.add_field(name="🌍 Localização", value=f"{world['emoji']} **{world['name']}**", inline=False)
        embed.add_field(name="⚔️ Arma", value=player["weapon"] or "*Nenhuma*", inline=True)
        embed.add_field(name="🛡️ Armadura", value=player["armor"] or "*Nenhuma*", inline=True)
        embed.add_field(name="👹 Bosses Derrotados", value=f"`{len(player['bosses'])}`", inline=True)

        active_quest = player.get("active_quest")
        if active_quest:
            progress = active_quest.get("progress", 0)
            total = active_quest.get("count", 1)
            embed.add_field(name="📜 Quest Ativa", value=f"{active_quest['name']}\n**Progresso:** {progress}/{total}", inline=False)

        if player.get("guild_id"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT name FROM guilds WHERE id = ?", (player["guild_id"],))
            result = c.fetchone()
            conn.close()
            if result:
                embed.add_field(name="🏰 Guilda", value=result[0], inline=True)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= INVENTÁRIO =========================
    # ======================================================
    elif any(word in content for word in ["ver inventario", "inventario", "inventário", "mochila", "itens"]):
        player = get_player(user_id)
        embed = discord.Embed(
            title=f"🎒 Inventário de {message.author.display_name}",
            description=f"*'O narrador vasculha sua mochila...'*",
            color=discord.Color.gold()
        )

        if not player["inventory"]:
            embed.add_field(name="Vazio", value="*'Suas bolsas estão vazias...'*", inline=False)
        else:
            items_count = {}
            for item in player["inventory"]:
                items_count[item] = items_count.get(item, 0) + 1

            RARITY_ORDER = ["Primordial", "Divino", "Mítico", "Lendário", "Épico", "Raro", "Incomum", "Comum"]

            def get_item_rarity_name(item_name):
                for w in ITEMS["weapons"]:
                    if w["name"] == item_name:
                        return w.get("rarity", "Comum")
                for a in ITEMS["armor"]:
                    if a["name"] == item_name:
                        return a.get("rarity", "Comum")
                if item_name in POTIONS:
                    return POTIONS[item_name].get("rarity", "Comum")
                return "Comum"

            weapons_in_inv = [i for i in items_count if any(w["name"] == i for w in ITEMS["weapons"])]
            armors_in_inv = [i for i in items_count if any(a["name"] == i for a in ITEMS["armor"])]
            potions_in_inv = [i for i in items_count if i in POTIONS]
            resources_in_inv = [i for i in items_count if i not in potions_in_inv and i not in weapons_in_inv and i not in armors_in_inv]

            def sort_by_rarity(item_list):
                return sorted(item_list, key=lambda i: RARITY_ORDER.index(get_item_rarity_name(i)) if get_item_rarity_name(i) in RARITY_ORDER else 99)

            def format_items_by_rarity(item_list, category_emoji):
                lines = []
                for rarity in RARITY_ORDER:
                    r_items = [i for i in item_list if get_item_rarity_name(i) == rarity]
                    if r_items:
                        r_emoji = RARITIES.get(rarity, {}).get("emoji", "•")
                        for i in r_items:
                            lines.append(f"{r_emoji} **{i}** x{items_count[i]}")
                return lines

            fields_added = 0
            if weapons_in_inv:
                lines = format_items_by_rarity(weapons_in_inv, "⚔️")
                chunk = "\n".join(lines)[:1024]
                embed.add_field(name="⚔️ Armas", value=chunk or "—", inline=False)
                fields_added += 1
            if armors_in_inv:
                lines = format_items_by_rarity(armors_in_inv, "🛡️")
                chunk = "\n".join(lines)[:1024]
                embed.add_field(name="🛡️ Armaduras", value=chunk or "—", inline=False)
                fields_added += 1
            if potions_in_inv:
                lines = format_items_by_rarity(potions_in_inv, "🧪")
                chunk = "\n".join(lines)[:1024]
                embed.add_field(name="🧪 Poções", value=chunk or "—", inline=False)
                fields_added += 1
            if resources_in_inv:
                # Separar chaves de dungeon dos demais recursos
                keys_in_inv = [i for i in resources_in_inv if i.startswith("🗝️")]
                regular_resources = [i for i in resources_in_inv if not i.startswith("🗝️")]
                if keys_in_inv:
                    embed.add_field(
                        name="🗝️ Chaves de Dungeon Secreta",
                        value="\n".join([f"🗝️ **{i}** x{items_count[i]}" for i in keys_in_inv])[:1024],
                        inline=False
                    )
                if regular_resources:
                    embed.add_field(name="📦 Recursos", value="\n".join([f"• **{i}** x{items_count[i]}" for i in regular_resources])[:1024], inline=False)

            if player.get("weapon") or player.get("armor"):
                equip_txt = []
                if player.get("weapon"):
                    r = get_item_rarity_name(player["weapon"])
                    equip_txt.append(f"{RARITIES.get(r,{}).get('emoji','⚔️')} Arma: **{player['weapon']}**")
                if player.get("armor"):
                    r = get_item_rarity_name(player["armor"])
                    equip_txt.append(f"{RARITIES.get(r,{}).get('emoji','🛡️')} Armadura: **{player['armor']}**")
                embed.add_field(name="🎖️ Equipado", value="\n".join(equip_txt), inline=False)

        embed.set_footer(text=f"Total: {len(player['inventory'])} itens | Moedas CSI: {player['coins']:,} | Conquistas: {len(player.get('achievements', []))}/{len(ACHIEVEMENTS)}")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VER CHAVES ========================
    # ======================================================
    elif any(word in content for word in ["ver chaves", "minhas chaves", "chaves dungeon", "chaves"]):
        player = get_player(user_id)
        world = get_world(player["level"], player)

        keys_in_inv = [i for i in player.get("inventory", []) if i.startswith("🗝️")]
        keys_count = {}
        for k in keys_in_inv:
            keys_count[k] = keys_count.get(k, 0) + 1

        embed = discord.Embed(
            title=f"🗝️ Chaves de Dungeon de {message.author.display_name}",
            description="*'Chaves desbloqueiam as Dungeons Secretas de cada reino. Encontre-as em baús de dungeons comuns!'*",
            color=discord.Color.dark_gold()
        )

        if not keys_count:
            embed.add_field(name="🔒 Sem Chaves", value="*'Você não possui nenhuma chave de dungeon secreta ainda.'*\n\n💡 **Dica:** Explore dungeons comuns (comando `dungeon`) para encontrar chaves em baús!", inline=False)
        else:
            for key, qty in keys_count.items():
                embed.add_field(name=f"{key} x{qty}", value="✅ Pronta para usar! (use `dungeon` e selecione a dungeon secreta)", inline=False)

        # Mostrar quais chaves são necessárias no reino atual
        secret_dungeons = world.get("secret_dungeons", [])
        if secret_dungeons:
            needed_keys = []
            for sd in secret_dungeons:
                kn = sd.get("key_name", "")
                if kn and kn not in keys_count:
                    needed_keys.append(f"🔒 **{kn}** → Dungeon: {sd['name']}")
            if needed_keys:
                embed.add_field(
                    name=f"🔒 Chaves Necessárias no {world['name']}",
                    value="\n".join(needed_keys),
                    inline=False
                )

        embed.set_footer(text="Use 'dungeon' para ver e explorar dungeons | Baús de dungeons comuns podem conter chaves!")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VER MANA ==========================
    # ======================================================
    elif any(word in content for word in ["ver mana", "minha mana", "mana"]):
        player = get_player(user_id)
        max_mana = calc_max_mana(player)
        player["max_mana"] = max_mana
        if player.get("mana", 0) > max_mana:
            player["mana"] = max_mana
        save_player_db(user_id, player)

        cls = player.get("class", "Sem Classe")
        embed = discord.Embed(
            title="✨ Status de Mana",
            description=f"*O narrador examina sua energia arcana...*",
            color=discord.Color.blue()
        )
        mana_bar = "🔵" * (player["mana"] // 10) + "⚫" * ((max_mana - player["mana"]) // 10)
        embed.add_field(name="💙 Mana Atual", value=f"`{player['mana']}/{max_mana}`\n{mana_bar}", inline=False)
        if cls and cls in CLASSES:
            skills_text = "\n".join([f"{s['name']} — {s['mana_cost']} mana | {s['desc']}" for s in get_player_skills(player)[:6]])
            embed.add_field(name=f"⚡ Habilidades de {cls}", value=skills_text[:1024], inline=False)
        embed.set_footer(text="Mana se recupera ao subir de nível e ao descansar!")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= VER CONQUISTAS ====================
    # ======================================================
    elif any(word in content for word in ["ver conquista", "conquistas", "ver conquistas", "achievements", "minhas conquistas"]):
        player = get_player(user_id)
        earned_ids = player.get("achievements", [])
        earned_set = set(earned_ids)

        # Group by category
        cats = {}
        for ach in ACHIEVEMENTS:
            c = ach["cat"]
            if c not in cats:
                cats[c] = {"earned": [], "locked": []}
            if ach["id"] in earned_set:
                cats[c]["earned"].append(ach)
            else:
                cats[c]["locked"].append(ach)

        total = len(ACHIEVEMENTS)
        earned_count = len(earned_ids)
        pct = int(earned_count / total * 100) if total > 0 else 0
        bar_filled = pct // 10
        prog_bar = "🟨" * bar_filled + "⬛" * (10 - bar_filled)

        embed = discord.Embed(
            title=f"🏆 Conquistas de {message.author.display_name}",
            description=f"*'O narrador registra seus feitos na Grande Crônica...'*\n\n{prog_bar} `{earned_count}/{total}` ({pct}%)",
            color=discord.Color.gold()
        )

        for cat_name, data in cats.items():
            is_secret = cat_name == "🔮 Secreta"
            earned_list = data["earned"]
            locked_list = data["locked"]
            value_parts = []
            for ach in earned_list[:5]:
                value_parts.append(f"✅ **{ach['name']}** — {ach['desc']} *(+{ach['xp']:,} XP)*")
            if locked_list:
                remaining = len(locked_list)
                if is_secret:
                    value_parts.append(f"🔒 *{remaining} conquista(s) secreta(s) ainda oculta(s)...*")
                else:
                    # Show next 2 locked
                    for ach in locked_list[:2]:
                        value_parts.append(f"🔒 ~~{ach['name']}~~ — {ach['desc']}")
                    if len(locked_list) > 2:
                        value_parts.append(f"*... e mais {len(locked_list)-2} conquista(s) bloqueada(s)*")
            if value_parts:
                embed.add_field(name=f"{cat_name} ({len(earned_list)}/{len(earned_list)+len(locked_list)})", value="\n".join(value_parts)[:1024], inline=False)

        embed.set_footer(text=f"XP total de conquistas: {sum(a['xp'] for a in ACHIEVEMENTS if a['id'] in earned_set):,} XP")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= TREINAR ==========================
    # ======================================================
    elif content.startswith("treinar "):
        player = get_player(user_id)
        training_key = content[8:].strip().lower()
        opt = TRAINING_OPTIONS.get(training_key)
        if not opt:
            opts_list = " | ".join([f"`treinar {k}`" for k in TRAINING_OPTIONS])
            await message.channel.send(f"❌ Tipo de treino inválido!\n\nOpções disponíveis: {opts_list}")
            return
        cost = opt["cost"]
        if player["coins"] < cost:
            await message.channel.send(f"❌ Você não tem CSI suficiente! Precisa de `{cost:,}` mas tem `{player['coins']:,}`.")
            return
        player["coins"] -= cost
        boosts = []
        if opt.get("atk_boost"):
            player["temp_atk_boost"] = player.get("temp_atk_boost", 0) + opt["atk_boost"]
            boosts.append(f"+{opt['atk_boost']} ATK")
        if opt.get("def_boost"):
            player["temp_def_boost"] = player.get("temp_def_boost", 0) + opt["def_boost"]
            boosts.append(f"+{opt['def_boost']} DEF")
        if opt.get("hp_boost"):
            player["temp_hp_boost"] = player.get("temp_hp_boost", 0) + opt["hp_boost"]
            player["max_hp"] = player.get("max_hp", 100) + opt["hp_boost"]
            player["hp"] = min(player["hp"] + opt["hp_boost"], player["max_hp"])
            boosts.append(f"+{opt['hp_boost']} HP Max")
        training_count = player.get("training_points", 0) + 1
        player["training_points"] = training_count
        save_player_db(user_id, player)
        embed = discord.Embed(
            title=f"💪 Treino Completo!",
            description=f"*'Seus músculos queimam, mas você fica mais forte!'*\n\n{opt['emoji']} **Treino de {training_key.capitalize()}** realizado!\n\n📈 **Melhorias permanentes:** {', '.join(boosts)}\n💰 **Custo:** −{cost:,} CSI",
            color=discord.Color.green()
        )
        embed.add_field(name="📊 Novos Stats", value=f"⚔️ ATK Bônus: +{player.get('temp_atk_boost',0)}\n🛡️ DEF Bônus: +{player.get('temp_def_boost',0)}\n❤️ HP Max Extra: +{player.get('temp_hp_boost',0)}", inline=False)
        embed.set_footer(text=f"Treinos realizados: {training_count}")
        await message.channel.send(embed=embed)
        if training_count >= 10:
            await check_achievements(message.channel, user_id, "training_10")
        await check_achievements(message.channel, user_id)
        return

    # ======================================================
    # ================= REALIZAR QUEST ====================
    # ======================================================
    elif any(word in content for word in ["realizar quest", "fazer quest", "iniciar quest", "minha quest", "status da quest"]):
        player = get_player(user_id)
        quest = player.get("active_quest")

        if not quest:
            await message.channel.send(
                "📋 **Você não tem nenhuma quest ativa!**\n\n*Use `ver quests` para ver as missões disponíveis e `aceitar quest [nome]` para iniciar uma.*"
            )
            return

        objective = quest.get("objective", "")
        progress = quest.get("progress", 0)
        total = quest.get("count", 1)
        pct = int((progress / total) * 100) if total > 0 else 0
        bar_filled = int(pct / 10)
        progress_bar = "🟩" * bar_filled + "⬛" * (10 - bar_filled)

        embed = discord.Embed(
            title=f"📜 Realizando: {quest['name']}",
            description=f"*{quest['npc']} aguarda seu progresso...*\n\n*'{quest['lore']}'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎯 Objetivo", value=quest["description"], inline=False)
        embed.add_field(name="📊 Progresso", value=f"`{progress}/{total}` — {pct}%\n{progress_bar}", inline=False)

        obj_tip = {
            "hunt": f"**Como avançar:** Use `caçar` para derrotar **{quest.get('target', 'monstros')}**!",
            "collect": "**Como avançar:** Use `coletar` ou `minerar` para coletar recursos!",
            "explore": "**Como avançar:** Use `explorar` para percorrer o mundo!",
            "boss": "**Como avançar:** Use `desafiar boss` para enfrentar o boss da missão!",
        }
        embed.add_field(name="💡 Dica", value=obj_tip.get(objective, "Explore o mundo!"), inline=False)

        # Recompensas
        rewards = f"⭐ **{quest['reward_xp']} XP** | 💰 **{quest['reward_coins']} CSI**"
        if quest.get("reward_item"):
            rewards += f" | 🎁 **{quest['reward_item']}**"
        embed.add_field(name="🏆 Recompensas ao Completar", value=rewards, inline=False)
        embed.add_field(name="⚔️ Dificuldade", value=quest.get("difficulty", "?"), inline=True)

        if progress >= total:
            embed.add_field(name="✅ Status", value="**COMPLETO! Use `finalizar quest` para receber as recompensas!**", inline=False)
            embed.color = discord.Color.green()
        else:
            remaining = total - progress
            embed.add_field(name="⏳ Faltam", value=f"`{remaining}` ações para completar", inline=True)

        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= FINALIZAR QUEST ===================
    # ======================================================
    elif any(word in content for word in ["finalizar quest", "entregar quest", "completar quest"]):
        player = get_player(user_id)
        quest = player.get("active_quest")

        if not quest:
            await message.channel.send("❌ Você não tem quest ativa!")
            return

        progress = quest.get("progress", 0)
        total = quest.get("count", 1)

        if progress < total and quest.get("objective") != "boss":
            await message.channel.send(
                f"⏳ **Quest ainda não concluída!**\n\nProgresso: `{progress}/{total}`\n\n*Continue realizando as atividades para completar a missão!*"
            )
            return

        await complete_quest(message.channel, user_id, player)
        return

    # ======================================================
    # ================= ABANDONAR QUEST ===================
    # ======================================================
    elif any(word in content for word in ["abandonar quest", "desistir da quest", "cancelar quest"]):
        player = get_player(user_id)
        if not player.get("active_quest"):
            await message.channel.send("❌ Você não tem quest ativa!")
            return

        quest_name = player["active_quest"]["name"]
        player["active_quest"] = None
        save_player_db(user_id, player)

        embed = discord.Embed(
            title="🚫 Quest Abandonada",
            description=f"*'Você abandona **{quest_name}**...'*\n\n*O narrador suspira com decepção.*",
            color=discord.Color.red()
        )
        embed.set_footer(text="Use 'ver quests' para encontrar novas missões.")
        await message.channel.send(embed=embed)
        return

    # ======================================================
    # ================= PROCURAR CIDADES / VILAREJOS =======
    # ======================================================
    elif any(word in content for word in ["procurar cidade", "procurar vilarejo", "buscar cidade",
                                           "explorar cidade", "visitar cidade", "visitar vilarejo",
                                           "ver cidades", "cidades próximas", "mapa de cidades"]):
        player = get_player(user_id)
        world_key = max([k for k in CITY_NPCS.keys() if k in player["worlds"]], default=1)
        city_data = CITY_NPCS[world_key]
        world = get_world(player["level"], player)

        embed = discord.Embed(
            title=f"🗺️ Explorando Cidades — {world['emoji']} {world['name']}",
            description=f"*O narrador revela os assentamentos desta região...*",
            color=discord.Color.blue()
        )

        # Mostra a cidade do mundo atual
        embed.add_field(
            name=f"📍 {city_data['city_name']}",
            value=f"**Habitantes notáveis:**\n" + "\n".join([f"{npc['emoji']} **{npc['name']}** — {npc['role']}" for npc in city_data["npcs"]]),
            inline=False
        )

        # Mostra outras cidades desbloqueadas
        other_cities = []
        for wk in sorted(player["worlds"]):
            if wk != world_key and wk in CITY_NPCS:
                cd = CITY_NPCS[wk]
                wn = WORLDS[wk]["name"]
                other_cities.append(f"{WORLDS[wk]['emoji']} **{cd['city_name']}** ({wn})")

        if other_cities:
            embed.add_field(name="🌍 Outras Cidades Conhecidas", value="\n".join(other_cities[:5]), inline=False)

        embed.add_field(
            name="💡 Comandos",
            value="`visitar cidade` — visita a cidade e conversa com NPCs\n`ver quests` — veja missões disponíveis",
            inline=False
        )
        await message.channel.send(embed=embed)

        # Visita automaticamente a cidade atual
        await asyncio.sleep(1)
        npc = random.choice(city_data["npcs"])
        dialogue = random.choice(npc["dialogues"])
        coins_found = random.randint(1, 3)
        add_coins(user_id, coins_found)

        visit_embed = discord.Embed(
            title=f"{npc['emoji']} {npc['name']} — {npc['role']}",
            description=f"*Você se aproxima do NPC na cidade...*\n\n*'{dialogue}'*",
            color=discord.Color.green()
        )
        visit_embed.add_field(name="💰 Recompensa pela Visita", value=f"+{coins_found} CSI", inline=True)

        # 25% chance de livro de lore ao visitar
        if random.random() < 0.25:
            all_books = list(LORE_BOOKS.get(world_key, [])) + list(LORE_BOOKS_EXTRA.get(world_key, []))
            if all_books:
                book = random.choice(all_books)
                visit_embed.add_field(name=f"📚 {book['title']}", value=book["content"][:512] + "...", inline=False)

        await message.channel.send(embed=visit_embed)
        return

    # ======================================================
    # ================= DESAFIAR @USER (PvP Pokémon) ======
    # ======================================================
    elif "desafiar" in content and "@" in message.content and "boss" not in content:
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione um jogador! Ex: `desafiar @jogador`")
            return

        target_user = mentions[0]
        if target_user.id == user_id:
            await message.channel.send("❌ Você não pode se desafiar!")
            return
        if target_user.bot:
            await message.channel.send("❌ Você não pode desafiar um bot!")
            return

        challenger = get_player(user_id)
        target = get_player(target_user.id)

        if not challenger.get("class"):
            await message.channel.send("❌ Escolha uma classe primeiro! Use: `escolher classe`")
            return
        if not target.get("class"):
            await message.channel.send(f"❌ **{target_user.display_name}** ainda não escolheu uma classe!")
            return

        # Envia desafio
        view = PvPChallengeButton(user_id, target_user.id, message.author.display_name, target_user.display_name)
        embed = discord.Embed(
            title="⚔️ DESAFIO DE BATALHA!",
            description=f"*O narrador anuncia com emoção:*\n\n🥊 **{message.author.display_name}** desafia **{target_user.display_name}** para um duelo!",
            color=discord.Color.red()
        )
        cls_ch = CLASSES[challenger["class"]]
        cls_tg = CLASSES[target["class"]]
        embed.add_field(name=f"{cls_ch['emoji']} {message.author.display_name}", value=f"**{challenger['class']}** | Nível {challenger['level']} | HP: {challenger['max_hp']} | Mana: {calc_max_mana(challenger)}", inline=True)
        embed.add_field(name=f"{cls_tg['emoji']} {target_user.display_name}", value=f"**{target['class']}** | Nível {target['level']} | HP: {target['max_hp']} | Mana: {calc_max_mana(target)}", inline=True)
        embed.set_footer(text=f"{target_user.mention}, você aceita o desafio?")
        await message.channel.send(content=f"{target_user.mention}", embed=embed, view=view)
        return

    # ======================================================
    # ================= VER QUESTS ========================
    # ======================================================
    elif any(word in content for word in ["ver quests", "quests", "missões", "missoes", "aceitar quest"]):
        player = get_player(user_id)
        world_key = max([k for k in QUESTS.keys() if k in player["worlds"]], default=1)
        available_quests = list(QUESTS.get(world_key, []))
        # Adicionar quests extras do mundo
        available_quests += QUESTS_EXTRA.get(world_key, [])
        # Adicionar quests de alinhamento
        align = get_alignment(player)
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    available_quests.append(q)

        embed = discord.Embed(
            title="📋 Quadro de Missões",
            description=f"*{WORLDS[world_key]['emoji']} Missões disponíveis em **{WORLDS[world_key]['name']}**...*",
            color=discord.Color.gold()
        )
        info = ALIGNMENT_TITLES[align]
        embed.add_field(name=f"{info['emoji']} Alinhamento", value=f"**{align}** — Misões exclusivas desbloqueadas!", inline=True)

        if player.get("active_quest"):
            embed.add_field(
                name="⚠️ Quest Ativa",
                value=f"Você está em: **{player['active_quest']['name']}**\nProgresso: {player['active_quest'].get('progress', 0)}/{player['active_quest'].get('count', 1)}\n\nUse `realizar quest` para ver detalhes.",
                inline=False
            )

        completed = player.get("completed_quests", [])
        for quest in available_quests[:12]:
            status = "✅" if quest["id"] in completed else ("🔄" if player.get("active_quest") and player["active_quest"].get("id") == quest["id"] else "📌")
            q_type = "👥 Equipe" if quest.get("type") == "team" else "👤 Solo"
            xp_str = f"{quest['reward_xp']:,}"
            embed.add_field(
                name=f"{status} {quest['name']} [{q_type}]",
                value=f"**Dif:** {quest['difficulty']} | **XP:** {xp_str} | **Coins:** {quest['reward_coins']}\n{quest['description'][:80]}...",
                inline=False
            )

        embed.set_footer(text="Use 'aceitar quest [nome]' para iniciar uma missão! | 'missão moral' para quests de alinhamento")
        await message.channel.send(embed=embed)

        # Se o comando for "aceitar quest X"
        if "aceitar quest" in content:
            quest_name_search = content.replace("aceitar quest", "").strip()
            found_quest = None
            for quest in available_quests:
                if quest_name_search in quest["name"].lower() or quest_name_search in quest["id"]:
                    found_quest = quest
                    break

            if found_quest:
                view = QuestAcceptButton(user_id, found_quest)
                q_embed = discord.Embed(
                    title=f"📜 {found_quest['name']}",
                    description=f"*{found_quest['npc']} se aproxima:*\n\n*'{found_quest['lore']}'*",
                    color=discord.Color.gold()
                )
                q_embed.add_field(name="🎯 Missão", value=found_quest["description"], inline=False)
                q_embed.add_field(name="⭐ XP", value=f"{found_quest['reward_xp']:,}", inline=True)
                q_embed.add_field(name="💰 Coins", value=str(found_quest["reward_coins"]), inline=True)
                q_embed.add_field(name="⚔️ Dificuldade", value=found_quest["difficulty"], inline=True)
                await message.channel.send(embed=q_embed, view=view)
        return

    await bot.process_commands(message)
# ================= FUNÇÕES AUXILIARES =================
# ======================================================

async def check_level_boss(channel, user_id):
    """Verifica e anuncia boss de level se necessário"""
    player = get_player(user_id)
    boss_levels = [9, 19, 29, 39, 49, 59]

    if player["level"] in boss_levels:
        boss_data = get_level_boss(player["level"])
        if boss_data and boss_data["name"] not in player["bosses"]:
            # *** CORREÇÃO: Salva o boss correto como pending_boss ***
            effects = player.get("active_effects", {})
            effects["pending_boss"] = boss_data
            player["active_effects"] = effects
            save_player_db(user_id, player)

            await asyncio.sleep(2)
            embed = discord.Embed(
                title="🚨 BOSS DE NÍVEL — PASSAGEM BLOQUEADA!",
                description=f"*'Um poder colossal bloqueia seu caminho...'*\n\n👹 **{boss_data['name']}** surge para impedir seu avanço!\n\n⚠️ **Seu XP está BLOQUEADO até você derrotá-lo!**\n*'Não há glória sem superar os grandes obstáculos!'*",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="❤️ HP", value=f"`{boss_data['hp']:,}`", inline=True)
            embed.add_field(name="⚔️ ATK", value=f"`{boss_data['atk']}`", inline=True)
            embed.add_field(name="🚫 XP Bloqueado", value="Você não ganhará mais XP até derrotá-lo!", inline=False)
            embed.add_field(name="💡 Opções", value="• `desafiar boss` — Enfrente o boss agora\n• `treinar força/defesa/vitalidade` — Fortaleça-se antes\n• `chamar aliados` — Peça ajuda!", inline=False)
            view = BossButton(user_id, boss_data["name"])
            await channel.send(embed=embed, view=view)


async def complete_quest(channel, user_id, player):
    """Completa uma quest e distribui recompensas"""
    quest = player["active_quest"]
    if not quest:
        return

    reward_xp = quest["reward_xp"]
    reward_coins = quest["reward_coins"]
    reward_item = quest.get("reward_item")

    completed = player.get("completed_quests", [])
    completed.append(quest["id"])
    player["completed_quests"] = completed
    player["active_quest"] = None

    save_player_db(user_id, player)
    add_xp(user_id, reward_xp)
    add_coins(user_id, reward_coins)

    if reward_item:
        player2 = get_player(user_id)
        player2["inventory"].append(reward_item)
        save_player_db(user_id, player2)

    embed = discord.Embed(
        title=f"🎉 QUEST COMPLETA!",
        description=f"**{quest['name']}** foi concluída!\n\n*'{quest['npc']} sorri e diz: Extraordinário! Você superou minhas expectativas!'*",
        color=discord.Color.gold()
    )
    embed.add_field(name="⭐ XP Ganho", value=str(reward_xp), inline=True)
    embed.add_field(name="💰 Coins Ganhos", value=str(reward_coins), inline=True)
    if reward_item:
        embed.add_field(name="🎁 Item Recebido", value=reward_item, inline=True)

    await channel.send(embed=embed)

    await channel.send(embed=embed)


# ================= HELPERS: ALINHAMENTO, MAPA, FAZENDA =================

def get_alignment(player):
    pts = player.get("alignment_points", 0)
    if pts >= 30:
        return "Heroi"
    elif pts <= -30:
        return "Vilao"
    elif -29 <= pts <= -5:
        return "Anti-Heroi"
    else:
        return "Neutro"

def get_alignment_info(player):
    align = get_alignment(player)
    return ALIGNMENT_TITLES[align]

def apply_alignment_points(user_id, points):
    player = get_player(user_id)
    cur = player.get("alignment_points", 0)
    player["alignment_points"] = max(-100, min(100, cur + points))
    save_player_db(user_id, player)
    return player

def get_player_map(player):
    """Retorna o mapa descoberto pelo jogador"""
    disc = player.get("discovered_map", {})
    result = {}
    for world_id, world_data in MAP_LOCATIONS.items():
        if world_id not in player.get("worlds", [1]):
            continue
        result[world_id] = {
            "world_name": world_data["world_name"],
            "locations": []
        }
        for loc in world_data["locations"]:
            # cidade principal sempre visível
            disc_locs = disc.get(str(world_id), [])
            visible = loc["discovered"] or loc["id"] in disc_locs
            result[world_id]["locations"].append({**loc, "visible": visible})
    return result

def discover_location(user_id, world_id, loc_id):
    player = get_player(user_id)
    disc = player.get("discovered_map", {})
    key = str(world_id)
    if key not in disc:
        disc[key] = []
    if loc_id not in disc[key]:
        disc[key].append(loc_id)
    player["discovered_map"] = disc
    save_player_db(user_id, player)

def get_dungeon_difficulty_multiplier(player):
    """Dungeons secretas ficam mais difíceis conforme o nível"""
    level = player.get("level", 1)
    return 1.0 + (level * 0.05)  # +5% por nível


# ================= VIEW: ESCOLHER PET DA FAZENDA =================
# ================= VIEW: EMPREGOS =================
class JobSelectView(discord.ui.View):
    def __init__(self, user_id, available_jobs):
        super().__init__(timeout=90)
        self.user_id = user_id
        for job_name in available_jobs[:5]:
            jdata = JOBS[job_name]
            btn = discord.ui.Button(
                label=f"{jdata['emoji']} {job_name}",
                style=discord.ButtonStyle.primary
            )
            btn.callback = self._make_cb(job_name)
            self.add_item(btn)
        cancel = discord.ui.Button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
        cancel.callback = self._cancel
        self.add_item(cancel)

    def _make_cb(self, job_name):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                return await interaction.response.send_message("❌ Não é sua escolha!", ephemeral=True)
            player = get_player(self.user_id)
            jdata = JOBS[job_name]
            old_job = player.get("job")
            player["job"] = job_name
            player["job_since"] = int(__import__("time").time())
            # Aplicar bônus permanente de HP
            if job_name == "Cavaleiro":
                player["max_hp"] += 20
                player["hp"] = min(player["hp"] + 20, player["max_hp"])
            elif job_name == "Guarda_Real":
                player["max_hp"] += 35
                player["hp"] = min(player["hp"] + 35, player["max_hp"])
            elif job_name == "Arcano":
                player["max_mana"] = player.get("max_mana", 50) + 15
            save_player_db(self.user_id, player)
            embed = discord.Embed(
                title=f"{jdata['emoji']} Emprego Aceito: **{job_name}**!",
                description=f"*{jdata['work_action']}*\n\n{jdata['description']}",
                color=discord.Color.green()
            )
            perks_text = "\n".join([f"• {p}" for p in jdata["perks"]])
            embed.add_field(name="✨ Benefícios", value=perks_text, inline=False)
            embed.add_field(name="💰 Salário", value=f"`{jdata['salary_coins'][0]}–{jdata['salary_coins'][1]}` coins por turno de trabalho", inline=True)
            embed.add_field(name="⭐ XP por trabalho", value=f"`{jdata['salary_xp'][0]}–{jdata['salary_xp'][1]}`", inline=True)
            if old_job:
                embed.add_field(name="⚠️ Emprego anterior", value=f"Você largou **{old_job}**.", inline=False)
            embed.set_footer(text="Use `trabalhar` para ganhar salário! | `ver emprego` para detalhes")
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _cancel(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Não é sua!", ephemeral=True)
        await interaction.response.edit_message(content="❌ Escolha de emprego cancelada.", embed=None, view=None)


# ================= VIEW: DEFESA DE CIDADE =================
class CityDefenseView(discord.ui.View):
    def __init__(self, user_id, invasion, channel, guild):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.invasion = invasion
        self.channel = channel
        self.guild = guild
        self.helpers = []

        for i, opt in enumerate(invasion.get("dialogue_options", [])):
            btn = discord.ui.Button(
                label=opt["text"][:80],
                style=discord.ButtonStyle.blurple if "negoci" in opt["text"].lower() or "diálogo" in opt["text"].lower()
                      else discord.ButtonStyle.danger,
                row=i // 2
            )
            btn.callback = self._make_cb(i)
            self.add_item(btn)

        call_btn = discord.ui.Button(label="📯 Convocar Aliados", style=discord.ButtonStyle.success, row=2)
        call_btn.callback = self._call_allies
        self.add_item(call_btn)

    def _make_cb(self, idx):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id) and str(interaction.user.id) not in self.helpers:
                return await interaction.response.send_message("❌ Você não está na defesa!", ephemeral=True)
            opt = self.invasion["dialogue_options"][idx]
            import random
            success = random.random() < opt["success_chance"]
            apply_alignment_points(str(interaction.user.id), opt.get("align", 0))
            for h in self.helpers:
                apply_alignment_points(h, opt.get("align", 0) // 2)
            if success:
                xp = self.invasion["xp_reward"]
                coins = self.invasion["coins_reward"]
                add_xp(str(interaction.user.id), xp)
                add_coins(str(interaction.user.id), coins)
                for h in self.helpers:
                    add_xp(h, xp // 2)
                    add_coins(h, coins // 2)
                embed = discord.Embed(
                    title=f"🏆 INVASÃO REPELIDA! — {self.invasion['title']}",
                    description=f"*Sua estratégia funcionou! {self.invasion['enemy']}s recuam!*\n\n"
                                f"🗡️ Opção: **{opt['text'][:60]}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="⭐ XP", value=f"`+{xp}`", inline=True)
                embed.add_field(name="💰 Coins", value=f"`+{coins}`", inline=True)
                if self.helpers:
                    embed.add_field(name="👥 Aliados (XP/2)", value=f"{len(self.helpers)} jogadores ajudaram!", inline=True)
                embed.add_field(name="📣 Povo", value="_As pessoas gritam vivas nas ruas!_", inline=False)
            else:
                xp_loss = self.invasion["xp_reward"] // 4
                remove_xp(str(interaction.user.id), xp_loss)
                embed = discord.Embed(
                    title=f"💀 INVASÃO AVANÇA! — {self.invasion['title']}",
                    description=f"*Sua estratégia falhou! Os inimigos avançam mais!*\n\n"
                                f"❌ Opção: **{opt['text'][:60]}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="❌ XP Perdido", value=f"`-{xp_loss}`", inline=True)
                embed.add_field(name="💡 Dica", value="Tente outra abordagem ou `lutar` diretamente!", inline=False)
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _call_allies(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            return await interaction.response.send_message("❌ Só o defensor pode convocar!", ephemeral=True)
        embed = discord.Embed(
            title=f"📯 CONVOCAÇÃO DE DEFESA!",
            description=f"**{interaction.user.display_name}** convoca aliados para defender contra:\n"
                        f"**{self.invasion['title']}**\n\n"
                        f"*Responda `ajudar defesa` para participar!*\n"
                        f"👥 Mínimo necessário: **{self.invasion['min_defenders']}** defensores",
            color=discord.Color.orange()
        )
        await self.channel.send(embed=embed)
        await interaction.response.send_message("📯 Convocação enviada ao canal!", ephemeral=True)


class CityDefenseJoinView(discord.ui.View):
    """View para aliados entrarem na defesa ativa"""
    def __init__(self, defense_view: CityDefenseView):
        super().__init__(timeout=60)
        self.dview = defense_view

    @discord.ui.button(label="⚔️ Entrar na Defesa!", style=discord.ButtonStyle.danger)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        if uid == self.dview.user_id:
            return await interaction.response.send_message("Você já é o defensor principal!", ephemeral=True)
        if uid in self.dview.helpers:
            return await interaction.response.send_message("Você já está na defesa!", ephemeral=True)
        player = get_player(uid)
        if not player:
            return await interaction.response.send_message("❌ Crie seu personagem primeiro!", ephemeral=True)
        self.dview.helpers.append(uid)
        await interaction.response.send_message(
            f"⚔️ **{interaction.user.display_name}** entra na defesa! ({len(self.dview.helpers)+1} defensores total)",
            ephemeral=False
        )


class NomearCavaleiroView(discord.ui.View):
    """View para Rei nomear cavaleiros"""
    def __init__(self, king_id, target_user):
        super().__init__(timeout=60)
        self.king_id = king_id
        self.target_user = target_user

    @discord.ui.button(label="⚔️ Aceitar o Título", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_user.id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        player = get_player(str(self.target_user.id))
        if player:
            player["city_title"] = "Cavaleiro"
            save_player_db(str(self.target_user.id), player)
            king = get_player(self.king_id)
            knights = king.get("knights", [])
            knights.append(str(self.target_user.id))
            king["knights"] = knights
            save_player_db(self.king_id, king)
        embed = discord.Embed(
            title="⚔️ Cavaleiro do Reino!",
            description=f"**{self.target_user.display_name}** aceita o título de **Cavaleiro** e ajoelha diante do Rei!\n\n*'Com este título, juro proteger o povo com minha vida!'*",
            color=discord.Color.gold()
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.target_user.id):
            return await interaction.response.send_message("❌ Não é para você!", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="*O guerreiro recusa a genuflexão. Um rei deve respeitar isso.*", embed=None, view=self)


class PetFarmSelectView(discord.ui.View):
    def __init__(self, user_id, farm_pets):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.farm_pets = farm_pets
        for i, pet in enumerate(farm_pets[:5]):
            btn = discord.ui.Button(
                label=f"{pet.get('emoji','🐾')} {pet['name']}",
                style=discord.ButtonStyle.primary,
                custom_id=f"farm_pet_{i}"
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                await interaction.response.send_message("❌ Não é sua fazenda!", ephemeral=True)
                return
            player = get_player(self.user_id)
            chosen = self.farm_pets[index]
            old_pet = player.get("pet")
            farm = player.get("pet_farm", [])
            # Remover da fazenda e colocar equipado
            farm = [p for p in farm if p["name"] != chosen["name"]]
            # Enviar atual para fazenda se tinha
            if old_pet:
                try:
                    old_pet_obj = json.loads(old_pet) if isinstance(old_pet, str) else old_pet
                    farm.append(old_pet_obj)
                except:
                    pass
            player["pet"] = json.dumps(chosen)
            player["pet_farm"] = farm
            save_player_db(self.user_id, player)
            embed = discord.Embed(
                title=f"🔄 Pet Trocado!",
                description=f"{chosen.get('emoji','🐾')} **{chosen['name']}** saiu da fazenda e agora te acompanha!",
                color=discord.Color.green()
            )
            if old_pet:
                try:
                    old_obj = json.loads(old_pet) if isinstance(old_pet, str) else old_pet
                    embed.add_field(name="🏡 Enviado à Fazenda", value=f"{old_obj.get('emoji','🐾')} {old_obj['name']}", inline=False)
                except:
                    pass
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


# ================= VIEW: MIMIC CHEST =================
class MimicChestView(discord.ui.View):
    def __init__(self, user_id, tier_idx, world):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.tier = MIMIC_TIERS[tier_idx]
        self.world = world

    @discord.ui.button(label="🔓 Abrir o Baú", style=discord.ButtonStyle.danger)
    async def open_chest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Não é seu baú!", ephemeral=True)
            return
        player = get_player(self.user_id)
        tier = self.tier
        is_mimic = random.random() < tier["mimic_chance"]

        if is_mimic:
            dmg = random.randint(*tier["mimic_dmg"])
            xp_loss = random.randint(*tier["mimic_xp_loss"])
            player["hp"] = max(1, player["hp"] - dmg)
            save_player_db(self.user_id, player)
            # Remove some XP
            remove_xp(self.user_id, xp_loss)
            embed = discord.Embed(
                title=f"💀 MIMIC! {tier['emoji']} — {tier['name']}",
                description=tier["mimic_desc"],
                color=discord.Color.dark_red()
            )
            embed.add_field(name="💥 Dano Sofrido", value=f"`-{dmg} HP`", inline=True)
            embed.add_field(name="💀 XP Perdido", value=f"`-{xp_loss} XP`", inline=True)
            embed.add_field(name="❤️ HP Restante", value=f"`{player['hp']}/{player['max_hp']}`", inline=True)
            embed.add_field(name="📝 Lição", value="_Mimics aprenderam a imitar baús para sobreviver. Você foi enganado pelo mais antigo truque das masmorras._", inline=False)
            embed.set_footer(text="Use `curar` para recuperar HP!")
        else:
            loot_xp = random.randint(*tier["loot_xp"])
            loot_coins = random.randint(*tier["loot_coins"])
            # Item aleatório pela raridade permitida
            rarity_pool = tier["loot_items"]
            loot_item = None
            world_items = WORLDS[self.world].get("items", []) if self.world in WORLDS else []
            filtered = [i for i in world_items if i.get("rarity") in rarity_pool]
            if filtered:
                loot_item = random.choice(filtered)["name"]
            add_xp(self.user_id, loot_xp)
            add_coins(self.user_id, loot_coins)
            if loot_item:
                p2 = get_player(self.user_id)
                p2["inventory"].append(loot_item)
                save_player_db(self.user_id, p2)
            embed = discord.Embed(
                title=f"✨ Baú Aberto! {tier['emoji']} — {tier['name']}",
                description=f"*O baú cede com um estalido. Uma aura dourada emana de dentro...*",
                color=discord.Color.gold()
            )
            embed.add_field(name="⭐ XP", value=f"`+{loot_xp}`", inline=True)
            embed.add_field(name="💰 Coins", value=f"`+{loot_coins}`", inline=True)
            if loot_item:
                embed.add_field(name="🎁 Item", value=f"`{loot_item}`", inline=True)

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🚶 Deixar pra lá", style=discord.ButtonStyle.secondary)
    async def leave_chest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Não é seu baú!", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🚶 Você se afastou do baú",
                description="*Às vezes a prudência é o maior tesouro.*",
                color=discord.Color.greyple()
            ), view=None
        )


# ================= VIEW: CENÁRIO MORAL =================
class ScenarioChoiceView(discord.ui.View):
    def __init__(self, user_id, scenario):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.scenario = scenario
        for i, choice in enumerate(scenario["choices"]):
            btn = discord.ui.Button(
                label=choice["text"][:80],
                style=discord.ButtonStyle.primary if choice["align"] > 0 else (
                    discord.ButtonStyle.danger if choice["align"] < -5 else discord.ButtonStyle.secondary
                ),
                row=i // 2
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                await interaction.response.send_message("❌ Não é sua escolha!", ephemeral=True)
                return
            choice = self.scenario["choices"][index]
            player = apply_alignment_points(self.user_id, choice["align"])
            add_xp(self.user_id, choice["xp"])
            add_coins(self.user_id, choice["coins"])
            new_align = get_alignment(player)
            info = ALIGNMENT_TITLES[new_align]
            color = discord.Color(info["color"])
            embed = discord.Embed(
                title=f"{info['emoji']} Consequência",
                description=f"*{choice['result']}*",
                color=color
            )
            if choice["xp"]:
                embed.add_field(name="⭐ XP", value=f"`+{choice['xp']}`", inline=True)
            if choice["coins"]:
                embed.add_field(name="💰 Coins", value=f"`+{choice['coins']}`", inline=True)
            align_pts = player.get("alignment_points", 0)
            embed.add_field(name=f"{info['emoji']} Alinhamento", value=f"**{new_align}** ({align_pts:+d} pts)", inline=False)
            embed.set_footer(text=info["desc"])
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        return callback


# ================= COMANDOS NOVOS =================
BOT_OWNER_ID = os.getenv("OWNER_ID", str(ADMIN_ID))  # Defina no .env OWNER_ID=seu_discord_id

@bot.listen("on_message")
async def handle_new_commands(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    # ===== FAZENDA DE PETS =====
    if content in ["fazenda", "minha fazenda", "pet fazenda", "pets fazenda"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro com `começar`!")
            return
        farm = player.get("pet_farm", [])
        current_pet = player.get("pet")
        embed = discord.Embed(title="🏡 Sua Fazenda de Pets", color=discord.Color.green())
        if current_pet:
            try:
                cp = json.loads(current_pet) if isinstance(current_pet, str) else current_pet
                embed.add_field(
                    name="🐾 Pet Equipado",
                    value=f"{cp.get('emoji','🐾')} **{cp['name']}** [{cp.get('rarity','?')}]\n`+{cp.get('bonus_hp',0)} HP` | `+{cp.get('bonus_atk',0)} ATK`",
                    inline=False
                )
            except:
                embed.add_field(name="🐾 Pet Equipado", value=str(current_pet), inline=False)
        else:
            embed.add_field(name="🐾 Pet Equipado", value="_Nenhum_", inline=False)

        if farm:
            farm_text = ""
            for i, pet in enumerate(farm[:10]):
                farm_text += f"{i+1}. {pet.get('emoji','🐾')} **{pet['name']}** [{pet.get('rarity','?')}] — `+{pet.get('bonus_hp',0)} HP` / `+{pet.get('bonus_atk',0)} ATK`\n"
            embed.add_field(name=f"🌾 Na Fazenda ({len(farm)} pets)", value=farm_text, inline=False)
            embed.set_footer(text="Use `trocar pet` para escolher um da fazenda!")
        else:
            embed.add_field(name="🌾 Na Fazenda", value="_Vazia. Caçe pets para populá-la!_", inline=False)
        await message.channel.send(embed=embed)

    # ===== TROCAR PET =====
    elif content.startswith("trocar pet") and "@" not in content and content != "trocar pet":
        # trocar pet [nome] — troca diretamente por nome
        player = get_player(uid)
        if not player:
            return
        pet_name_search = content.replace("trocar pet", "").strip()
        all_pets = player.get("pets_list", []) + player.get("pet_farm", [])
        found = None
        for p in all_pets:
            if pet_name_search.lower() in p.get("name", "").lower():
                found = p
                break
        if not found:
            await message.channel.send(f"❌ Pet '{pet_name_search}' não encontrado na sua fazenda.\nUse `ver fazenda` para listar seus pets.")
            return
        # Swap active pet with found pet
        current = player.get("pet")
        new_active_name = found["name"]
        # Remove found from farm lists
        plist = player.get("pets_list", [])
        pfarm = player.get("pet_farm", [])
        if found in plist:
            plist.remove(found)
        elif found in pfarm:
            pfarm.remove(found)
        # Send current to farm
        if current:
            cur_name = current if isinstance(current, str) else current.get("name", "?")
            # Find current pet data to store in farm
            cur_pet_obj = {"name": cur_name, "emoji": "🐾", "rarity": "Comum", "bonus_hp": 0, "bonus_atk": 0}
            for world_pets in PETS.values():
                for pp in world_pets:
                    if pp["name"] == cur_name:
                        cur_pet_obj = {**pp, "evo_stage": 1, "pet_xp": 0}
                        break
            plist.append(cur_pet_obj)
        player["pets_list"] = plist
        player["pet_farm"] = pfarm
        player["pet"] = new_active_name
        save_player_db(uid, player)
        # Find new pet data for display
        new_pet_data = found
        for world_pets in PETS.values():
            for pp in world_pets:
                if pp["name"] == new_active_name:
                    new_pet_data = pp
                    break
        await message.channel.send(
            f"🔄 **Pet trocado!**\n\n"
            f"{new_pet_data.get('emoji','🐾')} **{new_active_name}** é agora seu pet ativo!\n"
            f"+{new_pet_data.get('bonus_atk',0)} ATK | +{new_pet_data.get('bonus_hp',0)} HP\n"
            f"*O pet anterior foi para a fazenda.*"
        )

    elif content in ["trocar pet", "mudar pet", "escolher pet"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        all_pets = player.get("pets_list", []) + player.get("pet_farm", [])
        if not all_pets:
            await message.channel.send("🏡 Sua fazenda está vazia! Não há pets para trocar.\nCapture mais pets com `domesticar`.")
            return
        embed = discord.Embed(
            title="🔄 Trocar Pet",
            description="Escolha um pet da fazenda para equipar. O pet atual será enviado para a fazenda.\nOu use `trocar pet [nome]` diretamente!",
            color=discord.Color.blurple()
        )
        for pet in all_pets[:6]:
            evo_info = PET_EVOLUTIONS.get(pet.get("name",""))
            evo_txt = f"\n🔄 Evo: {evo_info['next']}" if evo_info else ""
            embed.add_field(
                name=f"{pet.get('emoji','🐾')} {pet['name']}",
                value=f"{RARITIES[pet.get('rarity','Comum')]['emoji']} {pet.get('rarity','?')}\n+{pet.get('bonus_hp',0)} HP | +{pet.get('bonus_atk',0)} ATK{evo_txt}",
                inline=True
            )
        view = PetFarmSelectView(uid, all_pets)
        await message.channel.send(embed=embed, view=view)

    # ===== ENVIAR PET PARA FAZENDA =====
    elif content.startswith("enviar pet fazenda") or content in ["guardar pet", "depositar pet"]:
        player = get_player(uid)
        if not player:
            return
        current_pet = player.get("pet")
        if not current_pet:
            await message.channel.send("❌ Você não tem pet equipado!")
            return
        try:
            cp = json.loads(current_pet) if isinstance(current_pet, str) else current_pet
            farm = player.get("pet_farm", [])
            farm.append(cp)
            player["pet"] = None
            player["pet_farm"] = farm
            save_player_db(uid, player)
            embed = discord.Embed(
                title="🏡 Pet Enviado!",
                description=f"{cp.get('emoji','🐾')} **{cp['name']}** foi para a fazenda feliz!",
                color=discord.Color.green()
            )
            embed.set_footer(text="Use `trocar pet` para escolhê-lo de volta quando quiser.")
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ Erro ao enviar pet: {e}")

    # ===== TROCAR CSI COINS POR MONSTRINHOS COINS =====
    elif content.startswith("trocar coins") or content.startswith("converter coins"):
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        parts = content.split()
        amount = 0
        for p in parts:
            if p.isdigit():
                amount = int(p)
                break
        if amount <= 0:
            await message.channel.send(
                "💱 **Como trocar coins:**\n`trocar coins 100` — envia pedido de troca de 100 CSI Coins por Monstrinhos Coins.\n"
                "O dono do servidor será notificado e aprovará a troca.\n\n"
                f"Seu saldo atual: **{player['coins']} CSI Coins** 💰"
            )
            return
        if player["coins"] < amount:
            await message.channel.send(f"❌ Você tem apenas **{player['coins']}** coins! Pediu {amount}.")
            return

        # Salvar pedido no DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO coin_exchange_requests (user_id, username, csi_coins) VALUES (?, ?, ?)",
                  (uid, str(message.author), amount))
        req_id = c.lastrowid
        conn.commit()
        conn.close()

        # Notificar dono via DM
        owner_id = int(BOT_OWNER_ID) if BOT_OWNER_ID != "0" else None
        if owner_id:
            try:
                owner = await bot.fetch_user(owner_id)
                dm_embed = discord.Embed(
                    title="💱 PEDIDO DE TROCA DE COINS",
                    description=f"**Usuário:** {message.author} (`{uid}`)\n**Servidor:** {message.guild.name if message.guild else 'DM'}\n**Pedido:** {amount} CSI Coins → Monstrinhos Coins\n**ID do Pedido:** #{req_id}",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="✅ Para APROVAR", value=f"`aprovar troca {req_id}`", inline=True)
                dm_embed.add_field(name="❌ Para RECUSAR", value=f"`recusar troca {req_id}`", inline=True)
                await owner.send(embed=dm_embed)
            except Exception as e:
                print(f"Erro ao enviar DM ao owner: {e}")

        embed = discord.Embed(
            title="📤 Pedido Enviado!",
            description=f"Seu pedido de troca de **{amount} CSI Coins** foi registrado e enviado ao administrador.\nAguarde a aprovação!",
            color=discord.Color.blurple()
        )
        embed.add_field(name="📋 ID do Pedido", value=f"#{req_id}", inline=True)
        embed.add_field(name="💰 Coins Solicitados", value=f"{amount}", inline=True)
        await message.channel.send(embed=embed)

    # ===== OWNER: APROVAR/RECUSAR TROCA =====
    elif content.startswith("aprovar troca ") and uid == BOT_OWNER_ID:
        parts = content.split()
        if len(parts) < 3 or not parts[2].isdigit():
            await message.channel.send("❌ Uso: `aprovar troca <id>`")
            return
        req_id = int(parts[2])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, username, csi_coins, status FROM coin_exchange_requests WHERE id = ?", (req_id,))
        row = c.fetchone()
        if not row:
            await message.channel.send(f"❌ Pedido #{req_id} não encontrado.")
            conn.close()
            return
        req_uid, req_uname, req_coins, status = row
        if status != "pending":
            await message.channel.send(f"❌ Pedido #{req_id} já foi processado ({status}).")
            conn.close()
            return
        # Resetar coins do jogador
        player = get_player(req_uid)
        if player:
            old_coins = player["coins"]
            player["coins"] = max(0, player["coins"] - req_coins)
            save_player_db(req_uid, player)
        c.execute("UPDATE coin_exchange_requests SET status = 'approved' WHERE id = ?", (req_id,))
        conn.commit()
        conn.close()
        # Notificar jogador
        try:
            target_user = await bot.fetch_user(int(req_uid))
            notify_embed = discord.Embed(
                title="✅ Troca Aprovada!",
                description=f"Sua troca de **{req_coins} CSI Coins** por Monstrinhos Coins foi **APROVADA**!\nSeus coins foram descontados. Entre em contato com o administrador para receber seus Monstrinhos Coins! 🎉",
                color=discord.Color.green()
            )
            await target_user.send(embed=notify_embed)
        except:
            pass
        await message.channel.send(f"✅ Pedido #{req_id} de **{req_uname}** aprovado! {req_coins} coins descontados.")

    elif content.startswith("recusar troca ") and uid == BOT_OWNER_ID:
        parts = content.split()
        if len(parts) < 3 or not parts[2].isdigit():
            await message.channel.send("❌ Uso: `recusar troca <id>`")
            return
        req_id = int(parts[2])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, username, csi_coins, status FROM coin_exchange_requests WHERE id = ?", (req_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            await message.channel.send(f"❌ Pedido #{req_id} não encontrado.")
            return
        req_uid, req_uname, req_coins, status = row
        conn2 = sqlite3.connect(DB_FILE)
        c2 = conn2.cursor()
        c2.execute("UPDATE coin_exchange_requests SET status = 'refused' WHERE id = ?", (req_id,))
        conn2.commit()
        conn2.close()
        try:
            target_user = await bot.fetch_user(int(req_uid))
            await target_user.send(embed=discord.Embed(
                title="❌ Troca Recusada",
                description=f"Seu pedido de troca de **{req_coins} CSI Coins** foi recusado. Entre em contato com o administrador para mais detalhes.",
                color=discord.Color.red()
            ))
        except:
            pass
        await message.channel.send(f"❌ Pedido #{req_id} de **{req_uname}** recusado.")

    # ===== ALINHAMENTO MORAL =====
    elif content in ["alinhamento", "meu alinhamento", "ver alinhamento", "moralidade"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        align = get_alignment(player)
        info = ALIGNMENT_TITLES[align]
        pts = player.get("alignment_points", 0)
        color = discord.Color(info["color"])

        bar_fill = int((pts + 100) / 200 * 20)
        bar = "🟥" * max(0, 10 - bar_fill // 2) + "⬛" * max(0, bar_fill - 10) if pts < 0 else "⬛" * max(0, 10 - bar_fill // 2) + "🟨" * max(0, bar_fill // 2)
        villain_bar = "🔴" * min(10, max(0, (-pts) // 10))
        hero_bar = "🟡" * min(10, max(0, pts // 10))
        full_bar = "💀" * max(0, 10 - len(villain_bar) - len(hero_bar)) + villain_bar + "⚖️" + hero_bar + "✨" * max(0, 10 - len(hero_bar))

        embed = discord.Embed(
            title=f"{info['emoji']} {align} — {message.author.display_name}",
            description=f"*{info['desc']}*",
            color=color
        )
        embed.add_field(name="📊 Pontos de Alinhamento", value=f"`{pts:+d} / 100`", inline=True)
        evil_bar = "🔴" * min(10, max(0, 10 - (pts + 100) // 20))
        good_bar = "🟡" * min(10, max(0, (pts + 100) // 20))
        embed.add_field(name="☯️ Espectro Moral", value=f"💀 {evil_bar}|{good_bar} ✨", inline=False)
        embed.add_field(
            name="🎯 Próximo Alinhamento",
            value=(
                f"**Herói** em `{max(0, 30 - pts)} pts`" if pts < 30 else
                f"**Vilão** em `{max(0, pts + 30)} pts negativos`" if pts > -30 else
                "Você está no extremo!"
            ),
            inline=False
        )
        quests_available = []
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    quests_available.append(q["name"])
        if quests_available:
            embed.add_field(name="📋 Quests Disponíveis pro seu Alinhamento", value="\n".join(quests_available[:5]), inline=False)
        await message.channel.send(embed=embed)

    # ===== CENÁRIO MORAL =====
    elif content in ["cenário", "cenario", "evento moral", "situação", "situacao"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        scenario_pool = ALIGNMENT_SCENARIOS.get(world_key, ALIGNMENT_SCENARIOS.get(1, []))
        if not scenario_pool:
            await message.channel.send("🌍 Não há cenários para este reino ainda.")
            return
        scenario = random.choice(scenario_pool)
        embed = discord.Embed(
            title=f"{scenario['emoji']} {scenario['title']}",
            description=scenario["description"],
            color=discord.Color.gold()
        )
        align = get_alignment(player)
        info = ALIGNMENT_TITLES[align]
        embed.set_footer(text=f"Alinhamento atual: {info['emoji']} {align} | Suas escolhas definem quem você é.")
        view = ScenarioChoiceView(uid, scenario)
        await message.channel.send(embed=embed, view=view)

    # ===== ABRIR MAPA =====
    elif content in ["abrir mapa", "mapa", "meu mapa", "ver mapa"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        player_map = get_player_map(player)
        embed = discord.Embed(
            title="🗺️ Mapa do Mundo",
            description="Locais descobertos durante sua jornada. Use `viajar <nome do local>` para se locomover.",
            color=discord.Color.blue()
        )
        current_world = max(player.get("worlds", [1]))
        for world_id, wdata in player_map.items():
            locs_text = ""
            for loc in wdata["locations"]:
                if loc.get("visible"):
                    type_icons = {
                        "cidade": "🏙️", "recurso": "⛏️", "dungeon": "🕳️", "dungeon_secreta": "🔮",
                        "boss_local": "💀", "lore": "📜", "loja": "🏪", "crafting": "⚒️",
                        "portal": "🌀", "evento_especial": "⭐", "npc_especial": "🧙"
                    }
                    icon = type_icons.get(loc["type"], "📍")
                    marker = "📌" if world_id == current_world else ""
                    locs_text += f"{icon} {loc['name']} {marker}\n"
                else:
                    locs_text += f"❓ *Local Desconhecido*\n"
            if locs_text:
                current_marker = " ← **AQUI**" if world_id == current_world else ""
                embed.add_field(
                    name=f"{wdata['world_name']}{current_marker}",
                    value=locs_text or "_Nenhum local descoberto_",
                    inline=False
                )
        embed.set_footer(text="💡 Dica: Explore com `explorar` para descobrir novos locais!")
        await message.channel.send(embed=embed)

    # ===== VIAJAR =====
    elif content.startswith("viajar ") or content.startswith("ir para ") or content.startswith("ir pra "):
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        destination = content.split(maxsplit=1)[1].strip().lower()
        player_map = get_player_map(player)
        found_loc = None
        found_world = None
        for world_id, wdata in player_map.items():
            for loc in wdata["locations"]:
                if loc.get("visible") and destination in loc["name"].lower():
                    found_loc = loc
                    found_world = world_id
                    break
        # Também verificar por número de mundo
        if not found_loc:
            for world_id in player.get("worlds", [1]):
                world_name = MAP_LOCATIONS.get(world_id, {}).get("world_name", "")
                if destination in world_name.lower():
                    found_world = world_id
                    found_loc = {"name": world_name, "id": f"world_{world_id}", "type": "cidade"}
                    break
        if not found_loc:
            await message.channel.send(
                f"❓ Local '**{destination}**' não encontrado ou ainda não descoberto.\n"
                "Use `abrir mapa` para ver seus locais conhecidos."
            )
            return
        # Verificar se o mundo está desbloqueado
        if found_world not in player.get("worlds", [1]):
            await message.channel.send(f"🔒 O reino **{MAP_LOCATIONS.get(found_world, {}).get('world_name', '?')}** ainda está bloqueado! Derrote o boss do reino anterior.")
            return
        # Atualizar mundo atual do jogador
        worlds = player.get("worlds", [1])
        if found_world not in worlds:
            await message.channel.send(f"🔒 Você ainda não desbloqueou este reino!")
            return
        # Registrar viagem (mover o "mundo ativo" para o escolhido)
        player["worlds"] = worlds  # mantém tudo que já tem
        save_player_db(uid, player)
        world_name = MAP_LOCATIONS.get(found_world, {}).get("world_name", str(found_world))
        embed = discord.Embed(
            title=f"✈️ Viajando para {found_loc['name']}",
            description=f"*Você parte em direção a **{world_name}**...*\n\nChegou em **{found_loc['name']}**! O ar aqui é diferente.",
            color=discord.Color.teal()
        )
        embed.add_field(name="📍 Local", value=found_loc["name"], inline=True)
        embed.add_field(name="🌍 Reino", value=world_name, inline=True)
        embed.set_footer(text="Use `explorar` para começar a aventura neste local!")
        # Descobrir local se ainda não estava marcado
        disc = player.get("discovered_map", {})
        key = str(found_world)
        if key not in disc:
            disc[key] = []
        if found_loc.get("id") and found_loc["id"] not in disc[key]:
            disc[key].append(found_loc["id"])
            player["discovered_map"] = disc
            save_player_db(uid, player)
            embed.add_field(name="🗺️ Descoberta!", value=f"Local adicionado ao mapa!", inline=False)
        await message.channel.send(embed=embed)

    # ===== MISSÃO MORAL =====
    elif content in ["missão moral", "missao moral", "quest moral", "missão alinhamento"]:
        player = get_player(uid)
        if not player:
            return
        align = get_alignment(player)
        all_quests = []
        for key, qlist in ALIGNMENT_QUESTS.items():
            for q in qlist:
                req = q.get("align_required")
                if req is None or req == align:
                    all_quests.append(q)
        if not all_quests:
            await message.channel.send("❌ Nenhuma missão disponível para seu alinhamento.")
            return
        quest = random.choice(all_quests)
        if player.get("active_quest"):
            await message.channel.send("❌ Você já tem uma quest ativa! Use `finalizar quest` ou `abandonar quest`.")
            return
        info = ALIGNMENT_TITLES[align]
        embed = discord.Embed(
            title=f"{info['emoji']} {quest['name']}",
            description=quest["description"],
            color=discord.Color(info["color"])
        )
        embed.add_field(name="📝 Lore", value=quest["lore"], inline=False)
        embed.add_field(name="👤 NPC", value=quest["npc"], inline=True)
        embed.add_field(name="⚔️ Dificuldade", value=quest["difficulty"], inline=True)
        embed.add_field(name="⭐ Recompensa XP", value=f"{quest['reward_xp']:,}", inline=True)
        embed.add_field(name="💰 Recompensa Coins", value=str(quest["reward_coins"]), inline=True)
        view = QuestAcceptButton(str(uid), quest)
        await message.channel.send(embed=embed, view=view)

    # ===== DESCOBRIR LOCAL (ao explorar) — trigger automático =====
    # Isso é chamado internamente, não diretamente pelo usuário

    # ===== VER PEDIDOS DE TROCA (admin) =====
    elif content in ["ver trocas", "pedidos de troca"] and uid == BOT_OWNER_ID:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, user_id, username, csi_coins, status, created_at FROM coin_exchange_requests WHERE status = 'pending' ORDER BY created_at DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        if not rows:
            await message.channel.send("📋 Nenhum pedido de troca pendente.")
            return
        embed = discord.Embed(title="💱 Pedidos de Troca Pendentes", color=discord.Color.orange())
        for row in rows:
            req_id, req_uid, req_uname, req_coins, req_status, created = row
            embed.add_field(
                name=f"#{req_id} — {req_uname}",
                value=f"💰 **{req_coins}** CSI Coins\n`aprovar troca {req_id}` | `recusar troca {req_id}`",
                inline=False
            )
        await message.channel.send(embed=embed)

    # ===== EMPREGOS =====
    elif content in ["procurar emprego", "empregos", "quero emprego", "ver empregos", "escolher emprego"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        if player["level"] < 5:
            await message.channel.send(
                f"⚠️ Você precisa ser **nível 5** para procurar emprego!\n"
                f"Nível atual: **{player['level']}**\nContinue explorando!"
            )
            return
        current_job = player.get("job")
        avail = [name for name, jdata in JOBS.items() if player["level"] >= jdata["min_level"]]
        embed = discord.Embed(
            title="💼 Empregos do Reino",
            description="*O taberneiro pregou uma lista de vagas na parede. Você se aproxima para ler...*",
            color=discord.Color.blurple()
        )
        if current_job:
            jd = JOBS.get(current_job, {})
            embed.add_field(
                name=f"🔖 Emprego Atual: {jd.get('emoji','?')} {current_job}",
                value=f"_{jd.get('description','')}_\nUse `trabalhar` para ganhar salário!",
                inline=False
            )
        for jname in avail:
            jd = JOBS[jname]
            embed.add_field(
                name=f"{jd['emoji']} {jname} (Nível {jd['min_level']}+)",
                value=f"_{jd['description']}_\n💰 `{jd['salary_coins'][0]}–{jd['salary_coins'][1]}` coins | ⭐ `{jd['salary_xp'][0]}–{jd['salary_xp'][1]}` XP",
                inline=True
            )
        embed.set_footer(text="Escolha um emprego abaixo! Você pode trocar a qualquer momento.")
        view = JobSelectView(uid, avail)
        await message.channel.send(embed=embed, view=view)

    elif content in ["ver emprego", "meu emprego", "emprego atual"]:
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego! Use `procurar emprego` para ver vagas disponíveis.")
            return
        jd = JOBS[job]
        import time
        since = player.get("job_since", 0)
        hours_working = int((time.time() - since) / 3600) if since else 0
        embed = discord.Embed(
            title=f"{jd['emoji']} Seu Emprego: **{job}**",
            description=f"*{jd['work_action']}*\n\n{jd['description']}",
            color=discord.Color.green()
        )
        perks_text = "\n".join([f"• {p}" for p in jd["perks"]])
        embed.add_field(name="✨ Benefícios", value=perks_text, inline=False)
        embed.add_field(name="💰 Salário por turno", value=f"`{jd['salary_coins'][0]}–{jd['salary_coins'][1]}` coins", inline=True)
        embed.add_field(name="⭐ XP por turno", value=f"`{jd['salary_xp'][0]}–{jd['salary_xp'][1]}`", inline=True)
        embed.add_field(name="⏱️ Trabalhando há", value=f"`{hours_working}h`", inline=True)
        title = player.get("city_title")
        if title:
            embed.add_field(name="🏅 Título na Cidade", value=f"**{title}**", inline=False)
        embed.set_footer(text="Use `trabalhar` para ganhar salário!")
        await message.channel.send(embed=embed)

    elif content in ["trabalhar", "ir trabalhar", "fazer trabalho"]:
        import time
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego! Use `procurar emprego`.")
            return
        jd = JOBS[job]
        last_work = player.get("last_work", 0)
        now = int(time.time())
        cooldown = 1800  # 30 min
        if now - last_work < cooldown:
            remaining = cooldown - (now - last_work)
            mins = remaining // 60
            await message.channel.send(f"⏳ Você já trabalhou recentemente! Próximo turno em **{mins} minutos**.")
            return
        coins = random.randint(*jd["salary_coins"])
        xp = random.randint(*jd["salary_xp"])
        work_msg = random.choice(jd["work_msgs"])
        # Bônus de curandeiro
        hp_bonus = 0
        if job == "Curandeiro":
            hp_bonus = 10
            player["hp"] = min(player["max_hp"], player["hp"] + hp_bonus)
        player["last_work"] = now
        save_player_db(uid, player)
        add_coins(uid, coins)
        leveled = add_xp(uid, xp)
        embed = discord.Embed(
            title=f"{jd['emoji']} Turno de Trabalho — {job}",
            description=work_msg,
            color=discord.Color.green()
        )
        embed.add_field(name="💰 Salário", value=f"`+{coins}` coins", inline=True)
        embed.add_field(name="⭐ XP", value=f"`+{xp}`", inline=True)
        if hp_bonus:
            embed.add_field(name="💚 Cura", value=f"`+{hp_bonus} HP`", inline=True)
        if leveled:
            p2 = get_player(uid)
            embed.add_field(name="🆙 Level Up!", value=f"Nível **{p2['level']}**!", inline=False)
        embed.set_footer(text="Próximo turno em 30 minutos.")
        await message.channel.send(embed=embed)

    elif content in ["largar emprego", "demissao", "demissão", "sair do emprego"]:
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        if not job:
            await message.channel.send("💼 Você não tem emprego para largar!")
            return
        jd = JOBS[job]
        player["job"] = None
        save_player_db(uid, player)
        await message.channel.send(
            embed=discord.Embed(
                title=f"{jd['emoji']} Você largou o emprego de **{job}**",
                description=f"*Você entrega sua ferramenta e parte. Um novo capítulo começa.*",
                color=discord.Color.greyple()
            )
        )

    # ===== DEFENDER CIDADE (Cavaleiro/Guarda/Rei) =====
    elif content in ["defender cidade", "patrulhar", "defender reino", "modo defesa"]:
        import time
        player = get_player(uid)
        if not player:
            return
        job = player.get("job")
        title = player.get("city_title")
        has_defense_role = job in ["Cavaleiro", "Guarda_Real", "Rei"] or title in ["Cavaleiro", "Rei"]
        if not has_defense_role:
            await message.channel.send(
                "⚔️ Apenas **Cavaleiros**, **Guardas Reais** e **Reis** podem defender a cidade!\n"
                "Use `procurar emprego` para se tornar um cavaleiro (requer nível 10)."
            )
            return
        last_defend = player.get("last_defend", 0)
        now = int(time.time())
        if now - last_defend < 3600:
            remaining = (3600 - (now - last_defend)) // 60
            await message.channel.send(f"⏳ Você já patrulhou! Próxima defesa em **{remaining} minutos**.")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        world_invasions = CITY_INVASION_EVENTS.get(world_key, CITY_INVASION_EVENTS.get(1, []))
        invasion = random.choice(world_invasions)
        player["last_defend"] = now
        save_player_db(uid, player)
        jd = JOBS.get(job, JOBS.get("Cavaleiro", {}))
        embed = discord.Embed(
            title=f"🚨 INVASÃO! — {invasion['title']}",
            description=f"*{invasion['description']}*\n\n"
                        f"👹 Inimigo: **{invasion['enemy']}** ×{invasion['enemy_count']}\n"
                        f"💪 Min. defensores: **{invasion['min_defenders']}**",
            color=discord.Color.red()
        )
        embed.add_field(name="⭐ Recompensa", value=f"`+{invasion['xp_reward']} XP` | `+{invasion['coins_reward']} coins`", inline=True)
        embed.add_field(
            name="💡 Como agir",
            value="Escolha sua estratégia abaixo!\nUse **📯 Convocar Aliados** para chamar outros jogadores.",
            inline=False
        )
        embed.set_footer(text=f"Defensor: {message.author.display_name} | {jd.get('emoji','⚔️')} {job}")
        view = CityDefenseView(uid, invasion, message.channel, message.guild)
        await message.channel.send(embed=embed, view=view)

    elif content in ["ajudar defesa", "defender junto", "entrar defesa"]:
        await message.channel.send(
            embed=discord.Embed(
                title="⚔️ Prontidão para Defesa",
                description=f"**{message.author.display_name}** está pronto para defender!\nAguardando convocação ativa de um Cavaleiro ou Rei.",
                color=discord.Color.blue()
            )
        )

    # ===== NOMEAR CAVALEIRO (só Rei) =====
    elif content.startswith("nomear cavaleiro ") or content.startswith("nomear guerreiro "):
        player = get_player(uid)
        if not player:
            return
        if player.get("job") != "Rei" and player.get("city_title") != "Rei":
            await message.channel.send("👑 Apenas o **Rei** pode nomear cavaleiros!")
            return
        mentions = message.mentions
        if not mentions:
            await message.channel.send("❌ Mencione o jogador: `nomear cavaleiro @usuario`")
            return
        target = mentions[0]
        tplayer = get_player(str(target.id))
        if not tplayer:
            await message.channel.send("❌ Esse jogador ainda não começou sua jornada!")
            return
        embed = discord.Embed(
            title="⚔️ Cerimônia de Nomeação",
            description=f"**{message.author.display_name}** deseja nomear **{target.display_name}** como **Cavaleiro do Reino**!\n\n{target.mention}, você aceita a responsabilidade?",
            color=discord.Color.gold()
        )
        view = NomearCavaleiroView(uid, target)
        await message.channel.send(embed=embed, view=view)

    # ===== TORNAR-SE REI =====
    elif content in ["me tornar rei", "quero ser rei", "proclamar rei", "assumir trono"]:
        player = get_player(uid)
        if not player:
            return
        if player["level"] < 30:
            await message.channel.send(f"👑 Você precisa ser **nível 30** para assumir um trono!\nNível atual: **{player['level']}**")
            return
        if player.get("job") == "Rei":
            await message.channel.send("👑 Você **já é** Rei! Governe com sabedoria.")
            return
        embed = discord.Embed(
            title="👑 PROCLAMAÇÃO REAL",
            description=f"*{message.author.display_name} ergue a espada diante do povo reunido...*\n\n"
                        f"Tornar-se Rei significa:\n"
                        f"• Responsabilidade por **defender a cidade**\n"
                        f"• Receber **tributo diário** de coins\n"
                        f"• Poder **nomear cavaleiros** com `nomear cavaleiro @user`\n"
                        f"• Receber **alertas de invasão** em primeira mão\n\n"
                        f"⚠️ Requer: Nível 30+ e dedicação!",
            color=discord.Color.gold()
        )
        confirm_view = discord.ui.View(timeout=30)
        yes_btn = discord.ui.Button(label="👑 Assumir o Trono", style=discord.ButtonStyle.success)
        no_btn = discord.ui.Button(label="❌ Recusar", style=discord.ButtonStyle.secondary)

        async def yes_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != uid:
                return await interaction.response.send_message("❌ Não é você!", ephemeral=True)
            p = get_player(uid)
            old_job = p.get("job")
            p["job"] = "Rei"
            p["city_title"] = "Rei"
            p["job_since"] = int(__import__("time").time())
            save_player_db(uid, p)
            crown_embed = discord.Embed(
                title="👑 LONGA VIDA AO REI!",
                description=f"*O povo ajoelha enquanto a coroa pousa na cabeça de **{interaction.user.display_name}**!*\n\n"
                            f"Que seu reino seja próspero e justo!",
                color=discord.Color.gold()
            )
            crown_embed.add_field(name="📜 Seus poderes", value="Use `trabalhar` | `defender cidade` | `nomear cavaleiro @user` | `ver emprego`", inline=False)
            for item in confirm_view.children:
                item.disabled = True
            await interaction.response.edit_message(embed=crown_embed, view=confirm_view)

        async def no_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != uid:
                return
            for item in confirm_view.children:
                item.disabled = True
            await interaction.response.edit_message(content="*O trono aguarda outro dia.*", embed=None, view=confirm_view)

        yes_btn.callback = yes_cb
        no_btn.callback = no_cb
        confirm_view.add_item(yes_btn)
        confirm_view.add_item(no_btn)
        await message.channel.send(embed=embed, view=confirm_view)

    # ===== ENCONTRAR BOSS (boss variado por mundo) =====
    elif content in ["encontrar boss", "procurar boss", "buscar boss", "caçar boss", "boss do reino"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        if not player.get("class"):
            await message.channel.send("⚠️ Escolha uma classe primeiro! Use: `escolher classe`")
            return
        # encontrar boss NUNCA mostra bosses de level — apenas variantes do mundo
        # Bosses de level (9/19/29/39/49/59) só aparecem via check_level_boss/desafiar boss
        boss_gate_levels = {9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149, 159, 169, 179, 189, 199}
        if player["level"] in boss_gate_levels:
            boss_data_gate = get_level_boss(player["level"])
            if boss_data_gate and boss_data_gate["name"] not in player.get("bosses", []):
                await message.channel.send(
                    f"🚨 **Você tem um Boss de Nível pendente!**\n\n👹 **{boss_data_gate['name']}** bloqueia sua passagem.\n⚠️ Seu XP está bloqueado até derrotá-lo!\n\nUse `desafiar boss` para enfrentá-lo."
                )
                return
        world_key = max(k for k in player.get("worlds", [1]))
        boss_pool = WORLD_BOSSES_VARIANTS.get(world_key, WORLD_BOSSES_VARIANTS.get(1, []))
        boss = random.choice(boss_pool)
        world_info = MAP_LOCATIONS.get(world_key, {})
        world_name = world_info.get("world_name", "este reino")
        intro_msgs = [
            "🌑 O ar fica pesado de magia maligna...",
            "⚡ Um trovão ecoa sem nuvens no céu...",
            "💀 A temperatura cai dez graus de repente...",
            "👁️ Você sente que está sendo observado há minutos...",
            "🔥 O chão treme levemente sob seus pés...",
        ]
        embed = discord.Embed(
            title=f"⚠️ BOSS ENCONTRADO — {world_name}",
            description=f"*{random.choice(intro_msgs)}*\n\n{boss['intro']}",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="👹 Boss", value=f"**{boss['name']}**", inline=True)
        embed.add_field(name="❤️ HP", value=f"`{boss['hp']:,}`", inline=True)
        embed.add_field(name="⚔️ ATK", value=f"`{boss['atk']}`", inline=True)
        embed.add_field(name="⭐ XP", value=f"`{boss['xp']:,}`", inline=True)
        embed.add_field(name="💰 Coins", value=f"`{boss['coins'][0]}–{boss['coins'][1]}`", inline=True)
        embed.add_field(name="📖 Lore", value=f"_{boss['desc']}_", inline=False)
        embed.set_footer(text="Use os botões para lutar, chamar aliados ou fugir!")
        view = BossButton(uid, boss["name"])
        # Passar os dados do boss customizado para a batalha
        # Armazenar no player para a fight_boss poder pegar
        player2 = get_player(uid)
        effects = player2.get("active_effects", {})
        effects["pending_boss"] = boss
        player2["active_effects"] = effects
        save_player_db(uid, player2)
        await message.channel.send(embed=embed, view=view)


# ================= MODIFICAR MINERAR PARA INCLUIR MIMIC CHEST =================
# (Hook aplicado no on_message principal — ver abaixo)

@bot.listen("on_message")
async def handle_mining_mimic(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["minerar baú", "minerar bau", "abrir bau", "abrir baú", "bau secreto", "baú secreto"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        world_key = max(k for k in player.get("worlds", [1]))
        # Nível do baú baseado no nível do mundo
        tier_idx = min(len(MIMIC_TIERS) - 1, list(MAP_LOCATIONS.keys()).index(world_key) if world_key in MAP_LOCATIONS else 0)
        tier = MIMIC_TIERS[tier_idx]
        embed = discord.Embed(
            title=f"🔮 Baú Encontrado! — {tier['emoji']} {tier['name']}",
            description=(
                f"*Enquanto minerava, você encontrou um baú misterioso...*\n\n"
                f"**Chance de ser Mimic:** `{int(tier['mimic_chance']*100)}%`\n"
                f"**XP potencial:** `{tier['loot_xp'][0]}–{tier['loot_xp'][1]}`\n"
                f"**Coins potenciais:** `{tier['loot_coins'][0]}–{tier['loot_coins'][1]}`\n\n"
                f"⚠️ *Mimics podem te atacar e roubar XP! Você abre sabendo do risco?*"
            ),
            color=discord.Color.dark_gold()
        )
        view = MimicChestView(uid, tier_idx, world_key)
        await message.channel.send(embed=embed, view=view)


# ================= MODIFICAR EXPLORAR PARA DESCOBRIR LOCAIS =================
@bot.listen("on_message")
async def handle_map_discovery(message):
    """Ao explorar, há chance de descobrir novo local no mapa"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["explorar", "explorar região", "explorar regiao"]:
        # Este listener só faz a descoberta de local — o explorar principal continua normalmente
        await asyncio.sleep(0.5)  # leve delay para não conflitar
        player = get_player(uid)
        if not player:
            return
        if random.random() < 0.20:  # 20% de chance de descobrir algo
            world_key = max(k for k in player.get("worlds", [1]))
            world_locs = MAP_LOCATIONS.get(world_key, {}).get("locations", [])
            disc = player.get("discovered_map", {})
            key = str(world_key)
            known = disc.get(key, [])
            unknown = [l for l in world_locs if not l["discovered"] and l["id"] not in known]
            if unknown:
                new_loc = random.choice(unknown)
                discover_location(uid, world_key, new_loc["id"])
                type_icons = {
                    "cidade": "🏙️", "recurso": "⛏️", "dungeon": "🕳️", "dungeon_secreta": "🔮",
                    "boss_local": "💀", "lore": "📜", "loja": "🏪", "crafting": "⚒️",
                    "portal": "🌀", "evento_especial": "⭐", "npc_especial": "🧙"
                }
                icon = type_icons.get(new_loc["type"], "📍")
                await message.channel.send(
                    embed=discord.Embed(
                        title=f"🗺️ Novo Local Descoberto!",
                        description=f"{icon} **{new_loc['name']}** foi adicionado ao seu mapa!\nUse `abrir mapa` para ver.",
                        color=discord.Color.teal()
                    )
                )

# ================= MASMORRAS SECRETAS MAIS DIFÍCEIS =================
# A função explore_dungeon já existe — vamos sobrecarregar o XP e dificuldade

@bot.listen("on_message")
async def handle_npc_lore(message):
    """NPCs extras que contam lore"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["falar npc especial", "conversar npc especial", "npc lore", "falar lore npc"]:
        player = get_player(uid)
        if not player:
            return
        world_key = max(k for k in player.get("worlds", [1]))
        npc_pool = WORLD_NPCS_EXTRA.get(world_key, WORLD_NPCS_EXTRA.get(1, []))
        if not npc_pool:
            await message.channel.send("🤷 Nenhum NPC especial aqui.")
            return
        npc = random.choice(npc_pool)
        dialogue = random.choice(npc["dialogues"])
        embed = discord.Embed(
            title=f"{npc['emoji']} {npc['name']} — _{npc['role']}_",
            description=f'*"{dialogue}"*',
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Fale novamente para ouvir mais histórias deste NPC.")
        await message.channel.send(embed=embed)




# ================= FARM AFK =================
@bot.listen("on_message")
async def handle_afk_farm(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["farm afk", "iniciar afk", "afk", "modo afk"]:
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro!")
            return
        if player.get("afk_farming"):
            # Coletar XP acumulado
            elapsed = int(time.time()) - player.get("afk_start", int(time.time()))
            minutes = elapsed // 60
            # 1 XP por minuto (bem pouco, como pedido)
            xp_earned = max(1, min(minutes * 1, 200))  # máx 200 XP por sessão
            player["afk_farming"] = 0
            player["afk_start"] = 0
            leveled = add_xp(uid, xp_earned, bypass_boss_gate=False)
            save_player_db(uid, player)
            embed = discord.Embed(
                title="⏹️ Farm AFK Encerrado!",
                description=f"*'Você retorna ao mundo após um longo descanso...'*\n\n"
                            f"⏱️ Tempo farmando: **{minutes} minutos**\n"
                            f"⭐ XP Ganho: **+{xp_earned}**",
                color=discord.Color.blue()
            )
            if leveled:
                p2 = get_player(uid)
                embed.add_field(name="🆙 Level Up!", value=f"**Nível {p2['level']}**", inline=False)
            embed.set_footer(text="Use 'farm afk' novamente para começar nova sessão.")
            await message.channel.send(embed=embed)
        else:
            player["afk_farming"] = 1
            player["afk_start"] = int(time.time())
            save_player_db(uid, player)
            await message.channel.send(
                f"🌙 **{message.author.mention}** entrou em modo **Farm AFK**!\n\n"
                f"*Você está treinando enquanto ausente...*\n"
                f"⭐ Você ganhará **~1 XP por minuto** (máx 200 XP).\n\n"
                f"Use `farm afk` novamente ao voltar para coletar o XP ganho!"
            )

    elif content in ["ver clima", "clima", "tempo", "clima atual"]:
        weather = CURRENT_WEATHER
        wdata = WEATHER_TYPES.get(weather["type"], WEATHER_TYPES["sol"])
        embed = discord.Embed(
            title=f"{wdata['emoji']} Clima Atual: {wdata['name']}",
            description=wdata["desc"],
            color=discord.Color.blue() if weather["type"] != "lua_sangue" else discord.Color.red()
        )
        if wdata.get("special_monsters"):
            embed.add_field(
                name="👹 Criaturas Especiais Ativas",
                value=" | ".join(wdata["special_monsters"]),
                inline=False
            )
        embed.add_field(name="⚔️ Boost Monstros", value=f"×{wdata['monster_boost']}", inline=True)
        embed.add_field(name="🎁 Boost Drops", value=f"×{wdata['drop_boost']}", inline=True)
        embed.set_footer(text="O clima muda a cada 30 minutos. Lua de Sangue é rara mas muito recompensadora!")
        await message.channel.send(embed=embed)


# ================= PET EVOLUTION =================
@bot.listen("on_message")
async def handle_pet_evolution(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["evoluir pet", "evoluir meu pet", "evolução pet"]:
        player = get_player(uid)
        if not player or not player.get("pet"):
            await message.channel.send("❌ Você não tem um pet ativo! Use `procurar pet` ou `domesticar`.")
            return

        pet_name = player["pet"]
        if isinstance(pet_name, dict):
            pet_name = pet_name.get("name", "")

        evo_data = PET_EVOLUTIONS.get(pet_name)
        if not evo_data:
            await message.channel.send(f"😔 **{pet_name}** não tem evolução disponível ainda (ou já é a forma final).")
            return

        if player["level"] < evo_data["level_required"]:
            await message.channel.send(
                f"❌ **{pet_name}** precisa que você seja **Nível {evo_data['level_required']}** para evoluir!\n"
                f"Seu nível atual: **{player['level']}**"
            )
            return

        # Evoluir!
        next_pet = evo_data["next_data"]
        player["pet"] = next_pet["name"]
        save_player_db(uid, player)

        embed = discord.Embed(
            title="⭐ EVOLUÇÃO DO PET! ⭐",
            description=f"*'Uma luz intensa envolve {pet_name}...'*\n\n"
                        f"🥚 **{pet_name}** → {next_pet['emoji']} **{next_pet['name']}**!\n\n"
                        f"*'Seu companheiro se tornou mais forte!'*",
            color=discord.Color.gold()
        )
        embed.add_field(name="💪 Novo ATK Bônus", value=f"+{next_pet['bonus_atk']}", inline=True)
        embed.add_field(name="❤️ Novo HP Bônus", value=f"+{next_pet['bonus_hp']}", inline=True)
        embed.add_field(name="✨ Raridade", value=f"{RARITIES[next_pet['rarity']]['emoji']} {next_pet['rarity']}", inline=True)
        await message.channel.send(embed=embed)

    elif content in ["ver fazenda", "meus pets", "todos pets", "pets"]:
        player = get_player(uid)
        if not player:
            return
        pets_list = player.get("pets_list", [])
        farm = player.get("pet_farm", [])
        # Combine both lists for display
        all_pets_farm = pets_list + farm
        active = player.get("pet")

        embed = discord.Embed(
            title="🐾 Sua Fazenda de Pets",
            description=f"Pets na fazenda: **{len(all_pets_farm)}/15**",
            color=discord.Color.green()
        )
        if active:
            aname = active if isinstance(active, str) else active.get("name", "?")
            # Find pet data
            pet_obj = None
            for world_pets in PETS.values():
                for p in world_pets:
                    if p["name"] == aname:
                        pet_obj = p
                        break
            if pet_obj:
                evo_info = PET_EVOLUTIONS.get(aname)
                evo_text = f"\n🔄 Próx. evo: **{evo_info['next']}** (Nv. {evo_info['level_required']})" if evo_info else "\n✨ Forma final!"
                embed.add_field(
                    name=f"⭐ Pet Ativo: {pet_obj['emoji']} {aname}",
                    value=f"{RARITIES[pet_obj['rarity']]['emoji']} {pet_obj['rarity']} | +{pet_obj['bonus_atk']} ATK | +{pet_obj['bonus_hp']} HP{evo_text}",
                    inline=False
                )
            else:
                embed.add_field(name="⭐ Pet Ativo", value=aname, inline=False)
        else:
            embed.add_field(name="⭐ Pet Ativo", value="_Nenhum_", inline=False)

        if all_pets_farm:
            farm_lines = []
            for i, p in enumerate(all_pets_farm[:15]):
                pname = p.get("name", "?")
                pemoji = p.get("emoji", "🐾")
                prarity = p.get("rarity", "?")
                batk = p.get("bonus_atk", 0)
                bhp = p.get("bonus_hp", 0)
                farm_lines.append(f"`{i+1}.` {pemoji} **{pname}** [{prarity}] +{batk}ATK/+{bhp}HP")
            embed.add_field(name="🌾 Pets na Fazenda", value="\n".join(farm_lines), inline=False)
        else:
            embed.add_field(name="🌾 Fazenda", value="_Vazia! Use `domesticar` para capturar mais pets._", inline=False)

        embed.set_footer(text="Use 'trocar pet [nome]' para definir ativo | 'evoluir pet' para evoluir | 'trocar pet @user [nome]' para trocar")
        await message.channel.send(embed=embed)

    elif content.startswith("trocar pet") and "@" in content:
        # Pet trading between players
        player = get_player(uid)
        if not player:
            return
        parts = content.split()
        # Format: trocar pet @user [nome do pet]
        target_mention = None
        pet_name_parts = []
        for part in parts[2:]:
            if part.startswith("<@"):
                target_mention = part
            else:
                pet_name_parts.append(part)

        if not target_mention or not pet_name_parts:
            await message.channel.send("❌ Uso: `trocar pet @usuario [nome do pet]`")
            return

        target_id = target_mention.replace("<@", "").replace(">", "").replace("!", "")
        target_player = get_player(target_id)
        if not target_player:
            await message.channel.send("❌ Jogador alvo não encontrado!")
            return

        pet_name = " ".join(pet_name_parts).title()
        pets_list = player.get("pets_list", [])
        farm = player.get("pet_farm", [])

        # Find the pet in sender's farm
        found_pet = None
        for p in pets_list + farm:
            if p.get("name", "").lower() == pet_name.lower():
                found_pet = p
                break

        if not found_pet:
            await message.channel.send(f"❌ Você não tem **{pet_name}** na sua fazenda!\nUse `ver fazenda` para ver seus pets.")
            return

        # Remove from sender, add to target farm
        if found_pet in pets_list:
            pets_list.remove(found_pet)
            player["pets_list"] = pets_list
        elif found_pet in farm:
            farm.remove(found_pet)
            player["pet_farm"] = farm

        t_pets_list = target_player.get("pets_list", [])
        t_pets_list.append(found_pet)
        target_player["pets_list"] = t_pets_list

        save_player_db(uid, player)
        save_player_db(target_id, target_player)

        await message.channel.send(
            f"🤝 **{message.author.display_name}** enviou {found_pet.get('emoji','🐾')} **{found_pet['name']}** "
            f"para <@{target_id}>!\n"
            f"*A amizade une os aventureiros!*"
        )


# ================= SPELL BOOK / LIVRO DE FEITIÇOS =================
@bot.listen("on_message")
async def handle_spell_book(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["livro de feitiços", "abrir livro de feitiços", "feitiços", "ver feitiços", "spellbook"]:
        player = get_player(uid)
        if not player:
            return

        if player["level"] < 12:
            await message.channel.send(
                f"📚 **Livro de Feitiços** — Bloqueado!\n\n"
                f"*'Você ainda não tem poder suficiente para acessar as artes arcanas...'*\n"
                f"Desbloqueie ao atingir o **Nível 12**! (Atual: Nível {player['level']})"
            )
            return

        cls = player.get("class")
        mana_cat = player.get("mana_category", "none")

        # Find current category index
        cat_idx = -1
        for i, cat in enumerate(MANA_CATEGORIES):
            if cat["id"] == mana_cat:
                cat_idx = i
                break

        # Find eligible categories
        unlocked_cats = [cat for cat in MANA_CATEGORIES if player["level"] >= cat["level_req"]]
        current_cat = MANA_CATEGORIES[cat_idx] if cat_idx >= 0 else None

        embed = discord.Embed(
            title="📚 Livro de Feitiços",
            description=f"*'O livro brilha com energia arcana incontida...'*\n\n"
                        f"🎭 Classe: **{cls or 'Sem Classe'}**\n"
                        f"💎 Categoria de Mana: **{current_cat['name'] if current_cat else 'Nenhuma'}**",
            color=discord.Color.purple()
        )

        # Show progression categories
        cat_text = ""
        for cat in MANA_CATEGORIES:
            req = cat["level_req"]
            status = "✅" if player["level"] >= req and cat["id"] in [c["id"] for c in unlocked_cats] else f"🔒 Nv.{req}"
            active = " ◄ ATIVA" if cat["id"] == mana_cat else ""
            cat_text += f"{status} {cat['name']} — {cat['desc']}{active}\n"
        embed.add_field(name="📊 Categorias de Mana", value=cat_text, inline=False)

        # Show class spells if has category
        if cls and cls in SPELL_BOOK_SKILLS and current_cat:
            class_spells = SPELL_BOOK_SKILLS.get(cls, [])
            spell_list = [s for s in class_spells if s["cat"] == mana_cat]
            if spell_list:
                spell_text = "\n".join([f"• **{s['name']}** — Mana: {s['mana_cost']} | Dano: ×{s['dmg_mult']} | {s['desc']}" for s in spell_list])
                embed.add_field(name=f"✨ Feitiços Desbloqueados ({cls})", value=spell_text, inline=False)

        # Show how to advance
        next_cats = [cat for cat in MANA_CATEGORIES if player["level"] < cat["level_req"]]
        if next_cats:
            nc = next_cats[0]
            embed.add_field(
                name="⬆️ Próxima Categoria",
                value=f"{nc['name']} — Atinja **Nível {nc['level_req']}** para desbloquear!",
                inline=False
            )

        embed.set_footer(text="Use 'avançar categoria mana' para subir de categoria | 'treinar mana' para aumentar mana máxima")
        await message.channel.send(embed=embed)

    elif content in ["avançar categoria mana", "subir categoria mana", "avançar mana", "upgrade mana"]:
        player = get_player(uid)
        if not player:
            return
        if player["level"] < 12:
            await message.channel.send("❌ Desbloqueie o Livro de Feitiços primeiro (Nível 12)!")
            return

        mana_cat = player.get("mana_category", "none")
        cat_idx = -1
        for i, cat in enumerate(MANA_CATEGORIES):
            if cat["id"] == mana_cat:
                cat_idx = i
                break

        next_idx = cat_idx + 1
        if cat_idx == -1:
            # First unlock - start at goblin
            first_cat = MANA_CATEGORIES[0]
            if player["level"] < first_cat["level_req"]:
                await message.channel.send(f"❌ Precisa ser Nível {first_cat['level_req']} para começar!")
                return
            player["mana_category"] = first_cat["id"]
            player["spell_book_unlocked"] = 1
            # Bonus max mana
            player["max_mana"] = player.get("max_mana", 50) + int(20 * first_cat["mana_mult"])
            save_player_db(uid, player)
            await message.channel.send(
                f"📚 **Livro de Feitiços Desbloqueado!**\n\n"
                f"Você ingressou na categoria {first_cat['name']}!\n"
                f"💎 Mana Máxima aumentada em **+{int(20 * first_cat['mana_mult'])}**!\n"
                f"*Use `ver feitiços` para ver seus novos poderes!*"
            )
        elif next_idx >= len(MANA_CATEGORIES):
            await message.channel.send("🏆 Você já atingiu a categoria máxima: **💎 Supremo**!")
        else:
            next_cat = MANA_CATEGORIES[next_idx]
            if player["level"] < next_cat["level_req"]:
                await message.channel.send(
                    f"❌ Precisa ser **Nível {next_cat['level_req']}** para avançar para {next_cat['name']}!\n"
                    f"Nível atual: {player['level']}"
                )
                return
            player["mana_category"] = next_cat["id"]
            bonus_mana = int(15 * next_cat["mana_mult"])
            player["max_mana"] = player.get("max_mana", 50) + bonus_mana
            save_player_db(uid, player)
            await message.channel.send(
                f"⬆️ **Categoria Avançada!**\n\n"
                f"Você agora é **{next_cat['name']}**!\n"
                f"💎 +{bonus_mana} Mana Máxima!\n"
                f"*{next_cat['desc']}*"
            )

    elif content.startswith("treinar mana"):
        player = get_player(uid)
        if not player:
            return
        if not player.get("spell_book_unlocked"):
            await message.channel.send("❌ Desbloqueie o Livro de Feitiços primeiro! (Nível 12 + `avançar categoria mana`)")
            return
        cost = 50
        if player["coins"] < cost:
            await message.channel.send(f"❌ Treinar mana custa **{cost} CSI**. Você tem: {player['coins']} CSI.")
            return
        player["coins"] -= cost
        mana_boost = 15
        player["max_mana"] = player.get("max_mana", 50) + mana_boost
        player["mana"] = min(player.get("mana", 50) + mana_boost, player["max_mana"])
        save_player_db(uid, player)
        await message.channel.send(
            f"💎 **Treino de Mana Concluído!**\n\n"
            f"−{cost} CSI | +{mana_boost} Mana Máxima\n"
            f"Nova mana máxima: **{player['max_mana']}**"
        )


# ================= KINGDOM SYSTEM =================
@bot.listen("on_message")
async def handle_kingdom(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["meu reino", "ver reino", "status reino", "reino"]:
        player = get_player(uid)
        if not player:
            return
        if player.get("city_title") != "Rei" and "Rei" not in str(player.get("city_title", "")):
            await message.channel.send(
                "👑 **Sistema de Reinos** — Apenas **Reis** podem gerenciar reinos!\n"
                "*Use `me tornar rei` quando atingir os requisitos!*"
            )
            return

        kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        kname = kd.get("name") or f"Reino de {message.author.display_name}"

        embed = discord.Embed(
            title=f"👑 {kname}",
            description=f"*O seu domínio se estende pelo horizonte...*",
            color=discord.Color.gold()
        )
        def status_icon(s):
            return {"Ruim": "🔴", "Neutra": "🟡", "Boa": "🟢", "Excelente": "💎"}.get(s, "⚪")

        embed.add_field(name="👥 População", value=f"{kd.get('population', 100)} habitantes", inline=True)
        embed.add_field(name=f"💰 Economia {status_icon(kd.get('economy','Neutra'))}", value=kd.get("economy", "Neutra"), inline=True)
        embed.add_field(name=f"⚔️ Exército {status_icon(kd.get('army','Neutra'))}", value=kd.get("army", "Neutra"), inline=True)
        if kd.get("bio"):
            embed.add_field(name="📜 Descrição", value=kd["bio"], inline=False)
        embed.add_field(name="🏆 Guerras Vencidas", value=str(kd.get("wars_won", 0)), inline=True)
        embed.add_field(name="🤝 Trocas Realizadas", value=str(kd.get("trades", 0)), inline=True)
        embed.add_field(
            name="🛠️ Comandos de Reino",
            value="`personalizar reino [nome]` — Renomear seu reino\n"
                  "`melhorar economia` — Invista CSI para melhorar\n"
                  "`reforçar exercito` — Fortaleça suas tropas\n"
                  "`atacar reino @rei` — Declare guerra!\n"
                  "`trocar recursos @rei [valor]` — Coopere com outros reinos",
            inline=False
        )
        await message.channel.send(embed=embed)

    elif content.startswith("personalizar reino"):
        player = get_player(uid)
        if not player:
            return
        if player.get("city_title") != "Rei" and "Rei" not in str(player.get("city_title", "")):
            await message.channel.send("❌ Apenas Reis podem personalizar reinos!")
            return
        parts = message.content.split(maxsplit=2)
        if len(parts) < 3:
            await message.channel.send("❌ Use: `personalizar reino [Nome do Reino]`")
            return
        new_name = parts[2].strip()[:40]
        kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        kd["name"] = new_name
        player["kingdom_data"] = kd
        save_player_db(uid, player)
        await message.channel.send(f"👑 Seu reino foi renomeado para **{new_name}**!\n*Que o nome ecoe por toda a terra!*")

    elif content in ["melhorar economia", "investir economia"]:
        player = get_player(uid)
        if not player:
            return
        if player.get("city_title") != "Rei" and "Rei" not in str(player.get("city_title", "")):
            await message.channel.send("❌ Apenas Reis podem investir no reino!")
            return
        kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        levels = ["Ruim", "Neutra", "Boa", "Excelente"]
        current = kd.get("economy", "Neutra")
        cur_idx = levels.index(current) if current in levels else 1
        costs = [500, 1000, 2500]
        if cur_idx >= len(levels) - 1:
            await message.channel.send("💎 Sua economia já está em nível **Excelente**!")
            return
        cost = costs[cur_idx]
        if player["coins"] < cost:
            await message.channel.send(f"❌ Melhorar a economia custa **{cost} CSI**. Você tem {player['coins']} CSI.")
            return
        player["coins"] -= cost
        kd["economy"] = levels[cur_idx + 1]
        player["kingdom_data"] = kd
        save_player_db(uid, player)
        await message.channel.send(
            f"📈 **Economia melhorada!**\n\n{current} → **{kd['economy']}**\n*Seu povo prospera!*"
        )

    elif content in ["reforçar exercito", "reforcar exercito", "melhorar exercito"]:
        player = get_player(uid)
        if not player:
            return
        if player.get("city_title") != "Rei" and "Rei" not in str(player.get("city_title", "")):
            await message.channel.send("❌ Apenas Reis podem reforçar o exército!")
            return
        kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        levels = ["Ruim", "Neutra", "Boa", "Excelente"]
        current = kd.get("army", "Neutra")
        cur_idx = levels.index(current) if current in levels else 1
        costs = [400, 900, 2000]
        if cur_idx >= len(levels) - 1:
            await message.channel.send("⚔️ Seu exército já está em nível **Excelente**!")
            return
        cost = costs[cur_idx]
        if player["coins"] < cost:
            await message.channel.send(f"❌ Reforçar o exército custa **{cost} CSI**. Você tem {player['coins']} CSI.")
            return
        player["coins"] -= cost
        kd["army"] = levels[cur_idx + 1]
        player["kingdom_data"] = kd
        save_player_db(uid, player)
        await message.channel.send(
            f"⚔️ **Exército reforçado!**\n\n{current} → **{kd['army']}**\n*Suas tropas marcham com determinação!*"
        )

    elif content.startswith("atacar reino"):
        player = get_player(uid)
        if not player:
            return
        if player.get("city_title") != "Rei" and "Rei" not in str(player.get("city_title", "")):
            await message.channel.send("❌ Apenas Reis podem declarar guerra!")
            return
        if "@" not in content:
            await message.channel.send("❌ Use: `atacar reino @rei`")
            return
        mention = message.mentions[0] if message.mentions else None
        if not mention:
            await message.channel.send("❌ Mencione um @rei válido!")
            return
        target_player = get_player(mention.id)
        if not target_player:
            await message.channel.send("❌ Jogador não encontrado!")
            return

        my_kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        their_kd = target_player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()

        army_power = {"Ruim": 1, "Neutra": 2, "Boa": 4, "Excelente": 7}
        my_power = army_power.get(my_kd.get("army", "Neutra"), 2) + player.get("temp_atk_boost", 0) // 10
        their_power = army_power.get(their_kd.get("army", "Neutra"), 2) + target_player.get("temp_atk_boost", 0) // 10

        my_roll = roll_dice() + my_power
        their_roll = roll_dice() + their_power

        their_name = their_kd.get("name") or f"Reino de {mention.display_name}"
        my_name = my_kd.get("name") or f"Reino de {message.author.display_name}"

        embed = discord.Embed(title="⚔️ GUERRA DE REINOS!", color=discord.Color.red())
        embed.add_field(name=f"🏰 {my_name}", value=f"Poder: {my_power} + Dado: {my_roll % 10}", inline=True)
        embed.add_field(name="VS", value="⚔️", inline=True)
        embed.add_field(name=f"🏰 {their_name}", value=f"Poder: {their_power} + Dado: {their_roll % 10}", inline=True)

        if my_roll > their_roll:
            reward = random.randint(200, 600)
            my_kd["wars_won"] = my_kd.get("wars_won", 0) + 1
            my_kd["population"] = my_kd.get("population", 100) + 20
            player["kingdom_data"] = my_kd
            player["coins"] += reward
            save_player_db(uid, player)
            save_player_db(mention.id, target_player)
            embed.add_field(
                name=f"🏆 {my_name} VENCEU!",
                value=f"*'{my_name} domina {their_name}!'*\n\n+{reward} CSI | +20 população",
                inline=False
            )
        else:
            their_kd["wars_won"] = their_kd.get("wars_won", 0) + 1
            target_player["kingdom_data"] = their_kd
            save_player_db(uid, player)
            save_player_db(mention.id, target_player)
            embed.add_field(
                name=f"💀 {their_name} DEFENDEU!",
                value=f"*'{their_name} resistiu ao ataque!'*\n\n{their_name} ganhou +1 vitória de guerra.",
                inline=False
            )
        await message.channel.send(embed=embed)

    elif content.startswith("trocar recursos"):
        player = get_player(uid)
        if not player:
            return
        if "@" not in content:
            await message.channel.send("❌ Use: `trocar recursos @rei [valor em CSI]`")
            return
        parts = content.split()
        mention = message.mentions[0] if message.mentions else None
        if not mention:
            await message.channel.send("❌ Mencione um @rei válido!")
            return
        amount = 0
        for p in parts:
            if p.isdigit():
                amount = int(p)
                break
        if amount <= 0:
            await message.channel.send("❌ Use: `trocar recursos @rei [valor]` — ex: `trocar recursos @rei 500`")
            return
        if player["coins"] < amount:
            await message.channel.send(f"❌ Você tem apenas **{player['coins']} CSI**!")
            return

        target_player = get_player(mention.id)
        if not target_player:
            await message.channel.send("❌ Jogador não encontrado!")
            return

        player["coins"] -= amount
        target_player["coins"] += amount
        my_kd = player.get("kingdom_data") or KINGDOM_DEFAULTS.copy()
        my_kd["trades"] = my_kd.get("trades", 0) + 1
        player["kingdom_data"] = my_kd
        save_player_db(uid, player)
        save_player_db(mention.id, target_player)
        await message.channel.send(
            f"🤝 **Troca de Recursos!**\n\n"
            f"**{message.author.display_name}** enviou **{amount} CSI** para {mention.mention}!\n"
            f"*Alianças entre reinos fortalecem a todos!*"
        )


# ================= WEATHER SYSTEM (muda a cada 30 min) =================
@tasks.loop(minutes=30)
async def weather_change_loop():
    """Muda o clima global a cada 30 minutos"""
    weights = [30, 20, 20, 10, 12, 8]  # sol, chuva, noite, tempestade, neblina, lua_sangue
    new_type = random.choices(list(WEATHER_TYPES.keys()), weights=weights)[0]
    CURRENT_WEATHER["type"] = new_type
    CURRENT_WEATHER["changed_at"] = int(time.time())

    # Anunciar em todos os canais configurados
    wdata = WEATHER_TYPES[new_type]
    for guild in bot.guilds:
        chan = discord.utils.get(guild.text_channels, name=CANAL_BETA)
        if chan:
            embed = discord.Embed(
                title=f"{wdata['emoji']} MUDANÇA DE CLIMA: {wdata['name']}",
                description=wdata["desc"],
                color=discord.Color.red() if new_type == "lua_sangue" else discord.Color.blue()
            )
            if wdata.get("special_monsters"):
                embed.add_field(
                    name="👹 Criaturas Especiais Surgem!",
                    value=" | ".join(wdata["special_monsters"]),
                    inline=False
                )
            embed.add_field(name="⚔️ Monstros Mais Fortes", value=f"×{wdata['monster_boost']}", inline=True)
            embed.add_field(name="🎁 Drops Melhorados", value=f"×{wdata['drop_boost']}", inline=True)
            if new_type == "lua_sangue":
                embed.set_footer(text="⚠️ LUA DE SANGUE: Monstros extremamente perigosos mas recompensas lendárias!")
            try:
                await chan.send(embed=embed)
            except:
                pass


# ================= SISTEMA DE PERÍODO =================
@bot.listen("on_message")
async def handle_period(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if content in ["período", "periodo", "ver período", "hora", "que horas", "tempo do dia"]:
        period_data = TIME_PERIODS.get(CURRENT_PERIOD.get("type", "dia"), TIME_PERIODS["dia"])
        embed = discord.Embed(
            title=f"{period_data['emoji']} Período Atual: {period_data['name']}",
            description=period_data["desc"],
            color=discord.Color.orange()
        )
        embed.add_field(name="⭐ Bônus de XP", value=f"×{period_data['xp_mult']}", inline=True)
        embed.add_field(name="💰 Bônus de Coins", value=f"×{period_data['coin_mult']}", inline=True)
        embed.add_field(name="✨ Especial", value=period_data["special"], inline=False)
        embed.set_footer(text="Use 'descansar' para avançar para o próximo período.")
        await message.channel.send(embed=embed)

    elif content in ["descansar", "dormir", "passar tempo", "descanso"]:
        player = get_player(uid)
        if not player:
            return
        current_idx = PERIOD_ORDER.index(CURRENT_PERIOD.get("type", "dia"))
        next_idx = (current_idx + 1) % len(PERIOD_ORDER)
        next_period_key = PERIOD_ORDER[next_idx]
        CURRENT_PERIOD["type"] = next_period_key
        CURRENT_PERIOD["changed_at"] = int(time.time())
        next_data = TIME_PERIODS[next_period_key]

        # Restaurar HP e Mana ao descansar
        player["hp"] = player["max_hp"]
        player["mana"] = player.get("max_mana", 50)
        save_player_db(uid, player)

        embed = discord.Embed(
            title=f"😴 Você descansou...",
            description=f"*O tempo passa enquanto você repousa suas forças.*\n\nO período avançou para **{next_data['emoji']} {next_data['name']}**!\n\n_{next_data['desc']}_",
            color=discord.Color.dark_blue()
        )
        embed.add_field(name="💚 HP Restaurado", value=f"`{player['max_hp']}/{player['max_hp']}`", inline=True)
        embed.add_field(name="💙 Mana Restaurada", value=f"`{player['mana']}/{player['mana']}`", inline=True)
        embed.add_field(name="⭐ Bônus do Período", value=f"XP ×{next_data['xp_mult']} | Coins ×{next_data['coin_mult']}", inline=False)
        if next_period_key == "meia_noite":
            embed.set_footer(text="🕛 MEIA-NOITE! Hora dos drops lendários — explore agora!")
        await message.channel.send(embed=embed)


# ================= SUPORTE EM BATALHA PvP/Boss =================
@bot.listen("on_message")
async def handle_support_action(message):
    """Classes de suporte podem curar aliados usando 'curar @aliado'"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    if (content.startswith("curar ") or content.startswith("apoiar ")) and message.mentions:
        player = get_player(uid)
        if not player:
            return
        cls = player.get("class", "")
        if cls not in SUPPORT_CLASSES:
            await message.channel.send(f"❌ Apenas classes de suporte podem curar! ({', '.join(SUPPORT_CLASSES)})")
            return

        mana_cost = 20
        if player.get("mana", 0) < mana_cost:
            await message.channel.send(f"❌ Você não tem mana suficiente! (Precisa de {mana_cost}, tem {player.get('mana', 0)})")
            return

        target = message.mentions[0]
        target_player = get_player(target.id)
        if not target_player:
            await message.channel.send("❌ Alvo não encontrado!")
            return

        # Rola dado para determinar efetividade da cura
        roll = roll_dice()
        luck = get_luck(roll)

        base_heal = CLASSES.get(cls, {}).get("hp_bonus", 10) + player["level"] * 2
        heal_mult = roll / 5  # dado 1-10 → multiplicador 0.2–2.0
        heal_amount = max(10, int(base_heal * heal_mult))

        old_hp = target_player["hp"]
        target_player["hp"] = min(target_player["max_hp"], target_player["hp"] + heal_amount)
        actual_heal = target_player["hp"] - old_hp

        player["mana"] = max(0, player.get("mana", 0) - mana_cost)
        save_player_db(uid, player)
        save_player_db(target.id, target_player)

        cls_emoji = CLASSES.get(cls, {}).get("emoji", "✨")
        embed = discord.Embed(
            title=f"{cls_emoji} Suporte Ativado!",
            description=f"*{message.author.display_name}* usa suas habilidades de **{cls}** para curar **{target.display_name}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="🎲 Dado", value=f"`{roll}` {luck['emoji']} **{luck['name']}**", inline=True)
        embed.add_field(name="💚 HP Curado", value=f"+{actual_heal} HP", inline=True)
        embed.add_field(name="💙 Mana Usada", value=f"-{mana_cost}", inline=True)
        embed.add_field(name=f"❤️ {target.display_name}", value=f"`{target_player['hp']}/{target_player['max_hp']}` HP", inline=False)
        await message.channel.send(embed=embed)


# ================= NOTIFICAÇÃO LIVRO DE FEITIÇOS =================
@bot.listen("on_message")
async def handle_spellbook_notify(message):
    """Notifica quando jogador desbloqueou livro de feitiços no nível 12"""
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    uid = str(message.author.id)
    player = get_player(uid)
    if not player:
        return
    effects = player.get("active_effects", {})
    if effects.get("notify_spellbook"):
        effects.pop("notify_spellbook")
        player["active_effects"] = effects
        save_player_db(uid, player)
        embed = discord.Embed(
            title="📖 LIVRO DE FEITIÇOS DESBLOQUEADO!",
            description=f"*'As páginas do conhecimento arcano se abrem diante de você...'*\n\n"
                        f"**{message.author.mention}** chegou ao **Nível 12** e desbloqueou o **Livro de Feitiços**!\n\n"
                        f"Agora você pode acessar magias poderosas usando mana.\nUse `livro de feitiços` para ver seus feitiços disponíveis.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="📖 'O conhecimento é a arma mais poderosa de todas.'")
        await message.channel.send(embed=embed)




@bot.listen("on_message")
async def handle_admin_levelup(message):
    """Comando exclusivo do admin para upar de nivel automaticamente.
    Uso:
      !admin upar             -> +1 nivel no seu personagem
      !admin upar 5           -> +5 niveis no seu personagem
      !admin upar @user       -> +1 nivel no personagem do @user
      !admin upar @user 3     -> +3 niveis no @user
    """
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return
    if message.author.id != ADMIN_ID:
        return

    content = message.content.lower().strip()
    if not content.startswith("!admin upar"):
        return

    parts = message.content.strip().split()
    target_user = message.author
    levels_to_add = 1

    extra = parts[2:]
    for part in extra:
        if part.startswith("<@") and message.mentions:
            target_user = message.mentions[0]
        else:
            try:
                levels_to_add = max(1, min(int(part), 100))
            except ValueError:
                pass

    uid = str(target_user.id)
    player = get_player(uid)
    if not player:
        await message.channel.send(f"Jogador {target_user.display_name} nao encontrado!")
        return

    old_level = player["level"]

    for _ in range(levels_to_add):
        player["xp"] = 0
        player["level"] += 1
        class_bonus = 0
        if player.get("class") and player["class"] in CLASSES:
            class_bonus = CLASSES[player["class"]]["hp_bonus"] // 10
        player["max_hp"] += (10 + class_bonus)
        player["hp"] = player["max_hp"]
        new_max_mana = calc_max_mana(player)
        player["max_mana"] = new_max_mana
        player["mana"] = new_max_mana
        if player["level"] == 12 and not player.get("spell_book_unlocked"):
            player["spell_book_unlocked"] = 1

    save_player_db(uid, player)

    embed = discord.Embed(
        title="ADMIN - NIVEL AUMENTADO",
        description=f"{target_user.display_name} subiu de nivel por comando admin!",
        color=discord.Color.gold()
    )
    embed.add_field(name="Nivel Anterior", value=f"`{old_level}`", inline=True)
    embed.add_field(name="Novo Nivel", value=f"`{player['level']}`", inline=True)
    embed.add_field(name="Niveis Adicionados", value=f"`+{levels_to_add}`", inline=True)
    embed.add_field(name="HP Max", value=f"`{player['max_hp']}`", inline=True)
    embed.add_field(name="Mana Max", value=f"`{player['max_mana']}`", inline=True)
    embed.set_footer(text="Comando exclusivo do administrador")
    await message.channel.send(embed=embed)



# ================= BATALHA DE PETS =================
# Desafios pendentes: {challenger_id: {"target_id": ..., "pet_name": ..., "timestamp": ...}}
PET_BATTLE_CHALLENGES = {}

def get_pet_battle_stats(player):
    """Retorna o pet ativo e seus stats de batalha."""
    pet_name = player.get("pet")
    if not pet_name:
        return None
    if isinstance(pet_name, dict):
        pet_name = pet_name.get("name", "")

    # Busca dados base do pet em PETS e em evoluções
    pet_data = None
    for world_pets in PETS.values():
        for p in world_pets:
            if p["name"] == pet_name:
                pet_data = dict(p)
                break
        if pet_data:
            break

    # Se não achou (pet evoluído), busca nos next_data de PET_EVOLUTIONS
    if not pet_data:
        for evo in PET_EVOLUTIONS.values():
            nd = evo.get("next_data", {})
            if nd.get("name") == pet_name:
                pet_data = dict(nd)
                break

    if not pet_data:
        pet_data = {"name": pet_name, "emoji": "🐾", "rarity": "Comum", "bonus_hp": 10, "bonus_atk": 3}

    # HP e ATK de batalha — escala com nível do dono
    owner_level = player.get("level", 1)
    base_hp  = pet_data["bonus_hp"] * 5 + owner_level * 3
    base_atk = pet_data["bonus_atk"] + owner_level // 2

    # Bônus por raridade
    rarity_mult = {"Comum":1.0,"Incomum":1.1,"Raro":1.25,"Épico":1.4,
                   "Lendário":1.6,"Mítico":1.85,"Divino":2.2,"Primordial":2.8}
    mult = rarity_mult.get(pet_data.get("rarity","Comum"), 1.0)
    hp  = int(base_hp  * mult)
    atk = int(base_atk * mult)

    pet_data["battle_hp"]  = hp
    pet_data["battle_atk"] = atk
    return pet_data


@bot.listen("on_message")
async def handle_pet_battle(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return

    content = message.content.lower().strip()
    uid = str(message.author.id)

    # ─── DESAFIAR PET ────────────────────────────────────────────────
    # "batalha pet @user"
    if (content.startswith("batalha pet") or content.startswith("desafiar pet")) and message.mentions:
        challenger = get_player(uid)
        if not challenger:
            return
        if not challenger.get("pet"):
            await message.channel.send(f"❌ {message.author.mention} você não tem pet ativo! Use `trocar pet [nome]`.")
            return

        target_user = message.mentions[0]
        if target_user.id == message.author.id:
            await message.channel.send("❌ Você não pode batalhar contra si mesmo!")
            return

        target = get_player(target_user.id)
        if not target:
            await message.channel.send(f"❌ {target_user.display_name} ainda não tem personagem.")
            return
        if not target.get("pet"):
            await message.channel.send(f"❌ {target_user.display_name} não tem pet ativo!")
            return

        c_pet = get_pet_battle_stats(challenger)
        t_pet = get_pet_battle_stats(target)

        PET_BATTLE_CHALLENGES[str(target_user.id)] = {
            "challenger_id": uid,
            "c_pet": c_pet,
            "t_pet": t_pet,
            "timestamp": time.time()
        }

        embed = discord.Embed(
            title="⚔️ DESAFIO DE PETS!",
            description=f"{message.author.mention} desafia {target_user.mention} para uma batalha de pets!",
            color=discord.Color.orange()
        )
        embed.add_field(
            name=f"{c_pet['emoji']} {c_pet['name']} ({message.author.display_name})",
            value=f"❤️ HP: `{c_pet['battle_hp']}` | ⚔️ ATK: `{c_pet['battle_atk']}`\n{RARITIES[c_pet['rarity']]['emoji']} {c_pet['rarity']}",
            inline=True
        )
        embed.add_field(
            name=f"{t_pet['emoji']} {t_pet['name']} ({target_user.display_name})",
            value=f"❤️ HP: `{t_pet['battle_hp']}` | ⚔️ ATK: `{t_pet['battle_atk']}`\n{RARITIES[t_pet['rarity']]['emoji']} {t_pet['rarity']}",
            inline=True
        )
        embed.set_footer(text=f"{target_user.display_name}, responda com 'aceitar pet' para batalhar! (expira em 2 min)")
        await message.channel.send(embed=embed)
        return

    # ─── ACEITAR BATALHA DE PET ──────────────────────────────────────
    if content in ["aceitar pet", "aceitar batalha pet"]:
        challenge = PET_BATTLE_CHALLENGES.get(uid)
        if not challenge:
            await message.channel.send(f"❌ {message.author.mention} você não tem desafio de pet pendente!")
            return
        if time.time() - challenge["timestamp"] > 120:
            PET_BATTLE_CHALLENGES.pop(uid, None)
            await message.channel.send("❌ O desafio expirou! Peça para reenviar.")
            return

        PET_BATTLE_CHALLENGES.pop(uid, None)

        challenger_id = challenge["challenger_id"]
        try:
            challenger_user = await bot.fetch_user(int(challenger_id))
        except:
            challenger_user = None

        c_pet = challenge["c_pet"]
        t_pet = challenge["t_pet"]

        c_hp = c_pet["battle_hp"]
        t_hp = t_pet["battle_hp"]
        c_atk = c_pet["battle_atk"]
        t_atk = t_pet["battle_atk"]

        # ── SIMULAÇÃO DA BATALHA ─────────────────────────────────────
        MOVES = {
            "Comum":     ["Arranhão", "Mordida", "Chute"],
            "Incomum":   ["Golpe Rápido", "Ataque Ágil", "Investida"],
            "Raro":      ["Garra Afiada", "Impacto Sólido", "Rugido"],
            "Épico":     ["Explosão Épica", "Golpe Épico", "Fúria"],
            "Lendário":  ["Lança Lendária", "Tempestade", "Poder Lendário"],
            "Mítico":    ["Raio Mítico", "Abismo", "Colapso"],
            "Divino":    ["Luz Divina", "Julgamento", "Purificação"],
            "Primordial":["Extinção", "Caos Primordial", "Aniquilação"],
        }

        battle_log = []
        turn = 0
        c_cur = c_hp
        t_cur = t_hp

        c_rar = c_pet.get("rarity","Comum")
        t_rar = t_pet.get("rarity","Comum")

        while c_cur > 0 and t_cur > 0 and turn < 30:
            turn += 1
            # Crítico: 20% chance, 1.5x dano
            c_crit = random.random() < 0.20
            t_crit = random.random() < 0.20

            c_dmg = max(1, int(c_atk * random.uniform(0.8, 1.3) * (1.5 if c_crit else 1.0)))
            t_dmg = max(1, int(t_atk * random.uniform(0.8, 1.3) * (1.5 if t_crit else 1.0)))

            t_cur = max(0, t_cur - c_dmg)
            c_cur = max(0, c_cur - t_dmg)

            c_move = random.choice(MOVES.get(c_rar, MOVES["Comum"]))
            t_move = random.choice(MOVES.get(t_rar, MOVES["Comum"]))

            c_bar = "█" * int(c_cur/c_hp*10) + "░" * (10 - int(c_cur/c_hp*10))
            t_bar = "█" * int(t_cur/t_hp*10) + "░" * (10 - int(t_cur/t_hp*10))

            entry = (
                f"**Turno {turn}**\n"
                f"{c_pet['emoji']} **{c_move}**{'💥' if c_crit else ''}: `-{c_dmg}` → {t_pet['emoji']} `{max(0,t_cur)}/{t_hp}` [{t_bar}]\n"
                f"{t_pet['emoji']} **{t_move}**{'💥' if t_crit else ''}: `-{t_dmg}` → {c_pet['emoji']} `{max(0,c_cur)}/{c_hp}` [{c_bar}]"
            )
            battle_log.append(entry)

            if c_cur <= 0 or t_cur <= 0:
                break

        # ── RESULTADO ────────────────────────────────────────────────
        if c_cur > t_cur:
            winner_name = challenger_user.display_name if challenger_user else "Desafiante"
            winner_pet  = c_pet
            loser_pet   = t_pet
            loser_name  = message.author.display_name
            winner_mention = challenger_user.mention if challenger_user else "Desafiante"
        elif t_cur > c_cur:
            winner_name    = message.author.display_name
            winner_pet     = t_pet
            loser_pet      = c_pet
            loser_name     = challenger_user.display_name if challenger_user else "Desafiante"
            winner_mention = message.author.mention
        else:
            winner_name    = None
            winner_mention = None

        # Envia turnos em embed (divide se muito longo)
        fight_embed = discord.Embed(
            title=f"🥊 BATALHA DE PETS — {c_pet['emoji']} {c_pet['name']} vs {t_pet['emoji']} {t_pet['name']}",
            description=f"*'Que comecem os jogos!'*\n\n" + "\n\n".join(battle_log[:5]),
            color=discord.Color.red()
        )
        fight_embed.add_field(
            name="📊 Stats Iniciais",
            value=(
                f"{c_pet['emoji']} **{c_pet['name']}**: `{c_hp}` HP | `{c_atk}` ATK\n"
                f"{t_pet['emoji']} **{t_pet['name']}**: `{t_hp}` HP | `{t_atk}` ATK"
            ),
            inline=False
        )
        await message.channel.send(embed=fight_embed)
        await asyncio.sleep(2)

        # Turnos do meio
        if len(battle_log) > 5:
            mid_embed = discord.Embed(
                title="⚔️ A batalha continua...",
                description="\n\n".join(battle_log[5:10]),
                color=discord.Color.orange()
            )
            await message.channel.send(embed=mid_embed)
            await asyncio.sleep(2)

        if len(battle_log) > 10:
            mid2_embed = discord.Embed(
                title="💢 Fase final da batalha!",
                description="\n\n".join(battle_log[10:15]),
                color=discord.Color.dark_red()
            )
            await message.channel.send(embed=mid2_embed)
            await asyncio.sleep(2)

        # Resultado final
        if winner_name:
            xp_reward = max(30, (winner_pet["battle_atk"] + loser_pet["battle_atk"]) * 2)
            add_xp(str(challenger_id) if c_cur > t_cur else uid, xp_reward)

            result_embed = discord.Embed(
                title=f"🏆 {winner_pet['emoji']} {winner_pet['name']} VENCEU!",
                description=(
                    f"*'O público enlouquece!'*\n\n"
                    f"🥇 **{winner_name}** e seu {winner_pet['emoji']} **{winner_pet['name']}** triunfam!\n"
                    f"💀 **{loser_name}** e seu {loser_pet['emoji']} **{loser_pet['name']}** foram derrotados!\n\n"
                    f"⭐ **{winner_name}** ganhou `+{xp_reward} XP`!"
                ),
                color=discord.Color.gold()
            )
            result_embed.add_field(
                name="📊 HP Final",
                value=(
                    f"{winner_pet['emoji']} **{winner_pet['name']}**: `{max(c_cur,t_cur)}` HP restante\n"
                    f"{loser_pet['emoji']} **{loser_pet['name']}**: `0` HP"
                ),
                inline=False
            )
            result_embed.add_field(name="🎲 Turnos", value=f"`{turn}` turnos", inline=True)
        else:
            result_embed = discord.Embed(
                title="🤝 EMPATE!",
                description=f"*'Ambos os pets caem ao mesmo tempo!'*\n\n{c_pet['emoji']} **{c_pet['name']}** e {t_pet['emoji']} **{t_pet['name']}** empataram!",
                color=discord.Color.greyple()
            )

        result_embed.set_footer(text="Use 'batalha pet @user' para desafiar alguém | 'evoluir pet' para ficar mais forte!")
        await message.channel.send(embed=result_embed)
        return

    # ─── VER STATS DO PET (para batalha) ────────────────────────────
    if content in ["stats pet", "poder pet", "meu pet stats"]:
        player = get_player(uid)
        if not player or not player.get("pet"):
            await message.channel.send("❌ Você não tem pet ativo!")
            return
        pet = get_pet_battle_stats(player)
        evo_info = PET_EVOLUTIONS.get(pet["name"])
        evo_text = f"\n🔄 Próx. evo: **{evo_info['next']}** (Nv. {evo_info['level_required']})" if evo_info else "\n✨ Forma final!"
        embed = discord.Embed(
            title=f"{pet['emoji']} Stats de Batalha — {pet['name']}",
            description=f"{RARITIES[pet['rarity']]['emoji']} **{pet['rarity']}**{evo_text}",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ HP Batalha",  value=f"`{pet['battle_hp']}`",  inline=True)
        embed.add_field(name="⚔️ ATK Batalha", value=f"`{pet['battle_atk']}`", inline=True)
        embed.set_footer(text="Stats escalam com o nível do dono + raridade do pet")
        await message.channel.send(embed=embed)


# ================= QUARTA FORMA EXCLUSIVA PARA PETS COMUNS =================
# Pets comuns (rarity="Comum") têm uma quarta forma especial exclusiva para eles
# Pets de nível mais alto (Lendário+) podem ter Forma Bestial (desbloqueada no nível 80 do jogador)

COMMON_PET_FOURTH_FORMS = {
    # ── Mundo 1 ───────────────────────────────────────────────────────
    "Slime Bebê": {
        "level_required": 3,
        "next": "Slime Rei Menor",
        "next_data": {"name": "Slime Rei Menor", "emoji": "👑", "rarity": "Comum",
                      "bonus_hp": 80, "bonus_atk": 30, "special": True, "form": "quarta_forma",
                      "desc": "A forma final dos Slimes Comuns — um Rei Slime em miniatura! Nenhum pet raro jamais alcançará isto."}
    },
    "Slime Adolescente": {
        "level_required": 5,
        "next": "Slime Rei do Abismo",
        "next_data": {"name": "Slime Rei do Abismo", "emoji": "🌑", "rarity": "Comum",
                      "bonus_hp": 100, "bonus_atk": 40, "special": True, "form": "quarta_forma",
                      "desc": "O Slime que tocou o Abismo. Uma mutação única que nenhuma raridade superior pode replicar!"}
    },
    "Rato Selvagem Domesticado": {
        "level_required": 2,
        "next": "Rato Ancestral",
        "next_data": {"name": "Rato Ancestral", "emoji": "🐀", "rarity": "Comum",
                      "bonus_hp": 60, "bonus_atk": 22, "special": True, "form": "quarta_forma",
                      "desc": "Pequeno mas absolutamente implacável. Superou todos os limites da sua raça!"}
    },
    "Fungo Espiritual": {
        "level_required": 4,
        "next": "Fungo Primordial",
        "next_data": {"name": "Fungo Primordial", "emoji": "🍄", "rarity": "Comum",
                      "bonus_hp": 75, "bonus_atk": 18, "special": True, "form": "quarta_forma",
                      "desc": "Absorveu energia espiritual dos Campos Iniciais por gerações. Tóxico e misterioso!"}
    },
    "Lagarta Arcana": {
        "level_required": 3,
        "next": "Mariposa do Caos",
        "next_data": {"name": "Mariposa do Caos", "emoji": "🦋", "rarity": "Comum",
                      "bonus_hp": 65, "bonus_atk": 25, "special": True, "form": "quarta_forma",
                      "desc": "Nunca virou borboleta — virou Caos! Uma forma que nenhum pet raro pode imitar."}
    },
    # ── Mundo 10 ──────────────────────────────────────────────────────
    "Toupeira das Sombras": {
        "level_required": 5,
        "next": "Toupeira Cega Ancestral",
        "next_data": {"name": "Toupeira Cega Ancestral", "emoji": "🦡", "rarity": "Comum",
                      "bonus_hp": 90, "bonus_atk": 28, "special": True, "form": "quarta_forma",
                      "desc": "Cega mas percebe o mundo de formas impossíveis. Poder através da escuridão absoluta!"}
    },
    "Cogumelo Sombrio": {
        "level_required": 5,
        "next": "Cogumelo Maldito Eterno",
        "next_data": {"name": "Cogumelo Maldito Eterno", "emoji": "🍄", "rarity": "Comum",
                      "bonus_hp": 85, "bonus_atk": 32, "special": True, "form": "quarta_forma",
                      "desc": "Absorveu a maldição da floresta inteira. Venenoso ao extremo!"}
    },
    # ── Mundo 20 ──────────────────────────────────────────────────────
    "Besouro do Deserto": {
        "level_required": 8,
        "next": "Besouro Faraó",
        "next_data": {"name": "Besouro Faraó", "emoji": "🪲", "rarity": "Comum",
                      "bonus_hp": 110, "bonus_atk": 38, "special": True, "form": "quarta_forma",
                      "desc": "O Faraó dos besouros! Sobreviveu ao sol ardente por séculos. Carrega toda a força do deserto!"}
    },
    "Cobra das Areias": {
        "level_required": 8,
        "next": "Cobra Guardiã das Areias",
        "next_data": {"name": "Cobra Guardiã das Areias", "emoji": "🐍", "rarity": "Comum",
                      "bonus_hp": 95, "bonus_atk": 42, "special": True, "form": "quarta_forma",
                      "desc": "Guardou os segredos das pirâmides por milênios. Veneno que carrega memória de mil faraós!"}
    },
}

BESTIAL_FORMS = {
    "Lobo Alpha Lendário": {
        "name": "Lobo Bestial Primordial", "emoji": "🐺", "rarity": "Lendário",
        "bonus_hp": 200, "bonus_atk": 100,
        "special": True, "form": "bestial",
        "desc": "A Forma Bestial desperta o poder ancestral do lobo primordial. Desbloqueada ao nível 80."
    },
    "Esfinge Imortal": {
        "name": "Esfinge Bestial Cósmica", "emoji": "🦁", "rarity": "Divino",
        "bonus_hp": 350, "bonus_atk": 175,
        "special": True, "form": "bestial",
        "desc": "A Forma Bestial transforma a Esfinge na guarda cósmica perfeita."
    },
    "Fênix Eterna": {
        "name": "Fênix Bestial do Caos", "emoji": "🔥", "rarity": "Divino",
        "bonus_hp": 400, "bonus_atk": 200,
        "special": True, "form": "bestial",
        "desc": "A Forma Bestial desperta o fogo do caos primordial dentro da Fênix."
    },
    "Dragão de Gelo Ancião": {
        "name": "Dragão Bestial do Gelo Eterno", "emoji": "❄️", "rarity": "Divino",
        "bonus_hp": 450, "bonus_atk": 225,
        "special": True, "form": "bestial",
        "desc": "A Forma Bestial libera o poder do gelo eterno que dormia no dragão ancião."
    },
    "Lobo Alpha Lendário": {
        "name": "Lobo Bestial Primordial", "emoji": "🐺", "rarity": "Lendário",
        "bonus_hp": 180, "bonus_atk": 90,
        "special": True, "form": "bestial",
        "desc": "O lobo unleashes power dormant since the first moon."
    },
    "Arcanjo Primordial": {
        "name": "Arcanjo Bestial Supremo", "emoji": "🕊️", "rarity": "Primordial",
        "bonus_hp": 800, "bonus_atk": 400,
        "special": True, "form": "bestial",
        "desc": "A Forma Bestial de um Arcanjo Primordial é simplesmente indescritível."
    },
    "Deus Primordial": {
        "name": "Deus Bestial Absoluto", "emoji": "✨", "rarity": "Primordial",
        "bonus_hp": 1000, "bonus_atk": 500,
        "special": True, "form": "bestial",
        "desc": "Forma Bestial do poder divino absoluto. Poucos sobrevivem para contar."
    },
}

# NPCs do mundo com diálogos de lore, segredos e quests ocultas
NPC_DIALOGUES_EXTENDED = {
    "Theron": {
        "full_name": "Aldeão Theron",
        "emoji": "👨‍🌾",
        "world": 1,
        "lore": [
            "Este reino existe há mais de mil anos. Mas poucos sabem que antes havia outro, engolido pelo Vazio.",
            "Minha avó dizia que o primeiro slime não nasceu aqui. Ele caiu de uma fenda no céu — quando o Abismo tentou invadir.",
            "Há uma cripta sob os Campos. Nunca entrei. Quem entra ouve vozes. Quem sai... não é mais a mesma pessoa.",
        ],
        "secrets": [
            "Se você cavar no centro exato dos Campos na lua cheia, encontrará uma pedra com um símbolo estranho. Dizem que é a marca do Primeiro Deus.",
            "O Slime Rei não morre de verdade. Ele absorve a magia da terra e renasce. Sempre renascerá... a menos que a fonte seja destruída.",
        ],
        "hidden_quests": [
            {
                "id": "hq_theron_001",
                "name": "🌑 A Cripta dos Campos",
                "description": "Theron te conta sobre uma cripta oculta nos Campos. Explore e descubra o que há lá.",
                "type": "individual", "objective": "explore", "count": 1,
                "reward_xp": 2000, "reward_coins": 50, "reward_item": "Fragmento de Cristal Antigo",
                "lore": "A cripta guarda um segredo que os aldeões preferiram esquecer.",
                "npc": "Aldeão Theron", "difficulty": "Raro"
            }
        ]
    },
    "Elara": {
        "full_name": "Curandeira Elara",
        "emoji": "👩‍⚕️",
        "world": 1,
        "lore": [
            "As ervas destes campos foram criadas por uma druida que deu sua vida para que elas crescessem para sempre.",
            "Já curei feridas que não deveriam existir. Marcas de algo que não vive neste mundo.",
            "A magia de cura não cria — ela restaura. Mas e se algo nunca foi inteiro para começo de conversa?",
        ],
        "secrets": [
            "Existe uma poção que pode restaurar um item destruído. A receita está guardada num livro que só aparece nas noites de neblina arcana.",
            "O veneno das Vespas Gigantes ao norte, se processado corretamente, cura qualquer maldição. Ninguém mais sabe fazer isso.",
        ],
        "hidden_quests": []
    },
    "Sylvara": {
        "full_name": "Druida Sylvara",
        "emoji": "🧙‍♀️",
        "world": 10,
        "lore": [
            "A Floresta Sombria tem memória. Cada árvore lembra de quem passou por aqui. Você está sendo lembrado agora.",
            "O Ent Ancião tem 3.000 anos. Ele viu o mundo antes dos humanos. Seu primeiro pensamento foi: 'que barulhentos'.",
            "Existe uma linguagem que apenas árvores falam. Levei 40 anos para aprender as primeiras três palavras.",
        ],
        "secrets": [
            "No coração da floresta existe uma clareira que não aparece em nenhum mapa. Nela, o tempo passa diferente.",
            "Os goblins desta floresta foram corrompidos por um artefato que ninguém encontrou ainda. Quem o destruir libertará a floresta.",
        ],
        "hidden_quests": [
            {
                "id": "hq_sylvara_001",
                "name": "🌳 O Artefato Corrompido",
                "description": "Sylvara te pede para encontrar o artefato que corrompeu os goblins da floresta.",
                "type": "individual", "objective": "explore", "count": 5,
                "reward_xp": 4000, "reward_coins": 80, "reward_item": "Essência Pura da Floresta",
                "lore": "O artefato pulsa com uma energia estranha. Como chegou aqui ninguém sabe.",
                "npc": "Druida Sylvara", "difficulty": "Difícil"
            }
        ]
    },
    "Bjorn": {
        "full_name": "Ancião da Montanha Bjorn",
        "emoji": "🧙",
        "world": 30,
        "lore": [
            "Os Titãs do Gelo não foram destruídos. Eles dormiram. E sonham. E os sonhos deles moldam estas montanhas.",
            "Krom, o Yeti, uma vez me falou. Ele disse: 'Preciso proteger, mas esqueci do quê.' Meu coração partiu.",
            "O Cristal do Inverno Eterno guarda memórias de mil anos de gelo. Quem o tocar verá tudo que já morreu neste frio.",
        ],
        "secrets": [
            "Há uma câmara secreta dentro do Yeti. Não literalmente — mas uma caverna que brilha com a mesma luz dos seus olhos.",
            "Se você derrotar Krom com compaixão — sem habilidades destrutivas — ele sussurra um nome antes de cair. O nome é a senha para a câmara.",
        ],
        "hidden_quests": [
            {
                "id": "hq_bjorn_001",
                "name": "❄️ O Segredo de Krom",
                "description": "Bjorn te conta que Krom guarda um segredo que pode revelar o paradeiro dos Titãs do Gelo.",
                "type": "individual", "objective": "boss", "target": "Yeti Colossal",
                "reward_xp": 8000, "reward_coins": 200, "reward_item": "Fragmento de Titã do Gelo",
                "lore": "A verdade sobre os Titãs do Gelo pode mudar tudo que você sabe sobre este mundo.",
                "npc": "Ancião Bjorn", "difficulty": "Muito Difícil"
            }
        ]
    },
    "Ramses": {
        "full_name": "Arqueólogo Ramses",
        "emoji": "🏺",
        "world": 20,
        "lore": [
            "A Décima Dinastia durou 600 anos. Eu passei 30 tentando entender por que ela caiu em um único dia.",
            "Os hieróglifos mais antigos não descrevem deuses. Descrevem algo muito mais velho e muito mais assustador.",
            "Kha-Mentu me visitou em sonho uma vez. Ele disse: 'O Olho de Ra não é uma joia. É um olho de verdade.'",
        ],
        "secrets": [
            "Existe uma pirâmide no deserto que não aparece de dia. Só ao entardecer, quando as sombras alcançam certo ângulo.",
            "O Faraó Kha-Mentu tinha um filho. Ninguém sabe o que aconteceu com ele. Os hieróglifos mencionam 'o Herdeiro Perdido'.",
        ],
        "hidden_quests": []
    },
    "Spectra": {
        "full_name": "Bibliotecária Spectra",
        "emoji": "👻",
        "world": 50,
        "lore": [
            "O Abismo não é um lugar. É um estado. Você pode estar no Abismo agora mesmo sem saber.",
            "Estudei aqui por 200 anos. Todo dia aprendo algo que desfaz o que aprendi antes.",
            "O Senhor das Sombras me perguntou uma vez: 'O que é pior — não existir, ou existir em sofrimento?' Ainda não respondi.",
        ],
        "secrets": [
            "Há uma sala nesta biblioteca que eu nunca abri. Ela abre sozinha em certas noites. E fecha antes que alguém possa entrar.",
            "O verdadeiro nome do Senhor das Sombras é proibido de ser dito. Mas está escrito em um livro aqui. Eu nunca o li.",
        ],
        "hidden_quests": [
            {
                "id": "hq_spectra_001",
                "name": "📚 O Livro Proibido",
                "description": "Spectra te conta sobre um livro que nunca foi lido. Encontre-o.",
                "type": "individual", "objective": "explore", "count": 8,
                "reward_xp": 15000, "reward_coins": 300, "reward_item": "Página do Livro Proibido",
                "lore": "Alguns conhecimentos existem para nunca serem descobertos. Ou será que existem para serem descobertos pelos dignos?",
                "npc": "Bibliotecária Spectra", "difficulty": "Mítico"
            }
        ]
    },
    "Imperador Astral": {
        "full_name": "Imperador Astral",
        "emoji": "👑",
        "world": 60,
        "lore": [
            "Governei os céus por dez mil anos. Você é a primeira criatura mortal que chega até mim sem ser destruída primeiro.",
            "Os deuses não criaram o universo. Encontraram ele. Eu fui o primeiro a acordar dentro dele.",
            "O verdadeiro poder não é destruição. É criação. Qualquer tolo pode destruir — poucos são capazes de criar.",
        ],
        "secrets": [
            "Existe um décimo terceiro reino além do Trono Celestial. Não está em nenhum mapa. Chega-se apenas sendo digno.",
            "O teste final não é derrotar inimigos. É fazer uma escolha que a maioria dos heróis se recusa a considerar.",
        ],
        "hidden_quests": []
    },
}

# Mapeamento de nomes parciais para NPCs
NPC_NAME_MAP = {
    "theron": "Theron", "aldeão": "Theron", "aldeao": "Theron",
    "elara": "Elara", "curandeira": "Elara",
    "sylvara": "Sylvara", "druida": "Sylvara",
    "bjorn": "Bjorn", "ancião": "Bjorn", "anciao": "Bjorn",
    "ramses": "Ramses", "arqueólogo": "Ramses", "arqueologo": "Ramses",
    "spectra": "Spectra", "bibliotecária": "Spectra", "bibliotecaria": "Spectra",
    "imperador": "Imperador Astral", "astral": "Imperador Astral",
    "brynn": "Mercador Brynn", "mercador": "Mercador Brynn",
    "capitão": "Capitão Aldric", "capitao": "Capitão Aldric", "aldric": "Capitão Aldric",
}

# Dicionário de canais de mundo próprio: {user_id: channel_id}
MUNDO_PROPRIO_CHANNELS = {}

# ================= HANDLER: CRIAR MUNDO PRÓPRIO + ADICIONAR JOGADOR =================
@bot.listen("on_message")
async def handle_mundo_proprio(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    # ─── CRIAR MUNDO PRÓPRIO ────────────────────────────────────────────
    # Pode ser usado em qualquer canal do servidor
    if content in ["criar mundo proprio", "criar mundo próprio", "criar meu mundo", "criar meu mundo proprio", "criar meu mundo próprio"]:
        if not message.guild:
            await message.channel.send("❌ Este comando só funciona em servidores!")
            return

        player = get_player(uid)
        if not player:
            await message.channel.send(f"❌ {message.author.mention} Crie seu personagem primeiro com `começar`!")
            return

        # Verificar se já tem um mundo próprio ativo
        if uid in MUNDO_PROPRIO_CHANNELS:
            ch = message.guild.get_channel(MUNDO_PROPRIO_CHANNELS[uid])
            if ch:
                await message.channel.send(f"🌍 {message.author.mention} Você já tem um mundo próprio: {ch.mention}!")
                return
            else:
                # Canal foi deletado, limpar do dicionário
                del MUNDO_PROPRIO_CHANNELS[uid]

        # Categoria: ╭━━━━━✦Monstrinho (ID: 1471273874204397578)
        CATEGORIA_ID = 1471273874204397578
        categoria = message.guild.get_channel(CATEGORIA_ID)

        # Nome do canal baseado no jogador (limpar caracteres especiais)
        import re as _re
        nome_limpo = _re.sub(r'[^a-z0-9\-]', '', message.author.display_name.lower().replace(' ', '-'))
        if not nome_limpo:
            nome_limpo = str(message.author.id)
        nome_canal = f"mundo-{nome_limpo}"[:100]

        # Permissões: todos podem ver, só criador e bot podem escrever
        overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=False, view_channel=True
            ),
            message.author: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, view_channel=True,
                embed_links=True, attach_files=True
            ),
            message.guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, view_channel=True,
                embed_links=True, manage_messages=True
            ),
        }

        try:
            if categoria:
                novo_canal = await message.guild.create_text_channel(
                    name=nome_canal,
                    category=categoria,
                    overwrites=overwrites,
                    topic=f"🌍 Mundo próprio de {message.author.display_name} | Use 'adicionar jogador @user' para convidar!"
                )
            else:
                # Se a categoria não existir, cria sem categoria
                novo_canal = await message.guild.create_text_channel(
                    name=nome_canal,
                    overwrites=overwrites,
                    topic=f"🌍 Mundo próprio de {message.author.display_name} | Use 'adicionar jogador @user' para convidar!"
                )

            MUNDO_PROPRIO_CHANNELS[uid] = novo_canal.id

            embed = discord.Embed(
                title="🌍 SEU MUNDO FOI CRIADO!",
                description=(
                    f"{message.author.mention} **Bem-vindo ao seu mundo próprio!**\n\n"
                    f"*'Um novo reino surge do nada, moldado pela sua vontade...'*\n\n"
                    f"Aqui é o seu domínio. Apenas você pode agir aqui — "
                    f"mas outros podem observar sua jornada.\n\n"
                    f"Use `adicionar jogador @usuario` para convidar alguém para explorar junto!"
                ),
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🎮 Comandos disponíveis",
                value="Todos os comandos do bot funcionam aqui!\nUse `adicionar jogador @user` para permitir que alguém jogue junto.",
                inline=False
            )
            embed.set_footer(text=f"Canal criado por {message.author.display_name}")
            await novo_canal.send(embed=embed)
            await message.channel.send(f"✅ {message.author.mention} Seu mundo foi criado: {novo_canal.mention}!")
        except discord.Forbidden:
            await message.channel.send(
                f"❌ {message.author.mention} O bot não tem permissão para criar canais!\n"
                f"Um administrador precisa dar ao bot a permissão **Gerenciar Canais**."
            )
        except Exception as e:
            await message.channel.send(f"❌ Erro ao criar o mundo: `{e}`")
        return

    # ─── ADICIONAR JOGADOR AO MUNDO PRÓPRIO ──────────────────────────────
    if content.startswith("adicionar jogador") and message.mentions:
        # Verificar se o canal atual é um mundo próprio do autor
        canal_dono = None
        for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
            if ch_id == message.channel.id and owner_id == uid:
                canal_dono = uid
                break

        if not canal_dono:
            # Não responder se não for o dono do canal
            return

        for target in message.mentions:
            if target.bot:
                continue
            try:
                await message.channel.set_permissions(
                    target,
                    read_messages=True,
                    send_messages=True
                )
                embed = discord.Embed(
                    title="🤝 Jogador Adicionado!",
                    description=(
                        f"{target.mention} **foi convidado para explorar este mundo!**\n\n"
                        f"*'Um novo aventureiro cruza as fronteiras do reino...'*\n\n"
                        f"Você agora pode usar todos os comandos aqui!"
                    ),
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"❌ Erro ao adicionar {target.display_name}: {e}")
        return


# ================= HANDLER: FORJAR ARMAS COM SISTEMA DE FUSÃO =================
@bot.listen("on_message")
async def handle_forjar_fusao(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    # Verificar canal (mundo proprio ou canal principal)
    canal_valido = (message.channel.name == CANAL_BETA)
    if not canal_valido:
        for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
            if ch_id == message.channel.id:
                canal_valido = True
                break
    if not canal_valido:
        return

    if content not in ["forjar armas", "forjar arma", "fusão de itens", "fusao de itens", "fundir itens"]:
        return

    player = get_player(uid)
    if not player:
        await message.channel.send("❌ Crie seu personagem primeiro!")
        return

    if player.get("job") != "Ferreiro":
        await message.channel.send(
            "⚒️ **Forjar com fusão é exclusivo do Ferreiro!**\n"
            "Use `procurar emprego` e escolha a profissão **Ferreiro** para desbloquear esta habilidade."
        )
        return

    # Sequência de raridades para fusão
    RARITY_CHAIN = ["Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico", "Ancestral", "Divino", "Primordial"]
    RARITY_NEXT = {RARITY_CHAIN[i]: RARITY_CHAIN[i+1] for i in range(len(RARITY_CHAIN)-1)}

    # Contar itens no inventário por raridade
    inventory = player.get("inventory", [])
    rarity_counts = {}
    item_by_rarity = {}

    # Verificar armas e armaduras equipadas e no inventário
    all_items_data = {}
    for world_data in WORLDS.values():
        for item_list_key in ["items"]:
            for item in world_data.get(item_list_key, []):
                all_items_data[item["name"]] = item

    # Contar itens do inventário por raridade
    for item_name in inventory:
        for world_data in WORLDS.values():
            for item in world_data.get("items", []):
                if item["name"] == item_name:
                    r = item.get("rarity", "Comum")
                    rarity_counts[r] = rarity_counts.get(r, 0) + 1
                    if r not in item_by_rarity:
                        item_by_rarity[r] = []
                    item_by_rarity[r].append(item_name)
                    break

    # Mostrar painel de fusão
    embed = discord.Embed(
        title="⚒️ FORJA — Sistema de Fusão",
        description=(
            "*'A forja geme com calor sobrenatural. Cinco itens fundidos como um só...'*\n\n"
            "**Para fundir:** Use `fundir [raridade]` com mínimo de **5 itens** da mesma raridade.\n"
            "Ex: `fundir lendário`, `fundir mítico`\n\n"
            "**Chances de fusão:**\n"
            "✅ **60%** — Item da raridade **superior** gerado!\n"
            "⚠️ **25%** — Item da **mesma raridade** (reduzido)\n"
            "💀 **15%** — Todos os itens **destruídos** na fusão"
        ),
        color=discord.Color.orange()
    )

    if rarity_counts:
        inv_text = ""
        for r in RARITY_CHAIN:
            if r in rarity_counts:
                count = rarity_counts[r]
                emoji = RARITIES.get(r, {}).get("emoji", "⚪")
                next_r = RARITY_NEXT.get(r, "—")
                fusible = "✅ Pode fundir!" if count >= 5 else f"❌ Faltam {5-count} para fundir"
                inv_text += f"{emoji} **{r}**: `{count}` itens → {fusible}\n"
        embed.add_field(name="📦 Seus Itens por Raridade", value=inv_text or "_Nenhum_", inline=False)
    else:
        embed.add_field(name="📦 Inventário", value="_Você não tem itens suficientes para fundir!_", inline=False)

    embed.set_footer(text="Use 'fundir [raridade]' para iniciar a fusão | Ex: 'fundir lendário'")
    await message.channel.send(embed=embed)


@bot.listen("on_message")
async def handle_fundir_raridade(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    canal_valido = (message.channel.name == CANAL_BETA)
    if not canal_valido:
        for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
            if ch_id == message.channel.id:
                canal_valido = True
                break
    if not canal_valido:
        return

    if not content.startswith("fundir "):
        return

    rarity_input = content.replace("fundir ", "").strip().capitalize()
    # Normalizar
    RARITY_ALIASES = {
        "Comum": "Comum", "Incomum": "Incomum", "Raro": "Raro", "Epico": "Épico", "Épico": "Épico",
        "Lendario": "Lendário", "Lendário": "Lendário", "Mitico": "Mítico", "Mítico": "Mítico",
        "Ancestral": "Ancestral", "Divino": "Divino", "Primordial": "Primordial"
    }
    rarity = RARITY_ALIASES.get(rarity_input)
    if not rarity:
        await message.channel.send(f"❌ Raridade inválida: **{rarity_input}**\nRaridades válidas: Comum, Incomum, Raro, Épico, Lendário, Mítico, Ancestral, Divino, Primordial")
        return

    player = get_player(uid)
    if not player:
        return

    if player.get("job") != "Ferreiro":
        await message.channel.send("⚒️ Apenas **Ferreiros** podem fundir itens!")
        return

    # Sequência de raridades
    RARITY_CHAIN = ["Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico", "Ancestral", "Divino", "Primordial"]
    RARITY_NEXT = {RARITY_CHAIN[i]: RARITY_CHAIN[i+1] for i in range(len(RARITY_CHAIN)-1)}

    # Coletar itens do inventário com a raridade especificada
    inventory = player.get("inventory", [])
    matching_items = []

    for item_name in inventory:
        for world_data in WORLDS.values():
            for item in world_data.get("items", []):
                if item["name"] == item_name and item.get("rarity", "Comum") == rarity:
                    matching_items.append(item_name)
                    break

    if len(matching_items) < 5:
        await message.channel.send(
            f"❌ Você precisa de pelo menos **5 itens {rarity}** para fundir!\n"
            f"Você tem: **{len(matching_items)}** itens {RARITIES.get(rarity,{}).get('emoji','')} {rarity}"
        )
        return

    # Remover 5 itens do inventário
    removed = 0
    new_inventory = []
    for item_name in inventory:
        found_in_matching = item_name in matching_items and removed < 5
        if found_in_matching and removed < 5:
            removed += 1
            matching_items.remove(item_name)
        else:
            new_inventory.append(item_name)

    # Rolar resultado
    roll = random.random()
    next_rarity = RARITY_NEXT.get(rarity)

    if roll < 0.60 and next_rarity:
        # Sucesso! Gerar item de raridade superior
        resultado = "sucesso"
        # Encontrar um item da próxima raridade
        possible_items = []
        for world_data in WORLDS.values():
            for item in world_data.get("items", []):
                if item.get("rarity") == next_rarity:
                    possible_items.append(item["name"])

        if possible_items:
            new_item = random.choice(possible_items)
        else:
            # Fallback: criar um item genérico
            new_item = f"Fragmento {next_rarity}"
        new_inventory.append(new_item)

        embed = discord.Embed(
            title="✨ FUSÃO BEM-SUCEDIDA!",
            description=f"*'As chamas da forja rugem! Os cinco itens se fundem em um só!'*",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="⚒️ Resultado",
            value=f"5× {RARITIES.get(rarity,{}).get('emoji','')} **{rarity}** → {RARITIES.get(next_rarity,{}).get('emoji','')} **{new_item}** ({next_rarity})",
            inline=False
        )
        embed.add_field(name="🎉 Parabéns!", value=f"Item **{next_rarity}** adicionado ao inventário!", inline=False)

    elif roll < 0.85:
        # Item de mesma raridade (menor)
        resultado = "parcial"
        possible_items = []
        for world_data in WORLDS.values():
            for item in world_data.get("items", []):
                if item.get("rarity") == rarity:
                    possible_items.append(item["name"])
        if possible_items:
            new_item = random.choice(possible_items)
            new_inventory.append(new_item)
        else:
            new_item = f"Fragmento {rarity}"
            new_inventory.append(new_item)

        embed = discord.Embed(
            title="⚠️ FUSÃO PARCIAL",
            description=f"*'A forja tremeu. Os itens se fundiram, mas algo foi perdido no processo...'*",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="⚒️ Resultado",
            value=f"5× {RARITIES.get(rarity,{}).get('emoji','')} **{rarity}** → {RARITIES.get(rarity,{}).get('emoji','')} **{new_item}** ({rarity} — qualidade reduzida)",
            inline=False
        )
        embed.add_field(name="💡 Dica", value="Tente novamente! As chances de sucesso total são **60%**.", inline=False)

    else:
        # Falha — todos destruídos
        resultado = "falha"
        embed = discord.Embed(
            title="💀 FUSÃO FRACASSADA!",
            description=f"*'Uma explosão de energia. Os itens se dissolvem em pó dourado... e somem.'*",
            color=discord.Color.red()
        )
        embed.add_field(
            name="💥 Resultado",
            value=f"5× {RARITIES.get(rarity,{}).get('emoji','')} **{rarity}** → ❌ **Todos destruídos!**",
            inline=False
        )
        embed.add_field(name="😔 Azar...", value="Os itens foram perdidos na fusão. Colete mais e tente novamente!", inline=False)

    player["inventory"] = new_inventory
    save_player_db(uid, player)

    embed.set_footer(text=f"Ferreiro {message.author.display_name} | Fusão de itens {rarity}")
    await message.channel.send(embed=embed)


# ================= HANDLER: DIALOGAR COM NPC =================
@bot.listen("on_message")
async def handle_dialogar_npc(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    canal_valido = (message.channel.name == CANAL_BETA)
    if not canal_valido:
        for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
            if ch_id == message.channel.id:
                canal_valido = True
                break
    if not canal_valido:
        return

    if not (content.startswith("dialogar com npc") or content.startswith("falar com npc") or
            content.startswith("conversar com npc") or content.startswith("dialogar npc")):
        return

    # Extrair nome do NPC
    for prefix in ["dialogar com npc ", "falar com npc ", "conversar com npc ", "dialogar npc "]:
        if content.startswith(prefix):
            npc_name_input = content.replace(prefix, "").strip()
            break
    else:
        npc_name_input = ""

    if not npc_name_input:
        # Mostrar lista de NPCs disponíveis
        embed = discord.Embed(
            title="🗣️ Dialogar com NPC",
            description=(
                "*'Os NPCs do reino têm muito a contar...'*\n\n"
                "Use: `dialogar com npc [nome]`\n\n"
                "**NPCs disponíveis:**\n"
                "• `dialogar com npc theron` — Aldeão Theron\n"
                "• `dialogar com npc elara` — Curandeira Elara\n"
                "• `dialogar com npc sylvara` — Druida Sylvara\n"
                "• `dialogar com npc bjorn` — Ancião Bjorn\n"
                "• `dialogar com npc ramses` — Arqueólogo Ramses\n"
                "• `dialogar com npc spectra` — Bibliotecária Spectra\n"
                "• `dialogar com npc imperador` — Imperador Astral\n"
                "• ...e outros NPCs dos reinos!"
            ),
            color=discord.Color.blurple()
        )
        await message.channel.send(embed=embed)
        return

    player = get_player(uid)
    if not player:
        await message.channel.send("❌ Crie seu personagem primeiro com `começar`!")
        return

    # Encontrar NPC
    npc_key = NPC_NAME_MAP.get(npc_name_input.lower())

    if not npc_key or npc_key not in NPC_DIALOGUES_EXTENDED:
        # Tentar encontrar em CITY_NPCS
        world_key = max(k for k in player.get("worlds", [1]))
        city_data = CITY_NPCS.get(world_key, {})
        npcs_list = city_data.get("npcs", [])
        found_npc = None
        for npc in npcs_list:
            if npc_name_input.lower() in npc["name"].lower():
                found_npc = npc
                break

        if found_npc:
            dialogue = random.choice(found_npc["dialogues"])
            embed = discord.Embed(
                title=f"{found_npc['emoji']} {found_npc['name']} — _{found_npc['role']}_",
                description=f'*"{dialogue}"*',
                color=discord.Color.purple()
            )
            embed.set_footer(text="Use 'dialogar com npc [nome]' novamente para ouvir mais!")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(
                f"❓ NPC **{npc_name_input}** não encontrado!\n"
                f"Use `dialogar com npc` para ver a lista de NPCs disponíveis."
            )
        return

    npc_data = NPC_DIALOGUES_EXTENDED[npc_key]

    # Rolar tipo de diálogo: lore, segredo ou quest
    roll = random.random()
    if roll < 0.50 and npc_data.get("lore"):
        # Lore
        dialogue = random.choice(npc_data["lore"])
        embed = discord.Embed(
            title=f"{npc_data['emoji']} {npc_data['full_name']}",
            description=f'*"{dialogue}"*',
            color=discord.Color.purple()
        )
        embed.set_footer(text="Continue dialogando para descobrir mais histórias, segredos e quests ocultas!")

    elif roll < 0.75 and npc_data.get("secrets"):
        # Segredo!
        secret = random.choice(npc_data["secrets"])
        embed = discord.Embed(
            title=f"🔮 {npc_data['emoji']} {npc_data['full_name']} — *sussurra um segredo...*",
            description=f'*"{secret}"*',
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="🤫 Segredo Revelado!", value="Guarde bem esta informação — ela pode ser valiosa.", inline=False)
        embed.set_footer(text="Segredos podem levar a quests ocultas e recompensas raras!")

    elif npc_data.get("hidden_quests"):
        # Quest oculta!
        quest = random.choice(npc_data["hidden_quests"])
        embed = discord.Embed(
            title=f"⭐ {npc_data['emoji']} {npc_data['full_name']} — *revela uma missão oculta!*",
            description=f'*"Tenho algo importante para te pedir... mas não é uma missão comum."*\n\n**{quest["name"]}**\n{quest["description"]}',
            color=discord.Color.gold()
        )
        embed.add_field(name="📖 Lore", value=quest["lore"], inline=False)
        rewards = f"⭐ **{quest['reward_xp']} XP** | 💰 **{quest['reward_coins']} coins**"
        if quest.get("reward_item"):
            rewards += f" | 🎁 **{quest['reward_item']}**"
        embed.add_field(name="🏆 Recompensas", value=rewards, inline=False)
        embed.add_field(name="⚔️ Dificuldade", value=quest["difficulty"], inline=True)
        embed.set_footer(text="Quest oculta desbloqueada via diálogo com NPC! Use 'aceitar quest [nome]' para iniciar.")
        # Oferecer aceitar
        view = QuestAcceptButton(uid, quest)
        await message.channel.send(embed=embed, view=view)
        return
    else:
        # Fallback: lore
        if npc_data.get("lore"):
            dialogue = random.choice(npc_data["lore"])
        else:
            dialogue = "..."
        embed = discord.Embed(
            title=f"{npc_data['emoji']} {npc_data['full_name']}",
            description=f'*"{dialogue}"*',
            color=discord.Color.purple()
        )
        embed.set_footer(text="Continue dialogando para descobrir mais!")

    await message.channel.send(embed=embed)


# ================= HANDLER: FORMA BESTIAL E QUARTA FORMA (PETS) =================
@bot.listen("on_message")
async def handle_formas_especiais_pet(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    uid = str(message.author.id)

    canal_valido = (message.channel.name == CANAL_BETA)
    if not canal_valido:
        for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
            if ch_id == message.channel.id:
                canal_valido = True
                break
    if not canal_valido:
        return

    # ─── QUARTA FORMA (exclusiva pets comuns) ─────────────────────────
    if content in ["quarta forma pet", "forma especial pet", "quarta forma", "evoluir quarta forma"]:
        player = get_player(uid)
        if not player or not player.get("pet"):
            await message.channel.send("❌ Você não tem um pet ativo!")
            return

        pet_name = player["pet"]
        if isinstance(pet_name, dict):
            pet_name = pet_name.get("name", "")

        # Verificar se o pet é Comum
        current_rarity = None
        for world_pets in PETS.values():
            for p in world_pets:
                if p["name"] == pet_name:
                    current_rarity = p["rarity"]
                    break

        # Verificar nas evoluções
        if not current_rarity:
            for evo in PET_EVOLUTIONS.values():
                if evo.get("next") == pet_name:
                    current_rarity = evo["next_data"].get("rarity")

        if current_rarity != "Comum":
            await message.channel.send(
                f"❌ A **Quarta Forma** é exclusiva de pets de raridade **Comum**!\n"
                f"Seu pet **{pet_name}** é de raridade **{current_rarity or '?'}**.\n\n"
                f"*Pets de raridade Lendário ou superior podem ter Forma Bestial (use `forma bestial pet` no nível 80)!*"
            )
            return

        # Verificar se tem quarta forma
        fourth_form_data = COMMON_PET_FOURTH_FORMS.get(pet_name)
        if not fourth_form_data:
            # Qualquer pet comum sem quarta forma registrada ganha uma genérica
            fourth_form_data = {
                "level_required": 3,
                "next": f"{pet_name} Desperto",
                "next_data": {
                    "name": f"{pet_name} Desperto",
                    "emoji": "✨",
                    "rarity": "Comum",
                    "bonus_hp": 50, "bonus_atk": 20,
                    "special": True, "form": "quarta_forma",
                    "desc": f"A quarta forma exclusiva do {pet_name}. Uma forma única que nenhum pet raro possui!"
                }
            }

        if player["level"] < fourth_form_data["level_required"]:
            await message.channel.send(
                f"❌ Seu pet precisa que você seja **Nível {fourth_form_data['level_required']}** para atingir a Quarta Forma!\n"
                f"Nível atual: **{player['level']}**"
            )
            return

        next_pet = fourth_form_data["next_data"]
        player["pet"] = next_pet["name"]
        save_player_db(uid, player)

        embed = discord.Embed(
            title="✨ QUARTA FORMA DESBLOQUEADA! ✨",
            description=(
                f"*'Uma aura dourada envolve {pet_name}... mas algo diferente acontece desta vez!'*\n\n"
                f"🌟 **{pet_name}** → {next_pet['emoji']} **{next_pet['name']}** — *Quarta Forma Exclusiva!*\n\n"
                f"*'{next_pet['desc']}'*"
            ),
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.add_field(name="💪 ATK Bônus", value=f"+{next_pet['bonus_atk']}", inline=True)
        embed.add_field(name="❤️ HP Bônus", value=f"+{next_pet['bonus_hp']}", inline=True)
        embed.add_field(name="⚪ Raridade", value="Comum — Quarta Forma Exclusiva!", inline=True)
        embed.add_field(
            name="🔮 Exclusividade",
            value="*Esta forma NUNCA poderá ser alcançada por pets raros ou superiores. É o poder secreto dos Comuns!*",
            inline=False
        )
        embed.set_footer(text="Pets comuns têm formas que nenhum lendário jamais alcançará...")
        await message.channel.send(embed=embed)
        return

    # ─── FORMA BESTIAL (pets de nível alto, nível 80 do jogador) ──────
    if content in ["forma bestial pet", "despertar bestial", "forma bestial", "bestial pet"]:
        player = get_player(uid)
        if not player or not player.get("pet"):
            await message.channel.send("❌ Você não tem um pet ativo!")
            return

        if player["level"] < 80:
            await message.channel.send(
                f"🔒 **Forma Bestial** requer que você seja **Nível 80**!\n"
                f"Nível atual: **{player['level']}**\n\n"
                f"*'O despertar bestial exige um mestre, não um aprendiz...'*"
            )
            return

        pet_name = player["pet"]
        if isinstance(pet_name, dict):
            pet_name = pet_name.get("name", "")

        bestial_data = BESTIAL_FORMS.get(pet_name)
        if not bestial_data:
            await message.channel.send(
                f"❌ **{pet_name}** não possui Forma Bestial registrada.\n\n"
                f"Pets elegíveis para Forma Bestial são de raridade **Lendário** ou superior.\n"
                f"Use `ver fazenda` para verificar seus pets."
            )
            return

        next_pet = bestial_data
        player["pet"] = next_pet["name"]
        save_player_db(uid, player)

        embed = discord.Embed(
            title="🔥 FORMA BESTIAL DESPERTADA! 🔥",
            description=(
                f"*'O poder ancestral surge do mais fundo do ser... A Forma Bestial foi liberada!'*\n\n"
                f"💀 **{pet_name}** → {next_pet['emoji']} **{next_pet['name']}** — *Forma Bestial!*\n\n"
                f"*'{next_pet['desc']}'*"
            ),
            color=discord.Color.dark_red()
        )
        embed.add_field(name="💪 ATK Bônus", value=f"+{next_pet['bonus_atk']}", inline=True)
        embed.add_field(name="❤️ HP Bônus", value=f"+{next_pet['bonus_hp']}", inline=True)
        embed.add_field(name=f"{RARITIES.get(next_pet['rarity'],{}).get('emoji','✨')} Raridade", value=next_pet["rarity"], inline=True)
        embed.add_field(
            name="⚠️ Atenção",
            value="*A Forma Bestial é permanente. Uma vez despertada, não pode ser revertida.*",
            inline=False
        )
        embed.set_footer(text="Apenas mestres de nível 80+ podem despertar a Forma Bestial.")
        await message.channel.send(embed=embed)
        return

    # Verificar canal mundo próprio para comandos do bot principal
    if not canal_valido:
        return

    if content in ["ajuda formas pet", "formas pet", "formas especiais pet"]:
        embed = discord.Embed(
            title="🐾 Formas Especiais de Pets",
            description="Sistema de transformações especiais para seus companheiros!",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="✨ Quarta Forma (Pets Comuns)",
            value=(
                "Exclusiva para pets de raridade **Comum**!\n"
                "Use: `quarta forma pet`\n"
                "Requer: Nível 3+ do jogador\n"
                "Uma forma que nenhum pet raro jamais poderá alcançar."
            ),
            inline=False
        )
        embed.add_field(
            name="🔥 Forma Bestial (Pets Lendário+)",
            value=(
                "Exclusiva para pets de raridade **Lendário** ou superior!\n"
                "Use: `forma bestial pet`\n"
                "Requer: **Nível 80** do jogador\n"
                "Desperta o poder ancestral adormecido no pet."
            ),
            inline=False
        )
        await message.channel.send(embed=embed)


# ================= COMANDO: MONTARIA =================
@bot.listen("on_message")
async def handle_montaria(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return

    content = message.content.lower().strip()
    uid = str(message.author.id)

    # ---- montar [pet] ----
    if content.startswith("montar "):
        pet_name_input = message.content.strip()[7:].strip()
        player = get_player(uid)
        if not player:
            await message.channel.send("❌ Crie seu personagem primeiro com `começar`!")
            return

        # Procura o pet no inventário de pets do jogador
        pets_list = player.get("pets_list", [])
        found_pet = None
        for p in pets_list:
            pn = p.get("name", "") if isinstance(p, dict) else str(p)
            if pet_name_input.lower() in pn.lower():
                found_pet = pn
                break

        # Também verifica o pet principal ativo
        if not found_pet:
            main_pet = player.get("pet")
            if main_pet:
                mpn = main_pet if isinstance(main_pet, str) else main_pet.get("name", "")
                if pet_name_input.lower() in mpn.lower():
                    found_pet = mpn

        if not found_pet:
            await message.channel.send(
                f"❌ Pet **{pet_name_input}** não encontrado na sua fazenda/pet ativo!\n"
                f"Use `ver fazenda` para listar seus pets."
            )
            return

        mount_data = get_pet_mount_data(found_pet)
        if not mount_data:
            await message.channel.send(
                f"❌ **{found_pet}** não pode ser usado como montaria!\n\n"
                f"Pets elegíveis para montaria incluem: Lobos, Dragões, Grifos, Unicórnios, Cavalos, e criaturas grandes de raridade **Incomum+**.\n"
                f"Verifique `lista montarias` para ver todos os pets elegíveis."
            )
            return

        player["mount"] = found_pet
        save_player_db(uid, player)

        embed = discord.Embed(
            title="🐎 MONTARIA EQUIPADA!",
            description=f"*'Você sobe em **{found_pet}** e sente o poder da criatura sob você!'*",
            color=discord.Color.green()
        )
        embed.add_field(name="🐎 Montaria", value=f"**{found_pet}**", inline=True)
        embed.add_field(name="🛡️ DEF Bônus", value=f"`+{mount_data['mount_bonus_def']}`", inline=True)
        embed.add_field(name="💨 Velocidade", value=f"`+{mount_data['mount_bonus_spd']}`", inline=True)
        embed.add_field(
            name="✅ Efeito Ativo",
            value="*Sua montaria te acompanha automaticamente em batalhas de boss, adicionando bônus de DEF!*",
            inline=False
        )
        await message.channel.send(embed=embed)
        return

    # ---- desmontar ----
    if content in ["desmontar", "remover montaria", "tirar montaria"]:
        player = get_player(uid)
        if not player:
            return
        current_mount = player.get("mount")
        if not current_mount:
            await message.channel.send("❌ Você não tem nenhuma montaria ativa!")
            return
        player["mount"] = None
        save_player_db(uid, player)
        await message.channel.send(f"🐎 Montaria **{current_mount}** removida. *Você desce do seu companheiro.*")
        return

    # ---- ver montaria ----
    if content in ["ver montaria", "minha montaria", "montaria"]:
        player = get_player(uid)
        if not player:
            return
        current_mount = player.get("mount")
        if not current_mount:
            await message.channel.send(
                f"🐎 Você não tem montaria ativa.\n\n"
                f"Para montar em um pet: `montar [nome do pet]`\n"
                f"Veja pets elegíveis: `lista montarias`"
            )
            return
        mount_data = get_pet_mount_data(current_mount)
        if not mount_data:
            await message.channel.send(f"🐎 Montaria ativa: **{current_mount}** *(dados não encontrados)*")
            return
        embed = discord.Embed(
            title="🐎 Sua Montaria Atual",
            color=discord.Color.blue()
        )
        embed.add_field(name="🐎 Montaria", value=f"**{current_mount}**", inline=True)
        embed.add_field(name="🛡️ DEF Bônus", value=f"`+{mount_data['mount_bonus_def']}`", inline=True)
        embed.add_field(name="💨 Velocidade", value=f"`+{mount_data['mount_bonus_spd']}`", inline=True)
        await message.channel.send(embed=embed)
        return

    # ---- lista montarias ----
    if content in ["lista montarias", "pets montaria", "montarias disponíveis", "montarias disponiveis"]:
        embed = discord.Embed(
            title="🐎 Pets que Podem Virar Montaria",
            description="Esses pets podem ser equipados como montaria com `montar [nome]`!\nMontarias adicionam bônus de DEF em batalhas de boss.",
            color=discord.Color.gold()
        )
        # Listar pets extras com montaria
        lines = []
        for world, pets in PETS_EXTRA.items():
            for p in pets:
                if p.get("can_mount"):
                    lines.append(f"{p['emoji']} **{p['name']}** [{p['rarity']}] — DEF +{p.get('mount_bonus_def',0)} | Spd +{p.get('mount_bonus_spd',0)}")
        # Listar pets originais com montaria
        for pname, mdata in EXISTING_PETS_MOUNT.items():
            lines.append(f"🐾 **{pname}** — DEF +{mdata.get('mount_bonus_def',0)} | Spd +{mdata.get('mount_bonus_spd',0)}")

        # Dividir em campos para não ultrapassar limite
        chunks = [lines[i:i+10] for i in range(0, len(lines), 10)]
        for i, chunk in enumerate(chunks):
            embed.add_field(name=f"Montarias {i+1}", value="\n".join(chunk), inline=False)
        embed.set_footer(text="Use: montar [nome do pet] | desmontar | ver montaria")
        await message.channel.send(embed=embed)
        return


# ================= COMANDO: MUNDOS PRÓPRIOS — BOT RESPONDE NELES TAMBÉM =================
# Garantir que o bot responde a todos os comandos nos canais de mundo próprio
@bot.listen("on_message")
async def handle_mundo_proprio_canal(message):
    """Permite que o bot responda nos canais de mundo próprio como se fosse o canal principal"""
    if message.author.bot:
        return
    # Verificar se o canal é um mundo próprio
    is_mundo_proprio = False
    for owner_id, ch_id in MUNDO_PROPRIO_CHANNELS.items():
        if ch_id == message.channel.id:
            is_mundo_proprio = True
            break
    if not is_mundo_proprio:
        return
    # O canal de mundo próprio deve funcionar como o canal beta
    # O CANAL_BETA é verificado em outros handlers — aqui garantimos que
    # os handlers principais também respondem neste canal
    # Isso é feito verificando o nome do canal nos handlers, mas como usamos
    # channel.name == CANAL_BETA, precisamos de uma abordagem diferente.
    # Os handlers de mundo próprio já verificam MUNDO_PROPRIO_CHANNELS,
    # então os principais comandos funcionam via os @bot.listen já existentes
    # que checam message.channel.name == CANAL_BETA.
    # Para garantir compatibilidade total, temporariamente alteramos a verificação
    # adicionando suporte a canais de mundo próprio nos handlers de mundo próprio acima.
    pass


# ================= HANDLER: CONFRONTAR BOSS DO LEVEL X =================
@bot.listen("on_message")
async def handle_confrontar_boss_level(message):
    if message.author.bot:
        return
    if message.channel.name != CANAL_BETA and message.channel.id not in MUNDO_PROPRIO_CHANNELS.values():
        return

    content = message.content.lower().strip()
    uid = str(message.author.id)

    # Aceita: "confrontar boss do level 9", "confrontar boss level 9"
    import re
    m = re.match(r"confrontar boss (?:do )?level (\d+)$", content)
    if not m:
        return

    target_level = int(m.group(1))
    boss_gate_levels = [9, 19, 29, 39, 49, 59, 69, 79, 89, 99,
                        109, 119, 129, 139, 149, 159, 169, 179, 189, 199]

    if target_level not in boss_gate_levels:
        niveis_str = ", ".join(str(x) for x in boss_gate_levels[:10]) + "..."
        await message.channel.send(
            f"❌ **Level {target_level}** não tem boss de nível!\n\n"
            f"Bosses de nível existem nos níveis: **{niveis_str}**\n"
            f"Exemplo: `confrontar boss do level 9`, `confrontar boss do level 19`"
        )
        return

    player = get_player(uid)
    if not player:
        await message.channel.send("❌ Crie seu personagem primeiro com `começar`!")
        return

    player_level = player.get("level", 1)
    if player_level < target_level:
        await message.channel.send(
            f"🔒 **Boss do Level {target_level}** ainda bloqueado!\n\n"
            f"Você está no nível **{player_level}**. Alcance o nível **{target_level}** para poder confrontar este boss.\n\n"
            f"*'O guardião desta passagem sequer nota sua presença... ainda.'*"
        )
        return

    boss_data = get_level_boss(target_level)
    if not boss_data:
        await message.channel.send(f"❌ Não foi possível encontrar o boss do level {target_level}.")
        return

    already_defeated = boss_data["name"] in player.get("bosses", [])

    # Salvar como pending boss para os botões funcionarem
    effects = player.get("active_effects", {})
    effects["pending_boss"] = boss_data
    player["active_effects"] = effects
    save_player_db(uid, player)

    boss_level_to_world = {
        9:1, 19:10, 29:20, 39:30, 49:40, 59:50, 69:60, 79:70, 89:80, 99:90,
        109:100, 119:110, 129:120, 139:130, 149:140, 159:150, 169:160, 179:170, 189:180, 199:190
    }
    world_key = boss_level_to_world.get(target_level, 1)
    world_data = WORLDS.get(world_key, {})
    world_name = world_data.get("name", f"Reino {target_level}")
    world_emoji = world_data.get("emoji", "🌍")
    boss_nm = boss_data["name"]

    if already_defeated:
        embed = discord.Embed(
            title=f"⚔️ REVANCHE — BOSS DO LEVEL {target_level}!",
            description=(
                f"*'As névoas do tempo se desfazem... O guardião ressurge das sombras para um novo duelo!'*\n\n"
                f"👹 **{boss_nm}** retorna para uma batalha épica!\n\n"
                f"{world_emoji} **{world_name}** — Este foi o guardião que desbloqueou este reino para você.\n\n"
                f"*A lenda diz que reviver grandes batalhas fortalece a alma do guerreiro...*"
            ),
            color=discord.Color.from_rgb(150, 0, 200)
        )
    else:
        embed = discord.Embed(
            title=f"🚨 BOSS DE NÍVEL {target_level} — PASSAGEM BLOQUEADA!",
            description=(
                f"*'O ar fica pesado... Uma sombra colossal bloqueia seu caminho!'*\n\n"
                f"👹 **{boss_nm}** surge diante de você!\n\n"
                f"⚠️ **Derrote-o para desbloquear o próximo reino e desbloquear o XP!**"
            ),
            color=discord.Color.dark_red()
        )

    embed.add_field(name="❤️ HP",           value=f"`{boss_data['hp']:,}`",  inline=True)
    embed.add_field(name="⚔️ ATK",          value=f"`{boss_data['atk']}`",   inline=True)
    embed.add_field(name="⭐ XP",           value=f"`{boss_data['xp']:,}`",  inline=True)
    embed.add_field(name="🎯 Level do Boss", value=f"`{target_level}`",       inline=True)
    if already_defeated:
        embed.add_field(name="🏆 Revanche", value="*Boss já derrotado anteriormente — nova chance de luta!*", inline=False)
    embed.add_field(name="💡 Dica", value="Use os botões abaixo para lutar ou chamar aliados!", inline=False)

    view = BossButton(uid, boss_data["name"])
    await message.channel.send(embed=embed, view=view)


# ================= RUN BOT =================
bot.run(TOKEN)
