# Sinais de negociação B3

Este projeto oferece um conjunto de scripts Python para gerar sinais de compra e venda para a Bolsa de Valores Brasileira (B3), aplicando o cruzamento de médias móveis simples (SMA) de curto e longo prazo em séries temporais de ativos do mercado à vista. Novos indicadores e funcionalidades poderão ser incorporados no futuro.

## 📊 Funcionalidades

- **Download de dados**: Realiza o download de dados de mercado pela API Yahoo Finance.
- **Cálculo de médias móveis**: Implementa estratégias SMA de curto e longo prazo para identificar tendências.
- ***Backtesting* das estratégias**: Realiza teste das estratégias com dados históricos, gerando figuras e resumo para tomada de decisão.
- **Notificações via Telegram**: Envia sinais de negociação provenientes da estratégia selecionada diretamente para o *smartphone*.
- **Agendamento automático**: Cria tarefas no Agendador de Tarefas do Windows para execução diária.
- **Arquivos de configuração**: Utiliza `.env` para variáveis de ambiente privadas `.txt` para lista de *tickers* e lista das combinações de SMA.

## ⚙️ Como Usar

1. **Instalar dependências**:
   ```bash
    pip install pandas
    pip install numpy
    pip install yfinance
    pip install requests
    pip install python-dotenv
    ```

2. **Configurar *tickers***
   - Em `tickers.txt` adicione os códigos das ações que deseja monitorar, um por linha.

3. **Configurar Telegram**
   - Crie um bot no Telegram e obtenha o seu `TOKEN` e `CHAT_ID`.
   - Adicione-os em `.env` para serem lidos por `b3_trading_signals_bot.py`.

4. **Executar o script**
   - Para rodar batelada de *backtesting* execute:
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


## 🧩 Estrutura do Projeto

- `b3_trading_signals.py` → Arquivo principal para *backtest* e comparação de estratégia.
- `b3_trading_signals_bot.py` → Arquivo para geração de sinais diários e notificações via Telegram.
- `b3_trading_signals_task_scheduler.py` → Criação de execução agendada no Windows.
- `b3_trading_signals_functions.py` → Funções auxiliares reutilizáveis.
- `tickers.txt` → Lista de *tickers* a serem monitorados.
- `ma_comb.txt` → Lista de indicadores SMA para análise.

## 📌 Observações

- O projeto está em desenvolvimento ocasional apenas durante horário de lazer e poderá sofrer constantes alterações.
- Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.
- Sanando possíveis dúvidas:
  - API Yahoo Finance: latência de 15 minutos para dados intradiários, sem limite de requisições;
  - API Brapi em seu plano gratuito: latência de 30 minutos, limite mensal de 15000 requisições;
  - Outras APIs: latências similares e envolvem custo.

## 🤝 Contato

- Para projetos avançados e personalizados, entrar em contato com o desenvolvedor.
- Sobre as qualificações do referido profissional:
  - A quantidade de desenvolvedores, por vezes mais habilidosos, disponíveis no mercado é enorme;
  - A quantidade de desenvolvedores que entendem de mercado financeiro e análise de séries financeiras é razoável;
  - A quantidade de desenvolvedores que entendem de análise de séries financeiras e teoria de análise/controle de sistemas (filtragem, estimação, análise frequencial) é mínima.
