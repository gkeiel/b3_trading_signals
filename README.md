# Sinais de negociação B3

Este projeto oferece um conjunto de scripts Python para gerar sinais de compra e venda para a Bolsa de Valores Brasileira (B3), utilizando o cruzamento de médias móveis simples (SMA) de curto e longo prazo. Novos indicadores poderão ser incorporados no futuro.

## 📊 Funcionalidades

- **Cálculo de médias móveis**: Implementa SMA de curto e longo prazo para identificar tendências.
- **Notificações via Telegram**: Envia sinais de negociação diretamente para o smartphone.
- **Agendamento automático**: Cria tarefas no Agendador de Tarefas do Windows para execução diária.
- **Arquivos de configuração**: Utiliza arquivos `.txt` para listagem de tickers e combinações de SMA.


## ⚙️ Como Usar

1. **Instalar dependências**:
    ```bash
    pip install pandas
    pip install numpy
    pip install requests
    pip install python-dotenv
    pip install python-telegram-bot
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
- `tickers.txt` → Lista de tickers a serem monitorados.
- `ma_comb.txt` → Lista de indicadores SMA para análise.

## 📌 Observações

- O projeto está em desenvolvimento ocasional durante horário de lazer e poderá sofrer constantes alterações.
- Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.