from collections import Counter
import crypt
import random

# Charge les textes de référence
def load_txt():
    urls = ["https://www.gutenberg.org/ebooks/13846.txt.utf-8", "https://www.gutenberg.org/ebooks/4650.txt.utf-8"]
    text = ""
    for url in urls:
        part = crypt.load_text_from_web(url)
        if part:
            text += part
    return text

# Génère les symboles triés sur la fréquence de caractères et bigrammes
def sort_syms(text):
    sym_count = Counter(text)
    bi_count = Counter(text[i:i + 2] for i in range(len(text) - 1))
    tri_count = Counter(text[i:i + 3] for i in range(len(text) - 2))

    sym_total = len(sym_count)
    extra = 256 - sym_total
    bigrams = [item for item, _ in bi_count.most_common(extra)]
    trigrams = [item for item, _ in tri_count.most_common(extra // 2)]

    syms = list(sym_count.keys()) + bigrams + trigrams
    return sorted(syms, key=lambda s: sym_count.get(s, 0), reverse=True)

# Calcule la fréquence des symboles sur le texte chiffré
def sym_freq(text, syms):
    return sorted([(sym, text.count(sym) / len(text)) for sym in syms], key=lambda x: x[1], reverse=True)

# Génère la table de traduction initiale
def init_table(sorted_syms, sorted_bytes):
    return {sorted_bytes[i][0]: sorted_syms[i] for i in range(min(len(sorted_bytes), len(sorted_syms)))}

# Déchiffre avec la table de traduction
def dec_table(C, table):
    return ''.join(table.get(C[i:i + 8], '?') for i in range(0, len(C), 8))

# Calcule le score du texte
def sc_txt(text):
    bi_count = Counter(text[i:i + 2] for i in range(len(text) - 1))
    tri_count = Counter(text[i:i + 3] for i in range(len(text) - 2))
    return sum(bi_count.values()) + sum(tri_count.values())

# Ajuste la table de traduction
def refine_table(C, init_table, tries=100):
    bsttab = init_table.copy()
    bstsc = sc_txt(dec_table(C, bsttab))
    for _ in range(tries):
        nw_tabl = bsttab.copy()
        k1, k2 = random.sample(list(nw_tabl.keys()), 2)
        nw_tabl[k1], nw_tabl[k2] = nw_tabl[k2], nw_tabl[k1]
        nwt = dec_table(C, nw_tabl)
        nws = sc_txt(nwt)
        if nws > bstsc:
            bsttab, bstsc = nw_tabl, nws

    return bsttab

# Fonction principale de déchiffrement
def decrypt(C):
    ref_text = load_txt()
    sorted_syms = sort_syms(ref_text)

    byt_b = [C[i:i + 8] for i in range(0, len(C), 8)]
    byt_freq = Counter(byt_b)
    sorted_bytes = sorted(byt_freq.items(), key=lambda x: x[1], reverse=True)

    init_trans_table = init_table(sorted_syms, sorted_bytes)
    refined_table = refine_table(C, init_trans_table)
    return dec_table(C, refined_table)
