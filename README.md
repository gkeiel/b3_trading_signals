# Sinais de negociação B3

Este projeto disponibiliza um script Python para **geração automática de sinais de compra e venda de ativos da B3 (Bolsa de Valores Brasileira)**, aplicando estratégias de cruzamento de médias móveis em séries temporais do mercado à vista. Inclui um script para ***backtesting* e seleção das estratégias com melhor desempenho**, permitindo avaliar as abordagens antes de aplicá-las.

Como principais vantagens, o projeto proporciona:
- envio de **sinais de negociação recorrentes via canal no Telegram** e que **evitem a necessidade de análise gráfica**.
- **código aberto** permitindo **flexibilidade para escolha das médias móveis** e comparação entre estratégias.

Canal Telegram aberto com sinais diários executado via GitHub Actions. Todos podem inscrever-se para uma impressão do que o *bot* pode oferecer.
[t.me/b3_trading_signals_free](https://t.me/b3_trading_signals_free)

## 📊 Funcionalidades

- **Download de dados**: Realiza o download de dados de mercado pela API Yahoo Finance.
- **Cruzamento de médias móveis**: Implementa estratégias de cruzamento de 2 ou 3 médias móveis (SMA, WMA ou EMA) para identificar possíveis tendências.
- ***Backtesting* das estratégias**: Realiza teste das estratégias com dados históricos, gerando figuras e resumo para tomada de decisão.
- **Avaliação de performance**: Avalia desempenho frente a uma função objetivo de ponderação e classifica as melhores estratégias.
- **Notificações via Telegram**: Envia sinais de negociação provenientes da estratégia escolhida diretamente para o *smartphone*/computador.
- **Agendamento automático**: Configura tarefa para execução recorrente via GitHub Actions ou então pelo Agendador de Tarefas do Windows.
- **Arquivos de configuração**: Utiliza `.env` para variáveis de ambiente privadas, `.txt` para lista de códigos, `.txt`para lista de indicadores e `.csv` para lista de estratégias.

## 📈 Estratégias Disponíveis

O projeto atualmente suporta as estratégias de **cruzamento duplo** e **cruzamento triplo** de médias móveis para geração de sinais de negociação, usando os seguintes métodos de cálculo:
- **SMA (Simple Moving Average)** - Média móvel simples.
- **EMA (Exponential Moving Average)** - Média móvel exponencial.
- **WMA (Weighted Moving Average)** – Média móvel ponderada.

Essas opções permitem que o usuário compare o desempenho de diferentes abordagens dentro da B3.

## ⚙️ Como Usar

1. **Instalar dependências**:
   ```bash
    pip install pandas
    pip install numpy
    pip install yfinance
    pip install requests
    pip install python-dotenv
    ```

2. **Configurar códigos e indicadores**
   - Em `tickers.txt` adicione os códigos das ações que deseja avaliar, um por linha.
   - Em `indicators.txt` adicione os indicadores que deseja gerar, um por linha. Inicialmente apenas SMA, WMA e EMA são implementáveis.
   - Em `strategies.csv` adicione os códigos das ações que deseja gerar sinais de negociação, cada qual com a respectiva melhor estratégia.

3. **Configurar Telegram**
   - Crie um *bot* no Telegram e obtenha o seu `TOKEN`.
   - Crie um canal no Telegram e obtenha o seu `CHAT_ID`.
   - Adicione o *bot* como administrador do canal.
   - Adicione as chaves em `.env` para serem lidas pelo `b3_trading_signals_bot.py`.

4. **Executar o script**
   - Para rodar a batelada de *backtests* execute:
     ```bash
     python b3_trading_signals.py
     ```
   - Para geração de sinais e notificação, para cada *ticker*, execute:
     ```bash
     python b3_trading_signals_bot.py
     ```
   - Para automatizar a geração de sinais com GitHub Actions, crie os *repository secrets* `TOKEN` e `CHAT_ID`, para o *workflow* já configurado. Alternativamente, para agendar tarefa somente pelo Windows, execute uma única vez:
     ```bash
     python b3_trading_signals_task_scheduler.py
     ```

## 🖼️ Exemplos de saídas

- **Gráfico do *backtest* com SMA**
  
  Após a execução do script `b3_trading_signals.py` são gerados gráficos de cada estratégia, planilhas para cada *ticker*, planilha com melhores resultados. As figuras geradas seguem o exemplo mostrado abaixo:
  <p align="center">
     <img width="733" height="395" alt="B3SA3 SA_5_30" src="https://github.com/user-attachments/assets/5f7c268b-1265-405a-a42f-a59f89729cd4"/>
     <img width="733" height="395" alt="B3SA3 SA_backtest_5_30" src="https://github.com/user-attachments/assets/c0cbff4a-7189-43dd-b6bc-000b4cea62b0"/>
  </p>

  Note como o ativo encerra o período avaliado próximo ao valor inicial, de modo que a estratégia *Buy & hold* resultaria em retorno nulo. Por outro lado, caso a estratégia SMA 5/30 fosse seguida à risca proporcionaria ao final do período um retorno de 20% sobre o valor investido, desconsiderando taxas de negociação. Ademais, a operação de venda a descoberto foi desconsiderada nos cálculos devido as taxas de aluguel envolvidas, embora possa facilmente ser habilitada no *backtest*.

- **Sinal de negociação via Telegram**

  Após a execução do script `b3_trading_signals_bot.py` são gerados sinais de negociação para as melhores estratégias escolhidas, seguindo o exemplo mostrado abaixo:
  <p align="center">
     <img width="480" height="511" alt="telegram" src="https://github.com/user-attachments/assets/39ac0ee0-c816-4bd6-8742-b4884156051a" />
  </p>

  Note como é gerado um sinal de negociação para cada ativo, sugerindo a tendência de alta, baixa ou neutralidade baseado na estratégia escolhida e a duração dessa tendência, que mostra a quantas amostras a tendência permanece sem trocar de lado. Adicionalmente, são mostrados dados de volume e das principais médias móveis como indicadores de força dessa tendência.

## 🧩 Estrutura do Projeto

- `b3_trading_signals.py` → Arquivo principal para *backtest* e seleção das melhores estratégias.
- `b3_trading_signals_bot.py` → Arquivo principal para geração de sinais diários e notificações via Telegram.
- `b3_trading_signals_functions.py` → Funções auxiliares reutilizáveis.
- `b3_trading_signals_task_scheduler.py` → Criação de execução agendada no Windows.
- `tickers.txt` → Lista de *tickers* para análise.
- `indicators.txt` → Lista de indicadores para análise.
- `strategies.csv` → Lista de estratégias para sinais de negociação consistindo de *tickers* e seus indicadores.

## 📌 Observações

⚠️ Não nos responsabilizamos por perdas ou prejuízos resultantes do uso das estratégias ou sinais gerados por este código.

- Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.
- Novas melhorias e funcionalidades poderão ser incorporadas no futuro. Estão planejadas:
  - alteração para o paradigma de orientação a objeto (POO); ✅
  - melhoria na função objetivo com novas ponderações e *presets*; ✅
  - novos indicadores para o preço;
  - salvamento de arquivos em nuvem;
  - alertas/relatório por e-mail.
- Possíveis dúvidas:
  - API Yahoo Finance: latência de 15 minutos para dados intradiários, sem limite de requisições;
  - API Brapi em seu plano gratuito: latência de 30 minutos, limite mensal de 15000 requisições;
  - Outras APIs: latências similares e/ou envolvem custo.

## 🤝 Apoio

Este repositório é mantido de forma independente, durante o tempo livre. Se o código lhe foi útil e deseja apoiar o seu desenvolvimento contínuo, considere fazer uma doação:

- [PayPal](https://www.paypal.com/donate/?hosted_button_id=BF6E8J7P32KWE)  

Seu apoio ajuda a manter e evoluir o projeto, adicionando novos indicadores, melhorias e documentação.
