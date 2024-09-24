import os
import requests
from typing import Dict, Any, Optional, List
from datetime import timedelta, datetime
# Load environment variables from the .env file

COINGECKO_API_KEY='CG-xXCJJaHa7QmvQNWyNheKmSfG'
BASE_URL = 'https://pro-api.coingecko.com/api/v3'
headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
def get_list_of_coins(coin_names: Optional[List[str]] = None, coin_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Retrieve a list of all available coins from the CoinGecko API or check for specific coins.
    This function makes a GET request to the CoinGecko API to fetch a comprehensive
    list of all cryptocurrencies available on the platform. Each coin in the list
    includes basic information such as id, symbol, and name. If specific coin_names
    or coin_symbols are provided, it checks if those coins are available in the list
    and they are returned if found.
    Args:
        coin_names (List[str], optional): The names of the coins to check for availability.
        coin_symbols (List[str], optional): The symbols of the coins to check for availability.
    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'coins' (List[Dict]): A list of dictionaries, each representing a coin
              with keys 'id', 'symbol', and 'name', if the request is successful.
            - 'length' (int): The length of the list of tokens.
            - 'success' (bool): True if the API call was successful, False otherwise.
            - 'error' (str): Error message or additional information if the request fails.
    """
    result = {
        'coins': [],
        'length': 0,
        'success': False,
    }
    try:
        response = requests.get(f'{BASE_URL}/coins/list', headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        all_coins = response.json()
        result['length'] = len(all_coins)
        result['success'] = True
        filtered_coins = []
        if coin_symbols:
            coin_symbols_lower = [symbol.lower() for symbol in coin_symbols]
            for coin in all_coins:
                if coin['symbol'].lower() in coin_symbols_lower:
                    filtered_coins.append(coin)
        if coin_names:
            coin_names_lower = [name.lower() for name in coin_names]
            for coin in all_coins:
                if coin['name'].lower() in coin_names_lower:
                    filtered_coins.append(coin)
        # Remove duplicates by converting to a set of tuples and back to a list
        unique_coins = {coin['id']: coin for coin in filtered_coins}.values()
        result['coins'] = list(unique_coins)
        result['length'] = len(result['coins'])
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error in CoinGecko API request in get_list_of_coins: {str(e)}")
    except ValueError as e:
        raise Exception(f"Error decoding JSON response in get_list_of_coins: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error in get_list_of_coins: {str(e)}")
    return result
def get_coin_data(name: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve data for a specific coin from the CoinGecko API.
    This function makes a GET request to the CoinGecko API to fetch a comprehensive
    list of all cryptocurrencies and then filters for the specific coin based on
    the provided name or symbol.
    Args:
        name (str, optional): The name of the coin to search for.
        symbol (str, optional): The symbol of the coin to search for.
    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'coin' (Dict): A dictionary representing the coin with keys 'id', 'symbol', and 'name',
              if the coin is found.
            - 'success' (bool): True if the API call was successful and the coin was found, False otherwise.
            - 'error' (str): Error message or additional information if the request fails or the coin is not found.
    """
    result = {
        'coin': None,
        'success': False,
        'error': None
    }
    if not name and not symbol:
        result['error'] = "Either name or symbol must be provided"
        return result
    try:
        response = requests.get(f'{BASE_URL}/coins/list', headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        all_coins = response.json()
        for coin in all_coins:
            print(coin)
            if (name and coin['name'].lower() == name.lower()) and (symbol and coin['symbol'].lower() == symbol.lower()):
                result['coin'] = coin
                result['success'] = True
                break
        if not result['success']:
            result['error'] = "No exact match found for both name and symbol"
    except requests.exceptions.RequestException as e:
        result['error'] = f"Error in CoinGecko API request: {str(e)}"
    except ValueError as e:
        result['error'] = f"Error decoding JSON response: {str(e)}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    return result
# Example usage:
#result=get_coin_data(symbol='dot', name='Polkadot')
#print("result: ", result)

headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
# Get today's date
current_date = datetime.now()
# Calculate the date one year ago
one_year_ago = current_date - timedelta(days=365)
# Format the date as "dd-mm-yyyy"
formatted_date = one_year_ago.strftime('%d-%m-%Y')
print("Date one year ago:", formatted_date)

def get_token_data(coin):
    try:
        formatted_coin = str(coin).casefold().strip()
        response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)
        historical_response = requests.get(f'{BASE_URL}/coins/{formatted_coin}/history?date={formatted_date}', headers=headers)
        if response.status_code == 200 and historical_response.status_code == 200:
            response = response.json()
            historical_response = historical_response.json()
            id = response.get('id')
            symbol = response.get('symbol')
            description = response['description']['en'] if 'description' in response and 'en' in response['description'] else None
            logo = response['image']['small'] if 'image' in response and 'small' in response['image'] else None
            market_cap_usd = response['market_data']['market_cap']['usd'] \
                if 'market_data' in response and 'market_cap' in response['market_data'] \
                and 'usd' in response['market_data']['market_cap'] else None
            total_volume = response['market_data']['total_volume']['usd'] \
                if 'market_data' in response and 'total_volume' in response['market_data'] \
                and 'usd' in response['market_data']['total_volume'] else None
            website = next((link for link in response.get('links', {}).get('homepage', []) if link.strip()), None)
            total_supply = response['market_data'].get('total_supply')
            circulating_supply = response['market_data'].get('circulating_supply')
            percentage_circulating_supply = (float(circulating_supply) / float(total_supply)) * 100 \
                if total_supply and circulating_supply else None
            max_supply = response['market_data'].get('max_supply')
            supply_model = 'Inflationary' if max_supply is None else 'Deflationary'
            current_price = response['market_data']['current_price']['usd'] \
                if 'market_data' in response and 'current_price' in response['market_data'] \
                and 'usd' in response['market_data']['current_price'] else None
            ath = response['market_data']['ath']['usd'] \
                if 'market_data' in response and 'ath' in response['market_data'] \
                and 'usd' in response['market_data']['ath'] else None
            ath_change_percentage = response['market_data']['ath_change_percentage']['usd'] \
                if 'market_data' in response and 'ath_change_percentage' in response['market_data'] \
                and 'usd' in response['market_data']['ath_change_percentage'] else None
            coingecko_link = f"https://www.coingecko.com/en/coins/{id}"
            categories = ", ".join([category for category in response.get("categories", [])
                                    if 'ecosystem' not in category.lower()]) or None
            chains = ", ".join([category for category in response.get("categories", [])
                                if 'ecosystem' in category.lower()]) or None
            contracts = ""
            if 'platforms' in response and response['platforms']:
                for platform, contract_address in response['platforms'].items():
                    if platform and contract_address:  # Check if both platform and contract_address are not empty
                        contracts += f"{platform}: {contract_address}\n"
            fully_diluted_valuation = response['market_data']['fully_diluted_valuation']['usd'] \
                if 'market_data' in response and 'fully_diluted_valuation' in response['market_data'] \
                and 'usd' in response['market_data']['fully_diluted_valuation'] else None
            price_a_year_ago = historical_response['market_data']['current_price']['usd']\
                if 'market_data' in historical_response and 'current_price' in historical_response['market_data']\
                and 'usd' in historical_response['market_data']['current_price'] else None
            price_change_percentage_1y = response['market_data']['price_change_percentage_1y']\
                if 'market_data' in response and 'price_change_percentage_1y' in response['market_data'] else None
            return {
                'id': id,
                'symbol': symbol,
                'logo': logo,
                'description': description,
                'market_cap_usd': market_cap_usd,
                'total_volume': total_volume,
                'website': website,
                'total_supply': total_supply,
                'circulating_supply': circulating_supply,
                'percentage_circulating_supply': percentage_circulating_supply,
                'max_supply': max_supply,
                'supply_model': supply_model,
                'current_price': current_price,
                'price_a_year_ago': price_a_year_ago,
                'price_change_percentage_1y': price_change_percentage_1y,
                'ath': ath,
                'ath_change_percentage': ath_change_percentage,
                'coingecko_link': coingecko_link,
                'categories': categories,
                'chains': chains,
                'contracts': contracts,
                'fully_diluted_valuation': fully_diluted_valuation,
                'success': True
            }
        else:
            return {'response': response.content.decode('utf-8'), 'success': False}
    except Exception as e:
        return {'response': str(e), 'success': False}
    
result = get_token_data('polkadot')
print(result)


#id, symbol, market_cap_usd, total_volume, circulating_supply, percentage_circulating_supply, current_price, ath, price_a_year_ago