# Sinais de negociação B3

Este projeto oferece um conjunto de scripts Python para geração de sinais de compra e venda para a Bolsa de Valores Brasileira (B3), aplicando o cruzamento de médias móveis simples (SMA) de curto e longo prazo em séries temporais de ativos do mercado à vista. Novos indicadores e funcionalidades poderão ser incorporados no futuro.

## 📊 Funcionalidades

- **Download de dados**: Realiza o download de dados de mercado pela API Yahoo Finance.
- **Cálculo de médias móveis**: Implementa estratégias SMA de curto e longo prazo para identificar tendências.
- ***Backtesting* das estratégias**: Realiza teste das estratégias com dados históricos, gerando figuras e resumo para tomada de decisão.
- **Notificações via Telegram**: Envia sinais de negociação provenientes da estratégia selecionada diretamente para o *smartphone*/computador.
- **Agendamento automático**: Cria tarefas no Agendador de Tarefas do Windows para execução diária.
- **Arquivos de configuração**: Utiliza `.env` para variáveis de ambiente privadas e `.txt` para lista de códigos e lista de indicadores.

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
   - Em `tickers.txt` adicione os códigos das ações que deseja monitorar, um por linha.
   - Em `indicators.txt` adicione os indicadores que deseja gerar, um por linha. Inicialmente apenas SMA são implementáveis.

3. **Configurar Telegram**
   - Crie um *bot* no Telegram e obtenha o seu `TOKEN` e `CHAT_ID`.
   - Adicione-os em `.env` para serem lidos por `b3_trading_signals_bot.py`.

4. **Executar o script**
   - Para rodar a batelada de *backtests* execute:
     ```bash
     python b3_trading_signals.py
     ```
   - Para geração de sinais e notificação, para cada *ticker*, execute:
     ```bash
     python b3_trading_signals_bot.py
     ```
   - Para automatizar a geração de sinais, agendando a execução diária no Windows, execute uma única vez:
     ```bash
     python b3_trading_signals_task_scheduler.py
     ```
## 🖼️ Exemplos de saídas

Após a execução dos scripts, são gerados gráficos e saídas como os mostrados nos exemplos abaixo:

- **Gráfico do *backtest* com SMA**
<p align="center">
<img width="733" height="395" alt="B3SA3 SA_5_30" src="https://github.com/user-attachments/assets/5f7c268b-1265-405a-a42f-a59f89729cd4"/>
<img width="733" height="395" alt="B3SA3 SA_backtest_5_30" src="https://github.com/user-attachments/assets/c0cbff4a-7189-43dd-b6bc-000b4cea62b0"/>
</p>

Note como o ativo encerra o período avaliado próximo ao valor inicial, de modo que a estratégia *Buy & hold* resultaria em retorno nulo. Por outro lado, caso a estratégia SMA 5/30 fosse seguida à risca proporcionaria ao final do período um retorno de 20% sobre o valor investido, desconsiderando taxas de negociação. Ademais, a operação de venda a descoberto foi desconsiderada nos cálculos devido as taxas de aluguel envolvidas, embora possa facilmente ser habilitada no *backtest*.

- **Sinal de negociação via Telegram**
<p align="center">
<img width="480" height="511" alt="telegram" src="https://github.com/user-attachments/assets/84a83c60-ac94-4759-bddf-b9708b5199f2" />
</p>

Note como é gerado um sinal de negociação para cada ativo, sugerindo a tendência de alta ou baixa baseado na melhor estratégia definida pelo operador e o acumulado dessa tendência, que mostra a quantas amostras a tendência permanece sem trocar de lado. 

## 🧩 Estrutura do Projeto

- `b3_trading_signals.py` → Arquivo principal para *backtest* e comparação de estratégia.
- `b3_trading_signals_bot.py` → Arquivo para geração de sinais diários e notificações via Telegram.
- `b3_trading_signals_task_scheduler.py` → Criação de execução agendada no Windows.
- `b3_trading_signals_functions.py` → Funções auxiliares reutilizáveis.
- `tickers.txt` → Lista de *tickers* a serem monitorados.
- `indicators.txt` → Lista de indicadores SMA para análise.

## 📌 Observações

- O projeto está em desenvolvimento ocasional apenas durante horário de lazer e poderá sofrer alterações.
- Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.
- Sanando possíveis dúvidas:
  - API Yahoo Finance: latência de 15 minutos para dados intradiários, sem limite de requisições;
  - API Brapi em seu plano gratuito: latência de 30 minutos, limite mensal de 15000 requisições;
  - Outras APIs: latências similares e/ou envolvem custo.

## 🤝 Contato

- Para projetos avançados e personalizados, entrar em contato com o desenvolvedor.
- Sobre as qualificações do referido profissional:
  - A quantidade de desenvolvedores, por vezes mais habilidosos, disponíveis no mercado é enorme;
  - A quantidade de desenvolvedores que entendem de mercado financeiro e análise de séries financeiras é razoável;
  - A quantidade de desenvolvedores que entendem de análise de séries financeiras e teoria de análise/controle de sistemas (filtragem, estimação, análise frequencial) é mínima.
