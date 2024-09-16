import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

class Plotter:
    def __init__(
        self,
        input_dir: str,
        strategy_type: str,
        initial_capital: float,
    ):
        self.input_dir = input_dir
        self.strategy_type = strategy_type
        self.initial_capital = initial_capital

        self.collateral_log = pd.read_csv(f'./results/{self.input_dir}/collateral_log.csv')
        self.funding_log = pd.read_csv(f'./results/{self.input_dir}/funding_log.csv')
        self.trades_log = pd.read_csv(f'./results/{self.input_dir}/trades_log.csv')

        if self.input_dir == 'simple_hold':
            self.plot_name = 'Simple Holding'
        elif self.input_dir == 'simple_threshold':
            self.plot_name = 'Simple Threshold'
        elif self.input_dir == 'simple_reinvest':
            self.plot_name = 'Simple Threshold & Reinvest'
        elif self.input_dir == 'complex_threshold':
            self.plot_name = 'Complex Threshold'
        elif self.input_dir == 'complex_reinvest':
            self.plot_name = 'Complex Threshold & Reinvest'
        else:
            self.plot_name = 'Strategy'


    def plot_pnl_over_time(self):
        collateral_log = self.collateral_log.copy()
        
        collateral_log['time'] = pd.to_datetime(collateral_log['time'])
        collateral_log.set_index('time', inplace=True)

        collateral_columns = [
            'binance_btc_collateral', 'binance_eth_collateral', 'binance_liquid_cash',
            'okx_btc_collateral', 'okx_eth_collateral', 'okx_liquid_cash',
            'bybit_btc_collateral', 'bybit_eth_collateral', 'bybit_liquid_cash'
        ]
        funding_columns = ['binance_funding', 'okx_funding', 'bybit_funding']
        unrealised_pnl_columns = ['binance_unrealised_pnl', 'okx_unrealised_pnl', 'bybit_unrealised_pnl']

        initial_investment = self.initial_capital

        if self.strategy_type == 'hold':
            collateral_log['pnl_basis'] = collateral_log[unrealised_pnl_columns].sum(axis=1)
            collateral_log['pnl_funding'] = collateral_log[funding_columns].sum(axis=1)
            collateral_log['total_pnl'] = collateral_log['pnl_basis'] + collateral_log['pnl_funding']
        else:
            collateral_log['pnl_basis'] = collateral_log[collateral_columns].sum(axis=1) - initial_investment
            collateral_log['pnl_funding'] = collateral_log[funding_columns].sum(axis=1)
            collateral_log['total_pnl'] = collateral_log['pnl_basis'] + collateral_log['pnl_funding']

        collateral_log['cumulative_pnl_basis_pct'] = (collateral_log['pnl_basis'] / initial_investment) * 100
        collateral_log['cumulative_pnl_funding_pct'] = (collateral_log['pnl_funding'] / initial_investment) * 100
        collateral_log['cumulative_total_pnl_pct'] = (collateral_log['total_pnl'] / initial_investment) * 100

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['pnl_basis'],
            mode='lines',
            name='P&L Basis',
            line=dict(width=2, color='blue'),
            hovertemplate='P&L Basis: $%{y:.2f}<br>Date: %{x}',
            yaxis='y1'
        ))

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['pnl_funding'],
            mode='lines',
            name='P&L Funding',
            line=dict(width=2, color='green'),
            hovertemplate='P&L Funding: $%{y:.2f}<br>Date: %{x}',
            yaxis='y1'
        ))

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['total_pnl'],
            mode='lines',
            name='P&L Total',
            line=dict(width=2, color='orange'),
            hovertemplate='Total P&L: $%{y:.2f}<br>Date: %{x}',
            yaxis='y1'
        ))

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['cumulative_pnl_basis_pct'],
            mode='lines',
            name='P&L Basis',
            line=dict(width=2, color='blue'),
            hovertemplate='P&L Basis: %{y:.2f}%<br>Date: %{x}',
            yaxis='y2',
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['cumulative_pnl_funding_pct'],
            mode='lines',
            name='P&L Funding',
            line=dict(width=2, color='green'),
            hovertemplate='P&L Funding: %{y:.2f}%<br>Date: %{x}',
            yaxis='y2',
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=collateral_log.index,
            y=collateral_log['cumulative_total_pnl_pct'],
            mode='lines',
            name='P&L Total',
            line=dict(width=2, color='orange'),
            hovertemplate='Total P&L: %{y:.2f}%<br>Date: %{x}',
            yaxis='y2',
            showlegend=False
        ))

        fig.update_layout(
            title=f'{self.plot_name} - Cumulative P&L Over Time',
            yaxis=dict(title='P&L ($)'),
            yaxis2=dict(title='P&L (%)', overlaying='y', side='right'),
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                x=0.5,
                y=-0.2,
                xanchor='center',
                yanchor='top'
            ),
            width=800,
            height=600,
            margin=dict(l=40, r=40, t=80, b=40), 
        )

        fig.update_xaxes(
            tickformat='%b %Y',
            tickangle=0,
            showgrid=True,
            zeroline=True,
            showticklabels=True,
            dtick='M3'
        )

        fig.write_image(f'./results/{self.input_dir}/cumulative_pnl.png')

        print(f"Plot saved to ./results/{self.input_dir}/cumulative_pnl.png")


    def plot_portfolio_over_time(self):
        ROLLING_WINDOW_DAYS = 30
        collateral_log = self.collateral_log.copy()

        collateral_log['time'] = pd.to_datetime(collateral_log['time'])
        collateral_log.set_index('time', inplace=True)

        collateral_log['binance_funding_value'] = collateral_log['binance_funding']
        collateral_log['okx_funding_value'] = collateral_log['okx_funding']
        collateral_log['bybit_funding_value'] = collateral_log['bybit_funding']

        collateral_log['binance_total'] = (
            collateral_log['binance_btc_collateral'] +
            collateral_log['binance_eth_collateral'] +
            collateral_log['binance_liquid_cash'] +
            collateral_log['binance_funding_value']
        )

        collateral_log['okx_total'] = (
            collateral_log['okx_btc_collateral'] +
            collateral_log['okx_eth_collateral'] +
            collateral_log['okx_liquid_cash'] +
            collateral_log['okx_funding_value']
        )

        collateral_log['bybit_total'] = (
            collateral_log['bybit_btc_collateral'] +
            collateral_log['bybit_eth_collateral'] +
            collateral_log['bybit_liquid_cash'] +
            collateral_log['bybit_funding_value']
        )

        collateral_log['portfolio_total'] = (
            collateral_log['binance_total'] + 
            collateral_log['okx_total'] + 
            collateral_log['bybit_total']
        )

        rolling_window = f'{ROLLING_WINDOW_DAYS}D'
        collateral_log['portfolio_total'] = collateral_log['portfolio_total'].rolling(window=rolling_window).mean()

        for exchange in ['binance', 'bybit', 'okx']:
            collateral_log[f'{exchange}_btc_pct'] = collateral_log[f'{exchange}_btc_collateral'].rolling(window=rolling_window).mean() / collateral_log['portfolio_total']
            collateral_log[f'{exchange}_eth_pct'] = collateral_log[f'{exchange}_eth_collateral'].rolling(window=rolling_window).mean() / collateral_log['portfolio_total']
            collateral_log[f'{exchange}_cash_pct'] = collateral_log[f'{exchange}_liquid_cash'].rolling(window=rolling_window).mean() / collateral_log['portfolio_total']
            collateral_log[f'{exchange}_funding_pct'] = collateral_log[f'{exchange}_funding_value'].rolling(window=rolling_window).mean() / collateral_log['portfolio_total']

        
        fig = go.Figure()

        exchange_shades = {
            'binance': {'cash': 'rgba(31, 119, 180, 1)', 'btc': 'rgba(255, 127, 14, 1)', 'eth': 'rgba(44, 160, 44, 1)', 'funding': 'rgba(214, 39, 40, 1)'},
            'bybit': {'cash': 'rgba(31, 119, 180, 0.7)', 'btc': 'rgba(255, 127, 14, 0.7)', 'eth': 'rgba(44, 160, 44, 0.7)', 'funding': 'rgba(214, 39, 40, 0.7)'},
            'okx': {'cash': 'rgba(31, 119, 180, 0.4)', 'btc': 'rgba(255, 127, 14, 0.4)', 'eth': 'rgba(44, 160, 44, 0.4)', 'funding': 'rgba(214, 39, 40, 0.4)'},
        }

        custom_names = {
            'binance': {'cash': 'Binance Liquid', 'btc': 'Binance BTC', 'eth': 'Binance ETH', 'funding': 'Binance Funding'},
            'bybit': {'cash': 'Bybit Liquid', 'btc': 'Bybit BTC', 'eth': 'Bybit ETH', 'funding': 'Bybit Funding'},
            'okx': {'cash': 'OKX Liquid', 'btc': 'OKX BTC', 'eth': 'OKX ETH', 'funding': 'OKX Funding'},
        }
        
        legend_ranks = {
            'binance': 1,
            'bybit': 2,
            'okx': 3
        }

        asset_types = ['cash', 'btc', 'eth', 'funding']
        for asset_type in asset_types:
            for exchange in ['binance', 'bybit', 'okx']:
                fig.add_trace(go.Scatter(
                    x=collateral_log.index,
                    y=collateral_log[f'{exchange}_{asset_type}_pct'] * 100,
                    mode='lines',
                    stackgroup='one',
                    name=custom_names[exchange][asset_type],
                    line=dict(color=exchange_shades[exchange][asset_type]),
                    legendrank=legend_ranks[exchange]
                ))

        fig.update_layout(
            title=f'{self.plot_name} - Portfolio Weighting (Monthly Rolling Average)',
            yaxis_title='Weighting (%)',
            template='plotly_white',
            xaxis=dict(tickformat='%b %Y'),
            yaxis=dict(tickformat='.0f', range=[0, 100]),
            hovermode='x unified',
            width=800,
            height=600,
            margin=dict(l=40, r=40, t=80, b=40), 
            legend=dict(
                orientation='h',
                x=0.5,
                y=-0.2,
                xanchor='center',
                yanchor='top'
            )
        )

        fig.write_image(f'./results/{self.input_dir}/portfolio_weighting.png')

        print(f"Plot saved to ./results/{self.input_dir}/portfolio_weighting.png")
        
        
    def plot_trading_volume(self):
            trades_df = self.trades_log.copy()

            trades_df['open_time'] = pd.to_datetime(trades_df['open_time'])
            trades_df['close_time'] = pd.to_datetime(trades_df['close_time'])

            trades_df['open_date'] = trades_df['open_time'].dt.date
            trades_df['close_date'] = trades_df['close_time'].dt.date

            trades_opened_per_day = trades_df['open_date'].value_counts().sort_index()
            trades_closed_per_day = trades_df['close_date'].value_counts().sort_index()

            trades_counts = pd.DataFrame({
                'date': pd.to_datetime(trades_opened_per_day.index),
                'trades_opened': trades_opened_per_day.values,
                'trades_closed': -trades_closed_per_day.reindex(trades_opened_per_day.index, fill_value=0).values
            })

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=trades_counts['date'],
                y=trades_counts['trades_opened'],
                name='Position Opened',
                marker_color='green',
                opacity=1.0
            ))

            fig.add_trace(go.Bar(
                x=trades_counts['date'],
                y=trades_counts['trades_closed'],
                name='Position Closed',
                marker_color='red',
                opacity=1.0
            ))

            fig.add_shape(
                type="line",
                x0=trades_counts['date'].min(), x1=trades_counts['date'].max(),
                y0=0, y1=0,
                line=dict(color="black", width=1)
            )

            fig.update_layout(
                title=f'{self.plot_name} - Trading Volume',
                yaxis_title='Number of Trades',
                barmode='relative',
                template='plotly_white',
                width=800,
                height=600,
                margin=dict(l=40, r=40, t=80, b=40), 
                legend=dict(
                    orientation='h',
                    x=0.5,
                    y=-0.2,
                    xanchor='center',
                    yanchor='top'
                )
            )

            fig.update_xaxes(
                tickformat='%b %Y',
                tickangle=0,
                showgrid=True,
                zeroline=True,
                showticklabels=True,
                dtick='M3'
            )

            fig.write_image(f'./results/{self.input_dir}/trading_volume.png')

            print(f"Plot saved to ./results/{self.input_dir}/trading_volume.png")


    def visualise(self):
        self.plot_pnl_over_time()
        self.plot_portfolio_over_time()
        self.plot_trading_volume()