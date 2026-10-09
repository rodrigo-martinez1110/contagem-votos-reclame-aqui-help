# Contagem de votos HELP — Prêmio Reclame Aqui

Projeto para contabilizar prints enviados ao grupo do WhatsApp e exibir o placar em um app Streamlit. O OCR roda no computador; o ZIP e as imagens não são enviados a serviços externos. O app lê `ranking_publico.csv`, que é atualizado manualmente depois de conferir o processamento. A página destaca a última atualização, mantém os cards de KPI, exibe a premiação do Top 3, compara os sete primeiros em um gráfico Plotly e permite buscar nomes ou os quatro últimos dígitos na tabela completa. A tabela indica quantos votos faltam para cada pessoa alcançar a colocação imediatamente acima. O layout adapta KPIs, prêmios, gráfico e tabela a telas de celular.

## O que fica público

O repositório público contém o código, instruções e `ranking_publico.csv`. Esse CSV exibe nomes, contagens e os quatro últimos dígitos de celular, conforme definido para o placar. Qualquer pessoa com acesso ao repositório poderá ver esses dados.

O ZIP exportado do WhatsApp, imagens, planilhas detalhadas, `dim_pessoas.csv` (aliases e dados usados no processamento) e `correcoes_votos.csv` ficam apenas na cópia local e são ignorados pelo Git.

## Instalação no Windows

1. Instale Python 3.10 ou mais recente.
2. Instale o Tesseract OCR para Windows. O projeto Tesseract indica instaladores mantidos pela UB Mannheim: <https://github.com/UB-Mannheim/tesseract/wiki>.
3. Inclua os idiomas Portuguese (`por`) e English (`eng`) na instalação.
4. No PowerShell, nesta pasta, rode:

   ```powershell
   python -m pip install -r requirements.txt
   ```

## Abrir o ranking localmente

```powershell
streamlit run app.py
```

O navegador abrirá o placar. O app mostra o total HELP, o líder, os participantes, os quatro últimos dígitos e a data/hora da última atualização.

## Dados locais necessários

Crie `dim_pessoas.csv` ao lado do script com as colunas `Nome no ranking`, `Aliases WhatsApp` e `Celular final 4`. O arquivo contém dados da equipe e não deve ser enviado ao GitHub. Os aliases alternativos são separados por `|`.

Opcionalmente, crie `correcoes_votos.csv` com as colunas `Arquivo` e `Classificação` para correções visuais manuais. Esse arquivo também é local.

Para não publicar determinados membros no ranking, crie `pessoas_excluidas.csv` ao lado do script com a coluna `Nome ou alias`, uma pessoa ou alias por linha. O script associa aliases cadastrados em `dim_pessoas.csv` ao nome do ranking e os omite do CSV público. Esse arquivo é local e ignorado pelo Git.

Opcionalmente, use `votos_multiplicadores.csv` para imagens HELP que comprovem mais de um voto. Crie as colunas `Arquivo` e `Votos HELP`; informe o nome da imagem e o total de votos HELP comprovados nela. Sem ajuste, cada imagem HELP conta como 1. Esse arquivo também é local e ignorado pelo Git.

Mantenha o ZIP exportado do WhatsApp localmente. O script precisa que a exportação inclua `_chat.txt` e as mídias.

## Contar os votos

No PowerShell, dentro desta pasta:

```powershell
python .\conta_votos_help.py --zip "C:\caminho\WhatsApp Chat.zip" --output ".\contagem_local.xlsx" --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

O Excel detalhado e as imagens de revisão ficam locais e são ignorados pelo Git. O script também gera `contagem_local_ranking.csv`, que é ignorado automaticamente.
Na primeira execução, imagens antigas ainda podem precisar de OCR. A partir daí, o script grava os resultados num cache SQLite local (`.ocr_cache.sqlite3`) e compara o conteúdo das imagens; exportações seguintes fazem OCR só em imagens novas ou alteradas. Refaça a contagem normalmente com o mesmo comando. Falhas de OCR serão tentadas novamente na próxima execução. O cache é local, ignorado pelo Git e pode ser apagado para reconstruí-lo.

Se você já tem um relatório detalhado anterior, pode carregá-lo uma vez para inicializar o cache e evitar OCR das imagens que já foram reconhecidas:

```powershell
python .\conta_votos_help.py --zip "C:\caminho\WhatsApp Chat.zip" --output ".\contagem_local.xlsx" --reuse-ocr-from ".\contagem_local_anterior.xlsx" --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```


## Atualizar o ranking publicado

Depois de revisar o resultado, copie o CSV gerado para o arquivo público:

```powershell
Copy-Item .\contagem_local_ranking.csv .\ranking_publico.csv -Force
```

Confira o CSV antes de publicar. Depois atualize o repositório:

```powershell
git add ranking_publico.csv
git commit -m "Atualiza ranking semanal"
git push
```

O ZIP, as imagens, os relatórios Excel, a dimensão e as correções não devem ser adicionados ao Git. O `.gitignore` já cobre esses arquivos.

## Publicar o app

O app está pronto para implantação pelo Streamlit Community Cloud. Acesse <https://share.streamlit.io/>, conecte o GitHub, crie um app e selecione este repositório, a branch `main` e o arquivo `app.py`. Como o repositório é público, o placar implantado também ficará acessível publicamente. A documentação oficial descreve o fluxo de implantação: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>.

Depois da implantação, cada atualização enviada ao `ranking_publico.csv` no GitHub será carregada pelo app.

## Regras de contagem

Cada print conta como uma ocorrência. Só confirmações de voto para HELP entram no placar. Votos para BMG são classificados separadamente e não contam para HELP. Convites sem confirmação entram como `SEM COMPROVANTE`; leituras inconclusivas entram em `REVISAR`. O CSV público contém a contagem agregada por pessoa, não o histórico de mensagens.
