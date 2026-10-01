import pymupdf4llm
import pandas as pd

# PDF -> Markdown, página por página
paginas = pymupdf4llm.to_markdown("cartasus.pdf", page_chunks=True)

with open("cartilha.md", "w", encoding="utf-8") as f:
    f.write("\n\n".join(p["text"] for p in paginas))

# Divide em seções usando os títulos (linhas que começam com #)
secoes = []
titulo, pagina_ini, buffer = "Sem título", 1, []

for num, p in enumerate(paginas, start=1):
    for linha in p["text"].splitlines():
        if linha.lstrip().startswith("#"):
            if buffer:
                secoes.append({"titulo": titulo, "pagina": pagina_ini,
                               "texto": "\n".join(buffer).strip()})
            titulo = linha.lstrip("# ").strip()
            pagina_ini = num
            buffer = []
        else:
            buffer.append(linha)

secoes.append({"titulo": titulo, "pagina": pagina_ini,
               "texto": "\n".join(buffer).strip()})

# 3) Tabela para o EDA
df = pd.DataFrame(secoes)
df["n_palavras"] = df["texto"].str.split().str.len()

df.to_csv("cartilha_secoes.csv", index=False)
df.to_json("cartilha_secoes.json", orient="records",
           force_ascii=False, indent=2)
print(df.head())