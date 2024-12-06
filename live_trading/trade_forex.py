import MetaTrader5 as mt5
import asyncio
from typing import Callable
import time
import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

# tick_data = {
#     "symbol": symbol,
#     "time": tick.time,
#     "bid": tick.bid,
#     "ask": tick.ask,
#     "last": tick.last,
#     "volume": tick.volume,
#     "time_msc": tick.time_msc,
#     "flags": tick.flags,
#     "volume_real": tick.volume_real
# }

class MT5AsyncStream:
    def __init__(self):
        self.is_running = False
        self.callbacks = []
        
    async def start(self, symbols: list[str]):
        if not mt5.initialize():
            print("MT5 initialize() failed")
            return False
            
        for symbol in symbols:
            if not mt5.symbol_select(symbol, True):
                print(f"Symbol {symbol} selection failed")
                continue
        
        self.is_running = True
        # Create tasks for each symbol
        tasks = [self._monitor_symbol(symbol) for symbol in symbols]
        await asyncio.gather(*tasks)
    
    def stop(self):
        self.is_running = False
        mt5.shutdown()
    
    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)
    
    async def _monitor_symbol(self, symbol: str):
        last_price = None
        
        while self.is_running:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                current_price = (tick.bid + tick.ask) / 2
                if last_price != current_price:
                    last_price = current_price
                    for callback in self.callbacks:
                        callback(symbol, tick)
            
            # Use async sleep instead of time.sleep
            await asyncio.sleep(0.001)

def format_time(timestamp, offset_hours=7):
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)  # UTC
    local_time = utc_time + timedelta(hours=offset_hours)  # ปรับเป็น timezone
    return local_time.strftime("%Y-%m-%d %H:%M:%S")   # แสดงเฉพาะเวลา (hh:mm:ss)

def get_all_positions():
    positions = mt5.positions_get()
    if positions is None or len(positions) == 0:
        return []

    positions_info = []
    for pos in positions: 
        total_profit = pos.profit + pos.swap

        positions_info.append({
            "symbol": pos.symbol,
            "type": "Buy" if pos.type == mt5.POSITION_TYPE_BUY else "Sell",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "price_current": pos.price_current,
            "profit": total_profit,
            "time": format_time(pos.time)
        })

    return positions_info

def get_account_info():
    """ดึงข้อมูล Account จาก MT5"""
    account_info = mt5.account_info()
    if account_info:
        return {
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "free_margin": account_info.margin_free,
            "profit": account_info.profit
        }
    return None

def display_positions(symbol: str, tick):
    print("\033[2J\033[H", end='')
    
    terminal_width = os.get_terminal_size().columns
    positions = get_all_positions()
    account = get_account_info()
    positions_separator = "=" * terminal_width
    
    # Account Info section with colors
    if account:
        profit_color = '\033[32m' if account['profit'] >= 0 else '\033[31m'
        account_info = (
            f"Balance: {account['balance']:,.2f} | "
            f"Equity: {account['equity']:,.2f} | "
            f"Margin: {account['margin']:,.2f} | "
            f"Free Margin: {account['free_margin']:,.2f} | "
            f"Profit: {profit_color}{account['profit']:,.2f}\033[0m"
        )
    else:
        account_info = "Account info not available"

    # Header with current price info
    time_formatted = format_time(tick.time, offset_hours=7)
    header = (
        f"{positions_separator}\n"
        f"Time:     {time_formatted:<19} | Symbol:   {symbol:<10} | "
        f"Bid: {tick.bid:>9.3f} | Ask: {tick.ask:>9.3f} | Last: {tick.last:>9.3f}\n"
        f"Volume:   {tick.volume:>8.2f} | Real Vol: {tick.volume_real:>8.2f}\n"
        f"{account_info}\n"
        f"{positions_separator}"
    )
    
    # Positions section with colors
    if positions:
        pos_format = "{:<3} {:<8} {:<20} {:<7} {:<12} {:<12} {:<20} {:<20}"
        positions_header = pos_format.format(
            "#", "Symbol", "Type", "Volume", "Open", "Current", "Profit", "Time"
        )
        
        positions_list = []
        for idx, pos in enumerate(positions, 1):
            # สีสำหรับ Type (Buy/Sell)
            type_color = '\033[34m' if pos['type'] == 'Buy' else '\033[33m'  # Blue for Buy, Yellow for Sell
            type_text = f"{type_color}{pos['type']:<6}\033[0m"
            
            # สีสำหรับ Profit
            profit_color = '\033[32m' if pos['profit'] >= 0 else '\033[31m'  # Green for profit, Red for loss
            profit_text = f"{profit_color}{pos['profit']:>9.2f}\033[0m"
            
            positions_list.append(pos_format.format(
                idx,
                pos['symbol'],
                type_text,
                f"{pos['volume']:.2f}",
                f"{pos['price_open']:.2f}",
                f"{pos['price_current']:.2f}",
                profit_text,
                pos['time']
            ))
        
        positions_section = (
            f"\nOpen Positions:\n{positions_header}\n"
            f"{'-' * terminal_width}\n"
            f"{chr(10).join(positions_list)}\n"
            f"{positions_separator}"
        )
    else:
        positions_section = f"\nNo open positions\n{positions_separator}"
    
    print(f"{header}{positions_section}")           

def on_price_change(symbol: str, tick):
    display_positions(symbol, tick)

async def main():
    try:
        price_stream = MT5AsyncStream()
        price_stream.add_callback(on_price_change)

        await price_stream.start(["ETHUSD"])
    except KeyboardInterrupt:
        price_stream.stop()

# รัน async code
if __name__ == "__main__":
    asyncio.run(main())