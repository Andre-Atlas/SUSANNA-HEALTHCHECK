# Componentes, versões e licenças

Inventário em 25/09/2026. Versões observadas neste computador, não versões mínimas
certificadas nem recomendação de atualização. Código de referência: commit
`5348c47` antes da consolidação documental da etapa 8.

| Componente | Versão / identificação | Licença / evidência |
|---|---|---|
| Código Python, HTML, CSS e JavaScript do projeto | Commit de referência acima; sem versão semântica declarada | [MIT no repositório](../LICENSE), copyright 2026 André Acioli |
| Python e biblioteca padrão | Python 3.14.6; requisito declarado 3.10+ | [PSF License 2 e avisos dos componentes incorporados](https://docs.python.org/3/license.html) |
| SQLite usado pelo Python | 3.50.4; extensão FTS5 necessária | [Declaração de domínio público do SQLite](https://sqlite.org/copyright.html) |
| Ollama | Cliente 0.32.5 | [MIT do Ollama](https://github.com/ollama/ollama/blob/main/LICENSE) |
| Modelo `qwen2.5:7b` | Manifesto local `845dbda0ea48…`; catálogo: 7,62 bilhões de parâmetros, Q4_K_M | [Apache 2.0 indicada para esta variante](https://ollama.com/library/qwen2.5:7b) |
| Interface web | JavaScript, HTML e CSS próprios; sem framework ou CDN | Licença do projeto; navegador é software instalado separadamente |
| Base documental | Seis JSONs versionados, com metadados de revisão | [Avisos e pendências das fontes](revisao-fontes.md); não abrangidos automaticamente pela MIT |

O cliente Ollama informou não conseguir conectar a uma instância em execução
durante o inventário; a versão do serviço ativo não foi confirmada. Os arquivos
do modelo existem localmente, mas isso não substitui uma execução de validação.
A instalação mínima 3.10+ não foi testada como matriz de compatibilidade nesta etapa.

Manifesto local SHA-256:
`845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`.
Camada de pesos indicada no manifesto:
`sha256:2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730`.
Foi calculado o hash do manifesto; o arquivo de pesos não foi revalidado por hash.
A tag do modelo pode mudar: registre o identificador após cada atualização.

## Reproduzir o inventário

```bash
python3 --version
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'
ollama --version
ollama list
ollama show qwen2.5:7b --license
git rev-parse HEAD
```

Os comandos `ollama list` e `show` precisam do serviço disponível. O projeto não
instala pacotes pip/npm. `unittest` faz parte do Python; testes de interface usam
JavaScriptCore do macOS e são ignorados em outras plataformas. Navegadores,
sistema operacional e ferramentas de desenvolvimento mantêm suas próprias licenças.

## Créditos e reutilização

O README identifica Guilherme Barros como autor; `LICENSE` identifica André
Acioli no aviso de copyright. Os registros foram preservados. Conferir a relação
de autoria e titularidade antes de editar créditos; nenhum nome foi substituído.
Responsabilidade pela manutenção é registrada separadamente em
[responsabilidades](responsabilidades.md).

Ao redistribuir, mantenha os textos de licença e avisos aplicáveis aos componentes
incluídos. O inventário não relicencia pesos, fontes oficiais ou marcas. As
pendências de reutilização documental continuam em [revisão das fontes](revisao-fontes.md).
Não extrapole a licença do Qwen 7B para todas as variantes do modelo.

## Componentes opcionais da demonstração externa

Waitress 3.0.2 (ZPL 2.1), fixado em `requirements-internet.txt`, e cloudflared
(Apache 2.0), instalado separadamente em `.internet/bin/`. Consulte
[o guia do túnel](internet-demo.md). O modo local continua sem dependências pip.
