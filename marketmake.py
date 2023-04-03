import util
from time import sleep

# Global variable for quantity so that it can be easily adjusted for flexibility
quantity = 5_000

def get_highest_bid_price(session, ticker):
    """
    This function returns the highest bid from the orderbook (top of book)
    """
    bids = util.get_bid_orders(session, ticker)
    highest_bid_price = bids[0]['price']
    return highest_bid_price

def get_lowest_ask_price(session, ticker):
    """
    This function returns the lowest ask from the orderbook (top of book)
    """
    asks = util.get_ask_orders(session, ticker)
    lowest_ask_price = asks[0]['price']
    return lowest_ask_price

def place_buy_order(session, ticker, highest_bid, lowest_ask, spread_divisor):
    """
    This function pulls the highest bid and lowest ask to find the spread,
    calculates the premium we are willing to pay on top of the bid (indicated
    with spread_divisor variable) and executes a bid at that price
    """
    spread = lowest_ask - highest_bid
    # The premium we are willing to pay on top of the highest bid
    premium = spread / spread_divisor
    buy_price = highest_bid + premium
    session.post(f'http://localhost:9999/v1/orders?ticker={ticker}&type=LIMIT&quantity={quantity}&action=BUY&price={buy_price}')

def place_sell_order(session, ticker, highest_bid, lowest_ask, spread_divisor):
    """
    This function pulls the highest bid and lowest ask to find the spread,
    calculates the premium we are willing to pay below the ask (indicated
    with spread_divisor variable) and executes an ask at that price
    """
    spread = lowest_ask - highest_bid
    # The premium we are willing to discount below the lowest ask
    premium = spread / spread_divisor
    sell_price = lowest_ask - premium
    session.post(f'http://localhost:9999/v1/orders?ticker={ticker}&type=LIMIT&quantity={quantity}&action=SELL&price={sell_price}')

def main():
    session = util.open_session()
    ticker = "ALGO"
    tick = util.get_tick(session)
    while tick > 0:
        highest_bid_price = get_highest_bid_price(session, ticker)
        lowest_ask_price = get_lowest_ask_price(session, ticker)
        position = util.get_position(session, ticker)
        spread = lowest_ask_price - highest_bid_price
        required_margin = 0.025
        # This ensures that trades will only be placed if the spread is larger than our desired margin and 
        # our inventory is lower than 10,000 and larger than -10,000. If inventory is larger or smaller,
        # it will automatically be rebalanced with the last two if statements
        if spread > required_margin and (position < 10_000 and position > -10_000):
            spread_divisor = 6
            place_buy_order(session, ticker, highest_bid_price, lowest_ask_price, spread_divisor)
            place_sell_order(session, ticker, highest_bid_price, lowest_ask_price, spread_divisor)
            print('Order placed :)')
            sleep(0.4)
        if position >= 10_000:
            place_sell_order(session, ticker, highest_bid_price, lowest_ask_price, spread_divisor=4.5)
            sleep(1)
        if position <= -10_000:
            place_buy_order(session, ticker, highest_bid_price, lowest_ask_price, spread_divisor=4.5)
            sleep(1)

main()
