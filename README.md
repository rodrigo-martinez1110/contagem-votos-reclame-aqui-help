# Contagem de votos HELP — Prêmio Reclame Aqui

Projeto local para contabilizar prints enviados ao grupo do WhatsApp. O OCR roda no computador; o ZIP e as imagens não são enviados a serviços externos. O arquivo `ranking_publico.csv` é a cópia publicada no GitHub para consumo por um app Streamlit.

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

## Dados locais necessários

Crie `dim_pessoas.csv` ao lado do script com as colunas `Nome no ranking`, `Aliases WhatsApp` e `Celular final 4`. O arquivo contém dados da equipe e não deve ser enviado ao GitHub. Os aliases alternativos são separados por `|`.

Opcionalmente, crie `correcoes_votos.csv` com as colunas `Arquivo` e `Classificação` para correções visuais manuais. Esse arquivo também é local.

Mantenha o ZIP exportado do WhatsApp localmente. O script precisa que a exportação inclua `_chat.txt` e as mídias.

## Contar os votos

No PowerShell, dentro desta pasta:

```powershell
python .\conta_votos_help.py --zip "C:\caminho\WhatsApp Chat.zip" --output ".\contagem_local.xlsx" --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

O Excel detalhado e as imagens de revisão ficam locais e são ignorados pelo Git. O script também gera `contagem_local_ranking.csv`, que é ignorado automaticamente.

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

## Regras de contagem

Cada print conta como uma ocorrência. Só confirmações de voto para HELP entram no placar. Votos para BMG são classificados separadamente e não contam para HELP. Convites sem confirmação entram como `SEM COMPROVANTE`; leituras inconclusivas entram em `REVISAR`. O CSV público contém a contagem agregada por pessoa, não o histórico de mensagens.
